"""Execute exactly one registered policy, with the supplied scorer unmodified."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time,hashlib,platform
from pathlib import Path
from collections import Counter
from importlib.metadata import version
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'research/wave4'),str(ROOT/'handoff_v3')]
import run_wave4 as W
from wave5_models import ResearchPolicy, risk_paths


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--mode',required=True);a=ap.parse_args();out=a.work/'results';out.mkdir(parents=True,exist_ok=True)
    if a.mode not in ('B0','R1'):
        receipt=json.loads((out/'reference_gate.json').read_text())
        if not receipt['passed']:raise RuntimeError('reference gate failed')
        synth=json.loads((a.work/'checks/synthetic_H.json').read_text())
        if not synth['passed']:raise RuntimeError('synthetic E2E gate failed')
    score=W.load_score(a.source);R,X,cost=W.load_inputs(score,a.source,a.work)
    p=ResearchPolicy(a.mode);t0=time.perf_counter()
    rows,sec=score.run(p,R,X,cost);wall=time.perf_counter()-t0
    targets=np.array(p.targets);f=p.forecast_output
    np.save(out/f'{a.mode}_rows.npy',rows);np.save(out/f'{a.mode}_targets.npy',targets);np.save(out/f'{a.mode}_forecast.npy',f)
    diag={}
    # Outcome diagnostics belong here, AFTER trading, never inside a policy.
    if a.mode in ('H','HP','EH'):
        d,u2,_,_=risk_paths(R,X,p.cfg)
        z=f[253:len(R)-1,:,1]
        q=np.log(z)+(u2[253:len(R)-1]/d[252:len(R)-2])*(1/z-1)
        diag['qlike_vs_B0']=float(np.mean(q))
        np.save(out/f'{a.mode}_qlike_daily.npy',np.mean(q,axis=1))
    res=W.summarize(rows);res.update(mode=a.mode,forecast_seconds=sec,forecast_hours_per_century=sec/len(R)*25200/3600,
        wall_seconds=wall,worst_net_day=float(np.min(rows[:,0]-rows[:,1])),outer_cap_count=p.outer_cap_count,
        solver_status=dict(Counter(x['status'] for x in p.certificates)),training_records=p.training_records,
        diagnostic=diag,variance_multiplier={'min':float(f[:,:,1].min()),'max':float(f[:,:,1].max()),'mean':float(f[253:,:,1].mean())},
        environment={'python':platform.python_version(),'numpy':version('numpy'),'scipy':version('scipy'),'scikit-learn':version('scikit-learn')})
    W.save_json(out/f'{a.mode}.json',res)
    print(json.dumps({k:v for k,v in res.items() if k not in ('training_records','stages','halves')}),flush=True)
    if a.mode=='R1':
        prior=ROOT.parents[0]/'wave4_evidence/results/R1_rows.npy'
        reference=np.load(prior)
        b0=np.load(out/'B0_rows.npy');old_b0=np.load(ROOT.parents[0]/'wave4_evidence/results/B0_rows.npy')
        err=float(np.max(abs(rows[:,:4]-reference[:,:4])));err0=float(np.max(abs(b0[:,:4]-old_b0[:,:4])))
        gate={'R1_max_economic_error':err,'B0_max_economic_error':err0,
              'R1_sharpe_error':abs(res['net_sharpe']-1.4576547036224103),'passed':err<1e-10 and err0<1e-10 and abs(res['net_sharpe']-1.4576547036224103)<1e-9}
        W.save_json(out/'reference_gate.json',gate);print(json.dumps(gate),flush=True);assert gate['passed']

if __name__=='__main__':main()
