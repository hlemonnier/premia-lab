"""Is there predictive information beyond the level of yesterday's characteristics?

For each day t, candidate signals use rows < t only. Each candidate is
residualized cross-sectionally on the C09 basis of X[t-1] (26 cols), then its
rank IC with the *idiosyncratic* return u[t] = e[t] - D[t-1] f[t] (the part
not explained by contemporaneous characteristic-factor returns) and with e[t].
Reported: annualized Sharpe of the daily IC series (~ t-stat / sqrt(years)) and
mean IC x1000, by stage.
"""
import json

import numpy as np
from scipy.stats import rankdata

from common import NAMES, STAGES, load, causal_betas, residuals, sharpe
from factor_level import basis  # noqa: F401  (re-run is cheap; reuses F26 on disk)

R, X, costs = load()
T, N = R.shape
beta, m = causal_betas(R)
E = residuals(R, beta, m)
F = np.load("out/F26.npy")
D = np.zeros((T, N, 26), dtype=np.float32)
for t in range(1, T):
    D[t] = basis(np.asarray(X[t - 1], dtype=np.float64))  # D[t] = basis of X[t-1]
U = np.full((T, N), np.nan)
for t in range(2, T):
    U[t] = E[t] - E[t].mean() - D[t] @ F[t]
csE = np.zeros((T + 1, N)); np.cumsum(E, axis=0, out=csE[1:])
Uz = np.nan_to_num(U); csU = np.zeros((T + 1, N)); np.cumsum(Uz, axis=0, out=csU[1:])
csE2 = np.zeros((T + 1, N)); np.cumsum(E * E, axis=0, out=csE2[1:])


def past(cs, t, a, b):
    """sum over rows [t-a, t-b) (a > b >= 1): strictly before t."""
    return cs[t - b] - cs[t - a] if t - a >= 0 else None


def cands(t):
    out = {
        "rev_e_1d": past(csE, t, 1, 0),
        "rev_e_5d": past(csE, t, 5, 0),
        "mom_e_21_2": past(csE, t, 21, 1),
        "mom_e_252_21": past(csE, t, 252, 21),
        "rev_u_1d": past(csU, t, 1, 0),
        "rev_u_5d": past(csU, t, 5, 0),
        "mom_u_21_2": past(csU, t, 21, 1),
        "mom_u_252_21": past(csU, t, 252, 21),
        "idio_vol_63": np.sqrt(past(csE2, t, 63, 0)),
        "beta": beta[t],
        "cost": costs,
    }
    Xm1 = np.asarray(X[t - 1], dtype=np.float64)
    for lag in (1, 5, 21):
        dz = Xm1 - np.asarray(X[t - 1 - lag], dtype=np.float64)
        out[f"dX_sum_{lag}d"] = dz  # (N,13) handled below per characteristic
    return out


def resid(sig, Dt):
    coef, *_ = np.linalg.lstsq(Dt, sig - sig.mean(), rcond=None)
    return sig - sig.mean() - Dt @ coef


def ric(a, b):
    ra = rankdata(a); rb = rankdata(b)
    ra -= ra.mean(); rb -= rb.mean()
    return float(ra @ rb / np.sqrt((ra @ ra) * (rb @ rb)))


start = 300
names = None; ICu = {}; ICe = {}
for t in range(start, T):
    Dt = np.asarray(D[t], dtype=np.float64)
    c = cands(t)
    flat = {}
    for k, v in c.items():
        if v is None:
            continue
        if v.ndim == 2:
            for j, n in enumerate(NAMES):
                flat[f"{k}:{n}"] = v[:, j]
        else:
            flat[k] = v
    for k, v in flat.items():
        r = resid(v, Dt)
        ICu.setdefault(k, np.full(T, np.nan))[t] = ric(r, U[t])
        ICe.setdefault(k, np.full(T, np.nan))[t] = ric(r, E[t])

res = {}
for k in ICu:
    res[k] = {}
    for s, (a, b) in {"all": (start, 3779), **STAGES}.items():
        a = max(a, start)
        res[k][s] = {"ic_sr_u": round(sharpe(ICu[k][a:b]), 2), "ic_u_x1000": round(1e3 * np.nanmean(ICu[k][a:b]), 2),
                     "ic_sr_e": round(sharpe(ICe[k][a:b]), 2)}
json.dump(res, open("out/alpha_sources.json", "w"), indent=1)
order = sorted(res, key=lambda k: -abs(res[k]["all"]["ic_sr_u"]))
print(f"{'signal':24s} {'IC-SR(u) all':>12} {'disc':>6} {'val':>6} {'aud':>6} {'IC(u)x1e3':>10} {'IC-SR(e)':>9}")
for k in order[:30]:
    r = res[k]
    print(f"{k:24s} {r['all']['ic_sr_u']:12.2f} {r['discovery']['ic_sr_u']:6.2f} {r['validation']['ic_sr_u']:6.2f} {r['audit']['ic_sr_u']:6.2f} {r['all']['ic_u_x1000']:10.2f} {r['all']['ic_sr_e']:9.2f}")
