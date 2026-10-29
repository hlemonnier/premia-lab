"""Frozen diagnostic controls for GLS attribution; none is selected for deployment.

See the preregistered PLAN_20261029.md, commit5ff3b0e. F/GLS originals are not
modified. Relative penalties scale with the EW-normalized Gram matrix, avoiding
an arbitrary change in ridge strength when precision units are rescaled.
"""
from __future__ import annotations
import numpy as np
from model_f.factor_risk import FactorPolicy
from model_f import engine as E

# precision, penalty, profile_daily_intercept, first_target_for_training
VARIANTS={
 'G_D':('full','diagonal',True,65),
 'O_D':('identity','diagonal',True,65),
 'G_S':('full','scalar',True,65),
 'O_S':('identity','scalar',True,65),
 'D_D':('specific','diagonal',True,65),
 'O_A':('identity','absolute',True,65),
 'G_N':('full','diagonal',False,65),
 'O_A0':('identity','absolute',True,2),
}


def controlled_forecast(R,X,baseline,cfg,variant,*,precision_scale=1.):
    if variant not in VARIANTS:raise ValueError('unknown registered control')
    if not np.isfinite(precision_scale) or precision_scale<=0:raise ValueError('precision scale must be positive')
    mode,penalty_kind,intercept,first=VARIANTS[variant]
    R=np.ascontiguousarray(R,dtype=np.float64);T,N=R.shape
    if np.shape(X)!=(T,N,13):raise ValueError('invalid characteristics shape')
    beta,market=E.causal_betas(R,cfg['beta_window'])
    state=E._RiskState(N,26,cfg)
    grams=[np.zeros((27,27)),np.zeros((27,27))];moments=[np.zeros(27),np.zeros(27)];masses=[0.,0.]
    decays=(2**(-1/1008.),2**(-1/252.));out=baseline[:,:N].copy();pairs=0;records=[];ones=np.ones(N)
    for t in range(first,T):
        u=t-1
        D=np.hstack([E.basis(X[u-1],cfg['feature_clip']),E._zcol(beta[u],cfg['feature_clip'])[:,None]])
        y=R[u]-beta[u]*market[u];V=np.column_stack([ones,D,y])
        if mode=='identity':
            precision_V=V.copy()
        else:
            while state.upto<u:state.absorb(R,X,state.upto)
            L,d=state.model()
            if mode=='specific':precision_V=V/d[:,None]
            else:
                L=L/np.sqrt(cfg['factor_risk_scale']);L=np.sqrt(baseline[u,N+1:])[:,None]*L
                M=D[:,:26]@L;Vi=V/d[:,None];Mi=M/d[:,None]
                precision_V=Vi-Mi@np.linalg.solve(np.eye(26)+M.T@Mi,M.T@Vi)
        precision_V*=precision_scale
        if intercept:
            normalizer=float(np.sum(precision_V[:,0]))
            if not np.isfinite(normalizer) or normalizer<=0:raise RuntimeError('nonpositive intercept precision')
            projected=precision_V[:,1:]-precision_V[:,0,None]*(np.sum(precision_V[:,1:],axis=0)/normalizer)[None,:]
        else:projected=precision_V[:,1:]
        G=D.T@projected[:,:27]/N;G=.5*(G+G.T);h=D.T@projected[:,27]/N;pairs+=1
        for k,decay in enumerate(decays):
            grams[k]=decay*grams[k]+G;moments[k]=decay*moments[k]+h;masses[k]=decay*masses[k]+1.
        if t<253 or pairs<126:continue
        coef=[];diag=[]
        for k in range(2):
            g=grams[k]/masses[k];v=moments[k]/masses[k]
            floor=1e-12*max(float(np.diag(g).mean()),1e-12)
            if penalty_kind=='diagonal':penalty=cfg['ridge']*np.diag(np.maximum(np.diag(g),floor))
            elif penalty_kind=='scalar':penalty=cfg['ridge']*max(float(np.diag(g).mean()),floor)*np.eye(27)
            else:penalty=cfg['ridge']*np.eye(27)
            coef.append(np.linalg.solve(g+penalty,v))
            diag.append(dict(gram_mean_diagonal=float(np.diag(g).mean()),gram_min_diagonal=float(np.diag(g).min()),
                gram_max_diagonal=float(np.diag(g).max()),penalty_min=float(np.diag(penalty).min()),penalty_max=float(np.diag(penalty).max())))
        combined=coef[0].copy();combined[:13]=.5*coef[0][:13]+.5*coef[1][:13]
        new_design=np.hstack([E.basis(X[t-1],cfg['feature_clip']),E._zcol(beta[t],cfg['feature_clip'])[:,None]])
        out[t]=.5*baseline[t,:N]+.5*(new_design@combined)
        if (t-253)%126==0:records.append(dict(target_row=t,last_label=u,covariance_last_row=u-1,
            training_pairs=pairs,coef=combined.tolist(),diagnostic=diag))
    if not np.isfinite(out).all():raise RuntimeError('nonfinite control forecast')
    return out,records


class ControlPolicy(FactorPolicy):
    def __init__(self,variant):
        super().__init__()
        if variant not in VARIANTS:raise ValueError('unknown control')
        self.variant=variant
    def forecast(self,returns_history,characteristics_history):
        base=super().forecast(returns_history,characteristics_history)
        alpha,self.learner_records=controlled_forecast(returns_history,characteristics_history,base,self.cfg,self.variant)
        n=np.shape(returns_history)[1];self.forecast_output=np.hstack([alpha,base[:,n:]])
        return self.forecast_output
