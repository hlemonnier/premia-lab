#!/usr/bin/env python3
"""Discovery-only risk census; see research/RISK_DIAGNOSTICS_PLAN.md."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import traceback

for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"
sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda:handle.read(1<<20),b""):
            digest.update(block)
    return digest.hexdigest()


def decompose(r):
    m=r.mean(axis=1)
    mc=m-m.mean()
    centered=r-r.mean(axis=0)
    denominator=mc@mc
    if denominator <= 0:
        raise ValueError("Undefined market beta: zero market variance")
    beta=mc@centered/denominator
    residual=centered-mc[:,None]*beta
    return m,mc,beta,residual


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    root,out=args.project.resolve(),args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    code=Path(__file__).resolve()
    command=shlex.join([sys.executable,str(code),"--project",str(root),"--out",str(out)])
    rerun=shlex.join([sys.executable,str(out/"runner_used.py"),"--project",str(root),"--out",str(out)+"_rerun"])
    result={"status":"RUNNING","started_utc":datetime.now(timezone.utc).isoformat(),"command":command,
            "rerun_command":rerun,"data_slice":[0,2016],"candidate_configs_used":0,"checks":[]}
    (out/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    (out/"runner_used.py").write_bytes(code.read_bytes())
    (out/"expectations.md").write_bytes((root/"research/RISK_DIAGNOSTICS_PLAN.md").read_bytes())
    (out/"rerun.txt").write_text(rerun+"\n")
    log=[]
    def check(name,condition,actual):
        rec={"name":name,"status":"PASS" if bool(condition) else "FAIL","actual":actual}
        result["checks"].append(rec)
        log.append(json.dumps(rec))
        print(log[-1],flush=True)
        if not condition:raise AssertionError(name)
    exit_code=1
    try:
        cache=root/"cache/discovery"
        metadata=json.loads((cache/"metadata.json").read_text())
        check("scope",metadata["input_slice"]==[0,2016],metadata["input_slice"])
        input_hashes={name:sha256(cache/name) for name in ("returns.npy","costs.npy")}
        check("input_identity",all(input_hashes[n]==metadata["cache_sha256"][n] for n in input_hashes),input_hashes)
        r=np.load(cache/"returns.npy")
        costs=np.load(cache/"costs.npy")
        check("shape",r.shape==(2016,1000) and costs.shape==(1000,),{"returns":list(r.shape),"costs":list(costs.shape)})
        check("valid_values",np.isfinite(r).all() and np.isfinite(costs).all() and (costs>=0).all(),"finite returns/nonnegative costs")
        m,mc,beta,residual=decompose(r)
        check("residual_market_orthogonality",np.max(np.abs(mc@residual/len(r)))<1e-12,float(np.max(np.abs(mc@residual/len(r)))))
        check("residual_mean",np.max(np.abs(residual.mean(axis=0)))<1e-12,float(np.max(np.abs(residual.mean(axis=0)))))
        cov=residual.T@residual/len(r)
        check("covariance_symmetric",np.max(np.abs(cov-cov.T))<1e-12,float(np.max(np.abs(cov-cov.T))))
        eigenvalues=np.linalg.eigvalsh(cov)[::-1]
        check("positive_semidefinite",eigenvalues[-1]>=-1e-12,float(eigenvalues[-1]))
        vols=r.std(axis=0)
        residual_vol=residual.std(axis=0)
        corr=cov/np.maximum(residual_vol[:,None]*residual_vol[None,:],1e-20)
        offdiag=~np.eye(len(costs),dtype=bool)
        cov_shares={str(k):float(eigenvalues[:k].sum()/eigenvalues.sum()) for k in (1,3,5,10,20,50,100)}
        correlation_eigenvalues=np.linalg.eigvalsh(corr)[::-1]
        corr_shares={str(k):float(correlation_eigenvalues[:k].sum()/correlation_eigenvalues.sum()) for k in (1,3,5,10,20,50,100)}
        blocks=[]
        block_betas=[]
        for block in range(4):
            rows=r[504*block:504*(block+1)]
            bm,bmc,bb,br=decompose(rows)
            block_betas.append(bb)
            blocks.append({"block":block+1,"input_start":504*block,"input_end_exclusive":504*(block+1),
                           "market_annual_vol":float(bm.std()*np.sqrt(252)),"beta_mean":float(bb.mean()),
                           "beta_std":float(bb.std()),"beta_p05":float(np.quantile(bb,.05)),"beta_p95":float(np.quantile(bb,.95)),
                           "stock_vol_median":float(np.median(rows.std(axis=0))*np.sqrt(252)),
                           "residual_vol_median":float(np.median(br.std(axis=0))*np.sqrt(252))})
        pd.DataFrame(blocks).to_csv(out/"blocks.csv",index=False)
        stock=pd.DataFrame({"stock":metadata["stocks"],"cost":costs,"beta":beta,"daily_total_vol":vols,"daily_residual_vol":residual_vol})
        for k,b in enumerate(block_betas):stock[f"beta_block_{k+1}"]=b
        stock.to_csv(out/"stocks.csv",index=False)
        pd.DataFrame({"rank":np.arange(1,1001),"residual_covariance_eigenvalue":eigenvalues,
                      "residual_correlation_eigenvalue":correlation_eigenvalues}).to_csv(out/"spectrum.csv",index=False)
        quantities={"cost_bps":costs*10000,"stock_beta":beta,"stock_annual_vol":vols*np.sqrt(252),"residual_annual_vol":residual_vol*np.sqrt(252)}
        quantiles={name:{str(q):float(np.quantile(v,q)) for q in (0,.01,.1,.5,.9,.99,1)} for name,v in quantities.items()}
        stability=[{"blocks":[i+1,i+2],"pearson":float(np.corrcoef(block_betas[i],block_betas[i+1])[0,1]),
                    "median_abs_change":float(np.median(np.abs(block_betas[i+1]-block_betas[i])))} for i in range(3)]
        cost_relations={name:{"pearson":float(np.corrcoef(costs,v)[0,1]),"spearman":float(spearmanr(costs,v).statistic)}
                        for name,v in {"total_vol":vols,"residual_vol":residual_vol,"abs_beta":np.abs(beta)}.items()}
        result.update({"status":"PASS","input_sha256":input_hashes,"protocol_sha256":sha256(root/"RESEARCH_PROTOCOL.json"),
                       "runner_sha256":sha256(code),"quantiles":quantiles,"market_annual_vol":float(m.std()*np.sqrt(252)),
                       "residual_covariance_shares":cov_shares,"residual_correlation_shares":corr_shares,
                       "residual_offdiag_correlation_mean":float(corr[offdiag].mean()),
                       "residual_offdiag_abs_correlation_mean":float(np.abs(corr[offdiag]).mean()),
                       "beta_stability":stability,"cost_relationships":cost_relations,
                       "limits":"Pooled descriptive decomposition uses discovery data retrospectively. It is not a causal risk forecast or trading result."})
        (out/"environment.json").write_text(json.dumps({"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"pandas":pd.__version__},indent=2)+"\n")
        check("unchanged_inputs",all(sha256(cache/n)==h for n,h in input_hashes.items()),"hashes unchanged")
        exit_code=0
    except Exception:
        result["status"]="FAIL"
        result["traceback"]=traceback.format_exc()
        log.append(result["traceback"])
        print(result["traceback"],file=sys.stderr,flush=True)
    finally:
        result["exit_code"]=exit_code
        result["finished_utc"]=datetime.now(timezone.utc).isoformat()
        (out/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
        (out/"run.log").write_text("\n".join(log)+"\n")
    return exit_code


if __name__=="__main__":raise SystemExit(main())
