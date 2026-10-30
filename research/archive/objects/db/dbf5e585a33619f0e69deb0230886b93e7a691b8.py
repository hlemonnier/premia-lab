"""Registered horizon-20 estimator and maturity-matched diagnostic.

The existing 50/50 F2/GLS blend is retained. Only the target and its required
maturity change. No outcomes enter a fit before the complete target matures.
Horizon 1 is a mathematical reproduction control, not a searched parameter.
"""
from __future__ import annotations
import numpy as np
from model_f.factor_risk import FactorPolicy
from model_f import engine as E


def horizon_forecast(R, X, baseline, cfg, horizon=20, delayed_one_day=False):
    if horizon not in (1, 20):
        raise ValueError('only the registered horizon and identity control are allowed')
    R = np.ascontiguousarray(R, dtype=np.float64)
    T, N = R.shape
    beta, market = E.causal_betas(R, cfg['beta_window'])
    residual = R - beta * market[:, None]
    state = E._RiskState(N, 26, cfg)
    grams = [np.zeros((27, 27)), np.zeros((27, 27))]
    moments = [np.zeros(27), np.zeros(27)]
    masses = [0., 0.]
    decays = (2. ** (-1. / 1008.), 2. ** (-1. / 252.))
    out = baseline[:, :N].copy()
    pairs = 0
    records = []
    ones = np.ones(N)
    # s=63 is the original GLS first feature row, for every horizon.
    for t in range(64 + horizon, T):
        s = t - horizon - 1
        u = s + 1
        while state.upto < u:
            state.absorb(R, X, state.upto)
        L, d = state.model()
        L = L / np.sqrt(cfg['factor_risk_scale'])
        L = np.sqrt(baseline[u, N + 1:])[:, None] * L
        D = np.hstack([E.basis(X[s], cfg['feature_clip']),
                       E._zcol(beta[u], cfg['feature_clip'])[:, None]])
        # Latest outcome is s+horizon == t-1. A deliberately delayed one-day
        # label is the prespecified explanatory control; never selectable.
        y = residual[u] if delayed_one_day or horizon == 1 else np.mean(residual[u:t], axis=0)
        M = D[:, :26] @ L
        V = np.column_stack([ones, D, y])
        Vi = V / d[:, None]
        Mi = M / d[:, None]
        precision_V = Vi - Mi @ np.linalg.solve(np.eye(26) + M.T @ Mi, M.T @ Vi)
        normalizer = float(np.sum(precision_V[:, 0]))
        if not np.isfinite(normalizer) or normalizer <= 0:
            raise RuntimeError('nonpositive intercept precision')
        projected = precision_V[:, 1:] - precision_V[:, 0, None] * (
            np.sum(precision_V[:, 1:], axis=0) / normalizer)[None, :]
        G = D.T @ projected[:, :27] / N
        G = .5 * (G + G.T)
        h = D.T @ projected[:, 27] / N
        pairs += 1
        for k, decay in enumerate(decays):
            grams[k] = decay * grams[k] + G
            moments[k] = decay * moments[k] + h
            masses[k] = decay * masses[k] + 1.
        if t < 253 or pairs < 126:
            continue
        coef = []
        for k in range(2):
            g = grams[k] / masses[k]
            v = moments[k] / masses[k]
            floor = 1e-12 * max(float(np.diag(g).mean()), 1e-12)
            penalty = cfg['ridge'] * np.diag(np.maximum(np.diag(g), floor))
            coef.append(np.linalg.solve(g + penalty, v))
        combined = coef[0].copy()
        combined[:13] = .5 * coef[0][:13] + .5 * coef[1][:13]
        current = np.hstack([E.basis(X[t-1], cfg['feature_clip']),
                             E._zcol(beta[t], cfg['feature_clip'])[:, None]])
        out[t] = .5 * baseline[t, :N] + .5 * (current @ combined)
        if (t - 253) % 126 == 0:
            records.append(dict(target_row=t, feature_row=s,
                first_label=u, last_label=u if delayed_one_day else t-1,
                covariance_last_row=s, training_pairs=pairs, horizon=horizon,
                delayed_one_day=delayed_one_day, coef=combined.tolist()))
    if not np.isfinite(out).all():
        raise RuntimeError('nonfinite horizon forecast')
    return out, records


class HorizonPolicy(FactorPolicy):
    def __init__(self, horizon=20, delayed_one_day=False):
        super().__init__()
        self.horizon = horizon
        self.delayed_one_day = delayed_one_day

    def forecast(self, returns_history, characteristics_history):
        base = super().forecast(returns_history, characteristics_history)
        alpha, self.learner_records = horizon_forecast(
            returns_history, characteristics_history, base, self.cfg,
            self.horizon, self.delayed_one_day,
        )
        n = np.shape(returns_history)[1]
        self.forecast_output = np.hstack([alpha, base[:, n:]])
        return self.forecast_output
