"""E2E contracts committed before standalone F package implementation."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse, json, sys
from pathlib import Path
import numpy as np
import runner as V

def check(checks,name,a,b,tol=1e-10):
    err=float(np.max(abs(np.asarray(a)-np.asarray(b)),initial=0))
    checks.append({'name':name,'max_error':err,'tolerance':tol,'passed':bool(np.isfinite(err) and err<=tol)})

def exercise(p,R,X,c,score):
    q=V.Recorded(p);rows,t=score.run(q,R,X,c)
    return q.f,np.asarray(q.weights),rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--mode',choices=['synthetic','market','equivalence'],required=True);a=ap.parse_args()
    p=V.load_policy('release');score=V.module(a.source/'score.py','release_score');checks=[]
    if a.mode=='equivalence':
        for suf in ('forecast','weights','rows'):
            x=np.load(a.work/'results'/f'F_{suf}.npy');y=np.load(a.work/'results'/f'release_{suf}.npy')
            if suf=='rows': x=x[:,:4];y=y[:,:4]
            check(checks,'research vs standalone '+suf,x,y)
        for name in ('F','B0','T'):
            old=a.work/'prior'/f'{name}_rows.npy'
            check(checks,name+' archived economics',np.load(a.work/'results'/f'{name}_rows.npy')[:,:4],np.load(old)[:,:4])
    elif a.mode=='synthetic':
        rng=np.random.default_rng(20261101);T,N=420,48
        X=rng.normal(size=(1,N,13))+np.cumsum(rng.normal(0,.025,(T,N,13)),axis=0)
        R=rng.normal(0,.004,(T,N));c=np.linspace(.0002,.0008,N)
        f,w,rows=exercise(p,R,X,c,score)
        for length in (0,1,2,20,126,253,379,400):
            ff=p.forecast(R[:length],X[:length]);check(checks,f'short prefix {length}',ff,f[:length])
        # Fresh histories with valid but extreme/degenerate inputs.
        for label,rr,xx in [('zero',np.zeros_like(R),np.zeros_like(X)),('constant',np.full_like(R,.0001),np.ones_like(X))]:
            ff,ww,rrs=exercise(p,rr,xx,c,score)
            checks.append({'name':label+' finite bounded workflow','passed':bool(np.isfinite(ff).all() and np.isfinite(ww).all() and np.isfinite(rrs).all() and np.max(np.abs(ww).sum(1))<=5+1e-10)})
        for cut,kind in ((0,'joint'),(1,'returns'),(126,'characteristics'),(252,'joint'),(378,'joint'),(379,'returns'),(419,'joint')):
            rr=R.copy();xx=X.copy()
            if kind!='characteristics':rr[cut:]=rng.normal(0,.006,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            ff,ww,rrs=exercise(p,rr,xx,c,score)
            check(checks,f'cut {cut} {kind} forecast',ff[:cut+1],f[:cut+1])
            check(checks,f'cut {cut} {kind} weights',ww[:max(0,cut-252)],w[:max(0,cut-252)])
        for layout in ('F','C'):
            ff,ww,rrs=exercise(p,np.array(R,order=layout),np.array(X,order=layout),c,score)
            check(checks,layout+' layout forecast',ff,f);check(checks,layout+' layout weights',ww,w)
        ff,ww,rrs=exercise(p,R,X,c,score);check(checks,'session reset forecast',ff,f);check(checks,'session reset weights',ww,w)
        # Costs and dimensions outside the input contract should fail, not produce orders.
        try:p.forecast(R,X[:,:,:12]);bad=False
        except (ValueError,IndexError):bad=True
        checks.append({'name':'reject wrong characteristic dimension','passed':bad})
        ff=p.forecast(R,X)
        try:p.rebalance(np.zeros(N),ff[253],R[:253],X[:253],-c);bad=False
        except ValueError:bad=True
        checks.append({'name':'reject negative costs','passed':bad})
    else:
        R,X,c=V.inputs(a.source,a.work)
        f=np.load(a.work/'results/release_forecast.npy',mmap_mode='r');w=np.load(a.work/'results/release_weights.npy',mmap_mode='r')
        for length in (379,630,2016,3779):
            ff,ww,rrs=exercise(p,R[:length],X[:length],c,score)
            check(checks,f'market prefix {length} forecast',ff,f[:length]);check(checks,f'market prefix {length} weights',ww,w[:len(ww)])
        rng=np.random.default_rng(20261101)
        for cut,length,kind in ((630,760,'returns'),(630,760,'characteristics'),(2016,2144,'joint'),(3779,3780,'joint')):
            rr=np.array(R[:length]);xx=np.array(X[:length])
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            ff,ww,rrs=exercise(p,rr,xx,c,score)
            check(checks,f'market cut {cut} {kind} forecast',ff[:cut+1],f[:cut+1]);check(checks,f'market cut {cut} {kind} weights',ww[:cut-252],w[:cut-252])
    result={'mode':a.mode,'checks':checks,'passed':all(c['passed'] for c in checks)}
    V.write(a.work/'checks'/f'release_{a.mode}.json',result);print(json.dumps(result),flush=True)
    assert result['passed']
if __name__=='__main__':main()
