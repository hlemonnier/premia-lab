"""One preregistered volatility-standardized correlation estimator on frozen F.

F's alpha and marginal variances are preserved. A rolling Ledoit-Wolf estimate
of standardized factor innovations is blended with F's original correlations.
This is not a fitted DCC-GARCH model and has no score-based parameter selection.
"""
from __future__ import annotations
import warnings
import numpy as np
from sklearn.covariance import LedoitWolf
from model_f import engine as E
from model_f import policy as P
from model_f import factor_risk as FR


def correlation_matrix(cov):
    v=np.maximum(np.diag(cov),0.)
    scale=np.sqrt(np.maximum(v,1e-16))
    out=cov/scale[:,None]/scale[None,:]
    zero=v<=1e-16
    out[zero,:]=0.;out[:,zero]=0.;np.fill_diagonal(out,1.)
    return .5*(out+out.T)


def fitted_correlations(R,X,multipliers,cfg):
    R=np.ascontiguousarray(R,dtype=np.float64)
    T,N=R.shape;k=26
    z=np.zeros((T,k));out=np.repeat(np.eye(k)[None,:,:],T,axis=0)
    v=np.full(k,1e-16);second=np.zeros(k);mass=0.
    decay=2.**(-1./cfg['factor_half_life'])
    current=np.eye(k);shrink=1.;records=[]
    for s in range(1,T-1):
        beta=E._window_beta(R[:s],cfg['beta_window'])
        D=E.basis(X[s-1],cfg['feature_clip'])
        e=R[s]-beta*R[s].mean();e=e-e.mean()
        f=np.linalg.solve(D.T@D/N+1e-10*np.eye(k),D.T@e/N)
        if s>=64:
            z[s]=f/np.sqrt(np.maximum(v*multipliers[s],1e-16))
        second=decay*second+f*f;mass=decay*mass+1.
        v=np.maximum(second/mass,1e-16)
        t=s+1
        if t>=253 and (t-253)%21==0:
            lo=max(64,t-252);training=np.ascontiguousarray(z[lo:t])
            if not np.any(training):
                current=np.eye(k);shrink=1.
            else:
                model=LedoitWolf(assume_centered=True).fit(training)
                current=correlation_matrix(model.covariance_)
                shrink=float(model.shrinkage_)
            ev=np.linalg.eigvalsh(current)
            if not np.isfinite(current).all() or ev.min()<-1e-10:
                raise RuntimeError('invalid shrunk correlation')
            records.append(dict(target_row=t,first_label=lo,last_label=t-1,
                training_dates=t-lo,shrinkage=shrink,min_eigenvalue=float(ev.min())))
        out[t]=current
    return out,records


class CorrelationState(FR._RescaledState):
    alternative=None
    max_relative_diagonal_error=0.
    def model(self):
        L,d=super().model()
        if self.alternative is None: raise RuntimeError('correlation payload not set')
        cov=L@L.T
        v=np.maximum(np.diag(cov),0.)
        corr=.5*correlation_matrix(cov)+.5*self.alternative
        sd=np.sqrt(v);new=sd[:,None]*corr*sd[None,:]
        ev,Q=np.linalg.eigh(.5*(new+new.T))
        Ln=Q*np.sqrt(np.maximum(ev,0.))
        error=float(np.max(np.abs(np.sum(Ln*Ln,axis=1)-v)/np.maximum(v,1e-16)))
        self.max_relative_diagonal_error=max(self.max_relative_diagonal_error,error)
        if error>1e-8: raise RuntimeError('factor marginal variance changed')
        return Ln,d


class CorrelationBook(FR._RescaledBook):
    def __init__(self,cfg,n):
        super().__init__(cfg,n);self.alternative=np.eye(26)
    def rebalance(self,held,mu,R,X,costs,gamma,cap):
        if self.state is None or self.state.upto>len(R):
            self.state=CorrelationState(R.shape[1],26,self.cfg)
        self.state.alternative=self.alternative
        return super().rebalance(held,mu,R,X,costs,gamma,cap)


class CandidatePolicy(FR.FactorPolicy):
    def forecast(self,returns_history,characteristics_history):
        baseline=super().forecast(returns_history,characteristics_history)
        T,n=np.shape(returns_history)
        corr,self.fit_records=fitted_correlations(returns_history,characteristics_history,
                                                  baseline[:,n+1:],self.cfg)
        self.virtual=CorrelationBook(self.cfg,n);self.inner=CorrelationBook(self.cfg,n)
        self.forecast_output=np.hstack([baseline,corr.reshape(T,26*26)])
        return self.forecast_output
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        n=np.shape(returns_history)[1];row=np.asarray(expected_returns,dtype=np.float64)
        if row.shape!=(n+27+26*26,) or not np.isfinite(row).all():
            raise ValueError('invalid correlation forecast payload')
        for book in (self.virtual,self.inner):book.alternative=row[n+27:].reshape(26,26)
        return super().rebalance(held_positions,row[:n+27],returns_history,
                                 characteristics_history,trading_costs)
