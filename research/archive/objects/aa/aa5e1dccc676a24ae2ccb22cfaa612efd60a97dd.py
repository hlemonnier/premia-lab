#!/usr/bin/env python3
"""Preimplementation E2E verifier for frozen-policy descriptive attribution.

Only synthetic packets are generated/read here. No strategy is executed.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import traceback

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
sys.dont_write_bytecode = True
import numpy as np

ATOL, RTOL = 1e-12, 1e-10
DAYS, STOCKS, CUT = 420, 16, 337
CONFIG_SHA = "aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba"
HELPERS = {
    "strategy.py": "104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7",
    "portfolio.py": "fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475",
    "strategy_factor.py": "9e63257c14859430b5190763c5f1fd35320c582019c941ae28b43243587a4959",
    "factor_portfolio.py": "60af66f9797585fec4189206c50481bfd1d3554beb6442ed5c19b2399ce375e5",
}
LEDGER_FIELDS = ["return_index", "csv_day_label", "gross_return", "full_cost", "net_return",
                 "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds"]
COMPONENTS = ("market_component", "residual_factor_component", "remainder_component")
VALUE_FIELDS = (*COMPONENTS, "full_cost", "gross_return", "net_return")
OUTPUT_FIELDS = ("return_index", "target_index", "risk_history_stop_exclusive",
                 "factor_history_stop_exclusive", "factor_age_days", "factor_rank",
                 "estimated_market_exposure", *VALUE_FIELDS, "gross_reconciliation_error",
                 "net_reconciliation_error", "opening_gross_reconciliation_error")
MASKS = {"discovery": [253, 2015], "validation": [2016, 3023], "audit": [3024, 3779]}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def read(path):
    return json.loads(Path(path).read_text())


def inventory(folder):
    return {str(path.relative_to(folder)): {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in sorted(folder.rglob("*")) if path.is_file() and path != folder / "artifact_manifest.json"}


def table(path, fields, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def hadamard():
    matrix = np.ones((1, 1))
    while len(matrix) < STOCKS:
        matrix = np.block([[matrix, matrix], [matrix, -matrix]])
    return matrix


def synthetic_arrays():
    h = hadamard()
    dates = np.arange(DAYS, dtype=float)
    market = .002 * np.cos(2 * np.pi * dates / 252)
    amplitudes = .0006 * np.arange(11, 0, -1)
    factor_scores = np.cos(2 * np.pi * dates[:, None] * np.arange(2, 13)[None, :] / 252) * amplitudes
    returns = np.asfortranarray(market[:, None] + factor_scores @ h[:, 1:12].T)
    earning = np.arange(253, DAYS, dtype=float)
    exposures = np.zeros((len(earning), STOCKS))
    exposures[:, 0] = .025 + .005 * np.sin(.37 * earning)
    exposures[:, 1] = .035 + .008 * np.sin(.13 * earning)
    exposures[:, 5] = .017 * np.cos(.11 * earning)
    exposures[:, 11] = .022 + .006 * np.cos(.19 * earning)
    targets = exposures @ h.T / STOCKS
    return returns, targets, h


def ledger(returns, targets):
    costs = np.linspace(.0002, .0008, returns.shape[1])
    rows = []
    for t in range(253, len(returns) - 1):
        opening, closing = targets[t - 253], targets[t - 252]
        gross = float(opening @ returns[t])
        held = opening * (1 + returns[t]) / (1 + gross)
        fee = float(costs @ np.abs(closing - held))
        rows.append(dict(zip(LEDGER_FIELDS, [t, t + 1, gross, fee, gross - fee,
                    float(np.abs(closing).sum()), float(returns[t].mean()), 0.0])))
    return rows


def make_packet(root, folder, returns, targets, definition, corrupt=None):
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "inputs").mkdir()
    (folder / "source/candidate").mkdir(parents=True)
    np.save(folder / "inputs/returns.npy", returns, allow_pickle=False)
    np.save(folder / "targets.npy", targets, allow_pickle=False)
    shutil.copyfile(root / "research/configs/C09_additive_long_memory.json", folder / "config.json")
    if sha(folder / "config.json") != CONFIG_SHA:
        raise AssertionError("Original C09 config identity changed")
    sources = {"config.json": CONFIG_SHA}
    for name, expected in HELPERS.items():
        source = root / "evidence/audit_C09_001/source/candidate" / name
        if sha(source) != expected:
            raise AssertionError("Original helper identity changed: " + name)
        shutil.copyfile(source, folder / "source/candidate" / name)
        sources["source/candidate/" + name] = expected
    write(folder / "source_manifest.json", sources)
    rows = ledger(returns, targets)
    if corrupt == "index":
        rows[7]["return_index"] = rows[6]["return_index"]
    elif corrupt == "accounting":
        rows[7]["gross_return"] += .001
        rows[7]["net_return"] += .001
    table(folder / "daily.csv", LEDGER_FIELDS, rows)
    write(folder / "input_manifest.json", {
        "kind": "synthetic_frozen_attribution", "input_slice": [0, len(returns)],
        "files": {"returns.npy": {"sha256": sha(folder / "inputs/returns.npy"),
          "shape": list(returns.shape), "dtype": str(returns.dtype), "strides": list(returns.strides),
          "c_contiguous": bool(returns.flags.c_contiguous), "f_contiguous": bool(returns.flags.f_contiguous)}}})
    write(folder / "fixture_definition.json", definition)
    write(folder / "artifact_manifest.json", inventory(folder))
    return rows


def oracle(returns, targets, h, selected=None, zero=False):
    indices = list(range(253, len(returns) - 1)) if selected is None else list(selected)
    q = h[:, 1:11] / math.sqrt(STOCKS)
    expected = []
    for t in indices:
        weights = targets[t - 253]
        market = float(returns[t].mean())
        residual = returns[t] - market
        factor = q @ (q.T @ residual) if not zero else np.zeros(STOCKS)
        expected.append([float(weights.sum() * market), float(weights @ factor),
                         float(weights @ (residual - factor))])
    return np.asarray(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--implementation", type=Path)
    parser.add_argument("--expect-missing", action="store_true")
    args = parser.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    implementation = (args.implementation or root / "tools/attribute_frozen_policy.py").resolve()
    out.mkdir(parents=True, exist_ok=False)
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    state = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
             "command": command, "market_data_read": False, "model_executions": 0,
             "expected_missing_mode": args.expect_missing, "checks": [], "processes": []}
    write(out / "summary.json", state)
    shutil.copyfile(Path(__file__).resolve(), out / "verifier_used.py")
    shutil.copyfile(root / "verification/FROZEN_ATTRIBUTION_E2E_PLAN.md", out / "expectations.md")
    shutil.copyfile(root / "research/FROZEN_ATTRIBUTION_PLAN_20261027.md", out / "admission.md")
    write(out / "environment.json", {"python": sys.version, "executable": sys.executable,
          "numpy": np.__version__, "platform": platform.platform(),
          "threads": {name: os.environ[name] for name in THREADS}})
    (out / "setup.md").write_text("# Synthetic attribution E2E\n\n" + command + "\n\n"
        "All fixtures are deterministic synthetic saved packets. No market array, forecast, rebalance or strategy execution.\n")
    exit_code = 1
    handoff_before = {str(p.relative_to(root)): sha(p) for p in sorted((root / "handoff").rglob("*.py"))}
    write(out / "handoff_before.json", handoff_before)
    logs = []

    def check(name, passed, actual=None):
        item = {"name": name, "status": "PASS" if passed else "FAIL"}
        if actual is not None:
            item["actual"] = actual
        state["checks"].append(item)
        logs.append(json.dumps(item, allow_nan=False))
        if not passed:
            raise AssertionError(name)

    def close(name, actual, expected):
        a, e = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        difference = float(np.max(np.abs(a - e))) if a.size else 0.0
        check(name, a.shape == e.shape and np.isfinite(a).all() and
              np.allclose(a, e, atol=ATOL, rtol=RTOL), {"max_abs_error": difference})

    def launch(name, packet, digest=None):
        result_dir = out / "runs" / name
        result_dir.parent.mkdir(exist_ok=True)
        argv = [sys.executable, str(frozen_implementation), "--project", str(root),
                "--packet", str(packet), "--mode", "synthetic", "--packet-manifest-sha256",
                digest or sha(packet / "artifact_manifest.json"), "--out", str(result_dir)]
        record = {"name": name, "command": shlex.join(argv), "packet": str(packet),
                  "packet_manifest_sha256": sha(packet / "artifact_manifest.json"), "output": str(result_dir)}
        state["processes"].append(record)
        write(out / "processes.json", state["processes"])
        process = subprocess.run(argv, cwd=root, env=os.environ.copy(), text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out / (name + "_stdout.log")).write_text(process.stdout)
        (out / (name + "_stderr.log")).write_text(process.stderr)
        record["exit_code"] = process.returncode
        summary = read(result_dir / "summary.json") if (result_dir / "summary.json").is_file() else None
        return result_dir, process, summary

    def read_success(name, packet, expected_days, expected_rank=None):
        directory, process, summary = launch(name, packet)
        check(name + ":exit", process.returncode == 0, process.returncode)
        check(name + ":status", summary is not None and summary["status"] == "EXECUTED_PASS_SCOPE_ONLY"
              and summary["exit_code"] == 0 and summary["model_executions"] == 0)
        check(name + ":numeric_read_declared", summary["numeric_content_read_started"] is True)
        with (directory / "daily_attribution.csv").open(newline="") as stream:
            reader = csv.DictReader(stream)
            check(name + ":required_columns", set(OUTPUT_FIELDS) <= set(reader.fieldnames or []))
            rows = list(reader)
        values = np.array([[float(row[key]) for key in OUTPUT_FIELDS] for row in rows])
        indices = np.array([int(row["return_index"]) for row in rows])
        check(name + ":rows_and_finiteness", np.array_equal(indices, np.arange(253, expected_days - 1))
              and values.shape == (expected_days - 254, len(OUTPUT_FIELDS)) and np.isfinite(values).all())
        check(name + ":opening_target_indices", all(int(r["target_index"]) == int(r["return_index"]) - 253 for r in rows))
        check(name + ":causal_risk_cutoffs", all(int(r["risk_history_stop_exclusive"]) == int(r["return_index"]) for r in rows))
        check(name + ":factor_refresh_cutoffs", all(int(r["factor_history_stop_exclusive"]) ==
              253 + 21 * ((int(r["return_index"]) - 253) // 21) for r in rows))
        check(name + ":factor_ages", all(int(r["factor_age_days"]) ==
              (int(r["return_index"]) - 253) % 21 for r in rows))
        if expected_rank is not None:
            check(name + ":known_span_rank", all(int(row["factor_rank"]) == expected_rank for row in rows))
        for error in ("gross_reconciliation_error", "net_reconciliation_error", "opening_gross_reconciliation_error"):
            close(name + ":" + error, [float(row[error]) for row in rows], np.zeros(len(rows)))
        for file in ("artifact_manifest.json", "input_manifest.json", "source_manifest.json", "rerun.txt"):
            check(name + ":evidence:" + file, (directory / file).is_file())
        actual_artifacts = read(directory / "artifact_manifest.json")
        for file in ("summary.json", "daily_attribution.csv"):
            entry = actual_artifacts.get(file, {})
            check(name + ":output_manifest:" + file, entry.get("sha256") == sha(directory / file)
                  and entry.get("bytes") == (directory / file).stat().st_size)
        check(name + ":fixed_masks", set(summary["stages"]) == set(MASKS))
        for stage, mask in MASKS.items():
            stats = summary["stages"][stage]
            take = (indices >= mask[0]) & (indices < mask[1])
            chosen = [row for row, active in zip(rows, take) if active]
            check(name + ":" + stage + ":mask", stats["index_slice"] == mask and stats["rows"] == int(take.sum()))
            if not chosen:
                keys = ("annual_arithmetic_mean", "annual_volatility", "gross_covariance_contribution",
                        "estimated_market_exposure", "factor_rank")
                check(name + ":" + stage + ":empty_null", all(all(value is None for value in stats[key].values()) for key in keys))
                continue
            selected = {key: np.array([float(row[key]) for row in chosen]) for key in VALUE_FIELDS}
            for key in VALUE_FIELDS:
                close(name + ":" + stage + ":mean:" + key, [stats["annual_arithmetic_mean"][key]], [252 * selected[key].mean()])
                close(name + ":" + stage + ":vol:" + key, [stats["annual_volatility"][key]], [math.sqrt(252) * selected[key].std(ddof=0)])
            gross = selected["gross_return"]
            variance = float(np.mean((gross - gross.mean()) ** 2))
            contributions = stats["gross_covariance_contribution"]
            for key in COMPONENTS:
                if variance == 0:
                    check(name + ":" + stage + ":undefined_contribution:" + key, contributions[key] is None)
                else:
                    comp = selected[key]
                    expected = float(np.mean((comp - comp.mean()) * (gross - gross.mean())) / variance)
                    close(name + ":" + stage + ":covariance_contribution:" + key, [contributions[key]], [expected])
            if variance:
                close(name + ":" + stage + ":contributions_add", [sum(contributions.values())], [1.0])
            exposures = np.abs([float(row["estimated_market_exposure"]) for row in chosen])
            close(name + ":" + stage + ":exposure", list(stats["estimated_market_exposure"][key] for key in ("mean_abs", "max_abs")), [float(exposures.mean()), float(exposures.max())])
            ranks = [int(row["factor_rank"]) for row in chosen]
            check(name + ":" + stage + ":ranks", stats["factor_rank"] == {"min": min(ranks), "max": max(ranks)})
            for result_key, column in (("max_risk_history_stop_exclusive", "risk_history_stop_exclusive"),
                    ("max_factor_history_stop_exclusive", "factor_history_stop_exclusive"),
                    ("max_factor_age_days", "factor_age_days")):
                check(name + ":" + stage + ":" + result_key, stats[result_key] == max(int(row[column]) for row in chosen))
        return rows, values, summary

    try:
        check("preimplementation_stage", not implementation.exists() if args.expect_missing else implementation.is_file())
        if implementation.is_file():
            shutil.copyfile(implementation, out / "implementation_used.py")
            frozen_implementation = out / "implementation_used.py"
        else:
            frozen_implementation = implementation
        returns, targets, h = synthetic_arrays()
        definition = {"kind": "deterministic_known_component", "days": DAYS, "stocks": STOCKS,
          "period": 252, "market_amplitude": .002, "residual_amplitudes": (.0006 * np.arange(11, 0, -1)).tolist(),
          "known_beta": "ones", "known_residual_span": "Hadamard columns1 through10",
          "known_remainder": "Hadamard column11", "factor_rank": 10, "factor_shrinkage": .5,
          "svd_threshold": "eps(float64)*max(n_stocks,n_loading_columns)*s_max",
          "wrong_index_discriminator": "predetermined opening exposures vary by earning day",
          "oracle": "Direct known spatial projector, no helper import", "cut": CUT,
          "atol": ATOL, "rtol": RTOL, "market_data": False, "candidate_executions": 0}
        write(out / "fixture_definition.json", definition)
        base = out / "packets/baseline"
        base_ledger = make_packet(root, base, returns, targets, definition)
        expected = oracle(returns, targets, h)
        table(out / "known_components.csv", ["return_index", *COMPONENTS],
              [dict(zip(["return_index", *COMPONENTS], [t, *row])) for t, row in zip(range(253, DAYS - 1), expected)])
        check("fixture_each_component_nonzero", bool(np.all(np.max(np.abs(expected), axis=0) > 1e-7)))
        direct = np.array([row["gross_return"] for row in base_ledger])
        close("fixture_known_component_sum", expected.sum(axis=1), direct)
        wrong = np.einsum("ij,ij->i", targets[1:], returns[253:DAYS-1])
        check("fixture_wrong_target_is_detectable", float(np.max(np.abs(wrong - direct))) > 1e-7,
              float(np.max(np.abs(wrong - direct))))
        if args.expect_missing:
            _, process, summary = launch("missing_implementation", base)
            check("expected_missing_tool_rejection", process.returncode != 0 and summary is None
                  and "No such file" in process.stderr)
            state["status"], exit_code = "EXPECTED_RED_MISSING_IMPLEMENTATION", 0
        else:
            baseline_rows, baseline_values, _ = read_success("baseline", base, DAYS, 10)
            close("baseline_known_components", [[float(row[key]) for key in COMPONENTS] for row in baseline_rows], expected)
            close("baseline_known_market_exposure", [float(row["estimated_market_exposure"]) for row in baseline_rows], targets[:-1].sum(axis=1))
            for key in ("full_cost", "gross_return", "net_return"):
                close("baseline_saved:" + key, [float(row[key]) for row in baseline_rows], [row[key] for row in base_ledger])
            _, repeat_values, _ = read_success("repeat", base, DAYS, 10)
            check("repeat_exact_daily", np.array_equal(repeat_values, baseline_values))
            changed = returns.copy(order="F")
            rng = np.random.default_rng(20261027)
            changed[CUT:] = rng.normal(0.001, .025, changed[CUT:].shape)
            suffix_packet = out / "packets/future_suffix"
            make_packet(root, suffix_packet, changed, targets, {**definition, "mutation_from": CUT, "seed": 20261027})
            suffix_rows, suffix_values, _ = read_success("future_suffix", suffix_packet, DAYS)
            protected = CUT - 253
            check("suffix_exact_protected_rows", np.array_equal(suffix_values[:protected], baseline_values[:protected]))
            close("suffix_boundary_uses_prior_span", [[float(suffix_rows[protected][key]) for key in COMPONENTS]], oracle(changed, targets, h, selected=[CUT]))
            close("suffix_boundary_prior_beta", [float(suffix_rows[protected]["estimated_market_exposure"])], [float(targets[protected].sum())])
            truncated = out / "packets/truncated"
            make_packet(root, truncated, np.asfortranarray(returns[:CUT+1]), targets[:CUT+1-253].copy(), {**definition, "days": CUT+1})
            _, truncated_values, _ = read_success("truncated", truncated, CUT+1, 10)
            check("truncation_exact_protected_rows", np.array_equal(truncated_values, baseline_values[:len(truncated_values)]))
            zeros = out / "packets/zero"
            make_packet(root, zeros, np.zeros_like(returns, order="F"), np.zeros_like(targets), {**definition, "kind": "exact_zero"})
            zero_rows, _, _ = read_success("zero", zeros, DAYS, 0)
            check("zero_exact_economics", all(float(row[key]) == 0 for row in zero_rows for key in (*VALUE_FIELDS, "estimated_market_exposure")))
            tampered = out / "packets/tampered_hash"
            shutil.copytree(base, tampered)
            with (tampered / "inputs/returns.npy").open("r+b") as stream:
                stream.seek(-1, os.SEEK_END)
                original = stream.read(1)
                stream.seek(-1, os.SEEK_END)
                stream.write(bytes([original[0] ^ 1]))
            malformed = out / "packets/malformed_index"
            make_packet(root, malformed, returns, targets, {**definition, "deliberate_corruption": "duplicate_index"}, corrupt="index")
            accounting = out / "packets/wrong_accounting"
            make_packet(root, accounting, returns, targets, {**definition, "deliberate_corruption": "gross_plus_0.001"}, corrupt="accounting")
            for name, packet, digest, before_numeric in (("wrong_manifest_digest", base, "0"*64, True),
                    ("tampered_hash", tampered, None, True), ("malformed_index", malformed, None, False),
                    ("wrong_accounting", accounting, None, False)):
                directory, process, summary = launch(name, packet, digest)
                check(name + ":expected_rejection", process.returncode != 0 and summary is not None
                      and summary["status"] == "EXECUTED_FAIL_OR_INCOMPLETE" and summary["exit_code"] != 0)
                check(name + ":no_model_execution", summary["model_executions"] == 0)
                if before_numeric:
                    check(name + ":rejected_before_numeric_read", summary["numeric_content_read_started"] is False)
                check(name + ":failure_evidence", (directory / "artifact_manifest.json").is_file()
                      and bool(summary.get("error")))
            state["status"], exit_code = "EXECUTED_PASS_SCOPE_ONLY", 0
        check("handoff_unchanged", handoff_before == {name: sha(root / name) for name in handoff_before})
    except Exception:
        state["status"] = "EXECUTED_FAIL_OR_INCOMPLETE"
        state["error"] = traceback.format_exc()
        (out / "controller_stderr.log").write_text(state["error"])
        traceback.print_exc()
    finally:
        state["exit_code"] = exit_code
        state["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write(out / "summary.json", state)
        write(out / "processes.json", state["processes"])
        (out / "controller_stdout.log").write_text("\n".join(logs) + "\n" + state["status"] + "\n")
        if not (out / "controller_stderr.log").exists():
            (out / "controller_stderr.log").write_text("")
        rerun = [sys.executable, str(out / "verifier_used.py"), "--project", str(root), "--out", str(out) + "_rerun"]
        if (out / "implementation_used.py").is_file():
            rerun += ["--implementation", str(out / "implementation_used.py")]
        elif args.expect_missing:
            rerun += ["--expect-missing", "--implementation", str(implementation)]
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        (out / "README.md").write_text("# Frozen attribution synthetic E2E\n\n"
            f"Status: {state['status']}. Candidate executions: 0. Market arrays read: none.\n\n"
            "The controller, implementation when present, plans, synthetic inputs, independent known-component oracle, exact commands, process logs, checks and identities are preserved. Expected rejection cases are not successful attributions. Known components use a Hadamard span, without importing implementation or risk helpers.\n")
        write(out / "artifact_manifest.json", inventory(out))
        print(json.dumps({"status": state["status"], "exit_code": exit_code,
              "checks": len(state["checks"]), "processes": len(state["processes"])}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
