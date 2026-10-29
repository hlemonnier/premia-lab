"""Constructed E2E risk-state transitions, not performance experiments."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import traceback,json
from pathlib import Path
import numpy as np
import runner as V
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
from release_e2e import exercise
p=V.load_policy('release');source=args.source;score=V.module(source/'score.py','transition_score')
rng=np.random.default_rng(20261101);T,N=640,48
X=rng.normal(size=(1,N,13))+np.cumsum(rng.normal(0,.02,(T,N,13)),axis=0)
base=rng.normal(0,.004,(T,N));c=np.full(N,.0005);cases=[]
r=base.copy();r[:254]=0;cases.append(('zero-to-live at label 254',r,X))
r=base.copy();r[300:]=r[300:]*5;cases.append(('fivefold volatility transition',r,X))
r=base.copy();r[300]=rng.normal(0,.2,N);cases.append(('isolated 20-percent cross-sectional shock',r,X))
r=base.copy();r[:,0]=-0.0001;r[300,0]=-.99;cases.append(('single stock loses 99 percent',r,X))
checks=[]
for label,r,x in cases:
 try:
  f,w,rows=exercise(p,r,x,c,score)
  checks.append({'name':label,'passed':bool(np.isfinite(f).all() and np.isfinite(w).all() and np.isfinite(rows).all() and np.abs(w).sum(1).max()<=5+1e-10),'min_gross_return':float(rows[:,0].min())})
 except Exception as exc:checks.append({'name':label,'passed':False,'error':repr(exc),'traceback':traceback.format_exc()})
res={'type':'constructed operational stress, not future-performance estimates','checks':checks,'passed':all(x['passed'] for x in checks)}
V.write(args.work/'checks/transitions.json',res);print(json.dumps(res),flush=True)
