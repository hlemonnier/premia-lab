"""Original-scorer research harness; no changes to supplied economic mechanics."""
from __future__ import annotations
import os
for _k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[_k]='1'
import argparse, hashlib, importlib.util, json, platform, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from model_f.factor_risk import FactorPolicy


def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def load_score(source):
    path=Path(source)/'score.py'
    expected='ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96'
    if sha256(path)!=expected: raise RuntimeError('unexpected original scorer identity')
    spec=importlib.util.spec_from_file_location('original_score',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def load_data(source,work):
    cache=Path(work)/'inputs';cache.mkdir(parents=True,exist_ok=True)
    if not (cache/'source_identity.json').exists():
        score=load_score(source)
        arrays=score.load(str(source))
        for k,a in zip(('R','X','cost'),arrays): np.save(cache/f'{k}.npy',a)
        write_json(cache/'source_identity.json',{
            k:sha256(Path(source)/k) for k in ['README.md','score.py','returns.csv','characteristics.csv','costs.csv']})
    return tuple(np.load(cache/f'{k}.npy',mmap_mode='r') for k in ('R','X','cost'))


def make_policy(candidate):
    if candidate=='F': return FactorPolicy()
    if candidate=='G':
        from gls_alpha import CandidatePolicy
        return CandidatePolicy()
    if candidate=='CORR':
        from research.gcorr.correlation_reference import CandidatePolicy
        return CandidatePolicy()
    if candidate in ('H20','L20','H1'):
        from research.horizon20.candidate import HorizonPolicy
        return HorizonPolicy(horizon=1 if candidate=='H1' else 20, delayed_one_day=candidate=='L20')
    if candidate=='GC':
        from research.gcorr.candidate import CandidatePolicy
        return CandidatePolicy()
    path=ROOT/'research'/candidate/'candidate.py'
    spec=importlib.util.spec_from_file_location(f'candidate_{candidate}',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.CandidatePolicy()


class Recorded:
    def __init__(self,policy):self.policy=policy
    def forecast(self,returns_history,characteristics_history):
        self.targets=[]
        self.forecasts=self.policy.forecast(returns_history,characteristics_history)
        return self.forecasts
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        w=self.policy.rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        self.targets.append(w.copy())
        return w


def independent_cashflows(targets,R,cost,start=252):
    vals=[]
    for i,day in enumerate(range(start+1,len(R)-1),start=1):
        prev=targets[i-1];g=float(np.sum(prev*R[day]))
        if g<=-1:raise RuntimeError('ruin')
        held=prev*(1+R[day])/(1+g)
        vals.append([g,float(np.sum(cost*np.abs(targets[i]-held))),
                     float(np.abs(targets[i]).sum()),float(R[day].mean())])
    return np.asarray(vals)


def metrics(rows):
    net=rows[:,0]-rows[:,1];m=rows[:,3];mm=m-m.mean()
    sr=lambda v:float(np.sqrt(252)*v.mean()/v.std()) if v.std()>0 else None
    beta=float(mm@(net-net.mean())/(mm@mm)) if mm@mm>0 else None
    return dict(n=len(net),net_sharpe=sr(net),gross_sharpe=sr(rows[:,0]),beta=beta,
                annual_return=float(net.mean()*252),annual_vol=float(net.std()*np.sqrt(252)),
                annual_fees=float(rows[:,1].mean()*252),mean_gross=float(rows[:,2].mean()),
                max_gross=float(rows[:,2].max()),worst_day=float(net.min()),
                rebalance_ms=float(rows[:,4].mean()*1000))


def summary(rows):
    d=253+np.arange(len(rows));out=metrics(rows)
    out['stages']=[metrics(rows[(d>=lo)&(d<hi)]) for lo,hi in [(253,2016),(2016,3024),(3024,3779)]
                   if np.any((d>=lo)&(d<hi))]
    h=len(rows)//2;out['halves']=[metrics(rows[:h]),metrics(rows[h:])]
    return out


def exercise(policy,R,X,cost,score):
    recorded=Recorded(policy)
    rows,seconds=score.run(recorded,R,X,cost)
    w=np.asarray(recorded.targets);f=recorded.forecasts
    if not all(np.isfinite(a).all() for a in [f,w,rows]):raise RuntimeError('nonfinite replay')
    econ=independent_cashflows(w,R,cost)
    return f,w,rows,seconds,econ


def run_main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--candidate',required=True)
    ap.add_argument('--sleeve',type=float,default=.05);ap.add_argument('--fees',type=float,default=1.);a=ap.parse_args()
    score=load_score(a.source);R,X,cost=load_data(a.source,a.work)
    p=make_policy(a.candidate);p.sleeve=a.sleeve;cost=np.asarray(cost)*a.fees
    name=a.candidate+('_nosleeve' if a.sleeve==0 else '')+(f'_fees{a.fees:g}' if a.fees!=1 else '')
    out=a.work/'runs'/name;out.mkdir(parents=True,exist_ok=True)
    tic=time.perf_counter();f,w,rows,sec,econ=exercise(p,R,X,cost,score)
    for k,v in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/f'{k}.npy',v)
    result=summary(rows)
    result.update(candidate=a.candidate,sleeve=a.sleeve,fee_multiplier=a.fees,forecast_seconds=sec,
        forecast_projected_hours_century=sec/len(R)*25200/3600,
        wall_seconds=time.perf_counter()-tic,
        independent_cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),
        certificates=dict(Counter(c['status'] for c in p.certificates)))
    result['max_factor_diagonal_relative_error']=max([getattr(getattr(getattr(p,b,None),'state',None),'max_relative_diagonal_error',0.) for b in ('inner','virtual')])
    write_json(out/'summary.json',result)
    for k in ['training_records','fit_records','learner_records']:
        if hasattr(p,k):write_json(out/f'{k}.json',getattr(p,k))
    if hasattr(p,'diagnostic_arrays'):
        np.savez_compressed(out/'diagnostics.npz',**p.diagnostic_arrays)
    print(json.dumps(result,indent=2),flush=True)
    assert result['independent_cashflow_error']<1e-10
    if a.candidate=='G' and a.sleeve==.05 and a.fees==1:
        assert abs(result['net_sharpe']-1.5332155606881952)<1e-9,'G reproduction failed'
    if a.candidate=='F' and a.sleeve==.05 and a.fees==1:
        assert abs(result['net_sharpe']-1.493439947872387)<1e-9,'F reproduction failed'
    assert result['rebalance_ms']<100
    assert result['forecast_projected_hours_century']<1

if __name__=='__main__':run_main()
