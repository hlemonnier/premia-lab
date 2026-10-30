"""Black-box E2E contracts written before the five paired model implementations.

No numerical unit test is added after the implementation it covers.  Source and
scorer identities, cashflows, past invariance and a planted directed-link fixture
are checked through complete forecasting/trading workflows.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.parallel10 import harness as H
from research.parallel10.models import make_policy
from gls_alpha import CandidatePolicy as Reference


def fixture(days=630):
    rng=np.random.default_rng(20261106);T,N=days,32
    X=np.empty((T,N,13));X[0]=rng.normal(size=(N,13))
    for t in range(1,T):X[t]=.99*X[t-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
    R=.008*rng.normal(size=(T,N))+.002*rng.normal(size=(T,1))
    # A directed lead-lag dependency is genuinely present; no future lookup.
    for t in range(1,T):R[t,1]+=.7*R[t-1,0]
    return R,X,np.linspace(.0002,.0008,N)


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--work',required=True,type=Path)
    p.add_argument('--model',required=True);p.add_argument('--mode',choices=['synthetic','market'],default='synthetic');a=p.parse_args()
    checks=[];score=H.load_score(a.source)
    def check(name,cond,**detail):checks.append(dict(name=name,passed=bool(cond),**detail))
    def equal(name,x,y,tol=1e-10):
        error=float(np.max(np.abs(x-y),initial=0));check(name,error<=tol,error=error,tolerance=tol)
    def run(name,R,X,c,pol=None):
        pol=make_policy(a.model) if pol is None else pol
        f,w,rows,sec,econ=H.exercise(pol,R,X,c,score)
        equal(name+'_cashflows',rows[:,:4],econ)
        check(name+'_finite',all(np.isfinite(v).all() for v in (f,w,rows)))
        check(name+'_bounds',float(np.abs(w).sum(1).max(initial=0))<=5*(1+1e-12))
        check(name+'_certificates',all(v['status']=='ok' for v in pol.certificates))
        check(name+'_maturity',all(v.get('last_label',0)<v['target_row'] for v in pol.records))
        return f,w,rows,pol,sec
    if a.mode=='synthetic':
        R,X,c=fixture(900 if a.model in ('M','M0') else 630);n=len(c);full=run('full',R,X,c)
        pre=run('prefix505',R[:505],X[:505],c)
        equal('prefix_forecast',full[0][:505],pre[0]);equal('prefix_positions',full[1][:len(pre[1])],pre[1])
        for j,kind in enumerate(('returns','characteristics','joint')):
            cut=504;rr,xx=R.copy(),X.copy();rng=np.random.default_rng(20261107+j)
            if kind!='characteristics':rr[cut:]=rng.normal(0,.01,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            ch=run(kind,rr,xx,c)
            equal(kind+'_past_forecasts',ch[0][:cut+1],full[0][:cut+1]);equal(kind+'_past_positions',ch[1][:cut-252],full[1][:cut-252])
            check(kind+'_perturbation_power',np.max(np.abs(ch[0][cut+1:]-full[0][cut+1:]))>1e-12)
        rr=R.copy();rr[-1]=.1;ch=run('last_source',rr,X,c);equal('last_row_unused',ch[0],full[0]);equal('last_row_positions',ch[1],full[1])
        ff=run('layout',np.asfortranarray(R),np.asfortranarray(X),c);equal('layout_forecast',ff[0],full[0]);equal('layout_weights',ff[1],full[1])
        run('reused_short',R[:505],X[:505],c,full[3]);repeat=run('reused',R,X,c,full[3]);equal('reset_forecast',repeat[0],full[0]);equal('reset_weights',repeat[1],full[1])
        perm=np.random.default_rng(20261106).permutation(n);inv=np.argsort(perm);pp=run('perm',R[:,perm],X[:,perm],c[perm])
        equal('perm_alpha',pp[0][:,:n][:,inv],full[0][:,:n]);equal('perm_risk',pp[0][:,n:n+27],full[0][:,n:n+27])
        if a.model in ('C','C0'):
            x=full[0][:,n+27:].reshape(len(R),n,5);y=pp[0][:,n+27:].reshape(len(R),n,5)[:,inv]
            equal('perm_residual_covariance',[redacted-email](0,2,1),[redacted-email](0,2,1),1e-8)
        equal('perm_weights',pp[1][:,inv],full[1],1e-8);equal('perm_cash',pp[2][:,:2],full[2][:,:2]);equal('perm_gross',pp[2][:,2],full[2][:,2],n*1e-8)
        zero=run('zero',np.zeros_like(R),np.zeros_like(X),c)
        run('one_stock',R[:,:1],X[:,:1],c[:1])
        baseline=Reference().forecast(R,X);equal('unchanged_F_risk_payload',full[0][:,n:n+27],baseline[:,n:])
        if a.model in ('C','C0'):equal('unchanged_alpha',full[0][:,:n],baseline[:,:n])
        if a.model in ('N','N0','V','V0'):
            ratio=np.sqrt(np.mean((full[0][:,:n]-baseline[:,:n])**2,axis=1))/np.maximum(np.sqrt(np.mean(baseline[:,:n]**2,axis=1)),1e-30)
            check('increment_cap',float(ratio.max())<=.2+1e-10,maximum=float(ratio.max()))
        if a.model in ('M','M0'):check('mix_bounds',all(.25<=v.get('weight',.5)<=.75 for v in full[3].records))
        if a.model=='N':
            # A standalone planted residual network fixture also drives the full
            # forecast interface; raw channels with zero characteristic factors
            # avoid regressors absorbing the injected effect.
            rng=np.random.default_rng(20261106);r=.01*rng.normal(size=(1100,64));xx=np.zeros((1100,64,13))
            for t in range(1,len(r)):r[t,1]+=.9*r[t-1,0]
            linked=make_policy('N');linked.forecast(r,xx)
            check('planted_directed_link_is_detected',any(v.get('edges',0)>0 for v in linked.records))
    else:
        R,X,c=H.load_data(a.source,a.work);n=len(c)
        fullf=np.load(a.work/'runs'/a.model/'forecast.npy',mmap_mode='r');fullw=np.load(a.work/'runs'/a.model/'targets.npy',mmap_mode='r')
        for length in (630,2016):
            pre=run('prefix'+str(length),R[:length],X[:length],c)
            equal('actual_prefix_f'+str(length),pre[0],fullf[:length]);equal('actual_prefix_w'+str(length),pre[1],fullw[:len(pre[1])])
        for j,kind in enumerate(('returns','characteristics')):
            cut,length=630,756;rr,xx=np.array(R[:length]),np.array(X[:length]);rng=np.random.default_rng(20261110+j)
            if kind=='returns':rr[cut:]=rng.normal(0,.01,rr[cut:].shape)
            else:xx[cut:]=rng.normal(size=xx[cut:].shape)
            ch=run(kind,rr,xx,c);equal('actual_'+kind+'_f',ch[0][:cut+1],fullf[:cut+1]);equal('actual_'+kind+'_w',ch[1][:cut-252],fullw[:cut-252])
        import time
        start=time.perf_counter();fresh=make_policy(a.model).forecast(R,X);seconds=time.perf_counter()-start
        equal('full_uncached_forecast_equals_shared_path',fresh,fullf)
        check('full_forecast_runtime',seconds/len(R)*25200<3600,seconds=seconds,projected_seconds_century=seconds/len(R)*25200)
        g=np.load(a.work/'runs/G/forecast.npy',mmap_mode='r');equal('same_risk_channels',fullf[:,n:n+27],g[:,n:])
        if a.model in ('C','C0'):equal('same_alpha',fullf[:,:n],g[:,:n])
    receipt=dict(model=a.model,mode=a.mode,checks=checks,passed=all(v['passed'] for v in checks))
    H.write_json(a.work/'checks'/f'{a.model}_{a.mode}.json',receipt);print(json.dumps(receipt,indent=2),flush=True)
    assert receipt['passed'],'E2E failed; retained receipt must not be relabeled'
if __name__=='__main__':main()
