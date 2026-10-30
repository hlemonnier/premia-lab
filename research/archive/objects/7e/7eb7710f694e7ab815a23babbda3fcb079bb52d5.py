"""One fixed F3 research forecast; see the prospective PLAN and E2E_SPEC.

Conditional characteristic premia use only a market-volatility state already
observable at each characteristic panel's publication date. The production
engine, risk basis, allocator and scorer are unchanged.
"""
import numpy as np


def make_forecast(engine):
    def forecast(returns_history, characteristics_history):
        engine._STATE = None
        engine.CERTIFICATES.clear()
        forecast.diagnostics = {}
        cfg = engine.CONFIG
        if cfg["beta_shrinkage"]:
            raise ValueError("F3 retains the raw-beta residual labels")
        if cfg["ridge"] != .1 or cfg["min_training_days"] != 126:
            raise ValueError("F3 has fixed ridge0.1 and126 matured-pair warm-up")
        R = np.ascontiguousarray(returns_history, dtype=np.float64)
        X = characteristics_history
        T, N = R.shape
        if np.shape(X) != (T, N, 13):
            raise ValueError("characteristics_history must have shape (days, stocks,13)")
        beta, market = engine.causal_betas(R, cfg["beta_window"])
        residual = R - beta * market[:, None]

        # Close s may use return s. Its state is paired with label s+1 below.
        state = np.zeros(T)
        q = {63: np.zeros(T), 1008: np.zeros(T)}
        sums = {63: 0.0, 1008: 0.0}
        masses = {63: 0.0, 1008: 0.0}
        decay = {h: 2.0 ** (-1.0 / h) for h in sums}
        for s in range(T):
            for h in sums:
                sums[h] = decay[h] * sums[h] + market[s] * market[s]
                masses[h] = decay[h] * masses[h] + 1.0
                q[h][s] = sums[h] / masses[h]
            if s + 1 >= 63:
                ratio = max(q[1008][s], 1e-12) / max(q[63][s], 1e-12)
                state[s] = np.clip(np.log(ratio) / (2.0 * np.log(2.0)), -1.0, 1.0)

        def design(s):
            base = np.hstack([engine.basis(X[s], cfg["feature_clip"]),
                              engine._zcol(beta[s + 1], cfg["feature_clip"])[:, None]])
            return np.hstack([base, state[s] * base[:, :26]])

        ridge = np.diag(np.r_[np.full(27, .1), np.ones(26)])
        grams = [np.zeros((53, 53)) for _ in range(2)]
        moments = [np.zeros(53) for _ in range(2)]
        fit_mass = [0.0, 0.0]
        fit_decays = (2.0 ** (-1.0 / 1008.0), 2.0 ** (-1.0 / 252.0))
        predictions = np.zeros((T, N))
        coefficient_trace = np.zeros((T, 53))
        pairs = 0
        for t in range(2, T):
            s = t - 2
            D = design(s)
            G = D.T @ D / N
            h = D.T @ residual[s + 1] / N
            pairs += 1
            for k, d in enumerate(fit_decays):
                grams[k] = d * grams[k] + G
                moments[k] = d * moments[k] + h
                fit_mass[k] = d * fit_mass[k] + 1.0
            if pairs >= 126:
                slow = np.linalg.solve(grams[0] / fit_mass[0] + ridge,
                                       moments[0] / fit_mass[0])
                fast = np.linalg.solve(grams[1] / fit_mass[1] + ridge,
                                       moments[1] / fit_mass[1])
                combined = slow.copy()
                combined[:13] = .5 * slow[:13] + .5 * fast[:13]
                predictions[t] = design(t - 1) @ combined
                coefficient_trace[t] = combined
        # Observer-only traces are not consumed by rebalance or the overlay.
        forecast.diagnostics = {"market_state": state, "market_q63": q[63],
                                "market_q1008": q[1008], "coefficients": coefficient_trace}
        return predictions

    forecast.diagnostics = {}
    return forecast
