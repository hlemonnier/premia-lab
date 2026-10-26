"""No forecast. Hold every stock at 0.1 percent of capital."""
import numpy as np


def rebalance(held_positions):
    number_of_stocks = len(held_positions)
    return np.full(number_of_stocks, 1 / number_of_stocks)
