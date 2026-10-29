"""Run registered Wave6 policies on the unmodified scorer; log all outcomes."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k]='1'
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
from collections import Counter
from importlib.metadata import version
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'research/wave4'),str(ROOT/'research/wave5'),str(ROOT/'handoff_v3')]
import run_wave4 as W
from wave5_models import ResearchPolicy
from wave6_models import RiskStatePolicy, sufficient_statistics


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def run(name,policy,R,X,cost,score,work):
    out=work/'results';out.mkdir(parents=True,exist_ok=True)
    before=time.perf_counter();rows,seconds=score.run(policy,R,X,cost)
    elapsed=time.perf_counter()-before
    forecasts=policy.forecast_output; targets=np.array(policy.targets)
    np.save(out/f'{name}_rows.npy',rows);np.save(out/f'{name}_forecast.npy',forecasts)
    np.save(out/f'{name}_targets.npy',targets)
    diagnostic={}
    if name in ('C','F','I','T','CF'):
        _,cy,_,fy=sufficient_statistics(R,X,policy.cfg)
        n=R.shape[1]; mask=slice(253,len(R)-1)
        c=forecasts[mask,n];v=forecasts[mask,n+1:]
        qspec=np.log(c)+cy[mask]*(1/c-1)
        qfactor=np.mean(np.log(v)+fy[mask]*(1/v-1),axis=1)
        np.save(out/f'{name}_specific_qlike.npy',qspec)
        np.save(out/f'{name}_factor_qlike.npy',qfactor)
        diagnostic={'specific_qlike_vs_B0':float(qspec.mean()),'factor_qlike_vs_B0':float(qfactor.mean()),
                    'specific_multiplier_mean':float(c.mean()),'specific_multiplier_std':float(c.std()),
                    'factor_multiplier_mean':float(v.mean()),'factor_multiplier_std':float(v.std())}
    res=W.summarize(rows)
    res.update(mode=name,forecast_seconds=seconds,forecast_hours_per_century=seconds/len(R)*25200/3600,
               wall_seconds=elapsed,worst_net_day=float(np.min(rows[:,0]-rows[:,1])),
               outer_cap_count=policy.outer_cap_count,solver_status=dict(Counter(c['status'] for c in policy.certificates)),
               training_records=policy.training_records,diagnostic=diagnostic,
               environment={'python':platform.python_version(),**{p:version(p) for p in ('numpy','pandas','scipy','scikit-learn')}})
    W.save_json(out/f'{name}.json',res)
    print(json.dumps({k:v for k,v in res.items() if k not in ('training_records','stages','halves')}),flush=True)
    return rows,res


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--prior',type=Path)
    ap.add_argument('--mode',choices=['refs','C','F','I','T','CF'],required=True);a=ap.parse_args()
    a.work.mkdir(exist_ok=True,parents=True)
    if a.mode!='refs':
        assert json.loads((a.work/'results/reference_gate.json').read_text())['passed'],'reference reproduction gate'
        assert json.loads((a.work/'checks/synthetic_C.json').read_text())['passed'],'synthetic E2E gate'
        if a.mode=='CF':
            assert json.loads((a.work/'results/assessment.json').read_text())['combination_allowed'],'unregistered combination'
    score=W.load_score(a.source);R,X,cost=W.load_inputs(score,a.source,a.work)
    if a.mode=='refs':
        if a.prior is None:raise ValueError('--prior is required for reference reproduction')
        identities=[]
        expected=json.loads((ROOT/'research/wave5/UPSTREAM_IDENTITY.json').read_text())
        for item in expected:
            path=ROOT/'handoff_v3'/item['path'];b=path.read_bytes()
            sha=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
            identities.append({'path':str(path.relative_to(ROOT)),'git_blob':sha,'expected':item['expected'],'passed':sha==item['expected']})
        assert all(x['passed'] for x in identities),'upstream source identity'
        source={f:digest(a.source/f) for f in ('README.md','score.py','returns.csv','characteristics.csv','costs.csv')}
        W.save_json(a.work/'results/source_identity.json',{'upstream':identities,'source_sha256':source})
        checks=[]
        for name in ('B0','H'):
            rows,res=run(name,ResearchPolicy(name),R,X,cost,score,a.work)
            prior=np.load(a.prior/f'{name}_rows.npy')
            err=float(np.max(abs(rows[:,:4]-prior[:,:4])))
            sr=W.metric(prior)['net_sharpe'];checks.append({'reference':name,'max_economic_error':err,'sharpe_error':abs(res['net_sharpe']-sr),'passed':err<1e-10 and abs(res['net_sharpe']-sr)<1e-9})
        W.save_json(a.work/'results/reference_gate.json',{'checks':checks,'passed':all(c['passed'] for c in checks)})
        assert all(c['passed'] for c in checks),'reference gate failed'
    else:
        run(a.mode,RiskStatePolicy(a.mode),R,X,cost,score,a.work)

if __name__=='__main__':main()
