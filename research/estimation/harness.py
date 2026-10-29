"""Original-scorer wrapper for the frozen R/K round."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.common import harness as H


def make_policy(name):
    if name=='R':
        from research.robust.candidate import CandidatePolicy
        return CandidatePolicy()
    if name=='K':
        from research.kalman.candidate import CandidatePolicy
        return CandidatePolicy()
    if name=='R0':
        from research.robust.candidate import CandidatePolicy
        return CandidatePolicy(force_unit_weights=True)
    return H.make_policy(name)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--candidate',required=True);ap.add_argument('--sleeve',type=float,default=.05);ap.add_argument('--fees',type=float,default=1.);a=ap.parse_args()
    score=H.load_score(a.source);R,X,c=H.load_data(a.source,a.work)
    p=make_policy(a.candidate);p.sleeve=a.sleeve;c=np.asarray(c)*a.fees
    name=a.candidate+('_nosleeve' if a.sleeve==0 else '')+(f'_fees{a.fees:g}' if a.fees!=1 else '')
    out=a.work/'runs'/name;out.mkdir(parents=True,exist_ok=True)
    tic=time.perf_counter();f,w,rows,sec,econ=H.exercise(p,R,X,c,score)
    for n,v in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/f'{n}.npy',v)
    result=H.summary(rows);result.update(candidate=a.candidate,sleeve=a.sleeve,fee_multiplier=a.fees,
        forecast_seconds=sec,forecast_projected_hours_century=sec/len(R)*25200/3600,
        wall_seconds=time.perf_counter()-tic,independent_cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),
        certificates=dict(Counter(c['status'] for c in p.certificates)))
    for attr in ('learner_records','training_records','fit_records'):
        if hasattr(p,attr):H.write_json(out/f'{attr}.json',getattr(p,attr))
    if hasattr(p,'diagnostic_arrays'):np.savez_compressed(out/'diagnostics.npz',**p.diagnostic_arrays)
    H.write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
    assert result['independent_cashflow_error']<1e-10
    assert result['rebalance_ms']<100 and result['forecast_projected_hours_century']<1
if __name__=='__main__':main()
