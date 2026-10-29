"""Prospective optional 25,200-row runtime/state stress; not an alpha experiment."""
from execution import make_execution

import argparse
import os
import platform
import sys
from pathlib import Path

import numpy as np

from common import dump, prepare, scorer, sha, wrapper


def tile_to_mmap(source,path,length):
    out=np.lib.format.open_memmap(path,mode="w+",dtype=np.float64,
        shape=(length,)+source.shape[1:])
    for start in range(0,length,len(source)):
        n=min(len(source),length-start); out[start:start+n]=source[:n]
    out.flush(); del out
    return np.load(path,mmap_mode="r")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--snapshot",type=Path,required=True)
    ap.add_argument("--cache",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--mode",choices=("E1","E2"),required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    if any(os.environ.get(k)!="1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")):
        raise RuntimeError("runtime check requires declared one-core BLAS")
    clean=prepare(args.snapshot,args.out)
    R0=np.load(args.cache/"returns.npy",mmap_mode="r")
    X0=np.load(args.cache/"characteristics.npy",mmap_mode="r")
    costs=np.load(args.cache/"costs.npy",allow_pickle=False)
    dump(args.out/"input_manifest.json",{p.name:sha(p) for p in
        (args.cache/"returns.npy",args.cache/"characteristics.npy",args.cache/"costs.npy")})
    R=tile_to_mmap(R0,args.out/"runtime_returns.npy",25200)
    X=tile_to_mmap(X0,args.out/"runtime_characteristics.npy",25200)
    policy=wrapper(clean,args.mode,make_execution,record_arrays=False)
    rows,fsec=scorer(clean).run(policy,R,X,costs)
    checks={"25200_rows":len(R)==25200,"finite":bool(np.isfinite(rows).all()),
        "solvent":bool(np.min(rows[:,0])>-1),"gross":bool(np.max(rows[:,2])<=5+1e-10),
        "forecast_under_hour":fsec<3600,"mean_rebalance_under_100ms":float(rows[:,4].mean())<.1,
        "base_certificates":all(r["certificate_status"] in ("ok","ok_after_recovery") for r in policy.records),
        "actual_certificates":all(r.get("actual_certificate_status","not_applicable") in
            ("ok","ok_after_recovery","not_applicable") for r in policy.records),
        "stock_cap":all(r["max_abs_actual_weight"]<=.1+1e-10 for r in policy.records)}
    dump(args.out/"result.json",{"checks":checks,"all_passed":all(checks.values()),
        "mode":args.mode,"forecast_seconds":fsec,"rebalance_ms_mean":float(1000*rows[:,4].mean()),
        "rebalance_ms_p99":float(1000*np.quantile(rows[:,4],.99)),
        "rebalance_ms_max":float(1000*rows[:,4].max()),"earning_rows":len(rows),
        "policy_state_rows":len(policy.records),"source_commit":"ce3fe4e76271709422165d6f24e2fbecd9d0fe07",
        "python":sys.version,"platform":platform.platform(),"argv":sys.argv,
        "meaning":"runtime/state stress only; repeated historical data are not future alpha"})
    if not all(checks.values()): raise RuntimeError("runtime/state gate failed")


if __name__=="__main__": main()
