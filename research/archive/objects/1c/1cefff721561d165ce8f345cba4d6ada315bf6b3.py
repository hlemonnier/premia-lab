"""Portable paired-wave execution; original scorer, actual positions/costs.

--prepare runs the frozen reference and creates causal shared snapshots. All
candidate numerical routines also run without caches in the E2E workflow.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,sys,time,hashlib,platform
from pathlib import Path
from collections import Counter
from importlib.metadata import version
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from research.parallel10 import harness as H
from research.parallel10.models import make_policy
from research.parallel10.core import snapshots


def save_run(mode,policy,R,X,c,score,work,baseline=None):
    start=time.perf_counter();f,w,rows,sec,econ=H.exercise(policy,R,X,c,score)
    out=work/'runs'/mode;out.mkdir(parents=True,exist_ok=True)
    for name,arr in [('forecast',f),('targets',w),('rows',rows)]:np.save(out/f'{name}.npy',arr)
    result=H.summary(rows);result.update(mode=mode,forecast_seconds=sec,wall_seconds=time.perf_counter()-start,
        cashflow_error=float(np.max(np.abs(rows[:,:4]-econ))),certificates=dict(Counter(v['status'] for v in policy.certificates)),
        forecast_uses_shared_research_snapshots=baseline is not None)
    H.write_json(out/'summary.json',result)
    if hasattr(policy,'records'):H.write_json(out/'records.json',policy.records)
    print(json.dumps(result),flush=True)
    assert result['cashflow_error']<1e-10
    assert result['rebalance_ms']<100
    assert all(v['status']=='ok' for v in policy.certificates)
    return f,w,rows,result


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--work',required=True,type=Path)
    p.add_argument('--prepare',action='store_true');p.add_argument('--model');p.add_argument('--uncached',action='store_true')
    p.add_argument('--sleeve',type=float,default=.05);p.add_argument('--fees',type=float,default=1.);a=p.parse_args()
    score=H.load_score(a.source);R,X,c=H.load_data(a.source,a.work)
    if a.prepare:
        pol=make_policy('G');f,w,rows,stats=save_run('G',pol,R,X,c,score,a.work)
        ref=Path('/mnt/data/parallel_wave/prior/PeerLinks_Research/evidence/runs/G/rows.npy')
        error=float(np.max(np.abs(rows[:,:4]-np.load(ref)[:,:4]))) if ref.exists() else None
        H.write_json(a.work/'BASELINE.json',{'net_sharpe':stats['net_sharpe'],'expected':1.5332155606881952,'economic_row_error_vs_archive':error})
        assert abs(stats['net_sharpe']-1.5332155606881952)<1e-9
        if error is not None:assert error<1e-10
        start=time.perf_counter();S=snapshots(R,X,f,pol.cfg);folder=a.work/'shared';folder.mkdir(exist_ok=True)
        for name,arr in S.items():np.save(folder/f'{name}.npy',arr)
        H.write_json(folder/'manifest.json',{'scorer_sha256':H.sha256(a.source/'score.py'),'construction_seconds':time.perf_counter()-start,
            'python':platform.python_version(),'versions':{x:version(x) for x in ['numpy','scipy','scikit-learn','pandas']},'source_identity':json.loads((a.work/'inputs/source_identity.json').read_text()),
            'arrays':{name:{'shape':list(arr.shape),'sha256':H.sha256(folder/f'{name}.npy')} for name,arr in S.items()}})
        return
    shared=None if a.uncached else {f.stem:np.load(f,mmap_mode='r') for f in (a.work/'shared').glob('*.npy')}
    pol=make_policy(a.model,shared);pol.sleeve=a.sleeve;c=np.asarray(c)*a.fees
    name=a.model+('_nosleeve' if a.sleeve==0 else '')+(f'_fees{a.fees:g}' if a.fees!=1 else '')+('_uncached' if a.uncached else '')
    save_run(name,pol,R,X,c,score,a.work,shared)
if __name__=='__main__':main()
