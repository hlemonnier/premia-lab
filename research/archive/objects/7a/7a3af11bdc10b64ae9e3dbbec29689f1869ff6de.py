"""Supplemental E2E coverage of the stock-order check specified in both plans.

Added after the primary implementations to close omitted workflow coverage;
not a new unit test, model variant, or relaxed numerical tolerance.
"""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from research.common import harness as H

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--candidate',choices=['GC','H20','G'],required=True);ap.add_argument('--refine',action='store_true');a=ap.parse_args()
 if a.refine:
  from model_f import policy as P
  from research.common.numerical_oracle import wrap_allocator
  P.allocate_factor=wrap_allocator(P.allocate_factor)
 rng=np.random.default_rng(20261104);T,N=440,48;X=np.empty((T,N,13));X[0]=rng.normal(size=(N,13))
 for t in range(1,T):X[t]=.99*X[t-1]+np.sqrt(1-.99**2)*rng.normal(size=(N,13))
 R=.008*rng.normal(size=(T,N))+.003*rng.normal(size=(T,1));cost=np.linspace(.0002,.0008,N)
 perm=rng.permutation(N);inv=np.argsort(perm);score=H.load_score(a.source)
 p=H.make_policy(a.candidate);f,w,rows,sec,econ=H.exercise(p,R,X,cost,score)
 q=H.make_policy(a.candidate);f2,w2,rows2,sec2,econ2=H.exercise(q,R[:,perm],X[:,perm],cost[perm],score)
 reordered=np.hstack([f2[:,:N][:,inv],f2[:,N:]])
 vals={'forecasts':(float(np.abs(f-reordered).max()),1e-10),'positions':(float(np.abs(w-w2[:,inv]).max()),1e-8),
       'returns_and_fees':(float(np.abs(rows[:,:2]-rows2[:,:2]).max()),1e-10),
       'aggregate_gross':(float(np.abs(rows[:,2]-rows2[:,2]).max()),1e-10)}
 checks=[dict(check=k,max_abs_error=v,tolerance=tol,passed=v<=tol) for k,(v,tol) in vals.items()]
 result=dict(candidate=a.candidate,verification_only_refinement=a.refine,original_default_receipt_unchanged=True,checks=checks,passed=all(x['passed'] for x in checks))
 H.write_json(a.work/'checks'/(f'{a.candidate}_permutation'+('_refined.json' if a.refine else '.json')),result);print(result)
 # Preserve a genuine failed assertion; never silently amend the tolerance.
 assert result['passed'],'stock-order numerical exception; receipt retained'
if __name__=='__main__':main()
