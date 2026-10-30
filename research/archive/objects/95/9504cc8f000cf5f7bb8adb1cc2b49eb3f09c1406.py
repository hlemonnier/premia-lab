#!/usr/bin/env python3
"""Run one frozen candidate through the original scorer on discovery only.

The preimplementation contract is research/EXPERIMENT_RUNNER_PLAN.md.
Invoke as a new process; it fixes threads before importing numerical libraries.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import time
import traceback
from types import SimpleNamespace

THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for _key in THREAD_KEYS:
    os.environ[_key] = "1"
sys.dont_write_bytecode = True
import numpy as np

SCORER_SHA256 = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
CACHE_SHA256 = {
    "returns.npy": "563cbcab745cc6ffc9d04739fd49a64a7881e3cfee81f2a157080a6336c3ba04",
    "characteristics.npy": "5b95d6c1ceb7c8a9209ca76fc6e7116f4b496933fe64771029a1192737fed1f4",
    "costs.npy": "8a80bf28efe25c9e33e05c5a0d89b3787459fbcf51f7b4f378c2ba0c8e992ee1",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_value(value):
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_value(value.tolist())
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(json_value(value), indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def write_csv(path, records, fields):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
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


def summarize_rows(rows, score_days):
    if not len(rows):
        return {"scored_days": 0, "undefined_reason": "Empty scored interval"}
    gross, costs, exposure, market, timing = rows.T
    net = gross - costs
    net_std, gross_std = float(net.std()), float(gross.std())
    market_centered = market - market.mean()
    market_ss = float(market_centered @ market_centered)
    geometric_valid = bool(np.all(net > -1))
    wealth = np.concatenate(([1.0], np.cumprod(1 + net))) if geometric_valid else None
    result = {
        "scored_days": len(rows), "first_return_index": int(score_days[0]),
        "last_return_index": int(score_days[-1]),
        "daily_net_mean": float(net.mean()), "daily_net_std_ddof0": net_std,
        "net_sharpe": math.sqrt(252) * float(net.mean()) / net_std if net_std else None,
        "gross_sharpe": math.sqrt(252) * float(gross.mean()) / gross_std if gross_std else None,
        "annual_arithmetic_net_return": float(net.mean() * 252),
        "annual_net_volatility": net_std * math.sqrt(252),
        "realized_net_market_beta": float(market_centered @ (net - net.mean()) / market_ss) if market_ss else None,
        "annual_full_cost": float(costs.mean() * 252),
        "mean_gross_exposure": float(exposure.mean()),
        "min_daily_net_return": float(net.min()), "max_daily_net_return": float(net.max()),
        "min_daily_gross_return": float(gross.min()), "net_bankruptcy_observed": not geometric_valid,
        "geometric_total_return": float(wealth[-1] - 1) if geometric_valid else None,
        "annual_geometric_return": float(np.expm1(np.log1p(net).mean() * 252)) if geometric_valid else None,
        "max_drawdown": float(np.max(1 - wealth / np.maximum.accumulate(wealth))) if geometric_valid else None,
        "official_instrumented_mean_rebalance_ms": float(timing.mean() * 1000),
    }
    result["undefined_metrics"] = {key: "Zero variance or nonpositive compounding wealth"
                                   for key, value in result.items() if value is None}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--strategy", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, help="Frozen protocol for an exact evidence rerun")
    parser.add_argument("--expectations", type=Path, help="Frozen preimplementation plan for a rerun")
    parser.add_argument("--scorer", type=Path, help="Frozen original scorer for a rerun")
    args = parser.parse_args()
    root, source_strategy, source_config, out = (p.resolve() for p in
                                              (args.project, args.strategy, args.config, args.out))
    out.mkdir(parents=True, exist_ok=False)
    source_dir = out / "source"
    source_dir.mkdir()
    (source_dir / "candidate").mkdir()
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    result = {"status": "RUNNING", "started_utc": now(), "command": command,
              "input_slice": [0, 2016], "score_slice": [253, 2015], "checks": [],
              "candidate_feasibility": {}, "causality_status": "NOT_TESTED_BY_THIS_RUN",
              "validation_status": "NOT_OPENED", "audit_status": "NOT_OPENED",
              "long_horizon_runtime": "NOT_EXECUTED", "returned_by_official_scorer": False}
    write_json(out / "summary.json", result)
    arrays, rows, forecasts = None, None, None
    targets, held_books, target_records = [], [], []
    input_hashes = {}
    source_hashes = {}
    exit_code = 1

    def check(name, condition, actual):
        record = {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual}
        result["checks"].append(record)
        print(json.dumps(json_value(record), allow_nan=False), flush=True)
        if not condition:
            raise AssertionError(name)

    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(Tee(sys.stdout, stdout)), contextlib.redirect_stderr(Tee(sys.stderr, stderr)):
            try:
                shutil.copy2(Path(__file__).resolve(), out / "runner_used.py")
                shutil.copy2(args.expectations or root / "research/EXPERIMENT_RUNNER_PLAN.md", out / "expectations.md")
                shutil.copy2(args.protocol or root / "RESEARCH_PROTOCOL.json", out / "protocol_used.json")
                shutil.copy2(source_config, out / "config.json")
                for path in sorted(source_strategy.parent.glob("*.py")):
                    shutil.copy2(path, source_dir / "candidate" / path.name)
                frozen_strategy = source_dir / "candidate" / source_strategy.name
                scorer_path = source_dir / "score.py"
                shutil.copy2(args.scorer or root / "source/Quant Research Take-Home/score.py", scorer_path)
                source_hashes = {str(p.relative_to(out)): sha256(p) for p in sorted(source_dir.rglob("*.py"))}
                source_hashes.update({name: sha256(out / name) for name in
                                     ("runner_used.py", "expectations.md", "protocol_used.json", "config.json")})
                write_json(out / "source_manifest.json", source_hashes)
                rerun = shlex.join([sys.executable, str(out / "runner_used.py"), "--project", str(root),
                                    "--strategy", str(frozen_strategy), "--config", str(out / "config.json"),
                                    "--out", str(out) + "_rerun", "--protocol", str(out / "protocol_used.json"),
                                    "--expectations", str(out / "expectations.md"), "--scorer", str(scorer_path)])
                (out / "rerun.txt").write_text(rerun + "\n")
                (out / "setup.md").write_text(
                    "# Setup\n\nRestore the source archive named in REPRODUCE.md and prepare the verified discovery cache "
                    "with tools/prepare_discovery.py. This run reads only cache/discovery numeric arrays. "
                    "Use the package versions in environment.json. The rerun command uses frozen strategy and helper sources; "
                    "it writes a new directory and refuses to overwrite evidence.\n\n"
                    "The large output arrays are reproducible from this command and identified in artifact_manifest.json. "
                    "Candidate timings exclude logging and the optional risk diagnostic; official timings include the transparent adapter.\n")
                result["rerun_command"] = rerun
                config = json.loads((out / "config.json").read_text())
                check("config_is_object", isinstance(config, dict), type(config).__name__)
                protocol = json.loads((out / "protocol_used.json").read_text())
                discovery = next(p for p in protocol["periods"] if p["name"] == "discovery")
                check("frozen_scope", discovery["input_slice"] == [0, 2016]
                      and discovery["score_slice"] == [253, 2015]
                      and protocol["replay"]["start"] == 252, discovery)
                check("official_scorer_identity", sha256(scorer_path) == SCORER_SHA256, sha256(scorer_path))
                controls = {"thread_environment": {k: os.environ[k] for k in THREAD_KEYS}}
                try:
                    available = sorted(os.sched_getaffinity(0))
                    os.sched_setaffinity(0, {available[0]})
                    controls["cpu_affinity"] = sorted(os.sched_getaffinity(0))
                except (AttributeError, OSError, IndexError) as exc:
                    controls["cpu_affinity_unavailable"] = str(exc)
                packages = {}
                for name in ("numpy", "pandas", "scipy", "cvxpy", "scikit-learn", "lightgbm"):
                    try:
                        packages[name] = importlib.metadata.version(name)
                    except importlib.metadata.PackageNotFoundError:
                        packages[name] = "NOT_INSTALLED"
                write_json(out / "environment.json", {"python": sys.version, "executable": sys.executable,
                           "platform": platform.platform(), "packages": packages, "pid": os.getpid(), **controls})
                result["process_controls"] = controls
                cache = root / "cache/discovery"
                metadata = json.loads((cache / "metadata.json").read_text())
                check("cache_scope", metadata["status"] == "READY" and metadata["input_slice"] == [0, 2016],
                      {"status": metadata["status"], "input_slice": metadata["input_slice"]})
                input_hashes = {name: sha256(cache / name) for name in ("returns.npy", "characteristics.npy", "costs.npy")}
                check("cache_identity", input_hashes == CACHE_SHA256
                      and all(input_hashes[n] == metadata["cache_sha256"][n] for n in input_hashes), input_hashes)
                write_json(out / "input_manifest.json", {"input_slice": [0, 2016], "cache_sha256": input_hashes,
                           "source_sha256": metadata["source_sha256"], "source_archive": protocol["source_archive"],
                           "metadata_sha256": sha256(cache / "metadata.json"), "features": metadata["features"]})
                arrays = tuple(np.load(cache / name, mmap_mode="r", allow_pickle=False)
                               for name in ("returns.npy", "characteristics.npy", "costs.npy"))
                returns, chars, costs = arrays
                check("input_shapes", returns.shape == (2016, 1000) and chars.shape == (2016, 1000, 13)
                      and costs.shape == (1000,), [list(a.shape) for a in arrays])
                check("input_values", all(a.dtype == np.float64 and np.isfinite(a).all() for a in arrays)
                      and bool(np.all(costs >= 0)), "float64, finite, nonnegative costs")
                sys.path.insert(0, str(frozen_strategy.parent))
                strategy = import_file(frozen_strategy, "candidate_strategy")
                scorer = import_file(scorer_path, "original_discovery_scorer")
                if callable(getattr(strategy, "configure", None)):
                    strategy.configure(config)
                elif config:
                    raise ValueError("Nonempty configuration requires strategy.configure(config)")
                result["configuration"] = config
                check("rebalance_interface", callable(getattr(strategy, "rebalance", None)), "callable rebalance")
                candidate_rebalance = scorer.with_declared_arguments(strategy.rebalance)
                forecast_calls = 0
                forecast_candidate_seconds = 0.0
                has_risk_interface = callable(getattr(strategy, "estimate_risk", None))
                result["estimated_beta_diagnostic"] = "AVAILABLE" if has_risk_interface else "UNAVAILABLE_NO_INTERFACE"
                has_portfolio_diagnostics = callable(getattr(strategy, "get_last_diagnostics", None))
                result["portfolio_diagnostics"] = "AVAILABLE" if has_portfolio_diagnostics else "UNAVAILABLE_NO_INTERFACE"
                diagnostic_fields = None

                def traced_forecast(**named):
                    nonlocal forecasts, forecast_calls, forecast_candidate_seconds
                    forecast_calls += 1
                    tick = time.perf_counter()
                    output = scorer.with_declared_arguments(strategy.forecast)(**named)
                    forecast_candidate_seconds = time.perf_counter() - tick
                    forecasts = np.asarray(output, dtype=np.float64)
                    check("forecast_shape", forecasts.shape == (2016, 1000), list(forecasts.shape))
                    check("forecast_finite", bool(np.isfinite(forecasts).all()), "all finite")
                    forecasts.setflags(write=False)
                    return forecasts

                def traced_rebalance(**named):
                    nonlocal diagnostic_fields
                    earning_day = len(named["returns_history"])
                    held = np.array(named["held_positions"], copy=True)
                    tick = time.perf_counter()
                    new = np.asarray(candidate_rebalance(**named), dtype=np.float64)
                    seconds = time.perf_counter() - tick
                    if new.shape != (1000,) or not np.isfinite(new).all():
                        raise ValueError(f"Invalid target on earning day {earning_day}: {new.shape}")
                    if not np.array_equal(named["held_positions"], held):
                        raise ValueError(f"Candidate mutated scorer held_positions on earning day {earning_day}")
                    trade = np.abs(new - held)
                    record = {"decision_close_index": earning_day - 1, "target_earning_index": earning_day,
                              "target_gross": float(np.abs(new).sum()), "target_net": float(new.sum()),
                              "max_abs_stock_weight": float(np.max(np.abs(new))),
                              "turnover_abs_weight": float(trade.sum()), "full_trade_cost": float(costs @ trade),
                              "official_expected_fee": 0.0 if earning_day == 253 else float(costs @ trade),
                              "candidate_rebalance_ms": seconds * 1000, "estimated_beta_exposure": None}
                    if has_portfolio_diagnostics:
                        diagnostics = strategy.get_last_diagnostics()
                        keys = ("pre_scale_gross", "gross_scale", "pre_scale_box_saturation_fraction", "post_scale_estimated_beta")
                        if not isinstance(diagnostics, dict) or not all(k in diagnostics for k in keys):
                            raise ValueError("Missing documented portfolio diagnostic fields")
                        if any(not isinstance(k, str) or not k or k in record for k in diagnostics):
                            raise ValueError("Diagnostic names must be strings distinct from core target fields")
                        if any(np.asarray(v).ndim != 0 for v in diagnostics.values()):
                            raise ValueError("Portfolio diagnostics must contain scalars only")
                        diagnostics = {k: float(v) for k, v in diagnostics.items()}
                        if diagnostic_fields is None:
                            diagnostic_fields = set(diagnostics)
                        elif set(diagnostics) != diagnostic_fields:
                            raise ValueError("Portfolio diagnostic fields changed between calls")
                        if (not all(math.isfinite(v) for v in diagnostics.values())
                                or diagnostics["pre_scale_gross"] < 0
                                or not 0 < diagnostics["gross_scale"] <= 1
                                or not 0 <= diagnostics["pre_scale_box_saturation_fraction"] <= 1):
                            raise ValueError("Invalid portfolio diagnostic values")
                        if not np.isclose(diagnostics["pre_scale_gross"] * diagnostics["gross_scale"],
                                          record["target_gross"], atol=1e-12, rtol=1e-12):
                            raise ValueError("Portfolio scaling diagnostics do not match returned target gross")
                        record.update(diagnostics)
                    if has_risk_interface:
                        beta, variance = strategy.estimate_risk(named["returns_history"])
                        beta = np.asarray(beta)
                        variance = np.asarray(variance)
                        if beta.shape != (1000,) or variance.shape != (1000,) or not np.isfinite(beta).all():
                            raise ValueError("Invalid read-only estimate_risk diagnostic output")
                        record["estimated_beta_exposure"] = float(beta @ new)
                    targets.append(new.copy())
                    held_books.append(held)
                    target_records.append(record)
                    if len(target_records) % 250 == 0:
                        result["completed_rebalances"] = len(target_records)
                        write_json(out / "summary.json", result)
                    return new

                proxy = SimpleNamespace(rebalance=traced_rebalance)
                has_forecast = callable(getattr(strategy, "forecast", None))
                if has_forecast:
                    proxy.forecast = traced_forecast
                tick = time.perf_counter()
                rows, official_forecast_seconds = scorer.run(proxy, *arrays, start=252)
                result["execution_seconds"] = time.perf_counter() - tick
                result["returned_by_official_scorer"] = True
                check("forecast_call_count", forecast_calls == int(has_forecast), forecast_calls)
                check("score_shape", rows.shape == (1762, 5), list(rows.shape))
                check("score_finite", bool(np.isfinite(rows).all()), "all finite")
                check("rebalance_count", len(target_records) == 1763, len(target_records))
                check("earning_day_sequence", [r["target_earning_index"] for r in target_records] == list(range(253, 2016)),
                      {"first": target_records[0]["target_earning_index"], "last": target_records[-1]["target_earning_index"]})
                captured_fees = np.array([r["official_expected_fee"] for r in target_records[1:]])
                captured_gross = np.array([r["target_gross"] for r in target_records[1:]])
                check("full_cost_accounting", np.array_equal(rows[:, 1], captured_fees),
                      {"max_abs_error": float(np.max(np.abs(rows[:, 1] - captured_fees)))})
                check("target_gross_accounting", np.array_equal(rows[:, 2], captured_gross),
                      {"max_abs_error": float(np.max(np.abs(rows[:, 2] - captured_gross)))})
                check("gross_solvency", bool(np.all(rows[:, 0] > -1)), float(rows[:, 0].min()))
                score_days = np.arange(253, 2015)
                result["metrics"] = summarize_rows(rows, score_days)
                result["blocks"] = []
                for block in range(4):
                    mask = (score_days >= 504 * block) & (score_days < 504 * (block + 1))
                    result["blocks"].append({"block": block + 1, "nominal_input_slice": [504 * block, 504 * (block + 1)],
                                             **summarize_rows(rows[mask], score_days[mask])})
                rebalance_times = np.array([r["candidate_rebalance_ms"] for r in target_records])
                result["timing"] = {"forecast_candidate_seconds": forecast_candidate_seconds,
                                    "forecast_official_instrumented_seconds": official_forecast_seconds,
                                    "forecast_century_extrapolation_hours": forecast_candidate_seconds / 2016 * 25200 / 3600,
                                    "forecast_extrapolation_is_actual_century_run": False,
                                    "all_calls_candidate_ms": {str(q): float(np.quantile(rebalance_times, q))
                                                               for q in (0, .5, .9, .95, .99, 1)},
                                    "all_calls_candidate_mean_ms": float(rebalance_times.mean()),
                                    "scored_calls_candidate_mean_ms": float(rebalance_times[1:].mean()),
                                    "discarded_opening_candidate_ms": float(rebalance_times[0])}
                selected = target_records[1:]
                result["trading"] = {"mean_daily_abs_turnover": float(np.mean([r["turnover_abs_weight"] for r in selected])),
                                     "total_abs_turnover_charged": float(sum(r["turnover_abs_weight"] for r in selected)),
                                     "maximum_gross": float(max(r["target_gross"] for r in target_records)),
                                     "maximum_abs_stock_weight": float(max(r["max_abs_stock_weight"] for r in target_records)),
                                     "maximum_abs_net_exposure": float(max(abs(r["target_net"]) for r in target_records)),
                                     "opening_trade_full_cost_waived": target_records[0]["full_trade_cost"]}
                if has_risk_interface:
                    result["trading"]["max_abs_estimated_beta_exposure"] = max(abs(r["estimated_beta_exposure"]) for r in target_records)
                if has_portfolio_diagnostics:
                    result["trading"]["rescale_call_count"] = sum(r["gross_scale"] < 1.0 for r in target_records)
                    result["trading"]["rescale_call_fraction"] = float(np.mean([r["gross_scale"] < 1.0 for r in target_records]))
                    result["trading"]["minimum_gross_scale"] = min(r["gross_scale"] for r in target_records)
                    result["trading"]["mean_pre_scale_gross"] = float(np.mean([r["pre_scale_gross"] for r in target_records]))
                    result["trading"]["maximum_pre_scale_gross"] = max(r["pre_scale_gross"] for r in target_records)
                    result["trading"]["mean_pre_scale_box_saturation_fraction"] = float(np.mean(
                        [r["pre_scale_box_saturation_fraction"] for r in target_records]))
                    factor_fields = {k for k in diagnostic_fields if k.startswith("factor_")}
                    if factor_fields:
                        result["factor_diagnostics"] = {
                            key: {"minimum": min(r[key] for r in target_records),
                                  "maximum": max(r[key] for r in target_records),
                                  "mean": float(np.mean([r[key] for r in target_records]))}
                            for key in sorted(factor_fields)
                        }
                        for key in ("factor_fallback", "factor_refreshed"):
                            if key in factor_fields:
                                result["factor_diagnostics"][key]["nonzero_call_count"] = sum(
                                    r[key] != 0.0 for r in target_records)
                beta = result["metrics"]["realized_net_market_beta"]
                feasibility = {"realized_abs_beta_below_0_2": beta is not None and abs(beta) < .2,
                               "realized_abs_beta_below_design_0_1": beta is not None and abs(beta) < .1,
                               "candidate_mean_rebalance_below_100ms": float(rebalance_times.mean()) < 100,
                               "net_solvency": not result["metrics"]["net_bankruptcy_observed"]}
                for key, measured in (("weight_cap", result["trading"]["maximum_abs_stock_weight"]),
                                      ("gross_cap", result["trading"]["maximum_gross"])):
                    if key in config:
                        feasibility[key + "_observed"] = measured <= float(config[key]) + 1e-12
                result["candidate_feasibility"] = feasibility
                report = io.StringIO()
                with contextlib.redirect_stdout(report):
                    scorer.report(config.get("candidate_id", source_strategy.stem), rows, official_forecast_seconds, 2016)
                (out / "official_report.txt").write_text(report.getvalue())
                print(report.getvalue(), end="")
                result["status"] = "EXECUTED_PASS_SCOPE_ONLY"
                exit_code = 0
            except KeyboardInterrupt:
                result["status"] = "INCOMPLETE"
                result["error"] = traceback.format_exc()
                traceback.print_exc()
                exit_code = 130
            except Exception:
                result["status"] = "EXECUTED_FAIL"
                result["error"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                try:
                    if input_hashes:
                        after = {name: sha256(root / "cache/discovery" / name) for name in input_hashes}
                        result["input_hashes_after"] = after
                        unchanged = after == input_hashes
                        result["checks"].append({"name": "input_files_unchanged", "status": "PASS" if unchanged else "FAIL"})
                        if not unchanged:
                            result["status"], exit_code = "EXECUTED_FAIL", 1
                    if source_hashes:
                        unchanged = all(sha256(out / name) == expected for name, expected in source_hashes.items())
                        result["checks"].append({"name": "frozen_sources_unchanged", "status": "PASS" if unchanged else "FAIL"})
                        if not unchanged:
                            result["status"], exit_code = "EXECUTED_FAIL", 1
                    if forecasts is not None:
                        np.save(out / "forecasts.npy", forecasts, allow_pickle=False)
                    if targets:
                        np.save(out / "targets.npy", np.stack(targets), allow_pickle=False)
                        np.save(out / "held_books.npy", np.stack(held_books), allow_pickle=False)
                        write_csv(out / "target_diagnostics.csv", target_records, list(target_records[0]))
                    if rows is not None:
                        fields = ["return_index", "csv_day_label", "gross_return", "full_cost", "net_return",
                                  "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds"]
                        ledger = [{"return_index": i + 253, "csv_day_label": i + 254, "gross_return": float(row[0]),
                                   "full_cost": float(row[1]), "net_return": float(row[0] - row[1]),
                                   "closing_target_gross": float(row[2]), "raw_market_return": float(row[3]),
                                   "official_instrumented_rebalance_seconds": float(row[4])} for i, row in enumerate(rows)]
                        write_csv(out / "daily.csv", ledger, fields)
                    result["completed_rebalances"] = len(target_records)
                    result["output_arrays"] = {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size}
                                               for p in sorted(out.glob("*.npy"))}
                except Exception:
                    result["evidence_error"] = traceback.format_exc()
                    result["status"], exit_code = "INCOMPLETE", 1
                    traceback.print_exc()
                result["finished_utc"], result["exit_code"] = now(), exit_code
                result["limitations"] = ["Discovery outcomes only; this is a development-sample experiment.",
                                         "Causality, later validation, audit and century-long runtime are not established by this runner.",
                                         "Single-core wall timings are measurements on this environment; no guarantee on other hardware."]
                write_json(out / "summary.json", result)
                print(f"{result['status']}: {len(target_records)} rebalance calls; exit {exit_code}", flush=True)
    artifacts = {str(p.relative_to(out)): {"sha256": sha256(p), "bytes": p.stat().st_size}
                 for p in sorted(out.rglob("*")) if p.is_file() and p.name != "artifact_manifest.json"}
    write_json(out / "artifact_manifest.json", artifacts)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
