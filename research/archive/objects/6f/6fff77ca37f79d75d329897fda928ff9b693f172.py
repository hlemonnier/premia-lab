"""Fixed assessment for GC/H20. Exposed-history evidence, not fresh validation."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research.common import harness as H
from model_f import engine as E


def shortlist(base,result):
    stage=[v['net_sharpe']-b['net_sharpe'] for v,b in zip(result['stages'],base['stages'])]
    halves=[v['net_sharpe']-b['net_sharpe'] for v,b in zip(result['halves'],base['halves'])]
    gate=dict(gain=result['net_sharpe']-base['net_sharpe']>=.005,
        stage_count=sum(x>0 for x in stage)>=2,halves=min(halves)>=0,
        worst_stage=min(stage)>=-.05,beta=abs(result['beta'])<.18 and result['beta']<=base['beta']+.01,
        runtime=result['rebalance_ms']<100 and result['forecast_projected_hours_century']<1,
        cashflow=result['independent_cashflow_error']<1e-10,
        certified=set(result['certificates'])<=set(['ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal']))
    return dict(gates=gate,passed=all(gate.values()),stage_gains=stage,half_gains=halves)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);a=ap.parse_args()
    w=a.work;names=['G','GC','H20','L20','F','CORR']
    summaries={n:json.loads((w/'runs'/n/'summary.json').read_text()) for n in names}
    rows={n:np.load(w/'runs'/n/'rows.npy') for n in names}
    results={'summaries':summaries,'shortlist':{n:shortlist(summaries['G'],summaries[n]) for n in ['GC','H20']}}
    for n in ('GC','H20'):
        receipts=[json.loads((w/'checks'/f'{n}_{m}.json').read_text()) for m in ('synthetic','market')]
        results['shortlist'][n]['e2e']=all(r['passed'] for r in receipts)
        results['shortlist'][n]['passed'] &= results['shortlist'][n]['e2e']
    r=np.column_stack([rows[n][:,0]-rows[n][:,1] for n in names]);T=len(r)
    sr=lambda v:np.sqrt(252)*v.mean(axis=0)/v.std(axis=0)
    observed=sr(r);rng=np.random.default_rng(20261104);boot={}
    for length in (21,63,126):
        draws=np.empty((3000,len(names)))
        for j in range(len(draws)):
            starts=rng.integers(0,T,size=int(np.ceil(T/length)))
            idx=((starts[:,None]+np.arange(length))%T).ravel()[:T]
            draws[j]=sr(r[idx])
        entry={};pvals=[]
        for k,n in enumerate(names[1:3],start=1):
            delta=draws[:,k]-draws[:,0];obs=observed[k]-observed[0]
            p=float((1+np.sum(delta-obs>=obs))/(len(delta)+1));pvals.append(p)
            entry[n]=dict(gain=float(obs),interval=np.quantile(delta,[.025,.975]).tolist(),centered_p=p,
                          positive_fraction=float(np.mean(delta>0)))
        order=np.argsort(pvals);cum=0.
        for rank,i in enumerate(order):
            cum=max(cum,min(1.,(2-rank)*pvals[i]));entry[names[i+1]]['holm_p']=cum
        interaction=(draws[:,1]-draws[:,0])-(draws[:,5]-draws[:,4])
        entry['combination_interaction']=dict(observed=float((observed[1]-observed[0])-(observed[5]-observed[4])),
             interval=np.quantile(interaction,[.025,.975]).tolist())
        boot[str(length)]=entry
    results['bootstrap']=boot
    results['stock_order_checks']={n:json.loads((w/'checks'/f'{n}_permutation.json').read_text()) for n in ['G','GC','H20']}
    results['all_registered_checks_passed']=all(d['passed'] for d in results['stock_order_checks'].values())
    results['main_promotion']=False
    results['numerical_note']='Strict aggregate-gross stock-order checks remain failed; research shortlisting is not full numerical/release sign-off.'
    R,X,cost=H.load_data(a.source,w);R=np.ascontiguousarray(R,dtype=np.float64)
    beta,market=E.causal_betas(R);e=R-beta*market[:,None];N=R.shape[1]
    forecasts={n:np.load(w/'runs'/n/'forecast.npy',mmap_mode='r') for n in ['G','GC','H20','L20']}
    results['identities']={'GC_main_forecast_channels_max_error':float(np.max(np.abs(forecasts['GC'][:,:N+27]-forecasts['G']))),
        'H20_risk_channels_max_error':float(np.max(np.abs(forecasts['H20'][:,N:]-forecasts['G'][:,N:])))}
    diag={};outputs={}
    dates=np.arange(253,len(R)-20+1)
    y20=np.array([np.mean(e[t:t+20],axis=0) for t in dates])
    for n in ['G','H20','L20']:
        pred=forecasts[n][dates,:N];yn=e[dates]
        def metrics(y):
            pc=pred-pred.mean(axis=1,keepdims=True);yc=y-y.mean(axis=1,keepdims=True)
            ic=np.sum(pc*yc,axis=1)/np.maximum(np.linalg.norm(pc,axis=1)*np.linalg.norm(yc,axis=1),1e-30)
            return dict(mse=float(np.mean((pred-y)**2)),mean_ic=float(ic.mean()),ic_mean_std_annualized=float(np.sqrt(252)*ic.mean()/ic.std()))
        diag[n]=dict(common_dates=len(dates),next_day=metrics(yn),forward20_daily_average=metrics(y20))
    results['forecast_diagnostics']=diag
    H.write_json(w/'ASSESSMENT.json',results)
    print(json.dumps({k:v for k,v in results.items() if k!='summaries'},indent=2))
if __name__=='__main__':main()
