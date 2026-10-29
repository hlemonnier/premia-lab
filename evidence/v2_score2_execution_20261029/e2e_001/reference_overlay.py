"""Bounded research-only volatility overlay on an unchanged virtual V2 book.

The original scorer owns actual drift and actual fees. This wrapper independently
maintains the base V2 portfolio, with the scorer's gross-return drift convention.
See PLAN.md and the preimplementation e2e.py; not production submission code.
"""
import numpy as np


class VolatilityOverlay:
    def __init__(self, engine, config, power):
        if power not in (0.0,0.5,1.0):
            raise ValueError("only fixed-one control, VTvol, and VTvar are admitted")
        self.engine=engine
        self.config=dict(config)
        self.power=float(power)
        self.forecast_output=None
        self.records=[]

    def forecast(self, returns_history, characteristics_history):
        self.virtual_target=np.zeros(returns_history.shape[1],dtype=np.float64)
        self.previous_actual=np.zeros_like(self.virtual_target)
        self.last_day=None
        self.earned=0
        self.sums={63:0.0,1008:0.0}
        self.masses={63:0.0,1008:0.0}
        self.records=[]
        self.engine.configure(self.config)
        self.forecast_output=self.engine.forecast(returns_history,characteristics_history)
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        if self.forecast_output is None:
            raise RuntimeError("forecast must start the scoring session")
        t=len(returns_history)-1
        if self.last_day is not None and t!=self.last_day+1:
            raise RuntimeError("rebalance calls must advance one published row")
        today=returns_history[-1]
        g=float(self.virtual_target @ today)
        if not np.isfinite(g) or g<=-1:
            raise RuntimeError("virtual base book has nonfinite return or is ruined")
        virtual_held=self.virtual_target*(1+today)/(1+g)
        if self.last_day is not None:
            self.earned+=1
            for hl in self.sums:
                decay=2.0**(-1.0/hl)
                self.sums[hl]=decay*self.sums[hl]+g*g
                self.masses[hl]=decay*self.masses[hl]+1.0
        q={hl:self.sums[hl]/self.masses[hl] if self.masses[hl] else 0.0 for hl in self.sums}
        ratio=max(q[1008],1e-12)/max(q[63],1e-12)
        a=1.0 if self.earned<63 else float(np.clip(ratio**self.power,.5,2.0))
        v=self.engine.rebalance(virtual_held,expected_returns,returns_history,
                                characteristics_history,trading_costs)
        proposed=a*v
        pre_gross=float(np.abs(proposed).sum())
        gross_scale=min(1.0,5.0/pre_gross) if pre_gross else 1.0
        target=proposed*gross_scale
        actual_g=float(self.previous_actual @ today)
        if not np.isfinite(target).all() or actual_g<=-1:
            raise RuntimeError("actual book has nonfinite target or is ruined")
        independent_held=self.previous_actual*(1+today)/(1+actual_g)
        held_error=float(np.max(np.abs(independent_held-held_positions)))
        cert=self.engine.CERTIFICATES[-1]
        first=self.last_day is None
        self.records.append({"decision_index":t,"earned_observations":self.earned,
            "virtual_gross_return":g,"q63":q[63],"q1008":q[1008],"moment_ratio":ratio,
            "multiplier":a,"aggregate_gross_scale":gross_scale,
            "virtual_gross":float(np.abs(v).sum()),"proposed_gross":pre_gross,
            "actual_gross":float(np.abs(target).sum()),"actual_net_dollars":float(target.sum()),
            "max_abs_actual_weight":float(np.max(np.abs(target))),
            "actual_return":actual_g,"supplied_held_identity_error":held_error,
            "actual_fee":0.0 if first else float(trading_costs @ np.abs(target-held_positions)),
            "virtual_fee":0.0 if first else float(trading_costs @ np.abs(v-virtual_held)),
            "certificate_status":cert["status"],"certificate_gap":cert["gap"],
            "virtual_target":v.copy(),"actual_target":target.copy()})
        self.virtual_target=v.copy()
        self.previous_actual=target.copy()
        self.last_day=t
        return target
