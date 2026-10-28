"""Forecast and rebalance for the V2 strategy. NumPy and the standard library only.

Forecast: C09's learner (exponentially weighted ridge on the 13 standardized
characteristics and their centered squares, half-life 1,008 days) plus one
column, each stock's trailing market beta. Pair s uses design X[s] (and the
beta estimated from rows before s+1) against the market-residual return of day
s+1; row t predicts with X[t-1]. The newest pair used at row t is s = t-2.

Rebalance: risk model Sigma = diag(d) + phi * D F D', where D is today's
characteristic basis (the same 26 columns), F an exponentially weighted
covariance of daily characteristic factor returns, d the variance those factors
leave unexplained. The exact allocator in allocator.py trades off forecast,
risk and linear costs around the drifted book, with an estimated-beta hedge and
per-stock caps. State is absorbed one day at a time from history through today.
"""
import math

import numpy as np

from .allocator import allocate_factor

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
    # allocation
    "risk_aversion": 1000.0, "cost_horizon": 20.0, "weight_cap": 0.01, "gross_cap": 1.0,
}


def configure(config):
    global CONFIG, _STATE
    unknown = set(config) - set(CONFIG)
    if unknown:
        raise ValueError(f"unknown configuration keys: {sorted(unknown)}")
    CONFIG = {**CONFIG, **config}
    _STATE = None


# ---------------------------------------------------------------- shared pieces
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


# ---------------------------------------------------------------- forecast
def forecast(returns_history, characteristics_history):
    """Also starts a new scoring session: the scorer calls forecast once per run, so the
    rebalance risk state and solver warm start are reset here."""
    global _STATE
    _STATE = None
    CERTIFICATES.clear()
    cfg = CONFIG
    R = np.ascontiguousarray(returns_history, dtype=np.float64)   # canonical layout keeps reductions prefix-stable
    X = characteristics_history
    T, N = R.shape
    if np.shape(X)[:2] != (T, N) or np.shape(X)[2] != 13:
        raise ValueError("characteristics_history must be (days, stocks, 13)")
    beta, m = causal_betas(R, cfg["beta_window"])
    if cfg["beta_shrinkage"]:                          # labels use corrected betas; eta_t from rows < t only
        tracker = _EtaTracker(cfg["beta_window"])
        eta = np.array([tracker.eta(R, t) for t in range(T)])
        bc = (1.0 - eta)[:, None] * beta + (eta * beta.mean(axis=1))[:, None]
        E = R - bc * m[:, None]
    else:
        E = R - beta * m[:, None]                      # residual of day s uses beta from rows < s

    def zcol(v):
        v = v - v.mean(); v = np.clip(v / max(v.std(), 1e-12), -cfg["feature_clip"], cfg["feature_clip"])
        return v - v.mean()

    def design(s):
        return np.hstack([basis(X[s], cfg["feature_clip"]), zcol(beta[s + 1])[:, None]])

    decay = 2.0 ** (-1.0 / cfg["alpha_half_life"])
    width = 27
    gram = np.zeros((width, width)); mom = np.zeros(width); mass = 0.0; pairs = 0
    ridge = cfg["ridge"] * np.eye(width)
    pred = np.zeros((T, N))
    for t in range(2, T):
        s = t - 2                                      # newest matured pair: X[t-2] -> e[t-1]
        D = design(s); y = E[s + 1]
        gram = decay * gram + D.T @ D / N
        mom = decay * mom + D.T @ y / N
        mass = decay * mass + 1.0; pairs += 1
        if pairs >= cfg["min_training_days"]:
            coef = np.linalg.solve(gram / mass + ridge, mom / mass)
            pred[t] = design(t - 1) @ coef
    return pred


# ---------------------------------------------------------------- risk state
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


_STATE = None
CERTIFICATES = []   # one allocator certificate per rebalance call in the current session


def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    global _STATE
    if expected_returns is None:
        raise ValueError("this strategy requires its forecast row")
    cfg = CONFIG
    R = np.ascontiguousarray(returns_history, dtype=np.float64)
    X = characteristics_history
    T, n = R.shape
    # Session contract: forecast() starts a session; within it the history is append-only.
    # A shrinking history (or no prior state) rebuilds the state from the supplied history.
    if _STATE is None or _STATE.upto > T:
        _STATE = _RiskState(n, 27 if cfg["risk_beta_column"] else 26, cfg)
    while _STATE.upto < T:
        _STATE.absorb(R, X, _STATE.upto)
    L, d = _STATE.model()
    beta = _window_beta(R, cfg["beta_window"])          # hedge betas from the last year through today
    D_today = risk_loadings(X[T - 1], beta, cfg)        # today's published characteristics (+ beta)
    if cfg["beta_shrinkage"]:
        beta = _correct(beta, _STATE.eta.eta(R, T))     # hedge corrected betas; eta from rows < T
    cert = {}
    if cfg["matched_diagonal"]:
        d = d + np.sum((D_today @ L) ** 2, axis=1)     # same marginal variances, no cross-stock covariance
        L = np.zeros_like(L)
    w = allocate_factor(expected_returns, held_positions, d, D_today, L, beta,
                        np.asarray(trading_costs, dtype=np.float64) / cfg["cost_horizon"],
                        cfg["risk_aversion"], cfg["weight_cap"], warm=_STATE.warm, info=cert,
                        beta_target=cfg["beta_target"])
    CERTIFICATES.append(cert)
    gross = float(np.abs(w).sum())
    return w * (min(1.0, cfg["gross_cap"] / gross) if gross else 1.0)
