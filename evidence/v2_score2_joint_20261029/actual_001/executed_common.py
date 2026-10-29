"""Prospective complete-scorer observation and immutable-source loading helpers."""
import ast
import csv
import hashlib
import importlib.util
import itertools
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

from forecast_reference import make_forecast
from reference_overlay import VolatilityOverlay

COMMIT = "ce3fe4e76271709422165d6f24e2fbecd9d0fe07"
SOURCE_HASHES = {
    "handoff_v2/strategy.py": "e8e7b96b70aab1ef05a1fcb4af7e02ab2df74484dc3ffdebb719b27acad153d3",
    "handoff_v2/model_v2/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "handoff_v2/model_v2/engine.py": "eedb367984ac1d3d36c8901236cdeceb2205d7e51bb5cd6ef9e85c466ae88fb8",
    "handoff_v2/model_v2/allocator.py": "70e744353440ec9daf57c4174cf61eb19144239bbba2a131e86abb5a3c395518",
    "source/Quant Research Take-Home/score.py": "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96",
}
SERIAL = itertools.count()
STAGES = {"full":(253,3779), "discovery":(253,2015),
          "validation":(2016,3023), "audit":(3024,3779)}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def array_sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def dump(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def module(name, path, package=False):
    spec = importlib.util.spec_from_file_location(name, path,
        submodule_search_locations=[str(Path(path).parent)] if package else None)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def prepare(snapshot, out):
    clean = out / "source"
    for rel, expected in SOURCE_HASHES.items():
        source = snapshot / rel
        if sha(source) != expected: raise RuntimeError("source mismatch: "+rel)
        target = clean / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    dump(out/"source_manifest.json", {"commit":COMMIT, "sha256":SOURCE_HASHES})
    for p in Path(__file__).parent.iterdir():
        if p.suffix == ".py" or p.name == "PLAN.md": shutil.copyfile(p, out/p.name)
    return clean


def engine(clean):
    folder = clean / "handoff_v2/model_v2"
    name = "score2_execution_engine_"+str(next(SERIAL))
    module(name, folder/"__init__.py", package=True)
    e = module(name+".engine", folder/"engine.py")
    assignments = ast.parse((clean/"handoff_v2/strategy.py").read_text()).body
    cfg = next(ast.literal_eval(n.value) for n in assignments if isinstance(n, ast.Assign)
               and any(isinstance(x, ast.Name) and x.id == "_CONFIG" for x in n.targets))
    e.configure(cfg)
    e.forecast = make_forecast(e, "F2")
    return e, dict(e.CONFIG)


def scorer(clean):
    return module("score2_original_scorer_"+str(next(SERIAL)),
                  clean/"source/Quant Research Take-Home/score.py")


def wrapper(clean, mode, factory=None, forecast_scale=1.0, record_arrays=True):
    e, cfg = engine(clean)
    if forecast_scale != 1:
        f = e.forecast
        def scaled_forecast(returns_history, characteristics_history):
            return forecast_scale*f(returns_history, characteristics_history)
        e.forecast = scaled_forecast
    if factory is None: return VolatilityOverlay(e,cfg,power=.5)
    actual = engine(clean)[0] if mode == "E2" else None
    return factory(e, cfg, mode=mode, actual_engine=actual,
                   record_arrays=record_arrays)


def fixture(n=64):
    rng = np.random.default_rng(20261028)
    T = 420
    X = np.zeros((T,n,13),dtype=np.float64)
    X[0] = rng.normal(size=(n,13))
    for t in range(1,T):
        X[t] = .92*X[t-1]+np.sqrt(1-.92**2)*rng.normal(size=(n,13))
    beta = rng.uniform(.7,1.3,n)
    market = .0003+.006*rng.normal(size=T)
    R = np.empty((T,n))
    for t in range(T):
        scale = .6 if t<330 else 2.
        z = X[max(0,t-1)]
        R[t] = beta*market[t]+.00008*z[:,0]+.00006*(z[:,1]**2-1) + scale*(
            .0015*z[:,2]*rng.normal()+.008*rng.normal(size=n))
    return np.ascontiguousarray(R),np.ascontiguousarray(X),np.linspace(.0001,.0005,n)


def execute(score, policy, R, X, costs):
    rows,fsec = score.run(policy,R,X,costs)
    targets = np.array([r["actual_target"] for r in policy.records])
    virtual = np.array([r["virtual_target"] for r in policy.records])
    meta = [{k:v for k,v in r.items() if k not in ("actual_target","virtual_target")}
            for r in policy.records]
    reconstructed=[]; held=[]; old=np.zeros(R.shape[1])
    for j,(rec,target) in enumerate(zip(meta,targets)):
        t=rec["decision_index"]; g=float(old@R[t])
        if g<=-1: raise RuntimeError("independent actual ruin")
        h=old*(1+R[t])/(1+g); held.append(h)
        fee=0.0 if j==0 else float(costs@np.abs(target-h))
        reconstructed.append([g,fee,float(np.abs(target).sum()),float(R[t].mean())])
        old=target
    err=float(np.max(np.abs(np.asarray(reconstructed)[1:]-rows[:,:4]),initial=0))
    return {"rows":rows,"forecast_seconds":fsec,"targets":targets,
        "virtual":virtual,"metadata":meta,"held":np.array(held),
        "forecast":policy.forecast_output.copy(),"accounting_max_error":err}


def atomic_array(path, a):
    tmp=path.with_name(path.name+".tmp")
    with tmp.open("wb") as f:
        np.save(f,a,allow_pickle=False); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)
    read=np.load(path,mmap_mode="r",allow_pickle=False)
    digest=array_sha(a)
    if read.shape!=a.shape or read.dtype!=a.dtype or array_sha(read)!=digest:
        raise RuntimeError("atomic array verification failed: "+str(path))
    return {"path":path.name,"shape":list(a.shape),"dtype":str(a.dtype),
            "array_sha256":digest,"file_sha256":sha(path),"verified":True}


def save_run(out,name,r,arrays=True):
    folder=out/name; folder.mkdir()
    with (folder/"daily.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["return_index","gross_return","full_cost",
            "net_return","closing_target_gross","market_return","instrumented_rebalance_seconds"])
        for t,(g,c,gross,m,sec) in zip(range(253,253+len(r["rows"])),r["rows"]):
            w.writerow([t,g,c,g-c,gross,m,sec])
    with (folder/"decisions.csv").open("w",newline="") as f:
        keys=list(dict.fromkeys(k for row in r["metadata"] for k in row))
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(r["metadata"])
    mapping={"targets.npy":r["targets"],"virtual_targets.npy":r["virtual"],
             "rows.npy":r["rows"],"forecast.npy":r["forecast"]}
    manifests={k:atomic_array(folder/k,a) if arrays else {
        "path":k,"shape":list(a.shape),"dtype":str(a.dtype),"array_sha256":array_sha(a),
        "saved":False} for k,a in mapping.items()}
    dump(folder/"verification.json",{"arrays":manifests,
        "accounting_max_error":r["accounting_max_error"],"opening_index":252,
        "first_earning_index":253,"final_decision_index":r["metadata"][-1]["decision_index"]})


def metrics(rows):
    day=np.arange(253,253+len(rows)); g,c,gross,m,sec=rows.T; out={}
    for name,(lo,hi) in STAGES.items():
        ix=(day>=lo)&(day<hi)
        if not ix.any(): continue
        net=(g-c)[ix]; market=m[ix]; mc=market-market.mean()
        out[name]={"n":int(ix.sum()),"net_sharpe":float(np.sqrt(252)*net.mean()/net.std()),
            "gross_sharpe":float(np.sqrt(252)*g[ix].mean()/g[ix].std()),
            "net_return_ann_pct":float(25200*net.mean()),
            "net_vol_ann_pct":float(100*np.sqrt(252)*net.std()),
            "cost_ann_pct":float(25200*c[ix].mean()),
            "net_beta":float(mc@(net-net.mean())/(mc@mc)),
            "mean_gross":float(gross[ix].mean()),"worst_gross_daily_return":float(g[ix].min())}
    return out
