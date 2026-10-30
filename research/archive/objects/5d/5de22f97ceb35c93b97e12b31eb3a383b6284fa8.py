"""Synthetic scheduled-trade control, not a candidate strategy."""
import numpy as np
CALLS = []
FORECAST_INPUT_SHAPES = []

def forecast(returns_history, characteristics_history, trading_costs):
    FORECAST_INPUT_SHAPES.append([list(returns_history.shape),
                                  list(characteristics_history.shape),
                                  list(trading_costs.shape)])
    clock = np.arange(len(returns_history), dtype=float)
    return np.column_stack([clock, -clock])

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    day = len(returns_history) - 1
    if day in (252, 253):
        target = np.array([0.5, 0.5])
    elif day == 254:
        target = np.array([-0.3, 0.3])
    else:
        raise ValueError(f"Unexpected synthetic decision day: {day}")
    CALLS.append({"day": day, "earning_day": day + 1,
                  "held": held_positions.copy().tolist(),
                  "target": target.copy().tolist(),
                  "expected_returns": expected_returns.copy().tolist(),
                  "returns_shape": list(returns_history.shape),
                  "characteristics_shape": list(characteristics_history.shape),
                  "latest_return": returns_history[-1].copy().tolist(),
                  "costs": trading_costs.copy().tolist()})
    return target
