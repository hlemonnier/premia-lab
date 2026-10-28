"""Separate H-beta-return from H-beta-error (descriptive; uses only published-time estimates
for every quantity that a trading decision could use, plus explicitly ex-post evaluation).

Usage:  python beta_diagnostics.py --data DIR_WITH_CSVS --ledgers DIR_WITH_net_*.npy --out OUT.json

D1  Beta factor return: each day t, cross-sectional regression of the market residual
    e_t = r_t - bhat_t m_t (bhat_t from rows < t, demeaned) on the standardized, clipped,
    centered bhat_t, alone and jointly with the 26-column characteristic basis of X[t-1].
    Then time-series regression f_beta,t = a + c m_t + u (Newey-West, 10 lags).
    H-beta-error predicts c < 0 and a mean of f_beta explained by c * mean(m);
    H-beta-return predicts an intercept a with c near 0.
D2  Regression toward one: slope of next-252-day realized beta on bhat (ex-post).
D3  Incremental span of the beta column relative to the 26 columns (same-date panel).
D4  Market component of realized strategy returns (ex-post regression on m).
D5  Synthetic known truth: constant true betas, zero alpha, positive market mean.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "handoff_v2"))
from model_v2.engine import basis, causal_betas  # noqa: E402


def nw_t(y, X, lags=10):
    """OLS with Newey-West standard errors. Returns coef, t-stats."""
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    S = (X * u[:, None]).T @ (X * u[:, None])
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = (X[L:] * u[L:, None]).T @ (X[:-L] * u[:-L, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return b, b / np.sqrt(np.diag(V))


def zcol(v, clip=4.0):
    v = v - v.mean(); v = np.clip(v / max(v.std(), 1e-12), -clip, clip)
    return v - v.mean()


def beta_factor(R, X, start=253):
    T, N = R.shape
    beta, m = causal_betas(R)
    E = R - beta * m[:, None]
    f_uni = np.full(T, np.nan); f_joint = np.full(T, np.nan); span = np.full(T, np.nan)
    for t in range(start, T):
        e = E[t] - E[t].mean(); z = zcol(beta[t])
        f_uni[t] = z @ e / (z @ z)
        if X is not None:
            D = basis(X[t - 1]); A = np.hstack([D, z[:, None]])
            f_joint[t] = np.linalg.lstsq(A, e, rcond=None)[0][-1]
            proj = D @ np.linalg.lstsq(D, z, rcond=None)[0]
            span[t] = 1 - (proj @ proj) / (z @ z)          # share of beta column outside the 26-column span
    return f_uni, f_joint, span, beta, m


def ts_test(f, m, start=253):
    k = np.isfinite(f); k[:start] = False
    y = f[k]; X = np.column_stack([np.ones(k.sum()), m[k]])
    b, t = nw_t(y, X)
    return {"intercept_bp_per_day": 1e4 * b[0], "intercept_t": t[0], "market_slope": b[1], "market_slope_t": t[1],
            "mean_f_bp": 1e4 * y.mean(), "slope_times_mean_market_bp": 1e4 * b[1] * m[k].mean(),
            "r2": 1 - np.var(y - X @ b) / np.var(y), "n": int(k.sum())}


def regression_to_one(R, beta, window=252, start=253):
    """Slope of realized beta over the next `window` days on bhat; 1 - slope = eta."""
    T, N = R.shape; slopes = []
    for t in range(start, T - window, 21):
        W = R[t:t + window]; m = W.mean(axis=1); m = m - m.mean(); c = W - W.mean(axis=0)
        b_post = (m @ c) / (m @ m); b_pre = beta[t]
        x = b_pre - b_pre.mean(); slopes.append((x @ (b_post - b_post.mean())) / (x @ x))
    s = np.array(slopes)
    return {"mean_slope": float(s.mean()), "eta": float(1 - s.mean()), "min": float(s.min()), "max": float(s.max()), "n_dates": len(s)}


def synthetic(T=2500, N=1000, seed=0):
    rng = np.random.default_rng(seed)
    b_true = rng.uniform(0.3, 1.7, N)
    m = 0.0005 + 0.008 * rng.standard_normal(T)            # positive market mean
    R = b_true * m[:, None] + 0.018 * rng.standard_normal((T, N))   # zero alpha
    R = np.ascontiguousarray(R)
    f_uni, _, _, beta, mm = beta_factor(R, None)
    out = ts_test(f_uni, mm)
    out["regression_to_one"] = regression_to_one(R, beta)
    return out


def market_component(path):
    day, net, pr, cost, mkt = np.load(path)
    X = np.column_stack([np.ones(len(net)), mkt]); b, t = nw_t(net, X)
    resid = net - b[1] * mkt
    return {"beta": b[1], "beta_t": t[1], "alpha_ann_pct": 100 * 252 * b[0], "alpha_t": t[0],
            "net_ann_pct": 100 * 252 * net.mean(), "market_part_ann_pct": 100 * 252 * b[1] * mkt.mean(),
            "sharpe": float(np.sqrt(252) * net.mean() / net.std()),
            "sharpe_ex_post_market_removed": float(np.sqrt(252) * resid.mean() / resid.std())}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--ledgers", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
    ch = pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"])
    X = np.ascontiguousarray(ch.to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    f_uni, f_joint, span, beta, m = beta_factor(R, X)
    res = {"D1_univariate": ts_test(f_uni, m), "D1_joint_with_26": ts_test(f_joint, m),
           "D2_regression_to_one": regression_to_one(R, beta),
           "D3_beta_share_outside_26_span": {"mean": float(np.nanmean(span[253:])), "min": float(np.nanmin(span[253:]))},
           "D4_market_component": {n: market_component(f"{a.ledgers}/net_{n}.npy")
                                   for n in ("C09_engine", "beta_feat", "fr_beta_phi03_x5")
                                   if os.path.exists(f"{a.ledgers}/net_{n}.npy")},
           "D5_synthetic_zero_alpha": synthetic()}
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))
