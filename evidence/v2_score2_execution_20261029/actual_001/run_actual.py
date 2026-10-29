"""Observe the two released execution policies under the unchanged original scorer."""
import argparse
import json
import os
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import (COMMIT, array_sha, dump, execute, metrics, prepare,
                    save_run, scorer, sha, wrapper)
from e2e import generic_checks
from execution import make_execution

INPUT_SHA={"returns.csv":"6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d",
 "characteristics.csv":"46b9df20aebb324bd0026090d54f04bd6835283881dd73e728e90f16a5279a08",
 "costs.csv":"ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186"}


def intervals(base,alt):
    n=len(base); result={}
    point=float(np.sqrt(252)*(alt.mean()/alt.std()-base.mean()/base.std()))
    for length in (21,63,126):
        rng=np.random.default_rng(20261027); values=[]; blocks=(n+length-1)//length
        for _ in range(20):
            starts=rng.integers(0,n-length+1,size=(100,blocks))
            ix=(starts[:,:,None]+np.arange(length)).reshape(100,-1)[:,:n]
            a=alt[ix]; b=base[ix]
            values.extend((np.sqrt(252)*(a.mean(axis=1)/a.std(axis=1)-b.mean(axis=1)/b.std(axis=1))).tolist())
        lo,hi=np.quantile(values,[.025,.975])
        result[str(length)]={"point":point,"lo":float(lo),"hi":float(hi),
            "draws":2000,"seed":20261027,"last_legal_block_start_included":True}
    return result


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--snapshot",type=Path,required=True)
    ap.add_argument("--data",type=Path,required=True); ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--e2e-result",type=Path,required=True)
    ap.add_argument("--reference-ledger",type=Path,required=True)
    ap.add_argument("--cache",type=Path)
    args=ap.parse_args()
    if any(os.environ.get(k)!="1" for k in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS")):
        raise RuntimeError("actual pilot requires declared one-core BLAS")
    gate=json.loads(args.e2e_result.read_text())
    if not gate["all_passed"]: raise RuntimeError("synthetic gate failed")
    for name,digest in gate["source_files"].items():
        if sha(Path(__file__).with_name(name))!=digest:
            raise RuntimeError("source differs from synthetic certificate: "+name)
    args.out.mkdir(parents=True,exist_ok=False)
    clean=prepare(args.snapshot,args.out); score=scorer(clean)
    data_manifest={name:{"path":str(args.data/name),"sha256":sha(args.data/name)} for name in INPUT_SHA}
    if any(data_manifest[k]["sha256"]!=v for k,v in INPUT_SHA.items()):
        raise RuntimeError("original input file identity mismatch")
    if args.cache:
        R=np.load(args.cache/"returns.npy",mmap_mode="r",allow_pickle=False)
        X=np.load(args.cache/"characteristics.npy",mmap_mode="r",allow_pickle=False)
        c=np.load(args.cache/"costs.npy",allow_pickle=False)
        cache_manifest=json.loads((args.cache/"manifest.json").read_text())
        for name,a in (("returns",R),("characteristics",X),("costs",c)):
            if array_sha(a)!=cache_manifest["arrays"][name]["array_sha256"]:
                raise RuntimeError("cache array identity mismatch: "+name)
        if cache_manifest["source_sha256"]!=INPUT_SHA:
            raise RuntimeError("cache input provenance mismatch")
        data_manifest["cache"]={"path":str(args.cache),"manifest_sha256":sha(args.cache/"manifest.json")}
    else:
        R=np.ascontiguousarray(pd.read_csv(args.data/"returns.csv",index_col="day").to_numpy(np.float64))
        X=np.ascontiguousarray(pd.read_csv(args.data/"characteristics.csv",index_col=["day","stock"])
                              .to_numpy(np.float64).reshape(R.shape[0],R.shape[1],13))
        c=pd.read_csv(args.data/"costs.csv",index_col="stock")["cost"].to_numpy(np.float64)
    if R.shape!=(3780,1000) or X.shape!=(3780,1000,13) or c.shape!=(1000,):
        raise RuntimeError("unexpected supplied data shape")
    if not all(np.isfinite(a).all() for a in (R,X,c)): raise RuntimeError("nonfinite input")
    data_manifest["array_sha256"]={"returns":array_sha(R),"characteristics":array_sha(X),"costs":array_sha(c)}
    dump(args.out/"input_manifest.json",data_manifest)
    dump(args.out/"environment.json",{"argv":sys.argv,"python":sys.version,
        "platform":platform.platform(),"numpy":np.__version__,"pandas":pd.__version__,
        "baseline_source":COMMIT,"e2e_result_sha256":sha(args.e2e_result),
        "reference_ledger_sha256":sha(args.reference_ledger),"runtime_is_instrumented":True})
    reference=pd.read_csv(args.reference_ledger)
    if not np.array_equal(reference["return_index"],np.arange(253,3779)):
        raise RuntimeError("wrong reference earning rows")
    ref_economics=reference[["gross_return","full_cost","closing_target_gross","market_return"]].to_numpy()
    ref_net=reference["net_return"].to_numpy()
    results={}; virtual_hash=None; forecast_hash=None
    for mode in ("baseline","E1","E2"):
        p=wrapper(clean,mode,make_execution)
        r=execute(score,p,R,X,c)
        checks={}; generic_checks(mode,r,R,c,checks)
        vhash=array_sha(r["virtual"]); fhash=array_sha(r["forecast"])
        if virtual_hash is None: virtual_hash=vhash; forecast_hash=fhash
        checks["virtual_same_as_baseline"]=vhash==virtual_hash
        checks["forecast_same_as_baseline"]=fhash==forecast_hash
        comparison=np.max(np.abs(r["rows"][:,:4]-ref_economics),axis=0)
        if mode=="baseline": checks["historical_economics_reproduced"]=bool(np.all(comparison<=1e-8))
        save_run(args.out,mode,r,arrays=True)
        perf=metrics(r["rows"]); rec=r["metadata"]
        a=np.array([x["multiplier"] for x in rec]); desired=np.array([x["desired_multiplier"] for x in rec])
        summary={"mode":mode,"performance":perf,"checks":checks,"all_checks_passed":all(checks.values()),
            "forecast_sha256":fhash,"virtual_targets_sha256":vhash,"actual_targets_sha256":array_sha(r["targets"]),
            "forecast_seconds":r["forecast_seconds"],
            "instrumented_rebalance_ms_mean":float(1000*r["rows"][:,4].mean()),
            "instrumented_rebalance_ms_p99":float(1000*np.quantile(r["rows"][:,4],.99)),
            "instrumented_rebalance_ms_max":float(1000*r["rows"][:,4].max()),
            "accounting_max_error":r["accounting_max_error"],
            "multiplier_min_mean_max":[float(a.min()),float(a.mean()),float(a.max())],
            "mean_absolute_desired_multiplier_deviation":float(np.mean(np.abs(a-desired))),
            "max_actual_weight":float(np.abs(r["targets"]).max()),
            "max_actual_gross":float(np.abs(r["targets"]).sum(axis=1).max()),
            "mean_net_dollars":float(r["targets"].sum(axis=1).mean()),
            "reference_economic_max_differences":comparison.tolist() if mode=="baseline" else None,
            "paired_sharpe_intervals":intervals(ref_net,r["rows"][:,0]-r["rows"][:,1])}
        summary["replacement_contender"]=(mode!="baseline" and summary["all_checks_passed"]
            and perf["full"]["net_sharpe"]>1.318334966090838+1e-8
            and abs(perf["full"]["net_beta"])<.2 and summary["instrumented_rebalance_ms_mean"]<100
            and r["forecast_seconds"]/len(R)*25200<3600)
        dump(args.out/mode/"summary.json",summary); results[mode]=summary
        dump(args.out/"results.json",{"results":results,"source_commit":COMMIT,
            "all_periods_development":True,"long_history_runtime_gate":"not run in actual pilot"})
        print(json.dumps({"completed":mode,"performance":perf,"checks":checks,
                          "replacement_contender":summary["replacement_contender"]}),flush=True)
        if not summary["all_checks_passed"]: raise RuntimeError("actual check failed: "+mode)
        del p,r
    dump(args.out/"artifact_manifest.json",{str(p.relative_to(args.out)):sha(p)
        for p in args.out.rglob("*") if p.is_file() and "__pycache__" not in str(p)})


if __name__=="__main__": main()
