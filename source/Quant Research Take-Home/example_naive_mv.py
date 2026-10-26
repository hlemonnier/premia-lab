"""Trailing one-year mean return as the forecast; each day, mean-variance on the trailing year's
covariance, charged for the trade it takes to get there."""
import cvxpy as cp
import numpy as np

WINDOW = 252         # trading days in the look-back
RISK_AVERSION = 50   # weight on variance against expected return; it sets the size of the book


def forecast(returns_history):
    """Row t: the mean return over the WINDOW days before day t. One pass over the history via a running total."""
    days, number_of_stocks = returns_history.shape
    running_total = np.vstack([np.zeros((1, number_of_stocks)), np.cumsum(returns_history, axis=0)])  # running_total[t] = sum of rows before t
    window_start = np.maximum(np.arange(days) - WINDOW, 0)
    days_in_window = np.maximum(np.arange(days) - window_start, 1)
    expected_returns = (running_total[np.arange(days)] - running_total[window_start]) / days_in_window[:, None]
    return expected_returns


def rebalance(held_positions, expected_returns, returns_history, trading_costs):
    trailing_returns = returns_history[-WINDOW:]                     # the last year, through today
    new_positions = cp.Variable(len(held_positions))
    portfolio_variance = cp.sum_squares(trailing_returns @ new_positions) / len(trailing_returns)
    cost_of_trading = trading_costs @ cp.abs(new_positions - held_positions)
    objective = expected_returns @ new_positions - RISK_AVERSION * portfolio_variance - cost_of_trading
    cp.Problem(cp.Maximize(objective)).solve()
    return new_positions.value
