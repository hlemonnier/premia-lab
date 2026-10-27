#!/usr/bin/env python3
"""Read back one completed root-released C09 audit; never execute a model.

The prospective contract is verification/AUDIT_READBACK_PLAN.md.
The caller still needs root's explicit audit-completion/review release.
"""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
import platform
import shlex
import shutil
import sys
import traceback

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[name] = "1"
sys.dont_write_bytecode = True
import numpy as np

PLAN_SHA = "6384a9f41a2824c3c8c28f7a3ab9acab3efdf1ee4d8c18c9e17b44950d753c40"
CONFIG_SHA = "aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba"
SELECTION_SHA = "941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa"
CONTROLLER_SHA = "d3c3cfd4a1fde10398fc5546f3dc48d395f68a4c06fbe73311c8b5c2cdc37dfe"
HELPER_SHA = "6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69"
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
PROTOCOL_SHA = "cc2de53284feaeff97022c869ee8ee6e7b9fb40ab3f3dd1c0353e5b9923ed737"
PACKAGE_SHA = "97ec4469c51311730d906a68bd594ecd48b75d87bb29f0beccb6f7e3e5d8d813"
PACKAGE_RESULT_SHA = "095fa56f8b52758e504bfbdd035204a878a1dcda638d63a355f08c72353c423f"
VALIDATION_SUMMARY_SHA = "b1355fe15276e48ffff92194718df74469d6615e27a017b591e9ead28ee9d125"
VALIDATION_ARTIFACT_SHA = "c182454de2be9e01ad21a7de42cfaa98be0b33eaa812015889ba03e23998bd87"
CID = "C09_additive_long_memory"
FIELDS = ("gross_return", "full_cost", "closing_target_gross", "raw_market_return", "official_instrumented_rebalance_seconds")
ATOL, RTOL = 1e-14, 1e-12


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def local(root, relative):
    relative = Path(relative)
    path = (root / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root):
        raise ValueError("Manifest path escapes its frozen root")
    return path


def csv_rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def npy_sha(array):
    buffer = io.BytesIO()
    np.save(buffer, np.ascontiguousarray(array), allow_pickle=False)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("project", "packet", "nomination", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--nomination-sha256", required=True)
    parser.add_argument("--plan", type=Path)
    args = parser.parse_args()
    root, packet, nomination_path, out = (p.resolve() for p in (args.project,args.packet,args.nomination,args.out))
    out.mkdir(parents=True, exist_ok=False)
    result = {"status":"RUNNING", "started_utc":datetime.now(timezone.utc).isoformat(), "checks":[],
              "command":shlex.join([sys.executable,str(Path(__file__).resolve()),*sys.argv[1:]]),
              "scope":"Full saved single-policy audit replay reconciliation, including entire validation prefixes",
              "audit_numeric_read_started":False,"model_executions":0,"new_selection":False}
    logs, source_hashes, packet_hashes = [], {}, {}
    exit_code = 1

    def save():
        (out / "summary.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")

    def check(name, passed, actual=None):
        row = {"name":name,"status":"PASS" if bool(passed) else "FAIL","actual":actual}
        result["checks"].append(row)
        logs.append(json.dumps(row,allow_nan=False))
        if not passed:
            raise AssertionError(name)

    def compare(name, actual, expected, exact=False):
        actual, expected = np.asarray(actual), np.asarray(expected)
        same = actual.shape == expected.shape
        error = np.abs(actual-expected) if same else np.array([np.inf])
        passed = same and np.isfinite(actual).all() and np.isfinite(expected).all()
        passed = passed and (np.array_equal(actual,expected) if exact else np.all(error <= ATOL+RTOL*np.abs(expected)))
        check(name,passed,{"shape":list(actual.shape),"expected_shape":list(expected.shape),"exact_required":exact,
            "exact_observed":bool(same and np.array_equal(actual,expected)),"max_abs_error":float(error.max()) if error.size and np.isfinite(error).all() else None})

    save()
    try:
        plan = args.plan or root / "verification/AUDIT_READBACK_PLAN.md"
        check("prospective_plan_identity",sha(plan)==PLAN_SHA,sha(plan))
        check("root_nomination_identity",sha(nomination_path)==args.nomination_sha256,sha(nomination_path))
        nomination = read(nomination_path)
        check("single_selected_audit",nomination["schema_version"]==1 and nomination["status"]=="ROOT_APPROVED_PROTECTED_REPLAY"
              and nomination["stage"]=="audit" and nomination["selected_candidate_id"]==CID
              and len(nomination["candidates"])==1 and nomination["candidates"][0]["candidate_id"]==CID,CID)
        item = nomination["candidates"][0]
        check("nomination_control_identities",nomination["controller_sha256"]==CONTROLLER_SHA
              and nomination["scorer_sha256"]==SCORER_SHA and nomination["protocol_sha256"]==PROTOCOL_SHA
              and nomination["metric_helper_sha256"]==HELPER_SHA and nomination["audit_readback_plan_sha256"]==PLAN_SHA
              and item["config_sha256"]==CONFIG_SHA,True)
        selection_path = local(root,nomination["selection_record"]["path"])
        check("selection_binding",sha(selection_path)==nomination["selection_record"]["sha256"]==SELECTION_SHA,sha(selection_path))
        selection = read(selection_path)
        check("selected_configuration",selection["selected_candidate_id"]==CID and selection["config_sha256"]==CONFIG_SHA,CID)
        binding = nomination["package_binding"]
        package_path = local(root,binding["manifest_path"])
        package_result_path = local(root,binding["discovery_equivalence_summary_path"])
        check("frozen_package_binding",sha(package_path)==binding["manifest_sha256"]==nomination["handoff_package_manifest_sha256"]==PACKAGE_SHA,sha(package_path))
        check("package_discovery_evidence_binding",sha(package_result_path)==binding["discovery_equivalence_summary_sha256"]==PACKAGE_RESULT_SHA,sha(package_result_path))
        package, package_result = read(package_path),read(package_result_path)
        check("package_policy_identity",package["schema_version"]==1 and package["status"]=="DISCOVERY_VERIFIED_PACKAGE"
              and package["candidate_id"]==CID and package["config_sha256"]==CONFIG_SHA and package["selection_sha256"]==SELECTION_SHA
              and package["engine_module"]=="strategy",package["files"])
        check("completed_package_discovery",package_result["status"]=="EXECUTED_PASS_SCOPE_ONLY" and package_result["exit_code"]==0
              and package_result["stage"]=="discovery" and package_result["configuration"]["candidate_id"]==CID
              and all(c["status"]=="PASS" for c in package_result["checks"]),package_result["status"])
        check("exact_minimal_package",set(package["files"])=={"strategy.py","model/__init__.py","model/strategy.py","model/portfolio.py"}
              and {str(p.relative_to(root/"handoff")) for p in (root/"handoff").rglob("*") if p.is_file()}==set(package["files"]),sorted(package["files"]))
        for relative,digest in package["files"].items():
            check("package_file:"+relative,sha(local(root/"handoff",relative))==digest,digest)
        check("package_engine_dependency_bytes",package["files"]["model/strategy.py"]==item["source_sha256"]["submission/strategy.py"]
              and package["files"]["model/portfolio.py"]==item["source_sha256"]["submission/portfolio.py"]
              and package["files"]["model/__init__.py"]==hashlib.sha256(b"").hexdigest(),True)
        for e in item["evidence"]:
            p=local(root,e["path"])
            check("engineering_identity:"+e["path"],sha(p)==e["sha256"],e["sha256"])
            if "status" in e:
                s=read(p)
                check("engineering_status:"+e["path"],s["status"]==e["status"] and s["exit_code"]==0,s["status"])
        expected_copies={"reviewer_used.py":sha(__file__),"expectations.md":PLAN_SHA,"nomination_used.json":args.nomination_sha256,
            "selection_used.json":SELECTION_SHA,"package_manifest_used.json":PACKAGE_SHA,
            "package_discovery_summary_used.json":PACKAGE_RESULT_SHA,"metric_helper_used.py":HELPER_SHA}
        for source,name in ((Path(__file__),"reviewer_used.py"),(plan,"expectations.md"),(nomination_path,"nomination_used.json"),
                            (selection_path,"selection_used.json"),(package_path,"package_manifest_used.json"),
                            (package_result_path,"package_discovery_summary_used.json"),(root/"tools/run_candidate.py","metric_helper_used.py")):
            shutil.copy2(source,out/name)
            source_hashes[name]=sha(out/name)
            check("frozen_review_copy:"+name,source_hashes[name]==expected_copies[name],source_hashes[name])
        check("metric_helper_identity",source_hashes["metric_helper_used.py"]==HELPER_SHA,HELPER_SHA)
        spec=importlib.util.spec_from_file_location("audit_readback_metrics",out/"metric_helper_used.py")
        helper=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=helper
        spec.loader.exec_module(helper)
        result["environment"]={"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),"pid":os.getpid(),
            "thread_environment":{k:os.environ[k] for k in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")}}
        result["audit_numeric_read_started"]=True
        save()
        state,artifacts=read(packet/"summary.json"),read(packet/"artifact_manifest.json")
        packet_hashes={"summary.json":sha(packet/"summary.json"),"artifact_manifest.json":sha(packet/"artifact_manifest.json")}
        check("complete_canonical_audit",state["status"]=="EXECUTED_PASS_SCOPE_ONLY" and state["exit_code"]==0
              and state["mode"]=="audit" and state["completed_rebalances"]==3527 and state["returned_by_official_scorer"]
              and state["protected_numeric_access_started"] and state["validation_opened"] and state["audit_opened"],state["status"])
        check("reported_controller_checks",bool(state["checks"]) and all(c["status"]=="PASS" for c in state["checks"]),len(state["checks"]))
        for relative,entry in artifacts.items():
            p=local(packet,relative)
            check("artifact:"+relative,p.stat().st_size==entry["bytes"] and sha(p)==entry["sha256"],entry["sha256"])
        check("copied_nomination_selection",sha(packet/"nomination_used.json")==args.nomination_sha256
              and sha(packet/"selection_used.json")==SELECTION_SHA,True)
        source_map,inputs,config=(read(packet/name) for name in ("source_manifest.json","input_manifest.json","config.json"))
        check("canonical_configuration",sha(packet/"config.json")==CONFIG_SHA and config==state["configuration"]==package_result["configuration"],config)
        check("canonical_candidate_closure",{k:v for k,v in source_map.items() if k.startswith("source/candidate/")}
              =={"source/candidate/"+Path(k).name:v for k,v in item["source_sha256"].items()},True)
        for relative,digest in source_map.items():
            check("source:"+relative,sha(local(packet,relative))==digest,digest)
        check("canonical_source_controls",source_map["runner_used.py"]==CONTROLLER_SHA and source_map["source/score.py"]==SCORER_SHA
              and source_map["protocol_used.json"]==PROTOCOL_SHA and source_map["metric_helper_used.py"]==HELPER_SHA,True)
        check("audit_input_scope",inputs["kind"]=="canonical_market" and inputs["input_slice"]==[0,3780],inputs["input_slice"])
        input_names=("returns.npy","characteristics.npy","costs.npy")
        input_hashes={n:sha(packet/"inputs"/n) for n in input_names}
        check("complete_input_identities",input_hashes==state["input_hashes_after"]=={k:v["sha256"] for k,v in inputs["files"].items()},input_hashes)
        r,x,costs=(np.load(packet/"inputs"/n,mmap_mode="r",allow_pickle=False) for n in input_names)
        f,t,h,latency=(np.load(packet/n,mmap_mode="r",allow_pickle=False) for n in ("forecasts.npy","targets.npy","held_books.npy","candidate_rebalance_seconds.npy"))
        arrays=(r,x,costs,f,t,h,latency)
        check("complete_shapes_and_values",[a.shape for a in arrays]==[(3780,1000),(3780,1000,13),(1000,),(3780,1000),(3527,1000),(3527,1000),(3527,)]
              and all(a.dtype==np.float64 and np.isfinite(a).all() for a in arrays) and np.all(costs>=0) and np.all(latency>=0),[list(a.shape) for a in arrays])
        check("canonical_layout",r.flags.f_contiguous and not r.flags.c_contiguous and x.flags.c_contiguous,[list(r.strides),list(x.strides)])
        daily,records=csv_rows(packet/"daily.csv"),csv_rows(packet/"targets.csv")
        indices=np.array([int(row["return_index"]) for row in daily])
        rows=np.array([[float(row[k]) for k in FIELDS] for row in daily])
        net=np.array([float(row["net_return"]) for row in daily])
        check("complete_indices",np.array_equal(indices,np.arange(253,3779)) and [int(row["earning_index"]) for row in records]==list(range(253,3780))
              and all(int(row["csv_day_label"])==i+1 for i,row in zip(indices,daily)),{"daily":len(daily),"targets":len(records)})
        check("finite_economics",rows.shape==(3526,5) and np.isfinite(rows).all() and np.isfinite(net).all() and np.all(rows[:,1]>=0),True)
        compare("exact_net_identity",net,rows[:,0]-rows[:,1],True)
        gross=np.einsum("ij,ij->i",t[:-1],r[indices])
        drift=t[:-1]*(1+r[indices])/(1+gross[:,None])
        compare("full_gross",rows[:,0],gross)
        compare("full_drift",h[1:],drift)
        compare("full_fees",rows[:,1],np.abs(t[1:]-drift)@costs)
        compare("full_market",rows[:,3],r[indices].mean(axis=1))
        compare("full_exposure",rows[:,2],np.abs(t[1:]).sum(axis=1))
        compare("target_csv_latency",[float(row["candidate_rebalance_seconds"]) for row in records],latency,True)
        compare("target_csv_costs",[float(row["full_trade_cost"]) for row in records],np.abs(t-h)@costs)
        compare("target_csv_exposure",[float(row["target_gross"]) for row in records],np.abs(t).sum(axis=1))
        check("single_empty_opening",np.count_nonzero(h[0])==0 and float(records[0]["full_trade_cost"])==state["trading"]["opening_full_cost_waived"],state["trading"]["opening_full_cost_waived"])
        check("full_path_controls",float(np.abs(t).max())<=config["weight_cap"]+1e-12 and float(np.abs(t).sum(axis=1).max())<=config["gross_cap"]+1e-12
              and np.all(rows[:,0]>-1) and np.all(net>-1),{"maximum_stock":float(np.abs(t).max()),"maximum_gross":float(np.abs(t).sum(axis=1).max()),"minimum_net":float(net.min())})
        validation=root/"evidence/validation_C09_001"
        check("frozen_validation_reference",sha(validation/"summary.json")==VALIDATION_SUMMARY_SHA
              and sha(validation/"artifact_manifest.json")==VALIDATION_ARTIFACT_SHA,VALIDATION_SUMMARY_SHA)
        validation_state,validation_artifacts=read(validation/"summary.json"),read(validation/"artifact_manifest.json")
        check("completed_validation_reference",validation_state["status"]=="EXECUTED_PASS_SCOPE_ONLY" and validation_state["exit_code"]==0
              and validation_state["mode"]=="validation" and validation_state["configuration"]==config,True)
        for name,panel in zip(input_names,(r[:3024],x[:3024],costs)):
            path=validation/"inputs"/name
            check("validation_input_identity:"+name,sha(path)==validation_artifacts["inputs/"+name]["sha256"],sha(path))
            compare("entire_validation_input_prefix:"+name,panel,np.load(path,mmap_mode="r",allow_pickle=False),True)
            cache=root/"cache/discovery"/name
            check("original_discovery_input_identity:"+name,sha(cache)==helper.CACHE_SHA256[name],helper.CACHE_SHA256[name])
            compare("original_discovery_input_prefix:"+name,panel[:2016] if name!="costs.npy" else panel,np.load(cache,mmap_mode="r",allow_pickle=False),True)
        original=root/item["discovery_reference"]
        for name,digest in item["discovery_reference_sha256"].items():
            check("original_reference:"+name,sha(original/name)==digest and sha(packet/"reference"/name)==digest,digest)
        original_state=read(original/"summary.json")
        for name,array,validation_count,discovery_count in (("forecasts.npy",f,3024,2016),("targets.npy",t,2771,1763),("held_books.npy",h,2771,1763)):
            validation_digest=npy_sha(array[:validation_count])
            check("entire_validation_array_prefix:"+name,validation_digest==validation_state["output_arrays"][name]["sha256"],validation_digest)
            discovery_digest=npy_sha(array[:discovery_count])
            check("original_discovery_array_prefix:"+name,discovery_digest==original_state["output_arrays"][name]["sha256"],discovery_digest)
        check("validation_ledger_identity",sha(validation/"daily.csv")==validation_artifacts["daily.csv"]["sha256"],sha(validation/"daily.csv"))
        for label,folder,count in (("entire_validation",validation,2770),("original_discovery",original,1762)):
            prior=csv_rows(folder/"daily.csv")
            check(label+":prior_indices",[int(row["return_index"]) for row in prior]==list(range(253,253+count)),len(prior))
            compare(label+":exact_economics",rows[:count,:4],np.array([[float(row[k]) for k in FIELDS[:4]] for row in prior]),True)
            compare(label+":exact_net",net[:count],[float(row["net_return"]) for row in prior],True)
        mask=(indices>=3024)&(indices<3779)
        check("fixed_audit_mask",np.array_equal(indices[mask],np.arange(3024,3779)) and state["score_masks"]=={"locked_audit":[3024,3779]},int(mask.sum()))
        metrics=helper.summarize_rows(rows[mask],indices[mask])
        check("all_reported_audit_metrics",metrics==state["metrics"]["locked_audit"],metrics)
        y,market=net[mask],rows[mask,3]
        ym,mm=float(y.mean()),float(market.mean())
        variance,market_ss=float(np.mean((y-ym)**2)),float(np.sum((market-mm)**2))
        independent={"annual_arithmetic_net_return":252*ym,"annual_net_volatility":math.sqrt(252*variance),
            "net_sharpe":math.sqrt(252)*ym/math.sqrt(variance) if variance else None,
            "realized_net_market_beta":float(np.sum((market-mm)*(y-ym))/market_ss) if market_ss else None}
        wealth=np.concatenate(([1.0],np.cumprod(1+y)))
        independent["max_drawdown"]=float(np.max(1-wealth/np.maximum.accumulate(wealth)))
        for key,value in independent.items():
            if value is None:
                check("undefined_metric:"+key,metrics[key] is None,None)
            else:
                compare("independent_metric:"+key,[value],[metrics[key]])
        mean_ms=float((latency*1000).mean())
        compare("exact_mean_candidate_latency",[mean_ms],[state["timing"]["mean_candidate_rebalance_ms"]],True)
        compare("exact_max_candidate_latency",[float(latency.max()*1000)],[state["timing"]["max_candidate_rebalance_ms"]],True)
        beta=metrics["realized_net_market_beta"]
        beta_ok=beta is not None and math.isfinite(beta) and abs(beta)<.2
        runtime_ok=mean_ms<100
        check("reported_audit_conditions",state["candidate_feasibility"]["scope"]=="audit"
              and state["candidate_feasibility"]["realized_abs_beta_below_0_2"]==beta_ok
              and state["candidate_feasibility"]["candidate_mean_rebalance_below_100ms"]==runtime_ok
              and state["candidate_feasibility"]["net_solvency"] and state["candidate_feasibility"]["position_controls"],state["candidate_feasibility"])
        result["metrics"]=metrics
        result["candidate_runtime"]=state["timing"]
        result["audit_conditions"]={"absolute_beta_below_0_2":beta_ok,"mean_candidate_rebalance_below_100ms":runtime_ok,"finite_and_path_controls":True}
        result["selected_candidate_id"]=CID
        result["audit_input_slice"]=[0,3780]
        result["audit_score_slice"]=[3024,3779]
        check("consumed_review_sources_unchanged",all(sha(out/name)==digest for name,digest in source_hashes.items()),len(source_hashes))
        result["status"],exit_code="EXECUTED_PASS_SCOPE_ONLY",0
    except Exception:
        result["status"]="EXECUTED_FAIL_OR_INCOMPLETE"
        result["error"]=traceback.format_exc()
    finally:
        result["exit_code"]=exit_code
        result["finished_utc"]=datetime.now(timezone.utc).isoformat()
        result["reviewer_source_sha256"]=sha(__file__)
        result["packet_identities"]=packet_hashes
        result["limitations"]=["Readback reconciles one fixed-policy complete audit replay; no universal causality, stationarity or no-overfit certificate.",
            "Economic audit conditions are reported separately; no new model, configuration, ranking or substitution is permitted."]
        (out/"stdout.log").write_text("\n".join(logs)+"\n"+result["status"]+"\n")
        (out/"stderr.log").write_text(result.get("error",""))
        (out/"source_manifest.json").write_text(json.dumps(source_hashes,indent=2)+"\n")
        rerun=[sys.executable,str(out/"reviewer_used.py"),"--project",str(root),"--packet",str(packet),"--nomination",str(out/"nomination_used.json"),
               "--nomination-sha256",args.nomination_sha256,"--plan",str(out/"expectations.md"),"--out",str(out)+"_rerun"]
        (out/"rerun.txt").write_text(shlex.join(rerun)+"\n")
        save()
        (out/"artifact_manifest.json").write_text(json.dumps({str(p.relative_to(out)):{"sha256":sha(p),"bytes":p.stat().st_size}
            for p in sorted(out.rglob("*")) if p.is_file() and p.name!="artifact_manifest.json"},indent=2)+"\n")
        print(json.dumps({"status":result["status"],"exit_code":exit_code,"checks":len(result["checks"]),"error":result.get("error")},indent=2))
    return exit_code


if __name__=="__main__":
    raise SystemExit(main())
