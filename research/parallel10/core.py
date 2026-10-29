"""Shared causal snapshots, not fitted full-sample transformations.

The cached path is a research acceleration only. Every candidate also accepts
raw histories and reconstructs the snapshots without any file or cache access.
"""
from __future__ import annotations
import numpy as np
from model_f import engine as E,policy as P
from model_f import factor_risk as FR
from gls_alpha import CandidatePolicy as G


def reset(policy,n):
    policy.virtual=FR._RescaledBook(policy.cfg,n);policy.inner=FR._RescaledBook(policy.cfg,n)
    policy.outer_target=np.zeros(n);policy.sums={63:0.,1008:0.};policy.masses={63:0.,1008:0.}
    policy.earned=0;policy.last_day=None;policy.certificates=[];policy.multiplier=1.


def snapshots(R,X,base,cfg):
    R=np.ascontiguousarray(R,dtype=np.float64);T,N=R.shape
    beta,m=E.causal_betas(R,cfg['beta_window']);f2=P.f2_forecast(R,X,cfg)
    u=np.zeros((T,N));f=np.zeros((T,26));d=np.full((T,N),cfg['variance_floor'])
    q=np.full((T,26),1e-16);cov=np.zeros((T,26,26));s2=np.zeros((26,26));u2=np.zeros(N);mf=ms=0.
    af=2**(-1/cfg['factor_half_life']);au=2**(-1/cfg['specific_half_life'])
    for s in range(1,T-1):
        b=E._window_beta(R[:s],cfg['beta_window']);D=E.basis(X[s-1],cfg['feature_clip'])
        y=R[s]-b*R[s].mean();y-=y.mean()
        f[s]=np.linalg.solve(D.T@D/N+1e-10*np.eye(26),D.T@y/N);u[s]=y-D@f[s]
        s2=af*s2+np.outer(f[s],f[s]);mf=af*mf+1.;cov[s]=s2/mf;q[s]=np.maximum(np.diag(cov[s]),1e-16)
        u2=au*u2+u[s]**2;ms=au*ms+1.;raw=u2/ms;sh=cfg['specific_shrinkage']
        d[s]=np.maximum((1-sh)*raw+sh*np.median(raw),cfg['variance_floor'])
    return dict(g=base,f2=f2,beta=beta,market=m,u=u,f=f,d=d,q=q,cov=cov)


def design(X,beta,s,cfg):
    return np.hstack([E.basis(X[s],cfg['feature_clip']),E._zcol(beta[s+1],cfg['feature_clip'])[:,None]])


def cap_increment(extra,baseline):
    limit=.2*np.sqrt(np.mean(baseline**2));extra=.5*extra
    return extra*min(1.,limit/max(float(np.sqrt(np.mean(extra**2))),1e-30))


def ew_level(a,half_life):
    out=np.zeros_like(a);val=np.zeros(a.shape[1:]);mass=0.;decay=2**(-1/half_life)
    for s in range(1,len(a)-1):val=decay*val+a[s];mass=decay*mass+1.;out[s]=val/mass
    return out


def marginal(s,X,S,cfg):
    D=E.basis(X[s],cfg['feature_clip']);mult=S['g'][s+1,X.shape[1]+1:]
    scale=np.sqrt(mult);F=scale[:,None]*S['cov'][s]*scale[None,:]
    return np.maximum(S['d'][s]+np.einsum('ij,ij->i',D@F,D),cfg['variance_floor'])


class BasePolicy(G):
    def __init__(self,mode,shared=None):super().__init__();self.mode=mode;self.shared=shared;self.records=[]
    def inputs(self,R,X):
        R=np.ascontiguousarray(R,dtype=np.float64);X=np.ascontiguousarray(X,dtype=np.float64)
        self.records=[]
        if self.shared is None:
            base=super().forecast(R,X);S=snapshots(R,X,base,self.cfg)
        else:
            if self.shared['g'].shape[0]!=len(R):raise ValueError('shared snapshots must match exact history length')
            reset(self,R.shape[1]);S=self.shared;base=S['g'];self.training_records=[];self.learner_records=[]
        return R,X,base,S
