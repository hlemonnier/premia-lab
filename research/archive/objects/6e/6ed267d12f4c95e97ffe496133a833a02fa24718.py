"""Preregistered E2E contracts, written before peer candidate implementation.

These execute full forecast/scorer/rebalance paths; no isolated post-hoc unit tests.
"""
from __future__ import annotations
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[name]='1'
import sys,json,argparse
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.common import harness as H
from gls_alpha import CandidatePolicy as Reference
from research.relations.runner import policy


def fixture():
    rng=np.random.default_rng(20261105);T,N=420,48
    X=np.empty((T,N,13));X[0]=rng.normal(size=(N,13))
    for s in range(1,T):X[s]=.99*X[s-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
    R=.007*rng.normal(size=(T,N))+.003*rng.normal(size=(T,1))
    return R,X,np.linspace(.0002,.0008,N)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--model',required=True);ap.add_argument('--mode',choices=['synthetic','market'],required=True);a=ap.parse_args()
    checks=[];score=H.load_score(a.source);out=a.work/'checks';out.mkdir(parents=True,exist_ok=True)
    def check(name,okay,**detail):checks.append(dict(name=name,passed=bool(okay),**detail))
    def equal(name,x,y,tol=1e-10):
        err=float(np.max(np.abs(x-y),initial=0.));check(name,err<=tol,error=err,tolerance=tol)
    def run(name,R,X,c):
        p=policy(a.model);f,w,rows,sec,econ=H.exercise(p,R,X,c,score)
        equal(name+'_cashflows',rows[:,:4],econ)
        check(name+'_finite',all(np.isfinite(v).all() for v in (f,w,rows)))
        check(name+'_gross',float(np.max(np.abs(w).sum(1),initial=0))<=5*(1+1e-12))
        check(name+'_certificates',all(v['status']=='ok' for v in p.certificates))
        meta=getattr(p,'relation_diagnostics',{})
        check(name+'_graph_self',meta.get('max_self_weight',0.)==0.)
        check(name+'_graph_normalization',meta.get('max_row_error',0.)<1e-12)
        if a.model in ('P','O','PS'):
            check(name+'_alpha_cap',meta.get('max_alpha_fraction',0.)<=.2+1e-12)
            check(name+'_mature_labels',all(r['last_label']<r['target_row'] and r['last_feature']==r['last_label']-1 for r in p.relation_records))
        else:
            check(name+'_variance_bounds',meta.get('min_ratio',1.)>=.75-1e-12 and meta.get('max_ratio',1.)<=1.5+1e-12)
        return f,w,rows,p
    if a.mode=='synthetic':
        R,X,c=fixture();full=run('full',R,X,c)
        pre=run('prefix',R[:379],X[:379],c)
        equal('prefix_forecasts',pre[0],full[0][:379]);equal('prefix_positions',pre[1],full[1][:len(pre[1])])
        for j,(kind,cut) in enumerate([('returns',1),('characteristics',252),('joint',378)]):
            rr,xx=R.copy(),X.copy();rng=np.random.default_rng(20261105+j)
            if kind!='characteristics':rr[cut:]=rng.normal(0,.01,size=rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            ch=run(kind,rr,xx,c)
            equal(kind+'_past_forecasts',ch[0][:cut+1],full[0][:cut+1])
            if cut>252:equal(kind+'_past_positions',ch[1][:cut-252],full[1][:cut-252])
            check(kind+'_has_power',float(np.max(np.abs(ch[0][cut+1:]-full[0][cut+1:])))>1e-12 or float(np.max(np.abs(ch[1]-full[1])))>1e-12)
        perm=np.random.default_rng(20261105).permutation(len(c));inv=np.argsort(perm)
        pp=run('permutation',R[:,perm],X[:,perm],c[perm]);n=len(c)
        equal('permutation_alpha',pp[0][:,:n][:,inv],full[0][:,:n]);equal('permutation_risk',pp[0][:,n:],full[0][:,n:])
        equal('permutation_weights',pp[1][:,inv],full[1],1e-8)
        equal('permutation_cash',pp[2][:,:2],full[2][:,:2]);equal('permutation_gross',pp[2][:,2],full[2][:,2],n*1e-8)
        ff=run('fortran',np.asfortranarray(R),np.asfortranarray(X),c)
        equal('layout_forecasts',ff[0],full[0]);equal('layout_positions',ff[1],full[1])
        same=full[3];r1=H.exercise(same,R[:379],X[:379],c,score);r2=H.exercise(same,R,X,c,score)
        equal('reused_session_forecasts',r2[0],full[0]);equal('reused_session_positions',r2[1],full[1])
        run('zero',np.zeros_like(R),np.zeros_like(X),c)
        run('tied_characteristics',R,np.zeros_like(X),c)
        run('one_stock',R[:,:1],X[:,:1],c[:1])
        baseline=Reference().forecast(R,X)
        equal('unchanged_risk_payload',full[0][:,n:],baseline[:,n:])
        if a.model in ('V','VG'):equal('unchanged_forecast',full[0],baseline)
    else:
        R,X,c=H.load_data(a.source,a.work)
        fullf=np.load(a.work/'runs'/a.model/'forecast.npy',mmap_mode='r');fullw=np.load(a.work/'runs'/a.model/'targets.npy',mmap_mode='r')
        for length in (630,2016):
            p=run('prefix'+str(length),R[:length],X[:length],c)
            equal('prefix_forecasts'+str(length),p[0],fullf[:length]);equal('prefix_positions'+str(length),p[1],fullw[:len(p[1])])
        for j,(kind,cut,length) in enumerate([('returns',630,756),('characteristics',630,756),('joint',2016,2142)]):
            rr,xx=np.array(R[:length]),np.array(X[:length]);rng=np.random.default_rng(20261108+j)
            if kind!='characteristics':rr[cut:]=rng.normal(0,.01,size=rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            ch=run(kind,rr,xx,c)
            equal(kind+'_past_forecasts',ch[0][:cut+1],fullf[:cut+1]);equal(kind+'_past_positions',ch[1][:cut-252],fullw[:cut-252])
        g=np.load(a.work/'runs/G/forecast.npy',mmap_mode='r');n=R.shape[1]
        equal('unchanged_risk_payload',fullf[:,n:],g[:,n:])
        if a.model in ('V','VG'):equal('unchanged_full_forecast',fullf,g)
    receipt=dict(model=a.model,mode=a.mode,checks=checks,passed=all(c['passed'] for c in checks))
    H.write_json(out/f'{a.model}_{a.mode}.json',receipt)
    print(json.dumps(receipt,indent=2),flush=True)
    assert receipt['passed'],'E2E failure; see retained receipt'
if __name__=='__main__':main()
