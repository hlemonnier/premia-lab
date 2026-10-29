"""Two predeclared cost-aware execution policies on an independent F2 book.

The inherited overlay owns the unchanged virtual book and desired volatility
multiplier. The original scorer owns actual drift and fees. Research only.
"""
import numpy as np

from reference_overlay import VolatilityOverlay


def _scalar_projection(v, held, costs, desired, q63):
    """Global minimizer of a strictly convex quadratic plus weighted absolute terms."""
    gross=float(np.abs(v).sum())
    lo=.5; hi=2. if gross<=2.5 else 5./gross
    if hi<lo: raise RuntimeError("infeasible scalar interval from virtual book")
    curvature=200.*max(float(q63),1e-12)
    nz=(v!=0)&(costs>0)
    if not np.any(nz):
        a=float(np.clip(desired,lo,hi))
    else:
        ratios=held[nz]/v[nz]
        weights=costs[nz]*np.abs(v[nz])/20.
        order=np.argsort(ratios,kind="stable")
        ratios=ratios[order]; weights=weights[order]
        cumulative=np.r_[0.,np.cumsum(weights)]
        total=float(cumulative[-1])
        knots=np.unique(np.r_[lo,ratios[(ratios>lo)&(ratios<hi)],hi])
        counts=np.searchsorted(ratios,knots,side="right")
        slopes=2*cumulative[counts]-total
        right_derivative=curvature*(knots-desired)+slopes
        crossing=np.flatnonzero(right_derivative>=0)
        if len(crossing)==0:
            a=float(hi)
        else:
            j=int(crossing[0])
            if j==0:
                a=float(lo)
            else:
                smooth_root=desired-slopes[j-1]/curvature
                a=float(np.clip(smooth_root,knots[j-1],knots[j]))
    residual=a*v-held
    tie_tol=16*np.finfo(float).eps*max(1.,float(np.abs(held).max(initial=0)),
                                      float(np.abs(a*v).max(initial=0)))
    tied=np.abs(residual)<=tie_tol
    central=curvature*(a-desired)+float((costs[~tied]*v[~tied])@np.sign(residual[~tied]))/20.
    radius=float(costs[tied]@np.abs(v[tied]))/20.
    left,right=central-radius,central+radius
    if a<=lo+1e-12: kkt=max(0.,-right)
    elif a>=hi-1e-12: kkt=max(0.,left)
    else: kkt=max(0.,left,-right)
    comparator=float(np.clip(desired,lo,hi))
    obj=.5*curvature*(a-desired)**2+float(costs@np.abs(a*v-held))/20.
    ref=.5*curvature*(comparator-desired)**2+float(costs@np.abs(comparator*v-held))/20.
    info={"scalar_lower_bound":lo,"scalar_upper_bound":hi,
          "scalar_left_derivative":left,"scalar_right_derivative":right,
          "scalar_kkt_residual":kkt,"scalar_objective":obj,
          "scalar_comparator_objective":ref}
    if not np.isfinite(a) or kkt>1e-10 or obj>ref+1e-12:
        raise RuntimeError("uncertified scalar projection: "+str(info))
    return a,info


class ExecutionOverlay(VolatilityOverlay):
    def __init__(self, engine, config, mode, actual_engine=None, record_arrays=True):
        if mode not in ("baseline","E1","E2"):
            raise ValueError("only baseline/E1/E2 are declared")
        if mode=="E2" and (actual_engine is None or actual_engine is engine):
            raise ValueError("E2 requires an independent actual engine")
        required={"risk_aversion":200.,"cost_horizon":20.,"weight_cap":.05,
                  "gross_cap":5.,"beta_target":0.}
        if any(config[k]!=v for k,v in required.items()):
            raise ValueError("execution experiments require unchanged declared V2 settings")
        super().__init__(engine,config,power=.5)
        self.mode=mode; self.actual_engine=actual_engine
        self.record_arrays=bool(record_arrays)

    def forecast(self, returns_history, characteristics_history):
        if self.actual_engine is not None:
            self.actual_engine.configure(self.config)
            self.actual_engine.CERTIFICATES.clear()
        return super().forecast(returns_history,characteristics_history)

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        costs=np.asarray(trading_costs,dtype=np.float64)
        if costs.shape!=held_positions.shape or not np.isfinite(costs).all() or np.any(costs<0):
            raise ValueError("finite nonnegative per-stock costs are required")
        reference_target=super().rebalance(held_positions,expected_returns,returns_history,
                                          characteristics_history,costs)
        rec=self.records[-1]; v=rec["virtual_target"]
        desired=rec["multiplier"]; a=desired
        rec["mode"]=self.mode; rec["desired_multiplier"]=desired
        rec["reference_gross_scale"]=rec["aggregate_gross_scale"]
        rec["scalar_kkt_residual"]=0.0
        rec["actual_certificate_status"]="not_applicable"
        rec["actual_certificate_gap"]=0.0
        rec["actual_state_upto"]=-1
        rec["virtual_state_upto"]=int(self.engine._STATE.upto)
        if rec["certificate_status"] not in ("ok","ok_after_recovery"):
            raise RuntimeError("uncertified virtual solve")
        if self.mode=="E1":
            if self.earned>=63:
                a,info=_scalar_projection(v,held_positions,costs,desired,rec["q63"])
                rec.update(info)
            else:
                a=1.
            target=a*v
            rec["multiplier"]=a
            rec["aggregate_gross_scale"]=1.
        elif self.mode=="E2":
            # These allocation fields are not used by risk absorption. Mutating
            # them preserves this engine's independent risk and warm history;
            # configure() here would erase that history every day.
            self.actual_engine.CONFIG["risk_aversion"]=200./desired
            self.actual_engine.CONFIG["weight_cap"]=.05*desired
            target=self.actual_engine.rebalance(held_positions,expected_returns,
                returns_history,characteristics_history,costs)
            cert=self.actual_engine.CERTIFICATES[-1]
            rec["actual_certificate_status"]=cert["status"]
            rec["actual_certificate_gap"]=float(cert["gap"])
            rec["actual_state_upto"]=int(self.actual_engine._STATE.upto)
            if cert["status"] not in ("ok","ok_after_recovery"):
                raise RuntimeError("uncertified actual solve: "+str(cert))
            if self.engine._STATE is self.actual_engine._STATE or self.engine._STATE.warm is self.actual_engine._STATE.warm:
                raise RuntimeError("virtual and actual optimizer state are shared")
            # E2's output comes from the actual allocator, not a post-solve
            # scalar transform. Keep the reference scale in its own field.
            rec["aggregate_gross_scale"]=None
        else:
            target=reference_target
        beta=self.engine._window_beta(np.ascontiguousarray(returns_history,dtype=np.float64),
                                      self.config["beta_window"])
        gross=float(np.abs(target).sum()); cap=.05*a
        beta_exposure=float(beta@target)
        if not np.isfinite(target).all() or gross>5+1e-10 or np.max(np.abs(target),initial=0)>cap+1e-10 or abs(beta_exposure)>1e-9:
            raise RuntimeError("actual returned book violates declared constraints")
        rec.update({"actual_gross":gross,"max_abs_actual_weight":float(np.max(np.abs(target),initial=0)),
            "actual_net_dollars":float(target.sum()),"actual_stock_cap":cap,
            "actual_raw_beta_exposure":beta_exposure,
            "actual_risk_aversion":200./a if self.mode=="E2" else None,
            "actual_fee":0. if self.earned==0 else float(costs@np.abs(target-held_positions)),
            "actual_target":target.copy()})
        self.previous_actual=target.copy()
        if not self.record_arrays:
            rec.pop("virtual_target"); rec.pop("actual_target")
        return target


def make_execution(engine, config, mode, actual_engine=None, record_arrays=True):
    return ExecutionOverlay(engine,config,mode,actual_engine,record_arrays)
