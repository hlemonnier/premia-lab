"""Does a richer per-characteristic shape (or interactions) raise the attainable Sharpe?

Same construction as research/v2/ceiling.py (joint daily cross-sectional regression of
market-residual returns on the design of day t-1; bias-corrected hindsight max Sharpe; causal
expanding-mean factor timer, no costs), for several candidate bases:
  B27      V2/F2 design: 13 z, 13 centered z^2, beta
  +cube    B27 + 13 centered z^3
  +abs     B27 + 13 centered |z|
  +tails   B27 + 26 one-sided hinges max(z-1,0), max(-z-1,0) (centered)
  +grpint  B27 + 24 within-group pairwise products (tempers 4, quarks 6, elves 3)
  +allint  B27 + 78 pairwise products
Descriptive; all rows are already exposed. python research/v3/ceiling_shapes.py --data DIR
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
groups = [range(0, 4), range(4, 10), range(10, 13)]
gpairs = [(i, j) for g in groups for i in g for j in g if i < j]
apairs = [(i, j) for i in range(13) for j in range(13) if i < j]
c = lambda M: M - M.mean(0)
def extra(z, kind):
    if kind == "cube": return c(z ** 3)
    if kind == "abs": return c(np.abs(z))
    if kind == "tails": return np.hstack([c(np.maximum(z - 1, 0)), c(np.maximum(-z - 1, 0))])
    if kind == "grpint": return c(np.stack([z[:, i] * z[:, j] for i, j in gpairs], 1))
    if kind == "allint": return c(np.stack([z[:, i] * z[:, j] for i, j in apairs], 1))
kinds = ["cube", "abs", "tails", "grpint", "allint"]
F = {k: [] for k in ["B27"] + kinds}
for t in range(253, 3779):
    z = E._standardize(np.ascontiguousarray(X[t - 1]), 4.0)
    base = np.hstack([E.basis(X[t - 1]), E._zcol(beta[t], 4.0)[:, None]])
    e = R[t] - beta[t] * m[t]; e = e - e.mean()
    for k in F:
        D = base if k == "B27" else np.hstack([base, extra(z, k)])
        F[k].append(np.linalg.lstsq(D, e, rcond=None)[0])
def ceiling(Fs):
    n, k = Fs.shape; mu = Fs.mean(0); S = np.cov(Fs.T)
    th2 = mu @ np.linalg.solve(S, mu); adj = max(th2 * (n - k - 2) / n - k / n, 0.0)
    return {"k": k, "sample": round(float(np.sqrt(252 * th2)), 3), "bias_corrected": round(float(np.sqrt(252 * adj)), 3)}
def timer(Fs, start=252):
    pn = []
    for i in range(start, len(Fs)):
        H = Fs[:i]; mu = H.mean(0); S = np.cov(H.T); S = 0.5 * S + 0.5 * np.diag(np.diag(S))
        w = np.linalg.solve(S, mu); pn.append(w @ Fs[i] / np.sqrt(w @ S @ w))
    pn = np.array(pn); h = len(pn) // 2
    return {"all": round(float(np.sqrt(252) * pn.mean() / pn.std()), 3),
            "first_half": round(float(np.sqrt(252) * pn[:h].mean() / pn[:h].std()), 3),
            "second_half": round(float(np.sqrt(252) * pn[h:].mean() / pn[h:].std()), 3)}
out = {}
for k, v in F.items():
    v = np.array(v)
    out[k] = {"ceiling": ceiling(v), "causal_timer_no_costs": timer(v)}
    if k != "B27":
        ex = v[:, 27:]; out[k]["extra_factor_ann_sharpes"] = (np.sqrt(252) * ex.mean(0) / ex.std(0)).round(2).tolist()
    print(k, json.dumps(out[k]), flush=True)
json.dump(out, open(os.path.join(ROOT, "research/v3/ceiling_shapes.json"), "w"), indent=1)
