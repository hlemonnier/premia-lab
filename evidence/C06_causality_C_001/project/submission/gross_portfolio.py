"""Exact beta/box/gross allocation with costs around drifted holdings.

The two absolute-value penalties have scalar knots at zero and held weight.
Nested safeguarded scalar roots solve the beta equality and active gross
budget; derivative steps accelerate roots but never replace bracketing or
final numerical feasibility checks. There is no proportional postsolve scale.
"""
from __future__ import annotations

from numbers import Integral
import numpy as np

if __package__:
    from .portfolio import allocate as diagonal_allocate
else:
    from portfolio import allocate as diagonal_allocate


def allocate_gross(expected_returns,held_positions,variances,betas,trading_costs,
                   risk_aversion,cost_horizon,weight_cap,gross_cap,max_iterations=96):
    """Return the convex beta/box/L1-budget optimum with solver diagnostics."""
    if isinstance(max_iterations,bool) or not isinstance(max_iterations,Integral) or max_iterations<=0:
        raise ValueError("max_iterations must be a positive integer")
    try:
        budget=np.asarray(gross_cap,dtype=np.float64)
    except (TypeError,ValueError) as exc:
        raise ValueError("gross_cap must be a nonnegative finite scalar") from exc
    if budget.ndim!=0 or not np.isfinite(budget) or budget<0:
        raise ValueError("gross_cap must be a nonnegative finite scalar")
    budget=float(budget)
    unconstrained=diagonal_allocate(expected_returns,held_positions,variances,betas,trading_costs,
                                    risk_aversion,cost_horizon,weight_cap)
    n=len(unconstrained)
    mu=np.asarray(expected_returns,dtype=np.float64)
    held=np.asarray(held_positions,dtype=np.float64)
    variance=np.asarray(variances,dtype=np.float64)
    beta=np.asarray(betas,dtype=np.float64)
    cost=np.asarray(trading_costs,dtype=np.float64)
    cap=np.broadcast_to(np.asarray(weight_cap,dtype=np.float64),(n,))
    gamma,horizon=float(risk_aversion),float(cost_horizon)
    a=gamma*variance;k=cost/horizon
    movable=cap>0
    beta_scale=float(np.max(np.abs(beta[movable]))) if movable.any() else 0.
    b=np.zeros(n)
    if beta_scale:b[movable]=beta[movable]/beta_scale
    attainable=float(np.abs(b)@cap)
    total_cap=float(cap.sum())
    if not np.isfinite(total_cap) or not np.isfinite(attainable):
        raise ValueError("total constraint bounds must be numerically representable")
    eps=np.finfo(np.float64).eps
    beta_tolerance=max(64*eps*attainable,float(np.nextafter(0.,1.)))
    gross_tolerance=128*eps*max(1.,budget,total_cap)
    initial_gross=float(np.abs(unconstrained).sum())
    evaluations=0

    def finish(weights,nu,iterations,binding):
        gross=float(np.abs(weights).sum())
        exposure=float(abs(b@weights))
        if (not np.isfinite(weights).all() or np.any(np.abs(weights)>cap+64*eps*np.maximum(1.,cap))
                or exposure>beta_tolerance or gross>budget+gross_tolerance):
            raise RuntimeError("Gross allocator could not certify final constraints")
        return weights,{"converged":True,"gross_multiplier":float(nu),"gross_iterations":int(iterations),
            "scalar_evaluations":evaluations,"gross_budget_bound":int(binding),
            "unconstrained_gross":initial_gross,"gross_excess":gross-budget,
            "normalized_beta_residual":exposure}

    if budget==0:
        return finish(np.zeros(n),0.,0,initial_gross>0)
    if initial_gross<=budget+gross_tolerance:
        return finish(unconstrained,0.,0,False)
    sign_held=np.where(held<0,-1.,1.)
    absolute_held=np.abs(held)
    with np.errstate(over="raise",invalid="raise",divide="raise"):
        held_gradient=a*absolute_held
    if not np.isfinite(held_gradient).all():
        raise ValueError("held risk gradients must be representable")

    def at_multipliers(multiplier,nu):
        nonlocal evaluations
        evaluations+=1
        try:
            with np.errstate(over="raise",invalid="raise",divide="raise"):
                x=sign_held*(mu-multiplier*b)
                negative=x < -k-nu
                middle=(x>nu-k)&(x<held_gradient+nu-k)
                holding=(x>=held_gradient+nu-k)&(x<=held_gradient+nu+k)
                positive=x>held_gradient+nu+k
                reflected=np.zeros(n)
                np.divide(x+k+nu,a,out=reflected,where=negative)
                np.divide(x+k-nu,a,out=reflected,where=middle)
                np.copyto(reflected,absolute_held,where=holding)
                np.divide(x-k-nu,a,out=reflected,where=positive)
                raw=sign_held*reflected
                weights=np.clip(raw,-cap,cap)
                active=(negative|middle|positive)&(np.abs(raw)<cap)
                inverse=np.where(active,1./a,0.)
                exposure=float(b@weights)
        except FloatingPointError as exc:
            raise ValueError("gross scalar-prox arithmetic must be representable") from exc
        if not np.isfinite(weights).all() or not np.isfinite(exposure):
            raise ValueError("gross scalar prox produced a nonfinite result")
        return weights,exposure,inverse

    def hedge(nu,warm=0.):
        multiplier=float(warm)
        weights,exposure,inverse=at_multipliers(multiplier,nu)
        if abs(exposure)<=beta_tolerance:
            return weights,inverse,multiplier
        origin,origin_exposure=multiplier,exposure
        denominator=float((b*b)@inverse)
        direction=1. if exposure>0 else -1.
        step=abs(exposure)/denominator if denominator>0 else float(max(np.max(np.abs(mu)),np.max(a*cap),np.max(k+nu),np.finfo(float).tiny))
        if not np.isfinite(step) or step<=0:
            raise RuntimeError("Could not construct finite beta bracket")
        for _ in range(max_iterations):
            trial=origin+direction*step
            if trial==origin:trial=float(np.nextafter(origin,np.inf if direction>0 else -np.inf))
            if not np.isfinite(trial):raise RuntimeError("Beta bracket exceeded floating-point range")
            tw,te,ti=at_multipliers(trial,nu)
            if abs(te)<=beta_tolerance:return tw,ti,trial
            if (origin_exposure>0 and te<0) or (origin_exposure<0 and te>0):
                lower,upper=(origin,trial) if origin<trial else (trial,origin)
                multiplier,weights,exposure,inverse=trial,tw,te,ti
                break
            step*=2.
        else:raise RuntimeError("Could not bracket beta equality")
        for _ in range(max_iterations):
            denominator=float((b*b)@inverse)
            candidate=multiplier+exposure/denominator if denominator>0 else float("nan")
            if not np.isfinite(candidate) or not lower<candidate<upper:
                candidate=.5*lower+.5*upper
            if candidate==lower or candidate==upper:
                raise RuntimeError("Beta equality unresolved at floating-point bracket limit")
            weights,exposure,inverse=at_multipliers(candidate,nu)
            multiplier=candidate
            if abs(exposure)<=beta_tolerance:return weights,inverse,multiplier
            if exposure>0:lower=candidate
            else:upper=candidate
        raise RuntimeError("Beta equality did not converge")

    try:
        with np.errstate(over="raise",invalid="raise"):
            upper=float(np.nextafter(np.max(np.abs(mu)+k),np.inf))
    except FloatingPointError as exc:
        raise ValueError("gross dual upper bound must be representable") from exc
    if not np.isfinite(upper):raise ValueError("gross dual upper bound must be finite")
    upper_weights,_,_=hedge(upper)
    if np.abs(upper_weights).sum()>budget+gross_tolerance:
        raise RuntimeError("Gross dual upper endpoint is not feasible")
    lower=0.;nu=0.
    weights,inverse,beta_multiplier=hedge(0.)
    for iteration in range(1,max_iterations+1):
        excess=float(np.abs(weights).sum()-budget)
        if abs(excess)<=gross_tolerance:return finish(weights,nu,iteration-1,True)
        signs=np.sign(weights)
        beta_denominator=float((b*b)@inverse)
        cross=float((b*signs)@inverse)
        slope=-float((signs*signs)@inverse)
        if beta_denominator>0:slope+=cross*cross/beta_denominator
        proposed=nu-excess/slope if slope<0 else float("nan")
        if not np.isfinite(proposed) or not lower<proposed<upper:
            proposed=.5*lower+.5*upper
        if proposed==lower or proposed==upper:
            raise RuntimeError("Gross budget unresolved at floating-point bracket limit")
        weights,inverse,beta_multiplier=hedge(proposed,beta_multiplier)
        nu=proposed
        new_excess=float(np.abs(weights).sum()-budget)
        if abs(new_excess)<=gross_tolerance:return finish(weights,nu,iteration,True)
        if new_excess>0:lower=nu
        else:upper=nu
    raise RuntimeError("Gross budget did not converge")
