"""Frozen characteristic-peer variance pooling; research, not a new alpha model."""
from __future__ import annotations
import numpy as np
from gls_alpha import CandidatePolicy as GLS
from model_f import factor_risk as F
from research.relations.graph import PeerGraph

class PooledState(F._RescaledState):
    graph=None
    mode='V'
    min_ratio=1.
    max_ratio=1.
    def model(self):
        L,d=super().model()
        peer=(np.full_like(d,d.mean()) if self.mode=='VG' else (self.graph@d if len(d)>1 else d))
        ratio=np.clip(.5+.5*peer/d,.75,1.5)
        self.min_ratio=min(self.min_ratio,float(ratio.min()));self.max_ratio=max(self.max_ratio,float(ratio.max()))
        return L,d*ratio

class PooledBook(F._RescaledBook):
    def __init__(self,cfg,n,mode):
        super().__init__(cfg,n);self.mode=mode;self.graph=None
    def rebalance(self,held,mu,R,X,costs,gamma,cap):
        if self.state is None or self.state.upto>len(R):
            self.state=PooledState(R.shape[1],26,self.cfg)
        self.state.graph=self.graph;self.state.mode=self.mode
        return super().rebalance(held,mu,R,X,costs,gamma,cap)

class CandidatePolicy(GLS):
    def __init__(self,mode='V'):
        super().__init__()
        if mode not in ('V','VG'):raise ValueError('unknown pooling mode')
        self.mode=mode
    def forecast(self,returns_history,characteristics_history):
        out=super().forecast(returns_history,characteristics_history);n=np.shape(returns_history)[1]
        self.graph=PeerGraph();self.relation_diagnostics={};self.relation_records=[]
        self.virtual=PooledBook(self.cfg,n,self.mode);self.inner=PooledBook(self.cfg,n,self.mode)
        return out
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        t=len(returns_history)-1
        W=self.graph.at(characteristics_history,t) if self.mode=='V' else None
        self.virtual.graph=W;self.inner.graph=W
        w=super().rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        self.relation_diagnostics={**self.graph.diagnostics,
            'min_ratio':min(b.state.min_ratio for b in (self.virtual,self.inner)),
            'max_ratio':max(b.state.max_ratio for b in (self.virtual,self.inner))}
        return w
