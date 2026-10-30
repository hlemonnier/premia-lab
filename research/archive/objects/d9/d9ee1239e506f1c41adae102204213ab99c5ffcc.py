"""Supplemental complete-workflow direction check, not an economic experiment.

The original planted-fixture assertion only established a nonempty graph; its
name overstated direction recovery. This supplementary E2E criterion is fixed
before running: for known 0->1 positive lag, the added target-1 forecast must
correlate positively (>0.1) with lagged source-0 return, after startup.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.parallel10 import harness as H
from research.parallel10.models import make_policy
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
rng=np.random.default_rng(20261106);T,N=1100,64
r=.01*rng.normal(size=(T,N));x=np.zeros((T,N,13));c=np.full(N,.0002)
for t in range(1,T):r[t,1]+=.9*r[t-1,0]
score=H.load_score(a.source);one=H.exercise(make_policy('N'),r,x,c,score);control=H.exercise(make_policy('N0'),r,x,c,score)
delta=one[0][505:,1]-control[0][505:,1];source=r[504:T-1,0]
corr=float(np.corrcoef(delta,source)[0,1])
checks=[dict(name='known_positive_0_to_1_direction',passed=bool(np.isfinite(corr) and corr>.1),correlation=corr,minimum=.1)]
for name,case in [('N',one),('N0',control)]:
 error=float(np.max(np.abs(case[2][:,:4]-case[4])))
 checks.append(dict(name=name+'_cashflows',passed=bool(error<1e-10),error=error))
result=dict(checks=checks,passed=all(v['passed'] for v in checks),postimplementation_supplemental_E2E=True)
H.write_json(a.work/'checks/injection_supplement.json',result);print(json.dumps(result,indent=2));assert result['passed']
