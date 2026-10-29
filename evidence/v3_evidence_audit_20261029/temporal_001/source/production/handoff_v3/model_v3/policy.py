"""F2 forecast -> E2 execution -> fixed M1 market sleeve, as explicit state objects.

Forecast (F2): two pooled exponentially weighted ridge regressions on the 27-column design
(13 standardized characteristics, 13 centered squares, standardized trailing beta), half-lives
1,008 and 252, ridge 0.1, 126 matured pairs before predicting. The 13 linear coefficients are
the average of the two fits; squares and beta use the slow fit. Row t uses X[t-1] and the beta
known at t; its newest matured pair is X[t-2] against the residual return of day t-1.

Books, each with its own risk state, solver warm start and drifted holdings:
- virtual: the F2 reference allocation (gamma 200, cap 0.05). Its earned gross returns feed
  EW63 / EW1008 second moments; after 63 earned days the multiplier is
  a = clip((max(q1008, 1e-12) / max(q63, 1e-12)) ** 0.5, 0.5, 2), else 1.
- inner (E2): the same allocator solved against its own holdings with gamma 200/a, cap 0.05a.
- outer: inner + 0.05/N in every stock (a deliberate equal-weight market position), reduced
  proportionally only if gross exceeds 5. This is the book returned to the scorer.
forecast() starts a session and resets all books, moments and counts.
"""
import numpy as np

from . import engine as E
from .allocator import allocate_factor


def f2_forecast(returns_history, characteristics_history, cfg):
    R = np.ascontiguousarray(returns_history, dtype=np.float64)
    X = characteristics_history
    T, N = R.shape
    if np.shape(X) != (T, N, 13):
        raise ValueError("characteristics_history must have shape (days, stocks, 13)")
    beta, market = E.causal_betas(R, cfg["beta_window"])
    residual = R - beta * market[:, None]
    ridge = cfg["ridge"] * np.eye(27)

    def design(s):
        return np.hstack([E.basis(X[s], cfg["feature_clip"]), E._zcol(beta[s + 1], cfg["feature_clip"])[:, None]])

    decays = (2.0 ** (-1.0 / 1008.0), 2.0 ** (-1.0 / 252.0))
    grams = [np.zeros((27, 27)) for _ in range(2)]
    moments = [np.zeros(27) for _ in range(2)]
    masses = [0.0, 0.0]
    pairs = 0
    predictions = np.zeros((T, N))
    for t in range(2, T):
        s = t - 2
        D = design(s)
        G = D.T @ D / N
        h = D.T @ residual[s + 1] / N
        pairs += 1
        for k, decay in enumerate(decays):
            grams[k] = decay * grams[k] + G
            moments[k] = decay * moments[k] + h
            masses[k] = decay * masses[k] + 1.0
        if pairs >= cfg["min_training_days"]:
            slow = np.linalg.solve(grams[0] / masses[0] + ridge, moments[0] / masses[0])
            fast = np.linalg.solve(grams[1] / masses[1] + ridge, moments[1] / masses[1])
            combined = slow.copy()
            combined[:13] = 0.5 * slow[:13] + 0.5 * fast[:13]
            predictions[t] = design(t - 1) @ combined
    return predictions


class Book:
    """One allocation book: production allocator and checks, with instance-owned state."""

    def __init__(self, cfg, n):
        self.cfg = dict(cfg)
        self.state = None
        self.target = np.zeros(n)

    def rebalance(self, held, mu, R, X, costs, gamma, cap):
        cfg = {**self.cfg, "risk_aversion": gamma, "weight_cap": cap}
        T, n = R.shape
        if self.state is None or self.state.upto > T:
            self.state = E._RiskState(n, 26, self.cfg)
        while self.state.upto < T:
            self.state.absorb(R, X, self.state.upto)
        L, d = self.state.model()
        beta = E._window_beta(R, cfg["beta_window"])
        D = E.risk_loadings(X[T - 1], beta, cfg)
        info = {}
        w = allocate_factor(mu, held, d, D, L, beta, np.asarray(costs, dtype=np.float64) / cfg["cost_horizon"],
                            gamma, cap, warm=self.state.warm, info=info, beta_target=0.0)
        gross = float(np.abs(w).sum())
        info["gross_action"] = "none"
        if gross > cfg["gross_cap"]:                   # zero beta target: scaling keeps b'w = 0
            w = w * (cfg["gross_cap"] / gross); info["gross_action"] = "scaled"
        E._final_check(w, beta, 0.0, cfg)
        self.target = w
        return w, info


class ScorePolicy:
    def __init__(self, cfg, sleeve=0.05, outer_gross_cap=5.0):
        if cfg["beta_shrinkage"] or cfg["risk_beta_column"] or cfg["matched_diagonal"] or cfg["beta_target"] != 0.0:
            raise ValueError("this policy uses the raw-beta, zero-target, 26-column V2 risk settings")
        self.cfg = dict(cfg)
        self.sleeve = float(sleeve)
        self.outer_gross_cap = float(outer_gross_cap)
        self.forecast_output = None

    def forecast(self, returns_history, characteristics_history):
        n = np.shape(returns_history)[1]
        self.virtual, self.inner = Book(self.cfg, n), Book(self.cfg, n)
        self.outer_target = np.zeros(n)
        self.sums = {63: 0.0, 1008: 0.0}
        self.masses = {63: 0.0, 1008: 0.0}
        self.earned = 0
        self.last_day = None
        self.certificates = []
        self.multiplier = 1.0
        self.forecast_output = f2_forecast(returns_history, characteristics_history, self.cfg)
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        if self.forecast_output is None:
            raise RuntimeError("forecast() must start the scoring session")
        R = np.ascontiguousarray(returns_history, dtype=np.float64)
        X = characteristics_history
        t = len(R) - 1
        if self.last_day is not None and t != self.last_day + 1:
            raise RuntimeError("rebalance calls must advance one published row at a time")
        r = R[-1]
        n = R.shape[1]
        # inner book drifts with its own return; the virtual book likewise
        inner_g = float(self.inner.target @ r)
        g = float(self.virtual.target @ r)
        if not (np.isfinite(inner_g) and np.isfinite(g)) or inner_g <= -1 or g <= -1:
            raise RuntimeError("an internal book has a nonfinite return or is ruined")
        inner_held = self.inner.target * (1 + r) / (1 + inner_g)
        virtual_held = self.virtual.target * (1 + r) / (1 + g)
        if self.last_day is not None:
            self.earned += 1
            for hl in self.sums:
                decay = 2.0 ** (-1.0 / hl)
                self.sums[hl] = decay * self.sums[hl] + g * g
                self.masses[hl] = decay * self.masses[hl] + 1.0
        q = {hl: self.sums[hl] / self.masses[hl] if self.masses[hl] else 0.0 for hl in self.sums}
        ratio = max(q[1008], 1e-12) / max(q[63], 1e-12)
        a = 1.0 if self.earned < 63 else float(np.clip(ratio ** 0.5, .5, 2.0))
        self.multiplier = a
        _, cv = self.virtual.rebalance(virtual_held, expected_returns, R, X, trading_costs, 200.0, 0.05)
        w_inner, ci = self.inner.rebalance(inner_held, expected_returns, R, X, trading_costs, 200. / a, .05 * a)
        self.certificates += [cv, ci]
        proposed = w_inner + self.sleeve / n
        gross = float(np.abs(proposed).sum())
        target = proposed * (min(1.0, self.outer_gross_cap / gross) if gross else 1.0)
        if not (np.isfinite(target).all() and float(np.abs(target).sum()) <= self.outer_gross_cap * (1 + 1e-12)
                and float(np.abs(target).max()) <= 0.10 + self.sleeve / n):
            raise RuntimeError("outer book failed its post-processing check")
        self.outer_target = target
        self.last_day = t
        return target
