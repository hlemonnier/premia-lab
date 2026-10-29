"""Read-only fixed-policy arithmetic under PLAN.md; no strategy imports/runs."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV_SHA = {
    "published_E2_daily.csv": "dfdd79e56ee789521a73a1ed0129cf1ee2cd6d8895f13012ba7b47b5e8c2e357",
    "published_joint_daily.csv": "460c9ade0270b219e89b7b834e4bd668a667c01aa20c9fa96746b9670211b0b6",
}
RETURNS_SHA = "6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def moments(net, market):
    p, m = net - net.mean(), market - market.mean()
    beta = float(p @ m / (m @ m))
    ann_mean = float(252 * net.mean())
    ann_vol = float(np.sqrt(252) * net.std(ddof=0))
    return {
        "n": int(len(net)),
        "ann_arithmetic_mean": ann_mean,
        "ann_volatility": ann_vol,
        "net_sharpe": ann_mean / ann_vol,
        "descriptive_net_beta": beta,
        "market_ols_explained_variance_fraction": float(beta**2 * (m @ m) / (p @ p)),
        "beta_times_market_mean_ann": float(beta * 252 * market.mean()),
        "remaining_mean_after_beta_times_market_mean_ann": float(ann_mean - beta * 252 * market.mean()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise RuntimeError("Do not overwrite a prior result")
    receipts = json.loads((HERE / "retrieval_receipts.json").read_text())
    inputs = {}
    for receipt in receipts:
        path = HERE / receipt["local"]
        b = path.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
        assert actual == receipt["blob_sha"], receipt["local"]
        inputs[receipt["local"]] = {"git_blob_sha": actual, "sha256": sha(path)}
    for name, expected in CSV_SHA.items():
        assert sha(HERE / name) == expected, name
    returns_file = args.data / "returns.csv"
    assert sha(returns_file) == RETURNS_SHA
    R = pd.read_csv(returns_file, index_col="day").to_numpy(np.float64)
    assert R.shape == (3780, 1000) and np.isfinite(R).all()
    originals = {
        "E2": pd.read_csv(HERE / "published_E2_daily.csv", float_precision="round_trip"),
        "joint": pd.read_csv(HERE / "published_joint_daily.csv", float_precision="round_trip"),
    }
    net, stats, checks = {}, {}, {}
    market = originals["joint"]["market_return"].to_numpy()
    expected_market = R[253:3779].mean(axis=1)
    checks["original_market_max_error"] = float(np.max(np.abs(market - expected_market)))
    assert checks["original_market_max_error"] <= 1e-15
    for name, frame in originals.items():
        assert np.array_equal(frame["return_index"].to_numpy(), np.arange(253, 3779))
        assert np.array_equal(frame["market_return"].to_numpy(), market)
        net[name] = frame["net_return"].to_numpy()
        assert np.isfinite(frame.to_numpy()).all()
        err = np.max(np.abs(net[name] - (frame["gross_return"] - frame["full_cost"]).to_numpy()))
        assert err <= 1e-15
        checks[name + "_saved_net_identity_error"] = float(err)
        stats[name] = moments(net[name], market)
        stats[name]["annual_actual_fees"] = float(252 * frame["full_cost"].mean())
    mu_m = float(252 * market.mean())
    sig_m = float(np.sqrt(252) * market.std(ddof=0))
    claude = json.loads((HERE / "claude_sleeve_comparison.json").read_text())
    checks["claude_moment_absolute_differences"] = {}
    for name, key in (("E2", "0.0"), ("joint", "0.05")):
        difference = {}
        for ours, theirs in (("net_sharpe", "net_sharpe"),
                             ("ann_arithmetic_mean", "ann_return"),
                             ("ann_volatility", "ann_vol"),
                             ("annual_actual_fees", "ann_cost"),
                             ("descriptive_net_beta", "beta")):
            difference[ours] = abs(stats[name][ours] - claude[key][theirs])
        checks["claude_moment_absolute_differences"][name] = difference
    delta_g = (originals["joint"]["gross_return"] - originals["E2"]["gross_return"]).to_numpy()
    checks["joint_minus_E2_gross_equals_point05_market_max_error"] = float(np.max(np.abs(delta_g - .05 * market)))
    assert checks["joint_minus_E2_gross_equals_point05_market_max_error"] <= 1e-12
    common_scenarios = []
    for scenario, nu in (("observed_mean", mu_m), ("zero_common_market_mean", 0.),
                         ("reversed_common_market_mean", -mu_m)):
        item = {"scenario": scenario, "assumed_market_annual_arithmetic_mean": nu}
        for name in ("joint", "E2"):
            s = stats[name]
            item[name + "_frozen_mean_sharpe"] = (
                s["ann_arithmetic_mean"] + s["descriptive_net_beta"] * (nu - mu_m)
            ) / s["ann_volatility"]
        item["joint_minus_E2"] = item["joint_frozen_mean_sharpe"] - item["E2_frozen_mean_sharpe"]
        common_scenarios.append(item)
    slope = (stats["joint"]["descriptive_net_beta"] / stats["joint"]["ann_volatility"]
             - stats["E2"]["descriptive_net_beta"] / stats["E2"]["ann_volatility"])
    observed_delta = stats["joint"]["net_sharpe"] - stats["E2"]["net_sharpe"]
    crossing = None if abs(slope) < 1e-15 else mu_m - observed_delta / slope
    narrow = {
        "meaning": "Change only the added .05 sleeve's annual mean contribution, retaining the inner book's historical mean, the final book's volatility and actual fees.",
        "sleeve_mean_zero_sharpe": (stats["joint"]["ann_arithmetic_mean"] - .05 * mu_m) / stats["joint"]["ann_volatility"],
        "sleeve_mean_reversed_sharpe": (stats["joint"]["ann_arithmetic_mean"] - .10 * mu_m) / stats["joint"]["ann_volatility"],
        "unchanged_E2_sharpe": stats["E2"]["net_sharpe"],
    }
    result = {
        "scope_sha256": sha(HERE / "PLAN.md"),
        "readback_source_sha256": sha(__file__),
        "argv": sys.argv,
        "source_heads": {"claude": "978824d4b6140c43566ebd61a3ee8157f4080e35", "research": "9e56aa755d20c5876485188f4c50ce959f6d63f3"},
        "inputs": inputs,
        "returns_csv_sha256": RETURNS_SHA,
        "earning_rows_zero_based_inclusive": [253, 3778],
        "no_strategy_execution": True,
        "no_new_policy_or_weight_search": True,
        "checks": checks,
        "market": {"annual_arithmetic_mean": mu_m, "annual_volatility": sig_m, "sharpe": mu_m / sig_m},
        "published_fixed_policy_moments": stats,
        "claude_sleeve_only_mean_sensitivity_reconstructed": narrow,
        "common_market_mean_sensitivity": common_scenarios,
        "conditional_common_market_mean_breakeven_ann": crossing,
        "sharpe_difference_slope_per_unit_annual_market_mean": slope,
        "limitations": [
            "Fixed full-sample beta, volatility, nonmarket mean, centered fluctuations, held positions and costs. These are descriptive scenarios, not policies or causal forecasts.",
            "No strategy rerun under a different market process. Changed returns can change future forecasts, risk estimates, portfolio drift, positions and fees.",
            "OLS remainder and beta-times-market mean are descriptive projections, not identified economic alpha or the result of a tradable hedge.",
            "No confidence interval for the breakeven and no claim that future market moments equal observed moments.",
            "All historical periods are exposed development data; no new out-of-sample evidence.",
        ],
    }
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"out": str(args.out), "sha256": sha(args.out),
                      "market": result["market"], "narrow": narrow,
                      "common_scenarios": common_scenarios,
                      "conditional_breakeven_ann": crossing}, indent=2))


if __name__ == "__main__":
    main()
