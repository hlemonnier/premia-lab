"""Do better cross-sectional estimators raise the attainable Sharpe of the same 27 directions?

  OLS       current: equal-weight daily cross-sectional regression (as research/v2/ceiling.py)
  WLS       weights 1/d_i, d = causal EW(126) second moment of each stock's OLS residual (rows < t)
  RANK      characteristics rank-transformed to N(0,1) scores (Gu-Kelly-Xiu style) before basis
Reports bias-corrected hindsight ceiling and causal no-cost factor timer, plus the
cross-sectional dispersion of d. Descriptive. python research/v3/ceiling_estimators.py --data DIR
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
from statistics import NormalDist
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
from model_v3 import engine as E  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
R = pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64)
X = pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13)
T, N = R.shape
beta, m = E.causal_betas(R, 252)
icdf = np.array([NormalDist().inv_cdf((i + 0.5) / N) for i in range(N)])
def rankpanel(P):
    Z = np.empty_like(P)
    for k in range(P.shape[1]):
        Z[np.argsort(P[:, k]), k] = icdf
    return Z
kurt = float(np.mean([((lambda z: np.mean(z ** 4))((X[t] - X[t].mean(0)) / X[t].std(0))) for t in range(300, T, 100)]))
dec = 2 ** (-1 / 126); U2 = np.zeros(N); w = 0.0
F = {"OLS": [], "WLS": [], "RANK": []}; disp = []
for t in range(253, 3779):
    D = np.hstack([E.basis(X[t - 1]), E._zcol(beta[t], 4.0)[:, None]])
    Dr = np.hstack([E.basis(rankpanel(X[t - 1])), E._zcol(beta[t], 4.0)[:, None]])
    e = R[t] - beta[t] * m[t]; e = e - e.mean()
    f = np.linalg.lstsq(D, e, rcond=None)[0]; F["OLS"].append(f)
    F["RANK"].append(np.linalg.lstsq(Dr, e, rcond=None)[0])
    if w > 0:
        d = U2 / w; d = 0.8 * d + 0.2 * np.median(d); wt = 1 / d; disp.append(np.sqrt(d.max() / d.min()))
        Dw = D * wt[:, None]; F["WLS"].append(np.linalg.solve(D.T @ Dw, Dw.T @ e))
    else:
        F["WLS"].append(f)
    u = e - D @ f; U2 = dec * U2 + u * u; w = dec * w + 1
def ceiling(Fs):
    n, k = Fs.shape; mu = Fs.mean(0); S = np.cov(Fs.T)
    th2 = mu @ np.linalg.solve(S, mu); adj = max(th2 * (n - k - 2) / n - k / n, 0.0)
    return {"sample": round(float(np.sqrt(252 * th2)), 3), "bias_corrected": round(float(np.sqrt(252 * adj)), 3)}
def timer(Fs, start=252):
    pn = []
    for i in range(start, len(Fs)):
        H = Fs[:i]; mu = H.mean(0); S = np.cov(H.T); S = 0.5 * S + 0.5 * np.diag(np.diag(S))
        wv = np.linalg.solve(S, mu); pn.append(wv @ Fs[i] / np.sqrt(wv @ S @ wv))
    pn = np.array(pn); h = len(pn) // 2
    return {"all": round(float(np.sqrt(252) * pn.mean() / pn.std()), 3), "first_half": round(float(np.sqrt(252) * pn[:h].mean() / pn[:h].std()), 3),
            "second_half": round(float(np.sqrt(252) * pn[h:].mean() / pn[h:].std()), 3)}
out = {"mean_kurtosis_raw_characteristics": round(kurt, 2), "specific_vol_max_over_min_median_day": round(float(np.median(disp)), 2)}
for k, v in F.items():
    v = np.array(v); out[k] = {"ceiling": ceiling(v), "causal_timer_no_costs": timer(v)}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(ROOT, "research/v3/ceiling_estimators.json"), "w"), indent=1)
