"""One preregistered GLS alpha candidate; F's submission files remain unchanged.

Weight each matured training cross-section by its lagged factor-plus-specific
noise covariance. The resulting signal is blended 50/50 with the frozen F2
signal. This is feasible GLS, not a new source of information or a claim of
statistical efficiency under a misspecified covariance.
"""
from __future__ import annotations
import numpy as np
from model_f.factor_risk import FactorPolicy
from model_f import engine as E


def gls_forecast(R, X, baseline, cfg):
    R=np.ascontiguousarray(R,dtype=np.float64)
    T,N=R.shape
    beta,market=E.causal_betas(R,cfg['beta_window'])
    state=E._RiskState(N,26,cfg)
    grams=[np.zeros((27,27)),np.zeros((27,27))]
    moments=[np.zeros(27),np.zeros(27)];masses=[0.,0.]
    decays=(2.**(-1./1008.),2.**(-1./252.))
    out=baseline[:,:N].copy();pairs=0;records=[]
    ones=np.ones(N)
    for t in range(65,T):
        u=t-1
        # Omega for label u is estimated only through u-1.
        while state.upto<u:
            state.absorb(R,X,state.upto)
        L,d=state.model()
        # Undo the portfolio optimizer's deliberate factor-risk discount.
        L=L/np.sqrt(cfg['factor_risk_scale'])
        L=np.sqrt(baseline[u,N+1:])[:,None]*L
        D=np.hstack([E.basis(X[u-1],cfg['feature_clip']),
                     E._zcol(beta[u],cfg['feature_clip'])[:,None]])
        y=R[u]-beta[u]*market[u]
        M=D[:,:26]@L
        V=np.column_stack([ones,D,y]);Vi=V/d[:,None];Mi=M/d[:,None]
        precision_V=Vi-Mi@np.linalg.solve(np.eye(26)+M.T@Mi,M.T@Vi)
        # Profile out an unpenalized intercept in the precision metric.
        normalizer=float(np.sum(precision_V[:,0]))
        if not np.isfinite(normalizer) or normalizer<=0:
            raise RuntimeError('nonpositive intercept precision')
        projected=precision_V[:,1:]-precision_V[:,0,None]*(
            np.sum(precision_V[:,1:],axis=0)/normalizer)[None,:]
        G=D.T@projected[:,:27]/N
        G=.5*(G+G.T)
        h=D.T@projected[:,27]/N
        pairs+=1
        for k,decay in enumerate(decays):
            grams[k]=decay*grams[k]+G
            moments[k]=decay*moments[k]+h
            masses[k]=decay*masses[k]+1.
        if t<253 or pairs<126:
            continue
        coef=[]
        for k in range(2):
            g=grams[k]/masses[k];v=moments[k]/masses[k]
            floor=1e-12*max(float(np.diag(g).mean()),1e-12)
            penalty=cfg['ridge']*np.diag(np.maximum(np.diag(g),floor))
            coef.append(np.linalg.solve(g+penalty,v))
        combined=coef[0].copy();combined[:13]=.5*coef[0][:13]+.5*coef[1][:13]
        new_design=np.hstack([E.basis(X[t-1],cfg['feature_clip']),
                             E._zcol(beta[t],cfg['feature_clip'])[:,None]])
        out[t]=.5*baseline[t,:N]+.5*(new_design@combined)
        if (t-253)%126==0:
            records.append(dict(target_row=t,last_label=u,covariance_last_row=u-1,
                                training_pairs=pairs,coef=combined.tolist()))
    if not np.isfinite(out).all(): raise RuntimeError('nonfinite GLS output')
    return out,records


class CandidatePolicy(FactorPolicy):
    def forecast(self,returns_history,characteristics_history):
        base=super().forecast(returns_history,characteristics_history)
        alpha,self.learner_records=gls_forecast(returns_history,characteristics_history,base,self.cfg)
        n=np.shape(returns_history)[1]
        self.forecast_output=np.hstack([alpha,base[:,n:]])
        return self.forecast_output
