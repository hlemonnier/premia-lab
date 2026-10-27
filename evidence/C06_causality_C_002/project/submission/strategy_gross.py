"""C07: unchanged C02 forecasts/risk with an exact joint gross constraint.

The first discovery runs showed habitual proportional scaling after a
cost-aware allocation. Such scaling changes both that objective's optimum and
its no-trade behavior. This controlled candidate solves the same diagonal-risk
and drift-aware cost objective under beta, stock and gross constraints jointly.
It does not rescale the returned book. Whether this improves net performance
is an empirical question under the frozen research protocol.

Forecast and causal risk estimation are delegated unchanged to C02. The new
pure optimizer uses scalar closed-form solutions for absolute costs about held
positions and an L1 gross penalty, then solves the beta and gross multipliers.
It raises on unresolved numerical convergence; there is no hidden proportional
fallback. Full actual fees remain in the unchanged official scorer.

This is AI-produced development research with no claimed applicant discovery or
unexecuted future result. Remaining risks include forecast noise, omitted common
covariance, parameter instability and numerical/runtime behavior on long unseen
histories. Requires strategy.py, portfolio.py and gross_portfolio.py; NumPy.
"""
from __future__ import annotations
import numpy as np

if __package__:
    from . import strategy as base
    from .gross_portfolio import allocate_gross
else:
    import strategy as base
    from gross_portfolio import allocate_gross

CONFIG={}
_LAST_DIAGNOSTICS={}


def configure(config):
    global CONFIG,_LAST_DIAGNOSTICS
    if not isinstance(config,dict):raise ValueError("configuration must be a dictionary")
    base.configure({"candidate_id":"C07_additive_exact_gross","basis":"additive",**config})
    CONFIG=dict(base.CONFIG)
    _LAST_DIAGNOSTICS={}


def forecast(returns_history,characteristics_history,trading_costs):
    return base.forecast(returns_history,characteristics_history,trading_costs)


def estimate_risk(returns_history):
    return base.estimate_risk(returns_history)


def rebalance(held_positions,expected_returns,returns_history,trading_costs):
    global _LAST_DIAGNOSTICS
    if expected_returns is None:raise ValueError("this strategy requires its forecast row")
    beta,variance=base.estimate_risk(returns_history)
    weights,info=allocate_gross(expected_returns,held_positions,variance,beta,trading_costs,
        CONFIG["risk_aversion"],CONFIG["cost_horizon"],CONFIG["weight_cap"],CONFIG["gross_cap"])
    gross=float(np.abs(weights).sum())
    _LAST_DIAGNOSTICS={"pre_scale_gross":gross,"gross_scale":1.,
        "pre_scale_box_saturation_fraction":float(np.mean(np.abs(weights)>=CONFIG["weight_cap"]-1e-14)),
        "post_scale_estimated_beta":float(beta@weights),
        "gross_unconstrained_target":info["unconstrained_gross"],
        "gross_budget_bound":info["gross_budget_bound"],"gross_multiplier":info["gross_multiplier"],
        "gross_solver_iterations":info["gross_iterations"],"gross_scalar_evaluations":info["scalar_evaluations"],
        "gross_constraint_excess":info["gross_excess"],"gross_normalized_beta_residual":info["normalized_beta_residual"]}
    return weights


def get_last_diagnostics():return dict(_LAST_DIAGNOSTICS)


configure({})
