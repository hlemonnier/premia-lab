"""Preregistered Wave5 research policies; no strategy is selected by this module.

All forecasts at row t depend only on source rows <t. Upstream V3 files are
unchanged and Git-blob verified. See PLAN_20261029.md (remote commit09cbdc7).
The module never loads market data, model files, caches or experiment results.
"""
from __future__ import annotations
import sys, warnings
from pathlib import Path
import numpy as np
from sklearn.linear_model import GammaRegressor
from sklearn.exceptions import ConvergenceWarning
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'handoff_v3'),str(ROOT/'research/wave4')]
from model_v3 import engine as E
from model_v3 import policy as P
from r1_candidate import CONFIG, _RiskBook, risk_multipliers


def risk_paths(returns_history, characteristics_history, cfg):
    """Daily published risk sufficient statistics; source-indexed, not target-indexed.

    The baseline d computation is exactly the upstream formula. Three shorter
    EW estimates and two factor second moments are additional causal statistics.
    Full arrays are research/forecast output storage, not pre-fitted parameters.
    """
    R=np.ascontiguousarray(returns_history,dtype=np.float64)
    X=characteristics_history;T,N=R.shape
    if np.shape(X)!=(T,N,13):raise ValueError('invalid characteristics shape')
    d=np.full((T,N),cfg['variance_floor'],dtype=np.float64)
    u2=np.zeros((T,N));features=np.zeros((T,N,3));v=np.ones((T,26))
    slow=np.zeros(N);slow_mass=0.;a_s=2.**(-1./cfg['specific_half_life'])
    fast=np.zeros((3,N));fast_mass=np.zeros(3);a_h=2.**(-1./np.array([5.,21.,63.]))
    factor=np.zeros((2,26));factor_mass=np.zeros(2);a_f=2.**(-1./np.array([63.,1008.]))
    for s in range(1,T):
        beta=E._window_beta(R[:s],cfg['beta_window'])
        D=E.basis(X[s-1],cfg['feature_clip'])
        e=R[s]-beta*R[s].mean();e=e-e.mean()
        G=D.T@D/N
        f=np.linalg.solve(G+1e-10*np.eye(26),D.T@e/N)
        u=e-D@f;u2[s]=u*u
        slow=a_s*slow+u2[s];slow_mass=a_s*slow_mass+1.
        dv=slow/slow_mass
        d[s]=np.maximum((1-cfg['specific_shrinkage'])*dv+cfg['specific_shrinkage']*np.median(dv),cfg['variance_floor'])
        fast=a_h[:,None]*fast+u2[s];fast_mass=a_h*fast_mass+1.
        features[s]=np.log(np.clip((fast/fast_mass[:,None])/d[s],.25,4.)).T
        factor=a_f[:,None]*factor+f*f;factor_mass=a_f*factor_mass+1.
        fm=factor/factor_mass[:,None]
        v[s]=np.clip(np.sqrt(np.maximum(fm[0],1e-16)/np.maximum(fm[1],1e-16)),.5,2.)
    return d,u2,features,v


def h_forecast(d,u2,features):
    """Pooled three-feature log-link GLM, fitted to matured next-day variances."""
    T,N=d.shape;out=np.ones((T,N));records=[];model=None
    for target in range(253,T):
        if (target-253)%126==0:
            labels=np.arange(max(64,target-504),target,5)
            tx=np.ascontiguousarray(features[labels-1].reshape(-1,3),dtype=np.float64)
            ty=np.maximum(u2[labels]/d[labels-1],1e-8).ravel()
            model=GammaRegressor(alpha=1.,max_iter=300,tol=1e-8)
            with warnings.catch_warnings():
                warnings.simplefilter('error',ConvergenceWarning)
                model.fit(tx,ty)
            records.append({'target_row':target,'first_label':int(labels[0]),'last_label':int(labels[-1]),
                            'latest_feature_row':int(labels[-1]-1),'stock_days':len(ty),
                            'coef':model.coef_.tolist(),'intercept':float(model.intercept_),'iterations':int(model.n_iter_)})
        predicted=model.predict(np.ascontiguousarray(features[target-1]))
        if not np.isfinite(predicted).all():raise RuntimeError('nonfinite variance forecast')
        out[target]=.5+.5*np.clip(predicted,.5,2.)
    return out,records


def p_forecast(returns_history,characteristics_history,cfg,v,baseline):
    """F2 on risk-scaled designs, blended 50/50 with unchanged F2.

    Label at u sees design X[u-1] and factor volatility published at u-1.
    Refit at target t uses labels only through t-1. No lookahead standardization.
    """
    R=np.ascontiguousarray(returns_history,dtype=np.float64);X=characteristics_history
    T,N=R.shape;beta,m=E.causal_betas(R,cfg['beta_window']);residual=R-beta*m[:,None]
    ridge=cfg['ridge']*np.eye(27)
    def design(s):
        return np.hstack([E.basis(X[s],cfg['feature_clip'])*v[s],E._zcol(beta[s+1],cfg['feature_clip'])[:,None]])
    grams=[np.zeros((27,27)),np.zeros((27,27))];mom=[np.zeros(27),np.zeros(27)];mass=[0.,0.]
    decay=(2.**(-1./1008.),2.**(-1./252.));new=np.zeros((T,N))
    for t in range(2,T):
        s=t-2;D=design(s);G=D.T@D/N;h=D.T@residual[s+1]/N
        for j in range(2):
            grams[j]=decay[j]*grams[j]+G;mom[j]=decay[j]*mom[j]+h;mass[j]=decay[j]*mass[j]+1.
        if t-1>=cfg['min_training_days']:
            slow=np.linalg.solve(grams[0]/mass[0]+ridge,mom[0]/mass[0])
            fast=np.linalg.solve(grams[1]/mass[1]+ridge,mom[1]/mass[1])
            coef=slow.copy();coef[:13]=.5*(slow[:13]+fast[:13])
            new[t]=design(t-1)@coef
    return .5*baseline+.5*new


class _ActualBook(_RiskBook):
    actual_held=None
    def rebalance(self,held,mu,R,X,costs,gamma,cap):
        if self.actual_held is None:raise RuntimeError('actual holdings were not supplied')
        return super().rebalance(self.actual_held,mu,R,X,costs,gamma,cap)


class ResearchPolicy(P.ScorePolicy):
    """Integrated original-scorer interface. Explicit mode, never selected by score."""
    def __init__(self,mode='H'):
        if mode not in ('B0','R1','A_pool','A_cross','H','P','E','HP','ER1','EH','EP'):
            raise ValueError('unregistered mode')
        super().__init__(dict(CONFIG),sleeve=.05,outer_gross_cap=5.)
        self.mode=mode

    def forecast(self,returns_history,characteristics_history):
        alpha=super().forecast(returns_history,characteristics_history)
        T,N=np.shape(returns_history);mult=np.ones((T,N));self.training_records=[]
        self.targets=[];self.sizing=[];self.outer_cap_count=0;self.diagnostic={}
        mode=self.mode
        if mode in ('R1','A_pool','A_cross','ER1'):
            mult,self.training_records=risk_multipliers(returns_history,characteristics_history,self.cfg)
            if mode=='A_pool':mult=np.broadcast_to(mult.mean(axis=1,keepdims=True),mult.shape).copy()
            elif mode=='A_cross':mult=np.clip(mult/mult.mean(axis=1,keepdims=True),.5,2.)
        if mode in ('H','P','HP','EH','EP'):
            d,u2,features,v=risk_paths(returns_history,characteristics_history,self.cfg)
            if mode in ('H','HP','EH'):
                mult,self.training_records=h_forecast(d,u2,features)
            if mode in ('P','HP','EP'):
                alpha=p_forecast(returns_history,characteristics_history,self.cfg,v,alpha)
        self.virtual=_RiskBook(self.cfg,N)
        self.inner=(_ActualBook if mode.startswith('E') else _RiskBook)(self.cfg,N)
        self.forecast_output=np.stack([alpha,mult],axis=-1)
        return self.forecast_output

    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        row=np.asarray(expected_returns,dtype=np.float64);n=np.shape(returns_history)[1]
        if row.shape!=(n,2) or not np.isfinite(row).all():raise ValueError('invalid forecast row')
        if np.any(row[:,1]<.5) or np.any(row[:,1]>2.):raise ValueError('variance multiplier bounds')
        self.virtual.multiplier=row[:,1];self.inner.multiplier=row[:,1]
        if self.mode.startswith('E'):
            self.inner.actual_held=np.asarray(held_positions,dtype=np.float64)-self.sleeve/n
        w=super().rebalance(held_positions,row[:,0],returns_history,characteristics_history,trading_costs)
        self.outer_cap_count+=int(np.abs(self.inner.target+self.sleeve/n).sum()>self.outer_gross_cap)
        self.targets.append(w.copy());self.sizing.append(self.multiplier)
        return w
