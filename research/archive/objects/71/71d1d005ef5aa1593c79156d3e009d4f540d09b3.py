"""How much Sharpe can the characteristic directions support at all?

Daily factor returns f_t: joint cross-sectional regression of market-residual returns
(beta from rows < t) on the 27-column V2 design of day t-1 (26 basis columns + beta).
Ex-post maximum Sharpe sqrt(mu' S^-1 mu) on the full sample, with the standard
small-sample bias correction for the squared Sharpe of a k-asset tangency portfolio
(theta2_hat*(T-k-2)/T - k/T, daily units), by sub-period too. Before costs, perfect
hindsight on the means: an upper reference, not an achievable target.
Then: what a causal expanding-mean, shrunk-covariance factor timer achieves (no costs).
"""
import json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
from model_v2.engine import basis, causal_betas, _zcol  # noqa: E402
d = sys.argv[1]
R = np.ascontiguousarray(pd.read_csv(f"{d}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{d}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
T, N = R.shape
beta, m = causal_betas(R); E = R - beta * m[:, None]
F = np.full((T, 27), np.nan)
for t in range(253, T):
    D = np.hstack([basis(X[t - 1]), _zcol(beta[t], 4.0)[:, None]]); e = E[t] - E[t].mean()
    F[t] = np.linalg.lstsq(D, e, rcond=None)[0]
F = F[253:3779]
def ceiling(Fs):
    n, k = Fs.shape; mu = Fs.mean(0); S = np.cov(Fs.T)
    th2 = mu @ np.linalg.solve(S, mu)
    adj = max(th2 * (n - k - 2) / n - k / n, 0.0)
    return {"n": n, "k": k, "sample_max_sharpe": float(np.sqrt(252 * th2)), "bias_corrected_max_sharpe": float(np.sqrt(252 * adj))}
out = {"all27": ceiling(F), "linear13": ceiling(F[:, :13]), "26_no_beta": ceiling(F[:, :26]),
       "by_period_all27": {s: ceiling(F[a - 253:b - 253]) for s, (a, b) in {"discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}.items()},
       "first_half": ceiling(F[: len(F) // 2]), "second_half": ceiling(F[len(F) // 2:])}
# causal factor timer: expanding mean, covariance shrunk 50% to its diagonal, weights from rows < t
pn = []
for i in range(252, len(F)):
    H = F[:i]; mu = H.mean(0); S = np.cov(H.T); S = 0.5 * S + 0.5 * np.diag(np.diag(S))
    w = np.linalg.solve(S, mu); pn.append(w @ F[i] / np.sqrt(w @ S @ w))
pn = np.array(pn)
out["causal_factor_timer_no_costs_sharpe"] = float(np.sqrt(252) * pn.mean() / pn.std())
json.dump(out, open(os.path.join(ROOT, "research/v2/results/ceiling.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
