"""ADAPTIVE_PREMIUM_PLAN.md gate 1 (forecast loss) and gate 3 (causality) for the adaptive model.

python research/v2/adaptive_gate.py --data DIR
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
import strategy as V2  # noqa: E402
from model_v2 import engine  # noqa: E402
STAGES = {"discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}


def block_ci(x, L, draws=2000, seed=20261027):
    n = len(x); rng = np.random.default_rng(seed); nb = int(np.ceil(n / L))
    st = rng.integers(0, n - L + 1, size=(draws, nb)); idx = (st[:, :, None] + np.arange(L)).reshape(draws, -1)[:, :n]
    v = x[idx].mean(axis=1); return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args()
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
beta, m = engine.causal_betas(R); E = R - beta * m[:, None]       # V2's labels (raw-beta residuals)
engine.configure({**V2._CONFIG}); p_fixed = engine.forecast(R, X)
engine.configure({**V2._CONFIG, "premium_model": "adaptive"}); p_adapt = engine.forecast(R, X)
kappa = np.array(engine.KAPPA_PATH)
rows = np.arange(378, 3779)
def loss(P):
    return np.array([np.mean((E[t] - E[t].mean() - P[t]) ** 2) for t in rows])
lf, la = loss(p_fixed), loss(p_adapt); dl = la - lf
out = {"rows": [int(rows[0]), int(rows[-1])], "mean_loss_fixed": float(lf.mean()), "mean_loss_adaptive": float(la.mean()),
       "mean_diff_adaptive_minus_fixed": float(dl.mean()), "gate1_pass": bool(dl.mean() < 0),
       "block_ci_95": {L: block_ci(dl, L) for L in (21, 63, 126)},
       "stages": {s: float(dl[(rows >= lo) & (rows < hi)].mean()) for s, (lo, hi) in STAGES.items()},
       "kappa": {"first_active_row": int(kappa[kappa[:, 1] > 0, 0].min()) if np.any(kappa[:, 1] > 0) else None,
                 "mean": float(kappa[:, 1].mean()), "last": float(kappa[-1, 1]),
                 "quantiles_10_50_90": [float(q) for q in np.percentile(kappa[:, 1], [10, 50, 90])]},
       # implied R2 against the cross-sectionally demeaned label: 1 - loss/var
       "r2_fixed": float(1 - lf.mean() / np.mean([np.var(E[t]) for t in rows])),
       "r2_adaptive": float(1 - la.mean() / np.mean([np.var(E[t]) for t in rows]))}
# gate 3: causality of the adaptive forecast
base = p_adapt; rng = np.random.default_rng(7); ok = True
for cut in (400, 900, 1500, 3024, 3700):
    R2 = R.copy(); X2 = X.copy(); R2[cut:] = rng.normal(0, .03, R2[cut:].shape); X2[cut:] = rng.normal(0, 1, X2[cut:].shape)
    for lab, args in (("altered", (R2, X2)), ("altered_fortran", (np.asfortranarray(R2), np.asfortranarray(X2))), ("truncated", (R[:cut], X[:cut]))):
        o = engine.forecast(*args); up = cut if lab == "truncated" else cut + 1
        ok &= bool(np.array_equal(base[:up], o[:up]))
out["gate3_causality_pass"] = ok
np.save(os.path.join(ROOT, "research/v2/results/adaptive_kappa_path.npy"), kappa)
json.dump(out, open(os.path.join(ROOT, "research/v2/results/adaptive_gate.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
