"""Shared loading and causal helpers for the exploration scripts.

Conventions: zero-based row indices. Row t of returns is day t's return,
published with day t's characteristics after day t's close.
"""
import os
import sys

import numpy as np
import pandas as pd

DATA = os.environ.get("TAKEHOME_DATA", "/home/claude/data/Quant Research Take-Home")
CACHE = os.environ.get("TAKEHOME_CACHE", "/home/claude/data/cache")
NAMES = "Woe Malice Dread Frolic Up Down Charm Strange Top Bottom Snap Crackle Pop".split()
GROUPS = {"tempers": NAMES[0:4], "quarks": NAMES[4:10], "elves": NAMES[10:13]}
GROUP_IDX = {g: [NAMES.index(n) for n in v] for g, v in GROUPS.items()}
# Same stage boundaries as the repo, for comparability (scorer row convention).
STAGES = {"discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}


def load():
    """R (T,N) float64, X (T,N,13) float32, costs (N,) — cached as .npy."""
    os.makedirs(CACHE, exist_ok=True)
    paths = [f"{CACHE}/{k}.npy" for k in ("R", "X", "costs")]
    if all(os.path.exists(p) for p in paths):
        R = np.load(paths[0]); X = np.load(paths[1], mmap_mode="r"); c = np.load(paths[2])
        return R, X, c
    R_df = pd.read_csv(f"{DATA}/returns.csv", index_col="day")
    costs = pd.read_csv(f"{DATA}/costs.csv", index_col="stock")["cost"]
    ch = pd.read_csv(f"{DATA}/characteristics.csv", index_col=["day", "stock"])
    assert list(ch.columns) == NAMES, ch.columns
    assert list(R_df.columns) == list(costs.index)
    R = np.ascontiguousarray(R_df.to_numpy(dtype=np.float64))
    X = np.ascontiguousarray(ch.to_numpy(dtype=np.float32).reshape(len(R_df), len(costs), 13))
    c = costs.to_numpy(dtype=np.float64)
    assert np.isfinite(R).all() and np.isfinite(X).all() and np.isfinite(c).all()
    np.save(paths[0], R); np.save(paths[1], X); np.save(paths[2], c)
    return R, X, c


def causal_betas(R, window=252, min_days=20):
    """beta[t] uses returns rows [t-window, t) only. beta[t] = 1 before min_days."""
    T, N = R.shape
    m = R.mean(axis=1)
    def csum(a):
        out = np.zeros((T + 1,) + a.shape[1:]); np.cumsum(a, axis=0, out=out[1:]); return out
    Sm, Smm = csum(m), csum(m * m)
    Sr, Smr = csum(R), csum(R * m[:, None])
    beta = np.ones((T, N))
    for t in range(min_days, T):
        lo = max(0, t - window); n = t - lo
        mm = (Smm[t] - Smm[lo]) / n - ((Sm[t] - Sm[lo]) / n) ** 2
        if mm <= 1e-12:
            continue
        cov = (Smr[t] - Smr[lo]) / n - (Sm[t] - Sm[lo]) / n * (Sr[t] - Sr[lo]) / n
        beta[t] = cov / mm
    return beta, m


def residuals(R, beta, m):
    """e[t] = r[t] - beta[t] * m[t], beta[t] estimated before day t."""
    return R - beta * m[:, None]


def zscore_panel(P):
    """Cross-sectional z-score of a (N,k) panel, using that panel only."""
    P = np.asarray(P, dtype=np.float64)
    c = P - P.mean(axis=0)
    return c / np.maximum(c.std(axis=0), 1e-12)


def stage_slices():
    return {k: slice(a, b) for k, (a, b) in STAGES.items()}


def sharpe(x):
    x = np.asarray(x); s = x.std()
    return float(np.sqrt(252) * x.mean() / s) if s > 0 else float("nan")


if __name__ == "__main__":
    R, X, c = load()
    print("R", R.shape, R.dtype, "X", X.shape, X.dtype, "costs", c.shape, c.min(), c.max())
    sys.exit(0)
