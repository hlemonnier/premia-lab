"""Frozen GLS release E2E workflows. Written before standalone packaging.
No unit tests, model selection, parameter search or modified original scorer.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
import argparse, ast, gc, hashlib, importlib.util, json, platform, resource, shutil, subprocess, sys, time, zipfile
from collections import Counter
from pathlib import Path
import numpy as np

TOL=1e-10
GOOD={'ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal'}

def dump(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')

def module(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def blob(p):
    b=Path(p).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def load_data(source,work):
    cache=work/'inputs';cache.mkdir(parents=True,exist_ok=True)
    if not (cache/'complete.json').exists():
        score=module(source/'score.py','source_score_load');arrays=score.load(source)
        for name,a in zip(('R','X','cost'),arrays): np.save(cache/f'{name}.npy',np.ascontiguousarray(a,dtype=np.float64))
        identities={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.suffix in ('.csv','.py','.md')}
        dump(cache/'complete.json',identities)
    return tuple(np.load(cache/f'{name}.npy',mmap_mode='r') for name in ('R','X','cost'))

class Audit:
    def __init__(self,pol,save_weights=True): self.pol=pol;self.save_weights=save_weights
    def forecast(self,returns_history,characteristics_history):
        n=returns_history.shape[1];self.prev=np.zeros(n);self.targets=[];self.econ=[];self.call_times=[]
        self.max_drift_error=0.;self.max_gross=0.;self.max_weight=0.;self.min_return=0.;self.calls=0
        return self.pol.forecast(returns_history,characteristics_history)
    def rebalance(self,held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        r=returns_history[-1];g=float(self.prev@r)
        assert np.isfinite(g) and g>-1,'ruin or nonfinite gross return'
        h=self.prev*(1+r)/(1+g)
        self.max_drift_error=max(self.max_drift_error,float(np.max(np.abs(h-held_positions))))
        start=time.perf_counter()
        w=self.pol.rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        self.call_times.append(time.perf_counter()-start)
        assert np.isfinite(w).all() and np.abs(w).sum()<=5*(1+1e-12),'invalid target'
        fee=0. if not self.calls else float(trading_costs@np.abs(w-h))
        self.econ.append([g,fee,float(np.abs(w).sum()),float(r.mean())])
        self.max_gross=max(self.max_gross,float(np.abs(w).sum()));self.max_weight=max(self.max_weight,float(np.abs(w).max()))
        self.min_return=min(self.min_return,g);self.prev=w.copy();self.calls+=1
        if self.save_weights:self.targets.append(w.copy())
        if self.calls%5000==0:print(json.dumps({'calls':self.calls,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}),flush=True)
        return w

def metrics(rows):
    x=rows[:,0]-rows[:,1];m=rows[:,3];mc=m-m.mean()
    return dict(sharpe=float(np.sqrt(252)*x.mean()/x.std()) if x.std()>0 else None,
        beta=float(mc@(x-x.mean())/(mc@mc)) if mc@mc>0 else None,
        annual_cost=float(252*rows[:,1].mean()),annual_mean=float(252*x.mean()),annual_vol=float(np.sqrt(252)*x.std()))

def replay(score,pol,R,X,cost,save_weights=True):
    p=Audit(pol,save_weights);start=time.perf_counter();rows,secs=score.run(p,R,X,cost)
    eco=np.array(p.econ)[1:];cert=Counter(c['status'] for c in pol.certificates)
    err=float(np.max(np.abs(rows[:,:4]-eco),initial=0.))
    f=pol.forecast_output
    s=dict(source_days=len(R),stocks=R.shape[1],scored_rows=len(rows),calls=p.calls,forecast_seconds=secs,
        rebalance_ms=float(rows[:,4].mean()*1000),all_call_ms=float(1000*np.mean(p.call_times)),
        p99_call_ms=float(1000*np.quantile(p.call_times,.99)),max_call_ms=float(1000*max(p.call_times)),
        wall_seconds=time.perf_counter()-start,peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        max_drift_error=p.max_drift_error,cashflow_error=err,max_gross=p.max_gross,max_abs_weight=p.max_weight,
        worst_gross_day=p.min_return,certificates=dict(cert),risk_fit_count=len(pol.training_records),
        gls_record_count=len(pol.learner_records),risk_min=float(f[:,R.shape[1]:].min()),risk_max=float(f[:,R.shape[1]:].max()))
    assert err<TOL and p.max_drift_error<TOL,'cashflow reconstruction'
    assert set(cert)<=GOOD and sum(cert.values())==2*p.calls,'certificates'
    assert np.isfinite(rows).all() and np.isfinite(f).all(),'finite outputs'
    assert s['risk_min']>=.75 and s['risk_max']<=1.5,'risk bound'
    assert all(r['last_label']<r['target_row'] for r in pol.training_records),'risk label timing'
    assert all(r['covariance_last_row']<r['last_label']<r['target_row'] for r in pol.learner_records),'GLS label timing'
    return f,np.array(p.targets) if save_weights else None,rows,s

def comparison(checks,name,a,b,tol=TOL):
    error=float(np.max(np.abs(a-b),initial=0.));checks.append(dict(name=name,error=error,tolerance=tol,passed=error<=tol))

def boolean(checks,name,v,**extra):checks.append(dict(name=name,passed=bool(v),**extra))

def finish(work,mode,checks,extra=None):
    rec=dict(mode=mode,checks=checks,passed=all(x['passed'] for x in checks),extra=extra)
    dump(work/'checks'/f'{mode}.json',rec);print(json.dumps(rec),flush=True)
    assert rec['passed'],f'{mode} failed; preserve receipt'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--prior',type=Path);ap.add_argument('--mode',required=True,choices=['package','synthetic','full','reference','market','century','late','cli'])
    a=ap.parse_args();repo=a.repo.resolve();work=a.work.resolve();work.mkdir(exist_ok=True,parents=True)
    pkg=repo/'handoff_gls';assert (pkg/'strategy.py').exists(),'standalone package not implemented yet'
    sys.path.insert(0,str(pkg));strategy=module(pkg/'strategy.py','release_strategy')
    from gls_alpha import CandidatePolicy
    score=module(a.source/'score.py','original_scorer');checks=[]
    if a.mode=='package':
        allowed={'strategy.py','gls_alpha.py','README.md','requirements.txt'}|{'model_f/'+p.name for p in (repo/'model_f').glob('*.py')}
        actual={str(p.relative_to(pkg)) for p in pkg.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        boolean(checks,'ten-file allowlist',actual==allowed and len(actual)==10)
        for path in sorted(allowed-{'strategy.py','README.md'}):
            src=repo/'research/gls/candidate.py' if path=='gls_alpha.py' else repo/path
            boolean(checks,'frozen bytes '+path,(pkg/path).read_bytes()==src.read_bytes(),git_blob=blob(pkg/path))
        for path in actual:
            if path.endswith('.py'):
                tree=ast.parse((pkg/path).read_text())
                imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]+[x.name for n in ast.walk(tree) if isinstance(n,ast.Import) for x in n.names]
                boolean(checks,'no research import '+path,not any('research' in x for x in imports))
        zpath=work/'GLS_Candidate.zip'
        with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(allowed):z.write(pkg/p,p)
        extract=work/'isolated';extract.mkdir(exist_ok=True)
        with zipfile.ZipFile(zpath) as z:z.extractall(extract)
        env={**os.environ,'PYTHONPATH':'','PYTHONDONTWRITEBYTECODE':'1'}
        cmd=[sys.executable,'-c',"import strategy; from pathlib import Path; import numpy as np; f=strategy.forecast(np.zeros((420,48)),np.zeros((420,48,13))); assert f.shape==(420,75); assert np.isfinite(f).all(); print(Path(strategy.__file__).resolve())"]
        run=subprocess.run(cmd,cwd=extract,env=env,text=True,capture_output=True)
        dump(work/'logs/isolation.json',dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
        boolean(checks,'isolated import and zero forecast',run.returncode==0)
        finish(work,a.mode,checks,{'archive_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest()});return
    if a.mode=='synthetic':
        rng=np.random.default_rng(20261029);T,N=420,48
        X=np.cumsum(rng.normal(0,.03,(T,N,13)),axis=0)+rng.normal(0,1,(N,13))
        R=.004*rng.normal(size=(T,1))+.012*rng.normal(size=(T,N))+.0001*X[:,:,0]
        cost=np.full(N,.0005);p=CandidatePolicy();f,w,rows,stats=replay(score,p,R,X,cost)
        boolean(checks,'complete finite certified workflow',True)
        for length in (0,1,64,65,126,252,253,379):
            fp=p.forecast(R[:length],X[:length]);comparison(checks,f'forecast prefix {length}',fp,f[:length])
        for cut in (64,126,252,253,378,379):
            rr=R.copy();xx=X.copy();rr[cut:]*=-2;xx[cut:]=rng.normal(size=xx[cut:].shape)
            fm=p.forecast(rr,xx);comparison(checks,f'joint cut {cut}',fm[:cut+1],f[:cut+1])
        for mode in ('returns','characteristics'):
            rr=R.copy();xx=X.copy();cut=378
            if mode=='returns':rr[cut:]*=-3
            else:xx[cut:]+=2*rng.normal(size=xx[cut:].shape)
            fm,wm,rm,_=replay(score,p,rr,xx,cost)
            comparison(checks,mode+' past forecasts',fm[:cut+1],f[:cut+1]);comparison(checks,mode+' past positions',wm[:cut-252],w[:cut-252])
        fp,wp,rp,_=replay(score,p,R[:379],X[:379],cost)
        comparison(checks,'prefix replay targets',wp,w[:len(wp)]);comparison(checks,'prefix cashflows',rp[:,:4],rows[:len(rp),:4])
        fr,wr,rr,_=replay(score,p,R,X,cost)
        comparison(checks,'reset forecast',fr,f);comparison(checks,'reset positions',wr,w)
        ff,wf,rf,_=replay(score,p,np.asfortranarray(R),np.asfortranarray(X),cost)
        comparison(checks,'Fortran forecast',ff,f);comparison(checks,'Fortran targets',wf,w)
        perm=rng.permutation(N);inv=np.argsort(perm)
        fs,ws,rs,_=replay(score,p,R[:,perm],X[:,perm],cost[perm])
        comparison(checks,'permutation alpha',fs[:,:N][:,inv],f[:,:N]);comparison(checks,'permutation risk',fs[:,N:],f[:,N:])
        comparison(checks,'permutation positions',ws[:,inv],w,1e-8);comparison(checks,'permutation economics',rs[:,:4],rows[:,:4])
        fz,wz,rz,_=replay(score,p,np.zeros_like(R),np.zeros_like(X),cost)
        boolean(checks,'zero history workflow',np.isfinite(fz).all() and np.isfinite(wz).all())
        for n in (1,13):
            replay(score,p,R[:,:n],X[:,:n],cost[:n]);boolean(checks,f'{n}-stock workflow',True)
        for name,action in [
            ('invalid characteristics',lambda:p.forecast(R,X[:,:,:12])),
            ('negative costs',lambda:p.rebalance(np.zeros(N),f[253],R[:253],X[:253],-cost))]:
            p.forecast(R,X)
            try: action();rejected=False
            except (ValueError,RuntimeError):rejected=True
            boolean(checks,name,rejected)
        p.forecast(R,X);p.rebalance(np.zeros(N),f[253],R[:253],X[:253],cost)
        try:p.rebalance(np.zeros(N),f[255],R[:255],X[:255],cost);rejected=False
        except RuntimeError:rejected=True
        boolean(checks,'nonsequential rejected',rejected)
        finish(work,a.mode,checks,stats);return
    R,X,cost=load_data(a.source,work)
    out=work/'results';out.mkdir(exist_ok=True)
    if a.mode in ('full','reference'):
        p=CandidatePolicy() if a.mode=='full' else module(repo/'research/gls/candidate.py','research_candidate').CandidatePolicy()
        f,w,rows,stats=replay(score,p,R,X,cost)
        for name,arr in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/f'{a.mode}_{name}.npy',arr)
        stats.update(metrics(rows));dump(out/f'{a.mode}.json',stats)
        dump(out/f'{a.mode}_fits.json',dict(risk=p.training_records,gls=p.learner_records))
        boolean(checks,'published Sharpe reproduced',abs(stats['sharpe']-1.5332155606881952)<1e-9)
        if a.prior:comparison(checks,'prior economic rows',rows[:,:4],np.load(a.prior)[:,:4])
        if a.mode=='reference':
            for name,arr in [('forecast',f),('targets',w),('rows',rows[:,:4])]:
                old=np.load(out/f'full_{name}.npy',mmap_mode='r');old=old[:,:4] if name=='rows' else old
                comparison(checks,'packaged vs original '+name,arr,old)
        boolean(checks,'runtime budget',stats['rebalance_ms']<100 and stats['forecast_seconds']/len(R)*25200<3600)
        boolean(checks,'finite, bounds, certificates and cashflows',True)
        finish(work,a.mode,checks,stats);return
    if a.mode=='market':
        f=np.load(out/'full_forecast.npy',mmap_mode='r');w=np.load(out/'full_targets.npy',mmap_mode='r');rows=np.load(out/'full_rows.npy')
        p=CandidatePolicy()
        for length in (379,630,2016,3779):
            fp,wp,rp,_=replay(score,p,R[:length],X[:length],cost)
            comparison(checks,f'prefix {length} forecast',fp,f[:length]);comparison(checks,f'prefix {length} targets',wp,w[:len(wp)])
            comparison(checks,f'prefix {length} economic rows',rp[:,:4],rows[:len(rp),:4])
        for mode,cut,length in [('returns',630,900),('characteristics',630,900),('joint',2016,2143),('last',3779,3780)]:
            rr=np.array(R[:length]);xx=np.array(X[:length]);rng=np.random.default_rng(20261029+cut)
            if mode!='characteristics':rr[cut:]=rng.normal(0,.02,rr[cut:].shape)
            if mode!='returns':xx[cut:]=rng.normal(size=xx[cut:].shape)
            fm,wm,rm,_=replay(score,p,rr,xx,cost)
            comparison(checks,mode+' future forecast',fm[:cut+1],f[:cut+1]);comparison(checks,mode+' future targets',wm[:cut-252],w[:cut-252])
        finish(work,a.mode,checks);return
    if a.mode=='cli':
        clean=work/'isolated';clean.mkdir(exist_ok=True)
        for p in pkg.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                dst=clean/p.relative_to(pkg);dst.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,dst)
        shutil.copy2(a.source/'score.py',clean/'score.py')
        for name in ('returns.csv','characteristics.csv','costs.csv'):
            dst=clean/name
            if not dst.exists():os.link(a.source/name,dst)
        env={**os.environ,'PYTHONPATH':'','PYTHONDONTWRITEBYTECODE':'1'}
        run=subprocess.run([sys.executable,'score.py','strategy'],cwd=clean,env=env,capture_output=True,text=True)
        dump(work/'logs/cli.json',dict(command='python score.py strategy',cwd=str(clean),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
        boolean(checks,'literal isolated original CLI',run.returncode==0)
        finish(work,a.mode,checks,{'stdout':run.stdout,'stderr':run.stderr});return
    end=work/'endurance';end.mkdir(exist_ok=True)
    if a.mode=='century':
        for name,base in [('R',R),('X',X)]:
            dst=np.lib.format.open_memmap(end/f'{name}.npy',mode='w+',dtype=np.float64,shape=(25200,)+base.shape[1:])
            for lo in range(0,25200,len(base)):
                k=min(25200-lo,len(base));dst[lo:lo+k]=base[:k]
            dst.flush();del dst
        del R,X;gc.collect()
        R=np.load(end/'R.npy',mmap_mode='r');X=np.load(end/'X.npy',mmap_mode='r');p=CandidatePolicy()
        f,w,rows,stats=replay(score,p,R,X,cost,save_weights=False)
        np.save(end/'forecast.npy',f);np.save(end/'rows.npy',rows)
        dump(end/'stats.json',stats);dump(end/'fits.json',dict(risk=p.training_records,gls=p.learner_records))
        boolean(checks,'actual century completed',stats['source_days']==25200 and stats['calls']==24947)
        boolean(checks,'actual century timing',stats['forecast_seconds']<3600 and stats['all_call_ms']<100)
        boolean(checks,'finite bounded certified cashflows and label timing',True)
        comparison(checks,'15-year prefix in century',f[:3780],np.load(out/'full_forecast.npy'))
        finish(work,a.mode,checks,stats);return
    if a.mode=='late':
        R=np.load(end/'R.npy',mmap_mode='r');X=np.load(end/'X.npy',mmap_mode='r');cut=25074
        rr=np.array(R);rr[cut:]=np.random.default_rng(20261029).normal(0,.01,rr[cut:].shape)
        p=CandidatePolicy();start=time.perf_counter();fm=p.forecast(rr,X)
        old=np.load(end/'forecast.npy',mmap_mode='r');err=0.
        for lo in range(0,cut+1,252):
            hi=min(cut+1,lo+252);err=max(err,float(np.max(abs(fm[lo:hi]-old[lo:hi]))))
        boolean(checks,'late century future mutation',err<=TOL,error=err,cut=cut)
        boolean(checks,'mutation affects later forecasts',float(np.max(abs(fm[cut+1:]-old[cut+1:])))>0)
        finish(work,a.mode,checks,{'forecast_seconds':time.perf_counter()-start,'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024})

if __name__=='__main__':main()
