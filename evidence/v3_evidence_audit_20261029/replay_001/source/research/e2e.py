"""Prospective complete-scorer composition harness, written before joint.py."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import sys

import numpy as np
import pandas as pd

from common import SOURCE_HASHES, fixture, prepare, scorer, sha, wrapper
from execution import make_execution
from sleeve import MarketSleeve

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
LOCAL = ("PLAN.md", "E2E_SPEC.md", "e2e.py", "joint.py", "common.py",
         "execution.py", "forecast_reference.py", "reference_overlay.py", "sleeve.py")
INPUT_SHA = {
    "returns.csv": "6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d",
    "characteristics.csv": "46b9df20aebb324bd0026090d54f04bd6835283881dd73e728e90f16a5279a08",
    "costs.csv": "ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186",
}
STAGES = {"full": (253, 3779), "discovery": (253, 2015),
          "validation": (2016, 3023), "audit": (3024, 3779)}


def dump(path, obj):
    def convert(v):
        if isinstance(v, np.generic):
            return v.item()
        raise TypeError(type(v).__name__)
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False, default=convert) + "\n")


def array_sha(a):
    """Hash C-order values without materializing a multi-gigabyte bytes copy."""
    a = np.asarray(a)
    h = hashlib.sha256()
    if a.ndim == 0:
        h.update(a.tobytes())
    else:
        for first in range(0, len(a), 128):
            h.update(np.ascontiguousarray(a[first:first + 128]).tobytes())
    return h.hexdigest()


def difference(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b)), initial=0.0))


def atomic_array(path, a):
    temp = path.with_name(path.name + ".tmp")
    with temp.open("wb") as f:
        np.save(f, a, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)
    readback = np.load(path, mmap_mode="r", allow_pickle=False)
    digest = array_sha(a)
    assert readback.shape == a.shape and readback.dtype == a.dtype
    assert array_sha(readback) == digest
    return {"path": path.name, "shape": list(a.shape), "dtype": str(a.dtype),
            "file_sha256": sha(path), "array_sha256": digest, "readback_exact": True}


class Observer:
    """Read completed decisions; optionally discard only completed trace copies."""
    def __init__(self, policy, outer, production=True, trim=False):
        self.policy = policy
        self.outer = outer
        self.production = production
        self.trim = trim
        self.sleeve = policy.sleeve if outer else 0.0

    def forecast(self, returns_history, characteristics_history):
        n = returns_history.shape[1]
        self.previous_actual = np.zeros(n)
        self.previous_inner = np.zeros(n)
        self.previous_virtual = np.zeros(n)
        self.previous_scale = 1.0
        self.records = []
        self.expected_rows = []
        self.values = {k: [] for k in ("targets", "inner_targets", "virtual_targets")}
        self.hashers = {k: hashlib.sha256() for k in self.values}
        self.moments = {h: [0.0, 0.0] for h in (63, 1008)}
        self.errors = {k: 0.0 for k in ("supplied_held", "recorded_fee", "inner_fee",
            "inner_held", "target_formula", "decomposition", "virtual_return",
            "q63", "q1008", "multiplier", "recorded_inner_return")}
        self.checks = {k: True for k in ("finite", "solvent", "gross_bound", "stock_bound",
            "virtual_certificates", "inner_certificates", "risk_clock", "independent_state",
            "allocation_parameters", "inner_raw_beta", "inner_dynamic_stock_bound")}
        self.forecast_output = self.policy.forecast(returns_history, characteristics_history)
        return self.forecast_output

    def rebalance(self, held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        t = len(returns_history) - 1
        today = returns_history[-1]
        j = len(self.records)
        g = float(self.previous_actual @ today)
        gi = float(self.previous_inner @ today)
        gv = float(self.previous_virtual @ today)
        if min(g, gi, gv) <= -1:
            raise RuntimeError("observer reconstructed ruin")
        held = self.previous_actual * (1 + today) / (1 + g)
        inner_held = self.previous_inner * (1 + today) / (1 + gi)
        self.errors["supplied_held"] = max(self.errors["supplied_held"], difference(held, held_positions))
        target = self.policy.rebalance(held_positions, expected_returns, returns_history,
                                       characteristics_history, trading_costs)
        inner_policy = self.policy.inner if self.outer else self.policy
        inner_record = inner_policy.records[-1]
        outer_record = self.policy.records[-1]
        inner_target = np.asarray(inner_record["actual_target"])
        virtual_target = (np.asarray(inner_record["virtual_target"]) if self.production
                          else np.zeros_like(target))
        fee = 0.0 if j == 0 else float(trading_costs @ np.abs(target - held))
        inner_fee = 0.0 if j == 0 else float(trading_costs @ np.abs(inner_target - inner_held))
        proposed = inner_target + self.sleeve / len(target)
        pgross = float(np.abs(proposed).sum())
        scale = min(1.0, 5.0 / pgross) if pgross else 1.0
        self.errors["target_formula"] = max(self.errors["target_formula"], difference(target, proposed * scale))
        self.errors["recorded_fee"] = max(self.errors["recorded_fee"], abs(fee - outer_record["actual_fee"]))
        self.errors["inner_fee"] = max(self.errors["inner_fee"], abs(inner_fee - inner_record["actual_fee"]))
        self.errors["inner_held"] = max(self.errors["inner_held"], float(inner_record["supplied_held_identity_error"]))
        if self.outer:
            self.errors["recorded_inner_return"] = max(self.errors["recorded_inner_return"],
                abs(gi - outer_record["inner_gross_return"]))
        if j and self.previous_scale == 1.0:
            self.errors["decomposition"] = max(self.errors["decomposition"], abs(g - gi - self.sleeve * float(today.mean())))
        gross = float(np.abs(target).sum())
        self.expected_rows.append([g, fee, gross, float(today.mean())])
        self.checks["finite"] &= bool(np.isfinite(target).all())
        self.checks["solvent"] &= min(g, gi, gv) > -1
        self.checks["gross_bound"] &= gross <= 5 + 1e-10
        self.checks["stock_bound"] &= (not self.production or float(np.abs(target).max()) <= .10 + self.sleeve / len(target) + 1e-10)
        if j:
            for h, moment in self.moments.items():
                d = 2.0 ** (-1.0 / h)
                moment[0], moment[1] = d * moment[0] + gv * gv, d * moment[1] + 1
        q = {h: v[0] / v[1] if v[1] else 0.0 for h, v in self.moments.items()}
        a = 1.0 if j < 63 else float(np.clip(np.sqrt(max(q[1008], 1e-12) / max(q[63], 1e-12)), .5, 2.0))
        if self.production:
            for key, expected in (("virtual_return", gv), ("q63", q[63]),
                                  ("q1008", q[1008]), ("multiplier", a)):
                observed = inner_record["virtual_gross_return" if key == "virtual_return" else key]
                self.errors[key] = max(self.errors[key], abs(float(observed) - expected))
            self.checks["virtual_certificates"] &= inner_record["certificate_status"] in ("ok", "ok_after_recovery")
            self.checks["inner_certificates"] &= inner_record["actual_certificate_status"] in ("ok", "ok_after_recovery")
            self.checks["risk_clock"] &= inner_record["actual_state_upto"] == t + 1 and inner_record["virtual_state_upto"] == t + 1
            self.checks["independent_state"] &= (inner_policy.engine._STATE is not inner_policy.actual_engine._STATE
                and inner_policy.engine._STATE.warm is not inner_policy.actual_engine._STATE.warm)
            self.checks["allocation_parameters"] &= (abs(inner_record["actual_risk_aversion"] - 200 / a) <= 1e-10
                and abs(inner_record["actual_stock_cap"] - .05 * a) <= 1e-12)
            self.checks["inner_raw_beta"] &= abs(inner_record["actual_raw_beta_exposure"]) <= 1e-9
            self.checks["inner_dynamic_stock_bound"] &= float(np.abs(inner_target).max()) <= .05 * a + 1e-10
        rec = {"decision_index": t, "sleeve": self.sleeve, "actual_gross_return": g,
            "inner_gross_return": gi, "virtual_gross_return": gv, "actual_fee": fee,
            "inner_fee": inner_fee, "actual_gross": gross, "inner_gross": float(np.abs(inner_target).sum()),
            "outer_gross_scale": scale, "q63": q[63], "q1008": q[1008], "multiplier": a,
            "max_abs_weight": float(np.abs(target).max()), "net_dollars": float(target.sum())}
        self.records.append(rec)
        for key, value in (("targets", target), ("inner_targets", inner_target), ("virtual_targets", virtual_target)):
            self.hashers[key].update(np.ascontiguousarray(value).tobytes())
            if not self.trim:
                self.values[key].append(value.copy())
        self.previous_actual = target.copy()
        self.previous_inner = inner_target.copy()
        self.previous_virtual = virtual_target.copy()
        self.previous_scale = scale
        if self.trim:
            # These records are trace copies; the policies' live state is untouched.
            for policy in ((self.policy, inner_policy) if self.outer else (self.policy,)):
                latest = policy.records[-1]
                for key in ("actual_target", "inner_target", "virtual_target"):
                    latest.pop(key, None)
                policy.records[:] = [latest]
        return target


def metrics(rows):
    days = np.arange(253, 253 + len(rows))
    out = {}
    for name, (lo, hi) in STAGES.items():
        mask = (days >= lo) & (days < hi)
        if not mask.any():
            continue
        g, c, gross, market, seconds = rows[mask].T
        net, mc = g - c, market - market.mean()
        out[name] = {"n": int(mask.sum()),
            "net_sharpe": float(np.sqrt(252) * net.mean() / net.std()) if net.std() else None,
            "gross_sharpe": float(np.sqrt(252) * g.mean() / g.std()) if g.std() else None,
            "net_return_ann_pct": float(25200 * net.mean()),
            "net_vol_ann_pct": float(100 * np.sqrt(252) * net.std()),
            "cost_ann_pct": float(25200 * c.mean()),
            "net_beta": float(mc @ (net - net.mean()) / (mc @ mc)) if mc @ mc else None,
            "mean_gross": float(gross.mean()), "worst_gross_daily_return": float(g.min())}
    return out


def execute(score, policy, R, X, costs, out, outer=True, production=True,
            trim=False, start=252, runtime=False):
    out.mkdir(parents=True, exist_ok=False)
    input_hashes = [array_sha(a) for a in (R, X, costs)]
    observed = Observer(policy, outer, production, trim)
    rows, fsec = score.run(observed, R, X, costs, start=start)
    pred = np.asarray(observed.forecast_output)
    rec = observed.records
    accounting = difference(np.asarray(observed.expected_rows)[1:], rows[:, :4])
    checks = dict(observed.checks)
    checks.update({"error_" + k: v <= 1e-12 for k, v in observed.errors.items()})
    checks.update({"accounting": accounting <= 1e-12,
        "input_unchanged": input_hashes == [array_sha(a) for a in (R, X, costs)],
        "finite_rows_forecast": bool(np.isfinite(rows).all() and np.isfinite(pred).all()),
        "row_count": len(rows) == len(R) - start - 2,
        "decision_count": len(rec) == len(R) - start - 1,
        "decision_clock": [m["decision_index"] for m in rec] == list(range(start, len(R) - 1)),
        "opening_free": rec[0]["actual_fee"] == 0,
        "endpoint_charged": abs(float(rows[-1, 1]) - rec[-1]["actual_fee"]) <= 1e-12,
        "forecast_warmup": not production or bool(np.all(pred[:127] == 0))})
    arrays = {"rows": rows, "forecast": pred,
        "decision_indices": np.asarray([m["decision_index"] for m in rec], dtype=np.int64),
        "virtual_returns": np.asarray([m["virtual_gross_return"] for m in rec]),
        "controller_trace": np.asarray([[m["q63"], m["q1008"], m["multiplier"]] for m in rec])}
    if trim:
        arrays.update({"final_targets": observed.previous_actual,
            "final_inner_targets": observed.previous_inner, "final_virtual_targets": observed.previous_virtual})
    else:
        arrays.update({k: np.asarray(v) for k, v in observed.values.items()})
    manifests = {name: atomic_array(out / (name + ".npy"), a) for name, a in arrays.items()}
    hashes = {k: h.hexdigest() for k, h in observed.hashers.items()}
    if not trim:
        checks["decision_hash_readback"] = all(hashes[k] == array_sha(arrays[k]) for k in hashes)
    p = {} if runtime or start != 252 else metrics(rows)
    summary = {"checks": checks, "all_passed": all(checks.values()), "performance": p,
        "forecast_seconds": fsec, "mean_rebalance_ms": float(1000 * rows[:, 4].mean()),
        "p99_rebalance_ms": float(1000 * np.quantile(rows[:, 4], .99)),
        "accounting_max_error": accounting, "independent_errors": observed.errors,
        "outer_cap_count": sum(m["outer_gross_scale"] < 1 for m in rec),
        "decision_hashes": hashes, "input_array_sha256": input_hashes,
        "trimmed_observation": trim, "runtime_stress_only": runtime,
        "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    dump(out / "array_manifest.json", manifests)
    dump(out / "summary.json", summary)
    with (out / "decisions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rec[0]))
        w.writeheader()
        w.writerows(rec)
    with (out / "daily.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["return_index", "gross_return", "full_cost", "net_return", "closing_target_gross", "market_return", "instrumented_rebalance_seconds"])
        for m, r in zip(rec[1:], rows):
            g, fee, gross, market, seconds = r
            w.writerow([m["decision_index"], g, fee, g - fee, gross, market, seconds])
    print(json.dumps({"case": out.name, "all_passed": summary["all_passed"],
        "performance": p.get("full"), "forecast_seconds": fsec,
        "mean_rebalance_ms": summary["mean_rebalance_ms"]}), flush=True)
    return {**arrays, "summary": summary, "records": rec}


def compare(a, b, cut=None):
    nf = len(b["forecast"]) if cut is None else cut + 1
    nt = len(b["decision_indices"]) if cut is None else int(np.sum(b["decision_indices"] < cut))
    nr = len(b["rows"]) if cut is None else max(0, cut - 253)
    errors = {"forecast": difference(a["forecast"][:nf], b["forecast"][:nf]),
              "economics": difference(a["rows"][:nr, :4], b["rows"][:nr, :4])}
    for key in ("targets", "inner_targets", "virtual_targets", "virtual_returns", "controller_trace"):
        errors[key] = difference(a[key][:nt], b[key][:nt])
    return {"pass": all(v == 0 for v in errors.values()), "max_differences": errors,
            "protected_forecasts": nf, "protected_decisions": nt, "protected_economic_rows": nr}


def compare_inner(base, joint):
    errors = {"inner_targets": difference(base["targets"], joint["inner_targets"])}
    for key in ("forecast", "virtual_targets", "virtual_returns", "controller_trace"):
        errors[key] = difference(base[key], joint[key])
    return {"pass": all(v == 0 for v in errors.values()), "max_differences": errors}


class KnownInner:
    """Predeclared deterministic fixture; never an economic candidate."""
    def __init__(self, sequence):
        self.sequence = np.asarray(sequence, dtype=np.float64)

    def forecast(self, R, X):
        self.previous = np.zeros(R.shape[1])
        self.calls = 0
        self.records = []
        return np.zeros_like(R)

    def rebalance(self, held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        r = returns_history[-1]
        g = float(self.previous @ r)
        held = self.previous * (1 + r) / (1 + g)
        target = self.sequence[self.calls % len(self.sequence)].copy()
        self.records.append({"supplied_held_identity_error": difference(held, held_positions),
            "actual_target": target.copy(), "certificate_status": "not_applicable",
            "actual_fee": 0.0 if self.calls == 0 else float(trading_costs @ np.abs(target - held))})
        self.previous = target.copy()
        self.calls += 1
        return target


def load_actual(data, out):
    hashes = {name: sha(data / name) for name in INPUT_SHA}
    assert hashes == INPUT_SHA
    R = np.ascontiguousarray(pd.read_csv(data / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(data / "characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
    c = pd.read_csv(data / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    assert R.shape == (3780, 1000) and X.shape == (3780, 1000, 13)
    assert all(np.isfinite(a).all() for a in (R, X, c))
    dump(out / "input_manifest.json", {"source_sha256": hashes,
        "array_sha256": [array_sha(a) for a in (R, X, c)]})
    return R, X, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("synthetic", "actual", "runtime"), required=True)
    ap.add_argument("--snapshot", type=Path, default=REPO.parent / "v2-followup-snapshot")
    ap.add_argument("--data", type=Path, default=REPO.parent / "v2-original-input/extracted/Quant Research Take-Home")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--release", type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    dump(args.out / "invocation.json", {"argv": sys.argv, "mode": args.mode,
        "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
        "platform": platform.platform(), "cpu_affinity": sorted(os.sched_getaffinity(0)),
        "blas_environment": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        "harness_sha256": sha(__file__), "spec_sha256": sha(ROOT / "E2E_SPEC.md")})
    shutil.copyfile(__file__, args.out / "executed_e2e.py")
    if not (ROOT / "joint.py").exists():
        dump(args.out / "status.json", {"status": "EXPECTED_RED_MISSING_JOINT", "economic_runs": 0})
        raise SystemExit(3)
    identities = {name: sha(ROOT / name) for name in LOCAL}
    dependencies = json.loads((ROOT / "dependency_manifest.json").read_text())
    assert all(identities[name] == item["sha256"] for name, item in dependencies.items())
    if args.mode != "synthetic":
        if args.release is None:
            raise RuntimeError("a matching source-bound root release is required")
        release = json.loads(args.release.read_text())
        assert release.get("allow_" + args.mode) is True and release["source_sha256"] == identities
        assert release.get("qualifying_components") == ["E2", "M1"]
        dump(args.out / "release_readback.json", {"path": str(args.release), "sha256": sha(args.release), "release": release})
    clean = prepare(args.snapshot, args.out)
    for name in LOCAL:
        shutil.copyfile(ROOT / name, args.out / ("executed_" + name))
    dump(args.out / "local_source_manifest.json", identities)
    from joint import make_joint
    score = scorer(clean)
    findings, runs = {}, []

    def run(name, p, R, X, c, **kwargs):
        result = execute(score, p, R, X, c, args.out / name, **kwargs)
        runs.append(result["summary"])
        return result

    if args.mode == "runtime":
        R0, X0, c = load_actual(args.data, args.out)
        T, N = 25200, R0.shape[1]
        path = args.out / "runtime_characteristics.npy"
        panel = np.lib.format.open_memmap(path, mode="w+", dtype=np.float64, shape=(T, N, 13))
        for first in range(0, T, len(R0)):
            panel[first:min(T, first + len(R0))] = X0[:min(len(R0), T - first)]
        panel.flush()
        del panel
        X = np.load(path, mmap_mode="r")
        R = np.ascontiguousarray(R0[np.arange(T) % len(R0)])
        stress = run("runtime_E2_M1", make_joint(clean), R, X, c, trim=True, runtime=True)
        findings["runtime_gate"] = {"pass": bool(len(os.sched_getaffinity(0)) == 1
            and all(os.environ.get(k) == "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"))
            and stress["summary"]["forecast_seconds"] < 3600 and stress["summary"]["mean_rebalance_ms"] < 100),
            "rows": T, "stocks": N, "not_alpha_evidence": True}
    else:
        if args.mode == "synthetic":
            R, X, c = fixture()
            cut = 360
            reference = REPO / "evidence/v2_score2_execution_20261029/e2e_001/E2"
            dump(args.out / "input_manifest.json", {"seed": 20261028,
                "array_sha256": [array_sha(a) for a in (R, X, c)], "returns_shape": list(R.shape)})
        else:
            R, X, c = load_actual(args.data, args.out)
            cut = 1500
            reference = REPO / "evidence/v2_score2_execution_20261029/actual_001/E2"
        base = run("standalone_E2", wrapper(clean, "E2", make_execution), R, X, c, outer=False)
        ref_errors = {key: difference(base[key], np.load(reference / (key + ".npy"), mmap_mode="r"))
                      for key in ("targets", "virtual_targets", "forecast")}
        ref_errors["economics"] = difference(base["rows"][:, :4], np.load(reference / "rows.npy", mmap_mode="r")[:, :4])
        findings["standalone_reproduction"] = {"pass": all(x == 0 for x in ref_errors.values()),
            "max_differences": ref_errors, "reference": str(reference),
            "reference_sha256": {name: sha(reference / name) for name in ("targets.npy", "virtual_targets.npy", "forecast.npy", "rows.npy")}}
        zero_sleeve = run("M0_E2", make_joint(clean, sleeve=0.0), R, X, c)
        findings["M0_exact"] = compare(base, zero_sleeve)
        policy = make_joint(clean)
        candidate = run("E2_M1", policy, R, X, c)
        findings["inner_E2_exact"] = compare_inner(base, candidate)
        Rf, Xf = R.copy(order="C"), X.copy(order="C")
        Rf[cut:] = -.6 * Rf[cut:] + .0007
        Xf[cut:] = np.flip(Xf[cut:], axis=1) + .2
        future = run("joint_future", policy, Rf, Xf, c)
        findings["future"] = compare(candidate, future, cut=cut)
        prefix = run("joint_prefix", policy, R[:cut + 1], X[:cut + 1], c)
        findings["prefix"] = compare(candidate, prefix)
        if args.mode == "synthetic":
            zero = run("joint_zero_returns", policy, np.zeros_like(R), X, c)
            findings["zero_return_books"] = {"pass": bool(np.all(zero["forecast"] == 0)
                and np.all(zero["inner_targets"] == 0) and np.all(zero["virtual_targets"] == 0)
                and np.all(zero["targets"] == .05 / R.shape[1]) and np.all(zero["rows"][:, :2] == 0))}
        repeated = run("joint_restart", policy, R, X, c)
        findings["restart"] = compare(candidate, repeated)
        if args.mode == "synthetic":
            trimmed = run("joint_trimmed", make_joint(clean), R, X, c, trim=True)
            findings["trimmed_exact"] = {"pass": bool(candidate["summary"]["decision_hashes"] == trimmed["summary"]["decision_hashes"]
                and np.array_equal(candidate["forecast"], trimmed["forecast"])
                and np.array_equal(candidate["rows"][:, :4], trimmed["rows"][:, :4])),
                "full_hashes": candidate["summary"]["decision_hashes"], "trimmed_hashes": trimmed["summary"]["decision_hashes"]}
            toy_R = np.asarray([[0, 0, 0], [-.01, .03, .005], [.02, -.01, .01], [-.03, .01, .02],
                [.01, .01, .01], [-.02, 0, .01], [.005, -.007, .012], [0, 0, 0]])
            toy_X, toy_c = np.zeros((8, 3, 13)), np.asarray([.001, .002, .003])
            sequence = [[.3, -.2, .1], [.3, -.2, .1], [-.3, .2, -.1], [0, 0, 0], [.1, .1, -.1]]
            toy = run("known_netting_reversals", MarketSleeve(KnownInner(sequence), .05), toy_R, toy_X, toy_c, production=False, start=0)
            g = float(toy["targets"][0] @ toy_R[1])
            held_alpha = toy["inner_targets"][0] * (1 + toy_R[1]) / (1 + g)
            held_basket = (.05 / 3) * (1 + toy_R[1]) / (1 + g)
            separate = float(toy_c @ (np.abs(toy["inner_targets"][1] - held_alpha) + np.abs(.05 / 3 - held_basket)))
            findings["known_trade_netting"] = {"pass": bool(toy["rows"][0, 1] < separate - 1e-12
                and np.any(toy["inner_targets"][1:] * toy["inner_targets"][:-1] < 0)),
                "actual_fee": float(toy["rows"][0, 1]), "separately_summed_fee": separate}
            cap = run("forced_outer_cap", MarketSleeve(KnownInner([[4.99 / 3] * 3]), .05), toy_R, toy_X, toy_c, production=False, start=0)
            findings["known_outer_cap"] = {"pass": bool(all(m["outer_gross_scale"] < 1 for m in cap["records"])
                and np.array_equal(cap["inner_targets"], np.full_like(cap["inner_targets"], 4.99 / 3)))}
            Re, Xe, ce = fixture(n=128)
            extreme_base = run("extreme_standalone_E2", wrapper(clean, "E2", make_execution, forecast_scale=100.0), Re, Xe, ce, outer=False)
            extreme_joint = run("extreme_joint", MarketSleeve(wrapper(clean, "E2", make_execution, forecast_scale=100.0), .05), Re, Xe, ce)
            findings["extreme_inner_exact"] = compare_inner(extreme_base, extreme_joint)
            findings["extreme_inner_cap_reached"] = {"pass": float(np.abs(extreme_base["targets"]).sum(axis=1).max()) >= 5 - 1e-8,
                "outer_cap_count": extreme_joint["summary"]["outer_cap_count"]}
        else:
            perf = candidate["summary"]["performance"]["full"]
            findings["actual_beta_runtime"] = {"pass": bool(abs(perf["net_beta"]) < .2
                and candidate["summary"]["mean_rebalance_ms"] < 100
                and candidate["summary"]["forecast_seconds"] < 3600)}
            dump(args.out / "economic_comparison.json", {"standalone_E2": base["summary"],
                "joint": candidate["summary"], "best_standalone_M1_sharpe": 1.426560898191992,
                "joint_minus_M1": perf["net_sharpe"] - 1.426560898191992,
                "exceeds_best_standalone": perf["net_sharpe"] > 1.426560898191992 + 1e-8,
                "all_history_development": True, "independent_root_readback_required": True})
    findings["all_workflow_checks"] = {"pass": all(r["all_passed"] for r in runs), "workflow_count": len(runs),
        "assertion_count": sum(len(r["checks"]) for r in runs)}
    findings["sources_unchanged"] = {"pass": identities == {name: sha(ROOT / name) for name in LOCAL}
        and SOURCE_HASHES == {name: sha(clean / name) for name in SOURCE_HASHES}}
    result = {"mode": args.mode, "checks": findings, "all_passed": all(v["pass"] for v in findings.values()),
        "source_sha256": identities, "baseline_source_sha256": SOURCE_HASHES,
        "one_new_economic_policy": "F2 -> E2 -> fixed M1", "production_modified": False}
    dump(args.out / "result.json", result)
    dump(args.out / "artifact_manifest.json", {str(p.relative_to(args.out)): sha(p)
        for p in sorted(args.out.rglob("*")) if p.is_file() and "__pycache__" not in str(p)})
    print(json.dumps(result, indent=2), flush=True)
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
