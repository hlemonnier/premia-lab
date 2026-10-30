"""Frozen N0 review E2E contracts, written before the diagnostic implementation."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
from research.parallel10 import harness as H
from research.parallel10.network import NetworkPolicy
from gls_alpha import CandidatePolicy as G
from research.n0_review.diagnostics import ReviewPolicy


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--market',action='store_true');a=ap.parse_args();score=H.load_score(a.source);checks=[]
    def close(name,x,y,tol=1e-10):
        error=float(np.max(np.abs(x-y),initial=0.));checks.append(dict(name=name,error=error,tolerance=tol,passed=error<=tol))
    def check(name,value):checks.append(dict(name=name,passed=bool(value)))
    def run(p,R,X,c):
        f,w,rows,sec,econ=H.exercise(p,R,X,c,score)
        close('cashflows',rows[:,:4],econ)
        check('certified',all(v['status']=='ok' for v in p.certificates))
        check('finite bounded',np.isfinite(f).all() and np.isfinite(w).all() and np.abs(w).sum(1).max()<=5*(1+1e-12))
        return f.copy(),w,rows
    if a.market:
        R,X,c=H.load_data(a.source,a.work)
        reference=np.load(a.work/'runs/N0/forecast.npy',mmap_mode='r')
        p=ReviewPolicy();f,w,rows=run(p,R[:1009],X[:1009],c)
        close('market prefix original N0',f,reference[:1009])
        for mode in ('none','causal'):
            p=ReviewPolicy(removal=mode);full=run(p,R[:1100],X[:1100],c)
            rr=np.array(R[:1100]);xx=np.array(X[:1100]);rng=np.random.default_rng(20261030)
            rr[1008:]=rng.normal(0,.02,rr[1008:].shape);xx[1008:]=rng.normal(size=xx[1008:].shape)
            alt=run(p,rr,xx,c)
            close(mode+' market changed-future forecast',full[0][:1009],alt[0][:1009])
            close(mode+' market changed-future positions',full[1][:1008-252],alt[1][:1008-252])
            check(mode+' mutation has effect',np.max(np.abs(full[0][1009:]-alt[0][1009:]))>1e-12)
            prefix=run(p,R[:1009],X[:1009],c)
            close(mode+' market prefix forecast',full[0][:1009],prefix[0])
            close(mode+' market prefix positions',full[1][:len(prefix[1])],prefix[1])
    else:
        rng=np.random.default_rng(20261030);T,N=800,48
        X=np.empty((T,N,13));X[0]=rng.normal(size=(N,13))
        for t in range(1,T):X[t]=.99*X[t-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
        R=.008*rng.normal(size=(T,N))+.003*rng.normal(size=(T,1))
        for t in range(1,T):R[t,:2]+=.70*R[t-1,:2]
        c=np.linspace(.0002,.0008,N)
        original=run(NetworkPolicy('N0'),R,X,c);p=ReviewPolicy();full=run(p,R,X,c)
        for i,label in enumerate(('forecast','positions','economic')):
            close('instrumentation '+label,original[i] if i!=2 else original[i][:,:4],full[i] if i!=2 else full[i][:,:4])
        check('own slope activation',np.count_nonzero(p.fit_own)>0)
        check('label chronology',all(r['last_label']==r['target_row']-1 for r in p.records))
        base=run(G(),R,X,c);all_removed=run(ReviewPolicy(removal='all'),R,X,c)
        for i,label in enumerate(('forecast','positions','economic')):
            close('remove all -> G '+label,base[i] if i!=2 else base[i][:,:4],all_removed[i] if i!=2 else all_removed[i][:,:4])
        for mode in ('none','fixed','causal'):
            p=ReviewPolicy(removal=mode,excluded=(0,))
            full=run(p,R,X,c)
            close(mode+' unchanged risk payload',full[0][:,N:],base[0][:,N:])
            if mode=='fixed':check('fixed raw source zero',np.max(np.abs(p.applied_raw[:,0]))==0)
            if mode=='causal':check('causal exclusion trace',all(r['removed'] or r['own']==0 for r in p.records))
            for cut in (504,630):
                prefix=run(p,R[:cut+1],X[:cut+1],c)
                close(mode+f' prefix {cut} f',full[0][:cut+1],prefix[0]);close(mode+f' prefix {cut} w',full[1][:len(prefix[1])],prefix[1])
                for kind in ('returns','characteristics'):
                    rr=R.copy();xx=X.copy()
                    if kind=='returns':rr[cut:]=rng.normal(0,.012,rr[cut:].shape)
                    else:xx[cut:]=rng.normal(size=xx[cut:].shape)
                    altered=run(p,rr,xx,c)
                    close(mode+f' {kind} cut {cut} f',full[0][:cut+1],altered[0][:cut+1])
                    close(mode+f' {kind} cut {cut} w',full[1][:cut-252],altered[1][:cut-252])
            repeated=run(p,R,X,c);close(mode+' reset f',full[0],repeated[0]);close(mode+' reset w',full[1],repeated[1])
            laid=run(p,np.asfortranarray(R),np.asfortranarray(X),c);close(mode+' layout f',full[0],laid[0]);close(mode+' layout w',full[1],laid[1])
        p=ReviewPolicy();full=run(p,R,X,c);order=rng.permutation(N);back=np.argsort(order)
        perm=run(ReviewPolicy(),R[:,order],X[:,order],c[order])
        close('permutation forecast',full[0][:,:N],perm[0][:,:N][:,back]);close('permutation risk',full[0][:,N:],perm[0][:,N:])
        close('permutation weights',full[1],perm[1][:,back],1e-8)
        close('permutation returns fees',full[2][:,:2],perm[2][:,:2]);close('permutation gross',full[2][:,2],perm[2][:,2],N*1e-8)
        zeros=run(ReviewPolicy(),np.zeros_like(R[:631]),np.zeros_like(X[:631]),c);check('zero finite',np.isfinite(zeros[0]).all())
    result=dict(passed=all(x['passed'] for x in checks),checks=checks,scope='market' if a.market else 'constructed')
    H.write_json(a.work/'checks'/('market.json' if a.market else 'constructed.json'),result)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise RuntimeError('E2E check failed; see receipts')
if __name__=='__main__':main()
