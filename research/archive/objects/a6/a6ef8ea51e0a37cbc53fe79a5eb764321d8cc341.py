"""Characteristic basis, causal beta and risk-state helpers used by N0.

No standalone forecast/rebalance strategy is exposed by this module.
"""

import math
import numpy as np

CONFIG = {
    # forecast
    "alpha_half_life": 1008.0, "ridge": 0.1, "min_training_days": 126, "feature_clip": 4.0,
    # risk model
    "beta_window": 252, "factor_half_life": 126.0, "specific_half_life": 126.0,
    "specific_shrinkage": 0.2, "variance_floor": 1e-6, "factor_risk_scale": 0.3,
    "risk_beta_column": False,   # R27 experiment: add the forecast's beta column to the risk loadings
    "matched_diagonal": False,   # control: keep marginal variances d + diag(phi*D F D'), drop correlations
    "beta_shrinkage": False,     # correct betas toward the cross-sectional mean by a causally estimated eta
    "beta_target": 0.0,          # explicit market exposure: hedge constraint b'w = beta_target
    "premium_model": "fixed",    # "fixed": one EW learner (alpha_half_life); "adaptive": stable + learned deviation
    "adaptive_half_life": 252.0, # half-life of the dynamic learner in the adaptive model
    # allocation
    "risk_aversion": 1000.0, "cost_horizon": 20.0, "weight_cap": 0.01, "gross_cap": 1.0,
}

def _standardize(v, clip):
    c = v - v.mean(axis=0)
    z = np.clip(c / np.maximum(np.sqrt(np.mean(c * c, axis=0)), 1e-12), -clip, clip)
    return z - z.mean(axis=0)

def basis(panel, clip=4.0):
    """13 standardized characteristics and their centered squares, from one published panel.

    The panel is canonicalized to C-contiguous float64 first, so results do not depend on
    the caller's memory layout (reductions follow one accumulation order)."""
    z = _standardize(np.ascontiguousarray(panel, dtype=np.float64), clip)
    s = z * z
    return np.hstack([z, (s - s.mean(axis=0)) / math.sqrt(2.0)])

def _zcol(v, clip):
    """Centered, clipped standardization of one cross-sectional vector (as in the forecast)."""
    v = v - v.mean(); v = np.clip(v / max(v.std(), 1e-12), -clip, clip)
    return v - v.mean()

def risk_loadings(panel, beta, cfg):
    """Risk loading matrix: the 26-column basis, plus the beta column when configured."""
    D = basis(panel, cfg["feature_clip"])
    return np.hstack([D, _zcol(beta, cfg["feature_clip"])[:, None]]) if cfg["risk_beta_column"] else D

def causal_betas(R, window=252, min_days=20):
    """beta[t] uses return rows [t-window, t) only; 1 before min_days."""
    T, N = R.shape
    m = R.mean(axis=1)

    def csum(a):
        out = np.zeros((T + 1,) + a.shape[1:]); np.cumsum(a, axis=0, out=out[1:]); return out
    Sm, Smm, Sr, Smr = csum(m), csum(m * m), csum(R), csum(R * m[:, None])
    beta = np.ones((T, N))
    for t in range(min_days, T):
        lo = max(0, t - window); n = t - lo
        mm = (Smm[t] - Smm[lo]) / n - ((Sm[t] - Sm[lo]) / n) ** 2
        if mm > 1e-12:
            beta[t] = ((Smr[t] - Smr[lo]) / n - (Sm[t] - Sm[lo]) / n * (Sr[t] - Sr[lo]) / n) / mm
    return beta, m

def _window_beta(R, window=252, min_days=20):
    """Betas from the last `window` rows of R (all of which are already published)."""
    W = R[-window:]
    if len(W) < min_days:
        return np.ones(R.shape[1])
    c = W - W.mean(axis=0); m = W.mean(axis=1); m = m - m.mean()
    mv = m @ m
    return np.ones(R.shape[1]) if mv <= 1e-12 * len(W) else (m @ c) / mv

class _EtaTracker:
    """Causal beta-shrinkage intensity. On grid dates s = window, window+step, ... a pair is
    complete once s + window <= t: regress realized betas over rows [s, s+window) on betas
    estimated from rows [s-window, s). eta_t = 1 - mean slope over completed pairs, else 0."""

    def __init__(self, window=252, step=21):
        self.window, self.step, self.next_s, self.slopes = window, step, window, []

    def eta(self, R, t):
        while self.next_s + self.window <= t:
            s = self.next_s
            pre = _window_beta(R[:s], self.window); post = _window_beta(R[s:s + self.window], self.window)
            x = pre - pre.mean()
            self.slopes.append(float(x @ (post - post.mean()) / (x @ x)))
            self.next_s += self.step
        return 1.0 - float(np.mean(self.slopes)) if self.slopes else 0.0

def _correct(beta, eta):
    return (1.0 - eta) * beta + eta * beta.mean()

class _RiskState:
    def __init__(self, n, k, cfg):
        self.cfg = cfg; self.upto = 1
        self.aF = 2 ** (-1 / cfg["factor_half_life"]); self.aS = 2 ** (-1 / cfg["specific_half_life"])
        self.S2 = np.zeros((k, k)); self.wF = 0.0
        self.U2 = np.zeros(n); self.wS = 0.0
        self.warm = {}
        self.eta = _EtaTracker(cfg["beta_window"])

    def absorb(self, R, X, s):
        """Use return row s and characteristics row s-1, both published by the close of day s."""
        beta = _window_beta(R[:s], self.cfg["beta_window"])
        D = risk_loadings(X[s - 1], beta, self.cfg)        # beta column (if any) uses raw betas, as the forecast does
        if self.cfg["beta_shrinkage"]:
            beta = _correct(beta, self.eta.eta(R, s))
        e = R[s] - beta * R[s].mean(); e = e - e.mean()
        G = D.T @ D / len(e)
        f = np.linalg.solve(G + 1e-10 * np.eye(G.shape[0]), D.T @ e / len(e))
        u = e - D @ f
        self.S2 = self.aF * self.S2 + np.outer(f, f); self.wF = self.aF * self.wF + 1
        self.U2 = self.aS * self.U2 + u * u; self.wS = self.aS * self.wS + 1
        self.upto = s + 1

    def model(self):
        F = self.S2 / self.wF
        ev, Q = np.linalg.eigh(0.5 * (F + F.T))
        L = Q * np.sqrt(np.maximum(ev, 0.0) * self.cfg["factor_risk_scale"])
        d = self.U2 / self.wS
        sh = self.cfg["specific_shrinkage"]
        d = (1 - sh) * d + sh * np.median(d)
        return L, np.maximum(d, self.cfg["variance_floor"])

def _final_check(w, beta, target, cfg):
    """Post-processing certificate on the book actually returned."""
    tol = 1e-9 * max(1.0, float(np.abs(beta).sum()) * cfg["weight_cap"])
    if not (np.isfinite(w).all() and np.all(np.abs(w) <= cfg["weight_cap"])
            and float(np.abs(w).sum()) <= cfg["gross_cap"] * (1 + 1e-12)
            and abs(float(beta @ w) - target) <= tol):
        raise RuntimeError("final book failed its post-processing check")
