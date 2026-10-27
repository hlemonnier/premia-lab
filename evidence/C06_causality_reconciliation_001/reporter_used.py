#!/usr/bin/env python3
"""Read saved C06 E2E outputs; do not fit or execute any candidate.

Written prospectively under C06_FULL_DISCOVERY_CAUSALITY_PLAN.md. Requires all
three complete group packets and the unchanged admission. Every output path is
new; failed reports are preserved. Timing columns are never invariant targets.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import traceback

import numpy as np


ADMISSION_SHA256 = "0c360b8cb10e7d43a03c08b0932acd7b50cf8d2acce6f434522a7a8688d12b72"
PID_AMENDMENT_SHA256 = "1ddd690f4b4f4f6eced0d23bbf229c68bfc51d7dd51c654ada3a5d8b2484a309"
ATOL, RTOL = 1e-14, 1e-12


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def npy_sha(array):
    buffer = io.BytesIO()
    np.save(buffer, np.ascontiguousarray(array), allow_pickle=False)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def raw_parts_sha(parts):
    digest = hashlib.sha256()
    for part in parts:
        for first in range(0, len(part), 128):
            digest.update(memoryview(np.ascontiguousarray(part[first:first + 128])).cast("B"))
    return digest.hexdigest()


def expected_scenarios(group):
    full = {"forecast_count": 2016, "earning_day_limit": 2015, "score_day_exclusive": 2015}
    result = [{"name": "baseline", "kind": "baseline", **full},
              {"name": "repeat", "kind": "repeat", **full}]
    for cutoff in group["cuts"]:
        for mode in ("returns", "characteristics", "joint"):
            result.append({"name": f"{mode}_from_{cutoff}", "kind": "suffix",
                           "cutoff": cutoff, "mode": mode, "forecast_count": cutoff + 1,
                           "earning_day_limit": cutoff, "score_day_exclusive": cutoff})
    prefix = group["prefix"]
    result.append({"name": f"prefix_{prefix}", "kind": "prefix", "length": prefix,
                   "forecast_count": prefix, "earning_day_limit": prefix - 1,
                   "score_day_exclusive": prefix - 1})
    result.append({"name": "synthetic_append_64", "kind": "append", "append_days": 64, **full})
    return result


def expected_inputs(base_arrays, scenario):
    hashes, shapes = [], []
    changes = {"returns_changed": 0, "characteristics_changed": 0}
    for number, array in enumerate(base_arrays):
        parts = [array]
        kind = scenario["kind"]
        if number < 2:
            if kind == "prefix":
                parts = [array[:scenario["length"]]]
            elif kind == "append":
                suffix = array[:64][::-1]
                parts = [array, suffix * .5 if number == 0 else suffix]
            elif kind == "suffix":
                cut, mode = scenario["cutoff"], scenario["mode"]
                changed = number == 0 and mode in ("returns", "joint") or number == 1 and mode in ("characteristics", "joint")
                if changed:
                    suffix = array[cut:] * .5 if number == 0 else (array[cut:][::-1] if len(array) - cut > 1 else array[:1])
                    parts = [array[:cut], suffix]
                    count = 0
                    for first in range(0, len(suffix), 128):
                        count += int(np.count_nonzero(suffix[first:first + 128] != array[cut + first:cut + first + 128]))
                    changes["returns_changed" if number == 0 else "characteristics_changed"] = count
        hashes.append(raw_parts_sha(parts))
        shapes.append([sum(len(part) for part in parts), *array.shape[1:]])
    return hashes, shapes, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Saved-output reconciliation of39 C06 discovery/synthetic E2E workers; no fitting or new market interval",
              "reporter_sha256": sha(Path(__file__)), "checks": [], "groups": [],
              "limitations": ["Finite cutoffs cannot prove causality for every possible history.",
                              "This audit cannot establish no research overfitting or an investable edge.",
                              "Validation/audit outcomes and final long-history/clean-folder gates are separate."]}

    def check(name, passed, actual=None):
        row = {"name": name, "status": "PASS" if passed else "FAIL"}
        if actual is not None:
            row["actual"] = actual
        report["checks"].append(row)
        if not passed:
            raise AssertionError(name)

    def equal(name, actual, expected, comparisons):
        row = {"name": name, "actual_shape": list(actual.shape), "expected_shape": list(expected.shape)}
        if actual.shape != expected.shape:
            row.update(status="FAIL", reason="shape_mismatch")
        elif not actual.size:
            row.update(status="NOT_APPLICABLE", reason="empty_protected_range")
        else:
            difference = np.abs(actual - expected)
            row.update(exact=bool(np.array_equal(actual, expected)), max_abs_error=float(difference.max()),
                       mismatched_elements=int(np.count_nonzero(difference > ATOL + RTOL * np.abs(expected))),
                       elements=int(actual.size), atol=ATOL, rtol=RTOL)
            row["status"] = "PASS" if np.isfinite(actual).all() and np.isfinite(expected).all() and row["mismatched_elements"] == 0 else "FAIL"
        comparisons.append(row)
        check(name, row["status"] in ("PASS", "NOT_APPLICABLE"), {k: v for k, v in row.items() if k != "name"})

    exit_code = 1
    try:
        admission_path = root / "evidence/C06_causality_admission_002/admission.json"
        check("admission_identity", sha(admission_path) == ADMISSION_SHA256, sha(admission_path))
        check("pid_scope_amendment_identity", sha(admission_path.parent / "PID_SCOPE_AMENDMENT.md") == PID_AMENDMENT_SHA256)
        admission = read(admission_path)
        for name, expected in admission["identities"].items():
            check("admitted_identity:" + name, sha(root / name) == expected)
        expected_files = {Path(name).name: value for name, value in admission["identities"].items() if name.startswith("submission/")}
        original_summary = read(root / "evidence/discovery_C06_001/summary.json")
        original_sources = read(root / "evidence/discovery_C06_001/source_manifest.json")
        for name, expected in original_sources.items():
            if name.startswith("source/candidate/"):
                check("historical_dependency:" + name, expected_files[Path(name).name] == expected)
        with (root / "evidence/discovery_C06_001/daily.csv").open(newline="") as stream:
            historic = list(csv.DictReader(stream))
        old_days = np.array([int(row["return_index"]) for row in historic])
        old_economics = np.array([[float(row[key]) for key in ("gross_return", "full_cost", "closing_target_gross", "raw_market_return")] for row in historic])
        old_net = np.array([float(row["net_return"]) for row in historic])
        check("historical_score_mask", np.array_equal(old_days, np.arange(253, 2015)))
        all_process_identities, baselines, scenario_count = [], [], 0
        comparison_count = {"PASS": 0, "NOT_APPLICABLE": 0}
        exact_numeric = True

        for group in admission["groups"]:
            label, folder = group["group"], Path(group["output"])
            summary = read(folder / "summary.json")
            group_pids = []
            specs = expected_scenarios(group)
            check(f"{label}:controller_completed", summary.get("status") == "EXECUTED_PASS_SCOPE_ONLY" and summary.get("exit_code") == 0)
            check(f"{label}:actual_scenario_manifest", read(folder / "scenarios.json") == specs)
            check(f"{label}:summary_scenarios_exact", [item["scenario"] for item in summary["scenario_results"]] == specs)
            check(f"{label}:summary_case_statuses", all(item.get("exit_code") == 0 and item["status"] == ("REFERENCE_COMPLETED" if i == 0 else "PASS") for i, item in enumerate(summary["scenario_results"])))
            check(f"{label}:controller_affinity", summary["process_controls"]["cpu_affinity"] == [group["cpu"]])
            check(f"{label}:controller_input_scope", summary["numeric_input_rows"] == [0, 2016])
            manifest = read(folder / "source_manifest.json")
            frozen = folder / "project"
            consumed_config = read(frozen / "candidate_config.json")
            actual_sources = {Path(item["frozen"]).name: item["sha256"] for item in manifest["candidate"]}
            check(f"{label}:frozen_candidate_set", actual_sources == expected_files)
            for item in manifest["candidate"]:
                check(f"{label}:frozen_source:" + Path(item["frozen"]).name, sha(Path(item["frozen"])) == item["sha256"])
            for key, path, expected in [
                ("runner_sha256", folder / "runner_used.py", admission["identities"]["tools/verify_causality.py"]),
                ("worker_sha256", folder / "worker_used.py", admission["identities"]["tools/verify_causality.py"]),
                ("scorer_sha256", frozen / "source/Quant Research Take-Home/score.py", admission["identities"]["source/Quant Research Take-Home/score.py"]),
                ("config_sha256", frozen / "candidate_config.json", admission["identities"]["research/configs/C06_gls_factor.json"]),
                ("protocol_sha256", frozen / "RESEARCH_PROTOCOL.json", admission["identities"]["RESEARCH_PROTOCOL.json"]),
                ("plan_sha256", frozen / "verification/CAUSALITY_PLAN.md", admission["identities"]["verification/CAUSALITY_PLAN.md"]),
            ]:
                check(f"{label}:{key}", manifest[key] == expected and sha(path) == expected)
            check(f"{label}:frozen_expectations", sha(folder / "expectations.md") == manifest["plan_sha256"])
            input_manifest = read(folder / "input_manifest.json")
            check(f"{label}:input_manifest_scope", input_manifest["accessed_numeric_rows"] == [0, 2016] and input_manifest["source_cache_slice"] == [0, 2016])
            check(f"{label}:input_manifest_exact_names", [item["name"] for item in input_manifest["files"]] == ["returns.npy", "characteristics.npy", "costs.npy"])
            for item in input_manifest["files"]:
                expected = admission["historical_source_input_checks"]["cache/discovery/" + item["name"]]["expected"]
                check(f"{label}:frozen_input:" + item["name"], item["source_sha256"] == expected and item["frozen_sha256"] == expected and sha(Path(item["frozen_path"])) == expected)
            arrays = [np.load(frozen / "cache/discovery" / name, mmap_mode="r", allow_pickle=False) for name in ("returns.npy", "characteristics.npy", "costs.npy")]
            baseline = None
            group_result = {"group": label, "scenarios": []}
            report["groups"].append(group_result)
            for index, scenario in enumerate(specs):
                scenario_count += 1
                name = scenario["name"]
                worker = folder / "workers" / name
                state = read(worker / "status.json")
                saved_manifest = read(folder / "manifests" / (name + ".json"))
                check(f"{label}/{name}:manifest_scenario", saved_manifest["scenario"] == scenario)
                check(f"{label}/{name}:manifest_config", saved_manifest["candidate_config_sha256"] == manifest["config_sha256"] and Path(saved_manifest["candidate_config"]) == frozen / "candidate_config.json")
                check(f"{label}/{name}:manifest_routing", all(Path(saved_manifest[key]) == expected for key, expected in {
                    "strategy": frozen / "submission/strategy_gls_factor.py",
                    "scorer": frozen / "source/Quant Research Take-Home/score.py",
                    "inputs": frozen / "cache/discovery", "output": worker}.items()))
                check(f"{label}/{name}:worker_completed", state.get("status") == "EXECUTED_PASS" and state.get("exit_code") == 0 and state.get("returned_by_scorer") is True)
                check(f"{label}/{name}:status_scenario", state["scenario"] == scenario)
                check(f"{label}/{name}:worker_affinity", state["process_controls"]["cpu_affinity"] == [group["cpu"]] and all(value == "1" for value in state["process_controls"]["thread_environment"].values()))
                check(f"{label}/{name}:worker_source_config", {Path(k).name: v for k, v in state["source_hashes"].items()} == expected_files and state["requested_config_sha256"] == manifest["config_sha256"] and state["scorer_sha256"] == manifest["scorer_sha256"])
                check(f"{label}/{name}:consumed_config", state["requested_config"] == consumed_config and state["candidate_config"] == consumed_config)
                worker_pid = state["environment"]["pid"]
                group_pids.append(worker_pid)
                all_process_identities.append((label, worker_pid))
                check(f"{label}/{name}:worker_parent", state["environment"]["parent_pid"] == summary["environment"]["pid"])
                input_hashes, input_shapes, changes = expected_inputs(arrays, scenario)
                check(f"{label}/{name}:actual_scenario_input_identity", state["input_hashes_before"] == input_hashes and state["input_hashes_after"] == input_hashes and state["input_shapes"] == input_shapes and state.get("inputs_unchanged") is True)
                child_input = read(worker / "input_manifest.json")
                check(f"{label}/{name}:worker_input_manifest", child_input["actual_array_hashes"] == input_hashes and child_input["scenario"] == scenario)
                alteration = state["alteration"]
                check(f"{label}/{name}:actual_perturbation_counts", all(alteration[key] == value for key, value in changes.items()))
                if scenario["kind"] == "suffix":
                    check(f"{label}/{name}:altered_prefix_protected", alteration["prefix_returns_unchanged"] is True and alteration["prefix_characteristics_unchanged"] is True and alteration["cutoff"] == scenario["cutoff"] and alteration["mode"] == scenario["mode"])
                    check(f"{label}/{name}:nonidentity", all(changes[key] > 0 for key in (["returns_changed"] if scenario["mode"] == "returns" else ["characteristics_changed"] if scenario["mode"] == "characteristics" else ["returns_changed", "characteristics_changed"])))
                position = state["position_checks"]
                check(f"{label}/{name}:complete_position_path", position["calls"] == input_shapes[0][0] - 253 and all(position[key] is True for key in ("all_shapes_valid", "all_finite", "held_input_unchanged")))
                check(f"{label}/{name}:forecast_interface", state["has_forecast"] is True and state["forecast_full_shape"] == [input_shapes[0][0], 1000])
                check(f"{label}/{name}:output_file_identity", sha(worker / "protected_outputs.npz") == state["output_sha256"])
                with np.load(worker / "protected_outputs.npz", allow_pickle=False) as archive:
                    data = {key: archive[key].copy() for key in archive.files}
                check(f"{label}/{name}:output_channels", set(data) == {"forecast_prefix", "targets", "target_earning_days", "scored_rows", "score_days"})
                target_days = np.arange(253, scenario["earning_day_limit"] + 1)
                score_days = np.arange(253, scenario["score_day_exclusive"])
                check(f"{label}/{name}:actual_target_mask", np.array_equal(data["target_earning_days"], target_days))
                check(f"{label}/{name}:actual_score_mask", np.array_equal(data["score_days"], score_days))
                check(f"{label}/{name}:actual_shapes", data["forecast_prefix"].shape == (scenario["forecast_count"], 1000) and data["targets"].shape == (len(target_days), 1000) and data["scored_rows"].shape == (len(score_days), 5))
                check(f"{label}/{name}:all_finite", all(np.isfinite(value).all() for value in data.values()))
                comparisons = []
                if index == 0:
                    baseline = data
                    baselines.append(data)
                    check(f"{label}:historical_forecast_npy_sha256", npy_sha(data["forecast_prefix"]) == original_summary["output_arrays"]["forecasts.npy"]["sha256"], npy_sha(data["forecast_prefix"]))
                    check(f"{label}:historical_target_npy_sha256", npy_sha(data["targets"]) == original_summary["output_arrays"]["targets.npy"]["sha256"], npy_sha(data["targets"]))
                    check(f"{label}:historical_economic_ledger_exact", np.array_equal(data["scored_rows"][:, :4], old_economics))
                    check(f"{label}:historical_net_ledger_exact", np.array_equal(data["scored_rows"][:, 0] - data["scored_rows"][:, 1], old_net))
                else:
                    equal(f"{label}/{name}:forecast", data["forecast_prefix"], baseline["forecast_prefix"][:scenario["forecast_count"]], comparisons)
                    equal(f"{label}/{name}:targets", data["targets"], baseline["targets"][:len(target_days)], comparisons)
                    equal(f"{label}/{name}:economic_columns", data["scored_rows"][:, :4], baseline["scored_rows"][:len(score_days), :4], comparisons)
                    equal(f"{label}/{name}:net", data["scored_rows"][:, 0] - data["scored_rows"][:, 1], baseline["scored_rows"][:len(score_days), 0] - baseline["scored_rows"][:len(score_days), 1], comparisons)
                    for row in comparisons:
                        comparison_count[row["status"]] += 1
                        exact_numeric &= row.get("exact", True)
                group_result["scenarios"].append({"scenario": scenario, "worker_pid": state["environment"]["pid"], "status": "REFERENCE_COMPLETED" if index == 0 else "PASS", "numeric_comparisons": comparisons})
            del arrays
            check(f"{label}:fresh_child_pids", len(group_pids) == len(set(group_pids)) == 13, group_pids)
        check("exact_worker_count", scenario_count == 39, scenario_count)
        check("fresh_group_process_identity_count", len(all_process_identities) == len(set(all_process_identities)) == 39, all_process_identities)
        for number, baseline in enumerate(baselines[1:], start=2):
            for key in ("forecast_prefix", "targets", "target_earning_days", "score_days"):
                check(f"baseline{number}_exact:" + key, np.array_equal(baseline[key], baselines[0][key]))
            check(f"baseline{number}_exact:economics", np.array_equal(baseline["scored_rows"][:, :4], baselines[0]["scored_rows"][:, :4]))
        report.update(status="EXECUTED_PASS_SCOPE_ONLY", workers=39, comparison_scenarios=36,
                      direct_numeric_comparisons=comparison_count, all_nonempty_numeric_comparisons_exact=exact_numeric,
                      unchanged_scenario_masks=39, historical_baselines_reconciled=3)
        exit_code = 0
    except Exception:
        report.update(status="EXECUTED_FAIL_OR_INCOMPLETE", error=traceback.format_exc())
        (out / "stderr.log").write_text(report["error"])
        traceback.print_exc()
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["exit_code"] = exit_code
        (out / "summary.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        (out / "stdout.log").write_text(report["status"] + "\n")
        print(json.dumps({key: report[key] for key in ("status", "exit_code")}, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
