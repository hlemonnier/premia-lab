"""Your strategy.

Write a short note here: what you came to believe about this market, what you built and
why, where the AI did the work and where you did, and what you expect to go wrong over a
long time. A page is plenty.
"""
import numpy as np


def forecast(returns_history, characteristics_history, trading_costs):
    """Optional. Runs once over the whole history, before the clock starts.

    returns_history          (days, n) every daily return, oldest first
    characteristics_history  (days, n, k) the characteristics published each day
    trading_costs            (n,) one-way trading cost per stock

    Returns an array whose first axis is days. Row t is handed to rebalance as
    expected_returns when it positions for day t, so row t may use days before t only.
    Delete this function if you do not need it.
    """
    return np.zeros_like(returns_history)


def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    """Required. The positions to hold through tomorrow. You pay trading_costs @ abs(new - held).

    Declare any of these five, by name; the ones you leave out are not passed.
    held_positions           (n,) what you hold now, after today's returns have moved it
    expected_returns         tomorrow's row of your forecast, or None if you have no forecast
    returns_history          (days, n) every daily return through today, oldest first
    characteristics_history  (days, n, k) every day's characteristics through today
    trading_costs            (n,) one-way trading cost per stock

    Returns an (n,) array: the fraction of capital in each stock through tomorrow.
    """
    number_of_stocks = len(held_positions)
    return np.full(number_of_stocks, 1 / number_of_stocks)
