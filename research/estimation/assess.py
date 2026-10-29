"""Frozen two-candidate comparisons; never used to tune either policy."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from model_f import engine as E
from research.common import harness as H


def holm(ps):
    ix=np.argsort(ps);out=np.empty(len(ps));last=0.
    for j,k in enumerate(ix):last=max(last,min(1.,(len(ps)-j)*ps[k]));out[k]=last
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    names=['G','GC','R','K'];root=a.work/'runs'
    summaries={n:json.loads((root/n/'summary.json').read_text()) for n in names}
    rows={n:np.load(root/n/'rows.npy') for n in names};nets={n:v[:,0]-v[:,1] for n,v in rows.items()};base=summaries['GC']
    report={'references':{n:summaries[n] for n in ['G','GC']},'candidates':{},'bootstrap':{},'diagnostics':{}}
    for n in ['R','K']:
        d=summaries[n];stages=[x['net_sharpe']-y['net_sharpe'] for x,y in zip(d['stages'],base['stages'])]
        halves=[x['net_sharpe']-y['net_sharpe'] for x,y in zip(d['halves'],base['halves'])]
        gain=d['net_sharpe']-base['net_sharpe'];software={}
        for mode in ['synthetic','market']:
            f=a.work/'checks'/f'{n}_{mode}.json';software[mode]=json.loads(f.read_text())['passed'] if f.exists() else None
        economic=(gain>=.005 and sum(x>0 for x in stages)>=2 and min(stages)>=-.05 and min(halves)>=0
                  and abs(d['beta'])<.18 and d['beta']<=base['beta']+.01)
        report['candidates'][n]={'summary':d,'gain_vs_GC':gain,'gain_vs_G':d['net_sharpe']-summaries['G']['net_sharpe'],
            'stage_changes':stages,'half_changes':halves,'economic_shortlist':economic,'software_checks':software,
            'stress_admitted':bool(economic and all(x is True for x in software.values()))}
    # Entire dates resampled, not correlated stock/date observations treated as independent.
    rng=np.random.default_rng(20261106);N=len(nets['GC']);s=lambda v:np.sqrt(252)*v.mean()/v.std()
    for block in [21,63,126]:
        ds=np.empty((3000,2))
        for j in range(3000):
            starts=rng.integers(0,N,size=int(np.ceil(N/block)));idx=((starts[:,None]+np.arange(block))%N).ravel()[:N]
            b=s(nets['GC'][idx])
            for k,n in enumerate(['R','K']):ds[j,k]=s(nets[n][idx])-b
        obs=np.array([report['candidates'][n]['gain_vs_GC'] for n in ['R','K']])
        ps=np.array([(1+np.sum(ds[:,k]-obs[k]>=obs[k]))/3001 for k in range(2)])
        hp=holm(ps);o={}
        for k,n in enumerate(['R','K']):o[n]={'gain':float(obs[k]),'ci95':np.quantile(ds[:,k],[.025,.975]).tolist(),
            'centered_one_sided_p':float(ps[k]),'holm_p':float(hp[k]),'fraction_positive_not_future_probability':float(np.mean(ds[:,k]>0))}
        report['bootstrap'][str(block)]=o
    R,X,c=H.load_data(a.source,a.work);beta,market=E.causal_betas(R,252);target=R-beta*market[:,None]
    t=np.arange(253,len(R)-1);yy=np.asarray(target[t]);yc=yy-yy.mean(1,keepdims=True)
    yn=np.linalg.norm(yc,axis=1)
    for n in names:
        pp=np.load(root/n/'forecast.npy',mmap_mode='r')[t,:R.shape[1]];pc=pp-pp.mean(1,keepdims=True)
        ic=np.sum(pc*yc,axis=1)/np.maximum(np.linalg.norm(pc,axis=1)*yn,1e-30)
        report['diagnostics'][n]={'forecast_mse':float(np.mean((pp-yy)**2)), 'mean_daily_ic':float(ic.mean()),
            'annualized_ic_mean_std':float(np.sqrt(252)*ic.mean()/ic.std()),'prediction_rms':float(np.sqrt(np.mean(pp*pp)))}
    rd=np.load(root/'R/diagnostics.npz');w=rd['reliability'][253:3779]
    report['robust_weights']={'mean':float(w.mean()),'minimum':float(w.min()),'fraction_below_one':float(np.mean(w<1)),
        'fraction_at_floor':float(np.mean(w<=.05)),'quantiles':np.quantile(w,[0,.05,.25,.5,.75,.95,1]).tolist(),
        'stage_means':[float(rd['reliability'][lo:hi].mean()) for lo,hi in [(253,2016),(2016,3024),(3024,3779)]]}
    report['limits']='All exposed development data. No independent holdout; Holm covers only this round. No century test or independent reviewer. No main promotion.'
    H.write_json(a.work/'ASSESSMENT.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
