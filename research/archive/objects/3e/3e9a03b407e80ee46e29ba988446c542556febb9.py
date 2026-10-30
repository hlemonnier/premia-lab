"""End-to-end contracts and separate dense oracle, written before control implementation.

Not a unit-test suite. Each control is checked through forecasts, original scorer,
actual portfolios and independent cashflow reconstruction. The dense oracle rebuilds
causal noise covariance independently and never uses Woodbury or the candidate's
statistics function. It shares the separately audited F risk-multiplier payload.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse, importlib.util, json, sys, time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research/common'))
import harness as H
from model_f.factor_risk import FactorPolicy
from research.gls.candidate import CandidatePolicy as Original
from controls import ControlPolicy, controlled_forecast, VARIANTS


def cmp(name,a,b,checks,tol=1e-10):
    err=float(np.max(np.abs(np.asarray(a)-np.asarray(b)),initial=0))
    checks.append(dict(check=name,max_abs_error=err,tolerance=tol,passed=bool(err<=tol)))


def independent_basis(panel):
    x=np.ascontiguousarray(panel,dtype=np.float64)
    c=x-x.mean(axis=0);std=np.sqrt(np.mean(c*c,axis=0))
    z=np.clip(c/np.maximum(std,1e-12),-4.,4.);z-=z.mean(axis=0)
    sq=z*z
    return np.concatenate((z,(sq-sq.mean(axis=0))/np.sqrt(2.)),axis=1)


def independent_beta(R,t):
    if t<20:return np.ones(R.shape[1])
    r=R[max(0,t-252):t];m=r.mean(axis=1);mc=m-m.mean();rc=r-r.mean(axis=0)
    var=mc@mc
    return mc@rc/var if var>1e-12*len(r) else np.ones(R.shape[1])


def dense_reference(R,X,base,cfg):
    """Direct N x N covariance solves, independently rebuilt lagged risk moments."""
    T,N=R.shape;B=[independent_basis(x) for x in X]
    beta=np.array([independent_beta(R,t) for t in range(T)])
    designs=[]
    for s in range(T-1):
        z=beta[s+1]-beta[s+1].mean();z=np.clip(z/max(z.std(),1e-12),-4.,4.);z-=z.mean()
        designs.append(np.column_stack([B[s],z]))
    qF=np.zeros((26,26));qU=np.zeros(N);mass=0.;a=2**(-1/126)
    Fs=[np.zeros((26,26))];ds=[np.ones(N)*1e-6]
    for s in range(1,T-1):
        y=R[s]-beta[s]*R[s].mean();y-=y.mean();D=B[s-1]
        f=np.linalg.solve(D.T@D/N+1e-10*np.eye(26),D.T@y/N)
        u=y-D@f;qF=a*qF+np.outer(f,f);qU=a*qU+u*u;mass=a*mass+1
        v=qU/mass;ds.append(np.maximum(.8*v+.2*np.median(v),1e-6));Fs.append(qF/mass)
    gs=[np.zeros((27,27)),np.zeros((27,27))];hs=[np.zeros(27),np.zeros(27)];ms=[0.,0.]
    out=base[:,:N].copy();conditions=[];resids=[]
    for t in range(65,T):
        u=t-1;D=designs[u-1];mult=base[u,N+1:]
        A=np.sqrt(mult);F=Fs[u-1]*np.outer(A,A)
        Om=np.diag(ds[u-1])+D[:,:26]@F@D[:,:26].T
        # Dense solve, then Schur complement of a separate daily nuisance intercept.
        Z=np.column_stack([np.ones(N),D]);y=R[u]-beta[u]*R[u].mean()
        J=np.linalg.solve(Om,Z);jy=np.linalg.solve(Om,y)
        K=Z.T@J/N;h=Z.T@jy/N
        g=K[1:,1:]-np.outer(K[1:,0],K[0,1:])/K[0,0]
        hh=h[1:]-K[1:,0]*h[0]/K[0,0];g=.5*(g+g.T)
        for k,hl in enumerate((1008.,252.)):
            a=2**(-1/hl);gs[k]=a*gs[k]+g;hs[k]=a*hs[k]+hh;ms[k]=a*ms[k]+1
        if t>=253 and t-64>=126:
            theta=[]
            for k in range(2):
                g=gs[k]/ms[k];h=hs[k]/ms[k];floor=1e-12*max(np.diag(g).mean(),1e-12)
                Q=g+.1*np.diag(np.maximum(np.diag(g),floor));coef=np.linalg.solve(Q,h)
                theta.append(coef);resids.append(float(np.linalg.norm(Q@coef-h)/(1+np.linalg.norm(h))))
            co=theta[0].copy();co[:13]=.5*(theta[0][:13]+theta[1][:13])
            out[t]=.5*base[t,:N]+.5*(designs[t-1]@co)
        if t in (65,253,379,T-1):conditions.append({'t':t,'omega_condition':float(np.linalg.cond(Om))})
    return out,{'condition_samples':conditions,'max_normal_equation_relative_residual':max(resids,default=0.)}


class FrozenPath(FactorPolicy):
    def __init__(self,path):super().__init__();self.path=path
    def forecast(self,returns_history,characteristics_history):
        super().forecast(returns_history,characteristics_history)
        self.forecast_output=self.path.copy();return self.forecast_output


def case(p,R,X,cost,score,checks,name):
    f,w,r,secs,econ=H.exercise(p,R,X,cost,score)
    cmp(name+' cashflow ledger',r[:,:4],econ,checks)
    checks.append(dict(check=name+' finite/bounds/certificates',passed=bool(np.isfinite(f).all() and np.isfinite(w).all()
        and np.max(np.abs(w).sum(axis=1))<=5+1e-10 and np.min(r[:,0])>-1
        and all(c['status'] in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal') for c in p.certificates))))
    return f,w,r


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--mode',choices=['algebra','controls','market'],required=True);ap.add_argument('--strict-numerics',action='store_true');ap.add_argument('--polish-numerics',action='store_true');a=ap.parse_args();checks=[]
    if a.strict_numerics:
        from model_f import policy as P
        original_allocate=P.allocate_factor
        def tightened(*args,**kwargs):
            kwargs['tol']=1e-15;kwargs['max_iter']=300
            return original_allocate(*args,**kwargs)
        P.allocate_factor=tightened
    if a.polish_numerics:
        from model_f import policy as P
        from numerical_oracle import wrap_allocator
        P.allocate_factor=wrap_allocator(P.allocate_factor)
    score=H.load_score(a.source);rng=np.random.default_rng(20261103)
    if a.mode in ('algebra','controls'):
        T,N=420,48;X=np.cumsum(rng.normal(0,.025,(T,N,13)),axis=0)+rng.normal(size=(1,N,13))
        R=.00005*X[:,:,0]+rng.normal(0,.003,(T,N))*np.linspace(.5,1.5,N)
        R+=rng.normal(0,.002,(T,1))+rng.normal(0,.001,(T,1))*X[:,:,2]
        cost=np.linspace(.0002,.0008,N);base=FactorPolicy().forecast(R,X)
    if a.mode=='algebra':
        f,w,r=case(Original(),R,X,cost,score,checks,'original GLS')
        oracle,diag=dense_reference(R,X,base,FactorPolicy().cfg)
        path=np.hstack([oracle,base[:,N:]])
        fo,wo,ro=case(FrozenPath(path),R,X,cost,score,checks,'dense GLS')
        cmp('dense forecast vs original',fo,f,checks);cmp('dense positions vs original',wo,w,checks)
        cmp('dense economic rows vs original',ro[:,:4],r[:,:4],checks)
        fg,wg,rg=case(ControlPolicy('G_D'),R,X,cost,score,checks,'generic GLS')
        cmp('generic original GLS forecasts',fg,f,checks);cmp('generic original GLS positions',wg,w,checks)
        cmp('generic original GLS economics',rg[:,:4],r[:,:4],checks)
        oa0,_=controlled_forecast(R,X,base,FactorPolicy().cfg,'O_A0')
        cmp('OLS full-start identity with F2',oa0,base[:,:N],checks)
        for key in ['G_D','G_S','O_D','O_S']:
            aa,_=controlled_forecast(R,X,base,FactorPolicy().cfg,key)
            bb,_=controlled_forecast(R,X,base,FactorPolicy().cfg,key,precision_scale=7.)
            cmp(key+' constant precision-scale invariance',aa,bb,checks)
        H.write_json(a.work/'checks/dense_conditioning.json',diag)
    elif a.mode=='controls':
        for key in ['O_D','G_S','O_S','D_D','O_A','G_N']:
            p=ControlPolicy(key);f,w,r=case(p,R,X,cost,score,checks,key)
            cmp(key+' unchanged risk channels',f[:,N:],base[:,N:],checks)
            for length in [379,400]:
                fp,wp,rp=case(p,R[:length],X[:length],cost,score,checks,key+f' prefix{length}')
                cmp(key+f' prefix{length} forecasts',fp,f[:length],checks);cmp(key+f' prefix{length} positions',wp,w[:len(wp)],checks)
            for cut,kind in [(126,'returns'),(252,'characteristics'),(378,'joint')]:
                rr=R.copy();xx=X.copy()
                if kind!='characteristics':rr[cut:]=rng.normal(0,.01,rr[cut:].shape)
                if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
                fm,wm,rm=case(p,rr,xx,cost,score,checks,key+f' mutation{cut}')
                cmp(key+f' {kind} past forecast',fm[:cut+1],f[:cut+1],checks)
                cmp(key+f' {kind} past positions',wm[:max(0,cut-252)],w[:max(0,cut-252)],checks)
                checks.append(dict(check=key+f' {kind} power',passed=bool(np.max(np.abs(fm[cut+1:]-f[cut+1:]))>1e-10)))
            fr,wr,rr=case(p,R,X,cost,score,checks,key+' reset');cmp(key+' reset forecast',fr,f,checks);cmp(key+' reset positions',wr,w,checks)
            ff,wf,rf=case(p,np.asfortranarray(R),np.asfortranarray(X),cost,score,checks,key+' layout')
            cmp(key+' layout forecasts',ff,f,checks);cmp(key+' layout positions',wf,w,checks)
            perm=rng.permutation(N);inv=np.argsort(perm)
            fp,wp,rp=case(p,R[:,perm],X[:,perm],cost[perm],score,checks,key+' permutation')
            cmp(key+' permuted forecasts',fp[:,:N][:,inv],f[:,:N],checks)
            cmp(key+' permuted positions',wp[:,inv],w,checks,1e-8)
            cmp(key+' permuted cashflows',rp[:,[0,1,3]],r[:,[0,1,3]],checks)
            fz,wz,rz=case(p,np.zeros_like(R),np.zeros_like(X),cost,score,checks,key+' zeros')
            cmp(key+' zero alpha',fz[:,:N],np.zeros((T,N)),checks)
    else:
        R,X,cost=H.load_data(a.source,a.work);N=R.shape[1]
        for key in ['G_D','O_D']:
            p=ControlPolicy(key);folder=a.work/'runs'/key
            f=np.load(folder/'forecast.npy',mmap_mode='r');w=np.load(folder/'targets.npy',mmap_mode='r')
            for length in (630,2016):
                fp,wp,rp=case(p,R[:length],X[:length],cost,score,checks,key+f' prefix{length}')
                cmp(key+f' prefix{length} forecasts',fp,f[:length],checks);cmp(key+f' prefix{length} positions',wp,w[:len(wp)],checks)
            for cut,kind in [(630,'returns'),(630,'characteristics'),(630,'joint')]:
                length=760;rr=np.array(R[:length]);xx=np.array(X[:length])
                if kind!='characteristics':rr[cut:]=rng.normal(0,.015,rr[cut:].shape)
                if kind!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
                fm,wm,rm=case(p,rr,xx,cost,score,checks,key+' '+kind)
                cmp(key+' '+kind+' prior forecasts',fm[:cut+1],f[:cut+1],checks);cmp(key+' '+kind+' prior positions',wm[:cut-252],w[:cut-252],checks)
            fr,wr,rr=case(p,R[:630],X[:630],cost,score,checks,key+' reset');cmp(key+' reset forecast',fr,f[:630],checks);cmp(key+' reset weights',wr,w[:len(wr)],checks)
    result=dict(mode=a.mode,strict_numerics=a.strict_numerics,polish_numerics=a.polish_numerics,checks=checks,passed=all(c['passed'] for c in checks),independent_person_review=False)
    H.write_json(a.work/'checks'/(f'e2e_{a.mode}'+('_tightened' if a.strict_numerics else '')+('_polished' if a.polish_numerics else '')+'.json'),result);print(json.dumps(result,indent=2),flush=True)
    assert result['passed'],'E2E failure; do not relax tolerances'
if __name__=='__main__':main()
