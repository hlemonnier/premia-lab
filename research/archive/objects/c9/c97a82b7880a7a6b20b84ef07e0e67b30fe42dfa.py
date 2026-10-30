"""End-to-end contracts written before Wave5 implementation.

No isolated unit tests. Run whole forecast -> original scorer -> target/cashflow
workflow on constructed inputs, then on full supplied-data prefixes/mutations.
"""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='1'
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'handoff_v3'),str(ROOT/'research/wave4')]
import run_wave4 as W


def check(name,a,b,checks,tol=1e-10):
    error=float(np.max(np.abs(np.asarray(a)-np.asarray(b)),initial=0))
    checks.append({'check':name,'error':error,'tolerance':tol,'passed':bool(error<=tol)})


def exercise(policy,R,X,cost,score):
    rows,seconds=score.run(policy,R,X,cost)
    f=policy.forecast_output.copy();targets=np.array(policy.targets)
    assert np.isfinite(f).all() and np.isfinite(rows).all() and np.isfinite(targets).all()
    # Independent cashflow reconstruction, including original scorer's fee timing.
    econ=[]
    for i,today in enumerate(range(253,len(R)-1),start=1):
        previous=targets[i-1]
        gross=float(previous@R[today])
        held=previous*(1+R[today])/(1+gross)
        cost_today=float([redacted-email](targets[i]-held))
        econ.append([gross,cost_today,float(np.abs(targets[i]).sum()),float(R[today].mean())])
    return f,targets,rows,seconds,np.array(econ)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--mode',choices=['synthetic','market'],required=True)
    ap.add_argument('--candidate',default='H');a=ap.parse_args()
    from wave5_models import ResearchPolicy
    score=W.load_score(a.source);checks=[]
    out=a.work/'checks';out.mkdir(exist_ok=True,parents=True)
    if a.mode=='synthetic':
        rng=np.random.default_rng(20261030);T,N=420,48
        X=np.cumsum(rng.normal(size=(T,N,13))*.025,axis=0)+rng.normal(size=(1,N,13))
        R=.00005*X[:,:,0]+rng.normal(0,.004,size=(T,N));cost=np.linspace(.0002,.0008,N)
        for mode in ('H','P','E'):
            p=ResearchPolicy(mode);f,w,rows,_,econ=exercise(p,R,X,cost,score)
            check(mode+' cashflow reconstruction',rows[:,:4],econ,checks)
            for length in (379,400):
                fp,wp,rp,_,ep=exercise(p,R[:length],X[:length],cost,score)
                check(mode+f' prefix {length} forecast',fp,f[:length],checks)
                check(mode+f' prefix {length} targets',wp,w[:len(wp)],checks)
            for cut,kind in ((127,'returns'),(252,'characteristics'),(378,'joint')):
                rr=R.copy();xx=X.copy()
                if kind!='characteristics':rr[cut:]=rng.normal(0,.006,size=rr[cut:].shape)
                if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
                fm,wm,rm,_,em=exercise(p,rr,xx,cost,score)
                check(mode+f' future mutation {cut} {kind} forecast',fm[:cut+1],f[:cut+1],checks)
                count=max(0,cut-252)
                check(mode+f' future mutation {cut} {kind} targets',wm[:count],w[:count],checks)
            fr,wr,_,_,_=exercise(p,R,X,cost,score)
            check(mode+' reset forecast',fr,f,checks);check(mode+' reset targets',wr,w,checks)
            zf,zw,zr,_,ze=exercise(p,np.zeros_like(R),np.zeros_like(X),cost,score)
            check(mode+' zero-data returns',zr[:,0],np.zeros(len(zr)),checks)
            checks.append({'check':mode+' bounded positions','passed':bool(np.max(np.sum(abs(w),axis=1))<=5+1e-10)})
    else:
        R,X,cost=W.load_inputs(score,a.source,a.work)
        mode=a.candidate;p=ResearchPolicy(mode)
        f=np.load(a.work/'results'/f'{mode}_forecast.npy',mmap_mode='r')
        w=np.load(a.work/'results'/f'{mode}_targets.npy',mmap_mode='r')
        for length in (379,630,2016):
            fp,wp,rows,_,econ=exercise(p,R[:length],X[:length],cost,score)
            check(mode+f' market prefix {length} forecast',fp,f[:length],checks)
            check(mode+f' market prefix {length} targets',wp,w[:len(wp)],checks)
            check(mode+f' market cashflows {length}',rows[:,:4],econ,checks)
        rng=np.random.default_rng(20261030)
        for cut,length,kind in ((630,760,'returns'),(630,760,'characteristics'),(2016,2144,'joint')):
            rr=np.array(R[:length],copy=True);xx=np.array(X[:length],copy=True)
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,size=rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            fm,wm,_,_,_=exercise(p,rr,xx,cost,score)
            check(mode+f' market mutation {cut} {kind} forecast',fm[:cut+1],f[:cut+1],checks)
            check(mode+f' market mutation {cut} {kind} positions',wm[:cut-252],w[:cut-252],checks)
        fr,wr,_,_,_=exercise(p,R[:379],X[:379],cost,score)
        check(mode+' market reset forecast',fr,f[:379],checks)
        check(mode+' market reset positions',wr,w[:len(wr)],checks)
    result={'mode':a.mode,'candidate':a.candidate,'checks':checks,'passed':all(c['passed'] for c in checks)}
    (out/f'{a.mode}_{a.candidate}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    assert result['passed'],'E2E failures recorded'

if __name__=='__main__':main()
