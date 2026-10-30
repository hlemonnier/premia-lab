"""Prospective whole-scorer checks; created before execution.py."""
from execution import make_execution

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np

from common import (SOURCE_HASHES, array_sha, dump, execute, fixture,
                    prepare, save_run, scorer, sha, wrapper)


def independent_scalar_certificate(rec,v,h,costs):
    a=rec["multiplier"]; desired=rec["desired_multiplier"]
    k=200*max(rec["q63"],1e-12); gross=float(np.abs(v).sum())
    lo=.5; hi=min(2.,5/gross) if gross else 2.
    residual=a*v-h
    eps=16*np.finfo(float).eps*max(1.,float(np.abs(h).max(initial=0)),
                                  float(np.abs(a*v).max(initial=0)))
    zero=np.abs(residual)<=eps
    smooth=k*(a-desired)+float((costs[~zero]*v[~zero])@np.sign(residual[~zero]))/20
    width=float(costs[zero]@np.abs(v[zero]))/20
    left,right=smooth-width,smooth+width
    if a<=lo+1e-12: kkt=max(0.,-right)
    elif a>=hi-1e-12: kkt=max(0.,left)
    else: kkt=max(0.,left,-right)
    comparator=float(np.clip(desired,lo,hi))
    objective=.5*k*(a-desired)**2+float([redacted-email](a*v-h))/20
    reference=.5*k*(comparator-desired)**2+float([redacted-email](comparator*v-h))/20
    return kkt,objective-reference,max(lo-a,a-hi,0.)


def beta_from_history(R,t):
    W=R[max(0,t-251):t+1]; c=W-W.mean(axis=0)
    m=W.mean(axis=1); m=m-m.mean(); mv=float(m@m)
    return np.ones(R.shape[1]) if mv<=1e-12*len(W) else (m@c)/mv


def generic_checks(name,r,R,costs,checks):
    rows=r["rows"]; targets=r["targets"]; meta=r["metadata"]
    checks[name+": accounting"] = r["accounting_max_error"]<=1e-12
    checks[name+": finite"] = bool(np.isfinite(rows).all() and np.isfinite(targets).all())
    checks[name+": solvent"] = bool(np.min(rows[:,0],initial=0)>-1)
    checks[name+": gross"] = bool(np.max(np.abs(targets).sum(axis=1),initial=0)<=5+1e-10)
    checks[name+": stock bounds"] = bool(np.max(np.abs(targets),initial=0)<=.1+1e-10)
    exposure=[float(beta_from_history(R,m["decision_index"])@w) for m,w in zip(meta,targets)]
    checks[name+": raw beta constraint"] = max(map(abs,exposure),default=0)<=1e-9
    checks[name+": base certificates"] = all(m["certificate_status"] in
                                            ("ok","ok_after_recovery") for m in meta)
    checks[name+": startup"] = all(m["multiplier"]==1 for m in meta if m["earned_observations"]<63)
    checks[name+": first earned observation"] = meta[0]["earned_observations"]==0 and meta[1]["earned_observations"]==1
    checks[name+": endpoint"] = len(meta)==len(R)-253 and len(rows)==len(R)-254 and meta[-1]["decision_index"]==len(R)-2
    if name.startswith("E1"):
        certificates=[independent_scalar_certificate(m,v,h,costs)
                      for m,v,h in zip(meta,r["virtual"],r["held"]) if m["earned_observations"]>=63]
        checks[name+": independent scalar KKT"] = max((c[0] for c in certificates),default=0)<=1e-10
        checks[name+": scalar objective comparator"] = max((c[1] for c in certificates),default=0)<=1e-12
        checks[name+": scalar bounds"] = max((c[2] for c in certificates),default=0)<=1e-12
    if name.startswith("E2"):
        checks[name+": actual certificates"] = all(m["actual_certificate_status"] in
                                                 ("ok","ok_after_recovery") for m in meta)
        checks[name+": independent actual risk clock"] = all(m["actual_state_upto"]==m["decision_index"]+1 for m in meta)


def same_economics(a,b):
    return np.array_equal(a["rows"][:,:4],b["rows"][:,:4])


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--snapshot",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True); args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    clean=prepare(args.snapshot,args.out); score=scorer(clean)
    R,X,c=fixture(); checks={}; saved={}
    dump(args.out/"environment.json",{"python":sys.version,"numpy":np.__version__,
        "platform":platform.platform(),"argv":sys.argv,"numerical_tolerances":{
            "accounting":1e-12,"zero_cost_scaling":1e-8,"gross":1e-10,
            "raw_beta":1e-9,"scalar_KKT":1e-10,"scalar_comparator":1e-12}})
    dump(args.out/"input_manifest.json",{"seed":20261028,"R":array_sha(R),
        "X":array_sha(X),"costs":array_sha(c),"shapes":[list(R.shape),list(X.shape)]})

    def run(label,mode,R0=R,X0=X,cost0=c,policy=None,scale=1.):
        if policy is None: policy=wrapper(clean,mode,make_execution,forecast_scale=scale)
        r=execute(score,policy,R0,X0,cost0)
        generic_checks(label,r,R0,cost0,checks)
        save_run(args.out,label,r)
        saved[label]={"forecast":array_sha(r["forecast"]),"virtual":array_sha(r["virtual"]),
                      "targets":array_sha(r["targets"]),"accounting_error":r["accounting_max_error"]}
        return r,policy

    reference=execute(score,wrapper(clean,"baseline"),R,X,c)
    save_run(args.out,"direct_reference",reference)
    control,_=run("baseline","baseline")
    checks["direct reference forecasts exact"]=np.array_equal(reference["forecast"],control["forecast"])
    checks["direct reference targets exact"]=np.array_equal(reference["targets"],control["targets"])
    checks["direct reference economics exact"]=same_economics(reference,control)

    rng=np.random.default_rng(20261029)
    Rf=R.copy(order="C"); Xf=X.copy(order="C")
    Rf[360:]=rng.normal(0,.015,size=Rf[360:].shape)
    Xf[360:]=rng.normal(size=Xf[360:].shape)
    for mode in ("E1","E2"):
        base,p=run(mode,mode)
        checks[mode+": virtual identity exact"]=np.array_equal(base["virtual"],control["virtual"])
        checks[mode+": forecast identity exact"]=np.array_equal(base["forecast"],control["forecast"])
        future,_=run(mode+"_future",mode,Rf,Xf,c,policy=p)
        n_decisions=360-252; n_economic=360-253
        checks[mode+": future forecasts exact"]=np.array_equal(base["forecast"][:361],future["forecast"][:361])
        checks[mode+": future targets exact"]=np.array_equal(base["targets"][:n_decisions],future["targets"][:n_decisions])
        checks[mode+": future economics exact"]=np.array_equal(base["rows"][:n_economic,:4],future["rows"][:n_economic,:4])
        prefix,_=run(mode+"_prefix",mode,R[:361].copy(),X[:361].copy(),c,policy=p)
        checks[mode+": prefix forecasts exact"]=np.array_equal(base["forecast"][:361],prefix["forecast"])
        checks[mode+": prefix targets exact"]=np.array_equal(base["targets"][:len(prefix["targets"])],prefix["targets"])
        checks[mode+": prefix economics exact"]=np.array_equal(base["rows"][:len(prefix["rows"]),:4],prefix["rows"][:,:4])
        repeat,_=run(mode+"_repeat",mode,policy=p)
        checks[mode+": restart forecasts exact"]=np.array_equal(base["forecast"],repeat["forecast"])
        checks[mode+": restart targets exact"]=np.array_equal(base["targets"],repeat["targets"])
        checks[mode+": restart economics exact"]=same_economics(base,repeat)
        if mode=="E2":
            checks["E2: independent risk objects"]=p.engine._STATE is not p.actual_engine._STATE
            checks["E2: independent optimizer objects"]=p.engine._STATE.warm is not p.actual_engine._STATE.warm
        zero,_=run(mode+"_zero_returns",mode,np.zeros_like(R),X,c)
        checks[mode+": zero targets/economics"]=bool(np.count_nonzero(zero["targets"])==0 and np.count_nonzero(zero["rows"][:,:4])==0)
    zero_reference=execute(score,wrapper(clean,"baseline"),R,X,np.zeros_like(c))
    save_run(args.out,"zero_cost_reference",zero_reference)
    for mode in ("E1","E2"):
        z,_=run(mode+"_zero_cost",mode,R,X,np.zeros_like(c))
        dt=float(np.max(np.abs(z["targets"]-zero_reference["targets"])))
        de=float(np.max(np.abs(z["rows"][:,:4]-zero_reference["rows"][:,:4])))
        checks[mode+": zero-cost scaling targets"]=dt<=1e-8
        checks[mode+": zero-cost scaling economics"]=de<=1e-8
        saved[mode+"_zero_cost"]["reference_differences"]={"targets":dt,"economics":de}
    Re,Xe,ce=fixture(n=128)
    for mode in ("E1","E2"):
        ex,_=run(mode+"_extreme",mode,Re,Xe,ce,scale=100.)
        checks[mode+": stress reaches gross cap"]=bool(np.max(np.abs(ex["targets"]).sum(axis=1))>=5-1e-8)

    result={"all_passed":all(checks.values()),"checks":checks,"cases":saved,
            "source_hashes":SOURCE_HASHES,"source_files":{
                p.name:sha(p) for p in Path(__file__).parent.glob("*.py")},
            "long_history_gate":"not run by synthetic E2E"}
    dump(args.out/"result.json",result)
    dump(args.out/"artifact_manifest.json",{str(p.relative_to(args.out)):sha(p)
        for p in args.out.rglob("*") if p.is_file() and "__pycache__" not in str(p)})
    print(json.dumps(result,indent=2))
    if not result["all_passed"]: raise RuntimeError("prospective E2E failed")


if __name__=="__main__": main()
