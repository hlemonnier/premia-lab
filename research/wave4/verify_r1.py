"""E2E verification of the registered R1 candidate; no isolated unit tests."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,platform,time
from pathlib import Path
from collections import Counter
from importlib.metadata import version
import numpy as np
import run_wave4 as W
from r1_candidate import RiskPolicy,CONFIG

class RecordedPolicy(RiskPolicy):
    def forecast(self,returns_history,characteristics_history):
        self.targets=[]
        return super().forecast(returns_history,characteristics_history)
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        w=super().rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        self.targets.append(w.copy())
        return w

def execute(name,R,X,cost,score,out):
    p=RecordedPolicy(CONFIG,sleeve=.05,outer_gross_cap=5.)
    rows,forecast_seconds=score.run(p,R,X,cost)
    target=np.array(p.targets)
    stats={'name':name,'source_days':len(R),'net_sharpe':W.metric(rows)['net_sharpe'],
      'forecast_seconds':forecast_seconds,'projected_forecast_hours_per_century':forecast_seconds/len(R)*25200/3600,
      'rebalance_ms':float(rows[:,4].mean()*1000),'solver_status':dict(Counter(c['status'] for c in p.certificates)),
      'latest_training_records':p.training_records[-2:]}
    np.save(out/(name+'_rows.npy'),rows);np.save(out/(name+'_targets.npy'),target)
    np.save(out/(name+'_forecast.npy'),p.forecast_output)
    W.save_json(out/(name+'.json'),stats);print(json.dumps(stats),flush=True)
    return p.forecast_output,target,rows,stats

def compare(name,a,b,tol=1e-10):
    err=float(np.max(np.abs(a-b),initial=0.));ok=bool(err<=tol)
    return {'check':name,'max_abs_error':err,'tolerance':tol,'passed':ok}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--mode',choices=['full','prefix','mutations'],required=True);a=ap.parse_args()
    score=W.load_score(a.source);R,X,cost=W.load_inputs(score,a.source,a.work)
    out=a.work/'verification';out.mkdir(exist_ok=True);checks=[]
    if a.mode=='full':
        f,w,rows,stats=execute('R1_integrated',R,X,cost,score,out)
        checks.append(compare('economic rows vs registered research R1',rows[:,:4],np.load(a.work/'results/R1_rows.npy')[:,:4]))
        checks.append(compare('all positions vs research R1',w,np.load(a.work/'results/R1_targets.npy')))
        checks.append(compare('F2 alpha unchanged',f[:,:,0],np.load(a.work/'cache/f2.npy')))
        expected=np.ones_like(f[:,:,1]);expected[1:]=.5+.5*np.load(a.work/'cache/R1_ratios.npy')[:-1]
        checks.append(compare('streamed risk multipliers vs research',f[:,:,1],expected))
        checks.append({'check':'complete forecast and uncached rebalance runtime','passed':stats['rebalance_ms']<100 and stats['projected_forecast_hours_per_century']<1,'rebalance_ms':stats['rebalance_ms'],'projected_hours':stats['projected_forecast_hours_per_century']})
        checks.append({'check':'all solves certified','passed':all(c in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal') for c in stats['solver_status'])})
    elif a.mode=='prefix':
        full_f=np.load(out/'R1_integrated_forecast.npy',mmap_mode='r');full_w=np.load(out/'R1_integrated_targets.npy',mmap_mode='r')
        for length in (630,2016):
            f,w,rows,_=execute(f'prefix_{length}',R[:length],X[:length],cost,score,out)
            checks.append(compare(f'prefix forecast {length}',f,full_f[:length]))
            checks.append(compare(f'prefix positions {length}',w,full_w[:len(w)]))
        # The second 630-row replay occurs after a different-length run in the same process.
        f,w,rows,_=execute('repeat_630',R[:630],X[:630],cost,score,out)
        checks.append(compare('repeat forecast after another session',f,np.load(out/'prefix_630_forecast.npy')))
        checks.append(compare('repeat positions after another session',w,np.load(out/'prefix_630_targets.npy')))
    else:
        full_f=np.load(out/'R1_integrated_forecast.npy',mmap_mode='r');full_w=np.load(out/'R1_integrated_targets.npy',mmap_mode='r')
        cases=[('return_future',630,900),('characteristic_future',630,900),('joint_future',2016,2268)]
        for i,(name,cut,length) in enumerate(cases):
            rr=np.array(R[:length],copy=True);xx=np.array(X[:length],copy=True);rng=np.random.default_rng(20261029+i)
            if name!='characteristic_future':rr[cut:]=rng.normal(0,.02,size=rr[cut:].shape)
            if name!='return_future':xx[cut:]=rng.normal(0,1,size=xx[cut:].shape)
            f,w,rows,_=execute(name,rr,xx,cost,score,out)
            checks.append(compare(f'{name} forecast through target row {cut}',f[:cut+1],full_f[:cut+1]))
            # today=252..cut-1 choose holdings for targets 253..cut, all before mutation.
            checks.append(compare(f'{name} executed positions before source mutation',w[:cut-252],full_w[:cut-252]))
    env={'python':platform.python_version(),'packages':{p:version(p) for p in ('numpy','pandas','scipy','scikit-learn')},'threads':{k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}}
    result={'mode':a.mode,'checks':checks,'environment':env,'passed':all(c['passed'] for c in checks)}
    W.save_json(out/(a.mode+'_checks.json'),result);print(json.dumps(result),flush=True)
    assert result['passed'],'E2E failed; see recorded checks'
if __name__=='__main__':main()
