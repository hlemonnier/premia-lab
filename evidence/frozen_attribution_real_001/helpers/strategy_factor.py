"""C04 development challenger: C02 alpha with causal residual-factor risk.

This wrapper preserves C02's forecasts, marginal variances, market beta, cost
horizon and position caps. Every21 closes it estimates ten factors from only
the trailing252 market-residual correlation observations. Half of that leading
factor covariance is retained. The loadings are rescaled by today's causal
marginal variances, and an explicit diagonal remainder preserves those marginal
variances exactly. Its risk model penalizes common residual exposures instead
of forcing their expected returns to zero.

Only rebalance populates the factor cache. Full-history forecast delegates to
the base causal learner and cannot initialize future risk state. Configure
resets the cache. The numerical factor optimizer preserves the base estimated
beta equality, stock box and drift-aware costs. A rare nonconvergence falls
back to the base diagonal allocation and is recorded; routine fallback is a
research failure. Actual fees are always charged in full by the original
scorer. The inherited gross rescale remains an approximation to the constrained
objective and its frequency is reported.

This design, implementation and numerical verification are AI work. It is a
development candidate, with no claimed human empirical discovery or unexecuted
performance, validation, audit or hidden-future result. Common-risk estimates
can be unstable, stale, or correlated with useful alpha; the complete net
comparison determines whether this extra model earns a place.

Requires strategy.py, portfolio.py and factor_portfolio.py; NumPy and SciPy.
"""
from __future__ import annotations

import math
from numbers import Integral, Real
import numpy as np
from scipy.linalg import eigh

if __package__:
    from . import strategy as base
    from .factor_portfolio import allocate_factor
    from .portfolio import allocate as diagonal_allocate
else:
    import strategy as base
    from factor_portfolio import allocate_factor
    from portfolio import allocate as diagonal_allocate


_FACTOR_DEFAULTS = {"factor_rank":10, "factor_shrinkage":0.5, "factor_refresh_days":21}
CONFIG = {}
_CACHE = None
_LAST_HISTORY_LENGTH = None
_LAST_DIAGNOSTICS = {}


def configure(config):
    """Configure the parent learner and reset all causal portfolio state."""
    global CONFIG,_CACHE,_LAST_HISTORY_LENGTH,_LAST_DIAGNOSTICS
    if not isinstance(config,dict):
        raise ValueError("configuration must be a dictionary")
    factor = {key:config.get(key,value) for key,value in _FACTOR_DEFAULTS.items()}
    for key in ("factor_rank","factor_refresh_days"):
        if isinstance(factor[key],bool) or not isinstance(factor[key],Integral) or factor[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
        factor[key]=int(factor[key])
    shrink=factor["factor_shrinkage"]
    if isinstance(shrink,bool) or not isinstance(shrink,Real) or not math.isfinite(shrink) or not 0 <= shrink < 1:
        raise ValueError("factor_shrinkage must lie in [0,1)")
    factor["factor_shrinkage"]=float(shrink)
    parent={"basis":"additive","candidate_id":"C04_additive_factor",
            **{key:value for key,value in config.items() if key not in _FACTOR_DEFAULTS}}
    base.configure(parent)
    CONFIG={**base.CONFIG,**factor}
    _CACHE=None
    _LAST_HISTORY_LENGTH=None
    _LAST_DIAGNOSTICS={}


def forecast(returns_history,characteristics_history,trading_costs):
    return base.forecast(returns_history,characteristics_history,trading_costs)


def estimate_risk(returns_history):
    return base.estimate_risk(returns_history)


def _correlation_factors(returns_history,beta):
    window=np.asarray(returns_history[-CONFIG["risk_window"]:],dtype=np.float64)
    n=window.shape[1]
    if len(window)<CONFIG["risk_min_days"] or CONFIG["factor_shrinkage"]==0:
        return np.empty((n,0))
    centered=window-window.mean(axis=0)
    market=window.mean(axis=1)
    market-=market.mean()
    residual=centered-market[:,None]*beta
    raw_variance=np.mean(residual*residual,axis=0)
    standardized=residual/np.sqrt(np.maximum(raw_variance,CONFIG["variance_floor"]))
    gram=(standardized@standardized.T)/len(window)
    rank=min(CONFIG["factor_rank"],len(window))
    eigenvalues,vectors=eigh(gram,subset_by_index=[len(window)-rank,len(window)-1],check_finite=False)
    keep=eigenvalues>1e-12
    # Z.T v / sqrt(T) already equals U sqrt(lambda), avoiding division by
    # tiny eigenvalues when residual correlation is nearly rank deficient.
    loadings=(standardized.T@vectors[:,keep])*math.sqrt(CONFIG["factor_shrinkage"]/len(window))
    energy=np.sum(loadings*loadings,axis=1)
    # Exact arithmetic has energy <= shrinkage. Bound numerical excess only.
    over=energy>CONFIG["factor_shrinkage"]
    if np.any(over):
        loadings[over]*=np.sqrt(CONFIG["factor_shrinkage"]/energy[over])[:,None]
    if not np.isfinite(loadings).all():
        raise ValueError("factor estimation produced nonfinite loadings")
    return loadings


def rebalance(held_positions,expected_returns,returns_history,trading_costs):
    global _CACHE,_LAST_HISTORY_LENGTH,_LAST_DIAGNOSTICS
    if expected_returns is None:
        raise ValueError("this strategy requires its forecast row")
    count=len(returns_history)
    beta,variance=base.estimate_risk(returns_history)
    epoch=max(0,(count-253)//CONFIG["factor_refresh_days"])
    if _LAST_HISTORY_LENGTH is not None and count<=_LAST_HISTORY_LENGTH:
        _CACHE=None
    refreshed=_CACHE is None or _CACHE["epoch"]!=epoch
    if refreshed:
        _CACHE={"epoch":epoch,"observed_rows":count,
                "loadings":_correlation_factors(returns_history,beta)}
    _LAST_HISTORY_LENGTH=count
    correlation_loadings=_CACHE["loadings"]
    factors=np.sqrt(variance)[:,None]*correlation_loadings
    factor_diagonal=np.sum(factors*factors,axis=1)
    diagonal=variance-factor_diagonal
    if np.any(diagonal<=0) or not np.isfinite(diagonal).all():
        raise ValueError("factor covariance remainder must be positive and finite")
    fallback=0
    try:
        weights,solver=allocate_factor(expected_returns,held_positions,diagonal,factors,beta,trading_costs,
            CONFIG["risk_aversion"],CONFIG["cost_horizon"],CONFIG["weight_cap"])
    except RuntimeError:
        weights=diagonal_allocate(expected_returns,held_positions,variance,beta,trading_costs,
            CONFIG["risk_aversion"],CONFIG["cost_horizon"],CONFIG["weight_cap"])
        solver={"iterations":-1,"inner_solves":-1,"dual_gradient_inf":-1.0}
        fallback=1
    gross=float(np.abs(weights).sum())
    scale=min(1.0,CONFIG["gross_cap"]/gross) if gross else 1.0
    saturation=float(np.mean(np.abs(weights)>=CONFIG["weight_cap"]-1e-14))
    weights=weights*scale
    _LAST_DIAGNOSTICS={"pre_scale_gross":gross,"gross_scale":scale,
        "pre_scale_box_saturation_fraction":saturation,"post_scale_estimated_beta":float(beta@weights),
        "factor_refreshed":int(refreshed),"factor_age_days":count-_CACHE["observed_rows"],
        "factor_rank":factors.shape[1],"factor_fallback":fallback,
        "factor_dual_iterations":solver["iterations"],"factor_inner_solves":solver["inner_solves"],
        "factor_dual_gradient_inf":solver["dual_gradient_inf"],
        "factor_max_diagonal_fraction":float(np.max(factor_diagonal/variance)),
        "factor_diagonal_identity_error":float(np.max(np.abs(diagonal+factor_diagonal-variance)))}
    return weights


def get_last_diagnostics():
    return dict(_LAST_DIAGNOSTICS)


configure({})
