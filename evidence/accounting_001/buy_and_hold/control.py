"""Synthetic buy-and-hold control with no forecast."""
import numpy as np
CALLS = []

def rebalance(held_positions):
    day = 252 + len(CALLS)
    target = np.array([0.5, 0.5]) if not CALLS else held_positions.copy()
    CALLS.append({"day": day, "earning_day": day + 1,
                  "held": held_positions.copy().tolist(),
                  "target": target.copy().tolist()})
    return target
