"""Run a strategy over the data and print its score.

    python score.py strategy
    python score.py example_naive_mv
"""
import importlib
import inspect
import sys
import time

import numpy as np
import pandas as pd

START = 252  # the first day positions are taken, so there is a year of history to look back on


def load(folder="."):
    """The three CSVs as arrays: returns (days, stocks), characteristics (days, stocks, k), costs (stocks,)."""
    returns = pd.read_csv(f"{folder}/returns.csv", index_col="day")
    characteristics = pd.read_csv(f"{folder}/characteristics.csv", index_col=["day", "stock"])
    costs = pd.read_csv(f"{folder}/costs.csv", index_col="stock")["cost"]
    characteristics = characteristics.to_numpy().reshape(len(returns), len(costs), -1)
    return returns.to_numpy(), characteristics, costs.to_numpy()


def with_declared_arguments(function):
    """Wrap a function so it receives only the named arguments it declares."""
    parameters = inspect.signature(function).parameters
    takes_everything = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values())
    return lambda **named: function(**(named if takes_everything else {k: v for k, v in named.items() if k in parameters}))


def run(strategy, all_returns, all_characteristics, trading_costs, start=START):
    """forecast once over everything (if the strategy has one), then rebalance day by day from an empty book.

    Returns one row per scored day (portfolio return, trading cost, gross exposure, equal-weight market
    return, seconds spent in rebalance) and the seconds spent in forecast.
    """
    days, number_of_stocks = all_returns.shape
    forecasts, forecast_seconds = None, 0.0
    if hasattr(strategy, "forecast"):
        tic = time.perf_counter()
        forecasts = np.asarray(with_declared_arguments(strategy.forecast)(
            returns_history=all_returns, characteristics_history=all_characteristics, trading_costs=trading_costs), dtype=float)
        forecast_seconds = time.perf_counter() - tic
        assert len(forecasts) == days, "forecast must return one row per day"
    rebalance = with_declared_arguments(strategy.rebalance)

    positions = np.zeros(number_of_stocks)
    rows = []
    for today in range(start, days - 1):
        # 1. today's returns come in and move the positions
        portfolio_return_today = positions @ all_returns[today]
        assert portfolio_return_today > -1, "the book lost everything"
        positions = positions * (1 + all_returns[today]) / (1 + portfolio_return_today)
        # 2. rebalance sees everything through today, and tomorrow's row of the forecast
        tic = time.perf_counter()
        new_positions = np.asarray(rebalance(
            held_positions=positions,
            expected_returns=None if forecasts is None else forecasts[today + 1],
            returns_history=all_returns[: today + 1],
            characteristics_history=all_characteristics[: today + 1],
            trading_costs=trading_costs,
        ), dtype=float)
        rebalance_seconds = time.perf_counter() - tic
        # 3. trade there, paying each stock's cost on the change; the first trade is free
        cost_today = 0.0 if today == start else trading_costs @ np.abs(new_positions - positions)
        rows.append((portfolio_return_today, cost_today, np.abs(new_positions).sum(), all_returns[today].mean(), rebalance_seconds))
        positions = new_positions
        # 4. tomorrow's returns are earned on new_positions, at the top of the next loop
    return np.array(rows)[1:], forecast_seconds  # the first row held nothing yet


def report(name, rows, forecast_seconds, days):
    portfolio_return, cost, gross, market_return, rebalance_seconds = rows.T
    net = portfolio_return - cost
    sharpe = 252 ** 0.5 * net.mean() / net.std()
    market_centered = market_return - market_return.mean()
    beta = (market_centered @ (net - net.mean())) / (market_centered @ market_centered)
    print(f"{name:22s} sharpe {sharpe:5.2f}   return {net.mean() * 252:6.1%}/yr   vol {net.std() * 252 ** 0.5:5.1%}   "
          f"beta {beta:5.2f}   cost {cost.mean() * 252:.2%}/yr   gross {gross.mean():.2f}   "
          f"forecast {forecast_seconds:.1f}s ({forecast_seconds / days * 25200 / 3600:.2f} h per century)   "
          f"rebalance {1000 * rebalance_seconds.mean():.1f} ms/call")


if __name__ == "__main__":
    all_returns, all_characteristics, trading_costs = load()
    for name in sys.argv[1:] or ["example_equal_weight", "example_naive_mv"]:
        rows, forecast_seconds = run(importlib.import_module(name), all_returns, all_characteristics, trading_costs)
        report(name, rows, forecast_seconds, len(all_returns))
