"""Supplemental full-replay numerical investigation; no production edits."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,argparse
from pathlib import Path
import numpy as np
import release_checks as V

def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
 sys.path.insert(0,str(a.repo.resolve()/'handoff_gls'))
 from gls_alpha import CandidatePolicy
 from model_f import policy as P
 oracle=V.module(a.repo/'research/gls_review/numerical_oracle.py','saved_numerical_oracle')
 score=V.module(a.source/'score.py','original_score_diag')
 rng=np.random.default_rng(20261029);T,N=420,48
 X=np.cumsum(rng.normal(0,.03,(T,N,13)),axis=0)+rng.normal(0,1,(N,13))
 R=.004*rng.normal(size=(T,1))+.012*rng.normal(size=(T,N))+.0001*X[:,:,0]
 cost=np.full(N,.0005)
 # Consume the exact preceding perturbation draws from the frozen suite.
 for cut in (64,126,252,253,378,379):rng.normal(size=X[cut:].shape)
 rng.normal(size=X[378:].shape)
 perm=rng.permutation(N);inv=np.argsort(perm);result={}
 for label in ('default','verification_only_KKT'):
  if label!='default':P.allocate_factor=oracle.wrap_allocator(P.allocate_factor)
  f,w,r,s=V.replay(score,CandidatePolicy(),R,X,cost)
  ff,ww,rr,ss=V.replay(score,CandidatePolicy(),R[:,perm],X[:,perm],cost[perm])
  result[label]={'alpha_error':float(np.max(abs(f[:,:N]-ff[:,:N][:,inv]))),
    'risk_error':float(np.max(abs(f[:,N:]-ff[:,N:]))),'weight_error':float(np.max(abs(w-ww[:,inv]))),
    'economic_errors_by_column':dict(zip(['return','fee','gross','market'],np.max(abs(r[:,:4]-rr[:,:4]),axis=0).tolist())),
    'independent_cashflow_errors':[s['cashflow_error'],ss['cashflow_error']],
    'certificates':[s['certificates'],ss['certificates']]}
 result['original_failure_reproduced']=abs(max(result['default']['economic_errors_by_column'].values())-2.8919333594501495e-10)<1e-15
 ref=result['verification_only_KKT']
 result['supplemental_passed']=ref['weight_error']<1e-10 and max(ref['economic_errors_by_column'].values())<1e-10
 result['original_assertion_remains_failed']=True
 V.dump(a.work/'checks/permutation_diagnostic.json',result);print(json.dumps(result),flush=True)
 assert result['original_failure_reproduced'] and result['supplemental_passed']
if __name__=='__main__':main()
