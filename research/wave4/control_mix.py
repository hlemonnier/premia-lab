"""Full-information online expert controller; not a claim of deep RL.

Shadow target paths come from causal policy replay. Actual traded-book costs are
recomputed by the unchanged scorer, never averaged from expert net returns.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from pathlib import Path
import numpy as np
import run_wave4 as W

class ExpertController:
    def __init__(self,targets):
        self.expert_targets=targets
    def forecast(self,returns_history,characteristics_history):
        T,N=np.shape(returns_history)
        self.prev=np.zeros((3,N));self.mean=np.zeros(3);self.second=np.zeros(3);self.mass=0.;self.count=0
        self.mix=np.array([0.,1.,0.]);self.targets=[];self.weights=[];self.certificates=[];self.last_day=None
        return np.zeros((T,1))
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        t=len(returns_history)-1
        if self.last_day is not None and t!=self.last_day+1:raise RuntimeError('non-sequential replay')
        r=returns_history[-1];gross_returns=self.prev@r
        if np.any(gross_returns<=-1):raise RuntimeError('expert ruin')
        held=self.prev*(1+r)[None,:]/(1+gross_returns)[:,None]
        current=self.expert_targets[:,t-252,:]
        fees=np.abs(current-held)@trading_costs
        if self.last_day is not None:
            reward=gross_returns-fees;decay=2.**(-1./252.)
            self.mean=decay*self.mean+reward;self.second=decay*self.second+reward*reward;self.mass=decay*self.mass+1.;self.count+=1
        if self.count>=252 and (t-252)%5==0:
            m=self.mean/self.mass;var=np.maximum(self.second/self.mass-m*m,1e-12)
            sh=np.clip(np.sqrt(252)*m/np.sqrt(var),-3.,3.)
            e=np.exp(sh-sh.max());self.mix=.5*e/e.sum()+np.array([0.,.5,0.])
        w=self.mix@current
        if not np.isfinite(w).all() or np.abs(w).sum()>5*(1+1e-12):raise RuntimeError('controller bound')
        self.prev=current.copy();self.last_day=t;self.targets.append(w.copy());self.weights.append(self.mix.copy())
        return w

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    score=W.load_score(a.source);R,X,cost=W.load_inputs(score,a.source,a.work)
    targets=np.array([np.load(a.work/'results'/f'{name}_targets.npy') for name in ('C5','B0_cached','C80')])
    pol=ExpertController(targets)
    rows,res=W.replay('Cmix',pol,score,R,X,cost,a.work/'results')
    np.save(a.work/'results/Cmix_weights.npy',np.array(pol.weights))
    W.save_json(a.work/'results/Cmix_weights_summary.json',{'mean':np.mean(pol.weights,axis=0).tolist(),'minimum':np.min(pol.weights,axis=0).tolist(),'maximum':np.max(pol.weights,axis=0).tolist(),'order':['C5','B0','C80']})
if __name__=='__main__':main()
