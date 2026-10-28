"""C09 forecast family + characteristic factor risk model (research module).

Forecast: C09's exponentially weighted ridge learner on the 13 standardized
characteristics and their centered squares, optionally with a trailing-beta
feature and decorrelated prediction (see explore/variants.py).

Rebalance: positions for tomorrow from a risk model whose loadings are today's
characteristic basis D (the same 26 columns), so

    Sigma = diag(d) + D F D'.

F is an exponentially weighted covariance of daily characteristic factor
returns f_s = argmin ||e_s - D_{s-1} f|| (e_s: market-residual return with beta
estimated before s). d is an EW variance of what those factors leave
unexplained, shrunk toward its median. All state is built from
returns/characteristics through today only, one day at a time.
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/home/claude/explore")
sys.path.insert(0, "/home/claude/explore/v2")
sys.path.insert(0, "/home/claude/continual-research-takehome/handoff")
from model import strategy as engine  # noqa: E402
from factor_allocator import allocate_factor  # noqa: E402
import variants as V  # noqa: E402

CONFIG = {
    "forecast": dict(beta_feature=True, decorrelate=False),
    "risk_aversion": 1000.0, "cost_horizon": 20.0, "weight_cap": 0.01, "gross_cap": 1.0,
    "factor_half_life": 126.0, "specific_half_life": 126.0, "specific_shrinkage": 0.2,
    "variance_floor": 1e-6, "beta_window": 252, "factor_shrinkage": 0.0,
    "factor_risk_scale": 1.0,
}


def configure(**kw):
    global _STATE
    for k, v in kw.items():
        if k == "forecast":
            CONFIG["forecast"] = {**CONFIG["forecast"], **v}
        else:
            assert k in CONFIG, k
            CONFIG[k] = v
    _STATE = None


def basis(panel):
    return V.basis_additive(np.asarray(panel, dtype=np.float64))


def forecast(returns_history, characteristics_history):
    return V.make_forecast(**CONFIG["forecast"])(returns_history, characteristics_history)


def _beta_before(R, s, window):
    """Market betas for day s estimated from rows [s-window, s)."""
    lo = max(0, s - window); W = R[lo:s]
    if len(W) < 20:
        return np.ones(R.shape[1])
    c = W - W.mean(axis=0); m = W.mean(axis=1); m = m - m.mean()
    mv = m @ m
    return np.ones(R.shape[1]) if mv <= 1e-12 * len(W) else (m @ c) / mv


class RiskState:
    """Incremental characteristic-factor risk model. `upto` = days absorbed."""

    def __init__(self, n, k, cfg):
        self.cfg = cfg; self.upto = 1
        self.aF = 2 ** (-1 / cfg["factor_half_life"]); self.aS = 2 ** (-1 / cfg["specific_half_life"])
        self.S2 = np.zeros((k, k)); self.wF = 0.0
        self.U2 = np.zeros(n); self.wS = 0.0
        self.warm = {}

    def absorb(self, R, X, s):
        """Use return row s and characteristics row s-1 (both published by close of s)."""
        D = basis(X[s - 1])
        beta = _beta_before(R, s, self.cfg["beta_window"])
        e = R[s] - beta * R[s].mean(); e = e - e.mean()
        G = D.T @ D / len(e)
        f = np.linalg.solve(G + 1e-10 * np.eye(G.shape[0]), D.T @ e / len(e))
        u = e - D @ f
        self.S2 = self.aF * self.S2 + np.outer(f, f); self.wF = self.aF * self.wF + 1
        self.U2 = self.aS * self.U2 + u * u; self.wS = self.aS * self.wS + 1
        self.upto = s + 1

    def model(self):
        F = self.S2 / self.wF
        sh = self.cfg["factor_shrinkage"]
        if sh:
            F = (1 - sh) * F + sh * np.diag(np.diag(F))
        ev, Q = np.linalg.eigh(0.5 * (F + F.T))
        L = Q * np.sqrt(np.maximum(ev, 0.0) * self.cfg["factor_risk_scale"])
        d = self.U2 / self.wS
        d = (1 - self.cfg["specific_shrinkage"]) * d + self.cfg["specific_shrinkage"] * np.median(d)
        return L, np.maximum(d, self.cfg["variance_floor"])


_STATE = None
DIAG = {}


def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    global _STATE
    R = np.ascontiguousarray(returns_history, dtype=np.float64)
    X = characteristics_history
    T, n = R.shape
    cfg = CONFIG
    if _STATE is None or _STATE.upto > T:
        _STATE = RiskState(n, 26, cfg)
    while _STATE.upto < T:                     # absorb rows up to and including today
        _STATE.absorb(R, X, _STATE.upto)
    L, d = _STATE.model()
    Dnow = basis(X[T - 1])                     # today's characteristics: loadings for tomorrow
    beta, _ = engine._risk_estimates(R, {**engine.CONFIG, "risk_window": 252, "risk_min_days": 20})
    w = allocate_factor(expected_returns, held_positions, d, Dnow, L, beta,
                        np.asarray(trading_costs) / cfg["cost_horizon"], cfg["risk_aversion"],
                        cfg["weight_cap"], warm=_STATE.warm)
    gross = np.abs(w).sum()
    scale = min(1.0, cfg["gross_cap"] / gross) if gross else 1.0
    DIAG.update(pre_gross=gross, scale=scale)
    return w * scale
