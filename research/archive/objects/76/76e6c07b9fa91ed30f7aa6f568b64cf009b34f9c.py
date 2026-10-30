"""Diagnostic: persistence of the 27 daily factor returns (26 basis + beta column), cross-sectional
OLS on X[t-1] of market-residual returns. For horizons H, the correlation across factors-and-time
of non-overlapping past-H mean vs next-H mean (pooled over factors, each factor demeaned by its
full-sample mean -> 'premium variation' persistence; and raw). Descriptive, full sample.
python research/v3/premia_persistence.py --data DIR
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
from model_v3 import engine as E  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
R = pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64)
X = pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13)
T, N = R.shape
beta, m = E.causal_betas(R, 252)
F = np.zeros((T, 27))
for t in range(253, T):
    D = np.hstack([E.basis(X[t - 1]), E._zcol(beta[t], 4.0)[:, None]]); e = R[t] - beta[t] * m[t]; e = e - e.mean()
    F[t] = np.linalg.solve(D.T @ D / N + 1e-10 * np.eye(27), D.T @ e / N)
F = F[253:]
out = {"factor_ann_sharpe": (np.sqrt(252) * F.mean(0) / F.std(0)).round(2).tolist()}
for H in (21, 63, 126, 252, 504):
    k = len(F) // H; B = F[:k * H].reshape(k, H, 27).mean(1)
    past, nxt = B[:-1], B[1:]
    raw = [np.corrcoef(past[:, j], nxt[:, j])[0, 1] for j in range(27)]
    # how much of the next-H mean variance is predictable from the past-H mean beyond the constant
    out[f"H{H}"] = {"blocks": k, "mean_autocorr_of_block_means": round(float(np.mean(raw)), 3),
                    "median": round(float(np.median(raw)), 3), "n_positive": int(np.sum(np.array(raw) > 0)),
                    "noise_se_approx": round(1 / np.sqrt(k - 1), 3)}
print(json.dumps(out, indent=1))
