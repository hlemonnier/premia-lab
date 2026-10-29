"""ML incremental-signal test (research/v3/ML_PLAN_20261029.md).
python research/v3/ml_incremental.py --data DIR"""
import argparse, json, os, sys, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
import strategy  # noqa: E402,F401  (configures the engine)
from model_v3 import engine as E  # noqa: E402
from model_v3.policy import f2_forecast  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
T, N = R.shape
t_start = time.time()
F2 = f2_forecast(R, X, E.CONFIG)
beta, m = E.causal_betas(R, 252)
res = R - beta * m[:, None]
cs = np.zeros((T + 1, N)); np.cumsum(res, axis=0, out=cs[1:])
z = lambda v: E._zcol(v, 4.0)
FEAT = np.zeros((T, N, 17), dtype=np.float32); Y = np.zeros((T, N), dtype=np.float32)
for t in range(253, T):
    Zc = E._standardize(np.ascontiguousarray(X[t - 1]), 4.0)
    FEAT[t, :, :13] = Zc; FEAT[t, :, 13] = z(beta[t])
    FEAT[t, :, 14] = z(cs[t] - cs[t - 5]); FEAT[t, :, 15] = z(cs[t] - cs[t - 21]); FEAT[t, :, 16] = z(cs[t - 21] - cs[t - 252])
    y = res[t] - res[t].mean(); Y[t] = y / max(y.std(), 1e-12)
print(f"features built in {time.time() - t_start:.0f}s", flush=True)

t0, step = 1008, 252
preds = {"GB": np.full((T, N), np.nan), "NN": np.full((T, N), np.nan)}
for r0 in range(t0, T, step):
    r1 = min(r0 + step, T)
    for name in preds:
        every = 3 if name == "GB" else 6
        days = np.arange(253, r0, every)              # target days strictly before the refit day
        Xtr = FEAT[days].reshape(-1, 17); ytr = Y[days].reshape(-1)
        if name == "GB":
            mdl = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=2000,
                                                l2_regularization=1.0, early_stopping=False, random_state=0)
        else:
            mdl = MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-3, learning_rate_init=1e-3, batch_size=4096,
                               max_iter=20, early_stopping=False, random_state=0)
        mdl.fit(Xtr, ytr)
        preds[name][r0:r1] = mdl.predict(FEAT[r0:r1].reshape(-1, 17)).reshape(r1 - r0, N)
    print(f"refit at {r0} done ({time.time() - t_start:.0f}s)", flush=True)

oos = np.arange(t0, T); half = len(oos) // 2
ic = lambda p, y: np.corrcoef(p, y)[0, 1]
def icsr(series):
    s = np.array(series); return {"ic_mean": float(s.mean()), "ic_sharpe": float(np.sqrt(252) * s.mean() / s.std()),
                                  "first_half": float(np.sqrt(252) * s[:half].mean() / s[:half].std()),
                                  "second_half": float(np.sqrt(252) * s[half:].mean() / s[half:].std())}
out = {"F2": icsr([ic(F2[t], Y[t]) for t in oos])}
for name, P in preds.items():
    inc, corr = [], []
    for t in oos:
        f = F2[t] - F2[t].mean(); p = P[t] - P[t].mean()
        pr = p - f * (f @ p) / max(f @ f, 1e-300)
        inc.append(ic(pr, Y[t])); corr.append(ic(p, f))
    out[name] = {"alone": icsr([ic(P[t], Y[t]) for t in oos]), "incremental_over_F2": icsr(inc), "mean_corr_with_F2": float(np.mean(corr))}
    out[name]["passes_gate"] = bool(out[name]["incremental_over_F2"]["ic_sharpe"] >= 1.0 and out[name]["incremental_over_F2"]["first_half"] > 0
                                    and out[name]["incremental_over_F2"]["second_half"] > 0)
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(ROOT, "research", "v3", "ml_incremental.json"), "w"), indent=1)
