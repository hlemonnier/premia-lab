"""Two fixed research forecasts; production V2 and its allocator remain unchanged.

The prospective controller and its missing-module result precede this file.
"""
import numpy as np


def make_forecast(engine, variant):
    if variant not in ("F1", "F2"):
        raise ValueError("Only the two prospectively specified forecasts are available")

    def forecast(returns_history, characteristics_history):
        engine._STATE = None
        engine.CERTIFICATES.clear()
        cfg = engine.CONFIG
        if cfg["beta_shrinkage"]:
            raise ValueError("These contrasts preserve the original raw-beta labels")
        R = np.ascontiguousarray(returns_history, dtype=np.float64)
        X = characteristics_history
        T, N = R.shape
        if np.shape(X) != (T, N, 13):
            raise ValueError("characteristics_history must have shape (days, stocks, 13)")
        beta, market = engine.causal_betas(R, cfg["beta_window"])
        residual = R - beta * market[:, None]
        ridge = cfg["ridge"] * np.eye(27)

        def design(s):
            return np.hstack([engine.basis(X[s], cfg["feature_clip"]),
                              engine._zcol(beta[s + 1], cfg["feature_clip"])[:, None]])

        decay_slow = 2.0 ** (-1.0 / 1008.0)
        decay_fast = 2.0 ** (-1.0 / 252.0)
        slope_sum = np.zeros(27)
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
            if variant == "F1":
                daily_slope = np.linalg.solve(G + ridge, h)
                slope_sum = decay_slow * slope_sum + daily_slope
                masses[0] = decay_slow * masses[0] + 1.0
                if pairs >= cfg["min_training_days"]:
                    predictions[t] = design(t - 1) @ (slope_sum / masses[0])
            else:
                for k, decay in enumerate((decay_slow, decay_fast)):
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

    return forecast
