"""Factor-level view: is the edge in *how* the characteristic factors are combined?

f[t] (26,) = cross-sectional regression slopes of residual returns e[t] on the
standardized day t-1 basis [Z, centered Z^2] (the C09 basis). These are the
returns of unit-exposure characteristic portfolios. No trading costs here.

A strategy chooses factor exposures h[t] from information before t; its
factor-level P&L is h[t] @ f[t]. Compare:
  mean      h = gamma_hat                     (premium estimate, raw)
  diag      h = Cx @ gamma_hat                (what a diagonal-risk optimizer
                                                approximately delivers from mu = Z gamma)
  mv        h = (F_hat + d I)^-1 gamma_hat    (mean-variance in factor space)
gamma_hat = exponentially weighted mean of past f; F_hat = EW covariance.
"""
import json

import numpy as np

from common import STAGES, load, causal_betas, residuals, zscore_panel, sharpe


def basis(panel):
    c = panel - panel.mean(axis=0)
    z = np.clip(c / np.maximum(np.sqrt(np.mean(c * c, axis=0)), 1e-12), -4, 4)
    z -= z.mean(axis=0)
    s = z * z; s = (s - s.mean(axis=0)) / np.sqrt(2)
    return np.hstack([z, s])



def main():
    global T
    R, X, _ = load()
    T, N = R.shape
    beta, m = causal_betas(R)
    E = residuals(R, beta, m)
    F = np.full((T, 26), np.nan); Cx = np.full((T, 26, 26), np.nan); R2 = np.full(T, np.nan)
    for t in range(2, T):
        D = basis(np.asarray(X[t - 1], dtype=np.float64)); e = E[t] - E[t].mean()
        G = D.T @ D / N
        F[t] = np.linalg.solve(G + 1e-8 * np.eye(26), D.T @ e / N); Cx[t] = G
        fit = D @ F[t]; R2[t] = fit @ fit / (e @ e)
    np.save("out/F26.npy", F)
    print("mean daily R2, 26-col basis:", round(float(np.nanmean(R2[253:])), 4))


    def ew_stats(F, hl_mean, hl_cov, start=21):
        """Causal EW mean/cov of F rows < t, starting at row 2."""
        a_m = 2 ** (-1 / hl_mean); a_c = 2 ** (-1 / hl_cov)
        k = F.shape[1]
        mu = np.zeros(k); w_m = 0.0
        S1 = np.zeros(k); S2 = np.zeros((k, k)); w_c = 0.0
        mus = np.full((T, k), np.nan); covs = np.full((T, k, k), np.nan)
        for t in range(3, T):
            f = F[t - 1]
            mu = a_m * mu + f; w_m = a_m * w_m + 1
            S1 = a_c * S1 + f; S2 = a_c * S2 + np.outer(f, f); w_c = a_c * w_c + 1
            if t - 2 >= start:
                mus[t] = mu / w_m
                mbar = S1 / w_c; covs[t] = S2 / w_c - np.outer(mbar, mbar)
        return mus, covs


    res = {}
    cols = {"linear13": slice(0, 13), "all26": slice(0, 26)}
    for hl_mean in (252, 1008, 1e9):
        mus, covs = ew_stats(F, hl_mean, 252)
        for cname, sl in cols.items():
            k = sl.stop - sl.start
            for rule in ("mean", "diag", "mv"):
                pnl = np.full(T, np.nan)
                for t in range(253, T):
                    g = mus[t, sl]
                    if rule == "mean":
                        h = g
                    elif rule == "diag":
                        h = Cx[t, sl, sl] @ g
                    else:
                        C = covs[t, sl, sl]
                        h = np.linalg.solve(C + 0.1 * np.trace(C) / k * np.eye(k), g)
                    pnl[t] = h @ F[t, sl] / np.sqrt(h @ h)
                key = f"hl{int(min(hl_mean, 99999))}_{cname}_{rule}"
                res[key] = {s: round(sharpe(pnl[a:b]), 2) for s, (a, b) in STAGES.items()}
                res[key]["all"] = round(sharpe(pnl[253:]), 2)
                print(key, res[key], flush=True)
    json.dump(res, open("out/factor_level.json", "w"), indent=1)


if __name__ == '__main__':
    main()
