"""Prospective M0/M1 original-scorer workflows; written before sleeve.py."""
from sleeve import MarketSleeve

import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import sys

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
REFERENCE = REPO / "evidence/v2_score_joint_20261028"
sys.path.insert(0, str(REFERENCE))
from joint import make_joint


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REF = load_module("m1_joint_reference_harness", REFERENCE / "e2e.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def dump(path, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError("unsupported JSON value: " + type(item).__name__)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False, default=convert) + "\n")


def atomic_array(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as f:
        np.save(f, value, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)
    readback = np.load(path, allow_pickle=False)
    if not np.array_equal(readback, value):
        raise RuntimeError("atomic array readback mismatch: " + str(path))
    return {"path": str(path), "shape": list(readback.shape),
            "dtype": str(readback.dtype), "sha256": sha(path),
            "array_sha256": array_sha(readback), "readback_exact": True}


def execute(scorer, policy, R, X, costs, start=252):
    rows, forecast_seconds = scorer.run(policy, R, X, costs, start=start)
    targets = np.asarray([r["actual_target"] for r in policy.records])
    inner_targets = np.asarray([r["inner_target"] for r in policy.records])
    meta = [{k: v for k, v in r.items() if k not in ("actual_target", "inner_target")}
            for r in policy.records]
    expected_rows = []
    previous_actual = np.zeros(R.shape[1])
    previous_inner = np.zeros(R.shape[1])
    error_inner_return = error_recorded_fee = error_actual_return = 0.0
    decomposition_errors = []
    for j, (record, target, inner_target) in enumerate(zip(meta, targets, inner_targets)):
        t = record["decision_index"]
        actual_gross = float(previous_actual @ R[t])
        inner_gross = float(previous_inner @ R[t])
        assert actual_gross > -1 and inner_gross > -1
        held = previous_actual * (1.0 + R[t]) / (1.0 + actual_gross)
        fee = 0.0 if j == 0 else float(costs @ np.abs(target - held))
        expected_rows.append([actual_gross, fee, float(np.abs(target).sum()), float(R[t].mean())])
        error_recorded_fee = max(error_recorded_fee, abs(fee-record["actual_fee"]))
        error_actual_return = max(error_actual_return, abs(actual_gross-record["actual_gross_return"]))
        error_inner_return = max(error_inner_return, abs(inner_gross-record["inner_gross_return"]))
        if j and meta[j-1]["outer_gross_scale"] == 1.0:
            decomposition_errors.append(abs(actual_gross-inner_gross-policy.sleeve*float(R[t].mean())))
        previous_actual = target
        previous_inner = inner_target
    expected = np.asarray(expected_rows)[1:]
    return {"rows": rows, "targets": targets, "inner_targets": inner_targets,
            "forecast": np.asarray(policy.forecast_output).copy(), "metadata": meta,
            "forecast_seconds": forecast_seconds,
            "accounting_error": float(np.max(np.abs(expected-rows[:, :4]))),
            "recorded_fee_error": error_recorded_fee,
            "recorded_actual_return_error": error_actual_return,
            "recorded_inner_return_error": error_inner_return,
            "gross_decomposition_error": max(decomposition_errors, default=0.0)}


def save_run(out, name, result):
    folder = out / name
    folder.mkdir()
    arrays = {}
    for key in ("targets", "inner_targets", "rows", "forecast"):
        arrays[key] = atomic_array(folder / (key + ".npy"), result[key])
    dump(folder / "array_manifest.json", arrays)
    with (folder / "daily.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["return_index", "gross_return", "full_cost", "net_return",
                         "closing_target_gross", "market_return", "instrumented_rebalance_seconds"])
        for record, row in zip(result["metadata"][1:], result["rows"]):
            g, c, gross, m, sec = row
            writer.writerow([record["decision_index"], g, c, g-c, gross, m, sec])
    with (folder / "decisions.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result["metadata"][0]))
        writer.writeheader()
        writer.writerows(result["metadata"])
    return arrays


def checks_for(result, sleeve, weight_bound=True):
    meta = result["metadata"]
    targets, inner = result["targets"], result["inner_targets"]
    expected = inner + sleeve / targets.shape[1]
    expected *= np.minimum(1.0, 5.0/np.maximum(np.abs(expected).sum(axis=1), 1e-300))[:, None]
    answer = {
        "target_formula": bool(np.max(np.abs(targets-expected)) <= 1e-12),
        "actual_accounting": result["accounting_error"] <= 1e-12,
        "recorded_fee": result["recorded_fee_error"] <= 1e-12,
        "recorded_actual_return": result["recorded_actual_return_error"] <= 1e-12,
        "recorded_inner_return": result["recorded_inner_return_error"] <= 1e-12,
        "gross_decomposition": result["gross_decomposition_error"] <= 1e-12,
        "outer_held_identity": max(r["outer_held_identity_error"] for r in meta) <= 1e-12,
        "inner_held_identity": max(r["inner_held_identity_error"] for r in meta) <= 1e-12,
        "gross_cap": bool(np.abs(targets).sum(axis=1).max() <= 5+1e-12),
        "finite": bool(np.isfinite(result["rows"]).all() and np.isfinite(targets).all()),
        "opening_free": meta[0]["actual_fee"] == 0.0,
        "endpoint_charged": abs(result["rows"][-1, 1]-meta[-1]["actual_fee"]) <= 1e-12,
        "solver_certificates": all(r["certificate_status"] in ("ok", "ok_after_recovery", "not_applicable") for r in meta),
    }
    if weight_bound:
        answer["stock_bound"] = bool(np.abs(targets).max() <= .10+sleeve/targets.shape[1]+1e-12)
    return answer


class KnownInner:
    """Prospective known-policy fixture, independently checking its held book."""
    def __init__(self, target_sequence):
        self.sequence = np.asarray(target_sequence, dtype=float)

    def forecast(self, returns_history, characteristics_history):
        self.previous = np.zeros(returns_history.shape[1])
        self.calls = 0
        self.records = []
        return np.zeros_like(returns_history)

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        r = returns_history[-1]
        g = float(self.previous @ r)
        expected_held = self.previous*(1+r)/(1+g)
        error = float(np.max(np.abs(expected_held-held_positions)))
        target = self.sequence[self.calls % len(self.sequence)].copy()
        self.records.append({"supplied_held_identity_error": error,
                             "certificate_status": "not_applicable"})
        self.previous = target.copy()
        self.calls += 1
        return target


def temporal_checks(scorer, policy, base, R, X, costs, out, cut, stem):
    R2, X2 = R.copy(order="C"), X.copy(order="C")
    R2[cut:] = -.6*R2[cut:] + .0007
    X2[cut:] = np.flip(X2[cut:], axis=1) + .2
    future = execute(scorer, policy, R2, X2, costs)
    save_run(out, stem+"_future", future)
    decision_mask = np.asarray([r["decision_index"] < cut for r in base["metadata"]])
    checks = {
        "future_forecast": bool(np.array_equal(base["forecast"][:cut+1], future["forecast"][:cut+1])),
        "future_targets": bool(np.array_equal(base["targets"][decision_mask], future["targets"][decision_mask])),
        "future_inner_targets": bool(np.array_equal(base["inner_targets"][decision_mask], future["inner_targets"][decision_mask])),
        "future_economics": bool(np.max(np.abs(base["rows"][:cut-253, :4]-future["rows"][:cut-253, :4])) <= 1e-12),
    }
    prefix = execute(scorer, policy, R[:cut+1], X[:cut+1], costs)
    save_run(out, stem+"_prefix", prefix)
    checks.update({
        "prefix_forecast": bool(np.array_equal(base["forecast"][:cut+1], prefix["forecast"])),
        "prefix_targets": bool(np.array_equal(base["targets"][:len(prefix["targets"])], prefix["targets"])),
        "prefix_inner_targets": bool(np.array_equal(base["inner_targets"][:len(prefix["targets"])], prefix["inner_targets"])),
        "prefix_economics": bool(np.max(np.abs(base["rows"][:len(prefix["rows"]), :4]-prefix["rows"][:, :4])) <= 1e-12),
    })
    if stem == "synthetic_M1":
        repeated = execute(scorer, policy, R, X, costs)
        save_run(out, stem+"_restart", repeated)
        checks["restart_forecast"] = bool(np.array_equal(base["forecast"], repeated["forecast"]))
        checks["restart_targets"] = bool(np.array_equal(base["targets"], repeated["targets"]))
        checks["restart_economics"] = bool(np.max(np.abs(base["rows"][:, :4]-repeated["rows"][:, :4])) <= 1e-12)
    return checks


def synthetic(args, engine, config, scorer):
    R, X, costs = REF.fixture()
    dump(args.out / "input_manifest.json", {"seed": 20261028, "R": array_sha(R),
         "X": array_sha(X), "costs": array_sha(costs), "shape": list(R.shape)})
    direct = REF.execute(scorer, make_joint(engine, config), R, X, costs)
    M0 = execute(scorer, MarketSleeve(make_joint(engine, config), 0.0), R, X, costs)
    save_run(args.out, "M0", M0)
    checks = {"M0_"+k: v for k, v in checks_for(M0, 0.0).items()}
    checks.update({"M0_direct_forecast": bool(np.array_equal(direct["forecast"], M0["forecast"])),
                   "M0_direct_targets": bool(np.array_equal(direct["targets"], M0["targets"])),
                   "M0_direct_economics": bool(np.max(np.abs(direct["rows"][:, :4]-M0["rows"][:, :4])) <= 1e-12)})
    policy = MarketSleeve(make_joint(engine, config), .05)
    M1 = execute(scorer, policy, R, X, costs)
    save_run(args.out, "M1", M1)
    checks.update({"M1_"+k: v for k, v in checks_for(M1, .05).items()})
    checks["M1_inner_is_M0"] = bool(np.array_equal(M1["inner_targets"], M0["targets"]))
    checks["M1_same_forecast"] = bool(np.array_equal(M1["forecast"], M0["forecast"]))
    checks.update(temporal_checks(scorer, policy, M1, R, X, costs, args.out, 360, "synthetic_M1"))

    toy_R = np.asarray([[.0,.0,.0],[-.01,.03,.005],[.02,-.01,.01],
                        [-.03,.01,.02],[.01,.01,.01],[-.02,.0,.01],
                        [.005,-.007,.012],[.0,.0,.0]])
    toy_X = np.zeros((len(toy_R), 3, 13))
    toy_costs = np.asarray([.001, .002, .003])
    sequence = [[.3,-.2,.1],[.3,-.2,.1],[-.3,.2,-.1],[0,0,0],[.1,.1,-.1]]
    toy_inner = KnownInner(sequence)
    toy = execute(scorer, MarketSleeve(toy_inner, .05), toy_R, toy_X, toy_costs, start=0)
    save_run(args.out, "known_returns_reversals", toy)
    checks.update({"toy_"+k: v for k, v in checks_for(toy, .05, False).items()})
    checks["toy_inner_targets_exact"] = bool(np.array_equal(toy["inner_targets"], np.asarray([sequence[j % len(sequence)] for j in range(len(toy_R)-1)])))
    checks["toy_reversals_present"] = bool(np.any(toy["inner_targets"][1:]*toy["inner_targets"][:-1] < 0))
    # Split the previous actual stock holdings using their common actual denominator.
    actual_g = float(toy["targets"][0] @ toy_R[1])
    held_alpha = toy["inner_targets"][0]*(1+toy_R[1])/(1+actual_g)
    held_basket = (.05/3)*(1+toy_R[1])/(1+actual_g)
    separately_summed_fee = float(toy_costs @ (np.abs(toy["inner_targets"][1]-held_alpha)+np.abs(.05/3-held_basket)))
    checks["strict_stock_trade_netting"] = bool(toy["rows"][0, 1] < separately_summed_fee-1e-12)
    cap = execute(scorer, MarketSleeve(KnownInner([[4.99/3]*3]), .05), toy_R, toy_X, toy_costs, start=0)
    save_run(args.out, "forced_aggregate_cap", cap)
    checks.update({"cap_"+k: v for k, v in checks_for(cap, .05, False).items()})
    checks["cap_actually_binds"] = all(r["outer_gross_scale"] < 1.0 for r in cap["metadata"])
    checks["cap_keeps_inner_target"] = bool(np.array_equal(cap["inner_targets"], np.full_like(cap["inner_targets"], 4.99/3)))
    zero = execute(scorer, MarketSleeve(KnownInner(sequence), .05), np.zeros_like(toy_R), toy_X, toy_costs, start=0)
    save_run(args.out, "zero_returns", zero)
    checks.update({"zero_"+k: v for k, v in checks_for(zero, .05, False).items()})
    checks["zero_gross_return"] = bool(np.array_equal(zero["rows"][:, 0], np.zeros(len(zero["rows"]))))
    checks["zero_reversal_still_costs"] = bool(zero["rows"][:, 1].max() > 0)
    bad = MarketSleeve(KnownInner(sequence), .05)
    bad.forecast(toy_R, toy_X)
    kwargs = {"held_positions": np.zeros(3), "expected_returns": np.zeros(3),
              "returns_history": toy_R[:1], "characteristics_history": toy_X[:1], "trading_costs": toy_costs}
    bad.rebalance(**kwargs)
    try:
        bad.rebalance(**kwargs)
        checks["repeated_close_rejected"] = False
    except (ValueError, RuntimeError):
        checks["repeated_close_rejected"] = True
    skipped = dict(kwargs)
    skipped["returns_history"] = toy_R[:3]
    skipped["characteristics_history"] = toy_X[:3]
    try:
        bad.rebalance(**skipped)
        checks["skipped_close_rejected"] = False
    except (ValueError, RuntimeError):
        checks["skipped_close_rejected"] = True
    try:
        MarketSleeve(KnownInner(sequence), .05).rebalance(**kwargs)
        checks["unstarted_session_rejected"] = False
    except (ValueError, RuntimeError):
        checks["unstarted_session_rejected"] = True
    expected_errors = {}
    for label, known_targets, returns in (
        ("nonfinite_target", [[float("nan"),0,0]], toy_R),
        ("ruined_inner", [[-10.03/3]*3], np.vstack([np.zeros(3),np.full((7,3),.1)])),
    ):
        try:
            scorer.run(MarketSleeve(KnownInner(known_targets), .05), returns, toy_X, toy_costs, start=0)
            checks[label+"_rejected"] = False
        except (ValueError, RuntimeError, AssertionError) as exc:
            checks[label+"_rejected"] = True
            expected_errors[label] = str(exc)
    try:
        MarketSleeve(KnownInner(sequence), .06)
        checks["unregistered_sleeve_rejected"] = False
    except ValueError:
        checks["unregistered_sleeve_rejected"] = True
    checks["harness_before_policy"] = json.loads((Path(__file__).parent / "build_order.json").read_text())["expected_missing_policy_exit_code"] != 0
    return {"mode": "synthetic", "checks": checks, "all_passed": all(checks.values()),
            "expected_error_details": expected_errors,
            "performance_claim": "none; synthetic verification only"}


def metrics(rows):
    days = np.arange(253, 253+len(rows))
    answer = {}
    for label, lo, hi in (("full",253,3779),("discovery",253,2015),("validation",2016,3023),("audit",3024,3779)):
        chosen = (days >= lo) & (days < hi)
        g, c, gross, market, seconds = rows[chosen].T
        net = g-c
        mc = market-market.mean()
        answer[label] = {"n": int(chosen.sum()), "net_sharpe": float(np.sqrt(252)*net.mean()/net.std()),
            "gross_sharpe": float(np.sqrt(252)*g.mean()/g.std()),
            "net_return_ann_pct": float(net.mean()*25200), "net_vol_ann_pct": float(net.std()*np.sqrt(252)*100),
            "cost_ann_pct": float(c.mean()*25200), "net_beta": float(mc@(net-net.mean())/(mc@mc)),
            "mean_gross": float(gross.mean()), "worst_gross_daily_return": float(g.min()),
            "rebalance_ms_mean": float(seconds.mean()*1000)}
    return answer


def actual(args, engine, config, scorer):
    release = json.loads(args.release.read_text())
    local = Path(__file__).parent
    if not release.get("approved") or release.get("sleeve_sha256") != sha(local / "sleeve.py") or release.get("harness_sha256") != sha(__file__):
        raise RuntimeError("actual replay requires explicit matching root release")
    prior = json.loads(args.e2e_result.read_text())
    if not prior["all_passed"] or prior["executed_sources"] != {name: sha(local/name) for name in ("sleeve.py","e2e.py","PLAN.md")}:
        raise RuntimeError("passing synthetic E2E belongs to different sources")
    R = np.ascontiguousarray(pd.read_csv(args.data / "returns.csv", index_col="day").to_numpy(float))
    X = np.ascontiguousarray(pd.read_csv(args.data / "characteristics.csv", index_col=["day","stock"]).to_numpy(float).reshape(len(R), R.shape[1],13))
    costs = pd.read_csv(args.data / "costs.csv", index_col="stock")["cost"].to_numpy(float)
    assert R.shape == (3780,1000) and np.isfinite(R).all() and np.isfinite(X).all()
    dump(args.out / "input_manifest.json", {name: {"path": str(args.data/name), "sha256": sha(args.data/name)} for name in ("returns.csv","characteristics.csv","costs.csv")})
    reference_path = REFERENCE / "actual_001/joint_F2_VTvol/daily.csv"
    reference = pd.read_csv(reference_path)
    dump(args.out / "references.json", {"joint_ledger": str(reference_path), "joint_ledger_sha256": sha(reference_path),
          "release": str(args.release), "release_sha256": sha(args.release), "e2e_result": str(args.e2e_result), "e2e_result_sha256": sha(args.e2e_result)})
    answer, base = {}, None
    for name, b in (("M0",0.0),("M1",.05)):
        policy = MarketSleeve(make_joint(engine, config), b)
        result = execute(scorer, policy, R, X, costs)
        arrays = save_run(args.out, name, result)
        checks = checks_for(result,b)
        checks["row_count"] = len(result["rows"]) == 3526 and len(result["targets"]) == 3527
        p = metrics(result["rows"])
        checks["net_beta"] = abs(p["full"]["net_beta"]) < .2
        checks["runtime"] = p["full"]["rebalance_ms_mean"] < 100
        checks["solvent"] = p["full"]["worst_gross_daily_return"] > -1
        checks["actual_solver_certificates"] = all(r["certificate_status"] in ("ok", "ok_after_recovery") for r in result["metadata"])
        if name == "M0":
            expected = reference[["gross_return","full_cost","closing_target_gross","market_return"]].to_numpy()
            difference = float(np.max(np.abs(result["rows"][:,:4]-expected)))
            checks["baseline_reproduction"] = difference <= 1e-8
            base = {"targets": result["targets"].copy(), "forecast": result["forecast"].copy()}
        else:
            difference = None
            checks["inner_is_M0"] = bool(np.array_equal(result["inner_targets"], base["targets"]))
            checks["forecast_is_M0"] = bool(np.array_equal(result["forecast"], base["forecast"]))
            checks.update(temporal_checks(scorer, policy, result, R, X, costs, args.out, 1500, "actual_M1"))
        summary = {"name": name, "sleeve": b, "performance": p, "checks": checks, "all_passed": all(checks.values()),
                   "forecast_seconds": result["forecast_seconds"], "array_manifest": arrays,
                   "baseline_reproduction_max_difference": difference,
                   "accounting_max_error": result["accounting_error"],
                   "outer_cap_count": sum(r["outer_gross_scale"] < 1 for r in result["metadata"]),
                   "max_abs_weight": float(np.abs(result["targets"]).max()),
                   "max_gross": float(np.abs(result["targets"]).sum(axis=1).max())}
        answer[name] = summary
        dump(args.out / name / "summary.json", summary)
        print((args.out / name / "summary.json").read_text(), flush=True)
        if not all(checks.values()):
            raise RuntimeError("actual checks failed: " + name)
    return {"mode":"actual","results":answer,"all_passed":all(s["all_passed"] for s in answer.values()),
            "long_history_runtime_gate":"not run here","all_history_development":True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--mode", choices=("synthetic","actual"), default="synthetic")
    ap.add_argument("--data", type=Path)
    ap.add_argument("--release", type=Path)
    ap.add_argument("--e2e-result", type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).parent
    executed_sources = {name: sha(source/name) for name in ("sleeve.py","e2e.py","PLAN.md")}
    for name in executed_sources:
        shutil.copyfile(source/name,args.out/ ("executed_"+name))
    engine, config, scorer, identities = REF.load_baseline(args.snapshot,args.out)
    reference_sources = {name: sha(REFERENCE/name) for name in ("joint.py","overlay.py","prototype.py","e2e.py")}
    dump(args.out / "reference_source_manifest.json", reference_sources)
    dump(args.out / "environment.json", {"python":sys.version,"numpy":np.__version__,"pandas":pd.__version__,
         "platform":platform.platform(),"argv":sys.argv,"configuration":config,"instrumented_runtime":True})
    result = synthetic(args,engine,config,scorer) if args.mode == "synthetic" else actual(args,engine,config,scorer)
    result["executed_sources"] = executed_sources
    result["reference_sources"] = reference_sources
    result["source_unchanged"] = identities == {rel:sha(args.out/"source"/rel) for rel in REF.FILES}
    result["all_passed"] = result["all_passed"] and result["source_unchanged"]
    dump(args.out / "result.json",result)
    dump(args.out / "artifact_manifest.json",{str(p.relative_to(args.out)):sha(p) for p in sorted(args.out.rglob("*")) if p.is_file() and "__pycache__" not in str(p)})
    print((args.out / "result.json").read_text())
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
