"""C05: causal covariance-weighted additive learning, C02 diagonal portfolio.

The hypothesis is that common residual shocks make ordinary cross-sectional
coefficient estimates noisy. It is not an established explanation for earlier
results. This learner changes only the precision used in the additive normal
equations; the original basis, EW half-life, ridge, warm-up and complete C02
portfolio remain unchanged. The zero residual intercept assumption is retained;
ordinary centering is not claimed to be precision-weighted centering.

For label day j, covariance and market beta use R[:j], never R[j]. Ten shrunk
residual-correlation factors refresh after20 prior observations and every21
thereafter; earlier pairs use diagonal precision. Current marginal variances
rescale those causal loadings each day. Woodbury applies the same precision to
both design and label, normalized to mean precision diagonal one, so the ridge
keeps its original overall scale. Coefficients and covariance caches stay local
to this forecast call and cannot seed the later portfolio with future state.

This is a development candidate and AI-produced research. Improvements, failure
modes and applicant contributions must be reported from actual evidence. Risks
include noisy covariance weights, removal of useful common expected-return
directions, the retained zero-intercept assumption and the original adaptation
and portfolio limitations. No unexecuted performance or generalization claim.

Requires strategy.py, portfolio.py and gls_precision.py; NumPy and SciPy.
"""
from __future__ import annotations

import math
from numbers import Integral, Real

import numpy as np
from scipy.linalg import eigh

if __package__:
    from . import strategy as base
    from .gls_precision import normalized_precision_apply
else:
    import strategy as base
    from gls_precision import normalized_precision_apply


_LEARNING_DEFAULTS = {
    "learning_factor_rank": 10,
    "learning_factor_shrinkage": 0.5,
    "learning_factor_refresh_days": 21,
}
CONFIG = {}


def configure(config):
    """Set research controls; all fitted state is local to forecast."""
    global CONFIG
    if not isinstance(config, dict):
        raise ValueError("configuration must be a dictionary")
    learning = {key: config.get(key, value) for key, value in _LEARNING_DEFAULTS.items()}
    for key in ("learning_factor_rank", "learning_factor_refresh_days"):
        value = learning[key]
        if isinstance(value, bool) or not isinstance(value, Integral) or value <= 0:
            raise ValueError(f"{key} must be a positive integer")
        learning[key] = int(value)
    shrinkage = learning["learning_factor_shrinkage"]
    if (isinstance(shrinkage, bool) or not isinstance(shrinkage, Real)
            or not math.isfinite(shrinkage) or not 0 <= shrinkage < 1):
        raise ValueError("learning_factor_shrinkage must lie in [0, 1)")
    learning["learning_factor_shrinkage"] = float(shrinkage)
    parent = {
        "basis": "additive", "candidate_id": "C05_gls_diagonal",
        **{key: value for key, value in config.items() if key not in _LEARNING_DEFAULTS},
    }
    base.configure(parent)
    CONFIG = {**base.CONFIG, **learning}


def _correlation_loadings(returns_history, beta, config):
    """The C04 correlation construction with explicit, forecast-local inputs."""
    window = np.asarray(returns_history[-config["risk_window"]:], dtype=np.float64)
    n = window.shape[1]
    shrinkage = config["learning_factor_shrinkage"]
    if len(window) < config["risk_min_days"] or shrinkage == 0:
        return np.empty((n, 0))
    centered = window - window.mean(axis=0)
    market = window.mean(axis=1)
    market -= market.mean()
    residual = centered - market[:, None] * beta
    raw_variance = np.mean(residual * residual, axis=0)
    standardized = residual / np.sqrt(np.maximum(raw_variance, config["variance_floor"]))
    gram = (standardized @ standardized.T) / len(window)
    rank = min(config["learning_factor_rank"], len(window))
    eigenvalues, vectors = eigh(
        gram, subset_by_index=[len(window) - rank, len(window) - 1], check_finite=False,
    )
    keep = eigenvalues > 1e-12
    loadings = (standardized.T @ vectors[:, keep]) * math.sqrt(shrinkage / len(window))
    energy = np.sum(loadings * loadings, axis=1)
    excess = energy > shrinkage
    if np.any(excess):
        loadings[excess] *= np.sqrt(shrinkage / energy[excess])[:, None]
    if not np.isfinite(loadings).all():
        raise ValueError("learner factor estimation produced nonfinite loadings")
    return loadings


def forecast(returns_history, characteristics_history, trading_costs):
    """Fit matured pairs using precision estimated strictly before each label."""
    config = dict(CONFIG)
    returns = np.asarray(returns_history, dtype=np.float64)
    characteristics = np.asarray(characteristics_history, dtype=np.float64)
    costs = np.asarray(trading_costs, dtype=np.float64)
    if returns.ndim != 2 or returns.shape[1] == 0:
        raise ValueError("returns_history must have shape (days, stocks)")
    days, n = returns.shape
    if characteristics.shape != (days, n, 13):
        raise ValueError("characteristics_history must match (days, stocks, 13)")
    if costs.shape != (n,) or not np.isfinite(costs).all() or np.any(costs < 0):
        raise ValueError("trading_costs must be a finite nonnegative stock vector")
    predictions = np.zeros((days, n), dtype=np.float64)
    width = 13 if config["basis"] == "linear" else 26
    gram = np.zeros((width, width), dtype=np.float64)
    moment = np.zeros(width, dtype=np.float64)
    ridge = config["ridge"] * np.eye(width)
    decay = 2.0 ** (-1.0 / config["alpha_half_life"])
    mass, matured_days = 0.0, 0
    correlation_loadings = np.empty((n, 0))
    factor_epoch = None

    for t in range(2, days):
        label_day = t - 1
        # Both covariance and beta are available before R[label_day]. The
        # factor cache is local and cannot populate the portfolio's cache.
        prior_history = returns[:label_day]
        beta, variance = base._risk_estimates(prior_history, config)
        if label_day >= config["risk_min_days"]:
            epoch = ((label_day - config["risk_min_days"])
                     // config["learning_factor_refresh_days"])
            if epoch != factor_epoch:
                correlation_loadings = _correlation_loadings(prior_history, beta, config)
                factor_epoch = epoch
        factors = np.sqrt(variance)[:, None] * correlation_loadings
        diagonal = variance - np.sum(factors * factors, axis=1)
        if np.any(diagonal <= 0) or not np.isfinite(diagonal).all():
            raise ValueError("learner covariance remainder must be positive and finite")

        design = base._basis(characteristics[t - 2], config)
        observed_return = returns[label_day]
        if not np.isfinite(observed_return).all():
            raise ValueError("consumed label returns must be finite")
        label = observed_return - beta * observed_return.mean()
        combined = np.column_stack((design, label))
        weighted, _ = normalized_precision_apply(diagonal, factors, combined)
        contribution = (design.T @ weighted[:, :width]) / n
        contribution = (contribution + contribution.T) * 0.5
        gram = decay * gram + contribution
        moment = decay * moment + (design.T @ weighted[:, width]) / n
        mass = decay * mass + 1.0
        matured_days += 1
        if matured_days >= config["min_training_days"]:
            coefficients = np.linalg.solve(gram / mass + ridge, moment / mass)
            predictions[t] = base._basis(characteristics[t - 1], config) @ coefficients
            if not np.isfinite(predictions[t]).all():
                raise ValueError("GLS forecast arithmetic produced a nonfinite prediction")
    return predictions


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    return base.rebalance(held_positions, expected_returns, returns_history, trading_costs)


def estimate_risk(returns_history):
    return base.estimate_risk(returns_history)


def get_last_diagnostics():
    return base.get_last_diagnostics()


configure({})
