"""Market-structure tests (descriptive, full sample, all periods exposed).

T1  Do the 4/6/3 name groups show up in the raw characteristic correlations?
T2  Do characteristics explain residual (market-removed) covariance, i.e. behave
    like factor loadings? Compare against PCA of the same residuals.
T3  Daily characteristic "factor returns" f_t from cross-sectional regressions of
    residual returns on X[t-1]: premia, stability, persistence, payoff decay.
"""
import itertools
import json
import os

import numpy as np

from common import NAMES, GROUPS, GROUP_IDX, STAGES, load, causal_betas, residuals, zscore_panel, sharpe

OUT = "/home/claude/explore/out"
os.makedirs(OUT, exist_ok=True)
R, X, costs = load()
T, N = R.shape
beta, m = causal_betas(R)
E = residuals(R, beta, m)
res = {}

# ---------- T1: group structure ----------
C = np.zeros((13, 13)); Cb = np.zeros((4, 13, 13))
block_of = np.minimum(np.arange(T) * 4 // T, 3)
for t in range(T):
    Z = zscore_panel(X[t]); c = Z.T @ Z / N
    C += c; Cb[block_of[t]] += c
C /= T; Cb /= np.bincount(block_of)[:, None, None]
grp = {n: g for g, v in GROUPS.items() for n in v}
lab = np.array([grp[n] for n in NAMES])
def within_between(M):
    w = [abs(M[i, j]) for i, j in itertools.combinations(range(13), 2) if lab[i] == lab[j]]
    b = [abs(M[i, j]) for i, j in itertools.combinations(range(13), 2) if lab[i] != lab[j]]
    return float(np.mean(w)), float(np.mean(b))
rng = np.random.default_rng(0)
obs = within_between(C)[0]
perm = []
for _ in range(20000):
    p = rng.permutation(lab); mask = p[:, None] == p[None, :]; np.fill_diagonal(mask, False)
    perm.append(np.abs(C[mask]).mean())
res["T1"] = {
    "within_between_full": within_between(C),
    "within_between_by_quarter_of_sample": [within_between(Cb[b]) for b in range(4)],
    "perm_p": float(np.mean(np.array(perm) >= obs)),
    "top_pairs": sorted([(NAMES[i], NAMES[j], round(float(C[i, j]), 3), lab[i] == lab[j])
                         for i, j in itertools.combinations(range(13), 2)], key=lambda x: -abs(x[2]))[:12],
    "group_first_pc_share": {g: float(np.linalg.eigvalsh(C[np.ix_(ix, ix)])[-1] / len(ix)) for g, ix in GROUP_IDX.items()},
}
np.save(f"{OUT}/char_corr.npy", C)

# ---------- T3 first: daily cross-sectional slopes on X[t-1] ----------
# f[t] = argmin ||e[t] - Z[t-1] f||, Z standardized panel of day t-1 (13 linear cols).
F = np.full((T, 13), np.nan); R2 = np.full(T, np.nan)
Fsq = np.full((T, 13), np.nan)
for t in range(253, T):  # betas mature by then; same start as the scorer
    Z = zscore_panel(X[t - 1]); e = E[t] - E[t].mean()
    f, *_ = np.linalg.lstsq(Z, e, rcond=None); F[t] = f
    fit = Z @ f; R2[t] = fit @ fit / (e @ e)
    S = Z * Z; S = S - S.mean(axis=0)
    fs, *_ = np.linalg.lstsq(np.hstack([Z, S]), e, rcond=None); Fsq[t] = fs[13:]
np.save(f"{OUT}/F_linear.npy", F); np.save(f"{OUT}/F_square.npy", Fsq)
ok = np.isfinite(F[:, 0])

# ---------- T2: characteristics vs residual covariance ----------
Ev = E[253:] - E[253:].mean(axis=0)
ev = np.linalg.eigvalsh(Ev.T @ Ev / len(Ev))[::-1]
pca_share = {k: float(ev[:k].sum() / ev.sum()) for k in (1, 3, 5, 10, 13, 20, 50)}
res["T2"] = {
    "mean_daily_R2_13_lagged_characteristics": float(np.nanmean(R2)),
    "chance_R2_13_regressors": 13 / N,
    "residual_variance_share_top_k_pcs_full_sample": pca_share,
    # stock-level: how much of each stock's residual covariance with others is
    # described by its average characteristics?
}
xbar = np.mean([zscore_panel(X[t]) for t in range(0, T, 5)], axis=0)  # (N,13)
corr = np.corrcoef(Ev.T)
iu = np.triu_indices(N, 1)
def mantel(S):
    a, b = corr[iu], S[iu]
    ra, rb = a.argsort().argsort(), b.argsort().argsort()
    return float(np.corrcoef(ra, rb)[0, 1])
res["T2"]["mantel_spearman_residcorr_vs_char_similarity"] = {
    **{g: mantel(xbar[:, ix] @ xbar[:, ix].T) for g, ix in GROUP_IDX.items()},
    "all13": mantel(xbar @ xbar.T),
    **{n: mantel(np.outer(xbar[:, k], xbar[:, k])) for k, n in enumerate(NAMES)},
}

# ---------- T3: premia, stability, persistence ----------
def stage_stats(series):
    out = {}
    for s, (a, b) in STAGES.items():
        x = series[a:b]; x = x[np.isfinite(x)]
        out[s] = {"ann_sharpe": sharpe(x), "mean_bp": float(1e4 * x.mean())}
    return out
res["T3"] = {"linear": {}, "square": {}}
for k, n in enumerate(NAMES):
    f = F[:, k]; fv = f[ok]
    ac = [float(np.corrcoef(fv[:-L], fv[L:])[0, 1]) for L in (1, 2, 5, 10, 21)]
    res["T3"]["linear"][n] = {"stages": stage_stats(f), "autocorr_1_2_5_10_21": ac,
                              "vol_bp_daily": float(1e4 * fv.std())}
    res["T3"]["square"][n] = {"stages": stage_stats(Fsq[:, k])}
# Factor-momentum style test: does a trailing mean of f predict tomorrow's f?
# Timing portfolio: hold sign/size of trailing mean over L days (causal: uses f up to t-1).
timing = {}
for L in (5, 21, 63, 126, 252, 504, 1008, 2016):
    pnl = np.full(T, np.nan)
    for t in range(253 + 21, T):
        lo = max(253, t - L); w = np.nanmean(F[lo:t], axis=0)
        pnl[t] = (w / np.linalg.norm(w)) @ F[t]
    timing[L] = stage_stats(pnl)
res["T3"]["trailing_mean_timing_by_lookback"] = timing
# Expanding-window (all history) for reference
pnl = np.full(T, np.nan)
for t in range(253 + 21, T):
    w = np.nanmean(F[253:t], axis=0); pnl[t] = (w / np.linalg.norm(w)) @ F[t]
res["T3"]["expanding_mean_timing"] = stage_stats(pnl)

# Payoff decay: cross-sectional IC of X[t-1] with residual return h-1 days later.
decay = {}
for h in (1, 2, 5, 10, 20, 40, 60, 120):
    ics = np.zeros((T, 13)) * np.nan
    for t in range(253, T - h + 1, 3):
        Z = zscore_panel(X[t - 1]); e = E[t + h - 1]; e = (e - e.mean()) / e.std()
        ics[t] = Z.T @ e / N
    decay[h] = {n: float(1e3 * np.nanmean(ics[:, k])) for k, n in enumerate(NAMES)}
res["T3"]["ic_x1000_by_lag_h"] = decay

with open(f"{OUT}/structure.json", "w") as fh:
    json.dump(res, fh, indent=1, default=float)
print(json.dumps(res["T1"], indent=1, default=float))
print(json.dumps(res["T2"], indent=1, default=float)[:3000])
