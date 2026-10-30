"""Run the two prospectively specified overlays through the unchanged scorer."""
import argparse
import json
import platform
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from overlay import VolatilityOverlay
from e2e import COMMIT, FILES, array_sha, dump, execute, load_baseline, save_run, sha

STAGES={"full":(253,3779),"discovery":(253,2015),
        "validation":(2016,3023),"audit":(3024,3779)}


def metrics(rows):
    day=np.arange(253,253+len(rows))
    g,c,gross,m,sec=rows.T
    out={}
    for name,(lo,hi) in STAGES.items():
        k=(day>=lo)&(day<hi); net=(g-c)[k]; market=m[k]
        mc=market-market.mean()
        out[name]={"n":int(k.sum()),"net_sharpe":float(np.sqrt(252)*net.mean()/net.std()),
            "gross_sharpe":float(np.sqrt(252)*g[k].mean()/g[k].std()),
            "net_return_ann_pct":float(25200*net.mean()),
            "net_vol_ann_pct":float(100*np.sqrt(252)*net.std()),
            "cost_ann_pct":float(25200*c[k].mean()),
            "net_beta":float(mc@(net-net.mean())/(mc@mc)),
            "mean_gross":float(gross[k].mean()),"worst_gross_daily_return":float(g[k].min())}
    return out


def paired_intervals(base,alt):
    n=len(base); answer={}
    point=float(np.sqrt(252)*(alt.mean()/alt.std()-base.mean()/base.std()))
    for length in (21,63,126):
        rng=np.random.default_rng(20261027)
        values=[]; blocks=(n+length-1)//length
        for _ in range(20):
            starts=rng.integers(0,n-length+1,size=(100,blocks))
            ix=(starts[:,:,None]+np.arange(length)).reshape(100,-1)[:,:n]
            a=alt[ix]; b=base[ix]
            values.extend((np.sqrt(252)*(a.mean(axis=1)/a.std(axis=1)-b.mean(axis=1)/b.std(axis=1))).tolist())
        lo,hi=np.quantile(values,[.025,.975])
        answer[str(length)]={"point":point,"lo":float(lo),"hi":float(hi),
            "draws":2000,"seed":20261027,"last_legal_block_start_included":True}
    return answer


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",type=Path,required=True)
    ap.add_argument("--data",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--e2e-result",type=Path,required=True)
    args=ap.parse_args()
    admitted=json.loads(args.e2e_result.read_text())
    if not admitted["all_passed"]: raise RuntimeError("synthetic E2E did not pass")
    for live,saved in (("e2e.py","executed_e2e.py"),("overlay.py","executed_overlay.py")):
        if sha(Path(__file__).with_name(live))!=sha(args.e2e_result.parent/saved):
            raise RuntimeError("E2E certificate belongs to different source: "+live)
    args.out.mkdir(parents=True,exist_ok=False)
    for name in ("run_pilot.py","overlay.py","e2e.py","PLAN.md"):
        shutil.copyfile(Path(__file__).with_name(name),args.out/name)
    engine,config,scorer,identities=load_baseline(args.snapshot,args.out)
    dump(args.out/"input_manifest.json",{name:{"path":str(args.data/name),"sha256":sha(args.data/name)}
        for name in ("returns.csv","characteristics.csv","costs.csv")})
    dump(args.out/"environment.json",{"python":sys.version,"numpy":np.__version__,"pandas":pd.__version__,
        "platform":platform.platform(),"argv":sys.argv,"baseline_configuration":config,
        "source_commit":COMMIT,"runtime_is_instrumented":True,
        "e2e_result_path":str(args.e2e_result),"e2e_result_sha256":sha(args.e2e_result)})
    R=np.ascontiguousarray(pd.read_csv(args.data/"returns.csv",index_col="day").to_numpy(np.float64))
    X=np.ascontiguousarray(pd.read_csv(args.data/"characteristics.csv",index_col=["day","stock"])
                          .to_numpy(np.float64).reshape(R.shape[0],R.shape[1],13))
    costs=pd.read_csv(args.data/"costs.csv",index_col="stock")["cost"].to_numpy(np.float64)
    assert R.shape==(3780,1000) and X.shape==(3780,1000,13)
    assert np.isfinite(R).all() and np.isfinite(X).all() and np.isfinite(costs).all()
    expected=np.load(args.snapshot/"research/v2/results/ledgers/net_fr_beta_phi03_x5.npy")
    results={}; net_series={}; base_hash=None; forecast_hash=None
    for name,power in (("fixed_one",0.0),("VTvol",.5),("VTvar",1.0)):
        wrapper=VolatilityOverlay(engine,config,power=power)
        replay=execute(scorer,wrapper,R,X,costs)
        save_run(args.out,name,replay,save_arrays=False)
        rows=replay["rows"]; meta=replay["metadata"]
        forecasts_equal=forecast_hash is None or replay["forecast_sha256"]==forecast_hash
        virtual_hash=array_sha(replay["virtual"])
        virtual_equal=base_hash is None or virtual_hash==base_hash
        if base_hash is None: base_hash=virtual_hash
        if forecast_hash is None: forecast_hash=replay["forecast_sha256"]
        mult=np.asarray([r["multiplier"] for r in meta])
        status={}
        for r in meta: status[r["certificate_status"]]=status.get(r["certificate_status"],0)+1
        p=metrics(rows)
        checks={"economic_rows":len(rows)==3526,"decision_rows":len(meta)==3527,
            "same_virtual_targets":virtual_equal,"same_forecasts":forecasts_equal,
            "actual_accounting":replay["accounting_max_error"]<=1e-12,
            "supplied_held_identity":max(r["supplied_held_identity_error"] for r in meta)<=1e-12,
            "finite":bool(np.isfinite(rows).all() and np.isfinite(replay["targets"]).all()),
            "final_gross":max(r["actual_gross"] for r in meta)<=5+1e-12,
            "certificates":all(k in ("ok","ok_after_recovery") for k in status),
            "startup":all(r["multiplier"]==1 for r in meta if r["earned_observations"]<63)}
        summary={"name":name,"power":power,"performance":p,"checks":checks,
            "virtual_targets_sha256":virtual_hash,"forecast_sha256":replay["forecast_sha256"],
            "forecast_seconds":replay["forecast_seconds"],
            "instrumented_rebalance_ms_mean":float(1000*rows[:,4].mean()),
            "instrumented_rebalance_ms_p99":float(1000*np.quantile(rows[:,4],.99)),
            "instrumented_rebalance_ms_max":float(1000*rows[:,4].max()),
            "multiplier_min_mean_max":[float(mult.min()),float(mult.mean()),float(mult.max())],
            "multiplier_low_clip_count":int(np.sum(mult==.5)),
            "multiplier_high_clip_count":int(np.sum(mult==2)),
            "aggregate_gross_cap_count":sum(r["aggregate_gross_scale"]<1 for r in meta),
            "max_actual_weight":max(r["max_abs_actual_weight"] for r in meta),
            "mean_net_dollars":float(np.mean([r["actual_net_dollars"] for r in meta])),
            "certificates":status,"accounting_max_error":replay["accounting_max_error"]}
        if name=="fixed_one":
            g,c,_,m,_=rows.T
            got=np.vstack((np.arange(253,3779),g-c,g,c,m))
            diff=np.max(np.abs(got-expected),axis=1)
            summary["baseline_committed_ledger_max_differences"]=diff.tolist()
            checks["baseline_reproduction"]=bool(np.all(diff<=1e-8))
        net_series[name]=rows[:,0]-rows[:,1]
        results[name]=summary
        dump(args.out/name/"summary.json",summary)
        print(json.dumps({"completed":name,"performance":p,"checks":checks,
            "multiplier_min_mean_max":summary["multiplier_min_mean_max"]}),flush=True)
        if not all(checks.values()): raise RuntimeError("actual replay check failed: "+name)
        del replay,wrapper
    for name in ("VTvol","VTvar"):
        s=results[name]
        s["paired_sharpe_intervals_vs_fixed_one"]=paired_intervals(net_series["fixed_one"],net_series[name])
        s["replacement_contender"]=(s["performance"]["full"]["net_sharpe"]>results["fixed_one"]["performance"]["full"]["net_sharpe"]+1e-8
            and abs(s["performance"]["full"]["net_beta"])<.2
            and s["instrumented_rebalance_ms_mean"]<100
            and s["performance"]["full"]["worst_gross_daily_return"]>-1
            and all(s["checks"].values()))
        dump(args.out/name/"summary.json",s)
    unchanged=identities=={rel:sha(args.out/"source"/rel) for rel in FILES}
    answer={"source_commit":COMMIT,"source_unchanged":unchanged,"all_periods_development":True,
        "synthetic_e2e_passed":admitted["all_passed"],"results":results,
        "long_history_runtime_gate":"not run in this pilot"}
    dump(args.out/"results.json",answer)
    dump(args.out/"artifact_manifest.json",{str(p.relative_to(args.out)):sha(p)
        for p in sorted(args.out.rglob("*")) if p.is_file() and "__pycache__" not in str(p)})
    print(json.dumps(answer,indent=2))
    if not unchanged: raise RuntimeError("source changed")


if __name__=="__main__": main()
