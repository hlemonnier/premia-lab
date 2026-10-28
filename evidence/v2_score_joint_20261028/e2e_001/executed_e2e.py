"""Prospective joint complete-scorer checks, written before joint.py. See PLAN.md."""
from joint import make_joint as VolatilityOverlay
from prototype import make_forecast

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

COMMIT = "ce3fe4e76271709422165d6f24e2fbecd9d0fe07"
FILES = ["handoff_v2/strategy.py", "handoff_v2/model_v2/__init__.py",
         "handoff_v2/model_v2/engine.py", "handoff_v2/model_v2/allocator.py",
         "source/Quant Research Take-Home/score.py"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def array_sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def load_baseline(snapshot, out):
    clean = out / "source"
    for rel in FILES:
        target = clean / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot / rel, target)
    ids = {rel: sha(clean / rel) for rel in FILES}
    dump(out / "source_manifest.json", {"commit": COMMIT, "sha256": ids})
    sys.path.insert(0, str(clean / "handoff_v2"))
    strategy = module("overlay_baseline_strategy", clean / "handoff_v2/strategy.py")
    engine = strategy._engine
    # Preserve all current defaults as well as the exact packaged overrides.
    config = dict(engine.CONFIG)
    engine.forecast = make_forecast(engine, "F2")
    scorer = module("overlay_original_scorer", clean / "source/Quant Research Take-Home/score.py")
    return engine, config, scorer, ids


def fixture():
    rng = np.random.default_rng(20261028)
    T, N = 420, 64
    X = np.zeros((T, N, 13), dtype=np.float64)
    X[0] = rng.normal(size=(N, 13))
    for t in range(1, T):
        X[t] = .92 * X[t-1] + np.sqrt(1-.92**2) * rng.normal(size=(N,13))
    beta = rng.uniform(.7, 1.3, size=N)
    market = .0003 + .006 * rng.normal(size=T)
    R = np.empty((T, N))
    for t in range(T):
        scale = .6 if t < 330 else 2.0
        z = X[max(0,t-1)]
        R[t] = (beta * market[t] + .00008*z[:,0] + .00006*(z[:,1]**2-1)
                + scale*(.0015*z[:,2]*rng.normal() + .008*rng.normal(size=N)))
    costs = np.linspace(.0001,.0005,N)
    return np.ascontiguousarray(R), np.ascontiguousarray(X), costs


def execute(scorer, wrapper, R, X, costs):
    rows, fsec = scorer.run(wrapper, R, X, costs)
    targets = np.asarray([r["actual_target"] for r in wrapper.records])
    virtual = np.asarray([r["virtual_target"] for r in wrapper.records])
    metadata = [{k:v for k,v in r.items() if k not in ("actual_target","virtual_target")}
                for r in wrapper.records]
    reconstructed = []
    old = np.zeros(R.shape[1])
    for j,(rec,target) in enumerate(zip(metadata,targets)):
        t = rec["decision_index"]
        g = float(old @ R[t])
        assert g > -1
        held = old*(1+R[t])/(1+g)
        fee = 0. if j == 0 else float(costs @ np.abs(target-held))
        reconstructed.append([g,fee,float(np.abs(target).sum()),float(R[t].mean())])
        old = target
    err = float(np.max(np.abs(np.asarray(reconstructed)[1:]-rows[:,:4])))
    return {"rows":rows,"forecast_seconds":fsec,"targets":targets,"virtual":virtual,
            "metadata":metadata,"accounting_max_error":err,
            "forecast":wrapper.forecast_output.copy(),
            "forecast_sha256":array_sha(wrapper.forecast_output)}


def save_run(out, name, result, save_arrays=True):
    folder = out / name
    folder.mkdir()
    with (folder / "daily.csv").open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["return_index","gross_return","full_cost","net_return",
                    "closing_target_gross","market_return","instrumented_rebalance_seconds"])
        for t,row in zip(range(253,253+len(result["rows"])),result["rows"]):
            g,c,gross,m,sec=row
            w.writerow([t,g,c,g-c,gross,m,sec])
    with (folder / "decisions.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result["metadata"][0]))
        w.writeheader(); w.writerows(result["metadata"])
    dump(folder / "array_hashes.json", {"forecast":result["forecast_sha256"],
        "actual_targets":array_sha(result["targets"]),"virtual_targets":array_sha(result["virtual"])})
    if save_arrays:
        np.savez_compressed(folder/"replay_arrays.npz",forecast=result["forecast"],
            actual_targets=result["targets"],virtual_targets=result["virtual"],rows=result["rows"])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__, args.out / "executed_e2e.py")
    shutil.copyfile(Path(__file__).with_name("overlay.py"), args.out / "executed_overlay.py")
    for source_name in ("prototype.py","joint.py"):
        shutil.copyfile(Path(__file__).with_name(source_name), args.out / ("executed_"+source_name))
    engine, config, scorer, identities=load_baseline(args.snapshot,args.out)
    R,X,cost=fixture()
    dump(args.out / "input_manifest.json", {"seed":20261028,"R_shape":list(R.shape),
        "X_shape":list(X.shape),"R_sha256":array_sha(R),"X_sha256":array_sha(X),
        "cost_sha256":array_sha(cost)})
    dump(args.out / "environment.json", {"python":sys.version,"numpy":np.__version__,
        "platform":platform.platform(),"argv":sys.argv,"config":config})
    checks={}
    engine.configure(config)
    direct_targets=[]
    direct_forecasts=[]
    def direct_forecast(returns_history,characteristics_history):
        p=engine.forecast(returns_history,characteristics_history)
        direct_forecasts.append(p.copy()); return p
    def direct_rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs):
        w=engine.rebalance(held_positions,expected_returns,returns_history,characteristics_history,trading_costs)
        direct_targets.append(w.copy()); return w
    direct, _ = scorer.run(SimpleNamespace(forecast=direct_forecast,rebalance=direct_rebalance),R,X,cost)
    fixed=VolatilityOverlay(engine,config,power=0.0)
    fixed_result=execute(scorer,fixed,R,X,cost)
    checks["fixed_one_economics"] = bool(np.max(np.abs(direct[:,:4]-fixed_result["rows"][:,:4]))<=1e-12)
    checks["fixed_one_actual_virtual"] = bool(np.array_equal(fixed_result["targets"],fixed_result["virtual"]))
    checks["fixed_one_direct_targets"] = bool(np.array_equal(fixed_result["targets"],np.asarray(direct_targets)))
    checks["fixed_one_direct_forecast"] = bool(np.array_equal(fixed_result["forecast"],direct_forecasts[0]))
    checks["fixed_one_accounting"] = fixed_result["accounting_max_error"]<=1e-12
    save_run(args.out,"fixed_one",fixed_result)
    for name,power in (("joint_F2_VTvol",.5),):
        wrapper=VolatilityOverlay(engine,config,power=power)
        base=execute(scorer,wrapper,R,X,cost)
        save_run(args.out,name,base)
        checks[name+"_same_virtual"] = bool(np.array_equal(base["virtual"],fixed_result["virtual"]))
        checks[name+"_same_forecast"] = bool(np.array_equal(base["forecast"],fixed_result["forecast"]))
        checks[name+"_accounting"] = base["accounting_max_error"]<=1e-12
        checks[name+"_finite"] = bool(np.isfinite(base["targets"]).all() and np.isfinite(base["rows"]).all())
        checks[name+"_bounds"] = all(.5<=r["multiplier"]<=2 and r["actual_gross"]<=5+1e-12 for r in base["metadata"])
        checks[name+"_certified"] = all(r["certificate_status"] in ("ok","ok_after_recovery") for r in base["metadata"])
        checks[name+"_startup"] = all(r["multiplier"]==1 for r in base["metadata"] if r["earned_observations"]<63)
        active=[r for r in base["metadata"] if r["earned_observations"]>=63]
        checks[name+"_active_at_63"] = active[0]["decision_index"]==315 and any(r["multiplier"]!=1 for r in active)
        # A current-close multiplier uses all observed base returns, including today's.
        acc={63:[0.,0.],1008:[0.,0.]}
        expected=[]
        for j,r in enumerate(base["metadata"]):
            if j:
                g=float(base["virtual"][j-1]@R[r["decision_index"]])
                for hl in acc:
                    decay=2**(-1/hl); acc[hl][0]=decay*acc[hl][0]+g*g; acc[hl][1]=decay*acc[hl][1]+1
            q={hl:acc[hl][0]/acc[hl][1] if acc[hl][1] else 0. for hl in acc}
            a=1. if j<63 else float(np.clip((max(q[1008],1e-12)/max(q[63],1e-12))**power,.5,2))
            expected.append(a)
        checks[name+"_moment_clock"] = bool(np.max(np.abs(np.asarray(expected)-[r["multiplier"] for r in base["metadata"]]))<=1e-14)
        cut=360
        R2=R.copy(); X2=X.copy()
        R2[cut:]=-.6*R2[cut:]+.0007
        X2[cut:]=np.flip(X2[cut:],axis=1)+.2
        mutated=execute(scorer,wrapper,R2,X2,cost)
        save_run(args.out,name+"_future_mutated",mutated)
        mask=np.asarray([r["decision_index"]<cut for r in base["metadata"]])
        checks[name+"_future_forecast"] = bool(np.array_equal(base["forecast"][:cut+1],mutated["forecast"][:cut+1]))
        checks[name+"_future_decisions"] = bool(np.array_equal(base["targets"][mask],mutated["targets"][mask]))
        checks[name+"_future_economics"] = bool(np.max(np.abs(base["rows"][:cut-253,:4]-mutated["rows"][:cut-253,:4]))<=1e-12)
        prefix=execute(scorer,wrapper,R[:cut+1],X[:cut+1],cost)
        save_run(args.out,name+"_prefix361",prefix)
        checks[name+"_prefix_forecast"] = bool(np.array_equal(base["forecast"][:cut+1],prefix["forecast"]))
        checks[name+"_prefix_decisions"] = bool(np.array_equal(base["targets"][:len(prefix["targets"])],prefix["targets"]))
        checks[name+"_prefix_economics"] = bool(np.max(np.abs(base["rows"][:len(prefix["rows"]),:4]-prefix["rows"][:,:4]))<=1e-12)
        again=execute(scorer,wrapper,R,X,cost)
        save_run(args.out,name+"_repeat_after_other_histories",again)
        checks[name+"_session_reset"] = bool(np.array_equal(base["targets"],again["targets"]))
    checks["source_unchanged"] = identities=={rel:sha(args.out/"source"/rel) for rel in FILES}
    result={"checks":checks,"all_passed":all(checks.values()),"fixture":"synthetic; not a performance claim",
            "fixed_one_accounting_max_error":fixed_result["accounting_max_error"]}
    dump(args.out/"result.json",result)
    dump(args.out/"artifact_manifest.json",{str(p.relative_to(args.out)):sha(p)
        for p in sorted(args.out.rglob("*")) if p.is_file() and "__pycache__" not in str(p)})
    print(json.dumps(result,indent=2))
    if not all(checks.values()): raise SystemExit(1)


if __name__=="__main__": main()
