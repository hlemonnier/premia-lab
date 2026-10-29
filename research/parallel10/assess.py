"""Fixed batch inference, including every registered primary/control contrast."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.parallel10 import harness as H


def holm(p):
    order=np.argsort(p);out=np.empty(len(p));previous=0.
    for j,i in enumerate(order):previous=max(previous,min(1.,(len(p)-j)*p[i]));out[i]=previous
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();w=a.work
    modes=['G','N','N0','V','V0','R','R0','M','M0','C','C0'];summaries={};net=[]
    for m in modes:
        summaries[m]=json.loads((w/'runs'/m/'summary.json').read_text());r=np.load(w/'runs'/m/'rows.npy');net.append(r[:,0]-r[:,1])
    net=np.column_stack(net);sr=lambda z:np.sqrt(252)*z.mean(0)/z.std(0);original=sr(net)
    contrasts=[(m,'G') for m in ['N','V','R','M','C']]+[(m,m+'0') for m in ['N','V','R','M','C']]
    indices=[(modes.index(x),modes.index(y)) for x,y in contrasts];boot={}
    for block in (21,63,126):
        rng=np.random.default_rng(20261106);draw=[];n=len(net)
        for _ in range(3000):
            starts=rng.integers(0,n,int(np.ceil(n/block)));ix=((starts[:,None]+np.arange(block))%n).ravel()[:n];s=sr(net[ix]);draw.append([s[i]-s[j] for i,j in indices])
        draw=np.asarray(draw);observed=np.array([original[i]-original[j] for i,j in indices]);raw=(1+np.sum(draw-observed>=observed,axis=0))/(len(draw)+1);adj=holm(raw)
        boot[str(block)]={f'{x}-{y}':dict(gain=float(observed[k]),ci95=np.quantile(draw[:,k],[.025,.975]).tolist(),centered_one_sided_p=float(raw[k]),holm_p=float(adj[k])) for k,(x,y) in enumerate(contrasts)}
    gates={};g=summaries['G'];benchmark=1.5473865516722796
    for m in ['N','V','R','M','C']:
        d=summaries[m];control=summaries[m+'0'];st=[a['net_sharpe']-b['net_sharpe'] for a,b in zip(d['stages'],g['stages'])];ha=[a['net_sharpe']-b['net_sharpe'] for a,b in zip(d['halves'],g['halves'])]
        criteria=dict(gain_vs_G=d['net_sharpe']-g['net_sharpe']>=.005,gain_vs_control=d['net_sharpe']-control['net_sharpe']>=.003,two_stages=sum(x>0 for x in st)>=2,both_halves=all(x>0 for x in ha),no_large_stage_decline=min(st)>=-.05,beta=abs(d['beta'])<.18 and d['beta']<=g['beta']+.01,runtime=d['rebalance_ms']<100,cashflows=d['cashflow_error']<1e-10,certificates=set(d['certificates'])=={'ok'})
        gates[m]=dict(criteria=criteria,economic_gate_pass=all(criteria.values()),stages=st,halves=ha,beats_archived_GC=d['net_sharpe']>benchmark)
    # All next-day ICs use the same scored dates and label definition.
    R=np.load(w/'inputs/R.npy',mmap_mode='r');b=np.load(w/'shared/beta.npy',mmap_mode='r');mk=np.load(w/'shared/market.npy',mmap_mode='r');N=R.shape[1]
    y=np.asarray(R[253:3779]-b[253:3779]*mk[253:3779,None]);yc=y-y.mean(1,keepdims=True);diag={}
    for mode in modes:
        f=np.load(w/'runs'/mode/'forecast.npy',mmap_mode='r')[253:3779,:N];fc=f-f.mean(1,keepdims=True)
        ic=np.sum(fc*yc,1)/np.maximum(np.sqrt(np.sum(fc*fc,1)*np.sum(yc*yc,1)),1e-30)
        diag[mode]=dict(mean_IC=float(ic.mean()),MSE=float(np.mean((f-y)**2)),IC_information_ratio=float(np.sqrt(252)*ic.mean()/ic.std()) if ic.std()>0 else None)
    result=dict(summaries=summaries,gates=gates,bootstrap=boot,predictive_diagnostics=diag,all_history_exposed=True,independent_agents_used=0,primaries=5,controls=5,simultaneous_market_process_limit=2,archived_GC=benchmark)
    H.write_json(w/'ASSESSMENT.json',result)
    print(json.dumps({'scores':{m:summaries[m]['net_sharpe'] for m in modes},'gates':gates,'diagnostics':diag},indent=2),flush=True)
if __name__=='__main__':main()
