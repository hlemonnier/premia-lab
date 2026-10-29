"""Causal adaptive characteristic forecasts with a cost-aware market hedge.

Research checkpoint, not a final submission claim. Discovery diagnostics found
slow-moving characteristics, changing linear effects and some persistent
tail-versus-center differences. C01 fits all thirteen linear effects jointly;
C02 adds all thirteen centered squares. Both use the same causal exponentially
weighted ridge fit, risk estimates and trading policy. No feature was selected
because its standalone diagnostic looked best, and no realized regime date is
hard-coded. Candidate performance and final selection belong in the evidence.

Forecast row t uses only rows before t. The newest training pair is X[t-2]
against R[t-1]; its market beta is estimated before that label return. The
learner keeps fixed-dimensional sufficient statistics, forgets with a fixed
252-day half-life and emits zero until 126 daily pairs have matured. All fitted
state is local to forecast, with no future-trained object used by rebalance.

The portfolio uses trailing 252-day market betas and shrunk diagonal residual
variances. A convex scalar-dual allocator balances alpha, risk and absolute
trading costs around the actual drifted holdings, with an exact estimated-beta
hedge and stock bounds. The 20-day cost amortization is a control approximation;
the evaluator still charges full actual costs. A gross cap can proportionally
shrink the result; this preserves the hedge but is not the exact gross-constrained
optimum. Its frequency must be measured rather than concealed.

The first candidate design and implementation are AI work, following the user's
instructions for source-grounded research, predeclared experiments and independent
verification. No human empirical discovery is claimed here. Long-run risks include
changing response shapes, adaptation lag, common residual risks omitted by the
diagonal model, beta estimation error, and costs caused by unstable estimates.
Validation, audit, causality and runtime claims require their recorded executions.

Requires this file and portfolio.py; only NumPy and the Python standard library.
Default configuration is the C01 development benchmark. configure() is the
research runner's explicit interface for the frozen C01/C02 JSON configurations.
"""
from __future__ import annotations

import math
from numbers import Integral, Real

import numpy as np

if __package__:
    from .portfolio import allocate
else:
    from portfolio import allocate


_DEFAULT_CONFIG = {
    "candidate_id": "C01_linear",
    "basis": "linear",
    "alpha_half_life": 252.0,
    "ridge": 0.1,
    "min_training_days": 126,
    "feature_clip": 4.0,
    "risk_window": 252,
    "risk_min_days": 20,
    "variance_shrinkage": 0.2,
    "variance_floor": 1e-6,
    "risk_aversion": 1000.0,
    "cost_horizon": 20.0,
    "weight_cap": 0.01,
    "gross_cap": 1.0,
}
CONFIG = dict(_DEFAULT_CONFIG)
_LAST_DIAGNOSTICS = {}


def configure(config):
    """Set an explicit research configuration; reject misspelled/invalid knobs.

    Each call begins with the defaults, so omitted values never inherit a prior
    candidate's settings. This function does not read data or fit a model.
    """
    global CONFIG, _LAST_DIAGNOSTICS
    if not isinstance(config, dict):
        raise ValueError("configuration must be a dictionary")
    unknown = set(config) - set(_DEFAULT_CONFIG)
    if unknown:
        raise ValueError(f"unknown configuration keys: {sorted(unknown)}")
    chosen = {**_DEFAULT_CONFIG, **config}
    if not isinstance(chosen["candidate_id"], str) or not chosen["candidate_id"]:
        raise ValueError("candidate_id must be a nonempty string")
    if chosen["basis"] not in ("linear", "additive"):
        raise ValueError("basis must be linear or additive")
    for key in ("min_training_days", "risk_window", "risk_min_days"):
        value = chosen[key]
        if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
            raise ValueError(f"{key} must be a positive integer")
        chosen[key] = int(value)
    if chosen["risk_min_days"] < 2 or chosen["risk_window"] < chosen["risk_min_days"]:
        raise ValueError("risk_window must be >= risk_min_days >= 2")
    for key in ("alpha_half_life", "ridge", "feature_clip", "variance_floor",
                "risk_aversion", "cost_horizon", "weight_cap", "gross_cap"):
        value = chosen[key]
        if (isinstance(value, bool) or not isinstance(value, Real)
                or not math.isfinite(value) or value <= 0):
            raise ValueError(f"{key} must be a positive finite number")
        chosen[key] = float(value)
    shrinkage = chosen["variance_shrinkage"]
    if (isinstance(shrinkage, bool) or not isinstance(shrinkage, Real)
            or not math.isfinite(shrinkage) or not 0 <= shrinkage <= 1):
        raise ValueError("variance_shrinkage must lie in [0, 1]")
    chosen["variance_shrinkage"] = float(shrinkage)
    CONFIG = chosen
    _LAST_DIAGNOSTICS = {}


def _basis(panel, config):
    """A bounded, centered design using only this one published panel."""
    panel = np.asarray(panel, dtype=np.float64)
    if panel.ndim != 2 or panel.shape[1] != 13 or panel.shape[0] == 0:
        raise ValueError("a characteristic panel must have shape (stocks, 13)")
    if not np.isfinite(panel).all():
        raise ValueError("consumed characteristics must be finite")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        centered = panel - panel.mean(axis=0)
        scale = np.maximum(np.sqrt(np.mean(centered * centered, axis=0)), 1e-12)
        linear = np.clip(centered / scale, -config["feature_clip"], config["feature_clip"])
        linear -= linear.mean(axis=0)
        if config["basis"] == "linear":
            return linear
        square = linear * linear
        square = (square - square.mean(axis=0)) / math.sqrt(2.0)
        return np.concatenate((linear, square), axis=1)


def _risk_estimates(returns_history, config):
    """Centered trailing estimates; never modifies inputs or global state."""
    history = np.asarray(returns_history, dtype=np.float64)
    if history.ndim != 2 or history.shape[1] == 0:
        raise ValueError("returns_history must have shape (days, stocks)")
    n = history.shape[1]
    window = history[-config["risk_window"]:]
    if not len(window):
        return np.ones(n), np.full(n, max(0.0004, config["variance_floor"]))
    if not np.isfinite(window).all():
        raise ValueError("consumed returns must be finite")
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        centered = window - window.mean(axis=0)
        market = window.mean(axis=1)
        market -= market.mean()
        market_variance = float(market @ market / len(window))
        if len(window) < config["risk_min_days"] or market_variance <= 1e-12:
            beta = np.ones(n)
        else:
            beta = (market @ centered) / (len(window) * market_variance)
        residual = centered - market[:, None] * beta
        variance = np.mean(residual * residual, axis=0)
        shrinkage = config["variance_shrinkage"]
        variance = ((1 - shrinkage) * variance + shrinkage * np.median(variance))
        variance = np.maximum(variance, config["variance_floor"])
    return beta, variance


def estimate_risk(returns_history):
    """Read-only diagnostic interface: current betas and diagonal variances."""
    return _risk_estimates(returns_history, CONFIG)


def forecast(returns_history, characteristics_history, trading_costs):
    """Return expected residual returns, with strict before-day-t information."""
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

    # All fitted state stays local. In particular, forecast never fills a
    # risk/model cache subsequently read by rebalance.
    for t in range(2, days):
        label_day = t - 1
        design = _basis(characteristics[t - 2], config)
        beta_before_label, _ = _risk_estimates(returns[:label_day], config)
        observed_return = returns[label_day]
        if not np.isfinite(observed_return).all():
            raise ValueError("consumed label returns must be finite")
        label = observed_return - beta_before_label * observed_return.mean()
        gram = decay * gram + (design.T @ design) / n
        moment = decay * moment + (design.T @ label) / n
        mass = decay * mass + 1.0
        matured_days += 1
        if matured_days >= config["min_training_days"]:
            coefficients = np.linalg.solve(gram / mass + ridge, moment / mass)
            predictions[t] = _basis(characteristics[t - 1], config) @ coefficients
            if not np.isfinite(predictions[t]).all():
                raise ValueError("forecast arithmetic produced a nonfinite prediction")
    return predictions


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    """Hedge estimated beta and pay attention to the actual drifted holdings."""
    global _LAST_DIAGNOSTICS
    if expected_returns is None:
        raise ValueError("this strategy requires its forecast row")
    config = CONFIG
    beta, variance = _risk_estimates(returns_history, config)
    positions = allocate(
        expected_returns, held_positions, variance, beta, trading_costs,
        config["risk_aversion"], config["cost_horizon"], config["weight_cap"],
    )
    pre_scale_gross = float(np.abs(positions).sum())
    cap_saturation = float(np.mean(np.abs(positions) >= config["weight_cap"] - 1e-14))
    scale = min(1.0, config["gross_cap"] / pre_scale_gross) if pre_scale_gross else 1.0
    positions = positions * scale
    _LAST_DIAGNOSTICS = {
        "pre_scale_gross": pre_scale_gross,
        "gross_scale": scale,
        "pre_scale_box_saturation_fraction": cap_saturation,
        "post_scale_estimated_beta": float(beta @ positions),
    }
    return positions


def get_last_diagnostics():
    """A copy of current-call diagnostics; these never affect a decision."""
    return dict(_LAST_DIAGNOSTICS)
