#!/usr/bin/env python3
"""Read saved C09 E2E evidence; never fit a candidate or read a holdout."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ADMISSION = Path(__file__).resolve().parent
RUN = ROOT / "evidence/C09_causality_001"
ATOL, RTOL = 1e-14, 1e-12


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def serialization_hash(array):
    buffer = io.BytesIO()
    np.save(buffer, array, allow_pickle=False)
    return hashlib.sha256(buffer.getbuffer()).hexdigest()


def main():
    output = ADMISSION / "saved_evidence_review.json"
    if output.exists():
        raise FileExistsError("Do not overwrite an earlier evidence review")
    records, numeric = [], []

    def check(name, passed, actual=None):
        records.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual})

    def compare(name, actual, expected):
        shape_ok = actual.shape == expected.shape
        item = {"name": name, "actual_shape": list(actual.shape), "expected_shape": list(expected.shape),
                "atol": ATOL, "rtol": RTOL}
        if not shape_ok:
            item.update(status="FAIL", reason="shape_mismatch")
        elif not actual.size:
            item.update(status="NOT_APPLICABLE", reason="declared_empty_range")
        else:
            difference = np.abs(actual - expected)
            finite = bool(np.isfinite(actual).all() and np.isfinite(expected).all())
            bad = ~np.isfinite(difference) | (difference > ATOL + RTOL * np.abs(expected))
            item.update(status="PASS" if finite and not bad.any() else "FAIL",
                        max_abs_error=float(difference.max()), mismatched_elements=int(bad.sum()),
                        exact=bool(np.array_equal(actual, expected)))
        numeric.append(item)

    result = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Saved C09 complete E2E records only; no strategy invocation or protected market input",
              "checks": records, "numeric_comparisons": numeric,
              "script_sha256": digest(Path(__file__))}
    try:
        admission = read(ADMISSION / "admission.json")
        summary = read(RUN / "summary.json")
        sources = read(RUN / "source_manifest.json")
        inputs = read(RUN / "input_manifest.json")
        historical = read(ADMISSION / "historical/summary.json")
        config = read(ADMISSION / "config.json")
        check("controller_completed", summary["status"] == "EXECUTED_PASS_SCOPE_ONLY" and summary["exit_code"] == 0,
              {"status": summary["status"], "exit_code": summary["exit_code"]})
        check("original_admission_artifacts", all(digest(ADMISSION / p) == m["sha256"]
              and (ADMISSION / p).stat().st_size == m["bytes"] for p, m in admission["artifacts"].items()))
        check("live_profile_matches_frozen", digest(ROOT / "verification/C09_FULL_DISCOVERY_CAUSALITY_PLAN.md")
              == admission["plan_sha256"])
        check("runner_worker_identities", sources["runner_sha256"] == sources["worker_sha256"]
              == admission["verifier_sha256"] == digest(RUN / "runner_used.py") == digest(RUN / "worker_used.py"))
        expected_sources = {i["frozen"]: i["sha256"] for i in sources["candidate"]}
        check("all_frozen_candidate_files", all(digest(Path(p)) == sha for p, sha in expected_sources.items()))
        check("candidate_copy_set", {Path(p).name: h for p, h in expected_sources.items()}
              == {Path(p).name: h for p, h in admission["current_all_candidate_files"].items()})
        frozen = RUN / "project"
        check("config_identity", digest(frozen / "candidate_config.json") == sources["config_sha256"]
              == admission["checked_historical_closure"]["research/configs/C09_additive_long_memory.json"])
        check("protocol_identity", digest(frozen / "RESEARCH_PROTOCOL.json") == sources["protocol_sha256"]
              == admission["checked_historical_closure"]["RESEARCH_PROTOCOL.json"])
        check("scorer_identity", digest(frozen / "source/Quant Research Take-Home/score.py") == sources["scorer_sha256"]
              == admission["checked_historical_closure"]["source/Quant Research Take-Home/score.py"])
        check("base_causality_plan_identity", digest(RUN / "expectations.md") == sources["plan_sha256"]
              == digest(ADMISSION / "base_expectations.md"))
        check("all_frozen_input_files", all(digest(Path(i["frozen_path"])) == i["frozen_sha256"]
              == admission["source_inputs_sha256"][i["name"]] for i in inputs["files"]))
        check("controller_final_integrity", all(summary["frozen_artifacts_unchanged"].values()))

        full = {"forecast_count": 2016, "earning_day_limit": 2015, "score_day_exclusive": 2015}
        specifications = [{"name": "baseline", "kind": "baseline", **full},
                          {"name": "repeat", "kind": "repeat", **full}]
        for c in (127, 253, 254, 1008, 2015):
            for mode in ("returns", "characteristics", "joint"):
                specifications.append({"name": f"{mode}_from_{c}", "kind": "suffix", "cutoff": c, "mode": mode,
                    "forecast_count": c + 1, "earning_day_limit": c, "score_day_exclusive": c})
        specifications += [{"name": "prefix_1008", "kind": "prefix", "length": 1008,
                            "forecast_count": 1008, "earning_day_limit": 1007, "score_day_exclusive": 1007},
                           {"name": "synthetic_append_64", "kind": "append", "append_days": 64, **full}]
        check("exact_nineteen_scenarios", read(RUN / "scenarios.json") == specifications
              and [r["scenario"] for r in summary["scenario_results"]] == specifications)
        controller_checks = [c for r in summary["scenario_results"][1:] for c in r["comparisons"]]
        counts = {state: sum(c["status"] == state for c in controller_checks)
                  for state in ("PASS", "FAIL", "NOT_APPLICABLE")}
        check("declared_controller_comparison_counts", counts == {"PASS": 93, "FAIL": 0, "NOT_APPLICABLE": 15}, counts)
        with np.load(RUN / "workers/baseline/protected_outputs.npz", allow_pickle=False) as payload:
            baseline = {key: payload[key].copy() for key in payload.files}
        pids = []
        for specification in specifications:
            name = specification["name"]
            child = RUN / "workers" / name
            status = read(child / "status.json")
            manifest = read(RUN / "manifests" / (name + ".json"))
            days = 1008 if specification["kind"] == "prefix" else 2080 if specification["kind"] == "append" else 2016
            expected_target_days = np.arange(253, specification["earning_day_limit"] + 1, dtype=int)
            expected_score_days = np.arange(253, specification["score_day_exclusive"], dtype=int)
            check(name + ":completed", status["status"] == "EXECUTED_PASS" and status["exit_code"] == 0
                  and status["returned_by_scorer"] and status["scenario"] == specification)
            check(name + ":manifest", manifest["scenario"] == specification
                  and manifest["candidate_config_sha256"] == sources["config_sha256"]
                  and Path(manifest["strategy"]) == frozen / "submission/strategy.py"
                  and Path(manifest["scorer"]) == frozen / "source/Quant Research Take-Home/score.py"
                  and Path(manifest["inputs"]) == frozen / "cache/discovery"
                  and Path(manifest["output"]) == child)
            check(name + ":source_config", status["source_hashes"] == expected_sources
                  and status["scorer_sha256"] == sources["scorer_sha256"]
                  and status["requested_config_sha256"] == sources["config_sha256"]
                  and status["requested_config"] == status["candidate_config"] == config)
            check(name + ":process", status["process_controls"]["cpu_affinity"] == [7]
                  and all(v == "1" for v in status["process_controls"]["thread_environment"].values())
                  and status["environment"]["parent_pid"] == summary["environment"]["pid"])
            pids.append(status["environment"]["pid"])
            check(name + ":input_integrity", status["inputs_unchanged"]
                  and status["input_hashes_before"] == status["input_hashes_after"]
                  and status["input_shapes"] == [[days, 1000], [days, 1000, 13], [1000]])
            layouts = status["input_layouts"]
            check(name + ":canonical_layout", layouts[0]["f_contiguous"] and not layouts[0]["c_contiguous"]
                  and layouts[0]["strides"] == [8, days * 8]
                  and layouts[1]["c_contiguous"] and not layouts[1]["f_contiguous"]
                  and all(item["dtype"] == "float64" for item in layouts), layouts)
            position_checks = status["position_checks"]
            check(name + ":full_path_outputs", position_checks["calls"] == days - 253
                  and all(position_checks[k] for k in ("all_shapes_valid", "all_finite", "held_input_unchanged"))
                  and status["forecast_full_shape"] == [days, 1000])
            alteration = status["alteration"]
            if specification["kind"] == "suffix":
                check(name + ":intervention", alteration["prefix_returns_unchanged"]
                      and alteration["prefix_characteristics_unchanged"]
                      and (alteration["returns_changed"] > 0 if specification["mode"] in ("returns", "joint")
                           else alteration["returns_changed"] == 0)
                      and (alteration["characteristics_changed"] > 0 if specification["mode"] in ("characteristics", "joint")
                           else alteration["characteristics_changed"] == 0))
            check(name + ":output_hash", digest(child / "protected_outputs.npz") == status["output_sha256"])
            with np.load(child / "protected_outputs.npz", allow_pickle=False) as actual:
                check(name + ":exact_masks", np.array_equal(actual["target_earning_days"], expected_target_days)
                      and np.array_equal(actual["score_days"], expected_score_days)
                      and actual["target_earning_days"].dtype.kind in "iu" and actual["score_days"].dtype.kind in "iu")
                check(name + ":saved_shapes", actual["forecast_prefix"].shape == (specification["forecast_count"], 1000)
                      and actual["targets"].shape == (len(expected_target_days), 1000)
                      and actual["scored_rows"].shape == (len(expected_score_days), 5)
                      and all(np.isfinite(actual[k]).all() for k in actual.files))
                if name != "baseline":
                    target_mask = baseline["target_earning_days"] <= specification["earning_day_limit"]
                    score_mask = baseline["score_days"] < specification["score_day_exclusive"]
                    compare(name + ":forecast", actual["forecast_prefix"], baseline["forecast_prefix"][:specification["forecast_count"]])
                    compare(name + ":targets", actual["targets"], baseline["targets"][target_mask])
                    compare(name + ":economics", actual["scored_rows"][:, :4], baseline["scored_rows"][score_mask, :4])
                    compare(name + ":net", actual["scored_rows"][:, 0] - actual["scored_rows"][:, 1],
                            baseline["scored_rows"][score_mask, 0] - baseline["scored_rows"][score_mask, 1])
        check("nineteen_fresh_worker_identities", len(set(pids)) == len(pids) == 19, pids)
        check("baseline_position_limits", float(np.abs(baseline["targets"]).max()) <= config["weight_cap"] + 1e-12
              and bool((np.abs(baseline["targets"]).sum(axis=1) <= config["gross_cap"] + 1e-12).all()))
        for name, key in (("forecasts.npy", "forecast_prefix"), ("targets.npy", "targets")):
            actual_sha = serialization_hash(baseline[key])
            old_sha = historical["output_arrays"][name]["sha256"]
            check("exact_original_canonical:" + name, actual_sha == old_sha, {"actual": actual_sha, "original": old_sha})
        with (ADMISSION / "historical/daily.csv").open(newline="") as stream:
            saved = list(csv.DictReader(stream))
        fields = ("gross_return", "full_cost", "closing_target_gross", "raw_market_return")
        old_rows = np.array([[float(r[k]) for k in fields] for r in saved], dtype=float)
        check("original_economic_mask", [int(r["return_index"]) for r in saved] == list(range(253, 2015)))
        check("exact_original_canonical_economics", np.array_equal(baseline["scored_rows"][:, :4], old_rows),
              {"max_abs_error": float(np.max(np.abs(baseline["scored_rows"][:, :4] - old_rows)))})
        returns = np.load(frozen / "cache/discovery/returns.npy", mmap_mode="r", allow_pickle=False)
        costs = np.load(frozen / "cache/discovery/costs.npy", mmap_mode="r", allow_pickle=False)
        rebuilt = []
        for i, day in enumerate(baseline["score_days"]):
            held_target, closing_target = baseline["targets"][i:i + 2]
            gross = float(held_target @ returns[day])
            drift = held_target * (1 + returns[day]) / (1 + gross)
            rebuilt.append((gross, float(costs @ np.abs(closing_target - drift)),
                            float(np.abs(closing_target).sum()), float(returns[day].mean())))
        compare("baseline_independent_full_fee_ledger", baseline["scored_rows"][:, :4], np.asarray(rebuilt))
        check("final_frozen_sources_and_inputs", all(digest(Path(p)) == h for p, h in expected_sources.items())
              and all(digest(Path(i["frozen_path"])) == i["frozen_sha256"] for i in inputs["files"]))
        result["status"] = "EXECUTED_PASS_SCOPE_ONLY" if all(r["status"] != "FAIL" for r in records + numeric) else "EXECUTED_FAIL"
        result["protected_comparison_summary"] = {
            "nonempty": sum(r["status"] == "PASS" for r in numeric[:-1]),
            "empty_not_applicable": sum(r["status"] == "NOT_APPLICABLE" for r in numeric[:-1]),
            "all_nonempty_exact": all(r.get("exact", True) for r in numeric[:-1]),
            "max_abs_error": max((r.get("max_abs_error", 0.0) for r in numeric[:-1]), default=0.0)}
    except Exception as exc:
        import traceback
        result.update(status="EXECUTED_FAIL", error=str(exc), traceback=traceback.format_exc())
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["limitations"] = ["Representative canonical-layout causality paths, not all possible histories.",
        "No long-history runtime, protected-period evaluation, or no-overfit certification is supplied by this readback."]
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "record_checks": len(records), "numeric_records": len(numeric),
                      "failed_checks": [r["name"] for r in records + numeric if r["status"] == "FAIL"],
                      "error": result.get("error"), "protected": result.get("protected_comparison_summary")}, indent=2))
    return 0 if result["status"] == "EXECUTED_PASS_SCOPE_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
