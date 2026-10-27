"""C12: fixed local additive responses, with the unchanged C02 portfolio.

Keep C02's thirteen linear and thirteen centered-square columns exactly. For
each characteristic append centered hinges at -1, 0 and +1, residualized and
scaled using analytic standard-normal reference constants. These constants
do not assume that observed panels are normal, fit a transformation to data,
or make the realized design orthogonal. All thirteen characteristics receive
the same extension; no feature or knot is selected from a favorable result.

Fit the 65 coefficients jointly with the unchanged causal 252-day EW moments:
ridge 0.1 for the original 26 columns and 0.3 for the 39 local terms. At row t,
the newest training pair is X[t-2] -> R[t-1], with label beta estimated strictly
before that return. Apply the fit to X[t-1]. Fitted state stays local to this
forecast call; rebalance receives no future-trained object or coefficient.

The prospective specification is research/LOCAL_ADDITIVE_PLAN.md. Independent
synthetic expectations, the controller and an expected missing-module run
preceded this implementation. Actual verification and market results belong
in their evidence packets. A more flexible shape can fit noise, create costly
turnover or become unstable. A discovery gain cannot establish a tradable edge
or remove selection optimism from the prior research process.

This is AI-produced implementation. Portfolio construction delegates unchanged
to C02, including its documented proportional gross-rescaling approximation.
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


# Fixed reference calculations, never estimated from a project input panel.
_KNOTS = np.array((-1.0, 0.0, 1.0), dtype=np.float64)
_REFERENCE_TAIL = np.array([
    0.5 * math.erfc(float(a) / math.sqrt(2.0)) for a in _KNOTS
])
_REFERENCE_PHI = np.array([
    math.exp(-float(a) * float(a) / 2.0) / math.sqrt(2.0 * math.pi)
    for a in _KNOTS
])
_REFERENCE_FIRST = _REFERENCE_PHI - _KNOTS * _REFERENCE_TAIL
_REFERENCE_SECOND = (1.0 + _KNOTS * _KNOTS) * _REFERENCE_TAIL - _KNOTS * _REFERENCE_PHI
_REFERENCE_SCALE = np.sqrt(
    _REFERENCE_SECOND - _REFERENCE_FIRST * _REFERENCE_FIRST
    - _REFERENCE_TAIL * _REFERENCE_TAIL - _REFERENCE_PHI * _REFERENCE_PHI / 2.0
)
CONFIG = {}


def configure(config):
    """Validate the local penalty and delegate all shared controls to C02."""
    global CONFIG
    if not isinstance(config, dict):
        raise ValueError("configuration must be a dictionary")
    penalty = config.get("local_ridge", 0.3)
    if (isinstance(penalty, bool) or not isinstance(penalty, Real)
            or not math.isfinite(penalty) or penalty <= 0):
        raise ValueError("local_ridge must be a positive finite number")
    parent = {
        "candidate_id": "C12_local_additive", "basis": "additive",
        **{key: value for key, value in config.items() if key != "local_ridge"},
    }
    if parent["basis"] != "additive":
        raise ValueError("C12 requires the unchanged additive base plus local terms")
    base.configure(parent)
    CONFIG = {**base.CONFIG, "local_ridge": float(penalty)}


def _local_design(panel, config):
    """Retain 26 base columns; append 13 feature-major groups of three hinges."""
    original = base._basis(panel, config)
    if original.shape[1] != 26:
        raise ValueError("the local model requires the 26-column additive base")
    linear = original[:, :13]
    square = original[:, 13:]
    hinges = np.maximum(linear[:, :, None] - _KNOTS, 0.0)
    hinges -= hinges.mean(axis=0)
    local = (
        hinges - linear[:, :, None] * _REFERENCE_TAIL
        - square[:, :, None] * (_REFERENCE_PHI / math.sqrt(2.0))
    ) / _REFERENCE_SCALE
    return np.concatenate((original, local.reshape(len(original), 39)), axis=1)


def forecast(returns_history, characteristics_history, trading_costs):
    """Learn only from completed pairs and predict from the preceding panel."""
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
    gram = np.zeros((65, 65), dtype=np.float64)
    moment = np.zeros(65, dtype=np.float64)
    ridge = np.diag(np.concatenate((
        np.full(26, config["ridge"]),
        np.full(39, config["local_ridge"]),
    )))
    decay = 2.0 ** (-1.0 / config["alpha_half_life"])
    mass, matured_days = 0.0, 0

    for t in range(2, days):
        label_day = t - 1
        design = _local_design(characteristics[t - 2], config)
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
            predictions[t] = _local_design(characteristics[t - 1], config) @ coefficients
            if not np.isfinite(predictions[t]).all():
                raise ValueError("local additive forecast produced a nonfinite prediction")
    return predictions


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    return base.rebalance(held_positions, expected_returns, returns_history, trading_costs)


def estimate_risk(returns_history):
    return base.estimate_risk(returns_history)


def get_last_diagnostics():
    return base.get_last_diagnostics()


configure({})
