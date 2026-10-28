"""Score C09 and one-change variants with the unmodified supplied scorer.

All variants keep C09's portfolio (diagonal residual risk, scalar-dual allocator,
beta hedge, 1% caps, gross cap 1) unless the variant says otherwise. Only the
forecast changes. Every forecast is causal by construction: row t uses rows < t.

Usage: python variants.py NAME [NAME ...]   (or 'all')
"""
import importlib.util
import json
import os
import sys
import time
import types

import numpy as np

from common import GROUP_IDX, STAGES, load, causal_betas, residuals, sharpe

REPO = "/home/claude/continual-research-takehome"
OUT = "/home/claude/explore/out"
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, f"{REPO}/handoff")
from model import strategy as engine  # noqa: E402
from model.portfolio import allocate  # noqa: E402

spec = importlib.util.spec_from_file_location("score", f"{REPO}/source/Quant Research Take-Home/score.py")
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)

C09 = {
    'candidate_id': 'C09_additive_long_memory', 'basis': 'additive', 'alpha_half_life': 1008.0,
    'ridge': 0.1, 'min_training_days': 126, 'feature_clip': 4.0, 'risk_window': 252,
    'risk_min_days': 20, 'variance_shrinkage': 0.2, 'variance_floor': 1e-06,
    'risk_aversion': 1000.0, 'cost_horizon': 20.0, 'weight_cap': 0.01, 'gross_cap': 1.0,
}


# ----------------------------------------------------------------- bases
def _std(panel, clip=4.0):
    c = panel - panel.mean(axis=0)
    z = np.clip(c / np.maximum(np.sqrt(np.mean(c * c, axis=0)), 1e-12), -clip, clip)
    return z - z.mean(axis=0)


def _squares(z):
    s = z * z
    return (s - s.mean(axis=0)) / np.sqrt(2.0)


def basis_additive(panel):
    z = _std(panel)
    return np.hstack([z, _squares(z)])


def basis_groups(panel):
    """One composite per name group (mean of its standardized members), plus squares."""
    z = _std(panel)
    g = np.stack([z[:, ix].mean(axis=1) for ix in GROUP_IDX.values()], axis=1)
    g = _std(g)
    return np.hstack([g, _squares(g)])


def basis_groups_plus(panel):
    """Group composites + within-group deviations (13 linear) + group squares."""
    z = _std(panel)
    g = _std(np.stack([z[:, ix].mean(axis=1) for ix in GROUP_IDX.values()], axis=1))
    return np.hstack([z, g, _squares(g)])


BASES = {"additive": basis_additive, "groups": basis_groups, "groups_plus": basis_groups_plus}


# ----------------------------------------------------------------- learner
def make_forecast(basis="additive", horizon=1, half_life=1008.0, ridge=0.1, min_pairs=126,
                  neutralize_k=0, neutralize_window=252, neutralize_refresh=21,
                  reversal=False, beta_feature=False, decorrelate=False, rev_scale=1.0):
    """C09-style exponentially weighted ridge learner, generalized.

    Pair s: design D[s] = basis(X[s]); label = mean residual return over days
    s+1..s+horizon (residuals use betas estimated before each day). The pair
    is usable at forecast row t only if s + horizon <= t - 1. Row t predicts
    with D[t-1]. Optional: project predictions orthogonal to the top-k
    loadings of trailing residual returns (rows < t), refreshed periodically.
    """
    bfun = BASES[basis]

    def forecast(returns_history, characteristics_history):
        R = np.ascontiguousarray(returns_history, dtype=np.float64)  # canonical layout: reductions stay prefix-stable
        Xh = characteristics_history
        T, N = R.shape
        beta, m = causal_betas(R)
        E = residuals(R, beta, m)
        csE = np.zeros((T + 1, N)); np.cumsum(E, axis=0, out=csE[1:])
        decay = 2.0 ** (-1.0 / half_life)
        def zcol(v):
            v = v - v.mean(); v = np.clip(v / max(v.std(), 1e-12), -4, 4); return v - v.mean()

        def design(s):
            parts = [bfun(np.asarray(Xh[s], dtype=np.float64))]
            if reversal:
                parts.append(np.stack([zcol(csE[s + 1] - csE[max(s - 4, 0)]),
                                       zcol(csE[max(s - 4, 0)] - csE[max(s - 20, 0)])], axis=1))
            if beta_feature:
                parts.append(zcol(beta[s + 1])[:, None])
            return np.hstack(parts)

        D0 = design(0); w = D0.shape[1]
        gram = np.zeros((w, w)); mom = np.zeros(w); mass = 0.0; pairs = 0
        pred = np.zeros((T, N))
        designs = {}
        loadings = None
        for t in range(2, T):
            s = t - 1 - horizon  # newest pair that matures for row t
            if s >= 0:
                D = designs.pop(s) if s in designs else design(s)
                y = (csE[s + 1 + horizon] - csE[s + 1]) / horizon
                gram = decay * gram + D.T @ D / N
                mom = decay * mom + D.T @ y / N
                mass = decay * mass + 1.0; pairs += 1
            Dnow = design(t - 1)
            if horizon > 1:
                designs[t - 1] = Dnow
            if pairs >= min_pairs:
                coef = np.linalg.solve(gram / mass + ridge * np.eye(w), mom / mass)
                if reversal and rev_scale != 1.0:
                    nb = w - 2 - (1 if beta_feature else 0)  # reversal columns follow the basis
                    c2 = coef.copy(); c2[nb:nb + 2] *= rev_scale
                    p = Dnow @ c2
                else:
                    p = Dnow @ coef
                if decorrelate:
                    q = Dnow @ np.linalg.solve(Dnow.T @ Dnow / N + ridge * np.eye(w), coef)
                    p = q * (p.std() / max(q.std(), 1e-300))
                if neutralize_k:
                    if loadings is None or (t % neutralize_refresh == 0):
                        lo = max(0, t - neutralize_window)
                        W = E[lo:t] - E[lo:t].mean(axis=0)
                        W = W / np.maximum(W.std(axis=0), 1e-12)  # correlation-based loadings
                        _, _, vt = np.linalg.svd(W, full_matrices=False)
                        loadings = vt[:neutralize_k].T  # (N,k), orthonormal columns
                    p = p - loadings @ (loadings.T @ p)
                pred[t] = p
        return pred

    return forecast


# ----------------------------------------------------------------- strategies
def c09_engine():
    engine.configure(C09)
    return types.SimpleNamespace(forecast=engine.forecast, rebalance=engine.rebalance)


def custom(cost_horizon=None, **kw):
    engine.configure({**C09, **({"cost_horizon": cost_horizon} if cost_horizon else {})})
    return types.SimpleNamespace(forecast=make_forecast(**kw), rebalance=engine.rebalance)


def v2(**kw):
    sys.path.insert(0, "/home/claude/explore/v2")
    import strategy_v2 as S
    import importlib; importlib.reload(S)
    S.configure(**kw)
    return types.SimpleNamespace(forecast=S.forecast, rebalance=S.rebalance)


VARIANTS = {
    "C09_engine": lambda: c09_engine(),
    "C09_reimpl": lambda: custom(),
    "groups": lambda: custom(basis="groups"),
    "groups_plus": lambda: custom(basis="groups_plus"),
    "h5": lambda: custom(horizon=5),
    "h20": lambda: custom(horizon=20),
    "hl_252": lambda: custom(half_life=252.0),
    "hl_inf": lambda: custom(half_life=1e9),
    "neutral_k10": lambda: custom(neutralize_k=10),
    "neutral_k20": lambda: custom(neutralize_k=20),
    "cost_h60": lambda: custom(cost_horizon=60.0),
    "cost_h5": lambda: custom(cost_horizon=5.0),
    "reversal": lambda: custom(reversal=True),
    "beta_feat": lambda: custom(beta_feature=True),
    "decor": lambda: custom(decorrelate=True),
    # reversal decays in ~6 days of lag-1 IC; the allocator amortizes costs over
    # cost_horizon days, so scale its contribution by persistence / horizon.
    "rev_scaled_h20": lambda: custom(reversal=True, rev_scale=6 / 20),
    "rev_scaled_h60": lambda: custom(reversal=True, rev_scale=6 / 60, cost_horizon=60.0),
    "decor_beta": lambda: custom(decorrelate=True, beta_feature=True),
    "cost_h120": lambda: custom(cost_horizon=120.0),
    "cost_h250": lambda: custom(cost_horizon=250.0),
    "fr_beta": lambda: v2(),
    "fr_decor_beta": lambda: v2(forecast=dict(decorrelate=True)),
    "fr_plain": lambda: v2(forecast=dict(beta_feature=False)),
    "fr_beta_phi03": lambda: v2(factor_risk_scale=0.3),
    "fr_beta_phi01": lambda: v2(factor_risk_scale=0.1),
    "fr_beta_phi03_x5": lambda: v2(factor_risk_scale=0.3, risk_aversion=200.0, weight_cap=0.05, gross_cap=5.0),
}


def evaluate(name, strat, R, X, c):
    t0 = time.time()
    rows, fsec = score.run(strat, R, X, c)
    pr, cost, gross, mkt, rsec = rows.T
    net = pr - cost
    day = score.START + 1 + np.arange(len(rows))
    out = {"name": name, "forecast_s": round(fsec, 1), "rebalance_ms": round(1e3 * rsec.mean(), 2),
           "wall_s": round(time.time() - t0, 1)}
    for s, (a, b) in {"all": (253, 3779), **STAGES}.items():
        k = (day >= a) & (day < b)
        mc = mkt[k] - mkt[k].mean()
        out[s] = {"sharpe": round(sharpe(net[k]), 3), "gross_sharpe": round(sharpe(pr[k]), 3),
                  "ret_pct": round(100 * 252 * net[k].mean(), 2), "cost_pct": round(100 * 252 * cost[k].mean(), 3),
                  "beta": round(float(mc @ (net[k] - net[k].mean()) / (mc @ mc)), 4),
                  "gross": round(float(gross[k].mean()), 3)}
    np.save(f"{OUT}/net_{name}.npy", np.vstack([day, net, pr, cost, mkt]))
    return out


if __name__ == "__main__":
    R, X, c = load()
    X = np.ascontiguousarray(X, dtype=np.float64) if os.environ.get("X64") else X
    names = list(VARIANTS) if sys.argv[1:] == ["all"] else sys.argv[1:]
    for n in names:
        res = evaluate(n, VARIANTS[n](), R, X, c)
        with open(f"{OUT}/variant_{n}.json", "w") as fh:
            json.dump(res, fh, indent=1)
        print(json.dumps({k: res[k] for k in ("name", "all", "discovery", "validation", "audit")}), flush=True)
