#!/usr/bin/env python3
"""Clean-folder original-scorer equivalence for one frozen selected policy."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib
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

PLAN_SHA = "f9b052fbd78b732397a1f9d0154e7fe342b7b2095ca4cda15ebf6922c68bc10f"
PROTOCOL_SHA = "cc2de53284feaeff97022c869ee8ee6e7b9fb40ab3f3dd1c0353e5b9923ed737"
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
ENGINES = {
    "C09_additive_long_memory": ("strategy", ("strategy.py", "portfolio.py")),
    "C06_gls_factor": ("strategy_gls_factor", ("strategy_gls_factor.py", "strategy_gls.py",
        "gls_precision.py", "strategy_factor.py", "factor_portfolio.py", "strategy.py", "portfolio.py")),
}
INPUTS = ("returns.npy", "characteristics.npy", "costs.npy")


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def package_files(folder):
    result = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink():
            raise ValueError("Handoff must not contain symbolic links")
        if path.is_file():
            result[str(path.relative_to(folder))] = sha(path)
    return result


def deployed_files(folder):
    files = package_files(folder)
    files.pop("score.py", None)
    return files


def original_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def worker(manifest_path):
    manifest = load(manifest_path)
    out, clean = Path(manifest["out"]), Path(manifest["clean"])
    os.sched_setaffinity(0, {manifest["cpu"]})
    sys.dont_write_bytecode = True
    import numpy as np
    checks, targets, held_books, target_days, seconds, fees, exposures = [], [], [], [], [], [], []
    forecasts = rows = entry = None
    forecast_calls = scorer_calls = 0
    forecast_seconds = 0.0
    result = {"status": "RUNNING", "started_utc": now(), "checks": checks, "stage": manifest["stage"],
              "configuration": manifest["config"], "scorer_calls": 0, "numeric_input_slice": None}

    save(out / "worker_summary.json", result)

    def check(name, condition, actual=None):
        checks.append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual})
        if not condition:
            raise AssertionError(name)

    try:
        check("isolated_process", bool(sys.flags.isolated) and os.getcwd() == str(clean))
        check("frozen_entry_and_helpers", deployed_files(clean) == manifest["package_files"])
        check("original_scorer", sha(clean / "score.py") == SCORER_SHA)
        inputs = Path(manifest["inputs"])
        check("authorized_input_identities", {name: sha(inputs / name) for name in INPUTS} == manifest["input_sha256"])
        arrays = tuple(np.load(inputs / name, mmap_mode="r", allow_pickle=False) for name in INPUTS)
        returns, chars, costs = arrays
        days = 2016 if manifest["stage"] == "discovery" else 3780
        result["numeric_input_slice"] = [0, days]
        check("canonical_input_contract", returns.shape == (days, 1000) and chars.shape == (days, 1000, 13)
              and costs.shape == (1000,) and returns.flags.f_contiguous and not returns.flags.c_contiguous
              and chars.flags.c_contiguous and all(a.dtype == np.float64 and not a.flags.writeable for a in arrays)
              and all(np.isfinite(a).all() for a in arrays) and np.all(costs >= 0))
        result["input_layouts"] = {name: {"shape": list(a.shape), "strides": list(a.strides),
            "dtype": str(a.dtype), "c_contiguous": bool(a.flags.c_contiguous),
            "f_contiguous": bool(a.flags.f_contiguous), "writeable": bool(a.flags.writeable)}
            for name, a in zip(INPUTS, arrays)}
        sys.path.insert(0, str(clean))
        entry = importlib.import_module("strategy")
        engine = entry._engine
        config = manifest["config"]
        engine_name, closure = ENGINES[config["candidate_id"]]
        check("fixed_configuration", entry._FROZEN_CONFIG == engine.CONFIG == config
              and getattr(entry, "CONFIG", config) == config)
        check("direct_function_aliases", entry.forecast is engine.forecast and entry.rebalance is engine.rebalance
              and engine.__name__ == "model." + engine_name)
        imported = {name: str(Path(module.__file__).resolve()) for name, module in sys.modules.items()
                    if name == "model" or name.startswith("model.")}
        expected_imports = {str((clean / "model" / name).resolve()) for name in (*closure, "__init__.py")}
        check("only_clean_local_engine_imports", set(imported.values()) == expected_imports
              and Path(entry.__file__).resolve() == (clean / "strategy.py").resolve(), imported)
        scorer = original_module(clean / "score.py", "handoff_original_scorer")
        save(out / "environment.json", {"python": sys.version, "platform": platform.platform(),
            "cpu_affinity": sorted(os.sched_getaffinity(0)), "thread_environment": {k: os.environ[k] for k in THREADS},
            "isolated": bool(sys.flags.isolated), "sys_path": sys.path, "project_module_paths": imported,
            "packages": {n: importlib.metadata.version(n) for n in ("numpy", "pandas", "scipy")}})
        candidate_forecast = scorer.with_declared_arguments(entry.forecast)
        candidate_rebalance = scorer.with_declared_arguments(entry.rebalance)

        def forecast(**named):
            nonlocal forecasts, forecast_calls, forecast_seconds
            forecast_calls += 1
            tick = time.perf_counter()
            forecasts = np.asarray(candidate_forecast(**named), dtype=np.float64)
            forecast_seconds = time.perf_counter() - tick
            check("forecast_shape_finite", forecasts.shape == (days, 1000) and np.isfinite(forecasts).all())
            forecasts.setflags(write=False)
            return forecasts

        def rebalance(**named):
            held = named["held_positions"].copy()
            tick = time.perf_counter()
            target = np.asarray(candidate_rebalance(**named), dtype=np.float64)
            seconds.append(time.perf_counter() - tick)
            day = len(named["returns_history"])
            if day != 253 + len(targets) or target.shape != (1000,) or not np.isfinite(target).all():
                raise ValueError("Invalid target or earning-day sequence")
            if not np.array_equal(held, named["held_positions"]):
                raise ValueError("Candidate mutated the scorer's held positions")
            if np.abs(target).max() > config["weight_cap"] + 1e-12 or np.abs(target).sum() > config["gross_cap"] + 1e-12:
                raise ValueError("Configured portfolio bound exceeded")
            targets.append(target.copy()); held_books.append(held); target_days.append(day)
            fees.append(float(costs @ np.abs(target - held))); exposures.append(float(np.abs(target).sum()))
            return target

        scorer_calls = 1
        result["scorer_calls"] = 1
        save(out / "worker_summary.json", result)
        rows, official_forecast_seconds = scorer.run(SimpleNamespace(forecast=forecast, rebalance=rebalance), *arrays, start=252)
        target_array, held_array = np.asarray(targets), np.asarray(held_books)
        score_days = np.arange(253, days - 1)
        check("complete_original_scorer_workflow", forecast_calls == 1 and rows.shape == (days - 254, 5)
              and target_array.shape == held_array.shape == (days - 253, 1000)
              and np.array_equal(target_days, np.arange(253, days)) and np.isfinite(rows).all())
        check("full_fees_and_closing_exposure", np.array_equal(rows[:, 1], fees[1:])
              and np.array_equal(rows[:, 2], exposures[1:]))
        check("empty_opening_book_and_solvency", np.array_equal(held_array[0], np.zeros(1000))
              and np.all(rows[:, 0] > -1) and np.all(rows[:, 0] - rows[:, 1] > -1))
        for i, day in enumerate(score_days):
            gross = float(target_array[i] @ returns[day])
            drift = target_array[i] * (1 + returns[day]) / (1 + gross)
            if gross != rows[i, 0] or not np.array_equal(drift, held_array[i + 1]):
                raise AssertionError("Independent full-path gross/drift reconciliation differs")
        check("full_path_gross_and_drift", True, len(score_days))
        reference = load(out / "reference/summary.json")
        for name, value in (("forecasts.npy", forecasts), ("targets.npy", target_array), ("held_books.npy", held_array)):
            np.save(out / name, value, allow_pickle=False)
            check("exact_reference_array:" + name, sha(out / name) == reference["output_arrays"][name]["sha256"], sha(out / name))
        with (out / "reference/daily.csv").open(newline="") as stream:
            old_rows = list(csv.DictReader(stream))
        columns = ("gross_return", "full_cost", "closing_target_gross", "raw_market_return")
        expected = np.array([[float(record[k]) for k in columns] for record in old_rows])
        check("exact_full_economic_mask", [int(record["return_index"]) for record in old_rows] == score_days.tolist())
        check("exact_full_reference_economics", np.array_equal(rows[:, :4], expected),
              {"max_abs_error": float(np.max(np.abs(rows[:, :4] - expected)))})
        check("exact_reference_net_returns", np.array_equal(rows[:, 0] - rows[:, 1],
              [float(record["net_return"]) for record in old_rows]))
        start, stop = (253, 2015) if manifest["stage"] == "discovery" else (3024, 3779)
        mask = (score_days >= start) & (score_days < stop)
        check("exact_reported_score_mask", np.array_equal(score_days[mask], np.arange(start, stop)))
        gross, paid_cost, _, market, _ = rows[mask].T
        net = gross - paid_cost; std = float(net.std()); centered = market - market.mean(); market_ss = float(centered @ centered)
        metrics = {"scored_days": int(mask.sum()), "net_sharpe": math.sqrt(252) * float(net.mean()) / std if std else None,
            "realized_net_market_beta": float(centered @ (net - net.mean()) / market_ss) if market_ss else None,
            "annual_arithmetic_net_return": float(net.mean() * 252), "annual_net_volatility": std * math.sqrt(252),
            "annual_full_cost": float(paid_cost.mean() * 252)}
        expected_metrics = reference["metrics"] if manifest["stage"] == "discovery" else reference["metrics"]["locked_audit"]
        check("reference_metrics_reconciled", all(metrics[k] == expected_metrics[k] for k in metrics))
        metrics["undefined_metrics"] = {k: "Zero variance" for k, value in metrics.items() if value is None}
        result.update(metrics=metrics, forecast_candidate_seconds=forecast_seconds,
            forecast_official_instrumented_seconds=float(official_forecast_seconds), opening_full_cost_waived=fees[0],
            score_mask=[start, stop], complete_economic_rows=len(rows),
            mean_candidate_rebalance_ms=float(np.mean(seconds) * 1000), maximum_candidate_rebalance_ms=float(np.max(seconds) * 1000))
        check("measured_rebalance_mean_limit", np.mean(seconds) < .1 and np.mean(seconds[1:]) < .1)
        result["status"] = "EXECUTED_PASS_SCOPE_ONLY"
    except BaseException:
        result.update(status="EXECUTED_FAIL", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        try:
            check("package_unchanged", deployed_files(clean) == manifest["package_files"])
            check("original_scorer_unchanged", sha(clean / "score.py") == SCORER_SHA)
            check("input_files_unchanged", {name: sha(Path(manifest["inputs"]) / name) for name in INPUTS} == manifest["input_sha256"])
            if entry is not None:
                check("configured_state_unchanged", entry._FROZEN_CONFIG == entry._engine.CONFIG == manifest["config"])
            if forecasts is not None: np.save(out / "forecasts.npy", forecasts, allow_pickle=False)
            if targets:
                np.save(out / "targets.npy", np.asarray(targets), allow_pickle=False)
                np.save(out / "held_books.npy", np.asarray(held_books), allow_pickle=False)
                np.save(out / "candidate_rebalance_seconds.npy", np.asarray(seconds), allow_pickle=False)
            if rows is not None:
                with (out / "daily.csv").open("w", newline="") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(("return_index", "gross_return", "full_cost", "net_return", "closing_target_gross", "raw_market_return", "official_rebalance_seconds"))
                    for i, (g, fee, exposure, market, elapsed) in enumerate(rows):
                        writer.writerow((253 + i, g, fee, g - fee, exposure, market, elapsed))
        except BaseException:
            result.update(status="EXECUTED_FAIL", evidence_error=traceback.format_exc())
        result.update(finished_utc=now(), scorer_calls=scorer_calls, forecast_calls=forecast_calls,
                      completed_rebalances=len(targets), exit_code=0 if result["status"] == "EXECUTED_PASS_SCOPE_ONLY" else 1)
        save(out / "worker_summary.json", result)
    return result["exit_code"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    for name in ("project", "handoff", "reference", "inputs", "selection-record", "config", "frozen-package-manifest", "out", "plan", "scorer", "protocol", "red-input-manifest"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--selection-sha256")
    parser.add_argument("--package-manifest-sha256")
    parser.add_argument("--stage", choices=("discovery", "audit"), default="discovery")
    parser.add_argument("--cpu", type=int, default=7)
    parser.add_argument("--timeout-seconds", type=float, default=1800)
    parser.add_argument("--expect-missing-wrapper", action="store_true")
    args = parser.parse_args()
    if args.worker: return worker(args.worker.resolve())
    if not args.project or not args.handoff or not args.out:
        parser.error("--project, --handoff and --out are required")
    root, handoff, out = args.project.resolve(), args.handoff.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    result = {"status": "RUNNING", "started_utc": now(), "stage": args.stage, "scorer_workflows": 0,
              "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]), "checks": []}
    save(out / "summary.json", result)

    def require(name, condition, actual=None):
        result["checks"].append({"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual})
        if not condition: raise AssertionError(name)

    frozen_controls = {}
    try:
        shutil.copyfile(Path(__file__), out / "runner_used.py")
        for source, name, expected in ((args.plan or root / "verification/HANDOFF_ENGINEERING_PLAN.md", "expectations.md", PLAN_SHA),
            (args.scorer or root / "source/Quant Research Take-Home/score.py", "score_used.py", SCORER_SHA),
            (args.protocol or root / "RESEARCH_PROTOCOL.json", "protocol_used.json", PROTOCOL_SHA)):
            require("identity:" + name, sha(source) == expected, sha(source)); shutil.copyfile(source, out / name)
        (out / "stdout.log").write_text(""); (out / "stderr.log").write_text("")
        if args.expect_missing_wrapper:
            require("red_discovery_only", args.stage == "discovery")
            require("wrapper_actually_absent", not (handoff / "strategy.py").exists())
            input_record = args.red_input_manifest or root / "cache/discovery/metadata.json"
            metadata = load(input_record)
            require("red_expected_input_scope", metadata["input_slice"] == [0, 2016] and set(metadata["cache_sha256"]) == set(INPUTS))
            shutil.copyfile(input_record, out / "prospective_input_manifest.json")
            result.update(status="EXPECTED_RED_MISSING_WRAPPER", numeric_inputs_accessed=False,
                prospective_input_sha256=metadata["cache_sha256"],
                reason="Selected deployment entry point is absent; zero strategy/scorer workflows executed")
        else:
            require("green_arguments", all((args.reference, args.inputs, args.selection_record, args.config, args.selection_sha256)))
            reference, inputs = args.reference.resolve(), args.inputs.resolve()
            require("selection_identity", sha(args.selection_record) == args.selection_sha256, sha(args.selection_record))
            selected, config = load(args.selection_record), load(args.config)
            candidate = selected["selected_candidate_id"]
            require("selected_fixed_configuration", candidate in ENGINES and config["candidate_id"] == candidate
                    and sha(args.config) == selected["config_sha256"])
            ref, original_sources, input_manifest = load(reference / "summary.json"), load(reference / "source_manifest.json"), load(reference / "input_manifest.json")
            require("complete_selected_reference", ref["status"] == "EXECUTED_PASS_SCOPE_ONLY" and ref["exit_code"] == 0 and ref["configuration"] == config)
            days = 2016 if args.stage == "discovery" else 3780
            require("exact_reference_input_scope", input_manifest["input_slice"] == [0, days])
            hashes = input_manifest.get("cache_sha256") or {n: item["sha256"] for n, item in input_manifest["files"].items()}
            require("exact_three_input_files", set(hashes) == set(INPUTS))
            engine_name, closure = ENGINES[candidate]
            files = package_files(handoff)
            require("exact_small_package_member_set", set(files) == {"strategy.py", "model/__init__.py", *("model/" + name for name in closure)}, sorted(files))
            require("empty_package_initializer", (handoff / "model/__init__.py").stat().st_size == 0)
            require("unchanged_engine_bytes", all(files["model/" + name] == original_sources["source/candidate/" + name] for name in closure))
            if args.stage == "audit":
                require("audit_manifest_arguments", bool(args.frozen_package_manifest and args.package_manifest_sha256))
                require("frozen_package_manifest_identity", sha(args.frozen_package_manifest) == args.package_manifest_sha256)
                frozen = load(args.frozen_package_manifest)
                require("unchanged_discovery_verified_package", frozen["status"] == "DISCOVERY_VERIFIED_PACKAGE" and frozen["files"] == files
                        and frozen["selection_sha256"] == args.selection_sha256 and frozen["config_sha256"] == selected["config_sha256"])
                require("completed_canonical_selected_audit", ref.get("mode") == "audit" and ref.get("audit_opened") is True
                        and sha(reference / "selection_used.json") == args.selection_sha256 and inputs == reference / "inputs")
                nomination = load(reference / "nomination_used.json")
                require("audit_nomination_bound_package", nomination.get("handoff_package_manifest_sha256") == args.package_manifest_sha256)
                shutil.copyfile(args.frozen_package_manifest, out / "frozen_package_manifest_used.json")
            (out / "reference").mkdir()
            for name in ("summary.json", "source_manifest.json", "input_manifest.json", "daily.csv"):
                shutil.copyfile(reference / name, out / "reference" / name)
            shutil.copyfile(args.selection_record, out / "selection_used.json"); shutil.copyfile(args.config, out / "config.json")
            clean = out / "clean"
            shutil.copytree(handoff, out / "package_used")
            shutil.copytree(out / "package_used", clean)
            shutil.copyfile(out / "score_used.py", clean / "score.py")
            manifest = {"out": str(out), "clean": str(clean), "stage": args.stage, "cpu": args.cpu,
                "inputs": str(inputs), "input_sha256": hashes, "package_files": files, "config": config}
            save(out / "worker_manifest.json", manifest)
            frozen_controls = {str(p.relative_to(out)): sha(p) for p in out.rglob("*") if p.is_file()}
            environment = dict(os.environ); environment.pop("PYTHONPATH", None)
            environment.update({name: "1" for name in THREADS})
            command = [sys.executable, "-I", str(out / "runner_used.py"), "--worker", str(out / "worker_manifest.json")]
            (out / "worker_command.txt").write_text(shlex.join(command) + "\n")
            with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
                completed = subprocess.run(command, cwd=clean, env=environment, stdout=stdout, stderr=stderr, timeout=args.timeout_seconds, check=False)
            observed = load(out / "worker_summary.json")
            result.update(worker=observed, scorer_workflows=observed["scorer_calls"], configuration=config)
            require("clean_worker_completed", completed.returncode == 0 and observed["status"] == "EXECUTED_PASS_SCOPE_ONLY")
            require("original_package_unchanged", package_files(handoff) == files)
            require("frozen_controls_unchanged", all(sha(out / name) == value for name, value in frozen_controls.items()
                    if name not in ("stdout.log", "stderr.log")))
            result["status"] = "EXECUTED_PASS_SCOPE_ONLY"
            if args.stage == "discovery":
                save(out / "package_manifest.json", {"schema_version": 1, "status": "DISCOVERY_VERIFIED_PACKAGE", "frozen_utc": now(),
                    "candidate_id": candidate, "engine_module": engine_name, "config_sha256": selected["config_sha256"],
                    "selection_sha256": args.selection_sha256, "files": files, "discovery_reference": str(reference),
                    "discovery_evidence": str(out), "verifier_sha256": sha(out / "runner_used.py")})
    except BaseException as exc:
        state = "INCOMPLETE_TIMEOUT" if isinstance(exc, subprocess.TimeoutExpired) else "INCOMPLETE" if isinstance(exc, KeyboardInterrupt) else "EXECUTED_FAIL"
        result.update(status=state, error=traceback.format_exc())
        if (out / "worker_summary.json").exists():
            result["worker"] = load(out / "worker_summary.json")
            result["scorer_workflows"] = result["worker"].get("scorer_calls", 0)
        traceback.print_exc()
    finally:
        (out / "controller.stderr.log").write_text(result.get("error", ""))
        (out / "controller.stdout.log").write_text(json.dumps({"status": result["status"], "scorer_workflows": result["scorer_workflows"]}) + "\n")
        rerun = [sys.executable, str(out / "runner_used.py"), "--project", str(root), "--handoff",
                 str(out / "intentionally_absent_handoff" if args.expect_missing_wrapper else out / "package_used"),
                 "--out", str(out) + "_rerun", "--stage", args.stage, "--cpu", str(args.cpu),
                 "--timeout-seconds", str(args.timeout_seconds), "--plan", str(out / "expectations.md"),
                 "--scorer", str(out / "score_used.py"), "--protocol", str(out / "protocol_used.json")]
        if args.expect_missing_wrapper:
            rerun += ["--expect-missing-wrapper", "--red-input-manifest", str(out / "prospective_input_manifest.json")]
        elif args.reference and args.inputs and args.selection_sha256:
            rerun += ["--reference", str(args.reference.resolve()), "--inputs", str(args.inputs.resolve()),
                      "--selection-record", str(out / "selection_used.json"), "--selection-sha256", args.selection_sha256,
                      "--config", str(out / "config.json")]
            if args.stage == "audit" and args.package_manifest_sha256:
                rerun += ["--frozen-package-manifest", str(out / "frozen_package_manifest_used.json"),
                          "--package-manifest-sha256", args.package_manifest_sha256]
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        (out / "setup.md").write_text("# Clean-folder handoff workflow\n\nRead expectations.md. Use the preserved reference/input identities and Python environment. "
            "The frozen rerun creates a new output directory and imports only the copied handoff plus allowed installed dependencies. "
            "A red rerun points to an intentionally absent entry point, even after the actual handoff is later implemented. "
            "Audit execution requires the completed selected canonical audit and its bound discovery-verified package manifest.\n")
        result.update(finished_utc=now(), exit_code=0 if result["status"] == "EXECUTED_PASS_SCOPE_ONLY" else 1,
            limitations=["Same-policy packaging equivalence only; no model selection or overfit certification.",
                         "A completed audit replay requires the already completed selected canonical audit and unchanged frozen package."])
        save(out / "summary.json", result)
        inventory = {str(p.relative_to(out)): {"sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(out.rglob("*"))
                     if p.is_file() and p.name != "artifact_manifest.json"}
        save(out / "artifact_manifest.json", inventory)
    print(json.dumps({"status": result["status"], "scorer_workflows": result["scorer_workflows"], "exit_code": result["exit_code"]}))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
