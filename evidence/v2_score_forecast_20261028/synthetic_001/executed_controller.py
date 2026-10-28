"""Prospectively specified E2E controller; does not change the original scorer."""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SNAPSHOT = REPO.parent / "v2-followup-snapshot"
DATA = REPO.parent / "v2-original-input/extracted/Quant Research Take-Home"
SOURCE_FILES = ["handoff_v2/strategy.py", "handoff_v2/model_v2/__init__.py",
                "handoff_v2/model_v2/engine.py", "handoff_v2/model_v2/allocator.py",
                "source/Quant Research Take-Home/score.py"]
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
STAGES = {"full": (253, 3779), "discovery": (253, 2015),
          "validation": (2016, 3023), "audit": (3024, 3779)}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def array_sha(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def maximum_difference(a, b):
    return float(np.max(np.abs(a - b), initial=0.0))


def metrics(rows, days):
    net = rows[:, 0] - rows[:, 1]
    result = {}
    for stage, (lo, hi) in STAGES.items():
        mask = (days >= lo) & (days < hi)
        if not mask.any():
            continue
        n, m = net[mask], rows[mask, 3]
        vol = float(n.std())
        mv = float(m.var())
        result[stage] = {
            "n": int(mask.sum()), "sharpe": float(np.sqrt(252) * n.mean() / vol) if vol else None,
            "annual_net_return_pct": float(25200 * n.mean()),
            "annual_vol_pct": float(100 * np.sqrt(252) * vol),
            "annual_cost_pct": float(25200 * rows[mask, 1].mean()),
            "beta": float((m - m.mean()) @ (n - n.mean()) / (len(m) * mv)) if mv else None,
            "mean_gross": float(rows[mask, 2].mean()),
        }
    return result


def fixture(engine, fixed=False, zero=False):
    rng = np.random.default_rng(20261028)
    T, N = 420, 64
    X = np.empty((T, N, 13))
    X[0] = rng.normal(size=(N, 13))
    for t in range(1, T):
        X[t] = X[0] if fixed else .995 * X[t - 1] + np.sqrt(1 - .995 ** 2) * rng.normal(size=(N, 13))
    beta = rng.uniform(.6, 1.4, N)
    beta /= beta.mean()
    market = np.zeros(T) if fixed else rng.normal(0, .008, T)
    R = np.zeros((T, N))
    for j in range(1, T):
        D = engine.basis(X[j - 1])
        linear = .0008 * (1 if fixed or j < 210 else -.5)
        e = linear * D[:, 0] + .0004 * D[:, 13] + rng.normal(0, .002, N)
        e -= e.mean()
        R[j] = beta * market[j] + e
    if zero:
        R.fill(0)
    return np.ascontiguousarray(R), np.ascontiguousarray(X), np.full(N, .0005)


def run_case(engine, score, prototype, variant, R, X, costs, out):
    out.mkdir(parents=True, exist_ok=False)
    before = [array_sha(v) for v in (R, X, costs)]
    observed = {"targets": [], "held": [], "indices": [], "pre_gross": [], "hedge_error": []}
    base_allocate = engine.allocate_factor

    def allocate_observer(*args, **kwargs):
        w = base_allocate(*args, **kwargs)
        observed["pre_gross"].append(float(np.abs(w).sum()))
        return w

    engine.allocate_factor = allocate_observer
    forecast_fn = engine.forecast if variant == "V2" else prototype.make_forecast(engine, variant)

    def forecast(returns_history, characteristics_history):
        p = forecast_fn(returns_history, characteristics_history)
        observed["forecast"] = p
        return p

    def rebalance(held_positions, expected_returns, returns_history,
                  characteristics_history, trading_costs):
        w = engine.rebalance(held_positions, expected_returns, returns_history,
                             characteristics_history, trading_costs)
        observed["indices"].append(len(returns_history) - 1)
        observed["held"].append(held_positions.copy())
        observed["targets"].append(w.copy())
        b = engine._window_beta(np.ascontiguousarray(returns_history), 252)
        observed["hedge_error"].append(float(b @ w))
        return w

    shim = type("ResearchStrategy", (), {"forecast": staticmethod(forecast),
                                         "rebalance": staticmethod(rebalance)})
    print("Starting", out.name, variant, "shape", R.shape, flush=True)
    started = time.perf_counter()
    try:
        rows, fsec = score.run(shim, R, X, costs)
    finally:
        engine.allocate_factor = base_allocate
    wall = time.perf_counter() - started
    pred = observed["forecast"]
    targets = np.asarray(observed["targets"])
    held = np.asarray(observed["held"])
    idx = np.asarray(observed["indices"])
    days = np.arange(253, len(R) - 1)
    previous = np.vstack([np.zeros((1, R.shape[1])), targets[:-1]])
    gross = np.einsum("ij,ij->i", previous, R[idx])
    drift = previous * (1 + R[idx]) / (1 + gross[:, None])
    fee = np.abs(targets - held) @ costs
    fee[0] = 0
    expected_rows = np.column_stack([gross, fee, np.abs(targets).sum(axis=1), R[idx].mean(axis=1)])[1:]
    status = [c["status"] for c in engine.CERTIFICATES]
    checks = {
        "finite": bool(np.isfinite(pred).all() and np.isfinite(targets).all() and np.isfinite(rows).all()),
        "warmup_zero": bool(np.all(pred[:127] == 0)),
        "counts": len(rows) == len(R) - 254 and len(targets) == len(R) - 253,
        "input_unchanged": before == [array_sha(v) for v in (R, X, costs)],
        "drift_reconciles": maximum_difference(drift, held) <= 1e-12,
        "scorer_reconciles": maximum_difference(expected_rows, rows[:, :4]) <= 1e-12,
        "all_certified": all(s in ("ok", "ok_after_recovery") for s in status) and len(status) == len(targets),
        "stock_caps": float(np.abs(targets).max()) <= .05 + 1e-12,
        "gross_cap": float(np.abs(targets).sum(axis=1).max()) <= 5 + 1e-12,
        "estimated_hedge": max(map(abs, observed["hedge_error"])) <= 1e-10,
    }
    summary = {"variant": variant, "configuration": dict(engine.CONFIG), "shape": list(R.shape),
               "checks": checks, "performance": metrics(rows, days), "forecast_seconds": fsec,
               "observed_rebalance_ms": float(1000 * rows[:, 4].mean()), "wall_seconds": wall,
               "forecast_century_extrapolation_seconds": fsec * 25200 / len(R),
               "certificates": {s: status.count(s) for s in sorted(set(status))},
               "max_gross_before_scale": max(observed["pre_gross"]),
               "gross_scalings": sum(g > 5 for g in observed["pre_gross"]),
               "max_estimated_hedge_error": max(map(abs, observed["hedge_error"])),
               "mean_net_stock_investment": float(targets.sum(axis=1).mean()),
               "forecast_sha256": array_sha(pred), "targets_sha256": array_sha(targets),
               "input_array_sha256": before,
               "scorer_max_error": maximum_difference(expected_rows, rows[:, :4]),
               "drift_max_error": maximum_difference(drift, held)}
    np.savez_compressed(out / "arrays.npz", forecast=pred, targets=targets,
                        decision_indices=idx, rows=rows, earning_indices=days)
    pd.DataFrame({"day": days, "gross_return": rows[:, 0], "cost": rows[:, 1],
                  "net_return": rows[:, 0] - rows[:, 1], "target_gross": rows[:, 2],
                  "market": rows[:, 3], "rebalance_seconds": rows[:, 4]}).to_csv(out / "daily.csv", index=False)
    pd.DataFrame({"decision_index": idx, "pre_gross": observed["pre_gross"],
                  "target_gross": np.abs(targets).sum(axis=1),
                  "net_stock": targets.sum(axis=1), "max_abs_weight": np.abs(targets).max(axis=1),
                  "estimated_beta_error": observed["hedge_error"], "certificate": status}).to_csv(out / "decisions.csv", index=False)
    write_json(out / "summary.json", summary)
    print("Completed", out.name, summary["performance"].get("full"), "checks", checks, flush=True)
    assert all(checks.values()), (out.name, checks)
    return {"forecast": pred, "targets": targets, "indices": idx, "rows": rows,
            "days": days, "summary": summary}


def compare(base, other, cut=None, tolerance=1e-12):
    forecast_n = len(other["forecast"]) if cut is None else cut + 1
    target_mask = other["indices"] < (cut if cut is not None else len(other["forecast"]))
    row_mask = other["days"] < (cut if cut is not None else len(other["forecast"]))
    nt, nr = int(target_mask.sum()), int(row_mask.sum())
    diffs = {"forecast": maximum_difference(base["forecast"][:forecast_n], other["forecast"][:forecast_n]),
             "targets": maximum_difference(base["targets"][:nt], other["targets"][target_mask]),
             "economics": maximum_difference(base["rows"][:nr, :4], other["rows"][row_mask, :4])}
    return {"max_differences": diffs, "tolerance": tolerance,
            "pass": all(x <= tolerance for x in diffs.values()),
            "protected_forecast_rows": forecast_n, "protected_decisions": nt, "protected_earning_rows": nr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("synthetic", "actual"), required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    prototype_path = ROOT / "prototype.py"
    write_json(args.out / "invocation.json", {"argv": sys.argv, "python": sys.version,
               "numpy": np.__version__, "pandas": pd.__version__, "mode": args.mode,
               "plan_sha256": sha(ROOT / "PLAN.md"), "controller_sha256": sha(__file__),
               "blas_environment": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}})
    shutil.copyfile(__file__, args.out / "executed_controller.py")
    if not prototype_path.exists():
        write_json(args.out / "status.json", {"status": "EXPECTED_RED_MISSING_PROTOTYPE", "economic_runs": 0})
        raise SystemExit(3)
    shutil.copyfile(prototype_path, args.out / "executed_prototype.py")
    clean = args.out / "clean"
    for rel in SOURCE_FILES:
        dest = clean / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SNAPSHOT / rel, dest)
    identities = {rel: sha(clean / rel) for rel in SOURCE_FILES}
    assert identities[SOURCE_FILES[-1]] == SCORER_SHA
    write_json(args.out / "source_manifest.json", {"commit": "ce3fe4e76271709422165d6f24e2fbecd9d0fe07",
               "source_sha256": identities, "prototype_sha256": sha(prototype_path)})
    sys.path.insert(0, str(clean / "handoff_v2"))
    strategy = load_module("baseline_strategy", clean / "handoff_v2/strategy.py")
    from model_v2 import engine
    score = load_module("unchanged_score", clean / SOURCE_FILES[-1])
    prototype = load_module("research_prototype", prototype_path)
    findings = {}
    if args.mode == "synthetic":
        R, X, c = fixture(engine, fixed=True)
        constant_v2 = run_case(engine, score, prototype, "V2", R, X, c, args.out / "constant_V2")
        constant_f1 = run_case(engine, score, prototype, "F1", R, X, c, args.out / "constant_F1")
        equivalence = compare(constant_v2, constant_f1, tolerance=1e-9)
        equivalence["pass"] &= equivalence["max_differences"]["forecast"] <= 1e-12 and bool(np.max(np.abs(constant_v2["forecast"])) > 0)
        findings["constant_Gram_F1"] = equivalence
        R, X, c = fixture(engine)
        np.savez_compressed(args.out / "synthetic_inputs.npz", returns=R, characteristics=X, costs=c)
        cut, prefix = 320, 360
    else:
        inputs = {name: sha(DATA / name) for name in ("returns.csv", "characteristics.csv", "costs.csv")}
        reference = json.loads((REPO / "evidence/v2_followup_review_20261028/replay_V2_002/input_hashes.json").read_text())
        assert inputs == reference, (inputs, reference)
        write_json(args.out / "input_hashes.json", inputs)
        R = np.ascontiguousarray(pd.read_csv(DATA / "returns.csv", index_col="day").to_numpy(np.float64))
        X = np.ascontiguousarray(pd.read_csv(DATA / "characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
        c = pd.read_csv(DATA / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
        baseline = run_case(engine, score, prototype, "V2", R, X, c, args.out / "baseline_V2")
        recorded = np.load(SNAPSHOT / "research/v2/results/ledgers/net_fr_beta_phi03_x5.npy")
        rows = baseline["rows"]
        now = np.vstack([baseline["days"], rows[:, 0] - rows[:, 1], rows[:, 0], rows[:, 1], rows[:, 3]])
        diff = np.max(np.abs(now - recorded), axis=1)
        findings["baseline_reproduction"] = {"max_differences": diff.tolist(), "pass": bool(np.all(diff <= 1e-8))}
        cut, prefix = 1500, 1500
    rng = np.random.default_rng(20261029)
    Ra = R.copy(); Xa = X.copy()
    Ra[cut:] = rng.normal(0, .025, Ra[cut:].shape)
    Xa[cut:] = rng.normal(0, 3, Xa[cut:].shape)
    Ra, Xa = np.asfortranarray(Ra), np.asfortranarray(Xa)
    for variant in ("F1", "F2"):
        b = run_case(engine, score, prototype, variant, R, X, c, args.out / (variant + "_base"))
        if args.mode == "synthetic":
            rep = run_case(engine, score, prototype, variant, R, X, c, args.out / (variant + "_repeat"))
            findings[variant + "_repeat"] = compare(b, rep)
        future = run_case(engine, score, prototype, variant, Ra, Xa, c, args.out / (variant + "_future"))
        findings[variant + "_future"] = compare(b, future, cut=cut)
        short = run_case(engine, score, prototype, variant, R[:prefix], X[:prefix], c, args.out / (variant + "_prefix"))
        findings[variant + "_prefix"] = compare(b, short)
        if args.mode == "synthetic":
            zero = run_case(engine, score, prototype, variant, np.zeros_like(R), X, c, args.out / (variant + "_zero"))
            findings[variant + "_zero"] = {"pass": bool(np.all(zero["forecast"] == 0) and np.all(zero["targets"] == 0) and np.all(zero["rows"][:, :4] == 0))}
    findings["source_identity"] = {"pass": identities == {rel: sha(clean / rel) for rel in SOURCE_FILES}}
    write_json(args.out / "verification.json", findings)
    write_json(args.out / "status.json", {"status": "PASS" if all(v["pass"] for v in findings.values()) else "FAIL",
               "checks": len(findings), "prototype_sha256": sha(prototype_path)})
    print(json.dumps(findings, indent=2), flush=True)
    assert all(v["pass"] for v in findings.values()), findings


if __name__ == "__main__":
    main()
