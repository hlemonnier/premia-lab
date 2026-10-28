"""Independent descriptive readback of committed ledgers; see PLAN.md."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

STAGES = {"full": (253, 3779), "discovery": (253, 2015),
          "validation": (2016, 3023), "audit": (3024, 3779)}
NAMES = {"C09": "C09_engine", "V2": "fr_beta_phi03_x5",
         "R27": "V2_R27_beta_risk", "diagonal": "V2_matched_diagonal",
         "B0": "V2_B0_beta_neutral", "B05": "V2_B05_explicit_beta"}


def hac_regression(y, market, lags=10):
    design = np.column_stack((np.ones(len(y)), market))
    coef = np.linalg.lstsq(design, y, rcond=None)[0]
    residual = y - design @ coef
    xu = design * residual[:, None]
    meat = xu.T @ xu
    for lag in range(1, lags + 1):
        cross = xu[lag:].T @ xu[:-lag]
        meat += (1 - lag / (lags + 1)) * (cross + cross.T)
    bread = np.linalg.inv(design.T @ design)
    se = np.sqrt(np.maximum(np.diag(bread @ meat @ bread), 0))
    return {
        "intercept_daily": float(coef[0]), "beta": float(coef[1]),
        "se": se.tolist(), "ci95_normal_hac": np.column_stack((coef - 1.96 * se, coef + 1.96 * se)).tolist(),
        "intercept_ann_pct": float(25200 * coef[0]),
        "market_mean_component_ann_pct": float(25200 * coef[1] * market.mean()),
        "r2": float(1 - np.var(residual) / np.var(y)),
        "residual_vol_ann_pct": float(100 * np.sqrt(252) * np.std(residual)),
        "ex_post_market_removed_sharpe": float(np.sqrt(252) * coef[0] / np.std(residual)),
        "lags": lags,
    }


def metrics(a):
    day, net, gross, fee, market = a
    return {name: {
        "n": int(np.sum(k)), "sharpe": float(np.sqrt(252) * net[k].mean() / net[k].std()),
        "ret_pct": float(25200 * net[k].mean()), "vol_pct": float(100 * np.sqrt(252) * net[k].std()),
        "cost_pct": float(25200 * fee[k].mean()),
        "net_market": hac_regression(net[k], market[k]),
        "gross_market": hac_regression(gross[k], market[k]),
        "fee_beta": float(np.cov(fee[k], market[k], ddof=0)[0, 1] / np.var(market[k])),
    } for name, (lo, hi) in STAGES.items() for k in [(day >= lo) & (day < hi)]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--prior-evidence", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    R = pd.read_csv(args.data / "returns.csv", index_col="day").to_numpy(np.float64)
    market = R.mean(axis=1)
    folder = args.snapshot / "research/v2/results/ledgers"
    identity, checks, arrays = {}, {}, {}
    for path in sorted(folder.glob("net_*.npy")):
        a = np.load(path, allow_pickle=False)
        assert a.shape == (5, 3526), (path.name, a.shape)
        assert np.isfinite(a).all(), path.name
        assert np.array_equal(a[0], np.arange(253, 3779)), path.name
        cost_error = float(np.max(np.abs(a[1] - (a[2] - a[3]))))
        market_error = float(np.max(np.abs(a[4] - market[a[0].astype(int)])))
        assert cost_error <= 1e-12 and market_error <= 1e-12, path.name
        checks[path.name] = {"net_gross_fee_error": cost_error, "market_error": market_error}
        identity[path.name] = sha(path)
        arrays[path.stem.removeprefix("net_")] = a
    chosen = {label: arrays[name] for label, name in NAMES.items()}
    result = {"source_commit": "ce3fe4e76271709422165d6f24e2fbecd9d0fe07",
              "input_return_csv_sha256": sha(args.data / "returns.csv"),
              "ledger_sha256": identity, "ledger_checks": checks,
              "policies": {label: metrics(a) for label, a in chosen.items()}}
    compare = {}
    for label, a in chosen.items():
        path = args.snapshot / f"research/v2/results/candidates/{NAMES[label]}.json"
        if path.exists():
            expected = json.loads(path.read_text())
            compare[label] = {s: {f: result["policies"][label][s][f] - expected[s][f]
                                 for f in ("sharpe", "ret_pct", "vol_pct", "cost_pct")}
                              for s in STAGES}
    result["candidate_summary_differences"] = compare
    reference = {}
    for label, run in (("C09", "run_c09_003"), ("V2", "run_v2_001")):
        prior = pd.read_csv(args.prior_evidence / run / "daily.csv")
        assert np.array_equal(prior["return_index"].to_numpy(), chosen[label][0]), label
        reference[label] = {"columns": prior.columns.tolist()}
        # Preserve exact column matching in the output; a schema mismatch is a failure.
        mapping = {"net": 1, "gross_return": 2, "cost": 3, "market": 4}
        aliases = {"net": ("net", "net_return"), "gross_return": ("gross_return", "gross", "portfolio_return"),
                   "cost": ("full_cost", "cost", "trading_cost", "fee"), "market": ("market", "market_return")}
        for key, row in mapping.items():
            col = next((c for c in aliases[key] if c in prior), None)
            if col is None:
                raise ValueError(f"Unrecognized prior ledger field {key}: {list(prior)}")
            error = float(np.max(np.abs(prior[col].to_numpy() - chosen[label][row])))
            reference[label][key + "_max_abs_difference"] = error
            assert error <= 1e-8, (label, key, error)
    result["prior_literal_package_comparison"] = reference
    increment = chosen["B05"].copy()
    increment[1:4] -= chosen["B0"][1:4]
    result["B05_minus_B0_incremental_policy_returns"] = metrics(increment)
    # One shared resampling index per length, applied to every policy.
    paired = {}
    for length in (21, 63, 126):
        n = 3526
        rng = np.random.default_rng(20261027)
        starts = rng.integers(0, n - length + 1, size=(2000, (n + length - 1) // length))
        indices = (starts[..., None] + np.arange(length)).reshape(2000, -1)[:, :n]
        sampled = {}
        for name, a in chosen.items():
            x = a[1][indices]
            sampled[name] = np.sqrt(252) * x.mean(axis=1) / x.std(axis=1)
        paired[str(length)] = {name: {
            "point_difference": result["policies"][name]["full"]["sharpe"] - result["policies"]["V2"]["full"]["sharpe"],
            "ci95_percentile": np.percentile(values - sampled["V2"], [2.5, 97.5]).tolist(),
        } for name, values in sampled.items() if name != "V2"}
    result["paired_net_sharpe_vs_V2"] = paired
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"ledgers_verified": len(checks), "summary": {
        k: {"sharpe": v["full"]["sharpe"], "beta": v["full"]["net_market"]["beta"],
            "market_removed": v["full"]["net_market"]["ex_post_market_removed_sharpe"]}
        for k, v in result["policies"].items()},
        "increment": result["B05_minus_B0_incremental_policy_returns"]["full"]}, indent=2))


if __name__ == "__main__":
    main()
