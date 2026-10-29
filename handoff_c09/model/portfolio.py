"""Diagonal-risk allocation with exact box, turnover and beta constraints.

The trading-cost horizon is a control approximation. It does not alter the
full costs charged by the supplied scorer. This module does not impose a
gross-exposure cap or estimate any market quantities.
"""
from __future__ import annotations

import numpy as np


def _vector(value, name, length=None):
    try:
        result = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric vector") from exc
    if result.ndim != 1 or result.size == 0 or (length is not None and result.size != length):
        raise ValueError(f"{name} must be a nonempty vector of the expected length")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")
    return result


def _positive_scalar(value, name):
    try:
        result = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive finite scalar") from exc
    if result.ndim != 0 or not np.isfinite(result) or result <= 0:
        raise ValueError(f"{name} must be a positive finite scalar")
    return float(result)


def allocate(expected_returns, held_positions, variances, betas, trading_costs,
             risk_aversion, cost_horizon, weight_cap):
    """Maximize alpha minus diagonal risk and amortized absolute trade costs.

    Specifically, maximize ``mu @ w - .5 * gamma * (var * w) @ w
    - (cost / horizon) @ abs(w - held)`` subject to ``beta @ w == 0``
    and ``abs(w) <= cap``. Cap may be a nonnegative scalar or a vector.
    Variances must already have a strictly positive caller-chosen floor.

    The function is deterministic and does not mutate its inputs. Invalid or
    numerically unrepresentable inputs raise ValueError. Failure to resolve
    the hedge to floating-point tolerance raises RuntimeError.
    """
    mu = _vector(expected_returns, "expected_returns")
    n = len(mu)
    held = _vector(held_positions, "held_positions", n)
    var = _vector(variances, "variances", n)
    beta = _vector(betas, "betas", n)
    costs = _vector(trading_costs, "trading_costs", n)
    gamma = _positive_scalar(risk_aversion, "risk_aversion")
    horizon = _positive_scalar(cost_horizon, "cost_horizon")
    if np.any(var <= 0):
        raise ValueError("variances must be strictly positive")
    if np.any(costs < 0):
        raise ValueError("trading_costs must be nonnegative")
    try:
        cap = np.asarray(weight_cap, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("weight_cap must be a nonnegative scalar or vector") from exc
    if cap.ndim == 0:
        cap = np.full(n, float(cap), dtype=np.float64)
    elif cap.ndim != 1 or cap.size != n:
        raise ValueError("weight_cap must be a scalar or a vector of the expected length")
    if not np.isfinite(cap).all() or np.any(cap < 0):
        raise ValueError("weight_cap must be finite and nonnegative")
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        diagonal = gamma * var
        penalty = costs / horizon
    if not np.isfinite(diagonal).all() or np.any(diagonal <= 0):
        raise ValueError("scaled diagonal risk must be finite and strictly positive")
    if not np.isfinite(penalty).all():
        raise ValueError("scaled trading costs must be finite")
    movable = cap > 0
    if not np.any(movable):
        return np.zeros(n, dtype=np.float64)
    with np.errstate(over="ignore", invalid="ignore"):
        held_gradient = diagonal * held
        cap_gradient = diagonal * cap
    if not np.isfinite(held_gradient).all() or not np.isfinite(cap_gradient).all():
        raise ValueError("risk gradients at holdings and caps must be representable")

    # A fixed-zero position cannot affect the hedge or its numerical scale.
    beta_scale = float(np.max(np.abs(beta[movable])))
    b = np.zeros(n, dtype=np.float64)
    if beta_scale:
        b[movable] = beta[movable] / beta_scale
        if np.any((beta[movable] != 0) & (b[movable] == 0)):
            raise ValueError("relative beta scales exceed floating-point range")

    def at_multiplier(multiplier):
        # Minimize each scalar Lagrangian. The risk gradient at held defines
        # the no-trade band; outside it, use the appropriate cost-adjusted
        # quadratic optimum. Clipping is exact for this scalar convex problem.
        # Overflow must fail before clipping: a later cost subtraction can
        # cancel a large finite intermediate, so clipping infinity could
        # otherwise return a feasible but nonoptimal portfolio.
        try:
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                shifted_mu = mu - multiplier * b
                marginal_gain = shifted_mu - held_gradient
                w = held.copy()
                np.divide(shifted_mu - penalty, diagonal, out=w, where=marginal_gain > penalty)
                np.divide(shifted_mu + penalty, diagonal, out=w, where=marginal_gain < -penalty)
                np.clip(w, -cap, cap, out=w)
        except FloatingPointError as exc:
            raise ValueError("scalar allocation arithmetic must be representable") from exc
        return w, float(b @ w)

    initial_weights, initial_exposure = at_multiplier(0.0)
    if beta_scale == 0:
        return initial_weights
    with np.errstate(over="ignore", invalid="ignore"):
        exposure_bound = float(np.abs(b) @ cap)
    if not np.isfinite(exposure_bound) or exposure_bound <= 0:
        raise ValueError("total attainable beta exposure must be representable")
    tolerance = max(64 * np.finfo(np.float64).eps * exposure_bound,
                    float(np.nextafter(0.0, 1.0)))
    if abs(initial_exposure) <= tolerance:
        return initial_weights

    hedge_assets = b != 0
    step = float(max(np.max(np.abs(mu[hedge_assets])),
                     np.max(cap_gradient[hedge_assets]),
                     np.max(penalty[hedge_assets]), np.finfo(np.float64).tiny))
    trial = step if initial_exposure > 0 else -step
    best_weights, best_error = initial_weights, abs(initial_exposure)
    # The exposure decreases continuously with the multiplier. At the two
    # infinite limits every nonzero-beta asset is at its opposing box bound.
    for _ in range(1024):
        weights, exposure = at_multiplier(trial)
        if abs(exposure) < best_error:
            best_weights, best_error = weights, abs(exposure)
        if abs(exposure) <= tolerance:
            return weights
        if (initial_exposure > 0 and exposure < 0) or (initial_exposure < 0 and exposure > 0):
            break
        if abs(trial) > np.finfo(np.float64).max / 2:
            raise RuntimeError("Cannot bracket the beta hedge within floating-point range")
        trial *= 2
    else:
        raise RuntimeError("Could not bracket the beta hedge")

    lower, upper = (0.0, trial) if initial_exposure > 0 else (trial, 0.0)
    for _ in range(200):
        midpoint = 0.5 * lower + 0.5 * upper
        if midpoint == lower or midpoint == upper:
            break
        weights, exposure = at_multiplier(midpoint)
        if abs(exposure) < best_error:
            best_weights, best_error = weights, abs(exposure)
        if abs(exposure) <= tolerance:
            return weights
        if exposure > 0:
            lower = midpoint
        else:
            upper = midpoint
    if best_error <= tolerance:
        return best_weights
    raise RuntimeError("Beta hedge did not converge to floating-point tolerance")
