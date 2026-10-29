"""F factor-risk model. Relocated unchanged statistics/fitting mathematics from Wave6.
The package reads no files, caches, network resources or saved fitted models.
"""
from __future__ import annotations
import warnings
import numpy as np
from sklearn.linear_model import GammaRegressor
from sklearn.exceptions import ConvergenceWarning
from . import engine as E
from . import policy as P
from .config import CONFIG

def sufficient_statistics(returns_history, characteristics_history, cfg):
    """Date-level common-risk and 26-factor predictors and matured labels.

    Statistics are source-indexed. Labels at s use denominators from s-1;
    features at s can first be used to predict s+1. No per-stock historical
    feature tensor is retained. Full output storage is O(T*26).
    """
    R = np.ascontiguousarray(returns_history, dtype=np.float64)
    X = characteristics_history
    if R.ndim != 2 or R.shape[1] < 1:
        raise ValueError('returns must be (days, positive number of stocks)')
    T, N = R.shape
    if np.shape(X) != (T, N, 13):
        raise ValueError('characteristics must be (days, stocks, 13)')
    cx = np.zeros((T, 3)); cy = np.zeros(T)
    fx = np.zeros((T, 26, 3)); fy = np.zeros((T, 26))
    d = np.full(N, cfg['variance_floor']); fv = np.full(26, 1e-16)
    slow_u = np.zeros(N); slow_f = np.zeros(26); mu = mf = 0.
    au = 2. ** (-1. / cfg['specific_half_life'])
    af = 2. ** (-1. / cfg['factor_half_life'])
    ah = 2. ** (-1. / np.array([5., 21., 63.]))
    fast_u = np.zeros((3, N)); fast_f = np.zeros((3, 26)); mass = np.zeros(3)
    # The final source row cannot contribute to any returned forecast row.
    for s in range(1, T - 1):
        beta = E._window_beta(R[:s], cfg['beta_window'])
        D = E.basis(X[s - 1], cfg['feature_clip'])
        e = R[s] - beta * R[s].mean(); e = e - e.mean()
        f = np.linalg.solve(D.T @ D / N + 1e-10 * np.eye(26), D.T @ e / N)
        u2 = (e - D @ f) ** 2; f2 = f * f
        cy[s] = float(np.mean(u2 / d))
        fy[s] = f2 / np.maximum(fv, 1e-16)
        slow_u = au * slow_u + u2; mu = au * mu + 1.
        slow_f = af * slow_f + f2; mf = af * mf + 1.
        ud = slow_u / mu; sh = cfg['specific_shrinkage']
        d = np.maximum((1. - sh) * ud + sh * np.median(ud), cfg['variance_floor'])
        fv = np.maximum(slow_f / mf, 1e-16)
        fast_u = ah[:, None] * fast_u + u2
        fast_f = ah[:, None] * fast_f + f2
        mass = ah * mass + 1.
        common = np.mean((fast_u / mass[:, None]) / d, axis=1)
        cx[s] = np.log(np.clip(common, .25, 4.))
        fx[s] = np.log(np.clip((fast_f / mass[:, None]) / fv, .25, 4.)).T
    return cx, cy, fx, fy


def fitted_multipliers(features, labels, *, intercept_only=False):
    """Date-block schedule fixed in advance; no score-based selection."""
    T = len(labels)
    factor = labels.ndim == 2
    width = labels.shape[1] if factor else 1
    out = np.ones((T, width)); records = []; model = None; level = 1.
    for t in range(253, T):
        if (t - 253) % 126 == 0:
            dates = np.arange(max(64, t - 504), t, 5)
            train_x = np.ascontiguousarray(features[dates - 1].reshape(-1, 3))
            train_y = np.maximum(labels[dates], 1e-8).ravel()
            rec = dict(target_row=t, first_label=int(dates[0]), last_label=int(dates[-1]),
                       latest_feature_row=int(dates[-1] - 1), training_dates=len(dates),
                       training_observations=len(train_y), intercept_only=intercept_only)
            if intercept_only:
                level = float(np.mean(train_y))
                rec.update(level=level)
            else:
                model = GammaRegressor(alpha=1., max_iter=300, tol=1e-8)
                with warnings.catch_warnings():
                    warnings.simplefilter('error', ConvergenceWarning)
                    model.fit(train_x, train_y)
                rec.update(coef=model.coef_.tolist(), intercept=float(model.intercept_),
                           iterations=int(model.n_iter_))
            records.append(rec)
        pred = np.full(width, level) if intercept_only else model.predict(
            np.ascontiguousarray(features[t - 1].reshape(-1, 3)))
        if not np.isfinite(pred).all():
            raise RuntimeError('nonfinite risk prediction')
        out[t] = .5 + .5 * np.clip(pred, .5, 2.)
    return (out if factor else out[:, 0]), records


class _RescaledState(E._RiskState):
    common = 1.
    factor = None

    def model(self):
        L, d = super().model()
        if self.factor is None:
            raise RuntimeError('factor multiplier missing')
        # Congruence scaling of F preserves positive semidefiniteness/correlations.
        return np.sqrt(self.factor)[:, None] * L, self.common * d


class _RescaledBook(P.Book):
    def __init__(self, cfg, n):
        super().__init__(cfg, n)
        self.common = 1.; self.factor = np.ones(26)

    def rebalance(self, held, mu, R, X, costs, gamma, cap):
        if self.state is None or self.state.upto > len(R):
            self.state = _RescaledState(R.shape[1], 26, self.cfg)
        self.state.common = self.common
        self.state.factor = self.factor
        return super().rebalance(held, mu, R, X, costs, gamma, cap)


class FactorPolicy(P.ScorePolicy):
    """F only: N alpha entries, unit specific multiplier, 26 factor multipliers."""
    def __init__(self):
        super().__init__(dict(CONFIG), sleeve=.05, outer_gross_cap=5.)

    def forecast(self, returns_history, characteristics_history):
        alpha = super().forecast(returns_history, characteristics_history)
        T, N = np.shape(returns_history)
        _, _, fx, fy = sufficient_statistics(returns_history, characteristics_history, self.cfg)
        factor, self.training_records = fitted_multipliers(fx, fy)
        self.virtual = _RescaledBook(self.cfg, N)
        self.inner = _RescaledBook(self.cfg, N)
        self.forecast_output = np.hstack([alpha, np.ones((T, 1)), factor])
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        n = np.shape(returns_history)[1]
        row = np.asarray(expected_returns, dtype=np.float64)
        if row.shape != (n + 27,) or not np.isfinite(row).all():
            raise ValueError('invalid alpha/risk forecast payload')
        if np.any(row[n:] < .75) or np.any(row[n:] > 1.5):
            raise ValueError('risk multipliers outside registered bounds')
        for book in (self.virtual, self.inner):
            book.common = float(row[n]); book.factor = row[n + 1:]
        return super().rebalance(held_positions, row[:n], returns_history,
                                 characteristics_history, trading_costs)
