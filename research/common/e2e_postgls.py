"""Complete workflow checks written before the new candidate implementations.

Forecast/policy identities, matured windows, altered futures, prefix/reset and
independently reconstructed scored cashflows. Not economic confirmation.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
import argparse,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research.common import harness as H


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--candidate',choices=['GC','H20','L20'],required=True);ap.add_argument('--mode',choices=['synthetic','market'],required=True);a=ap.parse_args()
    checks=[];score=H.load_score(a.source)
    def ck(name,passed,**kw):checks.append(dict(check=name,passed=bool(passed),**kw))
    def same(name,x,y,tol=1e-10):
        err=float(np.max(np.abs(x-y),initial=0.));ck(name,err<=tol,max_abs_error=err,tolerance=tol)
    def go(rr,xx,c,p=None):
        p=p or H.make_policy(a.candidate)
        out=H.exercise(p,rr,xx,c,score)
        f,w,rows,secs,econ=out
        same('independent cashflows',rows[:,:4],econ)
        ck('finite and gross bounds',np.isfinite(f).all() and np.isfinite(w).all() and (np.abs(w).sum(1)<=5*(1+1e-12)).all())
        for attr in ('learner_records','fit_records'):
            for rec in getattr(p,attr,[]):
                assert rec.get('last_label',-1)<rec['target_row'],'unmatured label'
                if 'feature_row' in rec:assert rec['covariance_last_row']==rec['feature_row']<rec['target_row']
        return p,out
    if a.mode=='synthetic':
        rng=np.random.default_rng(20261104);T,N=440,48
        X=np.empty((T,N,13));X[0]=rng.normal(size=(N,13))
        for t in range(1,T):X[t]=.99*X[t-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
        R=.008*rng.normal(size=(T,N))+.003*rng.normal(size=(T,1));c=np.linspace(.0002,.0008,N)
        pol,out=go(R,X,c);f,w=out[:2]
        baseline=H.make_policy('G');bf=baseline.forecast(R,X)
        if a.candidate=='GC':
            same('unchanged GLS alpha and F risk multiplier channels',f[:,:N+27],bf)
            corr=H.make_policy('CORR').forecast(R,X);same('exact frozen CORR channels',f[:,N+27:],corr[:,N+27:])
        else:same('unchanged F risk channels',f[:,N:],bf[:,N:])
        for length in (253,379):
            if length==253:
                same('short forecast prefix',H.make_policy(a.candidate).forecast(R[:length],X[:length]),f[:length]);continue
            _,o=go(R[:length],X[:length],c);same('prefix forecasts',o[0],f[:length]);same('prefix positions',o[1],w[:len(o[1])])
        for cut,kind in ((83,'joint'),(252,'returns'),(378,'characteristics'),(379,'joint')):
            rr,xx=R.copy(),X.copy()
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            if cut<252:
                ff=H.make_policy(a.candidate).forecast(rr,xx);same('early mutation forecasts',ff[:cut+1],f[:cut+1])
            else:
                _,o=go(rr,xx,c);ff=o[0];same('mutation forecasts',ff[:cut+1],f[:cut+1]);same('mutation positions',o[1][:cut-252],w[:cut-252])
            ck('mutation has power',np.max(np.abs(ff[cut+1:]-f[cut+1:]))>1e-12)
        _,o=go(np.asfortranarray(R),np.asfortranarray(X),c,pol)
        same('reset/layout forecasts',o[0],f);same('reset/layout positions',o[1],w)
        _,o=go(np.zeros_like(R),np.zeros_like(X),c)
        for length in (0,1,63,84,126):
            ff=H.make_policy(a.candidate).forecast(R[:length],X[:length]);ck('short forecast finite',ff.shape[0]==length and np.isfinite(ff).all())
        if a.candidate in ('H20','L20'):
            h1,o1=go(R,X,c,H.make_policy('H1'));b,ob=go(R,X,c,H.make_policy('G'))
            for name,x,y in zip(('H1 forecast identity','H1 positions identity','H1 economics identity'),o1[:3],ob[:3]):
                same(name,x[:,:4] if name.endswith('economics identity') else x,y[:,:4] if name.endswith('economics identity') else y)
    else:
        R,X,c=H.load_data(a.source,a.work);rng=np.random.default_rng(20261105)
        root=a.work/'runs'/a.candidate;f=np.load(root/'forecast.npy',mmap_mode='r');w=np.load(root/'targets.npy',mmap_mode='r')
        for length in (630,2016):
            pol,o=go(R[:length],X[:length],c);same('market prefix forecasts',o[0],f[:length]);same('market prefix positions',o[1],w[:len(o[1])])
        for cut,length,kind in ((630,900,'returns'),(630,900,'characteristics'),(2016,2268,'joint')):
            rr=np.array(R[:length]);xx=np.array(X[:length])
            if kind!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            pol,o=go(rr,xx,c);same('market altered-future forecast',o[0][:cut+1],f[:cut+1]);same('market altered-future positions',o[1][:cut-252],w[:cut-252])
            ck('market mutation has power',np.max(np.abs(o[0][cut+1:]-f[cut+1:length]))>1e-12)
        pol,o=go(R[:630],X[:630],c,pol);same('market reused-session forecasts',o[0],f[:630]);same('market reused-session positions',o[1],w[:len(o[1])])
    result=dict(candidate=a.candidate,mode=a.mode,checks=checks,passed=all(v['passed'] for v in checks))
    H.write_json(a.work/'checks'/f'{a.candidate}_{a.mode}.json',result);print(json.dumps(result,indent=2))
    assert result['passed'],'E2E failure retained'
if __name__=='__main__':main()
