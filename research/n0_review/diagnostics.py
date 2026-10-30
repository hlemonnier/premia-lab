"""N0 instrumentation and prespecified removals; no retuning of the estimator.

Fixed exclusions chosen from the full path are hindsight diagnostics only.
The causal exclusion uses only information available at each original refit.
"""
import numpy as np
from research.parallel10.core import BasePolicy,ew_level,design,cap_increment
from research.parallel10.network import correlation


class ReviewPolicy(BasePolicy):
    def __init__(self,removal='none',excluded=(),shared=None):
        super().__init__('N0',shared)
        if removal not in ('none','fixed','all','causal'):raise ValueError('invalid removal')
        self.removal=removal;self.excluded=tuple(excluded)

    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape
        z=np.zeros((T,N));z[1:]=np.clip(S['u'][1:]/np.sqrt(S['d'][:-1]),-6,6)
        x=ew_level(z,5);out=np.array(base,copy=True);own=np.zeros(N);xm=np.zeros(N)
        self.raw=np.zeros((T,N));self.applied_raw=np.zeros((T,N))
        fit_own=[];fit_rho=[];fit_half1=[];fit_half2=[];fit_score=[];removed=[]
        for t in range(505,T):
            if (t-505)%126==0:
                labels=np.arange(t-504,t);A=x[labels-1];Y=z[labels]
                rho,sx,sy=correlation(A,Y);r1,_,_=correlation(A[:252],Y[:252]);r2,_,_=correlation(A[252:],Y[252:])
                threshold=3/np.sqrt(504);valid=(r1*r2>0)&(np.abs(rho)>threshold)
                shrink=np.sign(rho)*np.maximum(np.abs(rho)-threshold,0);slopes=shrink*sy[None,:]/sx[:,None]
                slopes=np.where(valid,slopes,0);own=np.clip(np.diag(slopes),-.25,.25);xm=A.mean(0)
                importance=np.abs(own)*sx*np.sqrt(S['d'][t-1])
                removed=(np.flatnonzero(importance==importance.max()).tolist() if importance.max()>0 else []) if self.removal=='causal' else []
                fit_own.append(own.copy());fit_rho.append(np.diag(rho).copy());fit_half1.append(np.diag(r1).copy());fit_half2.append(np.diag(r2).copy());fit_score.append(importance)
                self.records.append(dict(target_row=t,last_label=t-1,own=int(np.count_nonzero(own)),removed=removed.copy()))
            normalized=(x[t-1]-xm)*own
            extra=np.sqrt(S['d'][t-1])*normalized
            self.raw[t]=extra
            if self.removal=='fixed':extra[list(self.excluded)]=0.
            elif self.removal=='all':extra[:]=0.
            elif self.removal=='causal':extra[removed]=0.
            self.applied_raw[t]=extra
            D=np.column_stack([np.ones(N),design(X,S['beta'],t-1,self.cfg)])
            extra-=D@np.linalg.solve(D.T@D/N+1e-8*np.eye(28),D.T@extra/N)
            out[t,:N]+=cap_increment(extra,base[t,:N])
        self.fit_own=np.asarray(fit_own).reshape(-1,N)
        self.trace=dict(own=self.fit_own,rho=np.asarray(fit_rho).reshape(-1,N),half1=np.asarray(fit_half1).reshape(-1,N),half2=np.asarray(fit_half2).reshape(-1,N),importance=np.asarray(fit_score).reshape(-1,N))
        self.forecast_output=out;return out
