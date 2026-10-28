"""Independent beta-factor and centering readback; no trading policy is changed."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from ledger_readback import hac_regression


def basis(panel):
    centered = panel - np.mean(panel, axis=0)
    z = centered / np.maximum(np.sqrt(np.mean(centered ** 2, axis=0)), 1e-12)
    z = np.clip(z, -4.0, 4.0)
    z -= z.mean(axis=0)
    squares = z ** 2
    return np.column_stack((z, (squares - squares.mean(axis=0)) / np.sqrt(2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    R = np.ascontiguousarray(pd.read_csv(args.data / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(args.data / "characteristics.csv", index_col=["day", "stock"])
                             .to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    market = R.mean(axis=1)
    rows = []
    for t in range(253, len(R)):
        window = R[t - 252:t]
        past_market = window.mean(axis=1)
        past_market -= past_market.mean()
        stock_centered = window - window.mean(axis=0)
        bhat = (past_market @ stock_centered) / (past_market @ past_market)
        e = R[t] - bhat * market[t]
        residual_mean_before_demeaning = float(e.mean())
        e -= e.mean()
        z = bhat - bhat.mean()
        z = np.clip(z / max(z.std(), 1e-12), -4.0, 4.0)
        z -= z.mean()
        D = basis(X[t - 1])
        projection = D @ np.linalg.lstsq(D, z, rcond=None)[0]
        z_orthogonal = z - projection
        denominator = float(z_orthogonal @ z_orthogonal)
        # Frisch-Waugh-Lovell calculation, independent of the submitted joint solve.
        joint = float(z_orthogonal @ e / denominator)
        raw_joint = float(z_orthogonal @ R[t] / denominator)
        hedge_loading = float(z_orthogonal @ bhat / denominator)
        rows.append({"diagnostic_return_index": t, "market": market[t],
                     "beta_factor_univariate": float(z @ e / (z @ z)),
                     "beta_factor_joint": joint, "raw_beta_factor_joint": raw_joint,
                     "estimated_beta_of_joint_raw_factor": hedge_loading,
                     "raw_residual_identity_error": raw_joint - joint - hedge_loading * market[t],
                     "outside_span_squared_norm_share": 1 - float(projection @ projection) / float(z @ z),
                     "mean_beta_minus_one": float(bhat.mean() - 1),
                     "residual_mean_before_demeaning": residual_mean_before_demeaning})
    daily = pd.DataFrame(rows)
    daily_path = args.out_dir / "factor_daily.csv"
    daily.to_csv(daily_path, index=False)
    regressions = {}
    for name in ("beta_factor_univariate", "beta_factor_joint", "raw_beta_factor_joint"):
        regressions[name] = {str(lag): hac_regression(daily[name].to_numpy(), daily.market.to_numpy(), lag)
                             for lag in (10, 21, 63, 126)}
    expected = json.loads((args.snapshot / "research/v2/results/beta_diagnostics.json").read_text())
    differences = {}
    for name, key in (("beta_factor_univariate", "D1_univariate"), ("beta_factor_joint", "D1_joint_with_26")):
        r = regressions[name]["10"]
        ref = expected[key]
        differences[name] = {
            "intercept_bp": 1e4 * r["intercept_daily"] - ref["intercept_bp_per_day"],
            "market_slope": r["beta"] - ref["market_slope"],
            "intercept_t": r["intercept_daily"] / r["se"][0] - ref["intercept_t"],
            "market_slope_t": r["beta"] / r["se"][1] - ref["market_slope_t"],
        }
    result = {
        "source_commit": "ce3fe4e76271709422165d6f24e2fbecd9d0fe07",
        "n": len(daily), "index_min": int(daily.diagnostic_return_index.min()),
        "index_max": int(daily.diagnostic_return_index.max()),
        "regressions": regressions, "differences_from_submitted": differences,
        "outside_span_squared_norm_share": {
            "mean": float(daily.outside_span_squared_norm_share.mean()),
            "min": float(daily.outside_span_squared_norm_share.min())},
        "max_abs_mean_beta_minus_one": float(daily.mean_beta_minus_one.abs().max()),
        "max_abs_residual_cross_section_mean_before_demeaning": float(daily.residual_mean_before_demeaning.abs().max()),
        "max_abs_raw_residual_factor_identity_error": float(daily.raw_residual_identity_error.abs().max()),
        "daily_sha256": hashlib.sha256(daily_path.read_bytes()).hexdigest(),
    }
    (args.out_dir / "factor_readback.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "regressions"}, indent=2))
    print(json.dumps({"joint_lag10": regressions["beta_factor_joint"]["10"]}, indent=2))


if __name__ == "__main__":
    main()
