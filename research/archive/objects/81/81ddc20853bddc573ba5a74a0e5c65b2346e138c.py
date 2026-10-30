#!/usr/bin/env python3
"""Report fixed-policy uncertainty from completed saved ledgers only.

No candidate is imported or executed. Actual protected packets require the
root-frozen nomination hash and separate session release. See the two frozen
plans; zero-check is the sole pre-access E2E mode.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import traceback

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for variable in THREADS:
    os.environ[variable] = "1"
sys.dont_write_bytecode = True
import numpy as np

PLAN_SHA = "ff7526bf7b869400274aed83e8c7f2d9a4e1f10a561da0591423e0cbafeef132"
WORKFLOW_SHA = "197bb5fc1e6394f772f6e71788ccb8d66ad401f47d43068aaf565a632508d594"
PROTOCOL_SHA = "cc2de53284feaeff97022c869ee8ee6e7b9fb40ab3f3dd1c0353e5b9923ed737"
HELPER_SHA = "6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69"
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
IDS = {"C06": "C06_gls_factor", "C09": "C09_additive_long_memory"}
VALIDATION_MASKS = {"validation_a": [2016, 2520], "validation_b": [2520, 3023], "pooled_validation": [2016, 3023]}
AUDIT_MASKS = {"locked_audit": [3024, 3779]}
FIELDS = ["return_index", "csv_day_label", "gross_return", "full_cost", "net_return", "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds"]
BLOCK_LENGTHS, REPLICATES, COST_MULTIPLIERS = (21, 63), 1000, (1.0, 1.5, 2.0)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1048576), b""):
            digest.update(part)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def local_file(folder, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Evidence paths must be relative without parent traversal")
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder.resolve()) or not path.is_file():
        raise ValueError(f"Missing or escaped evidence path: {relative}")
    return path


def interval(values):
    finite = [value for value in values if value is not None and math.isfinite(value)]
    bounds = [float(x) for x in np.quantile(finite, [.025, .975], method="linear")] if finite else [None, None]
    return {"lower_2_5_percent": bounds[0], "upper_97_5_percent": bounds[1],
            "finite_replicates": len(finite), "undefined_replicates": len(values) - len(finite),
            "total_replicates": len(values), "quantile_method": "linear",
            "conditioning": "Quantiles of finite replicates; undefined ratios are excluded and counted",
            "undefined_reason": "No finite replicates" if not finite else None}


def resample(arms, size, length, out):
    """Paired ordinary nonwrapping moving blocks, fixed before outcomes."""
    seed = 20261027 + length
    rng = np.random.default_rng(seed)
    count = math.ceil(size / length)
    starts = rng.integers(0, size - length + 1, size=(REPLICATES, count))
    arm_names = list(arms)
    pair = ("C06", "C09") if arm_names == ["C06", "C09"] else ("ZERO_A", "ZERO_B") if arm_names == ["ZERO_A", "ZERO_B"] else None
    records = []
    means = {name: [] for name in arm_names}
    sharpes = {name: [] for name in arm_names}
    differences = []
    for replicate, firsts in enumerate(starts):
        indices = (firsts[:, None] + np.arange(length)[None, :]).reshape(-1)[:size]
        row = {"replicate": replicate, "block_length": length, "arms": {}}
        for name in arm_names:
            sampled = arms[name][indices]
            net = sampled[:, 0] - sampled[:, 1]
            mean, deviation = float(net.mean()), float(net.std(ddof=0))
            annual = 252 * mean
            sharpe = math.sqrt(252) * mean / deviation if deviation else None
            if not math.isfinite(annual) or sharpe is not None and not math.isfinite(sharpe):
                raise FloatingPointError("Unrepresentable bootstrap arithmetic")
            means[name].append(annual)
            sharpes[name].append(sharpe)
            row["arms"][name] = {"annual_arithmetic_net_return": annual, "net_sharpe": sharpe,
                                  "undefined_reason": "Zero population standard deviation" if sharpe is None else None}
        if pair:
            left, right = (sharpes[name][-1] for name in pair)
            difference = None if left is None or right is None else left - right
            differences.append(difference)
            row["paired_sharpe_difference"] = difference
            row["paired_undefined_reason"] = "At least one component Sharpe is undefined" if difference is None else None
        records.append(row)
    write(out / f"block_starts_{length}.json", {"seed": seed, "sample_size": size, "block_length": length,
          "replicates": REPLICATES, "blocks_per_replicate": count, "valid_starts_inclusive": [0, size - length],
          "algorithm": "Uniform nonwrapping starts; concatenate contiguous blocks; truncate final block toN",
          "paired_arms_share_indices": True, "starts": starts.tolist()})
    write(out / f"bootstrap_replicates_{length}.json", records)
    result = {"block_length": length, "seed": seed, "sample_size": size, "replicates": REPLICATES,
              "candidates": {name: {"annual_arithmetic_net_return": interval(means[name]), "net_sharpe": interval(sharpes[name])} for name in arm_names}}
    if pair:
        result["paired_sharpe_difference"] = {"direction": f"{pair[0]} minus {pair[1]}", **interval(differences)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--mode", choices=("validation", "audit", "zero-check"), required=True)
    parser.add_argument("--run", action="append", required=True, help="C06=packet, C09=packet, or ZERO=synthetic packet")
    parser.add_argument("--nomination-sha256", help="Exact root-frozen stage nomination hash; required for actual protected modes")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = {"status": "RUNNING", "mode": args.mode, "started_utc": datetime.now(timezone.utc).isoformat(),
              "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
              "protected_outcome_read_started": False, "checks": [], "candidates": {}, "bootstrap": [],
              "model_executions": 0, "selection_rule_changed": False,
              "limitations": ["Fixed-policy bootstrap ranges are conditional on observed dependence and the exposed research path.",
                              "They do not correct all selection optimism or prove stationarity, no overfit, or future profitability.",
                              "Cost stresses hold recorded decisions fixed; the original1.0 fee case alone remains the selection input."]}
    write(out / "summary.json", report)
    logs = []
    consumed, original_packets = {}, {}

    def check(name, passed, actual=None):
        item = {"name": name, "status": "PASS" if passed else "FAIL"}
        if actual is not None:
            item["actual"] = actual
        report["checks"].append(item)
        logs.append(json.dumps(item, allow_nan=False))
        if not passed:
            raise AssertionError(name)

    def verify(folder, relative, artifacts):
        path = local_file(folder, relative)
        check("artifact_record:" + str(folder.name) + "/" + relative, relative in artifacts)
        expected = artifacts[relative]
        check("artifact_identity:" + str(folder.name) + "/" + relative,
              path.stat().st_size == expected["bytes"] and sha(path) == expected["sha256"])
        return path

    exit_code = 1
    try:
        run_map = {}
        for argument in args.run:
            label, path = argument.split("=", 1)
            check("unique_run:" + label, label not in run_map)
            run_map[label] = Path(path).resolve()
        expected_labels = {"ZERO"} if args.mode == "zero-check" else {"C06", "C09"} if args.mode == "validation" else set(run_map)
        check("mode_run_set", set(run_map) == expected_labels and (args.mode != "audit" or len(run_map) == 1 and set(run_map) <= set(IDS)), sorted(run_map))
        check("nomination_argument", args.nomination_sha256 is None if args.mode == "zero-check" else isinstance(args.nomination_sha256, str) and len(args.nomination_sha256) == 64)
        plan = root / "research/PROTECTED_UNCERTAINTY_PLAN.md"
        workflow = root / "verification/PROTECTED_UNCERTAINTY_E2E_PLAN.md"
        check("fixed_reporting_plan", sha(plan) == PLAN_SHA)
        check("fixed_workflow_expectations", sha(workflow) == WORKFLOW_SHA)
        for source, name in [(plan, "expectations.md"), (workflow, "workflow_expectations.md"), (Path(__file__).resolve(), "reporter_used.py")]:
            shutil.copyfile(source, out / name)
            consumed[name] = sha(out / name)
        environment = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                       "numpy": np.__version__, "pid": os.getpid(), "thread_environment": {k: os.environ[k] for k in THREADS},
                       "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None}
        write(out / "environment.json", environment)
        masks = AUDIT_MASKS if args.mode == "audit" else VALIDATION_MASKS
        days = 3780 if args.mode == "audit" else 3024
        report["score_masks"] = masks
        report["bootstrap_period"] = "locked_audit" if args.mode == "audit" else "pooled_validation"
        bootstrap_arms = {}
        input_identities = {}
        nominations = []
        helper = None

        for label in sorted(run_map):
            packet = run_map[label]
            original_packets[label] = str(packet)
            artifacts = read(local_file(packet, "artifact_manifest.json"))
            metadata_names = ["input_manifest.json", "source_manifest.json", "config.json", "protocol_used.json", "metric_helper_used.py", "environment.json"]
            for name in metadata_names:
                verify(packet, name, artifacts)
            inputs, config = read(packet / "input_manifest.json"), read(packet / "config.json")
            input_identities[label] = {name: entry["sha256"] for name, entry in inputs["files"].items()}
            check(label + ":input_scope_before_outcome_access", inputs["input_slice"] == [0, days])
            check(label + ":fixture_kind_before_outcome_access", inputs["kind"] == ("synthetic_exact_zero" if args.mode == "zero-check" else "canonical_market"))
            candidate_id = IDS["C06"] if label == "ZERO" else IDS[label]
            check(label + ":candidate_identity", config["candidate_id"] == candidate_id)
            check(label + ":protocol_identity", sha(packet / "protocol_used.json") == PROTOCOL_SHA)
            check(label + ":metric_helper_identity", sha(packet / "metric_helper_used.py") == HELPER_SHA)
            protocol = read(packet / "protocol_used.json")
            periods = {p["name"]: p["score_slice"] for p in protocol["periods"]}
            check(label + ":protocol_masks", all(periods[name] == mask for name, mask in masks.items()))
            if args.mode == "zero-check":
                check(label + ":no_protected_nomination", not (packet / "nomination_used.json").exists())
            else:
                verify(packet, "nomination_used.json", artifacts)
                check(label + ":nomination_identity", sha(packet / "nomination_used.json") == args.nomination_sha256)
                nomination = read(packet / "nomination_used.json")
                nominations.append(sha(packet / "nomination_used.json"))
                check(label + ":approved_stage", nomination.get("schema_version") == 1 and nomination.get("status") == "ROOT_APPROVED_PROTECTED_REPLAY" and nomination.get("stage") == args.mode)
                nominees = nomination["candidates"]
                chosen = [c for c in nominees if c["candidate_id"] == candidate_id]
                check(label + ":nominated_config", len(chosen) == 1 and chosen[0]["config_sha256"] == sha(packet / "config.json"))
                if args.mode == "validation":
                    check(label + ":exact_validation_pair", len(nominees) == 2 and {c["candidate_id"] for c in nominees} == set(IDS.values()))
                else:
                    verify(packet, "selection_used.json", artifacts)
                    check(label + ":selection_record_identity", sha(packet / "selection_used.json") == nomination["selection_record"]["sha256"])
                    selection = read(packet / "selection_used.json")
                    check(label + ":single_audit_selection", len(nominees) == 1 and nomination["selected_candidate_id"] == candidate_id and selection["selected_candidate_id"] == candidate_id and selection["config_sha256"] == sha(packet / "config.json"))
                report["protected_outcome_read_started"] = True
                write(out / "summary.json", report)

            verify(packet, "summary.json", artifacts)
            state = read(packet / "summary.json")
            check(label + ":completed_controller", state["status"] == "EXECUTED_PASS_SCOPE_ONLY" and state["exit_code"] == 0 and state["returned_by_official_scorer"] is True)
            check(label + ":controller_mode", state["mode"] == ("synthetic-zero" if args.mode == "zero-check" else args.mode))
            check(label + ":complete_continuous_replay", state["expected_input_slice"] == [0, days] and state["completed_rebalances"] == days - 253 and state["score_masks"] == masks)
            check(label + ":controller_configuration", state["configuration"] == config)
            check(label + ":controller_checks", bool(state["checks"]) and all(c["status"] == "PASS" for c in state["checks"]))
            check(label + ":access_flags", state["protected_numeric_access_started"] == (args.mode != "zero-check") and state["validation_opened"] == (args.mode != "zero-check") and state["audit_opened"] == (args.mode == "audit"))
            check(label + ":recorded_input_integrity", state["input_hashes_after"] == {name: entry["sha256"] for name, entry in inputs["files"].items()})
            source_map = read(packet / "source_manifest.json")
            check(label + ":source_contract", source_map["metric_helper_used.py"] == HELPER_SHA and source_map["source/score.py"] == SCORER_SHA and source_map["protocol_used.json"] == PROTOCOL_SHA)
            if args.mode != "zero-check":
                check(label + ":nominated_control_identities", nomination["protocol_sha256"] == PROTOCOL_SHA
                      and nomination["scorer_sha256"] == SCORER_SHA and nomination["metric_helper_sha256"] == HELPER_SHA
                      and source_map["runner_used.py"] == nomination["controller_sha256"]
                      and source_map["expectations.md"] == nomination["replay_plan_sha256"]
                      and source_map["admission_plan_used.md"] == nomination["admission_plan_sha256"])
                nominated_sources = {"source/candidate/" + Path(name).name: digest for name, digest in chosen[0]["source_sha256"].items()}
                actual_sources = {name: digest for name, digest in source_map.items() if name.startswith("source/candidate/")}
                check(label + ":nominated_candidate_sources", nominated_sources == actual_sources and len(nominated_sources) == len(chosen[0]["source_sha256"]))
            for name, expected in source_map.items():
                path = verify(packet, name, artifacts)
                check(label + ":source_identity:" + name, sha(path) == expected)
            verify(packet, "daily.csv", artifacts)
            snapshot = out / "inputs" / label
            snapshot.mkdir(parents=True)
            files = set(metadata_names) | set(source_map) | {"summary.json", "daily.csv", "artifact_manifest.json"}
            for name in sorted(files):
                source = local_file(packet, name)
                destination = snapshot / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                consumed[str(destination.relative_to(out))] = sha(destination)
            if helper is None:
                spec = importlib.util.spec_from_file_location("frozen_uncertainty_metrics", snapshot / "metric_helper_used.py")
                helper = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = helper
                spec.loader.exec_module(helper)
            with (snapshot / "daily.csv").open(newline="") as stream:
                reader = csv.DictReader(stream)
                check(label + ":daily_schema", reader.fieldnames == FIELDS, reader.fieldnames)
                saved = list(reader)
            indices = np.array([int(row["return_index"]) for row in saved])
            check(label + ":complete_daily_indices", np.array_equal(indices, np.arange(253, days - 1)), len(indices))
            check(label + ":csv_day_labels", all(int(row["csv_day_label"]) == int(day) + 1 for row, day in zip(saved, indices)))
            rows = np.array([[float(row[key]) for key in ("gross_return", "full_cost", "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds")] for row in saved])
            saved_net = np.array([float(row["net_return"]) for row in saved])
            check(label + ":finite_ledger", rows.shape == (days - 254, 5) and np.isfinite(rows).all() and np.isfinite(saved_net).all())
            check(label + ":full_fee_net_identity", np.array_equal(saved_net, rows[:, 0] - rows[:, 1]) and np.all(rows[:, 1] >= 0))
            check(label + ":valid_exposure_and_latency", np.all(rows[:, 2] >= 0) and np.all(rows[:, 4] >= 0))
            if args.mode == "zero-check":
                check(label + ":exact_zero_economics", np.count_nonzero(rows[:, :4]) == 0 and np.count_nonzero(saved_net) == 0)
            candidate = {"candidate_id": candidate_id, "source_packet": str(packet), "metrics": {}, "cost_stress": {},
                         "full_replay_candidate_runtime": state["timing"], "controller_candidate_feasibility": state["candidate_feasibility"]}
            check(label + ":finite_runtime", all(isinstance(value, (int, float)) and math.isfinite(value) and value >= 0 for value in state["timing"].values()))
            for name, (first, stop) in masks.items():
                mask = (indices >= first) & (indices < stop)
                check(label + ":exact_mask:" + name, np.array_equal(indices[mask], np.arange(first, stop)), int(mask.sum()))
                selected = rows[mask]
                metrics = helper.summarize_rows(selected, indices[mask])
                check(label + ":controller_metric_reconciliation:" + name, metrics == state["metrics"][name])
                candidate["metrics"][name] = metrics
                stresses = []
                for multiplier in COST_MULTIPLIERS:
                    stressed = selected.copy()
                    stressed[:, 1] *= multiplier
                    stressed_metrics = helper.summarize_rows(stressed, indices[mask])
                    if multiplier == 1:
                        check(label + ":original_cost_case:" + name, stressed_metrics == metrics)
                    stresses.append({"fee_multiplier": multiplier, "fixed_recorded_decisions": True, "metrics": stressed_metrics})
                candidate["cost_stress"][name] = stresses
                if name == report["bootstrap_period"]:
                    bootstrap_arms[label] = selected[:, [0, 1, 3]].copy()
            report["candidates"][label] = candidate
        if args.mode != "zero-check":
            check("shared_nomination_identity", len(set(nominations)) == 1)
            if args.mode == "validation":
                check("paired_canonical_input_identities", input_identities["C06"] == input_identities["C09"])
                check("paired_market_observations", np.array_equal(bootstrap_arms["C06"][:, 2], bootstrap_arms["C09"][:, 2]))
        else:
            zero = bootstrap_arms.pop("ZERO")
            bootstrap_arms = {"ZERO_A": zero, "ZERO_B": zero}
            report["synthetic_aliases"] = {"ZERO_A": "The same one ZERO synthetic ledger", "ZERO_B": "The same one ZERO synthetic ledger", "actual_candidate_executions_in_source_fixture": 1, "actual_c09_execution": False}
        sample_size = 755 if args.mode == "audit" else 1007
        check("bootstrap_sample_sizes", all(len(array) == sample_size for array in bootstrap_arms.values()), sample_size)
        for length in BLOCK_LENGTHS:
            result = resample(bootstrap_arms, sample_size, length, out)
            report["bootstrap"].append(result)
            if args.mode == "zero-check":
                for label, metrics in result["candidates"].items():
                    mean, ratio = metrics["annual_arithmetic_net_return"], metrics["net_sharpe"]
                    check(f"zero_bootstrap:{length}:{label}", mean["lower_2_5_percent"] == mean["upper_97_5_percent"] == 0 and mean["finite_replicates"] == 1000 and ratio["finite_replicates"] == 0 and ratio["undefined_replicates"] == 1000 and ratio["lower_2_5_percent"] is None and ratio["upper_97_5_percent"] is None)
                pair = result["paired_sharpe_difference"]
                check(f"zero_paired_ratio:{length}", pair["finite_replicates"] == 0 and pair["undefined_replicates"] == 1000 and pair["lower_2_5_percent"] is None and pair["upper_97_5_percent"] is None)
        if args.mode == "zero-check":
            for name, metrics in report["candidates"]["ZERO"]["metrics"].items():
                check("zero_metrics:" + name, all(metrics[key] is None for key in ("net_sharpe", "gross_sharpe", "realized_net_market_beta")) and all(metrics[key] == 0 for key in ("annual_arithmetic_net_return", "annual_full_cost", "annual_net_volatility", "max_drawdown")))
                for stress in report["candidates"]["ZERO"]["cost_stress"][name]:
                    value = stress["metrics"]
                    check(f"zero_stress:{name}:{stress['fee_multiplier']}", value["annual_arithmetic_net_return"] == value["annual_full_cost"] == 0 and value["net_sharpe"] is None and value["realized_net_market_beta"] is None)
        check("consumed_snapshots_unchanged", all(sha(out / name) == digest for name, digest in consumed.items()))
        write(out / "source_manifest.json", consumed)
        write(out / "input_manifest.json", {"packets": original_packets, "nomination_sha256": args.nomination_sha256, "consumed_file_sha256": consumed,
              "coverage": "Consumed saved ledgers and evidence/source metadata verified; model/input NPY arrays are not consumed by this report"})
        rerun = [sys.executable, str(out / "reporter_used.py"), "--project", str(root), "--mode", args.mode, "--out", str(out) + "_rerun"]
        for label in sorted(run_map):
            rerun += ["--run", label + "=" + str(out / "inputs" / label)]
        if args.nomination_sha256:
            rerun += ["--nomination-sha256", args.nomination_sha256]
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        report["status"], exit_code = "EXECUTED_PASS_SCOPE_ONLY", 0
        (out / "README.md").write_text("# Saved-ledger uncertainty report\n\n"
            f"Mode: {args.mode}. Status: EXECUTED_PASS_SCOPE_ONLY. No candidate execution or selection-rule change.\n\n"
            "summary.json contains exact-period metrics, full-replay candidate runtime, fixed-decision fee stresses, bootstrap percentile ranges and undefined counts. Block-start matrices and complete replicate records are retained separately. The two block lengths21/63,1000replicates and seeds20261027+L were fixed before protected outcomes. Paired validation draws use identical row indices; the reported difference is C06-minus-C09.\n\n"
            "A zero-check uses two explicitly synthetic aliases of one cash ledger. Its undefined ratios must remain null, including paired differences; it is not a C09 execution. Bootstrap ranges condition on the observed sample and research path and do not establish absence of overfit, a probability of being the true winner, or future stationarity. Cost stresses do not rerun the allocator and do not change selection.\n\n"
            "The exact reporter/plans, consumed evidence files, identities, environment, full results, logs and rerun command are preserved. Only the finite replicate subset enters percentile calculation; undefined counts are disclosed.\n")
    except Exception:
        report["status"] = "EXECUTED_FAIL_OR_INCOMPLETE"
        report["error"] = traceback.format_exc()
        (out / "stderr.log").write_text(report["error"])
        traceback.print_exc()
    finally:
        report["exit_code"] = exit_code
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write(out / "summary.json", report)
        (out / "stdout.log").write_text("\n".join(logs) + "\n" + report["status"] + "\n")
        if not (out / "stderr.log").exists():
            (out / "stderr.log").write_text("")
        (out / "setup.md").write_text("# Workflow setup\n\n" + report["command"] + "\n\n"
            "Source review and the zero-ledger E2E precede actual protected reporting. Real protected reporting requires the root's existing stage release and unchanged nomination identity. This workflow reads completed saved ledgers and never invokes a model.\n")
        write(out / "artifact_manifest.json", {str(path.relative_to(out)): {"sha256": sha(path), "bytes": path.stat().st_size} for path in sorted(out.rglob("*")) if path.is_file() and path != out / "artifact_manifest.json"})
        print(json.dumps({"status": report["status"], "mode": args.mode, "exit_code": exit_code}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
