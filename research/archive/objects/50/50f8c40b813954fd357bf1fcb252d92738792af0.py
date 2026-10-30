"""Fixed Wave5 evaluation. Reads completed runs; never changes a trading policy."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'research/wave4'),str(ROOT/'handoff_v3')]
import run_wave4 as W
from wave5_models import risk_paths,CONFIG


def sharpe(x):return np.sqrt(252)*np.mean(x,axis=0)/np.std(x,axis=0)

def holm(p):
    p=np.asarray(p);order=np.argsort(p);out=np.ones_like(p);level=0.
    for i,j in enumerate(order):level=max(level,min(1.,float((len(p)-i)*p[j])));out[j]=level
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    out=a.work/'results';names=['H','P','E'];reference=np.load(out/'R1_rows.npy');x=reference[:,0]-reference[:,1]
    ys=[];metrics={}
    for name in ['R1','H','P','E','A_pool','A_cross']:
        metrics[name]=json.loads((out/f'{name}.json').read_text())
    metrics['B0']=json.loads((out/'B0_portable_reproduction.json').read_text())
    for name in names:
        row=np.load(out/f'{name}_rows.npy');ys.append(row[:,0]-row[:,1])
    Y=np.array(ys).T;observed=sharpe(Y)-sharpe(x);n=len(x);blocks={}
    for length in (21,63,126):
        rng=np.random.default_rng(20261030);draws=np.empty((3000,len(names)))
        for i in range(len(draws)):
            starts=rng.integers(0,n,size=int(np.ceil(n/length)))
            idx=((starts[:,None]+np.arange(length))%n).ravel()[:n]
            draws[i]=sharpe(Y[idx])-sharpe(x[idx])
        centered=draws-observed
        p=(1+np.sum(centered>=observed,axis=0))/(len(draws)+1)
        corrected=holm(p);block={}
        for j,name in enumerate(names):
            block[name]={'difference':float(observed[j]),'interval95':np.quantile(draws[:,j],[.025,.975]).tolist(),
                         'fraction_positive':float(np.mean(draws[:,j]>0)),
                         'one_sided_centered_bootstrap_p':float(p[j]),'holm_adjusted_p':float(corrected[j])}
        blocks[str(length)]=block
        np.save(out/f'bootstrap_{length}_primary_deltas.npy',draws)
    gates={};r1=metrics['R1']
    for name in names:
        m=metrics[name];stages=np.array([s['net_sharpe'] for s in m['stages']])-np.array([s['net_sharpe'] for s in r1['stages']])
        halves=np.array([s['net_sharpe'] for s in m['halves']])-np.array([s['net_sharpe'] for s in r1['halves']])
        gate={'full_gain':m['net_sharpe']-r1['net_sharpe'],'stage_changes':stages.tolist(),'half_changes':halves.tolist(),
              'gain_at_least_005':m['net_sharpe']-r1['net_sharpe']>=.005,
              'two_improved_stages':int(np.sum(stages>0))>=2,'no_stage_below_minus_05':bool(np.min(stages)>=-.05),
              'beta_condition':abs(m['beta'])<.18 and m['beta']<=r1['beta']+.01,
              'runtime_condition':m['rebalance_ms']<100 and m['forecast_hours_per_century']<1,
              'risk_skill_condition':name!='H' or m['diagnostic']['qlike_vs_B0']<0}
        gate['development_gate_before_E2E']=all(gate[k] for k in ('gain_at_least_005','two_improved_stages','no_stage_below_minus_05','beta_condition','runtime_condition','risk_skill_condition'))
        gate['strong_statistics']=all(blocks[str(b)][name]['interval95'][0]>0 and blocks[str(b)][name]['holm_adjusted_p']<.05 for b in (21,63,126)) and bool(np.all(halves>0))
        gates[name]=gate
    # Diagnostics after all trading: no feedback into any model.
    score=W.load_score(a.source);R,X,cost=W.load_inputs(score,a.source,a.work)
    d,u2,_,_=risk_paths(R,X,CONFIG)
    variance={}
    for name in ('R1','H','A_pool','A_cross'):
        f=np.load(out/f'{name}_forecast.npy',mmap_mode='r');z=f[253:len(R)-1,:,1]
        q=np.log(z)+(u2[253:len(R)-1]/d[252:len(R)-2])*(1/z-1)
        variance[name]={'qlike_vs_B0':float(q.mean()),'stage_means':[float(z.mean()) for z in (q[:1763],q[1763:2771],q[2771:])],
                        'average_cross_sectional_multiplier_sd':float(f[253:,:,1].std(axis=1).mean())}
    beta,market=W.E.causal_betas(np.ascontiguousarray(R));res=R-beta*market[:,None];alpha={}
    f2=np.load(a.work/'cache/f2.npy',mmap_mode='r')
    for name,pred in [('B0',f2),('P',np.load(out/'P_forecast.npy',mmap_mode='r')[:,:,0])]:
        q=pred[253:len(R)-1];y=res[253:len(R)-1];q=q-q.mean(axis=1,keepdims=True);y=y-y.mean(axis=1,keepdims=True)
        ic=np.sum(q*y,axis=1)/np.maximum(np.sqrt(np.sum(q*q,axis=1)*np.sum(y*y,axis=1)),1e-30)
        alpha[name]={'daily_IC_mean':float(ic.mean()),'daily_IC_sharpe':float(sharpe(ic)),
                     'residual_mse':float(np.mean((pred[253:len(R)-1]-res[253:len(R)-1])**2))}
    b0=metrics['B0'];ablation_fraction=(metrics['A_pool']['net_sharpe']-b0['net_sharpe'])/(r1['net_sharpe']-b0['net_sharpe'])
    combinations={
        'HP_allowed':all(metrics[k]['net_sharpe']-r1['net_sharpe']>=.005 and sum(metrics[k]['stages'][j]['net_sharpe']>r1['stages'][j]['net_sharpe'] for j in range(3))>=2 for k in ('H','P')),
        'E_combination_allowed':metrics['E']['net_sharpe']-b0['net_sharpe']>=.005 and sum(metrics['E']['stages'][j]['net_sharpe']>b0['stages'][j]['net_sharpe'] for j in range(3))>=2}
    report={'metrics':metrics,'primary_comparison_reference':'R1','bootstrap':blocks,'gates':gates,'variance_diagnostics':variance,
            'alpha_diagnostics':alpha,'A_pool_fraction_of_R1_development_gain':float(ablation_fraction),'combinations':combinations,
            'selection_caveat':'All history exposed. Holm covers this wave only, not all project trials. Bootstrap probabilities are not probabilities of future superiority.'}
    W.save_json(out/'WAVE5_ASSESSMENT.json',report)
    print(json.dumps({'bootstrap63':blocks['63'],'gates':gates,'variance_diagnostics':variance,'alpha_diagnostics':alpha,'A_pool_gain_fraction':float(ablation_fraction),'combinations':combinations},indent=2),flush=True)

if __name__=='__main__':main()
