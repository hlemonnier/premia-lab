"""Beta-constrained, cost-aware allocation with diagonal plus low-rank risk.

The reduced factor dual is solved with a semismooth Newton direction. Each
inner primal problem is the separately verified diagonal allocator, so its
beta equality and boxes remain satisfied throughout. No market data or state
is stored here. See verification/FACTOR_PORTFOLIO_PLAN.md for the tests written
before this implementation.
"""
from __future__ import annotations

from numbers import Integral
import numpy as np

if __package__:
    from .portfolio import allocate as diagonal_allocate
else:
    from portfolio import allocate as diagonal_allocate


def allocate_factor(expected_returns, held_positions, diagonal_variances, factors,
                    betas, trading_costs, risk_aversion, cost_horizon, weight_cap,
                    max_iterations=80):
    """Return the strictly convex factor-risk optimum and convergence evidence.

    The covariance is diag(diagonal_variances) + factors @ factors.T. Costs
    penalize the absolute change from actual drifted holdings. A RuntimeError
    means the numerical convergence criterion was not met; no unconverged
    weights are presented as a successful solution.
    """
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, Integral) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")
    # The unchanged inner allocator validates all shared scalar/vector inputs.
    first_weights = diagonal_allocate(expected_returns, held_positions,
        diagonal_variances, betas, trading_costs, risk_aversion, cost_horizon, weight_cap)
    n = len(first_weights)
    try:
        factor = np.asarray(factors, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError("factors must be a finite stock-by-factor matrix") from exc
    if factor.ndim != 2 or factor.shape[0] != n or not np.isfinite(factor).all():
        raise ValueError("factors must be a finite stock-by-factor matrix")
    if factor.shape[1] == 0 or not np.any(factor):
        return first_weights, {"converged": True, "iterations": 0, "inner_solves": 1,
                               "dual_gradient_inf": 0.0, "factor_rank": int(factor.shape[1])}
    mu = np.asarray(expected_returns, dtype=np.float64)
    held = np.asarray(held_positions, dtype=np.float64)
    variance = np.asarray(diagonal_variances, dtype=np.float64)
    beta = np.asarray(betas, dtype=np.float64)
    costs = np.asarray(trading_costs, dtype=np.float64)
    gamma, horizon = float(risk_aversion), float(cost_horizon)
    cap = np.broadcast_to(np.asarray(weight_cap, dtype=np.float64), (n,))
    movable = cap > 0
    beta_scale = float(np.max(np.abs(beta[movable]))) if movable.any() else 0.0
    # A fixed-zero stock cannot affect the hedge and must not overflow its
    # numerical normalization. This matches the inner allocator's convention.
    b = np.zeros(n)
    if beta_scale:
        b[movable] = beta[movable] / beta_scale
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            loading = np.sqrt(gamma) * factor
            diagonal = gamma * variance
            penalty = costs / horizon
    except FloatingPointError as exc:
        raise ValueError("scaled factor-risk arithmetic must be representable") from exc
    rank = factor.shape[1]
    inner_solves = 0

    def evaluate(dual, weights=None):
        nonlocal inner_solves
        try:
            with np.errstate(over="raise", invalid="raise", divide="raise"):
                adjusted_mu = mu - loading @ dual
                if weights is None:
                    weights = diagonal_allocate(adjusted_mu, held, variance, beta, costs,
                                                gamma, horizon, cap)
                inner_solves += 1
                envelope = (adjusted_mu @ weights - 0.5 * diagonal @ (weights*weights)
                            - penalty @ np.abs(weights-held))
                value = float(0.5 * dual @ dual + envelope)
                gradient = dual - loading.T @ weights
        except FloatingPointError as exc:
            raise ValueError("factor-dual arithmetic must be representable") from exc
        if not np.isfinite(value) or not np.isfinite(gradient).all():
            raise ValueError("factor-dual arithmetic produced nonfinite values")
        return value, gradient, weights

    dual = np.zeros(rank)
    value, gradient, weights = evaluate(dual, first_weights)
    for iteration in range(max_iterations+1):
        residual = float(np.max(np.abs(gradient)))
        tolerance = 1e-11 * (1 + float(np.max(np.abs(dual))))
        if residual <= tolerance:
            return weights, {"converged": True, "iterations": iteration,
                "inner_solves": inner_solves, "dual_gradient_inf": residual,
                "factor_rank": rank, "dual_value": value}
        if iteration == max_iterations:
            break

        # In a quadratic segment the inner response is inverse diagonal risk
        # on trading, unboxed assets, projected onto the beta equality.
        edge_tolerance = 64*np.finfo(np.float64).eps*np.maximum(1.0, cap)
        active = ((np.abs(weights) < cap-edge_tolerance)
                  & ((penalty == 0) | (np.abs(weights-held) > edge_tolerance)))
        inverse = np.where(active, 1.0/diagonal, 0.0)
        weighted_loading = inverse[:,None]*loading
        hessian = np.eye(rank) + loading.T @ weighted_loading
        inverse_beta = inverse*b
        beta_denominator = float(b @ inverse_beta)
        if beta_denominator > 0:
            cross = loading.T @ inverse_beta
            hessian -= np.outer(cross,cross)/beta_denominator
        hessian = (hessian+hessian.T)*0.5
        try:
            direction = np.linalg.solve(hessian,-gradient)
        except np.linalg.LinAlgError as exc:
            raise RuntimeError("Factor dual Newton system could not be solved") from exc
        slope = float(gradient @ direction)
        if not np.isfinite(direction).all() or not np.isfinite(slope) or slope >= 0:
            direction = -gradient
            slope = -float(gradient@gradient)
        step = 1.0
        for _ in range(40):
            trial = dual + step*direction
            trial_value, trial_gradient, trial_weights = evaluate(trial)
            rounding = 32*np.finfo(np.float64).eps*max(1.0,abs(value))
            if trial_value <= value + 1e-4*step*slope + rounding:
                dual,value,gradient,weights = trial,trial_value,trial_gradient,trial_weights
                break
            step *= 0.5
        else:
            raise RuntimeError("Factor dual line search did not establish descent")
    raise RuntimeError(f"Factor optimizer did not converge after {max_iterations} iterations; residual={residual:.6g}")
