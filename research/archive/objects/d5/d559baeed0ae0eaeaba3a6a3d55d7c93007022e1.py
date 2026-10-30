#!/usr/bin/env python3
"""Preimplementation independent references for the NEW exact gross solver."""
from __future__ import annotations
import argparse
import contextlib
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import time
import traceback

THREADS=("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS")
for key in THREADS:os.environ[key]="1"
import numpy as np
from scipy.optimize import Bounds,LinearConstraint,minimize


def now():return datetime.now(timezone.utc).isoformat()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def plain(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,dict):return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    return v
def save(p,v):Path(p).write_text(json.dumps(plain(v),indent=2,allow_nan=False)+"\n")
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod


def fixture(mu,held,var,beta,cost,gamma=1.,horizon=1.,cap=1.,gross=1.):
    return {"mu":np.asarray(mu,float),"held":np.asarray(held,float),"variance":np.asarray(var,float),
            "beta":np.asarray(beta,float),"costs":np.asarray(cost,float),"gamma":gamma,"horizon":horizon,
            "cap":np.asarray(cap,float),"gross":gross}


def objective(f,w):
    return float(.5*f["gamma"]*(f["variance"]@(w*w))-f["mu"]@w+(f["costs"]/f["horizon"])@np.abs(w-f["held"]))


def reference(f):
    n=len(f["mu"]);cap=np.broadcast_to(f["cap"],(n,));cost=f["costs"]/f["horizon"]
    scale=max(1e-6,float(np.abs(f["mu"])@cap+.5*f["gamma"]*(f["variance"]@(cap*cap))+cost@(cap+np.abs(f["held"]))))
    def fun(x):return float((.5*f["gamma"]*(f["variance"]@(x[:n]*x[:n]))-f["mu"]@x[:n]+cost@x[n:2*n])/scale)
    def jac(x):return np.concatenate((f["gamma"]*f["variance"]*x[:n]-f["mu"],cost,np.zeros(n)))/scale
    eye=np.eye(n);zero=np.zeros((n,n))
    matrix=np.block([[-eye,eye,zero],[eye,eye,zero],[-eye,zero,eye],[eye,zero,eye]])
    lower=np.concatenate((-f["held"],f["held"],np.zeros(2*n)))
    constraints=[LinearConstraint(matrix,lower,np.full(4*n,np.inf)),
        LinearConstraint(np.concatenate((np.zeros(2*n),np.ones(n)))[None],-np.inf,f["gross"])]
    if np.any(f["beta"]):constraints.append(LinearConstraint(np.concatenate((f["beta"],np.zeros(2*n)))[None],0.,0.))
    initial=np.concatenate((np.zeros(n),np.abs(f["held"]),np.zeros(n)))
    bounds=Bounds(np.concatenate((-cap,np.zeros(2*n))),np.concatenate((cap,np.full(2*n,np.inf))))
    result=minimize(fun,initial,jac=jac,bounds=bounds,constraints=constraints,method="SLSQP",
                    options={"ftol":1e-12,"maxiter":4000})
    w=result.x[:n]
    feasible=bool(np.max(np.abs(w)-cap)<=1e-8 and abs(f["beta"]@w)<=1e-8
        and np.abs(w).sum()<=f["gross"]+1e-8 and np.min(matrix@result.x-lower)>=-1e-8
        and result.x[2*n:].sum()<=f["gross"]+1e-8)
    return w,scale,{"success":bool(result.success),"feasible":feasible,"message":result.message,
                    "iterations":int(result.nit),"objective":objective(f,w)}


def make_fixtures():
    fixtures={};known={}
    base=fixture([.3,-.1],[0,0],[1,1],[1,1],[0,0],cap=1,gross=.1)
    fixtures["two_stock_active"]=base;known["two_stock_active"]=np.array([.05,-.05])
    fixtures["nonbinding"]={**base,"gross":10.}
    fixtures["zero_budget"]={**base,"gross":0.};known["zero_budget"]=np.zeros(2)
    fixtures["zero_caps"]={**base,"cap":np.zeros(2)};known["zero_caps"]=np.zeros(2)
    fixtures["zero_beta_l1_edge"]=fixture([2,1],[0,0],[1,1],[0,0],[0,0],cap=10,gross=1.)
    known["zero_beta_l1_edge"]=np.array([1.,0.])
    fixtures["no_trade"]=fixture([0,0],[.2,-.2],[1,1],[1,1],[.5,.5],gross=.6)
    known["no_trade"]=np.array([.2,-.2])
    fixtures["no_trade_binding"]={**fixtures["no_trade"],"gross":.2}
    known["no_trade_binding"]=np.array([.1,-.1])
    w=np.array([.1,-.1,.05,-.05]);beta=np.ones(4);var=np.array([1.,.8,1.3,.7]);gamma=2.
    mu=gamma*var*w+.1*beta+.3*np.sign(w)
    fixtures["four_stock_kkt"]=fixture(mu,[0]*4,var,beta,[0]*4,gamma=gamma,cap=.5,gross=.3)
    known["four_stock_kkt"]=w
    fixtures["outside_held"]=fixture([.4,-.1,.2],[.7,-.4,.3],[.5,1.,1.5],[1.,.8,1.2],[.1,.2,.1],cap=[.1,.2,.2],gross=.25)
    rng=np.random.default_rng(809714)
    for i in range(6):
        n=5+i;cap=rng.uniform(.1,.7,n);beta=rng.normal(1.,.9,n);cost=rng.uniform(.01,.4,n)
        if i==1:beta[:]=0.
        if i==2:cap[0]=0.
        if i==3:cost[:]=0.
        fixtures[f"reference_{i}"]=fixture(rng.normal(0,.9,n),rng.normal(0,.45,n),rng.uniform(.4,1.5,n),
            beta,cost,gamma=1.5,horizon=2.,cap=cap,gross=float(cap.sum()*(.12 if i<5 else 1.2)))
    n=1000;beta=rng.uniform(.4,1.8,n);w=rng.normal(0,1,n);w-=beta*(beta@w)/(beta@beta);w/=np.abs(w).sum()
    held=w-rng.choice([-1.,1.],n)*rng.uniform(.0002,.0008,n)
    var=rng.uniform(.0002,.0006,n);cost=rng.uniform(.0002,.0008,n);gamma=1000.;horizon=20.
    mu=gamma*var*w+cost/horizon*np.sign(w-held)+.0002*beta+.00005*np.sign(w)
    fixtures["known_1000"]=fixture(mu,held,var,beta,cost,gamma,horizon,.01,1.)
    known["known_1000"]=w
    return fixtures,known


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module",type=Path,required=True)
    parser.add_argument("--diagonal-module",type=Path,required=True)
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--oracle-only",action="store_true",help="Validate synthetic reference fixtures before implementation")
    args=parser.parse_args()
    args.module,args.diagonal_module,args.plan,args.out=[p.resolve() for p in (args.module,args.diagonal_module,args.plan,args.out)]
    out=args.out;out.mkdir(parents=True,exist_ok=False)
    summary={"status":"RUNNING","started_utc":now(),"checks":[],"market_rows_read":0,"oracle_only":args.oracle_only,
             "command":shlex.join([sys.executable,str(Path(__file__).resolve()),*sys.argv[1:]])}
    save(out/"summary.json",summary)
    shutil.copy2(__file__,out/"runner_used.py");shutil.copy2(args.plan,out/"expectations.md")
    shutil.copy2(args.diagonal_module,out/"portfolio.py")
    if args.module.exists():shutil.copy2(args.module,out/"gross_portfolio.py")
    rerun=[sys.executable,str(out/"runner_used.py"),"--module",str(out/"gross_portfolio.py"),"--diagonal-module",str(out/"portfolio.py"),
           "--plan",str(out/"expectations.md"),"--out",str(out)+"_rerun"]
    if args.oracle_only:rerun.append("--oracle-only")
    (out/"rerun.txt").write_text(shlex.join(rerun)+"\n");summary["rerun_command"]=shlex.join(rerun)
    fixtures,known=make_fixtures();save(out/"inputs.json",{"fixtures":fixtures,"known_optima":known})
    save(out/"identity.json",{"verifier_sha256":digest(out/"runner_used.py"),"plan_sha256":digest(out/"expectations.md"),
         "diagonal_sha256":digest(out/"portfolio.py"),"gross_sha256":digest(out/"gross_portfolio.py") if (out/"gross_portfolio.py").exists() else None})
    controls={"threads":{k:os.environ[k] for k in THREADS}}
    try:os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});controls["cpu_affinity"]=sorted(os.sched_getaffinity(0))
    except (OSError,AttributeError) as exc:controls["affinity_unavailable"]=str(exc)
    save(out/"environment.json",{"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),**controls})
    outputs={}
    def check(name,condition,actual):
        rec={"name":name,"status":"PASS" if condition else "FAIL","actual":actual};summary["checks"].append(rec)
        print(json.dumps(plain(rec),allow_nan=False),flush=True)
        if not condition:raise AssertionError(name)
    exit_code=1
    with (out/"stdout.log").open("w") as stdout,(out/"stderr.log").open("w") as stderr:
      with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
        try:
            if args.oracle_only:
                for name,f in fixtures.items():
                    if name.startswith("reference_") or name=="outside_held":
                        _,_,ref=reference(f);check(name+"_oracle",ref["success"] and ref["feasible"],ref)
                summary["status"]="ORACLE_FIXTURES_READY";exit_code=0
            else:
                if not (out/"gross_portfolio.py").is_file():
                    raise FileNotFoundError("New gross allocator absent: expected preimplementation red stage; numerical checks NOT RUN")
                sys.path.insert(0,str(out));module=load(out/"gross_portfolio.py","new_gross_solver");diagonal=load(out/"portfolio.py","existing_diagonal_reference")
                def invoke(f,**extra):
                    before={k:v.copy() for k,v in f.items() if isinstance(v,np.ndarray)}
                    w,info=module.allocate_gross(f["mu"],f["held"],f["variance"],f["beta"],f["costs"],f["gamma"],f["horizon"],f["cap"],f["gross"],**extra)
                    if not all(np.array_equal(f[k],v,equal_nan=True) for k,v in before.items()):raise AssertionError("Input mutation")
                    return np.asarray(w),info
                for name,f in fixtures.items():
                    w,info=invoke(f);n=len(f["mu"]);cap=np.broadcast_to(f["cap"],(n,));movable=cap>0
                    scale=float(np.max(np.abs(f["beta"][movable]))) if movable.any() else 0.;beta=np.zeros(n)
                    if scale:beta[movable]=f["beta"][movable]/scale
                    beta_error=float(abs(beta@w));gross_error=float(np.abs(w).sum()-f["gross"])
                    check(name+"_feasibility",w.shape==(n,) and np.isfinite(w).all() and np.max(np.abs(w)-cap)<=2e-12*max(1.,float(cap.max()))
                          and beta_error<=5e-11*max(1.,float(np.abs(beta)@cap)) and gross_error<=2e-11*max(1.,f["gross"]),
                          {"beta_error":beta_error,"gross_excess":gross_error,"box_excess":float(np.max(np.abs(w)-cap))})
                    check(name+"_convergence",bool(info["converged"]),info)
                    repeated,_=invoke(f);check(name+"_deterministic",np.array_equal(w,repeated),"exact repeated output; inputs unchanged")
                    outputs[name]={"weights":w,"diagnostics":info,"objective":objective(f,w)}
                    if name in known:
                        error=float(np.max(np.abs(w-known[name])));check(name+"_known_optimum",error<=(1e-8 if name=="known_1000" else 2e-9),error)
                    elif name=="nonbinding":
                        expected=diagonal.allocate(f["mu"],f["held"],f["variance"],f["beta"],f["costs"],f["gamma"],f["horizon"],f["cap"])
                        error=float(np.max(np.abs(w-expected)));check(name+"_reduction",error<=2e-9,error)
                    else:
                        rw,rscale,ref=reference(f);check(name+"_reference_valid",ref["success"] and ref["feasible"],ref)
                        error=abs(objective(f,w)-objective(f,rw))/rscale;check(name+"_objective",error<=5e-8,error);outputs[name]["reference"]=ref
                f=fixtures["reference_0"];negative={**f,"mu":-f["mu"],"held":-f["held"]}
                w,_=invoke(negative);error=float(np.max(np.abs(w+outputs["reference_0"]["weights"])));check("sign_reflection",error<=2e-9,error)
                permutation=np.array([2,4,0,3,1]);permuted={k:(v[permutation] if isinstance(v,np.ndarray) and v.ndim else v) for k,v in f.items()}
                w,_=invoke(permuted);error=float(np.max(np.abs(w-outputs["reference_0"]["weights"][permutation])));check("stock_permutation",error<=2e-9,error)
                bad=[];f=fixtures["two_stock_active"]
                for name,value in [("negative_gross",-1.),("nan_gross",float("nan")),("inf_gross",float("inf")),("vector_gross",np.ones(2))]:bad.append((name,{**f,"gross":value},{}))
                bad.extend([("negative_variance",{**f,"variance":np.array([-1.,1.])},{}),("negative_cost",{**f,"costs":np.array([-.1,.1])},{}),
                    ("bad_shape",{**f,"mu":np.zeros(3)},{}),("negative_cap",{**f,"cap":np.array(-1.)},{}),
                    ("zero_gamma",{**f,"gamma":0.},{}),("zero_horizon",{**f,"horizon":0.},{}),
                    ("zero_iterations",f,{"max_iterations":0}),("float_iterations",f,{"max_iterations":1.5})])
                for name,f,extra in bad:
                    rejected=False
                    try:invoke(f,**extra)
                    except ValueError:rejected=True
                    check("invalid_"+name,rejected,"ValueError required")
                times=[];f=fixtures["known_1000"]
                for _ in range(8):
                    tic=time.perf_counter();module.allocate_gross(f["mu"],f["held"],f["variance"],f["beta"],f["costs"],f["gamma"],f["horizon"],f["cap"],f["gross"]);times.append((time.perf_counter()-tic)*1000)
                timing={"calls":8,"milliseconds":times,"mean_ms":float(np.mean(times)),"p95_ms":float(np.quantile(times,.95)),"max_ms":max(times),"scope":"synthetic complete gross allocator only"}
                save(out/"timings.json",timing);check("one_core_runtime",timing["mean_ms"]<100,timing)
                summary["status"]="PASS_SCOPE_ONLY";exit_code=0
        except KeyboardInterrupt:
            summary["status"]="INCOMPLETE";exit_code=130;summary["error"]=traceback.format_exc();traceback.print_exc()
        except Exception:
            summary["status"]="FAIL";summary["error"]=traceback.format_exc();traceback.print_exc()
        finally:
            save(out/"actual_results.json",outputs);summary["finished_utc"]=now();summary["exit_code"]=exit_code;save(out/"summary.json",summary)
    print(f"{summary['status']}: {len(summary['checks'])} checks; exit {exit_code}; {out}");return exit_code


if __name__=="__main__":raise SystemExit(main())
