"""C06: C05 covariance-weighted forecasts with the unchanged C04 portfolio.

This controlled combination has no separate alpha fit or altered risk policy.
Forecast delegates to C05, whose learned state stays local. Rebalance delegates
to C04, which initializes its factor cache only from available close history.
Configure supplies identical common controls to both and resets portfolio state.

This is AI-produced development research; see the component notes and recorded
experiments for assumptions, limitations and executed evidence. No performance,
causality or hidden-future result is claimed by this source file itself.

Requires strategy_gls.py, gls_precision.py, strategy_factor.py,
factor_portfolio.py, strategy.py and portfolio.py; NumPy and SciPy.
"""
from __future__ import annotations

if __package__:
    from . import strategy_gls as learner
    from . import strategy_factor as portfolio
else:
    import strategy_gls as learner
    import strategy_factor as portfolio


CONFIG = {}


def configure(config):
    """Share common controls while keeping learner and portfolio knobs explicit."""
    global CONFIG
    if not isinstance(config, dict):
        raise ValueError("configuration must be a dictionary")
    chosen = {"candidate_id": "C06_gls_factor", "basis": "additive", **config}
    learner.configure({key: value for key, value in chosen.items()
                       if key not in portfolio._FACTOR_DEFAULTS})
    portfolio.configure({key: value for key, value in chosen.items()
                         if key not in learner._LEARNING_DEFAULTS})
    CONFIG = {**learner.CONFIG, **portfolio.CONFIG}


def forecast(returns_history, characteristics_history, trading_costs):
    return learner.forecast(returns_history, characteristics_history, trading_costs)


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    return portfolio.rebalance(held_positions, expected_returns, returns_history, trading_costs)


def estimate_risk(returns_history):
    return portfolio.estimate_risk(returns_history)


def get_last_diagnostics():
    return portfolio.get_last_diagnostics()


configure({})
