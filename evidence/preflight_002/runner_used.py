#!/usr/bin/env python3
"""Structural census + supplied-example E2E; see PREFLIGHT_PLAN.md first.

No strategy is implemented here, and no predictive model is fitted.
Only rows [0,504) are used to calculate market/portfolio outcomes.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import time
import traceback
import zlib
from datetime import datetime, timezone
from zipfile import ZipFile

sys.dont_write_bytecode = True


THREAD_VARIABLES = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS",
)
for variable in THREAD_VARIABLES:
    os.environ[variable] = "1"

# Restrict the process before importing numerical libraries. Unsupported affinity
# is recorded as a limitation, never silently claimed as one-core verification.
affinity_error = None
try:
    available_cpus = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {available_cpus[0]})
except (AttributeError, OSError) as exc:
    affinity_error = repr(exc)

import numpy as np
import pandas as pd


FEATURES = ["Woe", "Malice", "Dread", "Frolic", "Up", "Down", "Charm",
            "Strange", "Top", "Bottom", "Snap", "Crackle", "Pop"]
PREFIX_DAYS = 504


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--plan", type=Path, default=Path(__file__).resolve().parents[1] / "PREFLIGHT_PLAN.md")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    archive = args.archive.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "inputs").mkdir()
    run_command = shlex.join([sys.executable, str(Path(__file__).resolve()),
                             "--source", str(source), "--archive", str(archive),
                             "--plan", str(args.plan.resolve()), "--out", str(out)])
    rerun_command = shlex.join([sys.executable, str(out / "runner_used.py"),
                               "--source", str(source), "--archive", str(archive),
                               "--plan", str(out / "expectations.md"), "--out", str(out) + "_rerun"])
    summary = {
        "scope": "Input hygiene and original equal-weight E2E on first504 rows only",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "run_command": run_command, "rerun_command": rerun_command,
        "source": str(source), "checks": [], "status": "RUNNING",
        "outcome_data_access": {"start_inclusive": 0, "end_exclusive": PREFIX_DAYS},
        "unverified": ["candidate strategy", "alpha", "future beta", "causality of a candidate",
                       "long-horizon runtime", "all evaluator dependencies", "remote CSV byte identity"],
    }
    (out / "rerun.txt").write_text(rerun_command + "\n")
    (out / "expectations.md").write_bytes(args.plan.read_bytes())
    (out / "runner_used.py").write_bytes(Path(__file__).read_bytes())
    log = []

    def record(name: str, condition: bool, actual):
        entry = {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual}
        summary["checks"].append(entry)
        message = json.dumps(entry, ensure_ascii=False)
        log.append(message)
        print(message, flush=True)
        if not condition:
            raise AssertionError(name)

    try:
        env = {"python": sys.version, "platform": platform.platform(),
               "thread_variables": {name: os.environ[name] for name in THREAD_VARIABLES},
               "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
               "cpu_affinity_error": affinity_error, "packages": {}}
        for name in ["numpy", "pandas", "scipy", "scikit-learn", "cvxpy", "lightgbm"]:
            try:
                env["packages"][name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                env["packages"][name] = "NOT_INSTALLED"
        (out / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
        with ZipFile(archive) as original:
            entries = sorted((entry for entry in original.infolist() if not entry.is_dir()), key=lambda entry: entry.filename)
        manifest = []
        for entry in entries:
            relative = Path(entry.filename).relative_to("Quant Research Take-Home")
            path = source / relative
            digest = hashlib.sha256()
            crc = 0
            with path.open("rb") as raw:
                for chunk in iter(lambda: raw.read(1 << 20), b""):
                    digest.update(chunk)
                    crc = zlib.crc32(chunk, crc)
            manifest.append({"path": str(relative), "bytes": path.stat().st_size,
                             "sha256": digest.hexdigest(), "archive_bytes": entry.file_size,
                             "archive_crc_matches": crc == entry.CRC})
        (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        summary["archive"] = {"path": str(archive), "bytes": archive.stat().st_size, "sha256": sha256(archive)}
        record("source_file_count", len(entries) == 12, len(entries))
        record("archive_content_integrity", all(f["archive_crc_matches"] and f["bytes"] == f["archive_bytes"] for f in manifest),
               {"matched_members": sum(f["archive_crc_matches"] and f["bytes"] == f["archive_bytes"] for f in manifest)})
        (out / "runner_sha256.txt").write_text(sha256(Path(__file__)) + "\n")

        returns = pd.read_csv(source / "returns.csv", index_col="day")
        costs = pd.read_csv(source / "costs.csv", index_col="stock")
        record("returns_shape", returns.shape == (3780, 1000), list(returns.shape))
        day_ids = returns.index.to_numpy()
        stocks = returns.columns.to_numpy()
        record("returns_day_keys", np.array_equal(day_ids, np.arange(1, 3781)),
               {"first": int(day_ids[0]), "last": int(day_ids[-1]), "unique": bool(returns.index.is_unique)})
        record("returns_stock_keys_unique", returns.columns.is_unique, len(stocks))
        record("returns_finite", np.isfinite(returns.to_numpy()).all(),
               {"nonfinite_count": int((~np.isfinite(returns.to_numpy())).sum())})
        record("cost_shape", costs.shape == (1000, 1) and list(costs.columns) == ["cost"], list(costs.shape))
        record("cost_stock_order", np.array_equal(costs.index.to_numpy(), stocks),
               {"exact_order_match": bool(np.array_equal(costs.index.to_numpy(), stocks))})
        c = costs["cost"].to_numpy()
        record("costs_valid", np.isfinite(c).all() and (c >= 0).all(),
               {"nonfinite_count": int((~np.isfinite(c)).sum()), "negative_count": int((c < 0).sum())})

        offset = 0
        nonfinite = 0
        keys_correct = True
        prefix_chunks = []
        expected_columns = ["day", "stock"] + FEATURES
        for chunk in pd.read_csv(source / "characteristics.csv", chunksize=100000):
            if list(chunk.columns) != expected_columns:
                raise AssertionError("characteristics feature schema/order differs from brief")
            indices = np.arange(offset, offset + len(chunk))
            if indices[-1] >= len(day_ids) * len(stocks):
                raise AssertionError("characteristics has excess rows")
            keys_correct &= bool(np.array_equal(chunk["day"].to_numpy(), day_ids[indices // len(stocks)]))
            keys_correct &= bool(np.array_equal(chunk["stock"].to_numpy(), stocks[indices % len(stocks)]))
            nonfinite += int((~np.isfinite(chunk[FEATURES].to_numpy())).sum())
            remaining = PREFIX_DAYS * len(stocks) - offset
            if remaining > 0:
                prefix_chunks.append(chunk.iloc[:min(remaining, len(chunk))].copy())
            offset += len(chunk)
        record("characteristics_shape", offset == 3780000, {"rows": offset, "features": len(FEATURES)})
        record("characteristics_order", keys_correct, {"exact_day_stock_grid_match": keys_correct})
        record("characteristics_finite", nonfinite == 0, {"nonfinite_count": nonfinite})
        record("one_core_affinity", env["cpu_affinity"] is not None and len(env["cpu_affinity"]) == 1,
               {"affinity": env["cpu_affinity"], "error": affinity_error})

        # A real CSV prefix is loaded by the supplied loader: the complete
        # CSV -> load -> replay -> report path, with later outcomes never used.
        returns.iloc[:PREFIX_DAYS].to_csv(out / "inputs" / "returns.csv", float_format="%.6f")
        pd.concat(prefix_chunks, ignore_index=True).to_csv(out / "inputs" / "characteristics.csv", index=False, float_format="%.3f")
        costs.to_csv(out / "inputs" / "costs.csv", float_format="%.8f")
        prefix_manifest = [{"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                           for path in sorted((out / "inputs").iterdir())]
        (out / "input_manifest.json").write_text(json.dumps(prefix_manifest, indent=2) + "\n")
        scorer = module_from_path("supplied_score", source / "score.py")
        example = module_from_path("supplied_equal_weight", source / "example_equal_weight.py")
        r, x, tc = scorer.load(str(out / "inputs"))
        record("prefix_load_shape", r.shape == (504, 1000) and x.shape == (504, 1000, 13) and tc.shape == (1000,),
               {"returns": list(r.shape), "characteristics": list(x.shape), "costs": list(tc.shape)})
        record("prefix_returns_equal", np.array_equal(r, returns.iloc[:PREFIX_DAYS].to_numpy()),
               {"exact_numeric_match": bool(np.array_equal(r, returns.iloc[:PREFIX_DAYS].to_numpy()))})
        record("prefix_costs_equal", np.array_equal(tc, c), {"exact_numeric_match": bool(np.array_equal(tc, c))})
        xp = pd.concat(prefix_chunks, ignore_index=True)[FEATURES].to_numpy().reshape(504, 1000, 13)
        record("prefix_characteristics_equal", np.array_equal(x, xp),
               {"exact_numeric_match": bool(np.array_equal(x, xp))})
        tic = time.perf_counter()
        rows, forecast_seconds = scorer.run(example, r, x, tc)
        elapsed = time.perf_counter() - tic
        repeated_rows, repeated_forecast_seconds = scorer.run(example, r, x, tc)
        record("scored_row_count", rows.shape == (250, 5), list(rows.shape))
        record("finite_scoring_outputs", np.isfinite(rows).all(), {"nonfinite": int((~np.isfinite(rows)).sum())})
        record("nonnegative_costs", (rows[:, 1] >= 0).all(), {"negative_cost_count": int((rows[:, 1] < 0).sum())})
        record("equal_weight_gross", np.allclose(rows[:, 2], 1, rtol=0, atol=1e-12),
               {"maximum_abs_error": float(np.max(np.abs(rows[:, 2] - 1)))})
        record("repeat_economic_outputs", np.array_equal(rows[:, :4], repeated_rows[:, :4]),
               {"max_abs_difference": float(np.max(np.abs(rows[:, :4] - repeated_rows[:, :4])))})
        net = rows[:, 0] - rows[:, 1]
        record("nonzero_net_dispersion", net.std() > 0, float(net.std()))
        market = rows[:, 3] - rows[:, 3].mean()
        beta = float(market @ (net - net.mean()) / (market @ market))
        record("equal_weight_beta_expected", abs(beta - 1) < 0.02, beta)
        columns = ["gross_return", "closing_trade_cost", "post_trade_gross_exposure", "market_return", "rebalance_seconds"]
        table = pd.DataFrame(rows, columns=columns)
        table.insert(0, "array_row", np.arange(253, 503))
        table.insert(1, "csv_day", np.arange(254, 504))
        table["net_return"] = net
        table.to_csv(out / "scored_rows.csv", index=False, float_format="%.17g")
        repeated = pd.DataFrame(repeated_rows, columns=columns)
        repeated.insert(0, "array_row", np.arange(253, 503))
        repeated.to_csv(out / "scored_rows_repeat.csv", index=False, float_format="%.17g")
        with contextlib.redirect_stdout(io.StringIO()) as capture:
            scorer.report("supplied_equal_weight_prefix", rows, forecast_seconds, len(r))
        report = capture.getvalue()
        (out / "scorer_report.txt").write_text(report)
        log.append(report)
        summary["smoke_metrics"] = {
            "sharpe": float(np.sqrt(252) * net.mean() / net.std()), "net_beta": beta,
            "mean_rebalance_ms": float(rows[:, 4].mean() * 1000),
            "max_rebalance_ms": float(rows[:, 4].max() * 1000),
            "forecast_seconds": float(forecast_seconds), "run_seconds": elapsed,
            "assignment_beta_status": "FAIL_BY_DESIGN: equal-weight is a plumbing example",
            "candidate_validation_status": "NOT_RUN",
        }
        summary["status"] = "PASS_SCOPE_ONLY"
        print(report, flush=True)
        return_code = 0
    except Exception:
        summary["status"] = "FAIL"
        summary["exception"] = traceback.format_exc()
        log.append(summary["exception"])
        print(summary["exception"], file=sys.stderr, flush=True)
        return_code = 1
    finally:
        summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
        summary["exit_code"] = return_code
        (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        (out / "run.log").write_text("\n".join(log) + "\n")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
