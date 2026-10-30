"""Preregistered Wave 4. Run from repository root; private data are not included.

Example:
 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/wave4/run_wave4.py \
   --source '/path/Quant Research Take-Home' --work /path/wave4-work --mode controls

Uses unchanged supplied score.py and handoff_v3. Caches are causal snapshots,
not fitted full-sample models. All outputs are development evidence, not holdout results.
"""
from __future__ import annotations
import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_name]='1'
import argparse, hashlib, importlib.util, json, math, sys, time
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'handoff_v3'))
from model_v3 import engine as E
from model_v3 import policy as P
from model_v3.allocator import allocate_factor
import strategy as V3
CFG=dict(V3.POLICY.cfg)
EXPECTED=1.4447333005564316


def load_score(source):
    spec=importlib.util.spec_from_file_location('original_score',Path(source)/'score.py')
    score=importlib.util.module_from_spec(spec);spec.loader.exec_module(score)
    return score


def save_json(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def load_inputs(score,source,work):
    cache=work/'cache';cache.mkdir(exist_ok=True,parents=True)
    if not (cache/'R.npy').exists():
        arrays=score.load(str(source))
        for name,a in zip(('R','X','cost'),arrays):np.save(cache/(name+'.npy'),a)
    return tuple(np.load(cache/(name+'.npy'),mmap_mode='r') for name in ('R','X','cost'))


def risk_cache(R,X,cache):
    """Snapshot at index s uses only returns/characteristics through s (published)."""
    T,N=R.shape
    names=('basis','L','d','beta_risk','u2')
    if all((cache/(n+'.npy')).exists() for n in names) and (cache/'risk_complete.json').exists():
        return {n:np.load(cache/(n+'.npy'),mmap_mode='r') for n in names}
    shapes={'basis':(T,N,26),'L':(T,26,26),'d':(T,N),'beta_risk':(T,N),'u2':(T,N)}
    out={n:np.lib.format.open_memmap(cache/(n+'.npy'),mode='w+',dtype=np.float64,shape=shapes[n]) for n in names}
    R=np.ascontiguousarray(R,dtype=np.float64)
    state=E._RiskState(N,26,CFG)
    t0=time.perf_counter()
    for s in range(T):
        out['basis'][s]=E.basis(X[s],4.)
        out['beta_risk'][s]=E._window_beta(R[:s+1],252)
        if s:
            prior=state.U2.copy()
            state.absorb(R,X,s)
            out['u2'][s]=np.maximum(state.U2-state.aS*prior,0.)
            out['L'][s],out['d'][s]=state.model()
        else:
            out['L'][s]=0.;out['d'][s]=1e-6;out['u2'][s]=0.
        if s%1000==0:print('risk cache row',s,flush=True)
    for a in out.values():a.flush()
    save_json(cache/'risk_complete.json',{'rows':T,'seconds':time.perf_counter()-t0,'definition':'snapshot s is known after close s'})
    return out


class CachedBook:
    """Same certified allocator as V3; reuses policy-independent risk snapshots."""
    def __init__(self,cfg,n,rc,ratios=None):
        self.cfg=dict(cfg);self.target=np.zeros(n);self.warm={};self.rc=rc;self.ratios=ratios
    def rebalance(self,held,mu,R,X,costs,gamma,cap):
        s=len(R)-1;cfg={**self.cfg,'risk_aversion':gamma,'weight_cap':cap}
        d=self.rc['d'][s]
        if self.ratios is not None:d=d*(.5+.5*self.ratios[s])
        beta=self.rc['beta_risk'][s];info={}
        w=allocate_factor(mu,held,d,self.rc['basis'][s],self.rc['L'][s],beta,
                          np.asarray(costs,dtype=np.float64)/cfg['cost_horizon'],gamma,cap,warm=self.warm,info=info,beta_target=0.)
        gross=float(np.abs(w).sum());info['gross_action']='none'
        if gross>cfg['gross_cap']:w=w*(cfg['gross_cap']/gross);info['gross_action']='scaled'
        E._final_check(w,beta,0.,cfg);self.target=w
        return w,info


class CachedPolicy(P.ScorePolicy):
    def __init__(self,cfg,forecast_array,rc,ratios=None):
        super().__init__(cfg,sleeve=.05,outer_gross_cap=5.)
        self.pred=forecast_array;self.rc=rc;self.ratios=ratios;self.targets=[]
    def forecast(self,returns_history,characteristics_history):
        n=np.shape(returns_history)[1]
        self.virtual=CachedBook(self.cfg,n,self.rc,self.ratios)
        self.inner=CachedBook(self.cfg,n,self.rc,self.ratios)
        self.outer_target=np.zeros(n);self.sums={63:0.,1008:0.};self.masses={63:0.,1008:0.}
        self.earned=0;self.last_day=None;self.certificates=[];self.multiplier=1.;self.targets=[]
        self.forecast_output=self.pred[:len(returns_history)]
        return self.forecast_output
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        w=super().rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        self.targets.append(w.copy())
        return w


def metric(rows):
    net=rows[:,0]-rows[:,1];market=rows[:,3];mc=market-market.mean()
    return {'net_sharpe':float(np.sqrt(252)*net.mean()/net.std()),
            'gross_sharpe':float(np.sqrt(252)*rows[:,0].mean()/rows[:,0].std()),
            'beta':float(mc@(net-net.mean())/(mc@mc)),
            'annual_mean':float(252*net.mean()),'annual_vol':float(np.sqrt(252)*net.std()),
            'annual_cost':float(252*rows[:,1].mean()),'mean_gross':float(rows[:,2].mean()),
            'rebalance_ms':float(1000*rows[:,4].mean()),'n':int(len(rows))}


def summarize(rows):
    days=253+np.arange(len(rows));out=metric(rows)
    out['stages']=[metric(rows[(days>=lo)&(days<hi)]) for lo,hi in ((253,2016),(2016,3024),(3024,3779)) if np.any((days>=lo)&(days<hi))]
    k=len(rows)//2;out['halves']=[metric(rows[:k]),metric(rows[k:])]
    return out


def replay(name,pol,score,R,X,cost,out):
    t0=time.perf_counter();rows,sec=score.run(pol,R,X,cost)
    np.save(out/(name+'_rows.npy'),rows);np.save(out/(name+'_targets.npy'),np.array(pol.targets))
    res=summarize(rows);res.update(forecast_seconds=sec,wall_seconds=time.perf_counter()-t0,
        solver_status=dict(Counter(c['status'] for c in pol.certificates)))
    save_json(out/(name+'.json'),res)
    print(name,json.dumps(res),flush=True)
    return rows,res


def innovation_prediction(R,X,f2,cache):
    """Incremental EW ridge. Training residual for label u was predicted at u."""
    R=np.ascontiguousarray(R,dtype=np.float64);T,N=R.shape;beta,m=E.causal_betas(R)
    residual=R-beta*m[:,None]
    def features(s):
        D=np.hstack([E.basis(X[s],4.),E._zcol(beta[s+1],4.)[:,None]])
        innov=np.hstack([E._standardize(np.ascontiguousarray(X[s]-X[s-h]),4.) if s>=h else np.zeros((N,13)) for h in (1,21)])
        # Orthogonalization uses only current cross-sectional features, no labels.
        proj=np.linalg.solve(D.T@D/N+1e-8*np.eye(27),D.T@innov/N)
        return innov-D@proj
    gram=np.zeros((26,26));mom=np.zeros(26);mass=0.;pairs=0;decay=2.**(-1./1008.)
    inc=np.zeros_like(f2);t0=time.perf_counter()
    previous=features(0)
    for t in range(2,T):
        s=t-2
        D=previous if s==0 else current
        current=features(t-1)
        # A training label uses the actual causal baseline forecast for that label.
        y=residual[s+1]-f2[s+1]
        gram=decay*gram+D.T@D/N;mom=decay*mom+D.T@y/N;mass=decay*mass+1.;pairs+=1
        if pairs>=252:
            coef=np.linalg.solve(gram/mass+np.eye(26),mom/mass)
            extra=current@coef
            limit=.25*float(np.sqrt(np.mean(f2[t]**2)))
            scale=min(1.,limit/max(float(np.sqrt(np.mean(extra**2))),1e-30))
            inc[t]=scale*extra
    np.save(cache/'I1_increment.npy',inc)
    save_json(cache/'I1_forecast_meta.json',{'seconds':time.perf_counter()-t0,'max_rms_fraction':.25,'pairs_min':252})
    return f2+inc


def risk_prediction(rc,cache):
    from sklearn.ensemble import HistGradientBoostingRegressor
    T,N=rc['d'].shape
    zbeta=np.array([E._zcol(b,4.) for b in rc['beta_risk']])
    features=np.empty((T,N,15),dtype=np.float32)
    features[:,:,:13]=rc['basis'][:,:,:13]
    features[:,:,13]=zbeta;features[:,:,14]=np.log(rc['d'])
    ratios=np.ones((T,N),dtype=np.float64);model=None;records=[];t0=time.perf_counter()
    for target in range(253,T):
        s=target-1
        if (target-253)%126==0:
            label_days=np.arange(max(2,target-504),target,5)
            train=features[label_days-1].reshape(-1,15)
            y=np.minimum(rc['u2'][label_days]/rc['d'][label_days-1],25.).ravel()
            model=HistGradientBoostingRegressor(loss='poisson',learning_rate=.05,max_iter=80,
                max_leaf_nodes=15,min_samples_leaf=200,l2_regularization=10.,random_state=20261029,
                early_stopping=False)
            fit0=time.perf_counter();model.fit(train,y)
            rec={'target':target,'last_label':int(label_days[-1]),'rows':len(y),'fit_seconds':time.perf_counter()-fit0}
            records.append(rec);print('R1 fit',json.dumps(rec),flush=True)
        ratios[s]=np.clip(model.predict(features[s]),.5,2.)
    np.save(cache/'R1_ratios.npy',ratios)
    save_json(cache/'R1_training.json',{'seconds':time.perf_counter()-t0,'fits':records,'early_stopping':False,'first_target':253,'label_start':2})
    return ratios


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--mode',choices=['cache','controls','innovation','risk'],required=True);a=ap.parse_args()
    work=a.work;cache=work/'cache';out=work/'results';out.mkdir(exist_ok=True,parents=True)
    score=load_score(a.source);R,X,cost=load_inputs(score,a.source,work)
    rc=risk_cache(R,X,cache)
    if a.mode=='cache':return
    if not (cache/'f2.npy').exists():np.save(cache/'f2.npy',P.f2_forecast(R,X,CFG))
    f2=np.load(cache/'f2.npy',mmap_mode='r')
    if a.mode=='controls':
        rows,res=replay('B0_cached',CachedPolicy(CFG,f2,rc),score,R,X,cost,out)
        assert abs(res['net_sharpe']-EXPECTED)<1e-9,'baseline gate'
        reference=np.load(out/'B0_rows.npy')
        error=float(np.max(np.abs(rows[:,:4]-reference[:,:4])))
        save_json(out/'cache_equivalence.json',{'max_abs_rows_0_to_3':error,'tolerance':1e-10})
        assert error<1e-10,'cache changed replay'
        for name,horizon in [('C5',5.),('C80',80.)]:
            replay(name,CachedPolicy({**CFG,'cost_horizon':horizon},f2,rc),score,R,X,cost,out)
    elif a.mode=='innovation':
        pred=innovation_prediction(R,X,f2,cache)
        replay('I1',CachedPolicy(CFG,pred,rc),score,R,X,cost,out)
    elif a.mode=='risk':
        ratios=risk_prediction(rc,cache)
        replay('R1',CachedPolicy(CFG,f2,rc,ratios),score,R,X,cost,out)

if __name__=='__main__':main()
