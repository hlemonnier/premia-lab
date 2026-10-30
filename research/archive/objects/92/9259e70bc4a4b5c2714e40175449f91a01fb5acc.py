"""Independent reconciliation of the two completed, released validation E2Es.

Expectations precede this source. A parent message disclosed the ranking before
source completion; that chronology is preserved separately. No model is loaded.
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

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[key] = "1"
sys.dont_write_bytecode = True
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PLAN_SHA = "adcf3443118be8ca809a5a82b6d9a8427396e5d72e4c8dd8755fa3ec8087fd87"
NOM_SHA = "fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5"
SELECT_SHA = "941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa"
CONTROLLER_SHA = "d3c3cfd4a1fde10398fc5546f3dc48d395f68a4c06fbe73311c8b5c2cdc37dfe"
HELPER_SHA = "6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69"
MASKS = {"validation_a": (2016, 2520), "validation_b": (2520, 3023), "pooled_validation": (2016, 3023)}
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


def npy_sha(array):
    stream = io.BytesIO()
    np.save(stream, np.ascontiguousarray(array), allow_pickle=False)
    return hashlib.sha256(stream.getvalue()).hexdigest()


def csv_rows(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
args = parser.parse_args()
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
if (OUT / "summary.json").exists():
    raise FileExistsError(OUT / "summary.json")
result = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(), "checks": [], "candidates": {},
          "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
          "scope": "Independent saved validation E2E reconciliation; no model execution or audit input access",
          "parent_ranking_disclosed_before_reviewer_source_completion": True,
          "validation_numeric_read_started": False, "audit_observations_read": False, "model_executions": 0}
logs = []
identities = {}


def save():
    (OUT / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")


def check(name, passed, actual=None):
    row = {"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual}
    result["checks"].append(row)
    logs.append(json.dumps(row, allow_nan=False))
    if not passed:
        raise AssertionError(name)


def compare(name, actual, expected, exact=False):
    actual, expected = np.asarray(actual), np.asarray(expected)
    same = actual.shape == expected.shape
    error = np.abs(actual - expected) if same else np.array([np.inf])
    finite = same and np.isfinite(actual).all() and np.isfinite(expected).all()
    passed = finite and (np.array_equal(actual, expected) if exact else np.all(error <= ATOL + RTOL * np.abs(expected)))
    maximum = float(error.max()) if error.size and np.isfinite(error).all() else None
    check(name, passed, {"shape": list(actual.shape), "expected_shape": list(expected.shape), "max_abs_error": maximum,
                        "exact_required": exact, "exact_observed": bool(same and np.array_equal(actual, expected))})


save()
try:
    plan = Path(__file__).with_name("EXPECTATIONS.md")
    check("prospective_expectations", sha(plan) == PLAN_SHA, sha(plan))
    check("frozen_nomination", sha(ROOT / "research/VALIDATION_NOMINATION.json") == NOM_SHA, NOM_SHA)
    check("frozen_selection_record", sha(ROOT / "research/VALIDATION_SELECTION.json") == SELECT_SHA, SELECT_SHA)
    for source, name in ((Path(__file__), "reviewer_used.py"), (plan, "expectations_used.md"),
                         (ROOT / "research/VALIDATION_NOMINATION.json", "nomination_used.json"),
                         (ROOT / "research/VALIDATION_SELECTION.json", "selection_used.json"),
                         (ROOT / "tools/run_candidate.py", "metric_helper_used.py")):
        shutil.copy2(source, OUT / name)
    check("metric_helper_identity", sha(OUT / "metric_helper_used.py") == HELPER_SHA, HELPER_SHA)
    spec = importlib.util.spec_from_file_location("validation_readback_helper", OUT / "metric_helper_used.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    nomination = read(OUT / "nomination_used.json")
    result["validation_numeric_read_started"] = True
    save()
    selection = read(OUT / "selection_used.json")
    check("fixed_pair", {c["candidate_id"] for c in nomination["candidates"]} == {"C06_gls_factor", "C09_additive_long_memory"}, len(nomination["candidates"]))
    result["environment"] = {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "pid": os.getpid(),
                             "thread_environment": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}}
    for candidate in nomination["candidates"]:
        for evidence in candidate["evidence"]:
            path = ROOT / evidence["path"]
            check(candidate["candidate_id"] + ":engineering_identity:" + evidence["path"], sha(path) == evidence["sha256"], evidence["sha256"])
            if "status" in evidence:
                state = read(path)
                check(candidate["candidate_id"] + ":engineering_completion:" + evidence["path"], state["status"] == evidence["status"] and state["exit_code"] == 0, state["status"])
    result["validation_numeric_read_started"] = True
    save()
    for item in nomination["candidates"]:
        cid = item["candidate_id"]
        label = cid.split("_")[0]
        packet = ROOT / "evidence" / ("validation_" + label + "_001")
        state, manifest = read(packet / "summary.json"), read(packet / "artifact_manifest.json")
        identities[label] = {"packet": str(packet), "summary_sha256": sha(packet / "summary.json"), "artifact_manifest_sha256": sha(packet / "artifact_manifest.json")}
        check(label + ":complete_validation", state["status"] == "EXECUTED_PASS_SCOPE_ONLY" and state["exit_code"] == 0
              and state["mode"] == "validation" and state["completed_rebalances"] == 2771
              and state["protected_numeric_access_started"] and state["validation_opened"] and not state["audit_opened"], state["status"])
        check(label + ":reported_checks", bool(state["checks"]) and all(c["status"] == "PASS" for c in state["checks"]), len(state["checks"]))
        for relative, recorded in manifest.items():
            path = packet / relative
            check(label + ":artifact:" + relative, path.stat().st_size == recorded["bytes"] and sha(path) == recorded["sha256"], recorded["sha256"])
        source_map, inputs, config = (read(packet / name) for name in ("source_manifest.json", "input_manifest.json", "config.json"))
        check(label + ":controller_nomination_config", sha(packet / "runner_used.py") == CONTROLLER_SHA
              and sha(packet / "nomination_used.json") == NOM_SHA and sha(packet / "config.json") == item["config_sha256"]
              and state["configuration"] == config and config["candidate_id"] == cid, cid)
        expected_sources = {"source/candidate/" + Path(k).name: v for k, v in item["source_sha256"].items()}
        check(label + ":candidate_closure", {k: v for k, v in source_map.items() if k.startswith("source/candidate/")} == expected_sources, expected_sources)
        for relative, digest in source_map.items():
            check(label + ":source:" + relative, sha(packet / relative) == digest, digest)
        check(label + ":control_identities", source_map["source/score.py"] == nomination["scorer_sha256"]
              and source_map["protocol_used.json"] == nomination["protocol_sha256"]
              and source_map["metric_helper_used.py"] == HELPER_SHA, True)
        check(label + ":input_scope", inputs["input_slice"] == [0, 3024] and inputs["kind"] == "canonical_market", inputs["input_slice"])
        input_hashes = {name: sha(packet / "inputs" / name) for name in ("returns.npy", "characteristics.npy", "costs.npy")}
        check(label + ":input_identities", input_hashes == state["input_hashes_after"] == {k: v["sha256"] for k, v in inputs["files"].items()}, input_hashes)
        identities[label]["input_hashes"] = input_hashes
        r, x, costs = (np.load(packet / "inputs" / name, mmap_mode="r", allow_pickle=False) for name in ("returns.npy", "characteristics.npy", "costs.npy"))
        f, t, h, latency = (np.load(packet / name, mmap_mode="r", allow_pickle=False) for name in ("forecasts.npy", "targets.npy", "held_books.npy", "candidate_rebalance_seconds.npy"))
        arrays = (r, x, costs, f, t, h, latency)
        check(label + ":full_array_shapes_values", [a.shape for a in arrays] == [(3024,1000),(3024,1000,13),(1000,),(3024,1000),(2771,1000),(2771,1000),(2771,)]
              and all(a.dtype == np.float64 and np.isfinite(a).all() for a in arrays) and np.all(costs >= 0) and np.all(latency >= 0), [list(a.shape) for a in arrays])
        check(label + ":canonical_layout", r.flags.f_contiguous and not r.flags.c_contiguous and x.flags.c_contiguous, [list(r.strides), list(x.strides)])
        for name, panel in zip(("returns.npy", "characteristics.npy", "costs.npy"), (r[:2016], x[:2016], costs)):
            cache = ROOT / "cache/discovery" / name
            check(label + ":discovery_cache_identity:" + name, sha(cache) == helper.CACHE_SHA256[name], helper.CACHE_SHA256[name])
            compare(label + ":discovery_input_prefix:" + name, panel, np.load(cache, mmap_mode="r", allow_pickle=False), True)
        daily, target_records = csv_rows(packet / "daily.csv"), csv_rows(packet / "targets.csv")
        indices = np.array([int(row["return_index"]) for row in daily])
        rows = np.array([[float(row[k]) for k in FIELDS] for row in daily])
        net = np.array([float(row["net_return"]) for row in daily])
        check(label + ":full_daily_indices", np.array_equal(indices, np.arange(253,3023)) and all(int(row["csv_day_label"]) == i+1 for i,row in zip(indices,daily)), len(daily))
        check(label + ":full_target_indices", [int(row["earning_index"]) for row in target_records] == list(range(253,3024)), len(target_records))
        check(label + ":finite_economics", rows.shape == (2770,5) and np.isfinite(rows).all() and np.isfinite(net).all() and np.all(rows[:,1] >= 0), True)
        compare(label + ":net_identity", net, rows[:,0]-rows[:,1], True)
        gross = np.einsum("ij,ij->i", t[:-1], r[indices])
        drift = t[:-1] * (1+r[indices]) / (1+gross[:,None])
        compare(label + ":full_gross", rows[:,0], gross)
        compare(label + ":full_drift", h[1:], drift)
        compare(label + ":full_fees", rows[:,1], np.abs(t[1:]-drift) @ costs)
        compare(label + ":full_market", rows[:,3], r[indices].mean(axis=1))
        compare(label + ":full_exposure", rows[:,2], np.abs(t[1:]).sum(axis=1))
        compare(label + ":target_csv_latency", np.array([float(row["candidate_rebalance_seconds"]) for row in target_records]), latency, True)
        compare(label + ":target_csv_costs", np.array([float(row["full_trade_cost"]) for row in target_records]), np.abs(t-h) @ costs)
        compare(label + ":target_csv_gross", np.array([float(row["target_gross"]) for row in target_records]), np.abs(t).sum(axis=1))
        check(label + ":opening_free_trade", np.count_nonzero(h[0]) == 0 and float(target_records[0]["full_trade_cost"]) == state["trading"]["opening_full_cost_waived"], state["trading"]["opening_full_cost_waived"])
        check(label + ":full_path_controls", float(np.abs(t).max()) <= config["weight_cap"]+1e-12
              and float(np.abs(t).sum(axis=1).max()) <= config["gross_cap"]+1e-12 and np.all(rows[:,0] > -1) and np.all(net > -1),
              {"maximum_stock": float(np.abs(t).max()), "maximum_gross": float(np.abs(t).sum(axis=1).max()), "minimum_net": float(net.min())})
        old = ROOT / item["discovery_reference"]
        for name, digest in item["discovery_reference_sha256"].items():
            check(label + ":historical_reference:" + name, sha(old / name) == digest and sha(packet / "reference" / name) == digest, digest)
        old_summary = read(old / "summary.json")
        for name, prefix in (("forecasts.npy", f[:2016]), ("targets.npy", t[:1763]), ("held_books.npy", h[:1763])):
            digest = npy_sha(prefix)
            check(label + ":actual_original_array_prefix:" + name, digest == old_summary["output_arrays"][name]["sha256"], digest)
        old_daily = csv_rows(old / "daily.csv")
        compare(label + ":exact_original_economics", rows[:1762,:4], np.array([[float(row[k]) for k in FIELDS[:4]] for row in old_daily]), True)
        compare(label + ":exact_original_net", net[:1762], np.array([float(row["net_return"]) for row in old_daily]), True)
        metrics_by_period = {}
        for period, (first,stop) in MASKS.items():
            mask = (indices >= first) & (indices < stop)
            check(label + ":mask:" + period, np.array_equal(indices[mask], np.arange(first,stop)) and state["score_masks"][period] == [first,stop], int(mask.sum()))
            metrics = helper.summarize_rows(rows[mask], indices[mask])
            check(label + ":all_reported_metrics:" + period, metrics == state["metrics"][period], metrics)
            y, market = net[mask], rows[mask,3]
            ym, mm = float(y.mean()), float(market.mean())
            variance = float(np.mean((y-ym)**2))
            market_ss = float(np.sum((market-mm)**2))
            independent = {"annual_arithmetic_net_return":252*ym, "annual_net_volatility":math.sqrt(252*variance),
                           "net_sharpe":math.sqrt(252)*ym/math.sqrt(variance) if variance else None,
                           "realized_net_market_beta":float(np.sum((market-mm)*(y-ym))/market_ss) if market_ss else None}
            wealth = np.concatenate(([1.0], np.cumprod(1+y)))
            independent["max_drawdown"] = float(np.max(1-wealth/np.maximum.accumulate(wealth)))
            for key,value in independent.items():
                if value is None:
                    check(label + ":independent_metric:" + period + ":" + key, metrics[key] is None, value)
                else:
                    compare(label + ":independent_metric:" + period + ":" + key, [value], [metrics[key]])
            metrics_by_period[period] = metrics
        mean_ms = float((latency*1000).mean())
        compare(label + ":mean_candidate_latency", [mean_ms], [state["timing"]["mean_candidate_rebalance_ms"]], True)
        compare(label + ":max_candidate_latency", [float(latency.max()*1000)], [state["timing"]["max_candidate_rebalance_ms"]], True)
        pooled = metrics_by_period["pooled_validation"]
        beta, score = pooled["realized_net_market_beta"], pooled["net_sharpe"]
        beta_ok = beta is not None and math.isfinite(beta) and abs(beta) < .2
        runtime_ok = mean_ms < 100
        score_ok = score is not None and math.isfinite(score)
        check(label + ":reported_feasibility", state["candidate_feasibility"]["scope"] == "validation"
              and state["candidate_feasibility"]["realized_abs_beta_below_0_2"] == beta_ok
              and state["candidate_feasibility"]["candidate_mean_rebalance_below_100ms"] == runtime_ok
              and state["candidate_feasibility"]["net_solvency"] and state["candidate_feasibility"]["position_controls"], state["candidate_feasibility"])
        result["candidates"][cid] = {"metrics": metrics_by_period, "mean_candidate_rebalance_ms":mean_ms,
            "eligible":bool(beta_ok and runtime_ok and score_ok), "eligibility_components":{"beta":beta_ok,"runtime":runtime_ok,"defined_score":score_ok,"engineering_and_path_checks":True},
            "simplicity_rank":item["simplicity_rank"], "config_sha256":item["config_sha256"]}
    check("same_canonical_validation_inputs", identities["C06"]["input_hashes"] == identities["C09"]["input_hashes"], identities["C06"]["input_hashes"])
    eligible = [(cid,value) for cid,value in result["candidates"].items() if value["eligible"]]
    selected = None
    if eligible:
        best = max(value["metrics"]["pooled_validation"]["net_sharpe"] for _,value in eligible)
        tied = [(cid,value) for cid,value in eligible if best-value["metrics"]["pooled_validation"]["net_sharpe"] <= 1e-6]
        selected = min(tied, key=lambda item:(item[1]["simplicity_rank"],item[1]["mean_candidate_rebalance_ms"]))[0]
    result["mechanically_selected_candidate_id"] = selected
    check("root_selection_reconciliation", selected == selection["selected_candidate_id"]
          and (selected is None or result["candidates"][selected]["config_sha256"] == selection["config_sha256"]), selected)
    result["input_packets"] = identities
    result["status"], result["exit_code"] = "EXECUTED_PASS_SCOPE_ONLY", 0
except Exception:
    result["status"], result["exit_code"] = "EXECUTED_FAIL_OR_INCOMPLETE", 1
    result["error"] = traceback.format_exc()
finally:
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["reviewer_source_sha256"] = sha(__file__)
    result["limitations"] = ["Independent saved E2E arithmetic and identity review, not a blinded ranking review or universal causal/overfit certificate.",
                             "No candidate execution, retuning, additional configuration, or audit numeric access occurred."]
    (OUT / "stdout.log").write_text("\n".join(logs)+"\n"+result["status"]+"\n")
    (OUT / "stderr.log").write_text(result.get("error", ""))
    (OUT / "rerun.txt").write_text(shlex.join([sys.executable,str(Path(__file__).resolve()),"--out",str(OUT)+"_rerun"])+"\n")
    save()
    (OUT / "artifact_manifest.json").write_text(json.dumps({str(p.relative_to(OUT)):{"sha256":sha(p),"bytes":p.stat().st_size}
        for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "artifact_manifest.json"},indent=2)+"\n")
    print(json.dumps({"status":result["status"],"exit_code":result["exit_code"],"checks":len(result["checks"]),
                      "selected_candidate":result.get("mechanically_selected_candidate_id"),"error":result.get("error")},indent=2))
raise SystemExit(result["exit_code"])
