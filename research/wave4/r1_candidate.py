"""R1 candidate: V3 alpha/execution with a causal ML specific-risk overlay.

Research candidate, not a replacement for the selected V3 submission. On the
exposed 15-year development sample, net Sharpe is 1.45765 versus V3 1.44473,
with the same 0.05 market sleeve. Two of three stages improve, the last worsens;
the paired bootstrap interval for the gain includes zero. Unweighted variance
QLIKE also worsens. These are not independent out-of-sample guarantees.

A fixed histogram gradient booster predicts next-day squared characteristic
residuals divided by prior specific variance. Inputs: the 13 standardized
characteristics, standardized trailing beta, and log prior specific variance.
It refits every 126 days on every fifth day of the last 504, with no tuning or
early stopping. Its bounded variance multiplier is blended 50/50 with V3's
historical variance. V3's expected returns, factor risk, market sleeve and
certified allocator remain unchanged.

Required: upstream handoff_v3/model_v3 package, NumPy, scikit-learn. To stage a
submission, copy handoff_v3, copy this file there as strategy.py, and preserve
model_v3 unchanged. Research, implementation and checks were performed by GPT;
Hugo directed the search toward ML beyond the earlier plateau. Independent
review and any submission remain separate steps.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
try:
    from model_v3 import engine as E
    from model_v3 import policy as P
except ModuleNotFoundError as exc:
    if exc.name != 'model_v3':
        raise
    # Repository execution; a staged submission has model_v3 alongside this file.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'handoff_v3'))
    from model_v3 import engine as E
    from model_v3 import policy as P

CONFIG = {
    **E.CONFIG,
    'alpha_half_life': 1008.0, 'ridge': 0.1, 'min_training_days': 126,
    'feature_clip': 4.0, 'beta_window': 252, 'factor_half_life': 126.0,
    'specific_half_life': 126.0, 'specific_shrinkage': 0.2,
    'variance_floor': 1e-6, 'factor_risk_scale': 0.3,
    'risk_aversion': 200.0, 'cost_horizon': 20.0,
    'weight_cap': 0.05, 'gross_cap': 5.0,
    'risk_beta_column': False, 'matched_diagonal': False,
    'beta_shrinkage': False, 'beta_target': 0.0,
}


def make_model() -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        loss='poisson', learning_rate=0.05, max_iter=80,
        max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=10.0,
        random_state=20261029, early_stopping=False,
    )


def risk_multipliers(returns_history, characteristics_history, cfg):
    """Output row t depends only on source rows < t, including at refits.

    A 506-day ring holds the longest training window and lagged feature row.
    Working memory for model training does not grow with total history length.
    The returned array grows linearly, like the scorer's forecast interface.
    """
    R = np.ascontiguousarray(returns_history, dtype=np.float64)
    X = characteristics_history
    T, N = R.shape
    if np.shape(X) != (T, N, 13):
        raise ValueError('characteristics must have shape (days, stocks, 13)')
    out = np.ones((T, N), dtype=np.float64)
    ring = 506
    features = np.zeros((ring, N, 15), dtype=np.float32)
    variances = np.full((ring, N), cfg['variance_floor'], dtype=np.float64)
    squares = np.zeros((ring, N), dtype=np.float64)
    state = E._RiskState(N, 26, cfg)
    model = None
    records = []
    for s in range(max(0, T - 1)):
        j = s % ring
        if s:
            old_second = state.U2.copy()
            state.absorb(R, X, s)
            squares[j] = np.maximum(state.U2 - state.aS * old_second, 0.0)
            _, d = state.model()
        else:
            d = np.full(N, cfg['variance_floor'])
        variances[j] = d
        features[j, :, :13] = E.basis(X[s], cfg['feature_clip'])[:, :13]
        beta = E._window_beta(R[:s + 1], cfg['beta_window'])
        features[j, :, 13] = E._zcol(beta, cfg['feature_clip'])
        features[j, :, 14] = np.log(d)
        target = s + 1
        if target < 253:
            continue
        if (target - 253) % 126 == 0:
            labels = np.arange(max(2, target - 504), target, 5)
            previous = (labels - 1) % ring
            train_x = features[previous].reshape(-1, 15)
            train_y = np.minimum(
                squares[labels % ring] / variances[previous], 25.0,
            ).ravel()
            model = make_model()
            tic = time.perf_counter()
            model.fit(train_x, train_y)
            records.append({
                'target_row': target, 'latest_label_row': int(labels[-1]),
                'training_stock_days': len(train_y),
                'fit_seconds': time.perf_counter() - tic,
            })
        ratio = np.clip(model.predict(features[j]), 0.5, 2.0)
        out[target] = 0.5 + 0.5 * ratio
    return out, records


class _ScaledRiskState(E._RiskState):
    multiplier = None

    def model(self):
        L, d = super().model()
        if self.multiplier is None:
            raise RuntimeError('risk multiplier must be set before allocation')
        return L, d * self.multiplier


class _RiskBook(P.Book):
    def __init__(self, cfg, n):
        super().__init__(cfg, n)
        self.multiplier = np.ones(n)

    def rebalance(self, held, mu, R, X, costs, gamma, cap):
        T, n = R.shape
        if self.state is None or self.state.upto > T:
            self.state = _ScaledRiskState(n, 26, self.cfg)
        self.state.multiplier = self.multiplier
        return super().rebalance(held, mu, R, X, costs, gamma, cap)


class RiskPolicy(P.ScorePolicy):
    def forecast(self, returns_history, characteristics_history):
        alpha = super().forecast(returns_history, characteristics_history)
        multiplier, self.training_records = risk_multipliers(
            returns_history, characteristics_history, self.cfg,
        )
        n = np.shape(returns_history)[1]
        self.virtual = _RiskBook(self.cfg, n)
        self.inner = _RiskBook(self.cfg, n)
        self.forecast_output = np.stack([alpha, multiplier], axis=-1)
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        row = np.asarray(expected_returns, dtype=np.float64)
        n = np.shape(returns_history)[1]
        if row.shape != (n, 2) or not np.isfinite(row).all():
            raise ValueError('expected_returns must be finite (stocks, 2)')
        if np.any(row[:, 1] < 0.75) or np.any(row[:, 1] > 1.5):
            raise ValueError('risk multiplier outside registered bounds')
        self.virtual.multiplier = row[:, 1]
        self.inner.multiplier = row[:, 1]
        return super().rebalance(
            held_positions, row[:, 0], returns_history,
            characteristics_history, trading_costs,
        )


POLICY = RiskPolicy(CONFIG, sleeve=0.05, outer_gross_cap=5.0)


def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)


def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(
        held_positions, expected_returns, returns_history,
        characteristics_history, trading_costs,
    )
