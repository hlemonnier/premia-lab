#!/usr/bin/env python3
"""Read-only evidence reconciliation; no candidate execution or gate rewriting."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import shlex
import sys
import numpy as np

ATOL, RTOL = 1e-14, 1e-12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def ledger(path, historic=False):
    with Path(path).open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    keys = ("gross_return", "full_cost", "net_return", "closing_target_gross", "raw_market_return") if historic else (
        "gross_return", "cost", "net_return", "target_gross", "market_return")
    day_key = "return_index" if historic else "array_index"
    return np.array([int(row[day_key]) for row in rows]), np.array([[float(row[k]) for k in keys] for row in rows])


def metrics(values):
    gross, fees, net, exposure, market = values.T
    centered = market - market.mean()
    return {
        "net_sharpe": float(math.sqrt(252) * net.mean() / net.std(ddof=0)),
        "gross_sharpe": float(math.sqrt(252) * gross.mean() / gross.std(ddof=0)),
        "annual_net_mean": float(252 * net.mean()),
        "annual_net_volatility": float(math.sqrt(252) * net.std(ddof=0)),
        "annual_full_cost": float(252 * fees.mean()),
        "net_market_beta": float(centered @ (net - net.mean()) / (centered @ centered)),
        "mean_gross_exposure": float(exposure.mean()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    historical = root / "evidence/discovery_C06_001"
    old_days, old = ledger(historical / "daily.csv", True)
    assert np.array_equal(old_days, np.arange(253, 2015))
    old_summary = load(historical / "summary.json")
    old_env = load(historical / "environment.json")
    old_sources = load(historical / "source_manifest.json")
    old_inputs = load(historical / "input_manifest.json")
    report = {
        "status": "HISTORICAL_EXACT_REPRODUCTION_FAIL_ECONOMIC_TOLERANCE_PASS",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
        "analysis_sha256": sha(__file__),
        "scope": "Already saved discovery ledgers/outputs only; no fitting, new interval, parameter choice, or modification of earlier evidence",
        "numeric_comparison_rule": {"atol": ATOL, "rtol": RTOL, "reference": "historical daily ledger", "changed": False},
        "score_mask": [253, 2015], "scored_rows": len(old_days),
        "historical_metrics_recomputed": metrics(old), "groups": [], "input_file_hashes": {},
        "historical_forecast_and_target_numeric_comparison": "UNAVAILABLE: original binary arrays were not persisted; their hashes do not bound numerical distance",
        "causality_or_overfit_claim": "No general no-lookahead/no-overfit certification; original failed exact gates remain failed",
    }
    for path in (historical / "daily.csv", historical / "summary.json", historical / "environment.json", historical / "source_manifest.json", historical / "input_manifest.json"):
        report["input_file_hashes"][str(path.relative_to(root))] = sha(path)
    baseline_forecasts = []
    baseline_targets = []
    baseline_values = []
    for name in ("A", "B", "C"):
        folder = root / f"evidence/C06_causality_{name}_001"
        worker = folder / "workers/baseline"
        status = load(worker / "status.json")
        day, values = ledger(worker / "daily.csv")
        assert np.array_equal(day, old_days) and np.isfinite(values).all()
        current_inputs = load(folder / "input_manifest.json")
        env = load(folder / "environment.json")
        current_sources = {Path(k).name: v for k, v in status["source_hashes"].items()}
        source_match = {k: current_sources[Path(k).name] == v for k, v in old_sources.items() if k.startswith("source/candidate/")}
        cache_match = {item["name"]: item["source_sha256"] == old_inputs["cache_sha256"][item["name"]]
                       and item["frozen_sha256"] == old_inputs["cache_sha256"][item["name"]]
                       and sha(item["frozen_path"]) == old_inputs["cache_sha256"][item["name"]]
                       for item in current_inputs["files"]}
        assert all(source_match.values()) and all(cache_match.values())
        assert status["requested_config"] == old_summary["configuration"] == status["candidate_config"]
        column_results = []
        for j, channel in enumerate(("gross_return", "full_cost", "net_return", "closing_target_gross", "raw_market_return")):
            error = np.abs(values[:, j] - old[:, j])
            allowed = ATOL + RTOL * np.abs(old[:, j])
            worst = int(np.argmax(error))
            column_results.append({
                "channel": channel, "exact": bool(np.array_equal(values[:, j], old[:, j])),
                "exact_differences": int(np.count_nonzero(error)),
                "within_frozen_tolerance": bool(np.all(error <= allowed)),
                "tolerance_exceedances": int(np.count_nonzero(error > allowed)),
                "max_abs_error": float(error[worst]), "worst_error_return_index": int(day[worst]),
                "historical_at_worst": float(old[worst, j]), "current_at_worst": float(values[worst, j]),
                "max_fraction_of_allowed_error": float(np.max(error / allowed)),
            })
        assert all(x["within_frozen_tolerance"] for x in column_results)
        current_metrics = metrics(values)
        with np.load(worker / "protected_outputs.npz", allow_pickle=False) as archive:
            forecasts = archive["forecast_prefix"].copy()
            targets = archive["targets"].copy()
        forecast_bytes, target_bytes = io.BytesIO(), io.BytesIO()
        np.save(forecast_bytes, forecasts, allow_pickle=False)
        np.save(target_bytes, targets, allow_pickle=False)
        forecast_hash = hashlib.sha256(forecast_bytes.getvalue()).hexdigest()
        target_hash = hashlib.sha256(target_bytes.getvalue()).hexdigest()
        row = {
            "group": name, "worker_status": status["status"], "economic_comparisons": column_results,
            "metrics_recomputed": current_metrics,
            "metric_differences_current_minus_historical": {k: current_metrics[k] - report["historical_metrics_recomputed"][k] for k in current_metrics},
            "historical_imported_dependency_hashes_match": source_match,
            "frozen_cache_hashes_match_historical": cache_match,
            "requested_and_consumed_config_matches_historical": True,
            "scorer_matches_historical": status["scorer_sha256"] == old_sources["source/score.py"],
            "environment_metadata_comparison": {
                "python_version_equal": env["python"] == old_env["python"],
                "platform_label_equal": env["platform"] == old_env["platform"],
                "package_versions_equal": env["packages"] == old_env["packages"],
                "thread_environment_equal": env["thread_environment"] == old_env["thread_environment"],
                "historical_affinity": old_env["cpu_affinity"], "current_affinity": env["cpu_affinity"],
                "historical_executable": old_env["executable"], "current_executable": env["executable"],
                "historical_hardware_backend_binary_fingerprint": "NOT_RECORDED",
            },
            "current_forecast_npy_sha256": forecast_hash,
            "historical_forecast_npy_sha256": old_summary["output_arrays"]["forecasts.npy"]["sha256"],
            "current_target_npy_sha256": target_hash,
            "historical_target_npy_sha256": old_summary["output_arrays"]["targets.npy"]["sha256"],
            "historical_forecast_exact_match": forecast_hash == old_summary["output_arrays"]["forecasts.npy"]["sha256"],
            "historical_target_exact_match": target_hash == old_summary["output_arrays"]["targets.npy"]["sha256"],
        }
        report["groups"].append(row)
        baseline_forecasts.append(forecasts)
        baseline_targets.append(targets)
        baseline_values.append(values)
        for path in (worker / "daily.csv", worker / "status.json", worker / "protected_outputs.npz", folder / "environment.json", folder / "input_manifest.json"):
            report["input_file_hashes"][str(path.relative_to(root))] = sha(path)
    report["current_baselines_exactly_equal"] = {
        "forecasts": all(np.array_equal(a, baseline_forecasts[0]) for a in baseline_forecasts[1:]),
        "targets": all(np.array_equal(a, baseline_targets[0]) for a in baseline_targets[1:]),
        "economic_ledgers": all(np.array_equal(a, baseline_values[0]) for a in baseline_values[1:]),
    }
    long = root / "evidence/C06_long_history_001/forecasts.npy"
    long_prefix = np.load(long, allow_pickle=False)
    report["current_long_prefix_comparison"] = {
        "path": str(long.relative_to(root)), "sha256": sha(long),
        "shape": list(long_prefix.shape),
        "exact_equal_to_current_discovery_baseline": bool(np.array_equal(long_prefix, baseline_forecasts[0])),
        "max_abs_error": float(np.max(np.abs(long_prefix - baseline_forecasts[0]))) if long_prefix.shape == baseline_forecasts[0].shape else None,
    }
    report["input_file_hashes"][str(long.relative_to(root))] = sha(long)
    report["interpretation"] = [
        "Saved historical economic channels differ in low-order floating-point digits, all within the original unchanged numerical tolerances.",
        "The historical forecast and target checksums fail exact reproduction; original binary arrays are unavailable for numerical distance measurements.",
        "Current discovery baselines and the long-input forecast prefix agree exactly on this path; the observed historical mismatch is not unique to the longer input.",
        "Recorded versions and platform labels agree, but do not establish identical hardware/backend binaries or all floating-point execution conditions.",
        "The causal source is unchanged and economic differences are small; a numerical execution/portability difference is a plausible explanation, not an identified root cause.",
        "Preserve failed historical exact gates. A newly frozen current-environment reference can support a separate prospective reproduction gate without rewriting the original result.",
    ]
    (out / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (out / "rerun.txt").write_text(shlex.join([sys.executable, str(Path(__file__).resolve()), "--project", str(root), "--out", str(out) + "_rerun"]) + "\n")
    print(json.dumps({"status": report["status"], "current_baselines_exactly_equal": report["current_baselines_exactly_equal"], "current_long_prefix_comparison": report["current_long_prefix_comparison"], "group_A_economic_comparisons": report["groups"][0]["economic_comparisons"], "group_A_metrics": report["groups"][0]["metrics_recomputed"], "group_A_metric_differences": report["groups"][0]["metric_differences_current_minus_historical"]}, indent=2))


if __name__ == "__main__":
    main()
