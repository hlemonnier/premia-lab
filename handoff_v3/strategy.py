"""V3: characteristic factor-risk strategy with adaptive premia, cost-aware execution and a fixed
market position. Draft note, 29 October 2026; candidate under review.

[Note to be completed: see research/v2/SCORE2_RESEARCH_RESULTS_20261029.md and
verification/V3_INTEGRATION_SPEC.md. The applicant writes the contribution section.]

Required files: model_v3/__init__.py, engine.py, allocator.py, policy.py. NumPy and the
Python standard library only.
"""

from model_v3 import engine as _engine
from model_v3.policy import ScorePolicy

_CONFIG = {
    "alpha_half_life": 1008.0, "ridge": 0.1, "min_training_days": 126, "feature_clip": 4.0,
    "beta_window": 252, "factor_half_life": 126.0, "specific_half_life": 126.0,
    "specific_shrinkage": 0.2, "variance_floor": 1e-6, "factor_risk_scale": 0.3,
    "risk_aversion": 200.0, "cost_horizon": 20.0, "weight_cap": 0.05, "gross_cap": 5.0,
}

_engine.configure(_CONFIG)
POLICY = ScorePolicy(dict(_engine.CONFIG), sleeve=0.05, outer_gross_cap=5.0)


def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)


def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
