#!/usr/bin/env python3
"""Preimplementation C12 synthetic whole-strategy workflow; see its frozen plan.

Reuse the existing fresh-process causality worker and unchanged original scorer.
No actual market input is read and no candidate parameter is selected here.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import traceback


SEED, DAYS, STOCKS, FEATURES = 20261027, 600, 1000, 13
TIMEOUT_SECONDS = 300
EXPECTED_CONFIG = {
    "candidate_id": "C12_local_additive", "basis": "additive",
    "alpha_half_life": 252.0, "ridge": 0.1, "min_training_days": 126,
    "feature_clip": 4.0, "risk_window": 252, "risk_min_days": 20,
    "variance_shrinkage": 0.2, "variance_floor": 0.000001,
    "risk_aversion": 1000.0, "cost_horizon": 20.0,
    "weight_cap": 0.01, "gross_cap": 1.0, "local_ridge": 0.3,
}


def load_helper(path):
    spec = importlib.util.spec_from_file_location("local_additive_frozen_worker", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def generate_fixture(folder, helper):
    """Independent analytic truth; never imports a candidate module."""
    rng = np.random.default_rng(SEED)
    characteristics = rng.standard_normal((DAYS, STOCKS, FEATURES))
    market = np.clip(rng.standard_normal(DAYS), -4.0, 4.0) * 0.008
    noise = np.clip(rng.standard_normal((DAYS, STOCKS)), -4.0, 4.0) * 0.006
    noise -= noise.mean(axis=1, keepdims=True)
    beta = np.linspace(0.6, 1.4, STOCKS)
    costs = np.linspace(0.000005, 0.000015, STOCKS)
    truth = np.zeros((DAYS, STOCKS))
    constants = []
    for feature, knot, coefficient in ((0, -1.0, 0.0015), (2, 0.0, -0.0010), (4, 1.0, 0.00075)):
        q_tail = 0.5 * math.erfc(knot / math.sqrt(2.0))
        density = math.exp(-0.5 * knot * knot) / math.sqrt(2.0 * math.pi)
        first = density - knot * q_tail
        second = (1 + knot * knot) * q_tail - knot * density
        scale = math.sqrt(second - first * first - q_tail * q_tail - density * density / 2)
        constants.append((feature, knot, coefficient, q_tail, density, scale))
    for day in range(1, DAYS):
        panel = characteristics[day - 1]
        centered = panel - panel.mean(axis=0)
        scale = np.maximum(np.sqrt(np.mean(centered * centered, axis=0)), 1e-12)
        linear = np.clip(centered / scale, -4.0, 4.0)
        linear -= linear.mean(axis=0)
        square = linear * linear
        square = (square - square.mean(axis=0)) / math.sqrt(2.0)
        for feature, knot, coefficient, q_tail, density, reference_sd in constants:
            hinge = np.maximum(linear[:, feature] - knot, 0.0)
            hinge -= hinge.mean()
            local = (hinge - q_tail * linear[:, feature]
                     - density * square[:, feature] / math.sqrt(2.0)) / reference_sd
            truth[day] += coefficient * local
    returns = market[:, None] * beta + truth + noise
    values = {"returns": returns, "characteristics": characteristics, "costs": costs,
              "truth": truth, "true_beta": beta, "market_innovation": market}
    folder.mkdir()
    manifest = []
    for name, array in values.items():
        path = folder / (name + ".npy")
        np.save(path, array, allow_pickle=False)
        manifest.append({"name": path.name, "shape": list(array.shape), "dtype": str(array.dtype),
                         "sha256": helper.file_hash(path), "array_sha256": helper.array_hash(array),
                         "candidate_argument": name in ("returns", "characteristics", "costs")})
    helper.require(all(np.isfinite(value).all() for value in values.values()), "Nonfinite generated fixture")
    helper.require(bool((returns > -1).all() and (costs >= 0).all()), "Inadmissible generated fixture")
    return manifest


def generate_cash_fixture(folder, baseline_folder, helper):
    """Same characteristics/costs, exactly zero returns; no candidate import."""
    folder.mkdir()
    manifest = []
    for name in ("returns", "characteristics", "costs"):
        array = np.load(baseline_folder / (name + ".npy"), allow_pickle=False)
        if name == "returns":
            array = np.zeros_like(array)
        path = folder / (name + ".npy")
        np.save(path, array, allow_pickle=False)
        manifest.append({"name": path.name, "shape": list(array.shape), "dtype": str(array.dtype),
                         "sha256": helper.file_hash(path), "array_sha256": helper.array_hash(array),
                         "candidate_argument": True})
    return manifest


def pearson(left, right):
    a, b = np.ravel(left), np.ravel(right)
    a, b = a - a.mean(), b - b.mean()
    denominator = math.sqrt(float(a @ a) * float(b @ b))
    if denominator <= 0:
        raise ValueError("Undefined correlation")
    return float(a @ b / denominator)


def main():
    global np
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--strategy", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker-script", type=Path)
    parser.add_argument("--scorer", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--model-plan", type=Path)
    parser.add_argument("--protocol", type=Path)
    args = parser.parse_args()
    root, strategy_source, out = (p.resolve() for p in (args.project, args.strategy, args.out))
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__).resolve(), out / "runner_used.py")
    shutil.copy2(args.worker_script or root / "tools/verify_causality.py", out / "worker_used.py")
    helper = load_helper(out / "worker_used.py")
    controls = helper.constrain_threads()
    import numpy as np
    helper.np = np
    summary = {"status": "RUNNING", "started_utc": helper.now(), "checks": [], "workflows": [],
               "scope": "Synthetic full C12 strategy through original scorer; no actual market data",
               "seed": SEED, "input_shape": [DAYS, STOCKS, FEATURES], "process_controls": controls,
               "run_command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
               "validation": "NOT_OPENED", "audit": "NOT_OPENED", "century_runtime": "NOT_EXECUTED",
               "actual_data_causality": "NOT_TESTED_BY_THIS_WORKFLOW"}
    helper.write_json(out / "summary.json", summary)
    (out / "controller.stderr.log").write_text("")
    source_hashes, input_hashes = {}, {}
    exit_code = 1

    def check(name, passed, actual):
        entry = {"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual}
        summary["checks"].append(entry)
        helper.log_line(out, json.dumps(helper.ready(entry), allow_nan=False))
        helper.write_json(out / "summary.json", summary)
        helper.require(passed, name)

    def equal(name, actual, expected):
        entry = helper.comparison(name, actual, expected)
        summary["checks"].append(entry)
        helper.log_line(out, json.dumps(helper.ready(entry), allow_nan=False))
        helper.require(entry["status"] == "PASS", name)

    try:
        for target, source in {
            "expectations.md": args.plan or root / "verification/C12_LOCAL_ADDITIVE_WORKFLOW_PLAN.md",
            "model_expectations.md": args.model_plan or root / "research/LOCAL_ADDITIVE_PLAN.md",
            "protocol_used.json": args.protocol or root / "RESEARCH_PROTOCOL.json",
        }.items():
            shutil.copy2(source, out / target)
        environment = {**helper.environment(), **controls}
        helper.write_json(out / "environment.json", environment)
        config = json.loads(args.config.read_text()) if args.config else dict(EXPECTED_CONFIG)
        helper.write_json(out / "config.json", config)
        check("exact_admitted_configuration", config == EXPECTED_CONFIG, config)
        source_folder = out / "source"
        candidate_folder = source_folder / "candidate"
        candidate_folder.mkdir(parents=True)
        for source in sorted(strategy_source.parent.glob("*.py")):
            shutil.copy2(source, candidate_folder / source.name)
        frozen_strategy = candidate_folder / strategy_source.name
        scorer = source_folder / "score.py"
        shutil.copy2(args.scorer or root / "source/Quant Research Take-Home/score.py", scorer)
        check("original_scorer_identity", helper.file_hash(scorer) == helper.SCORER_SHA256,
              helper.file_hash(scorer))
        source_files = list(source_folder.rglob("*.py")) + [out / name for name in
            ("runner_used.py", "worker_used.py", "config.json", "expectations.md", "model_expectations.md", "protocol_used.json")]
        source_hashes = {str(p.relative_to(out)): helper.file_hash(p) for p in source_files}
        helper.write_json(out / "source_manifest.json", source_hashes)
        inputs = out / "inputs"
        input_manifest = generate_fixture(inputs, helper)
        cash_inputs = out / "inputs_zero"
        cash_manifest = generate_cash_fixture(cash_inputs, inputs, helper)
        input_hashes = {"inputs/" + item["name"]: item["sha256"] for item in input_manifest}
        input_hashes.update({"inputs_zero/" + item["name"]: item["sha256"] for item in cash_manifest})
        helper.write_json(out / "input_manifest.json", {"seed": SEED, "kind": "synthetic_only", "files": input_manifest})
        helper.write_json(out / "cash_input_manifest.json", {"kind": "exact_zero_returns", "files": cash_manifest})
        expected_candidate_sources = {str(p): helper.file_hash(p) for p in sorted(candidate_folder.glob("*.py"))}
        rerun = ["taskset", "-c", str(controls.get("cpu_affinity", [5])[0]), sys.executable,
                 str(out / "runner_used.py"), "--project", str(root), "--strategy", str(frozen_strategy),
                 "--config", str(out / "config.json"), "--out", str(out) + "_rerun",
                 "--worker-script", str(out / "worker_used.py"), "--scorer", str(scorer),
                 "--plan", str(out / "expectations.md"), "--model-plan", str(out / "model_expectations.md"),
                 "--protocol", str(out / "protocol_used.json")]
        summary["rerun_command"] = shlex.join(rerun)
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        (out / "rerun.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\nexec " + shlex.join(rerun) + "\n")
        (out / "setup.md").write_text(
            "# Synthetic whole-strategy workflow setup\n\nUse the Python, NumPy and Pandas versions in environment.json. "
            "No supplied market arrays are needed. The frozen controller regenerates the exact seed/recipe in expectations.md, "
            "then starts the frozen causality worker in a fresh interpreter for every case. "
            "Each worker imports the frozen complete candidate and unchanged original scorer. "
            "Truth is retained only for controller evaluation and is not a candidate argument. "
            "Run bash rerun.sh to retain the original CPU affinity and write a new evidence directory. "
            "The red-stage snapshot deliberately lacks the candidate, so its frozen rerun remains an expected missing-module run.\n")
        if not frozen_strategy.is_file():
            summary["status"] = "EXPECTED_RED_MISSING_MODULE"
            summary["reason"] = "The complete new C12 module is absent; zero candidate/scorer workflows executed"
            helper.log_line(out, summary["reason"])
            return 1

        full = {"forecast_count": DAYS, "earning_day_limit": DAYS - 1, "score_day_exclusive": DAYS - 1}
        scenarios = [
            {"name": "baseline", "kind": "baseline", **full},
            {"name": "repeat", "kind": "repeat", **full},
            {"name": "joint_from_400", "kind": "suffix", "cutoff": 400, "mode": "joint", **full},
            {"name": "prefix_384", "kind": "prefix", "length": 384,
             "forecast_count": 384, "earning_day_limit": 383, "score_day_exclusive": 383},
            {"name": "zero_returns", "kind": "baseline", **full},
        ]
        helper.write_json(out / "scenarios.json", scenarios)
        (out / "workers").mkdir()
        (out / "manifests").mkdir()
        baseline = None
        incomplete = False
        for scenario in scenarios:
            name = scenario["name"]
            child = out / "workers" / name
            manifest = out / "manifests" / (name + ".json")
            command = [sys.executable, str(out / "worker_used.py"), "--worker", str(manifest)]
            active_inputs = cash_inputs if name == "zero_returns" else inputs
            active_manifest = cash_manifest if name == "zero_returns" else input_manifest
            helper.write_json(manifest, {
                "scenario": scenario, "strategy": str(frozen_strategy), "scorer": str(scorer),
                "candidate_config": str(out / "config.json"), "candidate_config_sha256": helper.file_hash(out / "config.json"),
                "inputs": str(active_inputs), "input_manifest": [v for v in active_manifest if v["candidate_argument"]],
                "output": str(child), "worker_command": shlex.join(command),
            })
            helper.log_line(out, "Starting complete synthetic workflow in fresh interpreter: " + name)
            with (out / "workers" / (name + ".stdout.log")).open("w") as stdout, (out / "workers" / (name + ".stderr.log")).open("w") as stderr:
                try:
                    completed = subprocess.run(command, cwd=str(candidate_folder), env=dict(os.environ),
                                               stdout=stdout, stderr=stderr, timeout=TIMEOUT_SECONDS, check=False)
                    code = completed.returncode
                except subprocess.TimeoutExpired:
                    code = 124
            status = json.loads((child / "status.json").read_text()) if (child / "status.json").exists() else {}
            complete = code == 0 and status.get("status") == "EXECUTED_PASS"
            summary["workflows"].append({"name": name, "exit_code": code, "worker_status": status.get("status", "MISSING"),
                                         "status": "COMPLETED" if complete else "UNVERIFIED", "pid": status.get("environment", {}).get("pid")})
            helper.write_json(out / "summary.json", summary)
            if not complete:
                incomplete = True
                helper.log_line(out, name + ": incomplete; no prefix leakage is inferred solely from this failure")
                if name == "baseline":
                    summary["status"] = "UNVERIFIED_INCOMPLETE_WORKFLOW"
                    return 1
                continue
            with np.load(child / "protected_outputs.npz", allow_pickle=False) as saved:
                data = {key: saved[key].copy() for key in saved.files}
            length = scenario.get("length", DAYS)
            check(name + ":finite_complete_outputs",
                  status["forecast_full_shape"] == [length, STOCKS]
                  and data["forecast_prefix"].shape == (length, STOCKS)
                  and data["targets"].shape == (length - 253, STOCKS)
                  and data["scored_rows"].shape == (length - 254, 5)
                  and all(np.isfinite(data[k]).all() for k in ("forecast_prefix", "targets", "scored_rows")),
                  {key: list(value.shape) for key, value in data.items()})
            check(name + ":unchanged_inputs_and_config", status.get("inputs_unchanged", False)
                  and status["requested_config"] == EXPECTED_CONFIG and status["candidate_config"] == EXPECTED_CONFIG,
                  {"inputs_unchanged": status.get("inputs_unchanged"), "config_sha256": status["requested_config_sha256"]})
            check(name + ":frozen_source_config_and_scorer_identity",
                  status.get("source_hashes") == expected_candidate_sources
                  and status.get("scorer_sha256") == helper.SCORER_SHA256
                  and status.get("requested_config_sha256") == helper.file_hash(out / "config.json"),
                  {"source_files": len(status.get("source_hashes", {})),
                   "scorer_sha256": status.get("scorer_sha256"),
                   "config_sha256": status.get("requested_config_sha256")})
            if scenario["kind"] == "suffix":
                alteration = status.get("alteration", {})
                check(name + ":admissible_nonidentity_intervention",
                      alteration.get("cutoff") == 400 and alteration.get("mode") == "joint"
                      and alteration.get("prefix_returns_unchanged") is True
                      and alteration.get("prefix_characteristics_unchanged") is True
                      and alteration.get("returns_changed", 0) > 0
                      and alteration.get("characteristics_changed", 0) > 0,
                      alteration)
            check(name + ":exact_day_sequences",
                  np.array_equal(data["target_earning_days"], np.arange(253, length))
                  and np.array_equal(data["score_days"], np.arange(253, length - 1)),
                  {"targets": len(data["targets"]), "scored_days": len(data["scored_rows"])})
            maximum_weight = float(np.max(np.abs(data["targets"])))
            maximum_gross = float(np.max(np.abs(data["targets"]).sum(axis=1)))
            net = data["scored_rows"][:, 0] - data["scored_rows"][:, 1]
            check(name + ":controls_and_solvency", maximum_weight <= .01 + 1e-12 and maximum_gross <= 1 + 1e-12
                  and np.all(data["scored_rows"][:, 0] > -1) and np.all(net > -1),
                  {"maximum_stock_weight": maximum_weight, "maximum_gross": maximum_gross, "minimum_net": float(net.min())})
            if name == "baseline":
                baseline = data
                forecasts = data["forecast_prefix"]
                check("baseline:declared_startup", np.array_equal(forecasts[:127], np.zeros_like(forecasts[:127]))
                      and np.any(forecasts[127] != 0), {"first_active_row": int(np.flatnonzero(np.any(forecasts != 0, axis=1))[0]) if np.any(forecasts) else None})
                truth = np.load(inputs / "truth.npy", allow_pickle=False)
                correlation = pearson(forecasts[data["score_days"]], truth[data["score_days"]])
                check("baseline:known_signal_correlation", correlation >= .90, {"correlation": correlation, "minimum": .90})
                gross, fees, exposure, market, seconds = data["scored_rows"].T
                mean, volatility = float(net.mean()), float(net.std(ddof=0))
                sharpe = math.sqrt(252) * mean / volatility if volatility > 0 else None
                centered_market = market - market.mean()
                beta = float(centered_market @ (net - mean) / (centered_market @ centered_market))
                check("baseline:positive_net_outcome", mean > 0 and sharpe is not None and sharpe > 1.0,
                      {"daily_net_mean": mean, "net_sharpe": sharpe, "sharpe_minimum_exclusive": 1.0})
                check("baseline:realized_beta", abs(beta) < .2, {"net_market_beta": beta, "absolute_limit_exclusive": .2})
                returns = np.load(inputs / "returns.npy", allow_pickle=False)
                costs = np.load(inputs / "costs.npy", allow_pickle=False)
                previous, following = data["targets"][:-1], data["targets"][1:]
                observed = returns[data["score_days"]]
                expected_gross = np.einsum("ij,ij->i", previous, observed)
                drifted = previous * (1 + observed) / (1 + expected_gross[:, None])
                expected_fee = np.abs(following - drifted) @ costs
                equal("baseline:original_gross_accounting", gross, expected_gross)
                equal("baseline:full_drift_based_fees", fees, expected_fee)
                equal("baseline:posttrade_gross_accounting", exposure, np.abs(following).sum(axis=1))
                true_beta = np.load(inputs / "true_beta.npy", allow_pickle=False)
                summary["baseline_metrics"] = {
                    "forecast_truth_correlation": correlation, "net_sharpe": sharpe,
                    "gross_sharpe": float(math.sqrt(252) * gross.mean() / gross.std(ddof=0)),
                    "annual_arithmetic_net_mean": mean * 252, "annual_net_volatility": volatility * math.sqrt(252),
                    "annual_full_fees": float(fees.mean() * 252), "paid_full_fees_sum": float(fees.sum()),
                    "net_market_beta": beta, "maximum_gross": maximum_gross, "maximum_stock_weight": maximum_weight,
                    "opening_full_cost_waived": float(costs @ np.abs(data["targets"][0])),
                    "maximum_abs_true_beta_exposure": float(np.max(np.abs(data["targets"] @ true_beta))),
                    "forecast_instrumented_seconds": status["forecast_seconds_instrumented"],
                    "mean_official_rebalance_ms": float(seconds.mean() * 1000),
                    "maximum_official_rebalance_ms": float(seconds.max() * 1000),
                }
                scorer_module = helper.import_file(scorer, "local_additive_original_scorer_report")
                report = io.StringIO()
                with contextlib.redirect_stdout(report):
                    scorer_module.report("C12_synthetic_only", data["scored_rows"], status["forecast_seconds_instrumented"], DAYS)
                (out / "official_report.txt").write_text(report.getvalue())
            elif name == "zero_returns":
                check("zero_returns:exact_zero_forecasts_targets_economics",
                      np.count_nonzero(data["forecast_prefix"]) == 0
                      and np.count_nonzero(data["targets"]) == 0
                      and np.count_nonzero(data["scored_rows"][:, :4]) == 0
                      and np.count_nonzero(net) == 0,
                      {"forecast_nonzero": int(np.count_nonzero(data["forecast_prefix"])),
                       "target_nonzero": int(np.count_nonzero(data["targets"])),
                       "economic_nonzero": int(np.count_nonzero(data["scored_rows"][:, :4])),
                       "net_nonzero": int(np.count_nonzero(net))})
                returns = np.load(cash_inputs / "returns.npy", allow_pickle=False)
                costs = np.load(cash_inputs / "costs.npy", allow_pickle=False)
                previous, following = data["targets"][:-1], data["targets"][1:]
                observed = returns[data["score_days"]]
                expected_gross = np.einsum("ij,ij->i", previous, observed)
                drifted = previous * (1 + observed) / (1 + expected_gross[:, None])
                equal("zero_returns:original_gross_accounting", data["scored_rows"][:, 0], expected_gross)
                equal("zero_returns:full_drift_based_fees", data["scored_rows"][:, 1], np.abs(following - drifted) @ costs)
                equal("zero_returns:posttrade_gross_accounting", data["scored_rows"][:, 2], np.abs(following).sum(axis=1))
                market = data["scored_rows"][:, 3]
                net_variance, market_variance = float(net.var(ddof=0)), float(market.var(ddof=0))
                check("zero_returns:undefined_variance_metrics", net_variance == 0 and market_variance == 0,
                      {"net_variance": net_variance, "market_variance": market_variance,
                       "net_sharpe": None, "net_market_beta": None,
                       "sharpe_reason": "undefined: zero net-return variance",
                       "beta_reason": "undefined: zero market-return variance"})
                summary["cash_control_metrics"] = {
                    "net_sharpe": None, "net_market_beta": None,
                    "sharpe_reason": "undefined: zero net-return variance",
                    "beta_reason": "undefined: zero market-return variance",
                    "annual_arithmetic_net_mean": float(net.mean() * 252),
                    "annual_net_volatility": float(net.std(ddof=0) * math.sqrt(252)),
                    "paid_full_fees_sum": float(data["scored_rows"][:, 1].sum()),
                    "maximum_gross": maximum_gross, "maximum_stock_weight": maximum_weight,
                    "forecast_instrumented_seconds": status["forecast_seconds_instrumented"],
                    "mean_official_rebalance_ms": float(data["scored_rows"][:, 4].mean() * 1000),
                    "maximum_official_rebalance_ms": float(data["scored_rows"][:, 4].max() * 1000),
                    "official_report": "NOT_CALLED: variance-based metrics undefined; original scorer.run completed",
                }
            else:
                forecast_limit = 401 if scenario["kind"] == "suffix" else length
                target_limit = 400 if scenario["kind"] == "suffix" else length - 1
                score_limit = 400 if scenario["kind"] == "suffix" else length - 1
                actual_targets = data["target_earning_days"] <= target_limit
                base_targets = baseline["target_earning_days"] <= target_limit
                actual_scores = data["score_days"] < score_limit
                base_scores = baseline["score_days"] < score_limit
                check(name + ":protected_date_indices",
                      np.array_equal(data["target_earning_days"][actual_targets], baseline["target_earning_days"][base_targets])
                      and np.array_equal(data["score_days"][actual_scores], baseline["score_days"][base_scores]),
                      {"forecast_last_inclusive": forecast_limit - 1, "target_last_inclusive": target_limit,
                       "economic_stop_exclusive": score_limit})
                equal(name + ":protected_forecasts", data["forecast_prefix"][:forecast_limit], baseline["forecast_prefix"][:forecast_limit])
                equal(name + ":protected_targets", data["targets"][actual_targets], baseline["targets"][base_targets])
                equal(name + ":protected_gross_fee_exposure_market", data["scored_rows"][actual_scores, :4], baseline["scored_rows"][base_scores, :4])
                expected_net = baseline["scored_rows"][base_scores, 0] - baseline["scored_rows"][base_scores, 1]
                equal(name + ":protected_net", net[actual_scores], expected_net)
            helper.write_json(out / "summary.json", summary)
        summary["status"] = "UNVERIFIED_INCOMPLETE_WORKFLOW" if incomplete else "EXECUTED_PASS_SCOPE_ONLY"
        exit_code = 1 if incomplete else 0
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
        if source_hashes or input_hashes:
            integrity = {"frozen_sources": all(helper.file_hash(out / p) == digest for p, digest in source_hashes.items()),
                         "generated_inputs": all(helper.file_hash(out / p) == digest for p, digest in input_hashes.items())}
            summary["final_integrity"] = integrity
            if not all(integrity.values()):
                summary["status"], exit_code = "EXECUTED_FAIL", 1
        summary["finished_utc"], summary["exit_code"] = helper.now(), exit_code
        helper.write_json(out / "summary.json", summary)
        (out / "README.md").write_text(
            "# C12 synthetic full-strategy workflow\n\nStatus: " + summary["status"] + ". Exit code: " + str(exit_code) + ".\n\n"
            "Read expectations.md for the preimplementation generator, fixed checks and exact protected boundaries; "
            "summary.json for actual results; workers/ for complete original-scorer evidence and logs. "
            "The deliberately strong synthetic signal tests model capability and execution, not actual-market performance. "
            "No validation/audit array or discovery market outcome is read. No long-history or real-market causality pass is implied.\n")
        helper.log_line(out, "Synthetic workflow finished: " + summary["status"])
        artifacts = {str(p.relative_to(out)): {"sha256": helper.file_hash(p), "bytes": p.stat().st_size}
                     for p in sorted(out.rglob("*")) if p.is_file() and p.name != "artifact_manifest.json"}
        helper.write_json(out / "artifact_manifest.json", artifacts)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
