"""Diagnostic (features + realized returns, descriptive): what co-movement is left in
u[t] = e[t] - D[t-1] f[t] after the market (raw causal beta) and the 26 characteristic factors?

Reports: variance share of top-k PCs of u (full sample and causal rolling), a Marchenko-Pastur
noise reference, and the in-sample / bias-corrected max Sharpe of the top-k PC returns.
python research/v3/residual_structure.py --data DIR
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
U = np.zeros((T, N)); Fr = np.zeros((T, 26))
for t in range(253, T):
    D = E.basis(X[t - 1]); e = R[t] - beta[t] * m[t]; e = e - e.mean()
    f = np.linalg.solve(D.T @ D / N + 1e-10 * np.eye(26), D.T @ e / N); Fr[t] = f; U[t] = e - D @ f
u = U[253:]; n = len(u)
C = u.T @ u / n
ev, Q = np.linalg.eigh(C); ev, Q = ev[::-1], Q[:, ::-1]
mp_edge = (1 + np.sqrt(N / n)) ** 2 * ev.mean()
out = {"days": n, "share_top_k": {k: float(ev[:k].sum() / ev.sum()) for k in (1, 3, 5, 10, 20, 50)},
       "n_eigs_above_mp_edge": int((ev > mp_edge).sum()), "top10_over_mp_edge": (ev[:10] / mp_edge).round(2).tolist()}
# PC returns (full-sample loadings: look-ahead, descriptive only) and their Sharpe
def maxsharpe(P):
    mu = P.mean(0); S = np.cov(P.T); k = P.shape[1]
    s2 = float(mu @ np.linalg.solve(S, mu)) * 252
    adj = max(s2 * (len(P) - k - 2) / len(P) - k * 252 / len(P), 0)  # standard small-sample correction (annualized)
    return float(np.sqrt(s2)), float(np.sqrt(adj))
for k in (5, 10, 20):
    P = u @ Q[:, :k]
    out[f"pc{k}_max_sharpe_insample_and_corrected"] = maxsharpe(P)
out["pc_individual_ann_sharpe_top10"] = [round(float(np.sqrt(252) * c.mean() / c.std()), 2) for c in (u @ Q[:, :10]).T]
# causal: loadings from rows before each 252-day block, applied to the next block
causal = []
for s in range(1008, n, 252):
    W = u[:s][-1008:]; ev2, Q2 = np.linalg.eigh(W.T @ W / len(W)); Q2 = Q2[:, ::-1][:, :10]
    blk = u[s:s + 252]; causal.append(blk @ Q2)
P = np.vstack(causal)
out["causal_pc10_share_of_u_variance"] = float((P ** 2).sum() / (u[1008:] ** 2).sum())
out["causal_pc10_individual_ann_sharpe"] = [round(float(np.sqrt(252) * c.mean() / c.std()), 2) for c in P.T]
print(json.dumps(out, indent=1))
