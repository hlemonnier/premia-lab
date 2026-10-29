"""Prespecified attribution contrasts; no model or portfolio tuning."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research/common'))
import harness as H
from model_f import engine as E

KEYS=['F','G_D','O_D','G_S','O_S','D_D','O_A','G_N']
CONTRASTS={'covariance_diagonal_ridge':('G_D','O_D'),'covariance_scalar_ridge':('G_S','O_S'),
 'GLS_vs_F':('G_D','F'),'OLS_diagonal_vs_absolute':('O_D','O_A'),
 'OLS_startup_vs_F':('O_A','F'),'full_vs_specific_weighting':('G_D','D_D'),
 'daily_intercept':('G_D','G_N'),'GLS_penalty_geometry':('G_D','G_S')}


def sr(x):return np.sqrt(252)*np.mean(x,axis=0)/np.std(x,axis=0)


def bootstrap(panel,draws=3000):
    n,k=panel.shape;out={};rng=np.random.default_rng(20261103)
    extended=np.concatenate([panel,panel]);cs=np.vstack([np.zeros(k),np.cumsum(extended,axis=0)]);c2=np.vstack([np.zeros(k),np.cumsum(extended**2,axis=0)])
    obs=sr(panel);ind={key:i for i,key in enumerate(KEYS)}
    for length in [21,63,126]:
        nb=int(np.ceil(n/length));last=n-(nb-1)*length;vals=[]
        for begin in range(0,draws,100):
            m=min(100,draws-begin);starts=rng.integers(0,n,size=(m,nb));sizes=np.full(nb,length);sizes[-1]=last
            sums=(cs[starts+sizes]-cs[starts]).sum(axis=1);squares=(c2[starts+sizes]-c2[starts]).sum(axis=1)
            means=sums/n;std=np.sqrt(np.maximum(squares/n-means*means,1e-30));vals.append(np.sqrt(252)*means/std)
        sampled=np.concatenate(vals);row={}
        for name,(a,b) in CONTRASTS.items():
            delta=sampled[:,ind[a]]-sampled[:,ind[b]];observed=float(obs[ind[a]]-obs[ind[b]])
            row[name]=dict(observed=observed,interval95=np.quantile(delta,[.025,.975]).tolist(),
                centered_one_sided_p=float((1+np.sum(delta-observed>=observed))/(draws+1)),positive_draw_fraction=float(np.mean(delta>0)))
        interaction=(sampled[:,ind['G_D']]-sampled[:,ind['O_D']])-(sampled[:,ind['G_S']]-sampled[:,ind['O_S']])
        row['weighting_penalty_interaction']={'observed':float((obs[ind['G_D']]-obs[ind['O_D']])-(obs[ind['G_S']]-obs[ind['O_S']])),
            'interval95':np.quantile(interaction,[.025,.975]).tolist()}
        names=['covariance_diagonal_ridge','covariance_scalar_ridge'];order=sorted(names,key=lambda x:row[x]['centered_one_sided_p']);prev=0.
        for rank,name in enumerate(order):
            prev=max(prev,min(1.,(2-rank)*row[name]['centered_one_sided_p']));row[name]['holm_p_two_primary']=prev
        out[str(length)]=row
    return out


def diagnostics(work,source):
    R,X,c=H.load_data(source,work);beta,m=E.causal_betas(np.ascontiguousarray(R));target=R-beta*m[:,None]
    day=253+np.arange(3526);y=np.array(target[253:3779]);yc=y-y.mean(axis=1,keepdims=True)
    ref=np.load(work/'runs/F/forecast.npy',mmap_mode='r');out={};daily={}
    for key in KEYS:
        f=np.load(work/'runs'/key/'forecast.npy',mmap_mode='r');pred=f[253:3779,:R.shape[1]];pc=pred-pred.mean(axis=1,keepdims=True)
        denominator=np.linalg.norm(pc,axis=1)*np.linalg.norm(yc,axis=1)
        ic=np.sum(pc*yc,axis=1)/np.maximum(denominator,1e-30);err=np.mean((pred-y)**2,axis=1)
        out[key]={'mean_IC':float(ic.mean()),'IC_sharpe':float(sr(ic)),'mean_squared_error':float(err.mean()),
          'risk_payload_error':float(np.max(np.abs(f[:,R.shape[1]:]-ref[:,R.shape[1]:]))),
          'prediction_RMS':float(np.sqrt(np.mean(pred*pred)))}
        daily[key+'_ic']=ic;daily[key+'_mse']=err
    np.savez_compressed(work/'diagnostic_daily.npz',**daily);return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--source',type=Path,required=True);a=p.parse_args()
    values={key:json.loads((a.work/'runs'/key/'summary.json').read_text()) for key in KEYS}
    panel=np.column_stack([np.load(a.work/'runs'/k/'rows.npy')[:,0]-np.load(a.work/'runs'/k/'rows.npy')[:,1] for k in KEYS])
    # Independent direct metrics rather than relying solely on score/harness summaries.
    recon={}
    for i,key in enumerate(KEYS):
        rows=np.load(a.work/'runs'/key/'rows.npy');net=panel[:,i];market=rows[:,3]
        beta=np.linalg.lstsq(np.column_stack([np.ones(len(net)),market]),net,rcond=None)[0][1]
        recon[key]={'sharpe_error':float(abs(sr(net)-values[key]['net_sharpe'])),'beta_error':float(abs(beta-values[key]['beta']))}
    assert all(d['sharpe_error']<1e-12 and d['beta_error']<1e-12 for d in recon.values())
    contrasts={}
    for name,(x,y) in CONTRASTS.items():
        contrasts[name]={'full':values[x]['net_sharpe']-values[y]['net_sharpe'],
          'stages':[values[x]['stages'][j]['net_sharpe']-values[y]['stages'][j]['net_sharpe'] for j in range(3)],
          'halves':[values[x]['halves'][j]['net_sharpe']-values[y]['halves'][j]['net_sharpe'] for j in range(2)]}
    result={'scored_rows':[253,3779],'n':len(panel),'summary':values,'contrasts':contrasts,'bootstrap':bootstrap(panel),
         'diagnostics':diagnostics(a.work,a.source),'independent_metric_check':recon,'new_model_selection':False,'main_modified':False}
    robust={}
    for file in (a.work/'runs').glob('*/summary.json'):
        if '_fee' in file.parent.name or '_nosleeve' in file.parent.name:robust[file.parent.name]=json.loads(file.read_text())
    result['robustness']=robust;H.write_json(a.work/'ASSESSMENT.json',result)
    print(json.dumps({k:result[k] for k in ['contrasts','diagnostics']},indent=2),flush=True)
if __name__=='__main__':main()
