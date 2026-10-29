"""One fixed stock-replicated market sleeve around an independent inner book.

Research implementation of the prospectively specified M0/M1 policies. The
original scorer owns actual trades and fees. No market instrument is assumed.
"""
import numpy as np


class MarketSleeve:
    def __init__(self, inner, sleeve):
        if sleeve not in (0.0, .05):
            raise ValueError("only the registered M0=0 and M1=0.05 sleeves are admitted")
        self.inner = inner
        self.sleeve = float(sleeve)
        self.forecast_output = None
        self.records = []

    def forecast(self, returns_history, characteristics_history):
        n = returns_history.shape[1]
        self.inner_target = np.zeros(n, dtype=np.float64)
        self.previous_actual = np.zeros(n, dtype=np.float64)
        self.last_day = None
        self.records = []
        self.forecast_output = self.inner.forecast(returns_history, characteristics_history)
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        if self.forecast_output is None:
            raise RuntimeError("forecast must start the market-sleeve session")
        t = len(returns_history)-1
        if self.last_day is not None and t != self.last_day+1:
            raise RuntimeError("market-sleeve decisions must advance one published row")
        r = returns_history[-1]
        inner_gross = float(self.inner_target @ r)
        actual_gross = float(self.previous_actual @ r)
        if not np.isfinite(inner_gross) or inner_gross <= -1:
            raise RuntimeError("inner portfolio has a nonfinite return or is ruined")
        if not np.isfinite(actual_gross) or actual_gross <= -1:
            raise RuntimeError("actual portfolio has a nonfinite return or is ruined")
        inner_held = self.inner_target*(1+r)/(1+inner_gross)
        expected_actual_held = self.previous_actual*(1+r)/(1+actual_gross)
        held_error = float(np.max(np.abs(expected_actual_held-held_positions)))
        inner_target = np.asarray(self.inner.rebalance(
            inner_held, expected_returns, returns_history,
            characteristics_history, trading_costs), dtype=np.float64)
        if inner_target.shape != self.inner_target.shape or not np.isfinite(inner_target).all():
            raise RuntimeError("inner policy returned an invalid target")
        proposed = inner_target + self.sleeve/len(inner_target)
        proposed_gross = float(np.abs(proposed).sum())
        gross_scale = min(1.0, 5.0/proposed_gross) if proposed_gross else 1.0
        target = proposed*gross_scale
        if not np.isfinite(target).all():
            raise RuntimeError("market sleeve produced a nonfinite target")
        first = self.last_day is None
        inner_records = getattr(self.inner, "records", None)
        latest_inner = inner_records[-1] if inner_records else {}
        self.records.append({
            "decision_index": t,
            "sleeve": self.sleeve,
            "inner_gross_return": inner_gross,
            "actual_gross_return": actual_gross,
            "outer_held_identity_error": held_error,
            "inner_held_identity_error": float(latest_inner.get("supplied_held_identity_error", 0.0)),
            "inner_gross": float(np.abs(inner_target).sum()),
            "proposed_gross": proposed_gross,
            "outer_gross_scale": gross_scale,
            "actual_gross": float(np.abs(target).sum()),
            "actual_net_dollars": float(target.sum()),
            "max_abs_actual_weight": float(np.abs(target).max()),
            "actual_fee": 0.0 if first else float(trading_costs @ np.abs(target-held_positions)),
            "certificate_status": latest_inner.get("certificate_status", "not_applicable"),
            "actual_target": target.copy(),
            "inner_target": inner_target.copy(),
        })
        self.inner_target = inner_target.copy()
        self.previous_actual = target.copy()
        self.last_day = t
        return target
