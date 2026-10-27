#!/usr/bin/env python3
"""Attribute saved C09 returns through one fixed, causal factor-risk lens.

This descriptive workflow never executes a forecast or rebalance. Its synthetic
E2E plan and missing-implementation run precede this implementation. Actual
market processing requires a separate root release and --allow-canonical.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import traceback
import types

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for variable in THREADS:
    os.environ[variable] = "1"
sys.dont_write_bytecode = True
import numpy as np

ATOL, RTOL = 1e-12, 1e-10
CONFIG_SHA = "aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba"
CANONICAL_MANIFEST_SHA = "2e1aff5ae8e1257a6abef712b821e4859778dd20f0bb60f2a9903cf0c350d95b"
CANONICAL_METADATA = {
    "input_manifest.json": "df920fd644c6aba72817f9e04170dfcec935f1f25e5694bd717021bc2d38e4f9",
    "source_manifest.json": "8746451b648ff1a917cfc2fa9f3decb4e2e31060298ecf51274af1f1648f41c3",
}
HELPERS = {
    "strategy.py": "104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7",
    "portfolio.py": "fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475",
    "strategy_factor.py": "9e63257c14859430b5190763c5f1fd35320c582019c941ae28b43243587a4959",
    "factor_portfolio.py": "60af66f9797585fec4189206c50481bfd1d3554beb6442ed5c19b2399ce375e5",
}
FACTOR_CONFIG = {"factor_rank": 10, "factor_shrinkage": .5, "factor_refresh_days": 21}
MASKS = {"discovery": [253, 2015], "validation": [2016, 3023], "audit": [3024, 3779]}
COMPONENTS = ("market_component", "residual_factor_component", "remainder_component")
VALUES = (*COMPONENTS, "full_cost", "gross_return", "net_return")
LEDGER_FIELDS = ["return_index", "csv_day_label", "gross_return", "full_cost", "net_return",
                 "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds"]
DAILY_FIELDS = ["return_index", "target_index", "risk_history_stop_exclusive",
    "factor_history_stop_exclusive", "factor_variance_history_stop_exclusive",
    "factor_age_days", "factor_refreshed", "factor_rank", "estimated_market_exposure",
    *VALUES, "gross_reconciliation_error", "net_reconciliation_error",
    "opening_gross_reconciliation_error"]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def packet_file(folder, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Packet paths must be relative and cannot traverse parents")
    path = (folder / relative).resolve()
    if not path.is_relative_to(folder) or not path.is_file():
        raise ValueError("Missing or escaped packet file: " + str(relative))
    return path


def summarize(rows, mask):
    chosen = [row for row in rows if mask[0] <= row["return_index"] < mask[1]]
    result = {
        "rows": len(chosen), "index_slice": mask,
        "annual_arithmetic_mean": dict.fromkeys(VALUES),
        "annual_volatility": dict.fromkeys(VALUES),
        "gross_covariance_contribution": dict.fromkeys(COMPONENTS),
        "estimated_market_exposure": {"mean_abs": None, "max_abs": None},
        "factor_rank": {"min": None, "max": None},
        "max_risk_history_stop_exclusive": None,
        "max_factor_history_stop_exclusive": None,
        "max_factor_age_days": None,
        "max_abs_gross_reconciliation_error": None,
        "max_abs_net_reconciliation_error": None,
        "max_abs_opening_gross_reconciliation_error": None,
        "gross_covariance_contribution_sum": None,
    }
    if not chosen:
        return result
    series = {key: np.array([row[key] for row in chosen]) for key in VALUES}
    result["annual_arithmetic_mean"] = {key: float(252 * value.mean()) for key, value in series.items()}
    result["annual_volatility"] = {key: float(math.sqrt(252) * value.std(ddof=0)) for key, value in series.items()}
    gross_centered = series["gross_return"] - series["gross_return"].mean()
    gross_variance = float(np.mean(gross_centered ** 2))
    if gross_variance > 0:
        result["gross_covariance_contribution"] = {
            key: float(np.mean((series[key] - series[key].mean()) * gross_centered) / gross_variance)
            for key in COMPONENTS}
        result["gross_covariance_contribution_sum"] = sum(result["gross_covariance_contribution"].values())
    exposures = np.abs([row["estimated_market_exposure"] for row in chosen])
    result["estimated_market_exposure"] = {"mean_abs": float(exposures.mean()), "max_abs": float(exposures.max())}
    ranks = [row["factor_rank"] for row in chosen]
    result["factor_rank"] = {"min": min(ranks), "max": max(ranks)}
    for key in ("risk_history_stop_exclusive", "factor_history_stop_exclusive", "factor_age_days"):
        result["max_" + key] = max(row[key] for row in chosen)
    for key in ("gross_reconciliation_error", "net_reconciliation_error", "opening_gross_reconciliation_error"):
        result["max_abs_" + key] = max(abs(row[key]) for row in chosen)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--mode", choices=("synthetic", "real"), required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--packet-manifest-sha256", required=True)
    parser.add_argument("--allow-canonical", action="store_true")
    args = parser.parse_args()
    root, packet, out = args.project.resolve(), args.packet.resolve(), args.out.resolve()
    if out.is_relative_to(packet):
        raise ValueError("Output must be outside the immutable input packet")
    out.mkdir(parents=True, exist_ok=False)
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    state = {
        "status": "RUNNING", "exit_code": 1,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "command": command, "mode": args.mode, "packet": str(packet),
        "numeric_content_read_started": False, "model_executions": 0,
        "checks": [], "consumed_files": {}, "stages": {},
        "completed_rows": 0, "factor_settings": FACTOR_CONFIG,
        "svd_rank_rule": "s > eps(float64) * max(n_stocks, n_loading_columns) * s_max; empty if s_max=0",
        "reconciliation_tolerance": {"atol": ATOL, "rtol": RTOL},
        "variance_convention": "population covariance and variance, ddof=0",
        "interpretation": "Descriptive ex post accounting. The remainder is not identified economic alpha.",
        "factor_cutoff_semantics": "factor_history_stop_exclusive dates cached correlation loadings; current marginal variance uses risk_history_stop_exclusive and can change the final span between refreshes",
        "covariance_contribution_semantics": "Cov(component,gross)/Var(gross); can be negative or exceed one; undefined at zero gross variance",
        "market_component_caveat": "Small estimated market attribution is partly constructional because C09 uses the same prior beta estimator; it is not independent realized-beta evidence",
    }
    rows, consumed = [], {}
    write(out / "summary.json", state)

    def check(name, passed, actual=None):
        item = {"name": name, "status": "PASS" if passed else "FAIL"}
        if actual is not None:
            item["actual"] = actual
        state["checks"].append(item)
        print(json.dumps(item, allow_nan=False), flush=True)
        if not passed:
            raise ValueError(name)

    def authenticate(relative, inventory, expected=None):
        path = packet_file(packet, relative)
        item = inventory.get(relative)
        valid = isinstance(item, dict) and isinstance(item.get("bytes"), int)
        valid = valid and isinstance(item.get("sha256"), str) and len(item["sha256"]) == 64
        check("inventory_entry:" + relative, valid)
        actual = {"sha256": sha(path), "bytes": path.stat().st_size}
        check("identity:" + relative, actual == {"sha256": item["sha256"], "bytes": item["bytes"]})
        if expected is not None:
            check("frozen_identity:" + relative, actual["sha256"] == expected)
        consumed[relative] = {**actual, "path": str(path)}
        return path

    try:
        with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                shutil.copyfile(Path(__file__).resolve(), out / "tool_used.py")
                for source, dest in (("research/FROZEN_ATTRIBUTION_PLAN_20261027.md", "admission.md"),
                                     ("verification/FROZEN_ATTRIBUTION_E2E_PLAN.md", "expectations.md")):
                    shutil.copyfile(root / source, out / dest)
                write(out / "environment.json", {"python": sys.version, "executable": sys.executable,
                    "numpy": np.__version__, "platform": platform.platform(),
                    "threads": {key: os.environ[key] for key in THREADS}})
                check("canonical_release_flag", args.allow_canonical == (args.mode == "real"))
                manifest_path = packet_file(packet, "artifact_manifest.json")
                manifest_sha = sha(manifest_path)
                check("packet_manifest_identity", manifest_sha == args.packet_manifest_sha256)
                if args.mode == "real":
                    check("original_canonical_inventory", manifest_sha == CANONICAL_MANIFEST_SHA)
                consumed["artifact_manifest.json"] = {"path": str(manifest_path), "sha256": manifest_sha,
                                                        "bytes": manifest_path.stat().st_size}
                artifacts = read(manifest_path)
                check("artifact_manifest_mapping", isinstance(artifacts, dict))
                for relative in ("input_manifest.json", "source_manifest.json", "config.json"):
                    expected = CONFIG_SHA if relative == "config.json" else CANONICAL_METADATA.get(relative) if args.mode == "real" else None
                    authenticate(relative, artifacts, expected)
                input_info = read(packet / "input_manifest.json")
                source_info = read(packet / "source_manifest.json")
                config = read(packet / "config.json")
                check("metadata_mappings", all(isinstance(item, dict) for item in (input_info, source_info, config)))
                expected_kind = "canonical_market" if args.mode == "real" else "synthetic_frozen_attribution"
                check("input_scope_kind", input_info.get("kind") == expected_kind)
                return_info = input_info.get("files", {}).get("returns.npy", {})
                shape = return_info.get("shape")
                check("declared_return_shape", isinstance(shape, list) and len(shape) == 2 and
                      all(type(value) is int for value in shape) and shape[0] >= 255 and shape[1] > 0)
                days, stocks = shape
                check("declared_input_slice", input_info.get("input_slice") == [0, days])
                if args.mode == "real":
                    check("canonical_dimensions", shape == [3780, 1000])
                check("frozen_risk_configuration", config.get("candidate_id") == "C09_additive_long_memory"
                      and config.get("risk_window") == 252 and config.get("risk_min_days") == 20
                      and source_info.get("config.json") == CONFIG_SHA)
                for name, expected in HELPERS.items():
                    relative = "source/candidate/" + name
                    authenticate(relative, artifacts, expected)
                    check("source_manifest_agrees:" + name, source_info.get(relative) == expected)
                authenticate("inputs/returns.npy", artifacts)
                authenticate("targets.npy", artifacts)
                authenticate("daily.csv", artifacts)
                check("return_manifest_agrees", return_info.get("sha256") == consumed["inputs/returns.npy"]["sha256"]
                      and return_info.get("dtype") == "float64")

                # Only authenticated helper bytes are imported. The package is
                # private to this process and cannot affect the handoff state.
                helpers = out / "helpers"
                helpers.mkdir()
                for name in HELPERS:
                    shutil.copyfile(packet / "source/candidate" / name, helpers / name)
                    check("copied_helper_identity:" + name, sha(helpers / name) == HELPERS[name])
                package_name = "_frozen_attribution_helpers"
                package = types.ModuleType(package_name)
                package.__path__ = [str(helpers)]
                sys.modules[package_name] = package
                factor = importlib.import_module(package_name + ".strategy_factor")

                def forbidden_model_call(*_args, **_kwargs):
                    state["model_executions"] += 1
                    raise RuntimeError("Attribution may not call forecast or rebalance")

                for module in (factor, factor.base):
                    module.forecast = forbidden_model_call
                    module.rebalance = forbidden_model_call
                factor.configure({**config, **FACTOR_CONFIG})
                shutil.copyfile(packet / "input_manifest.json", out / "input_manifest.json")
                shutil.copyfile(packet / "source_manifest.json", out / "source_manifest.json")
                shutil.copyfile(packet / "config.json", out / "config.json")
                shutil.copyfile(manifest_path, out / "packet_artifact_manifest.json")

                # Every consumed data/source identity was checked above. No
                # characteristics, forecasts, or cost arrays are needed.
                state["numeric_content_read_started"] = True
                returns = np.load(packet / "inputs/returns.npy", mmap_mode="r", allow_pickle=False)
                targets = np.load(packet / "targets.npy", mmap_mode="r", allow_pickle=False)
                check("return_shape_and_type", returns.shape == tuple(shape) and returns.dtype == np.float64)
                check("target_shape_and_type", targets.shape == (days - 253, stocks) and targets.dtype == np.float64)
                check("finite_inputs", bool(np.isfinite(returns).all() and np.isfinite(targets).all()))
                with (packet / "daily.csv").open(newline="") as stream:
                    reader = csv.DictReader(stream)
                    check("canonical_ledger_schema", reader.fieldnames == LEDGER_FIELDS)
                    ledger = list(reader)
                check("complete_scored_row_count", len(ledger) == days - 254)
                for t, record in enumerate(ledger, 253):
                    check_index = int(record["return_index"]) == t and int(record["csv_day_label"]) == t + 1
                    if not check_index:
                        raise ValueError("Saved ledger has malformed chronological indices at expected row " + str(t))
                    for key in LEDGER_FIELDS[2:]:
                        record[key] = float(record[key])
                    if not all(math.isfinite(record[key]) for key in LEDGER_FIELDS[2:]):
                        raise ValueError("Nonfinite saved ledger value at row " + str(t))
                    if record["full_cost"] < 0:
                        raise ValueError("Negative full trading cost at row " + str(t))
                check("chronological_finite_ledger", True)

                cached_epoch = None
                correlation_loadings = None
                factor_stop = None
                with np.errstate(over="raise", invalid="raise", divide="raise"):
                    for t, record in enumerate(ledger, 253):
                        weights = targets[t - 253]
                        realized = returns[t]
                        opening_gross = float(weights @ realized)
                        market = float(realized.mean())
                        for name, actual, expected in (
                                ("opening_gross", opening_gross, record["gross_return"]),
                                ("saved_net", record["gross_return"] - record["full_cost"], record["net_return"]),
                                ("saved_market", market, record["raw_market_return"])):
                            if not np.isclose(actual, expected, atol=ATOL, rtol=RTOL):
                                raise ValueError(f"{name} reconciliation failed at return row {t}: {actual - expected:.17g}")
                        beta, variance = factor.estimate_risk(returns[:t])
                        epoch = max(0, (t - 253) // 21)
                        refreshed = cached_epoch != epoch
                        if refreshed:
                            correlation_loadings = factor._correlation_factors(returns[:t], beta)
                            factor_stop, cached_epoch = t, epoch
                        loadings = np.sqrt(variance)[:, None] * correlation_loadings
                        if loadings.shape[1]:
                            vectors, singular, _ = np.linalg.svd(loadings, full_matrices=False)
                            threshold = np.finfo(np.float64).eps * max(loadings.shape) * singular[0]
                            q = vectors[:, singular > threshold]
                        else:
                            q = np.empty((stocks, 0), dtype=np.float64)
                        residual = realized - beta * market
                        projected = q @ (q.T @ residual)
                        exposure = float(weights @ beta)
                        market_component = exposure * market
                        residual_factor_component = float(weights @ projected)
                        remainder_component = float(weights @ (residual - projected))
                        attributed = market_component + residual_factor_component + remainder_component
                        net = attributed - record["full_cost"]
                        if not np.isclose(attributed, record["gross_return"], atol=ATOL, rtol=RTOL):
                            raise ValueError("Component gross reconciliation failed at row " + str(t))
                        if not np.isclose(net, record["net_return"], atol=ATOL, rtol=RTOL):
                            raise ValueError("Component net reconciliation failed at row " + str(t))
                        rows.append({"return_index": t, "target_index": t - 253,
                            "risk_history_stop_exclusive": t,
                            "factor_history_stop_exclusive": factor_stop,
                            "factor_variance_history_stop_exclusive": t,
                            "factor_age_days": t - factor_stop, "factor_refreshed": int(refreshed),
                            "factor_rank": int(q.shape[1]), "estimated_market_exposure": exposure,
                            "market_component": market_component,
                            "residual_factor_component": residual_factor_component,
                            "remainder_component": remainder_component,
                            "full_cost": record["full_cost"], "gross_return": record["gross_return"],
                            "net_return": record["net_return"],
                            "gross_reconciliation_error": attributed - record["gross_return"],
                            "net_reconciliation_error": net - record["net_return"],
                            "opening_gross_reconciliation_error": opening_gross - record["gross_return"]})
                        if len(rows) % 250 == 0:
                            print(json.dumps({"completed_rows": len(rows), "last_return_index": t}), flush=True)
                    state["stages"] = {name: summarize(rows, mask) for name, mask in MASKS.items()}
                check("complete_attribution", len(rows) == days - 254)
                check("all_daily_outputs_finite", all(math.isfinite(row[key]) for row in rows for key in DAILY_FIELDS))
                for name, stats in state["stages"].items():
                    total = stats["gross_covariance_contribution_sum"]
                    if total is not None:
                        check("covariance_additivity:" + name, bool(np.isclose(total, 1.0, atol=ATOL, rtol=RTOL)), total)
                check("no_forecast_or_rebalance", state["model_executions"] == 0)
                check("consumed_inputs_unchanged", all(sha(item["path"]) == item["sha256"] for item in consumed.values()))
                check("private_helpers_unchanged", all(sha(helpers / name) == expected for name, expected in HELPERS.items()))
                state["status"], state["exit_code"] = "EXECUTED_PASS_SCOPE_ONLY", 0
    except Exception:
        state["status"], state["exit_code"] = "EXECUTED_FAIL_OR_INCOMPLETE", 1
        state["error"] = traceback.format_exc()
        with (out / "stderr.log").open("a") as stream:
            stream.write(state["error"])
    finally:
        state["completed_rows"] = len(rows)
        state["consumed_files"] = consumed
        state["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if rows:
            with (out / "daily_attribution.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=DAILY_FIELDS)
                writer.writeheader()
                writer.writerows(rows)
        write(out / "summary.json", state)
        write(out / "consumed_manifest.json", consumed)
        rerun = [sys.executable, str(out / "tool_used.py"), "--project", str(root),
                 "--packet", str(packet), "--mode", args.mode, "--packet-manifest-sha256",
                 args.packet_manifest_sha256, "--out", str(out) + "_rerun"]
        if args.allow_canonical:
            rerun.append("--allow-canonical")
        (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
        (out / "setup.md").write_text("# Frozen-policy descriptive attribution\n\n"
            + command + "\n\nStatus: " + state["status"] + ".\n\n"
            "Input numeric files remain in the immutable identified packet. All consumed identities, helper snapshots, plans, logs and commands are recorded. Full original fees remain a separate subtraction; component returns are not independent trading strategies. The remainder is not identified economic alpha.\n\n"
            "Factor age refers to cached correlation loadings. The loading span is rescaled by current prior-estimated marginal variances each day.\n")
        write(out / "artifact_manifest.json", {
            str(path.relative_to(out)): {"sha256": sha(path), "bytes": path.stat().st_size}
            for path in sorted(out.rglob("*")) if path.is_file() and path != out / "artifact_manifest.json"})
        print(json.dumps({"status": state["status"], "exit_code": state["exit_code"],
                          "rows": len(rows), "model_executions": state["model_executions"]}))
    return state["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
