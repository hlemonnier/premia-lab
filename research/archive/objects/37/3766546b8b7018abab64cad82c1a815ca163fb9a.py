"""100-year operational endurance, not an independent economic simulation."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,time,json,resource,gc
from pathlib import Path
from collections import Counter
import numpy as np
import runner as V

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    R,X,cost=V.inputs(a.source,a.work);T,N=25200,R.shape[1];out=a.work/'endurance';out.mkdir(exist_ok=True)
    for name,base in [('R',R),('X',X)]:
        path=out/f'{name}.npy'
        if not path.exists():
            dst=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(T,)+base.shape[1:])
            for lo in range(0,T,len(base)):
                k=min(T-lo,len(base));dst[lo:lo+k]=base[:k]
            dst.flush();del dst
    del R,X;gc.collect()
    R=np.load(out/'R.npy',mmap_mode='r');X=np.load(out/'X.npy',mmap_mode='r');p=V.load_policy('release')
    score=V.module(a.source/'score.py','century_score')
    checks=[]
    class Audited:
        def __init__(self):self.prev=np.zeros(N);self.cash_error=0.;self.max_position=0.;self.max_gross=0.;self.min_gross_return=0.;self.calls=0
        def forecast(self,returns_history,characteristics_history):return p.forecast(returns_history,characteristics_history)
        def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
            r=returns_history[-1];g=float(self.prev@r)
            drift=self.prev*(1+r)/(1+g)
            self.cash_error=max(self.cash_error,float(np.max(np.abs(drift-held_positions))))
            w=p.rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
            self.max_position=max(self.max_position,float(np.abs(w).max()));self.max_gross=max(self.max_gross,float(np.abs(w).sum()));self.min_gross_return=min(self.min_gross_return,g)
            assert np.isfinite(w).all() and g>-1
            self.prev=w;self.calls+=1
            if self.calls%5000==0:print(json.dumps({'calls':self.calls,'rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}),flush=True)
            return w
    q=Audited();start=time.perf_counter();rows,forecast_s=score.run(q,R,X,cost);wall=time.perf_counter()-start
    forecasts=p.POLICY.forecast_output
    np.save(out/'rows.npy',rows);np.save(out/'forecast.npy',forecasts)
    cert=dict(Counter(x['status'] for x in p.POLICY.certificates))
    stats={'type':'operational endurance on repeated supplied data; not new future performance evidence','days':T,'stocks':N,'calls':q.calls,
    'forecast_seconds':forecast_s,'rebalance_ms_mean':float(1000*rows[:,4].mean()),'rebalance_ms_p99':float(1000*np.quantile(rows[:,4],.99)),
    'rebalance_ms_max':float(1000*rows[:,4].max()),'wall_seconds':wall,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
    'risk_min':float(forecasts[:,N:].min()),'risk_max':float(forecasts[:,N:].max()),'all_outputs_finite':bool(np.isfinite(rows).all() and np.isfinite(forecasts).all()),
    'max_gross':q.max_gross,'max_abs_weight':q.max_position,'min_gross_return':q.min_gross_return,'drift_reconstruction_error':q.cash_error,'certificates':cert,
    'fit_count':len(p.POLICY.training_records),'latest_fit':p.POLICY.training_records[-1]}
    checks.append({'name':'actual century runtime','passed':forecast_s<3600 and stats['rebalance_ms_mean']<100})
    checks.append({'name':'finite, bounded, no ruin, certified','passed':stats['all_outputs_finite'] and q.max_gross<=5+1e-10 and q.min_gross_return>-1 and set(cert)<=set(['ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal'])})
    checks.append({'name':'independent drift','passed':q.cash_error<1e-10})
    # Past prefix remains invariant even though the full call sees 100 years.
    original=np.load(a.work/'results/release_forecast.npy',mmap_mode='r')
    err=float(np.max(np.abs(forecasts[:3780]-original)));checks.append({'name':'15-year forecasts vs century prefix','max_error':err,'passed':err<1e-10})
    V.write(out/'endurance.json',dict(stats,checks=checks,passed=all(x['passed'] for x in checks)))
    print(json.dumps(stats),flush=True)
    # Full-path late-return mutation, beyond supplied history and around refit boundaries.
    cut=25074;rr=np.array(R);rng=np.random.default_rng(20261101);rr[cut:]=rng.normal(0,.01,rr[cut:].shape)
    del forecasts;gc.collect()
    ff=p.forecast(rr,X)
    original=np.load(out/'forecast.npy',mmap_mode='r')
    # Chunked comparison prevents an unnecessary >200 MB temporary.
    err=0.
    for lo in range(0,cut+1,252):
        hi=min(cut+1,lo+252);err=max(err,float(np.max(abs(ff[lo:hi]-original[lo:hi]))))
    checks.append({'name':'late future-return mutation at source 25074','max_error':err,'passed':err<1e-10})
    V.write(out/'endurance.json',dict(stats,checks=checks,passed=all(x['passed'] for x in checks)))
    print(json.dumps({'late_mutation_error':err,'all_checks_passed':all(x['passed'] for x in checks)}),flush=True)
    assert all(x['passed'] for x in checks)
if __name__=='__main__':main()
