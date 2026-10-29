"""Wave 4 Block 1: incremental IC over F2 of signals F2 does not use (WAVE4_PLAN_20261029.md).
python research/v3/wave4_newinfo.py --data DIR"""
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
import strategy  # noqa: E402,F401
from model_v3 import engine as E  # noqa: E402
from model_v3.policy import f2_forecast  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
cost = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
T, N = R.shape
F2 = f2_forecast(R, X, E.CONFIG)
beta, m = E.causal_betas(R, 252)
res = R - beta * m[:, None]
Y = np.zeros((T, N))
for t in range(253, T):
    y = res[t] - res[t].mean(); Y[t] = y / max(y.std(), 1e-12)
std = lambda P: E._standardize(np.ascontiguousarray(P), 4.0)
z = lambda v: E._zcol(v, 4.0)
t0 = 1008; oos = np.arange(t0, T)
S = {k: np.zeros((T, N)) for k in ("cost", "dX1", "dX21", "factor_lag1", "market_lag1")}

# 1. cost, static
S["cost"][:] = z(cost)

# 2. characteristic changes, causal expanding ridge (pairs: features for decision s, outcome Y[s], s < t)
for key, L in (("dX1", 1), ("dX21", 21)):
    G = np.zeros((13, 13)); h = np.zeros(13); n = 0
    for t in range(253 + L, T):
        Dt = std(X[t - 1] - X[t - 1 - L])
        if n >= 126:
            S[key][t] = Dt @ np.linalg.solve(G / n + 0.1 * np.eye(13), h / n)
        G += Dt.T @ Dt / N; h += Dt.T @ Y[t] / N; n += 1           # outcome t is used only from decision t+1 on

# 3. factor lead-lag: f[s] from res[s] on design(X[s-1], beta[s]); phi_k from pairs (f[s-1], f[s]), s < t
def design(t):
    return np.hstack([E.basis(X[t - 1]), z(beta[t])[:, None]])
f = np.zeros((T, 27))
for s in range(253, T):
    D = design(s); e = res[s] - res[s].mean()
    f[s] = np.linalg.solve(D.T @ D / N + 1e-10 * np.eye(27), D.T @ e / N)
num = np.zeros(27); den = np.zeros(27)
for t in range(255, T):
    s = t - 1                                                     # newest complete pair (f[s-1], f[s]), s = t-1
    num += f[s] * f[s - 1]; den += f[s - 1] ** 2
    if t >= 400:
        S["factor_lag1"][t] = design(t) @ ((num / den) * f[t - 1])

# 4. market lag-1: b_i from pairs (m[s-1], res[s]), s < t
num = np.zeros(N); den = 0.0
for t in range(255, T):
    s = t - 1
    num += res[s] * m[s - 1]; den += m[s - 1] ** 2
    if t >= 400:
        S["market_lag1"][t] = (num / den) * m[t - 1]

half = len(oos) // 2
def stats(series):
    x = np.array(series)
    return {"ic_mean": float(x.mean()), "ic_sharpe": float(np.sqrt(252) * x.mean() / x.std()),
            "first_half": float(np.sqrt(252) * x[:half].mean() / x[:half].std()),
            "second_half": float(np.sqrt(252) * x[half:].mean() / x[half:].std())}
out = {}
for k, P in S.items():
    alone, inc = [], []
    for t in oos:
        p = P[t] - P[t].mean(); g = F2[t] - F2[t].mean()
        if p.std() < 1e-15:
            alone.append(0.0); inc.append(0.0); continue
        pr = p - g * (g @ p) / max(g @ g, 1e-300)
        alone.append(np.corrcoef(p, Y[t])[0, 1]); inc.append(np.corrcoef(pr, Y[t])[0, 1])
    out[k] = {"alone": stats(alone), "incremental_over_F2": stats(inc)}
    i = out[k]["incremental_over_F2"]
    out[k]["passes_gate"] = bool(i["ic_sharpe"] >= 1.0 and i["first_half"] > 0 and i["second_half"] > 0)
    print(k, json.dumps(out[k]), flush=True)
json.dump(out, open(os.path.join(ROOT, "research", "v3", "wave4_newinfo.json"), "w"), indent=1)
