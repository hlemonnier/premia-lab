"""Original-scorer release replay. No model selection or parameter tuning."""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[name]='1'
import argparse, importlib.util, json, sys, time, resource, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2]

def write(p, x):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def inputs(source,work):
    c=work/'cache';c.mkdir(parents=True,exist_ok=True)
    if not (c/'ready.json').exists():
        score=module(source/'score.py','supplied_load')
        for name,a in zip(('R','X','cost'),score.load(str(source))): np.save(c/f'{name}.npy',a)
        write(c/'ready.json',{'source':str(source),'scorer_sha256':hashlib.sha256((source/'score.py').read_bytes()).hexdigest()})
    return [np.load(c/f'{name}.npy',mmap_mode='r') for name in ('R','X','cost')]

def load_policy(kind):
    if kind=='release':
        sys.path.insert(0,str(ROOT/'handoff_f'))
        return module(ROOT/'handoff_f/strategy.py','release_strategy')
    sys.path[:0]=[str(ROOT/'research/wave6'),str(ROOT/'research/wave5'),str(ROOT/'research/wave4'),str(ROOT/'handoff_v3')]
    if kind=='B0':
        return module(ROOT/'handoff_v3/strategy.py','baseline_strategy')
    from wave6_models import RiskStatePolicy
    return RiskStatePolicy(kind)

class Recorded:
    def __init__(self,p,store=True): self.p=p;self.store=store;self.weights=[];self.last=None;self.certificate_counts=Counter()
    def forecast(self,returns_history,characteristics_history):
        self.weights=[];self.f=self.p.forecast(returns_history,characteristics_history);return self.f
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        w=self.p.rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        if self.store: self.weights.append(w.copy())
        self.last=w
        return w

def stats(rows):
    x=rows[:,0]-rows[:,1];m=rows[:,3];mc=m-m.mean()
    out={'net_sharpe':float(np.sqrt(252)*x.mean()/x.std()),'gross_sharpe':float(np.sqrt(252)*rows[:,0].mean()/rows[:,0].std()),
    'annual_net_mean':float(x.mean()*252),'annual_vol':float(x.std()*np.sqrt(252)),'beta':float(mc@(x-x.mean())/(mc@mc)),
    'annual_fees':float(252*rows[:,1].mean()),'mean_gross':float(rows[:,2].mean()),'max_gross':float(rows[:,2].max()),
    'worst_net_day':float(x.min()),'n_scored':len(x),'rebalance_ms_mean':float(1000*rows[:,4].mean()),
    'rebalance_ms_p99':float(1000*np.quantile(rows[:,4],.99)),'rebalance_ms_max':float(1000*rows[:,4].max()),'finite':bool(np.isfinite(rows).all())}
    return out

def replay(kind,source,work,name,cost_scale=1,limit=None):
    R,X,cost=inputs(source,work)
    if limit: R=R[:limit];X=X[:limit]
    p=load_policy(kind);q=Recorded(p);score=module(source/'score.py','original_score')
    start=time.perf_counter();rows,forecast_s=score.run(q,R,X,cost*cost_scale)
    wall=time.perf_counter()-start;w=np.array(q.weights)
    out=work/'results';out.mkdir(exist_ok=True,parents=True)
    np.save(out/f'{name}_rows.npy',rows);np.save(out/f'{name}_forecast.npy',q.f);np.save(out/f'{name}_weights.npy',w)
    # Direct independent scorer accounting with first trade waived.
    previous=w[:-1];ret=np.einsum('ij,ij->i',previous,R[253:len(R)-1])
    drift=previous*(1+R[253:len(R)-1])/(1+ret[:,None])
    fees=np.abs(w[1:]-drift)@(cost*cost_scale)
    econ=np.column_stack((ret,fees,np.abs(w[1:]).sum(axis=1),R[253:len(R)-1].mean(axis=1)))
    error=float(np.max(np.abs(econ-rows[:,:4])))
    pol=p.POLICY if hasattr(p,'POLICY') else p
    result=stats(rows);result.update(kind=kind,cost_scale=cost_scale,forecast_seconds=forecast_s,wall_seconds=wall,
    projected_forecast_hours_per_century=forecast_s/len(R)*25200/3600,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
    cashflow_error=error,source_days=len(R),certificates=dict(Counter(c['status'] for c in pol.certificates)))
    write(out/f'{name}.json',result);print(json.dumps(result),flush=True)
    assert error<1e-10 and result['finite']
    assert all(x in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal') for x in result['certificates'])
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--work',type=Path,required=True)
    a.add_argument('--kind',required=True);a.add_argument('--name',required=True);a.add_argument('--cost-scale',type=float,default=1);a.add_argument('--limit',type=int)
    v=a.parse_args();replay(v.kind,v.source,v.work,v.name,v.cost_scale,v.limit)
