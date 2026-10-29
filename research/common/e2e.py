"""E2E contracts written before the GLS/CORR candidate implementations.

Checks complete causal forecasts, actual original-scorer replays and independently
reconstructed cashflows. No isolated unit tests or economic acceptance assertions
are created after inspecting new results.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import harness as H
import numpy as np


def compare(name,a,b,checks,tol=1e-10):
    err=float(np.max(np.abs(np.asarray(a)-np.asarray(b)),initial=0))
    checks.append(dict(check=name,error=err,tolerance=tol,passed=bool(err<=tol)))


def run_case(p,R,X,cost,score,checks,label):
    f,w,rows,sec,e=H.exercise(p,R,X,cost,score)
    compare(label+' independent cashflows',rows[:,:4],e,checks)
    checks.append(dict(check=label+' position and certificate bounds',passed=bool(
        np.max(np.abs(w).sum(axis=1))<=5+1e-10 and
        np.max(np.abs(w))<=.10+.05/R.shape[1]+1e-10 and
        all(c['status'] in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal')
            for c in p.certificates))))
    return f,w,rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--candidate',required=True)
    ap.add_argument('--mode',choices=['synthetic','market'],required=True);a=ap.parse_args()
    score=H.load_score(a.source);checks=[];rng=np.random.default_rng(20261102)
    p=H.make_policy(a.candidate)
    if a.mode=='synthetic':
        T,N=420,48
        X=np.cumsum(rng.normal(0,.025,(T,N,13)),axis=0)+rng.normal(size=(1,N,13))
        R=.00005*X[:,:,0]+rng.normal(0,.004,(T,N));cost=np.linspace(.0002,.0008,N)
        f,w,r=run_case(p,R,X,cost,score,checks,'base')
        for length in [379,400]:
            fp,wp,rp=run_case(p,R[:length],X[:length],cost,score,checks,f'prefix{length}')
            compare(f'prefix{length} forecast',fp,f[:length],checks)
            compare(f'prefix{length} positions',wp,w[:len(wp)],checks)
        changed=False
        for cut,kind in [(126,'returns'),(252,'characteristics'),(378,'joint')]:
            rr=R.copy();xx=X.copy()
            if kind!='characteristics':rr[cut:]=rng.normal(0,.006,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            fm,wm,rm=run_case(p,rr,xx,cost,score,checks,f'mutation{cut}_{kind}')
            compare(f'mutation{cut}_{kind} prior forecast',fm[:cut+1],f[:cut+1],checks)
            n=max(0,cut-252)
            compare(f'mutation{cut}_{kind} prior positions',wm[:n],w[:n],checks)
            changed |= bool(np.max(np.abs(fm[cut+1:]-f[cut+1:]),initial=0)>1e-10)
        checks.append(dict(check='future mutation changes later forecasts',passed=changed))
        fr,wr,rr=run_case(p,R,X,cost,score,checks,'reset')
        compare('reset forecasts',fr,f,checks);compare('reset positions',wr,w,checks)
        ff,wf,rf=run_case(p,np.asfortranarray(R),np.asfortranarray(X),cost,score,checks,'Fortran')
        compare('layout forecasts',ff,f,checks);compare('layout positions',wf,w,checks)
        perm=rng.permutation(N);inv=np.argsort(perm)
        fp,wp,rp=run_case(p,R[:,perm],X[:,perm],cost[perm],score,checks,'permutation')
        compare('permuted alpha',fp[:,:N][:,inv],f[:,:N],checks)
        compare('permuted risk payload',fp[:,N:],f[:,N:],checks)
        compare('permuted positions',wp[:,inv],w,checks,1e-8)
        compare('permuted cashflows',rp[:,[0,1,3]],r[:,[0,1,3]],checks)
        fz,wz,rz=run_case(p,np.zeros_like(R),np.zeros_like(X),cost,score,checks,'zeros')
        compare('zero gross return',rz[:,0],np.zeros(len(rz)),checks)
    else:
        R,X,cost=H.load_data(a.source,a.work)
        root=a.work/'runs'/a.candidate
        f=np.load(root/'forecast.npy',mmap_mode='r');w=np.load(root/'targets.npy',mmap_mode='r')
        for length in [379,630,2016]:
            fp,wp,rows=run_case(p,R[:length],X[:length],cost,score,checks,f'prefix{length}')
            compare(f'prefix{length} forecasts',fp,f[:length],checks)
            compare(f'prefix{length} positions',wp,w[:len(wp)],checks)
        for cut,length,kind in [(630,760,'returns'),(630,760,'characteristics'),(2016,2144,'joint')]:
            rr=np.array(R[:length],copy=True);xx=np.array(X[:length],copy=True)
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            fm,wm,rows=run_case(p,rr,xx,cost,score,checks,f'mutation{cut}_{kind}')
            compare(f'mutation{cut}_{kind} prior forecasts',fm[:cut+1],f[:cut+1],checks)
            compare(f'mutation{cut}_{kind} prior positions',wm[:cut-252],w[:cut-252],checks)
        fp,wp,rows=run_case(p,R[:379],X[:379],cost,score,checks,'reset')
        compare('reset forecasts',fp,f[:379],checks);compare('reset positions',wp,w[:len(wp)],checks)
    # Check trace contracts from the latest complete replay, not invented fitted stats.
    for record in getattr(p,'fit_records',[]):
        assert record['last_label']<record['target_row']
    for record in getattr(p,'learner_records',[]):
        assert record['last_label']<record['target_row']
        assert record['covariance_last_row']<record['last_label']
    result=dict(candidate=a.candidate,mode=a.mode,checks=checks,passed=all(c['passed'] for c in checks))
    H.write_json(a.work/'checks'/f'{a.candidate}_{a.mode}.json',result)
    print(json.dumps(result,indent=2),flush=True)
    assert result['passed'],'E2E failure retained; no scoring until corrected'

if __name__=='__main__':main()
