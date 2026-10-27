#!/usr/bin/env python3
"""One frozen continuous replay, with explicit protected-access admission.

Expectations were written first in verification/PROTECTED_REPLAY_PLAN.md.
No selection, tuning, unrestricted data loader, or boundary restart occurs here.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import importlib.metadata
import importlib.util
import io
import json
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
for key in THREAD_KEYS:
    os.environ[key] = "1"
sys.dont_write_bytecode = True

PROTOCOL_SHA = "cc2de53284feaeff97022c869ee8ee6e7b9fb40ab3f3dd1c0353e5b9923ed737"
ADMISSION_SHA = "105cc2ce46b4e84d98c0921f725ab90b13a4d8f13da9e854a085cb63840545cd"
PLAN_SHA = "32dc6a11c84ce4009490cccd057f0b0836f22581ef42e05ede77c51ebb0dd436"
HELPER_SHA = "6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69"
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
C06_CONFIG_SHA = "f424033fae2e2ca4a8f0a532a2da41dc4841235f1c8c67394e26e9081c9a49fb"
SOURCE_SHA = {
    "returns.csv": "6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d",
    "characteristics.csv": "46b9df20aebb324bd0026090d54f04bd6835283881dd73e728e90f16a5279a08",
    "costs.csv": "ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186",
}
FEATURES = ["Woe", "Malice", "Dread", "Frolic", "Up", "Down", "Charm", "Strange",
            "Top", "Bottom", "Snap", "Crackle", "Pop"]
MASKS = {
    "discovery-parity": {"discovery": (253, 2015)},
    "synthetic-zero": {"validation_a": (2016, 2520), "validation_b": (2520, 3023), "pooled_validation": (2016, 3023)},
    "validation": {"validation_a": (2016, 2520), "validation_b": (2520, 3023), "pooled_validation": (2016, 3023)},
    "audit": {"locked_audit": (3024, 3779)},
}
DAYS = {"discovery-parity": 2016, "synthetic-zero": 3024, "validation": 3024, "audit": 3780}
ATOL, RTOL = 1e-14, 1e-12


def load(path):
    return json.loads(Path(path).read_text())


def project_path(root, value):
    p = Path(value)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Manifest paths must be project-relative without parent traversal")
    result = (root / p).resolve()
    if not result.is_relative_to(root):
        raise ValueError("Manifest path escapes project")
    return result


def layout(a):
    return {"shape": list(a.shape), "dtype": str(a.dtype), "strides": list(a.strides),
            "c_contiguous": bool(a.flags.c_contiguous), "f_contiguous": bool(a.flags.f_contiguous)}


def admit(args, root, out, config, source_strategy, reference, helper, check):
    """Validate approval and all nominated identities before protected parsing."""
    if not args.nomination_manifest or not args.nomination_sha256:
        raise ValueError("Protected replay requires the root-approved manifest and its exact SHA256")
    manifest_path = args.nomination_manifest.resolve()
    check("nomination_manifest_identity", helper.sha256(manifest_path) == args.nomination_sha256,
          helper.sha256(manifest_path))
    nomination = load(manifest_path)
    check("root_approved_stage", nomination.get("schema_version") == 1
          and nomination.get("status") == "ROOT_APPROVED_PROTECTED_REPLAY"
          and nomination.get("stage") == args.mode, nomination.get("stage"))
    expected = {"protocol_sha256": PROTOCOL_SHA, "scorer_sha256": SCORER_SHA,
                "admission_plan_sha256": ADMISSION_SHA, "replay_plan_sha256": PLAN_SHA,
                "controller_sha256": helper.sha256(out / "runner_used.py"), "metric_helper_sha256": HELPER_SHA}
    check("nomination_control_identities", all(nomination.get(k) == v for k, v in expected.items()), expected)
    candidates = nomination.get("candidates", [])
    check("nomination_candidate_count", isinstance(candidates, list)
          and 1 <= len(candidates) <= (3 if args.mode == "validation" else 1), len(candidates))
    ids = [c.get("candidate_id") for c in candidates]
    check("unique_nominees", all(isinstance(x, str) and x for x in ids)
          and len(set(ids)) == len(ids), ids)
    selected = [c for c in candidates if c.get("candidate_id") == config.get("candidate_id")]
    check("requested_candidate_nominated", len(selected) == 1, config.get("candidate_id"))
    chosen = selected[0]
    for item in candidates:
        active = item is chosen
        entry = project_path(root, item["strategy_path"])
        cfg = args.config.resolve() if active else project_path(root, item["config_path"])
        check("nominated_config:" + item["candidate_id"], helper.sha256(cfg) == item["config_sha256"]
              and load(cfg).get("candidate_id") == item["candidate_id"], helper.sha256(cfg))
        source_map = item["source_sha256"]
        names = [Path(k).name for k in source_map]
        check("nominated_source_set:" + item["candidate_id"], bool(source_map)
              and item["strategy_path"] in source_map and len(set(names)) == len(names)
              and all(project_path(root, k).parent == entry.parent for k in source_map), sorted(source_map))
        for rel, digest in source_map.items():
            canonical = project_path(root, rel)
            source = source_strategy.parent / canonical.name if active else canonical
            check("nominated_source:" + rel, source.suffix == ".py" and helper.sha256(source) == digest,
                  helper.sha256(source))
        check("engineering_gate_status:" + item["candidate_id"], item.get("engineering_gate_status") == "PASSED",
              item.get("engineering_gate_status"))
        check("frozen_simplicity_rank:" + item["candidate_id"], item.get("simplicity_rank") ==
              {"C09_additive_long_memory": 1, "C12_local_additive": 2, "C06_gls_factor": 3}.get(item["candidate_id"], -1),
              item.get("simplicity_rank"))
        evidence = item.get("evidence", [])
        roles = {e.get("role") for e in evidence}
        check("engineering_roles:" + item["candidate_id"],
              {"source_review", "causality", "long_history", "controller_verification"} <= roles, sorted(roles))
        for e in evidence:
            path = project_path(root, e["path"])
            check("engineering_identity:" + e["path"], helper.sha256(path) == e["sha256"], helper.sha256(path))
            if e["role"] in {"causality", "long_history", "controller_verification"}:
                check("executed_engineering_gate:" + e["path"], e.get("status") == "EXECUTED_PASS_SCOPE_ONLY"
                      and path.suffix == ".json", e.get("status"))
            if "status" in e:
                state = load(path)
                check("engineering_result:" + e["path"], state.get("status") == e["status"]
                      and state.get("exit_code") == 0, {"status": state.get("status"), "exit_code": state.get("exit_code")})
        ref = project_path(root, item["discovery_reference"])
        required = {"summary.json", "source_manifest.json", "input_manifest.json", "daily.csv"}
        check("nominated_reference_set:" + item["candidate_id"], required <= set(item["discovery_reference_sha256"]),
              sorted(item["discovery_reference_sha256"]))
        for rel, digest in item["discovery_reference_sha256"].items():
            if Path(rel).is_absolute() or ".." in Path(rel).parts:
                raise ValueError("Reference entry must be relative")
            check("nominated_reference:" + item["candidate_id"] + "/" + rel, helper.sha256(ref / rel) == digest, digest)
        if active:
            check("requested_entrypoint", source_strategy.name == entry.name, source_strategy.name)
            check("requested_reference", all(helper.sha256(reference / n) == item["discovery_reference_sha256"][n]
                  for n in required), str(reference))
    if args.mode == "audit":
        record = nomination["selection_record"]
        path = project_path(root, record["path"])
        check("selection_record_identity", helper.sha256(path) == record["sha256"], helper.sha256(path))
        selection = load(path)
        check("audit_single_selected_policy", nomination.get("selected_candidate_id") == config["candidate_id"]
              and selection.get("selected_candidate_id") == config["candidate_id"]
              and selection.get("config_sha256") == chosen["config_sha256"], selection.get("selected_candidate_id"))
        shutil.copy2(path, out / "selection_used.json")
    shutil.copy2(manifest_path, out / "nomination_used.json")
    return {Path(k).name: v for k, v in chosen["source_sha256"].items()}


def prepare_inputs(args, root, out, days, helper, check, result):
    folder = out / "inputs"
    folder.mkdir()
    names = ("returns.npy", "characteristics.npy", "costs.npy")
    cache = root / "cache/discovery"
    if args.mode == "synthetic-zero":
        for name, shape, order in (("returns.npy", (days, 1000), True),
                                   ("characteristics.npy", (days, 1000, 13), False)):
            a = np.lib.format.open_memmap(folder / name, mode="w+", dtype=np.float64, shape=shape, fortran_order=order)
            a[:] = 0
            a.flush()
            del a
        np.save(folder / "costs.npy", np.full(1000, 0.00001), allow_pickle=False)
    else:
        check("discovery_cache_identity", {n: helper.sha256(cache / n) for n in names} == helper.CACHE_SHA256,
              helper.CACHE_SHA256)
        if args.mode == "discovery-parity":
            for name in names:
                shutil.copy2(cache / name, folder / name)
        else:
            source = root / "source/Quant Research Take-Home"
            hashes = {n: helper.sha256(source / n) for n in SOURCE_SHA}
            check("canonical_raw_source_identity", hashes == SOURCE_SHA, hashes)
            result["protected_numeric_access_started"] = True
            result["accessed_numeric_input_slice"] = [0, days]
            helper.write_json(out / "summary.json", result)
            import pandas as pd
            r = pd.read_csv(source / "returns.csv", index_col="day", nrows=days)
            c = pd.read_csv(source / "costs.csv", index_col="stock")["cost"]
            check("parsed_returns_schema", r.shape == (days, 1000)
                  and np.array_equal(r.index.to_numpy(), np.arange(1, days + 1))
                  and np.array_equal(r.columns.to_numpy(), c.index.to_numpy()), list(r.shape))
            metadata = load(cache / "metadata.json")
            check("canonical_stock_feature_order", list(r.columns) == metadata["stocks"]
                  and metadata["features"] == FEATURES, {"stocks": len(r.columns), "features": FEATURES})
            np.save(folder / "returns.npy", np.asfortranarray(r.to_numpy(dtype=np.float64)), allow_pickle=False)
            np.save(folder / "costs.npy", c.to_numpy(dtype=np.float64), allow_pickle=False)
            x = np.lib.format.open_memmap(folder / "characteristics.npy", mode="w+", dtype=np.float64,
                                          shape=(days, 1000, 13), fortran_order=False)
            flat, offset = x.reshape(-1, 13), 0
            for frame in pd.read_csv(source / "characteristics.csv", nrows=days * 1000, chunksize=100000):
                locations = np.arange(offset, offset + len(frame))
                if (list(frame.columns) != ["day", "stock"] + FEATURES
                        or not np.array_equal(frame["day"].to_numpy(), locations // 1000 + 1)
                        or not np.array_equal(frame["stock"].to_numpy(), r.columns.to_numpy()[locations % 1000])):
                    raise ValueError("Canonical characteristic keys or order differ")
                values = frame[FEATURES].to_numpy(dtype=np.float64)
                if not np.isfinite(values).all():
                    raise ValueError("Nonfinite characteristic input")
                flat[offset:offset + len(frame)] = values
                offset += len(frame)
            check("bounded_characteristic_rows", offset == days * 1000, offset)
            x.flush()
            del flat, x, r, c
    arrays = tuple(np.load(folder / n, mmap_mode="r", allow_pickle=False) for n in names)
    check("input_shapes_values", [a.shape for a in arrays] == [(days, 1000), (days, 1000, 13), (1000,)]
          and all(a.dtype == np.float64 and np.isfinite(a).all() for a in arrays)
          and np.all(arrays[2] >= 0), [layout(a) for a in arrays])
    check("canonical_input_layout", arrays[0].flags.f_contiguous and not arrays[0].flags.c_contiguous
          and arrays[1].flags.c_contiguous, [layout(a) for a in arrays])
    if args.mode != "synthetic-zero":
        for i, name in enumerate(names):
            old = np.load(cache / name, mmap_mode="r", allow_pickle=False)
            prefix = arrays[i][:2016] if i < 2 else arrays[i]
            check("discovery_input_prefix:" + name, np.array_equal(prefix, old), list(prefix.shape))
    input_manifest = {"kind": "synthetic_exact_zero" if args.mode == "synthetic-zero" else "canonical_market",
                      "input_slice": [0, days], "source_sha256": SOURCE_SHA if args.mode in ("validation", "audit") else None,
                      "files": {n: {"sha256": helper.sha256(folder / n), **layout(a)} for n, a in zip(names, arrays)}}
    helper.write_json(out / "input_manifest.json", input_manifest)
    result["accessed_numeric_input_slice"] = [0, days]
    return arrays, input_manifest


def main():
    global np
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "strategy", "config", "reference", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--mode", choices=tuple(DAYS), required=True)
    parser.add_argument("--cpu", type=int, default=5)
    for name in ("nomination-manifest", "metric-helper", "plan", "protocol", "scorer", "admission-plan"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--nomination-sha256")
    args = parser.parse_args()
    root, strategy_source, config_source, reference, out = (p.resolve() for p in
        (args.project, args.strategy, args.config, args.reference, args.out))
    os.sched_setaffinity(0, {args.cpu})
    import numpy as np
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__).resolve(), out / "runner_used.py")
    shutil.copy2(args.metric_helper or root / "tools/run_candidate.py", out / "metric_helper_used.py")
    if hashlib.sha256((out / "metric_helper_used.py").read_bytes()).hexdigest() != HELPER_SHA:
        (out / "summary.json").write_text(json.dumps({"status": "BLOCKED_HELPER_IDENTITY", "exit_code": 1,
            "protected_numeric_access_started": False, "validation_opened": False, "audit_opened": False}) + "\n")
        raise ValueError("Metric helper differs before import")
    spec = importlib.util.spec_from_file_location("protected_metric_helper", out / "metric_helper_used.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    days = DAYS[args.mode]
    result = {"status": "RUNNING", "started_utc": helper.now(), "mode": args.mode,
              "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
              "expected_input_slice": [0, days], "score_masks": MASKS[args.mode], "checks": [],
              "protected_numeric_access_started": False, "returned_by_official_scorer": False,
              "validation_opened": False, "audit_opened": False, "completed_rebalances": 0}
    helper.write_json(out / "summary.json", result)
    arrays = rows = forecasts = None
    targets, held_books, earning_days, candidate_seconds, captured_fees, captured_gross = [], [], [], [], [], []
    source_hashes, input_hashes = {}, {}
    exit_code = 1

    def check(name, condition, actual):
        row = {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual}
        result["checks"].append(row)
        print(json.dumps(helper.json_value(row), allow_nan=False), flush=True)
        helper.write_json(out / "summary.json", result)
        if not condition:
            raise AssertionError(name)

    def compare(name, actual, expected, exact=False):
        same = actual.shape == expected.shape
        error = np.abs(actual - expected) if same else np.array([np.inf])
        passed = same and np.isfinite(actual).all() and np.isfinite(expected).all()
        passed = passed and (np.array_equal(actual, expected) if exact else np.all(error <= ATOL + RTOL * np.abs(expected)))
        check(name, passed, {"shape": list(actual.shape), "expected_shape": list(expected.shape),
              "exact_required": exact, "exact_observed": bool(same and np.array_equal(actual, expected)),
              "max_abs_error": float(error.max()) if error.size else None, "atol": ATOL, "rtol": RTOL})

    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(helper.Tee(sys.stdout, stdout)), contextlib.redirect_stderr(helper.Tee(sys.stderr, stderr)):
            try:
                copies = {"expectations.md": args.plan or root / "verification/PROTECTED_REPLAY_PLAN.md",
                          "protocol_used.json": args.protocol or root / "RESEARCH_PROTOCOL.json",
                          "admission_plan_used.md": args.admission_plan or root / "research/PROTECTED_EVALUATION_ADMISSION_PLAN.md",
                          "config.json": config_source}
                for name, source in copies.items():
                    shutil.copy2(source, out / name)
                check("controller_contract_identities", helper.sha256(out / "expectations.md") == PLAN_SHA
                      and helper.sha256(out / "protocol_used.json") == PROTOCOL_SHA
                      and helper.sha256(out / "admission_plan_used.md") == ADMISSION_SHA
                      and helper.sha256(out / "metric_helper_used.py") == HELPER_SHA, list(copies))
                protocol = load(out / "protocol_used.json")
                expected_periods = {p["name"]: tuple(p["score_slice"]) for p in protocol["periods"]}
                check("frozen_masks", all(expected_periods[n] == bounds for n, bounds in MASKS[args.mode].items())
                      and protocol["replay"]["start"] == 252, MASKS[args.mode])
                config = load(out / "config.json")
                result["configuration"] = config
                if args.mode in ("discovery-parity", "synthetic-zero"):
                    check("fixed_engineering_configuration", config.get("candidate_id") == "C06_gls_factor"
                          and helper.sha256(out / "config.json") == C06_CONFIG_SHA, helper.sha256(out / "config.json"))
                ref_summary, ref_sources = load(reference / "summary.json"), load(reference / "source_manifest.json")
                ref_inputs = load(reference / "input_manifest.json")
                check("historical_reference_completed", ref_summary.get("status") == "EXECUTED_PASS_SCOPE_ONLY"
                      and ref_summary.get("exit_code") == 0 and ref_summary.get("configuration") == config,
                      {"status": ref_summary.get("status"), "candidate_id": config.get("candidate_id")})
                check("historical_reference_scope", ref_inputs.get("input_slice") == [0, 2016]
                      and ref_inputs.get("cache_sha256") == helper.CACHE_SHA256
                      and ref_sources.get("protocol_used.json") == PROTOCOL_SHA, ref_inputs.get("input_slice"))
                historical_sources = {Path(k).name: v for k, v in ref_sources.items() if k.startswith("source/candidate/")}
                chosen_sources = historical_sources
                if args.mode in ("validation", "audit"):
                    chosen_sources = admit(args, root, out, config, strategy_source, reference, helper, check)
                check("historical_dependency_closure", all(chosen_sources.get(n) == v for n, v in historical_sources.items())
                      and strategy_source.name in chosen_sources and helper.sha256(config_source) == ref_sources["config.json"], chosen_sources)
                folder = out / "source/candidate"
                folder.mkdir(parents=True)
                for name, expected in chosen_sources.items():
                    source = strategy_source.parent / name
                    check("candidate_source:" + name, helper.sha256(source) == expected, helper.sha256(source))
                    shutil.copy2(source, folder / name)
                scorer_path = out / "source/score.py"
                shutil.copy2(args.scorer or root / "source/Quant Research Take-Home/score.py", scorer_path)
                check("original_scorer_identity", helper.sha256(scorer_path) == SCORER_SHA
                      and ref_sources["source/score.py"] == SCORER_SHA, helper.sha256(scorer_path))
                (out / "reference").mkdir()
                for name in ("summary.json", "source_manifest.json", "input_manifest.json", "daily.csv"):
                    shutil.copy2(reference / name, out / "reference" / name)
                environment = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                               "pid": os.getpid(), "cpu_affinity": sorted(os.sched_getaffinity(0)),
                               "thread_environment": {k: os.environ[k] for k in THREAD_KEYS},
                               "packages": {p: importlib.metadata.version(p) for p in ("numpy", "pandas", "scipy")}}
                helper.write_json(out / "environment.json", environment)
                result["process_controls"] = environment
                source_files = list((out / "source").rglob("*.py")) + list((out / "reference").iterdir())
                source_files += [out / n for n in ("runner_used.py", "metric_helper_used.py", *copies)]
                source_files += [out / n for n in ("nomination_used.json", "selection_used.json") if (out / n).exists()]
                source_hashes = {str(p.relative_to(out)): helper.sha256(p) for p in source_files}
                helper.write_json(out / "source_manifest.json", source_hashes)
                rerun = [sys.executable, str(out / "runner_used.py"), "--project", str(root), "--mode", args.mode,
                         "--strategy", str(folder / strategy_source.name), "--config", str(out / "config.json"),
                         "--reference", str(out / "reference"), "--out", str(out) + "_rerun", "--cpu", str(args.cpu),
                         "--metric-helper", str(out / "metric_helper_used.py"), "--plan", str(out / "expectations.md"),
                         "--protocol", str(out / "protocol_used.json"), "--scorer", str(scorer_path),
                         "--admission-plan", str(out / "admission_plan_used.md")]
                if args.mode in ("validation", "audit"):
                    rerun += ["--nomination-manifest", str(out / "nomination_used.json"), "--nomination-sha256", args.nomination_sha256]
                (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
                (out / "setup.md").write_text("# Frozen continuous replay\n\nRead expectations.md before rerunning. "
                    "The rerun command uses copied code/config/helper/reference and a new output directory. "
                    "Actual protected parsing requires the unchanged root-approved manifest and explicit root release. "
                    "Synthetic metrics are engineering evidence only. No model selection occurs in this controller.\n")
                arrays, manifest = prepare_inputs(args, root, out, days, helper, check, result)
                input_hashes = {n: m["sha256"] for n, m in manifest["files"].items()}
                result["validation_opened"] = args.mode in ("validation", "audit")
                result["audit_opened"] = args.mode == "audit"
                returns, chars, costs = arrays
                sys.path.insert(0, str(folder))
                strategy = helper.import_file(folder / strategy_source.name, "protected_candidate")
                scorer = helper.import_file(scorer_path, "protected_original_scorer")
                strategy.configure(config)
                check("consumed_configuration", strategy.CONFIG == config, strategy.CONFIG)
                candidate_rebalance = scorer.with_declared_arguments(strategy.rebalance)
                forecast_calls, forecast_seconds = 0, 0.0

                def forecast(**named):
                    nonlocal forecasts, forecast_calls, forecast_seconds
                    forecast_calls += 1
                    tick = time.perf_counter()
                    forecasts = np.asarray(scorer.with_declared_arguments(strategy.forecast)(**named), dtype=np.float64)
                    forecast_seconds = time.perf_counter() - tick
                    check("complete_forecasts", forecasts.shape == (days, 1000) and np.isfinite(forecasts).all(), list(forecasts.shape))
                    forecasts.setflags(write=False)
                    if args.mode != "synthetic-zero":
                        p = out / "discovery_forecast_prefix.npy"
                        np.save(p, forecasts[:2016], allow_pickle=False)
                        check("exact_discovery_forecast_prefix", helper.sha256(p) == ref_summary["output_arrays"]["forecasts.npy"]["sha256"], helper.sha256(p))
                    return forecasts

                def rebalance(**named):
                    held = named["held_positions"].copy()
                    tick = time.perf_counter()
                    target = np.asarray(candidate_rebalance(**named), dtype=np.float64)
                    elapsed = time.perf_counter() - tick
                    day = len(named["returns_history"])
                    if target.shape != (1000,) or not np.isfinite(target).all() or not np.array_equal(named["held_positions"], held):
                        raise ValueError("Invalid target or mutated scorer holdings")
                    if np.max(np.abs(target)) > config["weight_cap"] + 1e-12 or np.abs(target).sum() > config["gross_cap"] + 1e-12:
                        raise ValueError("Position controls exceeded")
                    earning_days.append(day)
                    targets.append(target.copy())
                    held_books.append(held)
                    candidate_seconds.append(elapsed)
                    captured_fees.append(float(costs @ np.abs(target - held)))
                    captured_gross.append(float(np.abs(target).sum()))
                    if len(targets) % 250 == 0:
                        result["completed_rebalances"] = len(targets)
                        helper.write_json(out / "summary.json", result)
                    return target

                rows, official_forecast_seconds = scorer.run(SimpleNamespace(forecast=forecast, rebalance=rebalance), *arrays, start=252)
                result["returned_by_official_scorer"] = True
                days_scored = np.arange(253, days - 1)
                target_array, held_array = np.asarray(targets), np.asarray(held_books)
                check("complete_continuous_path", forecast_calls == 1 and len(targets) == days - 253
                      and np.array_equal(earning_days, np.arange(253, days)) and rows.shape == (days - 254, 5)
                      and np.isfinite(rows).all(), {"forecasts_called": forecast_calls, "targets": len(targets), "rows": len(rows)})
                compare("exact_captured_full_costs", rows[:, 1], np.array(captured_fees[1:]), True)
                compare("exact_captured_target_gross", rows[:, 2], np.array(captured_gross[1:]), True)
                gross = np.einsum("ij,ij->i", target_array[:-1], returns[days_scored])
                drift = target_array[:-1] * (1 + returns[days_scored]) / (1 + gross[:, None])
                compare("reconciled_gross", rows[:, 0], gross)
                compare("reconciled_drifted_holdings", held_array[1:], drift)
                compare("reconciled_full_costs", rows[:, 1], np.abs(target_array[1:] - drift) @ costs)
                check("full_path_solvency", np.all(rows[:, 0] > -1) and np.all(rows[:, 0] - rows[:, 1] > -1), float((rows[:, 0] - rows[:, 1]).min()))
                if args.mode != "synthetic-zero":
                    for filename, value in (("targets.npy", target_array[:1763]), ("held_books.npy", held_array[:1763])):
                        path = out / ("discovery_" + filename)
                        np.save(path, value, allow_pickle=False)
                        check("exact_discovery_prefix:" + filename, helper.sha256(path) == ref_summary["output_arrays"][filename]["sha256"], helper.sha256(path))
                    with (out / "reference/daily.csv").open(newline="") as stream:
                        old = list(csv.DictReader(stream))
                    check("reference_score_indices", np.array_equal([int(r["return_index"]) for r in old], np.arange(253, 2015)), len(old))
                    old_values = np.array([[float(r[k]) for k in ("gross_return", "full_cost", "closing_target_gross", "raw_market_return")] for r in old])
                    compare("exact_discovery_economic_prefix", rows[:1762, :4], old_values, True)
                    compare("exact_discovery_net_prefix", rows[:1762, 0] - rows[:1762, 1], np.array([float(r["net_return"]) for r in old]), True)
                else:
                    check("exact_cash_path", all(np.count_nonzero(a) == 0 for a in (forecasts, target_array, held_array, rows[:, :4])), "exact zero forecasts/targets/held/economics")
                    result["historical_prefix_reconciliation"] = "NOT_APPLICABLE_SYNTHETIC_VALUES"
                result["metrics"] = {}
                for name, (start, stop) in MASKS[args.mode].items():
                    mask = (days_scored >= start) & (days_scored < stop)
                    check("exact_mask:" + name, np.array_equal(days_scored[mask], np.arange(start, stop)), {"slice": [start, stop], "rows": int(mask.sum())})
                    result["metrics"][name] = helper.summarize_rows(rows[mask], days_scored[mask])
                    metrics = result["metrics"][name]
                    if args.mode == "synthetic-zero":
                        check("undefined_cash_metrics:" + name, metrics["net_sharpe"] is None
                              and metrics["gross_sharpe"] is None and metrics["realized_net_market_beta"] is None
                              and metrics["annual_arithmetic_net_return"] == 0 and metrics["annual_full_cost"] == 0,
                              metrics["undefined_metrics"])
                    report = io.StringIO()
                    with contextlib.redirect_stdout(report):
                        if metrics["net_sharpe"] is not None and metrics["realized_net_market_beta"] is not None:
                            scorer.report(config["candidate_id"] + ":" + name, rows[mask], official_forecast_seconds, days)
                        else:
                            print("Official ratio report skipped: zero variance; see explicit null metrics in summary.json")
                    (out / ("official_report_" + name + ".txt")).write_text(report.getvalue())
                timings = np.array(candidate_seconds) * 1000
                result["timing"] = {"forecast_candidate_seconds": forecast_seconds, "forecast_official_seconds": official_forecast_seconds,
                                    "mean_candidate_rebalance_ms": float(timings.mean()), "max_candidate_rebalance_ms": float(timings.max())}
                result["trading"] = {"maximum_abs_stock_weight": float(np.max(np.abs(target_array))),
                                     "maximum_gross": float(np.max(np.abs(target_array).sum(axis=1))),
                                     "opening_full_cost_waived": captured_fees[0], "paid_full_cost_sum": float(rows[:, 1].sum())}
                primary = result["metrics"]["pooled_validation" if args.mode in ("validation", "synthetic-zero") else "locked_audit" if args.mode == "audit" else "discovery"]
                beta = primary["realized_net_market_beta"]
                result["candidate_feasibility"] = {"scope": "NOT_APPLICABLE_SYNTHETIC" if args.mode == "synthetic-zero" else args.mode,
                    "realized_abs_beta_below_0_2": beta is not None and abs(beta) < .2,
                    "candidate_mean_rebalance_below_100ms": float(timings.mean()) < 100,
                    "net_solvency": not primary["net_bankruptcy_observed"], "position_controls": True}
                result["status"], exit_code = "EXECUTED_PASS_SCOPE_ONLY", 0
            except KeyboardInterrupt:
                result["status"], exit_code = "INCOMPLETE", 130
                result["error"] = traceback.format_exc()
                traceback.print_exc()
            except Exception:
                result["status"] = "EXECUTED_FAIL"
                result["error"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                try:
                    if arrays is not None:
                        result["input_hashes_after"] = {n: helper.sha256(out / "inputs" / n) for n in input_hashes}
                        check("input_files_unchanged", result["input_hashes_after"] == input_hashes, result["input_hashes_after"])
                    if source_hashes:
                        check("frozen_sources_unchanged", all(helper.sha256(out / n) == h for n, h in source_hashes.items()), len(source_hashes))
                    if forecasts is not None:
                        np.save(out / "forecasts.npy", forecasts, allow_pickle=False)
                    if targets:
                        np.save(out / "targets.npy", np.asarray(targets), allow_pickle=False)
                        np.save(out / "held_books.npy", np.asarray(held_books), allow_pickle=False)
                        np.save(out / "candidate_rebalance_seconds.npy", np.array(candidate_seconds), allow_pickle=False)
                        helper.write_csv(out / "targets.csv", [{"earning_index": d, "candidate_rebalance_seconds": t,
                            "full_trade_cost": fee, "target_gross": g} for d, t, fee, g in zip(earning_days, candidate_seconds, captured_fees, captured_gross)],
                            ["earning_index", "candidate_rebalance_seconds", "full_trade_cost", "target_gross"])
                    if rows is not None:
                        helper.write_csv(out / "daily.csv", [{"return_index": i + 253, "csv_day_label": i + 254,
                            "gross_return": float(r[0]), "full_cost": float(r[1]), "net_return": float(r[0] - r[1]),
                            "closing_target_gross": float(r[2]), "raw_market_return": float(r[3]),
                            "official_instrumented_rebalance_seconds": float(r[4])} for i, r in enumerate(rows)],
                            ["return_index", "csv_day_label", "gross_return", "full_cost", "net_return", "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds"])
                    result["output_arrays"] = {p.name: {"sha256": helper.sha256(p), "bytes": p.stat().st_size} for p in out.glob("*.npy")}
                except Exception:
                    result["evidence_error"] = traceback.format_exc()
                    result["status"], exit_code = "INCOMPLETE", 1
                    traceback.print_exc()
                result["completed_rebalances"] = len(targets)
                result["validation_opened"] = result["protected_numeric_access_started"] and args.mode in ("validation", "audit")
                result["audit_opened"] = result["protected_numeric_access_started"] and args.mode == "audit"
                result["exit_code"], result["finished_utc"] = exit_code, helper.now()
                result["limitations"] = ["A completed replay is not evidence of no selection overfit or guaranteed future alpha.",
                    "No model selection or retuning occurs here; the root-owned protocol controls those decisions.",
                    "Synthetic/parity controller checks do not open a protected market period."]
                helper.write_json(out / "summary.json", result)
                print(result["status"], flush=True)
    helper.write_json(out / "artifact_manifest.json", {str(p.relative_to(out)): {"sha256": helper.sha256(p), "bytes": p.stat().st_size}
        for p in sorted(out.rglob("*")) if p.is_file() and p.name != "artifact_manifest.json"})
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
