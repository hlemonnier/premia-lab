#!/usr/bin/env python3
"""Discovery-only descriptive diagnostics; see ALPHA_DIAGNOSTICS_PLAN.md.

This is not a strategy, a portfolio backtest, or a candidate Sharpe evaluation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone

for _name in (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS",
):
    os.environ[_name] = "1"

import numpy as np
import pandas as pd
import scipy
from scipy.stats import rankdata

FEATURES = ["Woe", "Malice", "Dread", "Frolic", "Up", "Down", "Charm",
            "Strange", "Top", "Bottom", "Snap", "Crackle", "Pop"]
HORIZONS = (1, 5, 20)
PERIODS = [("pooled", 0, 2016)] + [
    (f"block_{b + 1}", b * 504, (b + 1) * 504) for b in range(4)
]
EXPECTED_COUNTS = {1: [251, 504, 504, 504],
                   5: [247, 500, 500, 500],
                   20: [232, 485, 485, 485]}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean_json(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(path: Path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(clean_json(value), indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


class Tee:
    def __init__(self, original, logfile):
        self.original = original
        self.logfile = logfile

    def write(self, message):
        self.original.write(message)
        self.logfile.write(message)
        self.logfile.flush()

    def flush(self):
        self.original.flush()
        self.logfile.flush()


def row_corr(a, b):
    ac = np.asarray(a, dtype=float) - np.mean(a, axis=1, keepdims=True)
    bc = np.asarray(b, dtype=float) - np.mean(b, axis=1, keepdims=True)
    denominator = np.sqrt(np.einsum("ij,ij->i", ac, ac) *
                          np.einsum("ij,ij->i", bc, bc))
    result = np.full(len(a), np.nan)
    valid = np.isfinite(denominator) & (denominator > 0)
    result[valid] = np.einsum("ij,ij->i", ac[valid], bc[valid]) / denominator[valid]
    return result


def mean_or_nan(values):
    finite = np.asarray(values)[np.isfinite(values)]
    return float(finite.mean()) if len(finite) else np.nan


def daily_stats(values, dates):
    values = np.asarray(values)
    dates = np.asarray(dates)
    valid = np.isfinite(values)
    v, d = values[valid], dates[valid]
    if not len(v):
        return {"n": 0, "mean": np.nan, "median": np.nan, "daily_std": np.nan,
                "positive_fraction": np.nan, "quarter_n": 0,
                "quarter_mean_min": np.nan, "quarter_mean_max": np.nan,
                "quarter_mean_std": np.nan}
    quarter_means = np.array([v[d // 63 == q].mean() for q in np.unique(d // 63)])
    return {
        "n": len(v), "mean": v.mean(), "median": np.median(v),
        "daily_std": v.std(ddof=0), "positive_fraction": np.mean(v > 0),
        "quarter_n": len(quarter_means), "quarter_mean_min": quarter_means.min(),
        "quarter_mean_max": quarter_means.max(),
        "quarter_mean_std": quarter_means.std(ddof=1) if len(quarter_means) > 1 else np.nan,
    }


def quantile_bins(ranks):
    # Average ranks are half-integers and exactly represented by float32 here.
    return np.minimum(9, np.floor((ranks - 0.5) * 10 / 1000).astype(np.int8))


def write_csv(path: Path, rows):
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.17g")


def main(args):
    root = Path(args.project_root).resolve()
    out = Path(args.output).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Evidence directory must be new or empty: {out}")
    out.mkdir(parents=True, exist_ok=True)
    sys.stdout = Tee(sys.stdout, (out / "stdout.log").open("w"))
    sys.stderr = Tee(sys.stderr, (out / "stderr.log").open("w"))
    started = time.perf_counter()
    checks = []
    summary = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
               "scope": "Discovery-only descriptive diagnostics, no portfolio scoring",
               "actual_data_slice": [0, 2016], "pipeline_configuration_slots_used": 0}
    write_json(out / "summary.json", summary)

    def check(name, passed, expected, actual):
        record = {"name": name, "status": "PASS" if passed else "FAIL",
                  "expected": expected, "actual": actual}
        checks.append(record)
        write_json(out / "checks.json", checks)
        if not passed:
            raise AssertionError(f"{name}: expected {expected!r}; got {actual!r}")

    try:
        plan = root / "research" / "ALPHA_DIAGNOSTICS_PLAN.md"
        protocol_path = root / "RESEARCH_PROTOCOL.json"
        cache = root / "cache" / "discovery"
        source_files = [cache / name for name in (
            "returns.npy", "characteristics.npy", "costs.npy", "metadata.json")]
        protocol = json.loads(protocol_path.read_text())
        metadata = json.loads((cache / "metadata.json").read_text())
        shutil.copyfile(plan, out / "expectations.md")
        shutil.copyfile(protocol_path, out / "protocol_used.json")
        shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
        command = shlex.join([sys.executable, *sys.argv])
        (out / "command.txt").write_text(command + "\n")
        rerun = ("#!/usr/bin/env bash\nset -euo pipefail\n"
                 "diagnostic_rerun_dir=\"${1:-$(mktemp -d /tmp/continual-alpha-rerun-XXXXXX)}\"\n" +
                 shlex.join([sys.executable, str(out / "runner_used.py"), "--project-root", str(root)]) +
                 ' --output "$diagnostic_rerun_dir"\n')
        (out / "rerun.sh").write_text(rerun)
        os.chmod(out / "rerun.sh", 0o755)
        input_hashes = {str(p): sha256(p) for p in source_files}
        write_json(out / "inputs.json", {"files": input_hashes, "metadata": metadata,
                   "plan_sha256": sha256(plan), "protocol_sha256": sha256(protocol_path),
                   "code_sha256": sha256(Path(__file__).resolve())})
        affinity = None
        if hasattr(os, "sched_getaffinity"):
            allowed = sorted(os.sched_getaffinity(0))
            if allowed:
                os.sched_setaffinity(0, {allowed[0]})
            affinity = sorted(os.sched_getaffinity(0))
        write_json(out / "environment.json", {
            "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": scipy.__version__, "platform": platform.platform(),
            "processor": platform.processor(), "cpu_affinity": affinity,
            "threads": {k: os.environ[k] for k in os.environ if k.endswith("NUM_THREADS")
                        or k == "VECLIB_MAXIMUM_THREADS"},
        })
        check("cache_prefix", metadata.get("input_slice") == [0, 2016],
              [0, 2016], metadata.get("input_slice"))
        check("feature_order", metadata.get("features") == FEATURES,
              FEATURES, metadata.get("features"))
        check("protocol_permission", protocol["data_access"]["pre_freeze_research"] == [0, 2016],
              [0, 2016], protocol["data_access"]["pre_freeze_research"])
        for name, digest in metadata["cache_sha256"].items():
            check("cache_hash_" + name, input_hashes[str(cache / name)] == digest,
                  digest, input_hashes[str(cache / name)])
        returns = np.load(cache / "returns.npy", mmap_mode="r")
        chars = np.load(cache / "characteristics.npy", mmap_mode="r")
        costs = np.load(cache / "costs.npy", mmap_mode="r")
        for name, array, shape in (("returns", returns, (2016, 1000)),
                                   ("characteristics", chars, (2016, 1000, 13)),
                                   ("costs", costs, (1000,))):
            check(name + "_shape", array.shape == shape, shape, array.shape)
            check(name + "_finite", bool(np.isfinite(array).all()), True,
                  bool(np.isfinite(array).all()))
        check("cost_nonnegative", bool(np.all(costs >= 0)), True, bool(np.all(costs >= 0)))

        config = {"features": FEATURES, "horizons": HORIZONS,
                  "periods": PERIODS, "first_feature_index": 252,
                  "target": "forward arithmetic daily-average return",
                  "beta": "centered trailing252 days through feature date, unshrunk",
                  "expected_origins_per_block": EXPECTED_COUNTS,
                  "quantiles": 10, "tie_method": "average ranks",
                  "contrasts": ["top_minus_bottom", "(Q1+Q10-Q5-Q6)/2"],
                  "temporal_summary_block": 63}
        write_json(out / "config.json", config)
        print("Inputs verified; actual rows 0:2016 only.", flush=True)

        exposures = []
        for feature in FEATURES:
            exposures.append({"id": f"behavior:{feature}", "kind": "behavior/cost association",
                              "feature": feature, "periods": "pooled and four fixed blocks"})
            for lag in HORIZONS:
                exposures.append({"id": f"persistence:{feature}:{lag}",
                                  "kind": "raw/rank/decile persistence", "feature": feature,
                                  "lag": lag})
            for horizon in HORIZONS:
                for target in ("raw", "market_controlled"):
                    exposures.append({"id": f"prediction:{feature}:{horizon}:{target}",
                                      "kind": "Pearson/rank/linear/decile/curvature diagnostic",
                                      "feature": feature, "horizon": horizon, "target": target})
        exposures.append({"id": "redundancy:all13", "kind": "all-pair daily raw/rank correlations",
                          "feature_pairs_including_diagonal": 91})
        write_json(out / "diagnostic_exposures.json", {
            "exposures": exposures, "pipeline_configuration_slots_used": 0,
            "note": "All descriptive choices are research exposures; none is a scored portfolio."})

        feature_rows, persistence_rows = [], []
        ranks_all = np.empty(chars.shape, dtype=np.float32)
        for j, feature in enumerate(FEATURES):
            x = np.array(chars[:, :, j], dtype=float)
            ranks = rankdata(x, axis=1, method="average")
            ranks_all[:, :, j] = ranks
            bins = quantile_bins(ranks)
            cost_corr = row_corr(x, np.broadcast_to(costs, x.shape))
            for period, lo, hi in PERIODS:
                v = x[lo:hi]
                quantiles = np.quantile(v, [0, .01, .1, .5, .9, .99, 1])
                cross_std = v.std(axis=1)
                pooled_var = v.var()
                feature_rows.append({
                    "feature": feature, "period": period, "rows": hi - lo,
                    **{label: value for label, value in zip(
                        ("min", "q01", "q10", "median", "q90", "q99", "max"), quantiles)},
                    "mean_daily_xs_mean": v.mean(axis=1).mean(),
                    "std_daily_xs_mean": v.mean(axis=1).std(),
                    "median_daily_xs_std": np.median(cross_std),
                    "constant_xs_fraction": np.mean(cross_std == 0),
                    "common_time_mean_variance_fraction": v.mean(axis=1).var() / pooled_var if pooled_var else np.nan,
                    "persistent_stock_mean_variance_fraction": v.mean(axis=0).var() / pooled_var if pooled_var else np.nan,
                    "mean_cost_correlation": mean_or_nan(cost_corr[lo:hi]),
                })
                for lag in HORIZONS:
                    a, b = x[lo + lag:hi], x[lo:hi - lag]
                    ra, rb = ranks[lo + lag:hi], ranks[lo:hi - lag]
                    ca, cb = bins[lo + lag:hi], bins[lo:hi - lag]
                    retention = {}
                    for q, label in ((0, "bottom"), (9, "top")):
                        previous_count = (cb == q).sum(axis=1)
                        overlap = ((ca == q) & (cb == q)).sum(axis=1)
                        ratio = np.full(len(previous_count), np.nan)
                        good = previous_count > 0
                        ratio[good] = overlap[good] / previous_count[good]
                        retention[label + "_retention"] = mean_or_nan(ratio)
                    persistence_rows.append({
                        "feature": feature, "period": period, "lag": lag,
                        "n_pairs": len(a), "pearson_mean": mean_or_nan(row_corr(a, b)),
                        "spearman_mean": mean_or_nan(row_corr(ra, rb)), **retention,
                    })
            last = next(r for r in persistence_rows if r["feature"] == feature
                        and r["period"] == "pooled" and r["lag"] == 1)
            print(f"Behavior {feature:8s}: lag1 rank persistence={last['spearman_mean']:.4f}, "
                  f"top retention={last['top_retention']:.3f}", flush=True)
        write_csv(out / "characteristic_summary.csv", feature_rows)
        write_csv(out / "persistence.csv", persistence_rows)

        # Past-only beta for labels: each date s includes observations s-251,...,s.
        r = np.asarray(returns, dtype=float)
        market = r.mean(axis=1)
        prefix_r = np.vstack([np.zeros((1, 1000)), np.cumsum(r, axis=0)])
        prefix_rm = np.vstack([np.zeros((1, 1000)), np.cumsum(r * market[:, None], axis=0)])
        prefix_m = np.r_[0., np.cumsum(market)]
        prefix_mm = np.r_[0., np.cumsum(market * market)]
        s_beta = np.arange(252, 2016)
        lo, hi = s_beta - 251, s_beta + 1
        sum_m = prefix_m[hi] - prefix_m[lo]
        denominator = prefix_mm[hi] - prefix_mm[lo] - sum_m ** 2 / 252
        beta = np.full((2016, 1000), np.nan)
        valid_beta = denominator > 0
        numerator = ((prefix_rm[hi] - prefix_rm[lo]) -
                     (prefix_r[hi] - prefix_r[lo]) * (sum_m / 252)[:, None])
        beta[s_beta[valid_beta]] = numerator[valid_beta] / denominator[valid_beta, None]
        write_json(out / "beta_control_coverage.json", {
            "first_feature_index": 252, "window": 252,
            "available_feature_dates": int(valid_beta.sum()),
            "unavailable_feature_dates": int((~valid_beta).sum()),
            "reason_if_unavailable": "nonpositive trailing market variance",
            "restriction": "This beta is a diagnostic label control, not a portfolio."})

        summary_rows, quantile_rows = [], []
        daily_count = 0
        max_reconstruction_error = 0.
        undefined = {"pearson": 0, "spearman": 0, "empty_buckets": 0}
        for horizon in HORIZONS:
            origins, blocks = [], []
            for b in range(4):
                first_label = max(253, b * 504)
                last_label = (b + 1) * 504 - horizon
                starts = np.arange(first_label, last_label + 1)
                check(f"origin_count_h{horizon}_b{b + 1}", len(starts) == EXPECTED_COUNTS[horizon][b],
                      EXPECTED_COUNTS[horizon][b], len(starts))
                origins.extend(starts - 1)
                blocks.extend([b + 1] * len(starts))
            origins = np.asarray(origins, dtype=int)
            blocks = np.asarray(blocks, dtype=int)
            first_labels, final_labels = origins + 1, origins + horizon
            check(f"chronology_h{horizon}", bool(np.all(origins < first_labels)), True,
                  bool(np.all(origins < first_labels)))
            check(f"maturity_h{horizon}", bool(np.all(final_labels < blocks * 504)), True,
                  bool(np.all(final_labels < blocks * 504)))
            raw = (prefix_r[origins + horizon + 1] - prefix_r[origins + 1]) / horizon
            forward_market = (prefix_m[origins + horizon + 1] - prefix_m[origins + 1]) / horizon
            controlled = raw - beta[origins] * forward_market[:, None]
            horizon_rows = []
            for target_name, y in (("raw", raw), ("market_controlled", controlled)):
                yranks = rankdata(y, axis=1, method="average", nan_policy="propagate")
                ystd = np.std(y, axis=1)
                for j, feature in enumerate(FEATURES):
                    x = np.asarray(chars[origins, :, j], dtype=float)
                    xranks = ranks_all[origins, :, j]
                    bins = quantile_bins(xranks)
                    pearson = row_corr(x, y)
                    spearman = row_corr(xranks, yranks)
                    linear_bps = pearson * ystd * 1e4
                    beta_corr = row_corr(x, beta[origins])
                    qmeans = np.full((len(origins), 10), np.nan)
                    qcounts = np.zeros((len(origins), 10), dtype=int)
                    for q in range(10):
                        membership = bins == q
                        counts = membership.sum(axis=1)
                        qcounts[:, q] = counts
                        good = counts > 0
                        qmeans[good, q] = np.sum(np.where(membership[good], y[good], 0.), axis=1) / counts[good]
                    # Each stock must be assigned once, and the mean must reconcile.
                    check(f"quantile_partition_h{horizon}_{target_name}_{feature}",
                          bool(np.all(qcounts.sum(axis=1) == 1000)), 1000,
                          sorted(np.unique(qcounts.sum(axis=1)).tolist()))
                    reconstruct = np.nansum(qmeans * qcounts, axis=1) / 1000
                    valid_y = np.isfinite(y).all(axis=1)
                    if np.any(valid_y):
                        error = float(np.max(np.abs(reconstruct[valid_y] - y[valid_y].mean(axis=1))))
                        max_reconstruction_error = max(max_reconstruction_error, error)
                    undefined["pearson"] += int((~np.isfinite(pearson)).sum())
                    undefined["spearman"] += int((~np.isfinite(spearman)).sum())
                    undefined["empty_buckets"] += int((qcounts == 0).sum())
                    spread_bps = (qmeans[:, 9] - qmeans[:, 0]) * 1e4
                    curvature_bps = (qmeans[:, 0] + qmeans[:, 9] - qmeans[:, 4] - qmeans[:, 5]) * .5e4
                    daily = pd.DataFrame({
                        "feature": feature, "horizon": horizon, "target": target_name,
                        "block": blocks, "feature_index": origins,
                        "label_start_index": first_labels, "label_end_index": final_labels,
                        "pearson_ic": pearson, "spearman_ic": spearman,
                        "standardized_linear_bps": linear_bps,
                        "top_minus_bottom_bps": spread_bps,
                        "curvature_bps": curvature_bps, "past_beta_corr": beta_corr,
                        **{f"q{q + 1}_bps": qmeans[:, q] * 1e4 for q in range(10)},
                    })
                    daily.to_csv(out / "daily_diagnostics.csv", mode="a", header=(daily_count == 0),
                                 index=False, float_format="%.17g")
                    daily_count += len(daily)
                    for period in ("pooled", "block_1", "block_2", "block_3", "block_4"):
                        mask = np.ones(len(origins), dtype=bool) if period == "pooled" else blocks == int(period[-1])
                        row = {"feature": feature, "horizon": horizon, "target": target_name,
                               "period": period, "n_origins": int(mask.sum()),
                               "mean_past_beta_corr": mean_or_nan(beta_corr[mask])}
                        for label, values in (("pearson", pearson), ("spearman", spearman),
                                              ("linear_bps", linear_bps), ("spread_bps", spread_bps),
                                              ("curvature_bps", curvature_bps)):
                            row.update({label + "_" + k: v for k, v in daily_stats(values[mask], first_labels[mask]).items()})
                        summary_rows.append(row)
                        horizon_rows.append(row)
                        for q in range(10):
                            quantile_rows.append({
                                "feature": feature, "horizon": horizon, "target": target_name,
                                "period": period, "quantile": q + 1,
                                "mean_bps_per_day": mean_or_nan(qmeans[mask, q] * 1e4),
                                "valid_origins": int(np.isfinite(qmeans[mask, q]).sum()),
                                "mean_bucket_size": qcounts[mask, q].mean(),
                            })
                    pooled = horizon_rows[-5]
                    if horizon == 1:
                        print(f"H1 {target_name:17s} {feature:8s}: IC={pooled['pearson_mean']:+.5f} "
                              f"rankIC={pooled['spearman_mean']:+.5f} "
                              f"spread={pooled['spread_bps_mean']:+.3f}bp/day "
                              f"curvature={pooled['curvature_bps_mean']:+.3f}bp/day", flush=True)
            write_csv(out / f"horizon_{horizon}_summary.csv", horizon_rows)
            print(f"Horizon {horizon} complete ({len(origins)} matured origins).", flush=True)

        write_csv(out / "predictive_summary.csv", summary_rows)
        write_csv(out / "quantile_shapes.csv", quantile_rows)
        redundancy_rows = []
        for j, left in enumerate(FEATURES):
            for k in range(j, len(FEATURES)):
                right = FEATURES[k]
                pearson = row_corr(chars[:, :, j], chars[:, :, k])
                spearman = row_corr(ranks_all[:, :, j], ranks_all[:, :, k])
                for period, lo, hi in PERIODS:
                    for method, values in (("pearson", pearson), ("spearman", spearman)):
                        row = {"feature_a": left, "feature_b": right, "period": period,
                               "method": method, "mean_daily_correlation": mean_or_nan(values[lo:hi]),
                               "valid_days": int(np.isfinite(values[lo:hi]).sum())}
                        redundancy_rows.append(row)
                        if j != k:
                            redundancy_rows.append({**row, "feature_a": right, "feature_b": left})
        write_csv(out / "redundancy.csv", redundancy_rows)

        check("daily_rows", daily_count == 135122, 135122, daily_count)
        check("summary_rows", len(summary_rows) == 390, 390, len(summary_rows))
        check("quantile_rows", len(quantile_rows) == 3900, 3900, len(quantile_rows))
        check("behavior_rows", len(feature_rows) == 65, 65, len(feature_rows))
        check("persistence_rows", len(persistence_rows) == 195, 195, len(persistence_rows))
        check("redundancy_rows", len(redundancy_rows) == 1690, 1690, len(redundancy_rows))
        check("quantile_reconstruction", max_reconstruction_error <= 1e-12,
              "maximum absolute error <= 1e-12", max_reconstruction_error)
        for filename in ("daily_diagnostics.csv", "predictive_summary.csv", "quantile_shapes.csv",
                         "characteristic_summary.csv", "persistence.csv", "redundancy.csv"):
            check("nonempty_" + filename, (out / filename).stat().st_size > 0,
                  "nonempty", (out / filename).stat().st_size)
        input_after = {str(p): sha256(p) for p in source_files}
        check("input_immutability", input_after == input_hashes, input_hashes, input_after)
        write_json(out / "undefined_values.json", {
            **undefined,
            "interpretation": "Undefined values arise from zero cross-sectional variance, unavailable past beta, or empty rank buckets; never replaced with zero.",
            "unavailable_beta_feature_dates": int((~valid_beta).sum()),
        })
        artifacts = [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)}
                     for p in sorted(out.iterdir()) if p.is_file() and p.name not in
                     {"summary.json", "stdout.log", "stderr.log", "artifact_manifest.json"}]
        write_json(out / "artifact_manifest.json", artifacts)
        summary.update({"status": "PASS_SCOPE_ONLY", "exit_code": 0,
                        "checks_passed": len(checks), "elapsed_seconds": time.perf_counter() - started,
                        "daily_diagnostic_rows": daily_count,
                        "undefined_value_counts": undefined,
                        "completed_utc": datetime.now(timezone.utc).isoformat(),
                        "limitations": ["descriptive discovery relationships only", "no portfolio or costs scored",
                                        "no validation or audit access", "no hidden-future evidence",
                                        "multiple inspected features/horizons are recorded research exposures"]})
        write_json(out / "summary.json", summary)
        print(json.dumps(clean_json(summary)), flush=True)
        return 0
    except BaseException as exc:
        traceback.print_exc()
        summary.update({"status": "INCOMPLETE" if isinstance(exc, KeyboardInterrupt) else "FAIL",
                        "exit_code": 130 if isinstance(exc, KeyboardInterrupt) else 1,
                        "exception": repr(exc), "checks_passed": sum(x["status"] == "PASS" for x in checks),
                        "elapsed_seconds": time.perf_counter() - started})
        write_json(out / "summary.json", summary)
        return summary["exit_code"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    sys.exit(main(parser.parse_args()))
