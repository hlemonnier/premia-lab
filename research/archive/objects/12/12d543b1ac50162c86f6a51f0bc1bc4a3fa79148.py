"""Fresh-process original-scorer replays, with independent cashflow reconstruction."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research/common'))
import harness as H
from controls import ControlPolicy
from model_f.factor_risk import FactorPolicy
from research.gls.candidate import CandidatePolicy as Original


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--variant',required=True);ap.add_argument('--sleeve',type=float,default=.05);ap.add_argument('--fee',type=float,default=1.)
    ap.add_argument('--prior',type=Path);a=ap.parse_args()
    score=H.load_score(a.source);R,X,cost=H.load_data(a.source,a.work)
    p=FactorPolicy() if a.variant=='F' else Original() if a.variant=='GLS_original' else ControlPolicy(a.variant)
    p.sleeve=a.sleeve;cost=np.asarray(cost)*a.fee
    name=a.variant+('_nosleeve' if a.sleeve==0 else '')+(f'_fee{a.fee:g}' if a.fee!=1 else '')
    out=a.work/'runs'/name;out.mkdir(parents=True,exist_ok=True);tic=time.perf_counter()
    f,w,rows,secs,econ=H.exercise(p,R,X,cost,score)
    result=H.summary(rows);result.update(variant=a.variant,sleeve=a.sleeve,fee_multiplier=a.fee,
        forecast_seconds=secs,projected_forecast_hours_century=secs/len(R)*25200/3600,
        wall_seconds=time.perf_counter()-tic,cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),
        certificates=dict(Counter(c['status'] for c in p.certificates)))
    for k,v in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/f'{k}.npy',v)
    if hasattr(p,'learner_records'):H.write_json(out/'learner_records.json',p.learner_records)
    if a.prior:
        old=np.load(a.prior);result['prior_economic_max_abs_error']=float(np.max(np.abs(rows[:,:4]-old[:,:4])))
    if a.variant=='G_D' and a.sleeve==.05 and a.fee==1:
        other=a.work/'runs/GLS_original'
        result['generic_original_forecast_error']=float(np.max(np.abs(f-np.load(other/'forecast.npy'))))
        result['generic_original_weight_error']=float(np.max(np.abs(w-np.load(other/'targets.npy'))))
    H.write_json(out/'summary.json',result);print(json.dumps(result,indent=2),flush=True)
    assert result['cashflow_error']<=1e-10
    assert result['rebalance_ms']<100 and result['projected_forecast_hours_century']<1
    assert all(k in ('ok','ok_after_recovery','ok_after_cold_restart','fallback_diagonal') for k in result['certificates'])
    for k in ('prior_economic_max_abs_error','generic_original_forecast_error','generic_original_weight_error'):
        if k in result:assert result[k]<=1e-10,(k,result[k])
if __name__=='__main__':main()
