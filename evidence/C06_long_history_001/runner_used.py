#!/usr/bin/env python3
"""Execute the prospectively specified full-century strategy workflow."""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import shlex
import shutil
import sys
import time
import traceback
from types import SimpleNamespace

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
sys.dont_write_bytecode = True
import numpy as np

DAYS, BASE_DAYS, STOCKS = 25200, 2016, 1000
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
BASE_SHA = {
    "returns.npy": "563cbcab745cc6ffc9d04739fd49a64a7881e3cfee81f2a157080a6336c3ba04",
    "characteristics.npy": "5b95d6c1ceb7c8a9209ca76fc6e7116f4b496933fe64771029a1192737fed1f4",
    "costs.npy": "8a80bf28efe25c9e33e05c5a0d89b3787459fbcf51f7b4f378c2ba0c8e992ee1",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(path, obj):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def prepare_inputs(base, cache):
    actual = {name: digest(base / name) for name in BASE_SHA}
    if actual != BASE_SHA:
        raise ValueError("Discovery input identity differs")
    recipe = {"kind": "fixed_discovery_tile", "days": DAYS, "base_days": BASE_DAYS,
              "source_sha256": actual, "numeric_source_slice": [0, BASE_DAYS]}
    if (cache / "metadata.json").exists():
        metadata = json.loads((cache / "metadata.json").read_text())
        if metadata["recipe"] != recipe:
            raise ValueError("Existing long-history cache has a different recipe")
    else:
        cache.mkdir(parents=True, exist_ok=False)
        for name in ("returns.npy", "characteristics.npy"):
            source = np.load(base / name, mmap_mode="r", allow_pickle=False)
            if len(source) != BASE_DAYS or source.dtype != np.float64:
                raise ValueError("Unexpected base array")
            target = np.lib.format.open_memmap(cache / name, mode="w+", dtype=np.float64,
                                              shape=(DAYS, *source.shape[1:]))
            for start in range(0, DAYS, BASE_DAYS):
                count = min(BASE_DAYS, DAYS - start)
                target[start:start + count] = source[:count]
            target.flush()
            del target, source
        shutil.copyfile(base / "costs.npy", cache / "costs.npy")
        metadata = {"recipe": recipe, "cache_sha256": {n: digest(cache / n) for n in BASE_SHA}}
        write_json(cache / "metadata.json", metadata)
    if {n: digest(cache / n) for n in BASE_SHA} != metadata["cache_sha256"]:
        raise ValueError("Long-history cache identity differs")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "strategy", "config", "reference", "out", "cache"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("plan", "protocol", "scorer"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--cpu", type=int, required=True)
    args = parser.parse_args()
    root, strategy_path, config_path, reference, out, cache = [p.resolve() for p in
        (args.project, args.strategy, args.config, args.reference, args.out, args.cache)]
    out.mkdir(parents=True, exist_ok=False)
    result = {"status": "RUNNING", "started_utc": now(), "checks": [],
              "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
              "market_validation_opened": False, "market_audit_opened": False,
              "synthetic_only": True, "days": DAYS}
    write_json(out / "summary.json", result)
    source_hashes, input_metadata, timings, expected_fees, target_gross = {}, None, [], [], []
    prefix_targets, prefix_held, calls, forecast_calls = [], [], 0, 0
    forecast_seconds, max_weight, max_gross, fallback_count = 0.0, 0.0, 0.0, 0
    exit_code = 1

    def check(name, passed, actual):
        record = {"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual}
        result["checks"].append(record)
        print(json.dumps(record), flush=True)
        if not passed:
            raise AssertionError(name)

    with (out / "stdout.log").open("w") as log, (out / "stderr.log").open("w") as errors:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, errors)):
            try:
                os.sched_setaffinity(0, {args.cpu})
                write_json(out / "environment.json", {"python": sys.version, "platform": platform.platform(),
                    "cpu_affinity": sorted(os.sched_getaffinity(0)), "thread_environment": {k: os.environ[k] for k in THREADS},
                    "packages": {n: importlib.metadata.version(n) for n in ("numpy", "pandas", "scipy")},
                    "host_contention": "Other research workflows may run on separate pinned CPUs."})
                historical = json.loads((reference / "source_manifest.json").read_text())
                historical_summary = json.loads((reference / "summary.json").read_text())
                check("historical_discovery_completed", historical_summary["status"] == "EXECUTED_PASS_SCOPE_ONLY"
                      and historical_summary["exit_code"] == 0, historical_summary["status"])
                candidate_dir = out / "source/candidate"
                candidate_dir.mkdir(parents=True)
                for name, sha in historical.items():
                    if name.startswith("source/candidate/"):
                        source = strategy_path.parent / Path(name).name
                        check("source_identity:" + Path(name).name, digest(source) == sha, digest(source))
                        shutil.copyfile(source, out / name)
                frozen_strategy = candidate_dir / strategy_path.name
                check("candidate_in_historical_closure", frozen_strategy.is_file(), strategy_path.name)
                scorer = out / "source/score.py"
                shutil.copyfile(args.scorer or root / "source/Quant Research Take-Home/score.py", scorer)
                shutil.copyfile(config_path, out / "config.json")
                shutil.copyfile(args.plan or root / "verification/LONG_HISTORY_E2E_PLAN.md", out / "expectations.md")
                shutil.copyfile(args.protocol or root / "RESEARCH_PROTOCOL.json", out / "protocol_used.json")
                shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
                (out / "reference").mkdir()
                for name in ("summary.json", "daily.csv", "source_manifest.json"):
                    shutil.copyfile(reference / name, out / "reference" / name)
                check("scorer_identity", digest(scorer) == SCORER_SHA == historical["source/score.py"], digest(scorer))
                check("config_identity", digest(out / "config.json") == historical["config.json"], digest(out / "config.json"))
                check("protocol_identity", digest(out / "protocol_used.json") == historical["protocol_used.json"], digest(out / "protocol_used.json"))
                frozen_files = list((out / "source").rglob("*.py")) + list((out / "reference").iterdir())
                frozen_files += [out / n for n in ("runner_used.py", "expectations.md", "protocol_used.json", "config.json")]
                source_hashes = {str(p.relative_to(out)): digest(p) for p in frozen_files}
                write_json(out / "source_manifest.json", source_hashes)
                rerun = [sys.executable, str(out / "runner_used.py"), "--project", str(root), "--strategy", str(frozen_strategy),
                         "--config", str(out / "config.json"), "--reference", str(out / "reference"), "--out", str(out) + "_rerun",
                         "--cache", str(cache), "--cpu", str(args.cpu), "--plan", str(out / "expectations.md"),
                         "--protocol", str(out / "protocol_used.json"), "--scorer", str(scorer)]
                (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
                (out / "setup.md").write_text("# Setup\n\nRestore the original discovery cache using REPRODUCE.md. "
                    "Use environment.json dependency versions and the frozen rerun command. The controller deterministically "
                    "creates or verifies the repeated discovery cache. Output directories never overwrite prior evidence. "
                    "Synthetic economics are accounting evidence only; no predictive performance claim is made.\n")
                input_metadata = prepare_inputs(root / "cache/discovery", cache)
                write_json(out / "input_manifest.json", input_metadata)
                arrays = tuple(np.load(cache / n, mmap_mode="r", allow_pickle=False) for n in BASE_SHA)
                returns, chars, costs = arrays
                check("input_shapes", returns.shape == (DAYS, STOCKS) and chars.shape == (DAYS, STOCKS, 13)
                      and costs.shape == (STOCKS,), [list(a.shape) for a in arrays])
                check("inputs_read_only", all(not a.flags.writeable for a in arrays), "read-only memory maps")
                for start in range(0, DAYS, 252):
                    if not np.isfinite(returns[start:start + 252]).all() or not np.isfinite(chars[start:start + 252]).all():
                        raise ValueError("Nonfinite synthetic input")
                check("input_values", bool(np.isfinite(costs).all() and np.all(costs >= 0)), "finite float64 arrays; nonnegative costs")
                sys.path.insert(0, str(candidate_dir))
                strategy = load_module(frozen_strategy, "long_history_candidate")
                official = load_module(scorer, "long_history_official_scorer")
                config = json.loads((out / "config.json").read_text())
                strategy.configure(config)
                candidate_forecast = official.with_declared_arguments(strategy.forecast)
                candidate_rebalance = official.with_declared_arguments(strategy.rebalance)

                def forecast(**named):
                    nonlocal forecast_seconds, forecast_calls
                    forecast_calls += 1
                    tick = time.perf_counter()
                    values = np.asarray(candidate_forecast(**named), dtype=np.float64)
                    forecast_seconds = time.perf_counter() - tick
                    check("forecast_shape_finite", values.shape == (DAYS, STOCKS) and bool(np.isfinite(values).all()), list(values.shape))
                    np.save(out / "forecasts.npy", values[:BASE_DAYS])
                    expected = historical_summary["output_arrays"]["forecasts.npy"]["sha256"]
                    check("exact_discovery_forecast_prefix", digest(out / "forecasts.npy") == expected, digest(out / "forecasts.npy"))
                    values.setflags(write=False)
                    print(json.dumps({"phase": "forecast_completed", "candidate_seconds": forecast_seconds}), flush=True)
                    return values

                def rebalance(**named):
                    nonlocal calls, max_weight, max_gross, fallback_count
                    earning_day = len(named["returns_history"])
                    if earning_day != 253 + calls:
                        raise AssertionError("Target earning-day sequence differs")
                    held = named["held_positions"].copy()
                    tick = time.perf_counter()
                    new = np.asarray(candidate_rebalance(**named), dtype=np.float64)
                    timings.append(time.perf_counter() - tick)
                    if new.shape != (STOCKS,) or not np.isfinite(new).all():
                        raise ValueError("Nonfinite or misshaped target")
                    if not np.array_equal(held, named["held_positions"]):
                        raise AssertionError("Candidate changed the scorer's held book")
                    gross, weight = float(np.abs(new).sum()), float(np.max(np.abs(new)))
                    if gross > config["gross_cap"] + 1e-12 or weight > config["weight_cap"] + 1e-12:
                        raise AssertionError("Configured position limit exceeded")
                    max_gross, max_weight = max(max_gross, gross), max(max_weight, weight)
                    target_gross.append(gross)
                    expected_fees.append(0.0 if calls == 0 else float(costs @ np.abs(new - held)))
                    if calls < 1763:
                        prefix_targets.append(new.copy())
                        prefix_held.append(held)
                    if hasattr(strategy, "get_last_diagnostics"):
                        fallback_count += int(bool(strategy.get_last_diagnostics().get("factor_fallback", 0)))
                    calls += 1
                    if calls % 1008 == 0:
                        print(json.dumps({"phase": "rebalance", "completed_calls": calls, "earning_day": earning_day}), flush=True)
                    return new

                rows, official_forecast_seconds = official.run(SimpleNamespace(forecast=forecast, rebalance=rebalance),
                    returns, chars, costs, start=252)
                check("complete_counts", forecast_calls == 1 and calls == DAYS - 253 and rows.shape == (DAYS - 254, 5),
                      {"forecast_calls": forecast_calls, "targets": calls, "scored_rows": list(rows.shape)})
                check("scored_rows_finite_and_solvency", bool(np.isfinite(rows).all() and np.all(rows[:, 0] > -1)
                      and np.all(rows[:, 0] - rows[:, 1] > -1)), "all official scored rows")
                check("full_fee_reconciliation", np.array_equal(rows[:, 1], np.asarray(expected_fees[1:])),
                      {"max_abs_error": float(np.max(np.abs(rows[:, 1] - expected_fees[1:])))})
                check("gross_reconciliation", np.array_equal(rows[:, 2], np.asarray(target_gross[1:])),
                      {"max_abs_error": float(np.max(np.abs(rows[:, 2] - target_gross[1:])))})
                for name, values in (("targets.npy", prefix_targets), ("held_books.npy", prefix_held)):
                    np.save(out / name, np.asarray(values))
                    check("exact_discovery_prefix:" + name, digest(out / name) == historical_summary["output_arrays"][name]["sha256"], digest(out / name))
                fields = ("gross_return", "full_cost", "closing_target_gross", "raw_market_return")
                with (out / "reference/daily.csv").open(newline="") as handle:
                    saved = list(csv.DictReader(handle))
                expected = np.array([[float(record[k]) for k in fields] for record in saved])
                check("historical_score_mask", [int(r["return_index"]) for r in saved] == list(range(253, 2015)), len(saved))
                check("exact_discovery_economics", np.array_equal(rows[:1762, :4], expected),
                      {"max_abs_error": float(np.max(np.abs(rows[:1762, :4] - expected)))})
                timing_array = np.asarray(timings)
                result["timing"] = {"forecast_candidate_seconds": forecast_seconds,
                    "forecast_official_instrumented_seconds": float(official_forecast_seconds), "actual_century_executed": True,
                    "mean_candidate_rebalance_ms": float(timing_array.mean() * 1000),
                    "mean_scored_candidate_rebalance_ms": float(timing_array[1:].mean() * 1000),
                    "mean_official_instrumented_rebalance_ms": float(rows[:, 4].mean() * 1000),
                    "quantiles_candidate_ms": {str(q): float(np.quantile(timing_array, q) * 1000) for q in (0, .5, .9, .95, .99, 1)},
                    "quarter_mean_candidate_ms": [float(a.mean() * 1000) for a in np.array_split(timing_array, 4)]}
                result["positions"] = {"max_abs_weight": max_weight, "max_gross": max_gross, "factor_fallback_calls": fallback_count}
                (out / "daily").mkdir()
                for start in range(0, len(rows), 1008):
                    with (out / "daily" / f"part_{start // 1008:03d}.csv").open("w", newline="") as handle:
                        writer = csv.writer(handle)
                        writer.writerow(["return_index", "gross_return", "full_cost", "net_return", "target_gross", "market_return",
                                         "candidate_rebalance_ms", "official_rebalance_seconds"])
                        for i in range(start, min(start + 1008, len(rows))):
                            g, fee, exposure, market, sec = rows[i]
                            writer.writerow([i + 253, g, fee, g - fee, exposure, market, timing_array[i + 1] * 1000, sec])
                np.save(out / "all_candidate_rebalance_seconds.npy", timing_array)
                check("century_forecast_runtime", forecast_seconds < 3600 and official_forecast_seconds < 3600, result["timing"])
                check("mean_rebalance_runtime", timing_array.mean() < .1 and timing_array[1:].mean() < .1, result["timing"])
                result["status"], exit_code = "EXECUTED_PASS_SCOPE_ONLY", 0
            except BaseException as exc:
                result["status"] = "INTERRUPTED" if isinstance(exc, KeyboardInterrupt) else "EXECUTED_FAIL"
                result["traceback"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                try:
                    if source_hashes:
                        check("frozen_sources_unchanged", all(digest(out / p) == h for p, h in source_hashes.items()), "frozen file hashes")
                    if input_metadata is not None:
                        check("inputs_unchanged", {n: digest(cache / n) for n in BASE_SHA} == input_metadata["cache_sha256"], "full synthetic array hashes")
                except Exception:
                    result["status"], exit_code = "EXECUTED_FAIL", 1
                    result["final_integrity_traceback"] = traceback.format_exc()
                    traceback.print_exc()
                result.update({"exit_code": exit_code, "finished_utc": now(), "completed_rebalances": calls,
                               "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               "limitations": ["Repeated discovery workload, not independent market history or alpha evidence.",
                                               "Host-specific runtime with possible contention; finite path safety only."]})
                write_json(out / "summary.json", result)
                artifacts = {str(p.relative_to(out)): {"sha256": digest(p), "bytes": p.stat().st_size}
                             for p in sorted(out.rglob("*")) if p.is_file() and p.name not in ("artifact_manifest.json", "stdout.log", "stderr.log")}
                write_json(out / "artifact_manifest.json", artifacts)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
