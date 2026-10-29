"""Causal cross-sectional GLS likelihood; same arithmetic as frozen gls_alpha.

N*G and N*h are the unnormalized Gaussian likelihood precision and information.
The daily nuisance intercept is projected out before accumulating the premia.
"""
from __future__ import annotations
import numpy as np
from model_f import engine as E


def likelihoods(R,X,baseline,cfg):
    R=np.ascontiguousarray(R,dtype=np.float64);T,N=R.shape
    beta,market=E.causal_betas(R,cfg['beta_window']);state=E._RiskState(N,26,cfg)
    ones=np.ones(N)
    for t in range(65,T):
        u=t-1
        while state.upto<u:state.absorb(R,X,state.upto)
        L,d=state.model();L=L/np.sqrt(cfg['factor_risk_scale'])
        L=np.sqrt(baseline[u,N+1:N+27])[:,None]*L
        D=np.hstack([E.basis(X[u-1],cfg['feature_clip']),E._zcol(beta[u],cfg['feature_clip'])[:,None]])
        y=R[u]-beta[u]*market[u]
        M=D[:,:26]@L;V=np.column_stack([ones,D,y]);Vi=V/d[:,None];Mi=M/d[:,None]
        precision_V=Vi-Mi@np.linalg.solve(np.eye(26)+M.T@Mi,M.T@Vi)
        normalizer=float(np.sum(precision_V[:,0]))
        if not np.isfinite(normalizer) or normalizer<=0:raise RuntimeError('nonpositive intercept precision')
        projected=precision_V[:,1:]-precision_V[:,0,None]*(np.sum(precision_V[:,1:],axis=0)/normalizer)[None,:]
        G=D.T@projected[:,:27]/N;G=.5*(G+G.T);h=D.T@projected[:,27]/N
        current=np.hstack([E.basis(X[t-1],cfg['feature_clip']),E._zcol(beta[t],cfg['feature_clip'])[:,None]])
        yield t,G,h,current


def symmetric_pinv(B):
    """Fixed-rank diagnostic inverse; materially negative precision fails."""
    ev,U=np.linalg.eigh(.5*(B+B.T));scale=max(float(np.max(np.abs(ev))),1e-30)
    if float(ev.min()) < -1e-10*scale:raise RuntimeError('materially non-PSD likelihood precision')
    keep=ev>1e-10*scale
    C=(U[:,keep]/ev[keep])@U[:,keep].T if np.any(keep) else np.zeros_like(B)
    return .5*(C+C.T),int(keep.sum())
