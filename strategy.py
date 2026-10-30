"""Premia Lab: compatibility entry point for the single maintained N0 policy.

Forecast row t uses observations strictly before t. Both alpha and risk channels
are returned; the sequential allocator receives the next forecast row, published
histories, one-way costs and drifted holdings. Model settings are frozen.

This is experimental research software, not a live trading service. Recorded
benchmark results use an exposed simulated history. The independent public demo
does not reproduce that benchmark or establish out-of-sample performance.
"""
from model_n0 import N0Policy

POLICY = N0Policy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
