"""C11: the complete second-degree characteristic basis, C02 portfolio.

Marginal curvature does not identify an additive mechanism when predictors
correlate. For illustration, jointly Gaussian standardized X and Z satisfy
E[X*Z | X] = correlation(X,Z)*X**2. This does not identify the simulator; it
motivates a controlled test of additive separability. Retain C02's thirteen
linear and thirteen square columns exactly, then append every one of the78
distinct centered pair products. No pair is selected from favorable diagnostics.

The104 coefficients are estimated jointly from the same causal matured pairs,
market-residual labels and252-day EW moments. Ridge penalties are0.1 for the
original26 terms and1.0 for interactions. Their stronger shrinkage is fixed,
not a selected optimum. The first active forecast remains row127. Learned
moments and coefficients are local; nothing trained on a later row can seed
an earlier portfolio decision.

Portfolio construction delegates unchanged to C02, including its documented
postsolve gross-rescaling approximation. This is an alpha contrast, not a new
optimizer or a simultaneous covariance change. Strong collinearity, dependent
observations, estimation noise, shifting response shapes and omitted common
risk remain possible failures. A discovery gain alone does not prove a joint
mechanism or hidden-future quality.

This is AI-produced development research. The known-interaction synthetic E2E
was specified before implementation; actual verification and market findings
belong in their evidence packets, not inferred from this source note. No
applicant empirical discovery is invented here.

Requires strategy.py and portfolio.py; NumPy and the Python standard library.
"""
from __future__ import annotations

import math
from numbers import Real

import numpy as np

if __package__:
    from . import strategy as base
else:
    import strategy as base


_PAIR_LEFT, _PAIR_RIGHT = np.triu_indices(13, k=1)
CONFIG = {}


def configure(config):
    """Set the one interaction control and delegate all shared validation."""
    global CONFIG
    if not isinstance(config, dict):
        raise ValueError("configuration must be a dictionary")
    penalty = config.get("interaction_ridge", 1.0)
    if (isinstance(penalty, bool) or not isinstance(penalty, Real)
            or not math.isfinite(penalty) or penalty <= 0):
        raise ValueError("interaction_ridge must be a positive finite number")
    parent = {
        "candidate_id": "C11_interactions", "basis": "additive",
        **{key: value for key, value in config.items() if key != "interaction_ridge"},
    }
    if parent["basis"] != "additive":
        raise ValueError("C11 requires the unchanged additive base plus interactions")
    base.configure(parent)
    CONFIG = {**base.CONFIG, "interaction_ridge": float(penalty)}


def _interaction_design(panel, config):
    """Retain the26 base columns and append all78 centered pair products."""
    original = base._basis(panel, config)
    if original.shape[1] != 26:
        raise ValueError("the interaction model requires the26-column additive base")
    linear = original[:, :13]
    products = linear[:, _PAIR_LEFT] * linear[:, _PAIR_RIGHT]
    products -= products.mean(axis=0)
    return np.concatenate((original, products), axis=1)


def forecast(returns_history, characteristics_history, trading_costs):
    """Fit only completed pairs; apply the full basis to the prior panel."""
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
    width = 26 + len(_PAIR_LEFT)
    gram = np.zeros((width, width), dtype=np.float64)
    moment = np.zeros(width, dtype=np.float64)
    ridge = np.diag(np.concatenate((
        np.full(26, config["ridge"]),
        np.full(len(_PAIR_LEFT), config["interaction_ridge"]),
    )))
    decay = 2.0 ** (-1.0 / config["alpha_half_life"])
    mass, matured_days = 0.0, 0

    for t in range(2, days):
        label_day = t - 1
        design = _interaction_design(characteristics[t - 2], config)
        beta_before_label, _ = base._risk_estimates(returns[:label_day], config)
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
            predictions[t] = _interaction_design(characteristics[t - 1], config) @ coefficients
            if not np.isfinite(predictions[t]).all():
                raise ValueError("interaction forecast arithmetic produced a nonfinite prediction")
    return predictions


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    return base.rebalance(held_positions, expected_returns, returns_history, trading_costs)


def estimate_risk(returns_history):
    return base.estimate_risk(returns_history)


def get_last_diagnostics():
    return base.get_last_diagnostics()


configure({})
