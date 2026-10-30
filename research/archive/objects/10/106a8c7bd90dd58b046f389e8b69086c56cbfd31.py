"""Conservative residual low-rank risk addition; matched-diagonal control."""
import numpy as np
from model_f import engine as E,policy as P,factor_risk as FR
from model_f.allocator import allocate_factor
from .core import BasePolicy


class CovBook(FR._RescaledBook):
    def __init__(self,cfg,n,mode):super().__init__(cfg,n);self.mode=mode;self.links=np.zeros((n,5))
    def rebalance(self,held,mu,R,X,costs,gamma,cap):
        if not np.any(self.links):return super().rebalance(held,mu,R,X,costs,gamma,cap)
        if self.state is None or self.state.upto>len(R):self.state=FR._RescaledState(R.shape[1],26,self.cfg)
        self.state.common=self.common;self.state.factor=self.factor
        while self.state.upto<len(R):self.state.absorb(R,X,self.state.upto)
        L,d=self.state.model();beta=E._window_beta(R,self.cfg['beta_window']);D=E.risk_loadings(X[-1],beta,self.cfg)
        M=np.sqrt(d)[:,None]*self.links
        if self.mode=='C':
            LL=np.zeros((31,31));LL[:26,:26]=L;LL[26:,26:]=np.eye(5);L=LL;D=np.hstack([D,M])
        else:d=d+np.sum(M*M,axis=1)
        info={};w=allocate_factor(mu,held,d,D,L,beta,np.asarray(costs)/self.cfg['cost_horizon'],gamma,cap,warm=self.state.warm,info=info,beta_target=0.)
        gross=float(np.abs(w).sum());info['gross_action']='none'
        if gross>self.cfg['gross_cap']:w=w*self.cfg['gross_cap']/gross;info['gross_action']='scaled'
        E._final_check(w,beta,0.,{**self.cfg,'weight_cap':cap});self.target=w;return w,info


class ResidualCovPolicy(BasePolicy):
    def forecast(self,returns_history,characteristics_history):
        R,X,base,S=self.inputs(returns_history,characteristics_history);T,N=R.shape
        z=np.zeros((T,N));z[1:]=np.clip(S['u'][1:]/np.sqrt(S['d'][:-1]),-6,6)
        loadings=np.zeros((T,N,5));current=np.zeros((N,5))
        for t in range(253,T):
            if (t-253)%63==0:
                dates=np.arange(max(1,t-252),t);Z=z[dates];Z=Z-Z.mean(0);W=len(dates);denom=max(1,W-1)
                vals,vecs=np.linalg.eigh((Z@Z.T)/denom);threshold=(1+np.sqrt(N/denom))**2
                inds=np.where(vals>threshold)[0][-5:][::-1];current=np.zeros((N,5))
                for j,k in enumerate(inds):
                    v=Z.T@vecs[:,k]/np.sqrt(denom*vals[k]);current[:,j]=v*np.sqrt(.1*(vals[k]-1))
                row_norm=np.sqrt(np.sum(current*current,axis=1));current*=np.minimum(1.,.5/np.maximum(row_norm,1e-30))[:,None]
                self.records.append(dict(target_row=t,last_label=t-1,modes=len(inds),eigenvalues=vals[inds].tolist(),threshold=float(threshold),maximum_extra_specific_fraction=float(np.sum(current*current,1).max(initial=0))))
            loadings[t]=current
        self.virtual=CovBook(self.cfg,N,self.mode);self.inner=CovBook(self.cfg,N,self.mode)
        self.forecast_output=np.hstack([base,loadings.reshape(T,N*5)]);return self.forecast_output
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        n=returns_history.shape[1];row=np.asarray(expected_returns);links=row[n+27:].reshape(n,5)
        if not np.isfinite(links).all() or np.max(np.sum(links*links,1))>.25+1e-10:raise ValueError('invalid residual links')
        self.virtual.links=links;self.inner.links=links
        return super().rebalance(held_positions,row[:n+27],returns_history,characteristics_history,trading_costs)
