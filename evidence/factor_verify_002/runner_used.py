#!/usr/bin/env python3
"""Preimplementation numerical oracle for the NEW factor optimizer only."""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
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

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, minimize


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    return value


def save(path, value):
    Path(path).write_text(json.dumps(plain(value), indent=2, allow_nan=False) + "\n")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture(mu, held, diagonal, factors, beta, costs, gamma=1.0, horizon=1.0, cap=1.0):
    return {"mu": np.asarray(mu, dtype=float), "held": np.asarray(held, dtype=float),
            "diagonal": np.asarray(diagonal, dtype=float), "factors": np.asarray(factors, dtype=float),
            "beta": np.asarray(beta, dtype=float), "costs": np.asarray(costs, dtype=float),
            "gamma": gamma, "horizon": horizon, "cap": np.asarray(cap, dtype=float)}


def objective(f, w):
    return float(0.5 * f["gamma"] * (f["diagonal"] @ (w*w) + np.sum((f["factors"].T @ w)**2))
                 - f["mu"] @ w + (f["costs"] / f["horizon"]) @ np.abs(w-f["held"]))


def reference(f):
    n = len(f["mu"])
    cap = np.broadcast_to(f["cap"], (n,))
    covariance = np.diag(f["diagonal"]) + f["factors"] @ f["factors"].T
    costs = f["costs"] / f["horizon"]
    scale = max(1e-6, np.abs(f["mu"]) @ cap + 0.5*f["gamma"]*(f["diagonal"]@(cap*cap)
                + np.sum((np.abs(f["factors"]).T@cap)**2)) + costs@(cap+np.abs(f["held"])))

    def fun(x):
        w, z = x[:n], x[n:]
        return float((0.5*f["gamma"]*w@covariance@w - f["mu"]@w + costs@z)/scale)

    def jac(x):
        return np.concatenate((f["gamma"]*covariance@x[:n]-f["mu"], costs))/scale

    eye = np.eye(n)
    epigraph = np.block([[-eye, eye], [eye, eye]])
    lower = np.concatenate((-f["held"], f["held"]))
    constraints = [LinearConstraint(epigraph, lower, np.full(2*n, np.inf))]
    if np.any(f["beta"]):
        constraints.append(LinearConstraint(np.concatenate((f["beta"], np.zeros(n)))[None], 0., 0.))
    initial = np.concatenate((np.zeros(n), np.abs(f["held"])))
    bounds = Bounds(np.concatenate((-cap, np.zeros(n))), np.concatenate((cap, np.full(n, np.inf))))
    result = minimize(fun, initial, jac=jac, bounds=bounds, constraints=constraints,
                      method="SLSQP", options={"ftol": 1e-12, "maxiter": 3000})
    w = result.x[:n]
    feasible = bool(np.max(np.abs(w)-cap) <= 1e-8 and abs(f["beta"]@w) <= 1e-8
                    and np.min(epigraph@result.x-lower) >= -1e-8)
    return w, scale, {"success": bool(result.success), "feasible": feasible,
                     "message": result.message, "iterations": int(result.nit), "objective": objective(f,w)}


def make_fixtures():
    small = fixture([.3,-.2,.5,-.1,.15,.07], [0]*6, [.8,1.1,1.4,.6,1.7,.9],
                    [[.2,.1],[-.3,.05],[.4,-.1],[.1,.3],[-.2,.2],[.05,-.4]],
                    [1.,.8,1.3,-.2,0.,1.1], [0]*6, gamma=2., cap=10.)
    fixtures = {"analytic": small}
    fixtures["no_factors"] = {**small, "factors": np.zeros((6,0)), "costs": np.full(6,.02)}
    fixtures["zero_factors"] = {**fixtures["no_factors"], "factors": np.zeros((6,2))}
    fixtures["zero_betas"] = {**small, "beta": np.zeros(6)}
    fixtures["mixed_zero_caps"] = {**small, "beta": np.array([0.,1.,-1.,0.,.5,1.]),
                                  "cap": np.array([0.,.4,.3,.2,.1,.25]), "costs": np.full(6,.03)}
    held = np.array([.1,-.1])
    factors = np.array([[.2],[.3]])
    mu = held + factors@(factors.T@held)
    fixtures["no_trade"] = fixture(mu, held, [1.,1.], factors, [1.,1.], [10.,10.])
    rng = np.random.default_rng(74129)
    for i in range(6):
        n = 5+i
        factor = rng.normal(0,.35,(n,3))
        if i == 1:
            factor[:,2] = factor[:,0]
        beta = rng.normal(1.,.7,n)
        if i == 2:
            beta[:] = 0.
        cap = rng.uniform(.1,.7,n)
        if i == 3:
            cap[0] = 0.
        fixtures[f"reference_{i}"] = fixture(rng.normal(0,.7,n), rng.normal(0,.5,n),
             rng.uniform(.4,1.5,n), factor, beta, rng.uniform(.01,.3,n), gamma=1.7, horizon=2., cap=cap)
    n,k = 1000,10
    beta = rng.uniform(.4,1.8,n)
    known = rng.normal(0,.0008,n)
    known -= beta*(beta@known)/(beta@beta)
    held = known-rng.choice([-1.,1.],n)*rng.uniform(.0002,.001,n)
    diagonal = rng.uniform(.0002,.0006,n)
    factor = rng.normal(0,.003,(n,k))
    cost = rng.uniform(.0002,.0008,n)
    gamma,horizon = 1000.,20.
    mu = gamma*(diagonal*known+factor@(factor.T@known)) + cost/horizon*np.sign(known-held)+.0002*beta
    fixtures["known_1000"] = fixture(mu,held,diagonal,factor,beta,cost,gamma,horizon,.01)
    return fixtures, known


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--diagonal-module", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.module,args.diagonal_module,args.plan,args.out = [p.resolve() for p in
                                      (args.module,args.diagonal_module,args.plan,args.out)]
    out=args.out
    out.mkdir(parents=True,exist_ok=False)
    summary={"status":"RUNNING","started_utc":now(),"checks":[],"numeric_market_rows_read":0,
             "command":shlex.join([sys.executable,str(Path(__file__).resolve()),*sys.argv[1:]])}
    save(out/"summary.json",summary)
    shutil.copy2(__file__,out/"runner_used.py")
    shutil.copy2(args.plan,out/"expectations.md")
    shutil.copy2(args.diagonal_module,out/"portfolio.py")
    if args.module.exists():
        shutil.copy2(args.module,out/"factor_portfolio.py")
    rerun=[sys.executable,str(out/"runner_used.py"),"--module",str(out/"factor_portfolio.py"),
           "--diagonal-module",str(out/"portfolio.py"),"--plan",str(out/"expectations.md"),
           "--out",str(out)+"_rerun"]
    (out/"rerun.txt").write_text(shlex.join(rerun)+"\n")
    summary["rerun_command"]=shlex.join(rerun)
    fixtures,known = make_fixtures()
    save(out/"inputs.json",{"fixtures":fixtures,"known_1000_optimum":known})
    save(out/"identity.json",{"runner_sha256":digest(out/"runner_used.py"),
          "plan_sha256":digest(out/"expectations.md"),"diagonal_sha256":digest(out/"portfolio.py"),
          "factor_sha256":digest(out/"factor_portfolio.py") if (out/"factor_portfolio.py").exists() else None})
    controls={"threads":{k:os.environ[k] for k in THREADS}}
    try:
        os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
        controls["cpu_affinity"]=sorted(os.sched_getaffinity(0))
    except (AttributeError,OSError) as exc:
        controls["affinity_unavailable"]=str(exc)
    save(out/"environment.json",{"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),**controls})
    outputs={}
    def check(name,condition,actual):
        rec={"name":name,"status":"PASS" if condition else "FAIL","actual":actual}
        summary["checks"].append(rec)
        print(json.dumps(plain(rec),allow_nan=False),flush=True)
        if not condition:
            raise AssertionError(name)
    exit_code=1
    with (out/"stdout.log").open("w") as log, (out/"stderr.log").open("w") as errors:
      with contextlib.redirect_stdout(log), contextlib.redirect_stderr(errors):
        try:
            if not (out/"factor_portfolio.py").is_file():
                raise FileNotFoundError("New factor solver absent: expected preimplementation red stage; numerical checks NOT RUN")
            sys.path.insert(0,str(out))
            module=load_module(out/"factor_portfolio.py","factor_under_test")
            diagonal=load_module(out/"portfolio.py","diagonal_reference")
            def invoke(f,**extra):
                before={key:value.copy() for key,value in f.items() if isinstance(value,np.ndarray)}
                w,info=module.allocate_factor(f["mu"],f["held"],f["diagonal"],f["factors"],f["beta"],f["costs"],
                    f["gamma"],f["horizon"],f["cap"],**extra)
                if not all(np.array_equal(f[key],v,equal_nan=True) for key,v in before.items()):
                    raise AssertionError("Input mutation")
                return np.asarray(w),info
            for name,f in fixtures.items():
                w,info=invoke(f)
                n=len(w);cap=np.broadcast_to(f["cap"],(n,));movable=cap>0
                scale=float(np.max(np.abs(f["beta"][movable]))) if movable.any() else 0.
                beta=f["beta"]/scale if scale else np.zeros(n)
                exposure=float(abs(beta@w));btol=5e-11*max(1.,float(np.abs(beta)@cap))
                check(name+"_feasible", w.shape==(len(f["mu"]),) and np.isfinite(w).all()
                     and np.max(np.abs(w)-cap)<=2e-12*max(1.,float(cap.max())) and exposure<=btol,
                     {"beta_residual":exposure,"box_excess":float(np.max(np.abs(w)-cap))})
                check(name+"_converged",bool(info["converged"]) and np.isfinite(info["dual_gradient_inf"]),info)
                repeated,_=invoke(f)
                check(name+"_determinism",np.array_equal(w,repeated),"exact repeat; all inputs unchanged")
                outputs[name]={"weights":w,"diagnostics":info,"objective":objective(f,w)}
                if name in ("no_factors","zero_factors"):
                    expected=diagonal.allocate(f["mu"],f["held"],f["diagonal"],f["beta"],f["costs"],f["gamma"],f["horizon"],f["cap"])
                    error=float(np.max(np.abs(w-expected)))
                    check(name+"_reduction",error<=2e-9,error)
                elif name in ("analytic","zero_betas"):
                    matrix=f["gamma"]*(np.diag(f["diagonal"])+f["factors"]@f["factors"].T)
                    inverse_alpha=np.linalg.solve(matrix,f["mu"])
                    inverse_beta=np.linalg.solve(matrix,f["beta"])
                    expected=inverse_alpha-(inverse_beta*(f["beta"]@inverse_alpha)/(f["beta"]@inverse_beta) if np.any(f["beta"]) else 0.)
                    error=float(np.max(np.abs(w-expected)))
                    check(name+"_dense_kkt",error<=2e-9,error)
                elif name=="no_trade":
                    error=float(np.max(np.abs(w-f["held"])))
                    check(name+"_known_optimum",error<=2e-9,error)
                elif name=="known_1000":
                    error=float(np.max(np.abs(w-known)))
                    check(name+"_kkt",error<=1e-8,error)
                else:
                    rw,rscale,ref=reference(f)
                    check(name+"_reference_valid",ref["success"] and ref["feasible"],ref)
                    error=abs(objective(f,w)-objective(f,rw))/rscale
                    check(name+"_reference_objective",error<=5e-8,error)
                    outputs[name]["reference"]=ref
            original=fixtures["analytic"]
            for name,rotation in (("sign",np.diag([-1.,1.])),("orthogonal",np.array([[1.,1.],[-1.,1.]])/np.sqrt(2))):
                f={**original,"factors":original["factors"]@rotation}
                weights,info=invoke(f)
                error=float(np.max(np.abs(weights-outputs["analytic"]["weights"])))
                check(name+"_invariance",error<=2e-9,error)
            bad=[]
            f=fixtures["analytic"]
            bad.extend([("wrong_factor_rows",{**f,"factors":np.zeros((5,2))},{}),
                        ("factor_vector",{**f,"factors":np.zeros(6)},{}),
                        ("factor_nan",{**f,"factors":np.full((6,2),np.nan)},{}),
                        ("factor_inf",{**f,"factors":np.full((6,2),np.inf)},{}),
                        ("zero_diagonal",{**f,"diagonal":np.zeros(6)},{}),
                        ("negative_cost",{**f,"costs":np.full(6,-1.)},{}),
                        ("zero_gamma",{**f,"gamma":0.},{}),
                        ("zero_horizon",{**f,"horizon":0.},{}),
                        ("negative_cap",{**f,"cap":np.array(-1.)},{}),
                        ("zero_iterations",f,{"max_iterations":0}),
                        ("float_iterations",f,{"max_iterations":1.5})])
            for name,f,extra in bad:
                rejected=False
                try:invoke(f,**extra)
                except ValueError:rejected=True
                check("invalid_"+name,rejected,"ValueError required")
            timings=[]
            f=fixtures["known_1000"]
            for _ in range(8):
                tic=time.perf_counter()
                module.allocate_factor(f["mu"],f["held"],f["diagonal"],f["factors"],f["beta"],f["costs"],f["gamma"],f["horizon"],f["cap"])
                timings.append((time.perf_counter()-tic)*1000)
            timing={"calls":8,"milliseconds":timings,"mean_ms":float(np.mean(timings)),
                    "p95_ms":float(np.quantile(timings,.95)),"max_ms":float(max(timings)),"scope":"new factor solver synthetic calls only"}
            save(out/"timings.json",timing)
            check("single_core_runtime",timing["mean_ms"]<100,timing)
            summary["status"]="PASS_SCOPE_ONLY"
            exit_code=0
        except KeyboardInterrupt:
            summary["status"]="INCOMPLETE";exit_code=130
            summary["error"]=traceback.format_exc();traceback.print_exc()
        except Exception:
            summary["status"]="FAIL"
            summary["error"]=traceback.format_exc();traceback.print_exc()
        finally:
            save(out/"actual_results.json",outputs)
            summary["finished_utc"]=now();summary["exit_code"]=exit_code
            save(out/"summary.json",summary)
    print(f"{summary['status']}: {len(summary['checks'])} checks; exit {exit_code}; {out}")
    return exit_code


if __name__=="__main__":
    raise SystemExit(main())
