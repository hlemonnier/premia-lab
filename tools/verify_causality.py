#!/usr/bin/env python3
"""Fresh-process candidate causality E2E on a bounded discovery prefix.

See verification/CAUSALITY_PLAN.md. This file contains both the controller and
the standalone worker; each scenario starts a new Python interpreter. It does
not select models or calculate an alpha ranking.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import dataclasses
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace


ATOL, RTOL = 1e-14, 1e-12
SCORER_SHA256 = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
THREAD_VARIABLES = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)


def now():
    return datetime.now(timezone.utc).isoformat()


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_hash(array):
    return hashlib.sha256(memoryview(np.ascontiguousarray(array)).cast("B")).hexdigest()


def array_layout(array):
    return {"shape": list(array.shape), "strides": list(array.strides), "dtype": str(array.dtype),
            "c_contiguous": bool(array.flags.c_contiguous), "f_contiguous": bool(array.flags.f_contiguous)}


def append_preserving_order(array, suffix):
    """Keep the canonical source's C/F representation when adding test rows."""
    order = "F" if array.flags.f_contiguous and not array.flags.c_contiguous else "C"
    result = np.empty((len(array) + len(suffix), *array.shape[1:]), dtype=array.dtype, order=order)
    result[:len(array)] = array
    result[len(array):] = suffix
    return result


def ready(value):
    if hasattr(value, "tolist"):
        return ready(value.tolist())
    if isinstance(value, dict):
        return {str(k): ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [ready(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(ready(value), indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def log_line(out, message):
    with (out / "controller.stdout.log").open("a") as stream:
        stream.write(message + "\n")
    print(message, flush=True)


def constrain_threads():
    for name in THREAD_VARIABLES:
        os.environ[name] = "1"
    result = {"thread_environment": {k: os.environ[k] for k in THREAD_VARIABLES}}
    try:
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {available[0]})
        result["cpu_affinity"] = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError, IndexError) as exc:
        result["cpu_affinity_unavailable"] = str(exc)
    return result


def environment():
    packages = {}
    for name in ("numpy", "pandas", "scipy", "cvxpy", "scikit-learn", "lightgbm"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_INSTALLED"
    return {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "packages": packages, "pid": os.getpid(), "parent_pid": os.getppid()}


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # Required by dataclasses and ordinary module imports.
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def scenario_inputs(inputs, scenario):
    base_returns = np.load(inputs / "returns.npy", allow_pickle=False)
    base_chars = np.load(inputs / "characteristics.npy", allow_pickle=False)
    base_costs = np.load(inputs / "costs.npy", allow_pickle=False)
    costs = base_costs.copy(order="K")
    returns, chars = base_returns.copy(order="K"), base_chars.copy(order="K")
    kind = scenario["kind"]
    alteration = {"kind": kind, "returns_changed": 0, "characteristics_changed": 0,
                  "source_layouts": [array_layout(a) for a in (base_returns, base_chars, base_costs)]}
    if kind == "suffix":
        cut, mode = scenario["cutoff"], scenario["mode"]
        if mode in ("returns", "joint"):
            returns[cut:] *= 0.5
        if mode in ("characteristics", "joint"):
            if len(chars) - cut > 1:
                chars[cut:] = base_chars[cut:][::-1]
            else:
                chars[cut] = base_chars[0]
        alteration.update({"cutoff": cut, "mode": mode,
                           "returns_changed": int(np.count_nonzero(returns != base_returns)),
                           "characteristics_changed": int(np.count_nonzero(chars != base_chars)),
                           "prefix_returns_unchanged": bool(np.array_equal(returns[:cut], base_returns[:cut])),
                           "prefix_characteristics_unchanged": bool(np.array_equal(chars[:cut], base_chars[:cut]))})
        require(alteration["prefix_returns_unchanged"] and alteration["prefix_characteristics_unchanged"],
                "Perturbation modified a protected input prefix")
        if mode in ("returns", "joint"):
            require(alteration["returns_changed"] > 0, "Return perturbation is an identity intervention")
        if mode in ("characteristics", "joint"):
            require(alteration["characteristics_changed"] > 0, "Characteristic perturbation is an identity intervention")
    elif kind == "prefix":
        returns = returns[:scenario["length"]].copy(order="K")
        chars = chars[:scenario["length"]].copy(order="K")
    elif kind == "append":
        count = scenario["append_days"]
        require(0 < count <= len(base_returns), "Invalid synthetic append length")
        returns = append_preserving_order(returns, 0.5 * base_returns[:count][::-1])
        chars = append_preserving_order(chars, base_chars[:count][::-1])
        alteration["synthetic_append_days"] = count
        alteration["synthetic_recipe"] = "Reverse first append_days permitted panels; scale their returns by0.5"
    elif kind not in ("baseline", "repeat"):
        raise ValueError(f"Unknown scenario kind: {kind}")
    require(returns.ndim == 2 and returns.shape[1] == 1000, "Candidate interface requires1000 stocks")
    require(chars.shape == (*returns.shape, 13), "Characteristic shape mismatch")
    require(costs.shape == (1000,), "Cost shape mismatch")
    require(all(np.isfinite(a).all() for a in (returns, chars, costs)), "Nonfinite scenario input")
    require(bool((costs >= 0).all()), "Negative costs")
    return (returns, chars, costs), alteration


def save_daily(path, rows, days):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["array_index", "csv_day", "gross_return", "cost", "net_return",
                         "target_gross", "market_return", "rebalance_seconds"])
        for day, row in zip(days, rows):
            gross, cost, exposure, market, seconds = row
            writer.writerow([int(day), int(day) + 1, gross, cost, gross - cost, exposure, market, seconds])


def worker(manifest_path):
    global np
    config = json.loads(manifest_path.read_text())
    out, scenario = Path(config["output"]), config["scenario"]
    out.mkdir(parents=True, exist_ok=False)
    status = {"status": "running", "started_utc": now(), "scenario": scenario,
              "command": shlex.join([sys.executable, str(Path(__file__).resolve()), "--worker", str(manifest_path)]),
              "process_controls": constrain_threads(), "returned_by_scorer": False}
    write_json(out / "status.json", status)
    forecast_saved = None
    target_days, targets = [], []
    observed = {}
    arrays = None
    rows = None
    exit_code = 1
    try:
        import numpy as np
        status["environment"] = environment()
        arrays, alteration = scenario_inputs(Path(config["inputs"]), scenario)
        status["alteration"] = alteration
        status["input_shapes"] = [list(a.shape) for a in arrays]
        status["input_layouts"] = [array_layout(a) for a in arrays]
        status["input_hashes_before"] = [array_hash(a) for a in arrays]
        for array in arrays:
            array.setflags(write=False)
        write_json(out / "input_manifest.json", {"base": config["input_manifest"], "scenario": scenario,
                   "actual_array_hashes": status["input_hashes_before"],
                   "actual_array_layouts": status["input_layouts"], "alteration": alteration})
        strategy_path, scorer_path = Path(config["strategy"]), Path(config["scorer"])
        sys.path.insert(0, str(strategy_path.parent))
        strategy = import_file(strategy_path, strategy_path.stem)
        scorer = import_file(scorer_path, "causality_original_scorer")
        status["source_hashes"] = {str(p): file_hash(p) for p in sorted(strategy_path.parent.glob("*.py"))}
        status["scorer_sha256"] = file_hash(scorer_path)
        require(status["scorer_sha256"] == SCORER_SHA256, "Supplied scorer identity differs")
        config_path = Path(config["candidate_config"])
        config_sha256 = file_hash(config_path)
        require(config_sha256 == config["candidate_config_sha256"], "Frozen candidate configuration differs")
        candidate_config = json.loads(config_path.read_text())
        require(isinstance(candidate_config, dict), "Candidate configuration must be a JSON object")
        if callable(getattr(strategy, "configure", None)):
            strategy.configure(candidate_config)
        elif candidate_config:
            raise ValueError("Nonempty configuration requires strategy.configure(config)")
        status["requested_config"] = candidate_config
        status["requested_config_sha256"] = config_sha256
        cfg = getattr(strategy, "CONFIG", None)
        if dataclasses.is_dataclass(cfg):
            status["candidate_config"] = dataclasses.asdict(cfg)
        elif isinstance(cfg, (dict, list, tuple, str, int, float, bool, type(None))):
            status["candidate_config"] = cfg
        else:
            status["candidate_config_type"] = type(cfg).__qualname__
        require(callable(getattr(strategy, "rebalance", None)), "Candidate lacks rebalance")
        candidate_rebalance = scorer.with_declared_arguments(strategy.rebalance)
        forecast_count = scenario["forecast_count"]
        target_limit = scenario["earning_day_limit"]
        positions_valid = {"calls": 0, "all_shapes_valid": True, "all_finite": True, "held_input_unchanged": True}

        def traced_forecast(**named):
            nonlocal forecast_saved
            result = np.asarray(scorer.with_declared_arguments(strategy.forecast)(**named), dtype=float)
            require(result.ndim >= 1 and len(result) == len(arrays[0]), "Invalid forecast time axis")
            require(bool(np.isfinite(result).all()), "Nonfinite forecast output")
            status["forecast_full_shape"] = list(result.shape)
            status["forecast_full_hash"] = array_hash(result)
            forecast_saved = result[:forecast_count].copy()
            return result

        def traced_rebalance(**named):
            earning_day = len(named["returns_history"])
            held = named["held_positions"].copy()
            result = np.asarray(candidate_rebalance(**named), dtype=float)
            positions_valid["calls"] += 1
            positions_valid["all_shapes_valid"] &= result.shape == (1000,)
            positions_valid["all_finite"] &= bool(np.isfinite(result).all())
            positions_valid["held_input_unchanged"] &= bool(np.array_equal(held, named["held_positions"]))
            require(positions_valid["all_shapes_valid"] and positions_valid["all_finite"], "Invalid candidate positions")
            require(positions_valid["held_input_unchanged"], "Candidate mutated held_positions and scorer accounting")
            if earning_day <= target_limit:
                target_days.append(earning_day)
                targets.append(result.copy())
            return result

        proxy = SimpleNamespace(rebalance=traced_rebalance)
        status["has_forecast"] = callable(getattr(strategy, "forecast", None))
        if status["has_forecast"]:
            proxy.forecast = traced_forecast

        tic = time.perf_counter()
        try:
            rows, forecast_seconds = scorer.run(proxy, *arrays, start=252)
        except BaseException as exc:
            # Read the original scorer's existing partial ledger only when
            # needed. A global profile hook would instrument every numerical
            # call and materially distort the normal workflow's runtime.
            trace = exc.__traceback__
            while trace is not None:
                frame = trace.tb_frame
                if frame.f_code is scorer.run.__code__:
                    observed["raw_rows"] = np.asarray(frame.f_locals.get("rows", []), dtype=float).copy()
                    break
                trace = trace.tb_next
            raise
        finally:
            status["execution_seconds"] = time.perf_counter() - tic
            status["position_checks"] = positions_valid
        status["returned_by_scorer"] = True
        status["forecast_seconds_instrumented"] = forecast_seconds
        require(rows.shape == (len(arrays[0]) - 254, 5), "Unexpected official score row count")
        require(bool(np.isfinite(rows).all()), "Nonfinite scorer rows")
        status["status"] = "EXECUTED_PASS"
        exit_code = 0
    except KeyboardInterrupt:
        status["status"] = "INCOMPLETE"
        status["error"] = traceback.format_exc()
        traceback.print_exc()
        exit_code = 130
    except Exception:
        status["status"] = "EXECUTED_FAIL"
        status["error"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        if arrays is not None:
            status["input_hashes_after"] = [array_hash(a) for a in arrays]
            status["inputs_unchanged"] = status["input_hashes_after"] == status.get("input_hashes_before")
            if not status["inputs_unchanged"]:
                status["status"] = "EXECUTED_FAIL"
                status["input_mutation_detected"] = True
                exit_code = 1
        if "np" in globals():
            if rows is None:
                raw = observed.get("raw_rows", np.empty((0, 5)))
                rows = raw[1:] if raw.ndim == 2 and raw.shape[1:] == (5,) else np.empty((0, 5))
            score_days = np.arange(253, 253 + len(rows), dtype=int)
            keep = score_days < scenario["score_day_exclusive"]
            payload = {"targets": np.array(targets, dtype=float).reshape(-1, 1000),
                       "target_earning_days": np.array(target_days, dtype=int),
                       "scored_rows": rows[keep], "score_days": score_days[keep]}
            if forecast_saved is not None:
                payload["forecast_prefix"] = forecast_saved
            np.savez_compressed(out / "protected_outputs.npz", **payload)
            save_daily(out / "daily.csv", rows, score_days)
            status["saved_shapes"] = {k: list(v.shape) for k, v in payload.items()}
            status["output_sha256"] = file_hash(out / "protected_outputs.npz")
        status["finished_utc"], status["exit_code"] = now(), exit_code
        write_json(out / "status.json", status)
        print(f"{scenario['name']}: {status['status']}; pid {os.getpid()}", flush=True)
    return exit_code


def comparison(name, actual, expected):
    same_shape = actual.shape == expected.shape
    entry = {"name": name, "actual_shape": list(actual.shape), "expected_shape": list(expected.shape),
             "atol": ATOL, "rtol": RTOL}
    if not same_shape:
        return {**entry, "status": "FAIL", "reason": "shape_mismatch"}
    if not actual.size:
        return {**entry, "status": "NOT_APPLICABLE", "reason": "empty_protected_range"}
    difference = np.abs(actual - expected)
    allowed = ATOL + RTOL * np.abs(expected)
    finite = bool(np.isfinite(actual).all() and np.isfinite(expected).all())
    bad = ~np.isfinite(difference) | (difference > allowed)
    entry.update({"status": "PASS" if finite and not bad.any() else "FAIL",
                  "elements": int(actual.size), "mismatched_elements": int(np.count_nonzero(bad)),
                  "max_abs_error": float(difference.max()),
                  "max_relative_error": float(np.max(difference / np.maximum(np.abs(expected), ATOL)))})
    if bad.any():
        entry["first_mismatch_index"] = [int(x) for x in np.argwhere(bad)[0]]
    if actual.ndim == 3:
        entry["all_output_channels"] = [
            {"channel": i, "max_abs_error": float(difference[..., i].max()),
             "mismatched_elements": int(np.count_nonzero(bad[..., i]))} for i in range(actual.shape[-1])]
    return entry


def compare_case(out, baseline_status, baseline, scenario):
    child = out / "workers" / scenario["name"]
    status_path = child / "status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {"status": "MISSING"}
    result = {"scenario": scenario, "worker_status": status.get("status"), "comparisons": []}
    if status.get("input_mutation_detected", False):
        result.update({"status": "FAIL", "reason": "caller_input_mutation"})
        return result
    if status.get("status") != "EXECUTED_PASS":
        result.update({"status": "UNVERIFIED", "reason": "worker_did_not_complete",
                       "note": "A later suffix failure alone is not a prefix-leakage diagnosis; worker logs are preserved."})
        return result
    if not status.get("inputs_unchanged", False):
        result.update({"status": "FAIL", "reason": "caller_input_mutation"})
        return result
    if status.get("has_forecast") != baseline_status.get("has_forecast"):
        result.update({"status": "FAIL", "reason": "forecast_interface_changed"})
        return result
    if status.get("requested_config_sha256") != baseline_status.get("requested_config_sha256"):
        result.update({"status": "FAIL", "reason": "candidate_configuration_changed"})
        return result
    with np.load(child / "protected_outputs.npz", allow_pickle=False) as actual:
        if status.get("has_forecast"):
            if "forecast_prefix" not in actual or "forecast_prefix" not in baseline:
                result["comparisons"].append({"name": "forecast_all_channels", "status": "FAIL", "reason": "missing_output"})
            else:
                result["comparisons"].append(comparison("forecast_all_channels", actual["forecast_prefix"],
                                                       baseline["forecast_prefix"][:scenario["forecast_count"]]))
        else:
            result["comparisons"].append({"name": "forecast_all_channels", "status": "NOT_APPLICABLE", "reason": "no_forecast"})
        target_mask = baseline["target_earning_days"] <= scenario["earning_day_limit"]
        expected_days = baseline["target_earning_days"][target_mask]
        result["comparisons"].append({"name": "target_day_indices", "status": "PASS" if np.array_equal(actual["target_earning_days"], expected_days) else "FAIL",
                                      "actual": actual["target_earning_days"].tolist(), "expected": expected_days.tolist()})
        result["comparisons"].append(comparison("protected_targets", actual["targets"], baseline["targets"][target_mask]))
        score_mask = baseline["score_days"] < scenario["score_day_exclusive"]
        expected_score_days = baseline["score_days"][score_mask]
        result["comparisons"].append({"name": "score_day_indices", "status": "PASS" if np.array_equal(actual["score_days"], expected_score_days) else "FAIL",
                                      "actual": actual["score_days"].tolist(), "expected": expected_score_days.tolist()})
        result["comparisons"].append(comparison("protected_gross_cost_exposure_market", actual["scored_rows"][:, :4],
                                               baseline["scored_rows"][score_mask, :4]))
        actual_net = actual["scored_rows"][:, 0] - actual["scored_rows"][:, 1]
        expected_net = baseline["scored_rows"][score_mask, 0] - baseline["scored_rows"][score_mask, 1]
        result["comparisons"].append(comparison("protected_net", actual_net, expected_net))
    result["status"] = "FAIL" if any(c["status"] == "FAIL" for c in result["comparisons"]) else "PASS"
    return result


def freeze_project(args, out):
    root = args.project
    metadata_path = root / "cache" / "discovery" / "metadata.json"
    metadata = json.loads(metadata_path.read_text())
    require(metadata.get("status") == "READY", "Discovery cache metadata is not READY")
    permitted = metadata.get("input_slice")
    require(isinstance(permitted, list) and len(permitted) == 2 and permitted[0] == 0
            and args.days <= permitted[1] <= 2016, "Cache provenance exceeds or cannot supply the permitted discovery prefix")
    frozen = out / "project"
    cache = frozen / "cache" / "discovery"
    cache.mkdir(parents=True)
    input_manifest = []
    for name in ("returns.npy", "characteristics.npy", "costs.npy"):
        source = metadata_path.parent / name
        source_hash = file_hash(source)
        require(source_hash == metadata["cache_sha256"][name], f"Discovery cache hash mismatch: {name}")
        source_array = np.load(source, mmap_mode="r", allow_pickle=False)
        bounded = source_array if name == "costs.npy" else source_array[:args.days]
        np.save(cache / name, np.array(bounded, dtype=float, copy=True))
        input_manifest.append({"name": name, "source_path": str(source), "source_sha256": source_hash,
                               "frozen_path": str(cache / name), "frozen_sha256": file_hash(cache / name),
                               "shape": list(bounded.shape), "array_sha256": array_hash(bounded)})
    frozen_metadata = {**metadata, "input_slice": [0, args.days], "day_labels": [1, args.days],
                       "shape_returns": [args.days, 1000], "shape_characteristics": [args.days, 1000, 13],
                       "cache_sha256": {i["name"]: i["frozen_sha256"] for i in input_manifest},
                       "source_metadata": metadata}
    write_json(cache / "metadata.json", frozen_metadata)
    write_json(out / "input_manifest.json", {"accessed_numeric_rows": [0, args.days], "files": input_manifest,
               "source_cache_slice": permitted, "source_metadata": metadata})
    submission = frozen / "submission"
    submission.mkdir()
    code_manifest = []
    for source in sorted(args.strategy.parent.glob("*.py")):
        target = submission / source.name
        shutil.copyfile(source, target)
        code_manifest.append({"source": str(source), "frozen": str(target), "sha256": file_hash(target)})
    require((submission / args.strategy.name).is_file(), "Candidate strategy was not frozen")
    scorer_source = root / "source" / "Quant Research Take-Home" / "score.py"
    require(file_hash(scorer_source) == SCORER_SHA256, "Official scorer identity mismatch")
    scorer_target = frozen / "source" / "Quant Research Take-Home" / "score.py"
    scorer_target.parent.mkdir(parents=True)
    shutil.copyfile(scorer_source, scorer_target)
    plan_target = frozen / "verification" / "CAUSALITY_PLAN.md"
    plan_target.parent.mkdir()
    shutil.copyfile(root / "verification" / "CAUSALITY_PLAN.md", plan_target)
    shutil.copyfile(plan_target, out / "expectations.md")
    config_target = frozen / "candidate_config.json"
    shutil.copyfile(args.config, config_target)
    protocol_target = frozen / "RESEARCH_PROTOCOL.json"
    shutil.copyfile(root / "RESEARCH_PROTOCOL.json", protocol_target)
    write_json(out / "source_manifest.json", {"candidate": code_manifest, "scorer_sha256": SCORER_SHA256,
               "runner_sha256": file_hash(out / "runner_used.py"), "worker_sha256": file_hash(out / "worker_used.py"),
               "plan_sha256": file_hash(plan_target), "config_sha256": file_hash(config_target),
               "protocol_sha256": file_hash(protocol_target)})
    return frozen, submission / args.strategy.name, scorer_target, cache, input_manifest, config_target


def scenarios(args):
    full = {"forecast_count": args.days, "earning_day_limit": args.days - 1,
            "score_day_exclusive": args.days - 1}
    result = [{"name": "baseline", "kind": "baseline", **full},
              {"name": "repeat", "kind": "repeat", **full}]
    for cutoff in args.cuts:
        for mode in ("returns", "characteristics", "joint"):
            result.append({"name": f"{mode}_from_{cutoff}", "kind": "suffix", "cutoff": cutoff, "mode": mode,
                           "forecast_count": cutoff + 1, "earning_day_limit": cutoff, "score_day_exclusive": cutoff})
    for prefix_days in args.prefix_days:
        result.append({"name": f"prefix_{prefix_days}", "kind": "prefix", "length": prefix_days,
                       "forecast_count": prefix_days, "earning_day_limit": prefix_days - 1,
                       "score_day_exclusive": prefix_days - 1})
    result.append({"name": f"synthetic_append_{args.append_days}", "kind": "append", "append_days": args.append_days, **full})
    return result


def controller(args):
    global np
    args.project, args.strategy, args.config, args.out = (path.resolve() for path in
                                                       (args.project, args.strategy, args.config, args.out))
    require(args.strategy.is_file(), "Candidate strategy does not exist; do not run before implementation is ready")
    require(args.config.is_file(), "Candidate configuration does not exist")
    require(isinstance(json.loads(args.config.read_text()), dict), "Candidate configuration must be a JSON object")
    require(255 <= args.days <= 2016, "Requested actual-data prefix must remain in discovery")
    require(all(254 < p < args.days for p in args.prefix_days), "Invalid shorter prefix")
    require(len(args.prefix_days) == len(set(args.prefix_days)), "Duplicate prefix length")
    require(all(0 <= c < args.days for c in args.cuts), "Cutoff outside bounded prefix")
    require(len(args.cuts) == len(set(args.cuts)), "Duplicate cutoff")
    require(0 < args.append_days <= args.days, "Invalid synthetic append")
    args.out.mkdir(parents=True, exist_ok=False)
    out = args.out
    summary = {"status": "running", "started_utc": now(), "scope": "Bounded discovery-prefix causality E2E; no alpha ranking",
               "process_controls": constrain_threads(), "scenario_results": [], "numeric_input_rows": [0, args.days],
               "run_command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
               "unverified": ["untested discovery perturbations", "validation/audit data", "multi-decade causality and runtime",
                              "alpha generalization", "source-review gate until independently reviewed"]}
    write_json(out / "summary.json", summary)
    (out / "controller.stderr.log").write_text("")
    shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
    shutil.copyfile(Path(__file__).resolve(), out / "worker_used.py")
    exit_code = 1
    try:
        import numpy as np
        summary["environment"] = environment()
        write_json(out / "environment.json", {**summary["environment"], **summary["process_controls"]})
        frozen, strategy, scorer, inputs, input_manifest, candidate_config_path = freeze_project(args, out)
        summary["requested_config"] = json.loads(candidate_config_path.read_text())
        summary["requested_config_sha256"] = file_hash(candidate_config_path)
        run_specs = scenarios(args)
        write_json(out / "scenarios.json", run_specs)
        rerun = [sys.executable, str(out / "runner_used.py"), "--strategy", str(strategy),
                 "--config", str(candidate_config_path), "--project", str(frozen),
                 "--out", str(out.with_name(out.name + "_rerun")), "--days", str(args.days), "--cuts", *map(str, args.cuts),
                 "--prefix-days", *map(str, args.prefix_days), "--append-days", str(args.append_days), "--timeout-seconds", str(args.timeout_seconds)]
        summary["rerun_command"] = shlex.join(rerun)
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        (out / "rerun.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\nexec " + shlex.join(rerun) + "\n")
        (out / "workers").mkdir()
        (out / "manifests").mkdir()
        baseline = None
        baseline_status = None
        for scenario in run_specs:
            name = scenario["name"]
            manifest = out / "manifests" / (name + ".json")
            config = {"scenario": scenario, "strategy": str(strategy), "scorer": str(scorer),
                      "candidate_config": str(candidate_config_path),
                      "candidate_config_sha256": summary["requested_config_sha256"],
                      "inputs": str(inputs), "input_manifest": input_manifest, "output": str(out / "workers" / name)}
            write_json(manifest, config)
            command = [sys.executable, str(out / "worker_used.py"), "--worker", str(manifest)]
            config["worker_command"] = shlex.join(command)
            write_json(manifest, config)
            log_line(out, f"Causality E2E: starting {name} in a fresh interpreter")
            with (out / "workers" / (name + ".stdout.log")).open("w") as stdout, (out / "workers" / (name + ".stderr.log")).open("w") as stderr:
                try:
                    completed = subprocess.run(command, cwd=str(strategy.parent), stdout=stdout, stderr=stderr,
                                               timeout=args.timeout_seconds, check=False, env=dict(os.environ))
                    child_exit = completed.returncode
                except subprocess.TimeoutExpired:
                    child_exit = 124
                    child_status_path = out / "workers" / name / "status.json"
                    child_status = json.loads(child_status_path.read_text()) if child_status_path.exists() else {}
                    child_status.update({"status": "INCOMPLETE_TIMEOUT", "exit_code": 124, "finished_utc": now()})
                    child_status_path.parent.mkdir(exist_ok=True)
                    write_json(child_status_path, child_status)
            if name == "baseline":
                status_file = out / "workers" / name / "status.json"
                baseline_status = json.loads(status_file.read_text()) if status_file.exists() else {"status": "MISSING"}
                require(child_exit == 0 and baseline_status.get("status") == "EXECUTED_PASS", "Baseline execution failed; candidate causality is unverified")
                require(baseline_status.get("inputs_unchanged", False), "Baseline mutated caller inputs")
                with np.load(out / "workers" / name / "protected_outputs.npz", allow_pickle=False) as data:
                    baseline = {key: data[key].copy() for key in data.files}
                result = {"scenario": scenario, "status": "REFERENCE_COMPLETED", "worker_status": baseline_status["status"], "exit_code": child_exit}
            else:
                result = compare_case(out, baseline_status, baseline, scenario)
                result["exit_code"] = child_exit
                if child_exit != 0 and result["status"] == "PASS":
                    result["status"] = "UNVERIFIED"
                    result["reason"] = "Nonzero worker exit; a saved status alone cannot establish completion"
            summary["scenario_results"].append(result)
            write_json(out / "summary.json", summary)
            log_line(out, f"Causality E2E: {name}: {result['status']}")
        checks = summary["scenario_results"][1:]
        if any(result["status"] == "FAIL" for result in checks):
            summary["status"] = "EXECUTED_FAIL"
            summary["reason"] = "A protected comparison or input-integrity gate failed"
        elif any(result["status"] != "PASS" for result in checks):
            summary["status"] = "UNVERIFIED_INCOMPLETE_COMPARISONS"
            summary["reason"] = "At least one required worker/comparison did not complete; no leak is inferred solely from suffix failure"
        else:
            summary["status"] = "EXECUTED_PASS_SCOPE_ONLY"
            exit_code = 0
        sources = json.loads((out / "source_manifest.json").read_text())
        code_unchanged = all(file_hash(item["frozen"]) == item["sha256"] for item in sources["candidate"])
        inputs_unchanged = all(file_hash(item["frozen_path"]) == item["frozen_sha256"] for item in input_manifest)
        scorer_unchanged = file_hash(scorer) == SCORER_SHA256
        config_unchanged = file_hash(candidate_config_path) == sources["config_sha256"]
        protocol_unchanged = file_hash(frozen / "RESEARCH_PROTOCOL.json") == sources["protocol_sha256"]
        summary["frozen_artifacts_unchanged"] = {"candidate": code_unchanged, "inputs": inputs_unchanged,
                                                "scorer": scorer_unchanged, "config": config_unchanged,
                                                "protocol": protocol_unchanged}
        if not all(summary["frozen_artifacts_unchanged"].values()):
            summary["status"], exit_code = "EXECUTED_FAIL", 1
            summary["reason"] = "Frozen source or input artifacts changed"
    except KeyboardInterrupt:
        summary["status"], exit_code = "INCOMPLETE", 130
        summary["error"] = traceback.format_exc()
        (out / "controller.stderr.log").write_text(summary["error"])
        traceback.print_exc()
    except Exception:
        summary["status"] = "EXECUTED_FAIL"
        summary["error"] = traceback.format_exc()
        (out / "controller.stderr.log").write_text(summary["error"])
        traceback.print_exc()
    finally:
        summary["finished_utc"], summary["exit_code"] = now(), exit_code
        write_json(out / "summary.json", summary)
        (out / "README.md").write_text(
            "# Bounded candidate causality E2E\n\n"
            f"Status: **{summary['status']}**. Exit code: {exit_code}. Actual input prefix: [0,{args.days}).\n\n"
            "The frozen worker starts a new Python interpreter for every scenario and calls the unchanged official evaluator. "
            "The project/ directory contains the exact bounded input files, candidate/helpers, scorer and plan. "
            "No actual validation/audit data is included. Read expectations.md and scenarios.json for expected boundaries; "
            "summary.json records actual comparisons and limitations. Each worker has its manifest, command, input hashes, "
            "status, protected forecast/target/ledger arrays, daily ledger and stdout/stderr logs.\n\n"
            "Use rerun.txt or `bash rerun.sh` for an exact frozen rerun into a new directory. Select a fresh output path if it exists. "
            "A completed comparison does not establish untested dates, hidden-future performance or runtime. "
            "Empty protected ranges are marked not applicable; failed workers are not claimed passed. "
            "Source review for prohibited access and future-informed state remains a separate required gate.\n")
        log_line(out, f"Causality E2E finished: {summary['status']}; evidence {out}")
    return exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--strategy", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--days", type=int, default=600)
    parser.add_argument("--cuts", type=int, nargs="+", default=[0, 20, 21, 127, 252, 253, 254, 400])
    parser.add_argument("--prefix-days", type=int, nargs="+", default=[384])
    parser.add_argument("--append-days", type=int, default=64)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()
    if args.worker:
        return worker(args.worker.resolve())
    if any(value is None for value in (args.strategy, args.config, args.project, args.out)):
        parser.error("--strategy, --config, --project and --out are required for the controller")
    return controller(args)


if __name__ == "__main__":
    raise SystemExit(main())
