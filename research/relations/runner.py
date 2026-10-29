"""Original-scorer peer relationship experiments; selected G files stay frozen."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,argparse,time,hashlib
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.common import harness as H

def policy(mode):
    if mode in ('G','GC'):return H.make_policy(mode)
    if mode in ('P','O','PS'):
        from research.peer_alpha.candidate import CandidatePolicy
    elif mode in ('V','VG'):
        from research.peer_risk.candidate import CandidatePolicy
    else:raise ValueError(mode)
    return CandidatePolicy(mode)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--work',required=True,type=Path);ap.add_argument('--model',required=True)
    ap.add_argument('--sleeve',type=float,default=.05);ap.add_argument('--fees',type=float,default=1.);a=ap.parse_args()
    score=H.load_score(a.source);R,X,c=H.load_data(a.source,a.work);c=np.asarray(c)*a.fees
    p=policy(a.model);p.sleeve=a.sleeve
    name=a.model+('_nosleeve' if a.sleeve==0 else '')+(f'_fees{a.fees:g}' if a.fees!=1 else '')
    out=a.work/'runs'/name;out.mkdir(parents=True,exist_ok=True)
    tic=time.perf_counter();f,w,rows,sec,econ=H.exercise(p,R,X,c,score)
    for k,v in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/(k+'.npy'),v)
    stats=H.summary(rows);stats.update(model=a.model,forecast_seconds=sec,forecast_projected_hours_century=sec/len(R)*25200/3600,
       wall_seconds=time.perf_counter()-tic,independent_cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),
       certificates=dict(Counter(v['status'] for v in p.certificates)),relations=getattr(p,'relation_diagnostics',{}),sleeve=a.sleeve,fee_multiplier=a.fees)
    H.write_json(out/'summary.json',stats)
    for k in ('training_records','learner_records','relation_records'):
        if hasattr(p,k):H.write_json(out/(k+'.json'),getattr(p,k))
    if hasattr(p,'diagnostic_arrays'):np.savez_compressed(out/'diagnostics.npz',**p.diagnostic_arrays)
    print(json.dumps(stats,indent=2),flush=True)
    assert stats['independent_cashflow_error']<1e-10
    assert stats['rebalance_ms']<100
    assert stats['forecast_projected_hours_century']<1
if __name__=='__main__':main()
