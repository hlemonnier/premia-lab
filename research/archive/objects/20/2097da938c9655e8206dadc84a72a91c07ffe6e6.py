"""Decay of the residual-reversal and characteristic signals: IC of a signal formed at
close of day s with residual return on day s+L, L = 1..30 (every day sampled)."""
import numpy as np
from common import load, causal_betas, residuals, zscore_panel
from factor_level import basis
R, X, _ = load(); T, N = R.shape
beta, m = causal_betas(R); E = residuals(R, beta, m)
cs = np.zeros((T + 1, N)); np.cumsum(E, axis=0, out=cs[1:])
F = np.load("out/F26.npy")
lags = [1, 2, 3, 5, 10, 15, 20, 30, 60]
ic_rev = {L: [] for L in lags}; ic_c09 = {L: [] for L in lags}
coef = np.nanmean(F[253:], axis=0)  # full-sample premium vector: descriptive only
for s in range(300, T - 61):
    D = basis(np.asarray(X[s], dtype=np.float64))
    resid = lambda v: v - D @ np.linalg.lstsq(D, v - v.mean(), rcond=None)[0] - v.mean()
    rev = -resid(cs[s + 1] - cs[s - 20])          # minus past 21-day residual return
    sig = D @ coef
    for L in lags:
        e = E[s + L] - E[s + L].mean()
        ic_rev[L].append(np.corrcoef(rev, e)[0, 1]); ic_c09[L].append(np.corrcoef(sig, e)[0, 1])
print("lag   rev_IC*1e3 (t)     char_IC*1e3 (t)")
for L in lags:
    a = np.array(ic_rev[L]); b = np.array(ic_c09[L])
    print(f"{L:3d}  {1e3*a.mean():+7.2f} ({a.mean()/a.std()*np.sqrt(len(a)):+5.1f})   {1e3*b.mean():+7.2f} ({b.mean()/b.std()*np.sqrt(len(b)):+5.1f})")
