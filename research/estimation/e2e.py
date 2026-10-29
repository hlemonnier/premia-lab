"""Complete R/K workflows, written before either candidate implementation.
No isolated post-implementation tests. All nonpassing assertions are retained.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.estimation.harness import make_policy
from research.common import harness as H


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--candidate',choices=['R','K'],required=True);ap.add_argument('--mode',choices=['synthetic','market'],required=True);a=ap.parse_args()
    score=H.load_score(a.source);checks=[]
    def ck(name,passed,**kw):checks.append(dict(check=name,passed=bool(passed),**kw))
    def same(name,x,y,tol=1e-10):
        err=float(np.max(np.abs(x-y),initial=0.));ck(name,err<=tol,max_abs_error=err,tolerance=tol)
    def go(R,X,c,p=None):
        p=p or make_policy(a.candidate);f,w,rows,sec,econ=H.exercise(p,R,X,c,score)
        same('separate scorer cashflows',rows[:,:4],econ)
        ck('finite and gross bounds',np.isfinite(f).all() and np.isfinite(w).all() and np.max(np.abs(w).sum(1),initial=0.)<=5*(1+1e-12))
        rec=getattr(p,'learner_records',[])
        ck('mature labels and lagged covariance',all(z['last_label']<z['target_row'] and z['covariance_last_row']<z['last_label'] for z in rec))
        ck('certified allocations',all(x['status']=='ok' for x in p.certificates))
        if a.candidate=='R':ck('bounded reliability',all(.05<=z['reliability']<=1. for z in rec))
        if a.candidate=='K':ck('finite positive posterior',all(z['posterior_min_eigenvalue']>0 and np.isfinite(z['coefficient_norm']) for z in rec))
        return p,(f,w,rows)
    if a.mode=='synthetic':
        rng=np.random.default_rng(20261106);T,N=440,48
        X=np.zeros((T,N,13));X[0]=rng.normal(size=(N,13))
        for s in range(1,T):X[s]=.99*X[s-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
        R=.008*rng.normal(size=(T,N))+.003*rng.normal(size=(T,1));c=np.linspace(.0002,.0008,N)
        pol,(f,w,rows)=go(R,X,c)
        base=make_policy('GC').forecast(R,X);same('frozen GC risk channels',f[:,N:],base[:,N:])
        for length in (0,1,64,65,126,253):
            ff=make_policy(a.candidate).forecast(R[:length],X[:length]);same(f'short prefix {length}',ff,f[:length])
            ck(f'short finite {length}',np.isfinite(ff).all())
        _,o=go(R[:379],X[:379],c);same('prefix forecast',o[0],f[:379]);same('prefix positions',o[1],w[:len(o[1])])
        for cut,kind in [(64,'joint'),(126,'returns'),(252,'returns'),(378,'characteristics'),(379,'joint')]:
            rr=R.copy();xx=X.copy()
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            if cut<252:
                ff=make_policy(a.candidate).forecast(rr,xx)
            else:
                _,o=go(rr,xx,c);ff=o[0];same(f'{kind} positions before {cut}',o[1][:cut-252],w[:cut-252])
            same(f'{kind} forecast through {cut}',ff[:cut+1],f[:cut+1]);ck('mutation has power',np.max(np.abs(ff[cut+1:]-f[cut+1:]))>1e-12)
        _,o=go(np.asfortranarray(R),np.asfortranarray(X),c,pol);same('reuse/layout forecast',o[0],f);same('reuse/layout positions',o[1],w)
        _,o=go(np.zeros_like(R),np.zeros_like(X),c)
        # Permutation tolerances are fixed before scores and reflect aggregate error propagation.
        perm=rng.permutation(N);inv=np.argsort(perm)
        _,o=go(R[:,perm],X[:,perm],c[perm]);ff=np.hstack([o[0][:,:N][:,inv],o[0][:,N:]])
        same('permutation forecasts',ff,f);same('permutation positions',o[1][:,inv],w,1e-8)
        same('permutation returns and fees',o[2][:,:2],rows[:,:2]);same('permutation gross aggregate bound',o[2][:,2],rows[:,2],N*1e-8)
        if a.candidate=='R':
            _,o=go(R,X,c,make_policy('R0'));baseline=H.exercise(make_policy('GC'),R,X,c,score)
            same('unit-weight GLS forecast identity',o[0],baseline[0]);same('unit-weight GLS positions',o[1],baseline[1],1e-8)
            same('unit-weight GLS economic identity',o[2][:,:4],baseline[2][:,:4])
    else:
        R,X,c=H.load_data(a.source,a.work);N=R.shape[1];rng=np.random.default_rng(20261107)
        root=a.work/'runs'/a.candidate;f=np.load(root/'forecast.npy',mmap_mode='r');w=np.load(root/'targets.npy',mmap_mode='r')
        bf=np.load(a.work/'runs/GC/forecast.npy',mmap_mode='r');same('actual unchanged GC risk channels',f[:,N:],bf[:,N:])
        for length in (630,2016):
            pol,o=go(R[:length],X[:length],c);same('market prefix forecasts',o[0],f[:length]);same('market prefix targets',o[1],w[:len(o[1])])
        for cut,length,kind in [(630,900,'returns'),(630,900,'characteristics'),(2016,2268,'joint')]:
            rr=np.array(R[:length]);xx=np.array(X[:length])
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            pol,o=go(rr,xx,c);same('market mutated forecast prefix',o[0][:cut+1],f[:cut+1]);same('market mutated targets prefix',o[1][:cut-252],w[:cut-252])
            ck('market mutation power',np.max(np.abs(o[0][cut+1:]-f[cut+1:length]))>1e-12)
        pol,o=go(R[:630],X[:630],c,pol);same('market reused forecast',o[0],f[:630]);same('market reused targets',o[1],w[:len(o[1])])
    result=dict(candidate=a.candidate,mode=a.mode,checks=checks,passed=all(z['passed'] for z in checks))
    H.write_json(a.work/'checks'/f'{a.candidate}_{a.mode}.json',result);print(json.dumps(result,indent=2),flush=True)
    assert result['passed'],'E2E failure; original receipt retained'
if __name__=='__main__':main()
