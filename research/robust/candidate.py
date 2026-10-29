"""R: fixed Student-t-inspired date weights, no score-tuned settings.

Only the GLS half of GC's forecast changes. This is not an exact t filter;
it bounds the influence of large cross-sectional premium innovations.
"""
from __future__ import annotations
import numpy as np
from research.gcorr.correlation_reference import CandidatePolicy as CorrelationPolicy
from research.estimation.likelihood import likelihoods,symmetric_pinv


def robust_forecast(R,X,baseline,cfg,force_unit_weights=False):
    T,N=np.shape(R);out=baseline[:,:N].copy();records=[]
    grams=[np.zeros((27,27)),np.zeros((27,27))];moments=[np.zeros(27),np.zeros(27)];masses=[0.,0.]
    decays=(2.**(-1./1008.),2.**(-1./252.));previous=np.zeros(27);pairs=0
    weights=np.ones(T);innovation=np.zeros(T);ranks=np.zeros(T,dtype=np.int64)
    for t,G,h,D in likelihoods(R,X,baseline,cfg):
        B=N*G;b=N*h;C,rank=symmetric_pinv(B);premium=C@b
        e=premium-previous;z2=max(float(e@B@e),0.)
        weight=1. if force_unit_weights or rank==0 else max(.05,min(1.,(5.+rank)/(5.+z2)))
        weights[t]=weight;innovation[t]=z2;ranks[t]=rank;pairs+=1
        for k,decay in enumerate(decays):
            grams[k]=decay*grams[k]+weight*G;moments[k]=decay*moments[k]+weight*h;masses[k]=decay*masses[k]+1.
        if t>=253 and pairs>=126:
            coef=[]
            for k in range(2):
                g=grams[k]/masses[k];v=moments[k]/masses[k]
                floor=1e-12*max(float(np.diag(g).mean()),1e-12)
                penalty=cfg['ridge']*np.diag(np.maximum(np.diag(g),floor))
                coef.append(np.linalg.solve(g+penalty,v))
            previous=coef[0].copy();previous[:13]=.5*coef[0][:13]+.5*coef[1][:13]
            out[t]=.5*baseline[t,:N]+.5*(D@previous)
        if t==65 or t==T-1 or (t-253)%126==0:
            records.append(dict(target_row=t,last_label=t-1,covariance_last_row=t-2,
                                reliability=weight,innovation_squared=z2,rank=rank,training_pairs=pairs,
                                coefficient_norm=float(np.linalg.norm(previous))))
    if not np.isfinite(out).all():raise RuntimeError('nonfinite robust forecast')
    return out,records,dict(reliability=weights,innovation_squared=innovation,rank=ranks)


class CandidatePolicy(CorrelationPolicy):
    def __init__(self,force_unit_weights=False):
        super().__init__();self.force_unit_weights=force_unit_weights
    def forecast(self,returns_history,characteristics_history):
        base=super().forecast(returns_history,characteristics_history);n=np.shape(returns_history)[1]
        alpha,self.learner_records,self.diagnostic_arrays=robust_forecast(
            returns_history,characteristics_history,base[:,:n+27],self.cfg,self.force_unit_weights)
        self.forecast_output=np.hstack([alpha,base[:,n:]])
        return self.forecast_output
