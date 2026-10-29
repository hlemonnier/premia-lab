"""Prospective complete-scorer F3 harness; written before prototype.py."""
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
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
COMMIT = "ce3fe4e76271709422165d6f24e2fbecd9d0fe07"
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
FILES = ["handoff_v2/strategy.py", "handoff_v2/model_v2/__init__.py",
         "handoff_v2/model_v2/engine.py", "handoff_v2/model_v2/allocator.py",
         "source/Quant Research Take-Home/score.py"]
LOCAL = ["e2e.py", "prototype.py", "baseline_forecast.py", "overlay.py",
         "PLAN.md", "E2E_SPEC.md"]
STAGES = {"full": (253, 3779), "discovery": (253, 2015),
          "validation": (2016, 3023), "audit": (3024, 3779)}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def array_sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def difference(a, b):
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b)), initial=0.0))


def atomic_array(path, a):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("wb") as f:
        np.save(f, a, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)
    saved = np.load(path, mmap_mode="r", allow_pickle=False)
    assert saved.shape == a.shape and saved.dtype == a.dtype
    assert array_sha(saved) == array_sha(a)
    return {"path": path.name, "shape": list(a.shape), "dtype": str(a.dtype),
            "sha256": sha(path), "array_sha256": array_sha(a), "readback": True}


def load_baseline(snapshot, out):
    for rel in FILES:
        dest = out / "source" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot / rel, dest)
    identities = {rel: sha(out / "source" / rel) for rel in FILES}
    assert identities[FILES[-1]] == SCORER_SHA
    sys.path.insert(0, str(out / "source/handoff_v2"))
    strategy = module("f3_baseline_strategy", out / "source/handoff_v2/strategy.py")
    engine = strategy._engine
    scorer = module("f3_original_scorer", out / "source" / FILES[-1])
    dump(out / "source_manifest.json", {"commit": COMMIT, "sha256": identities})
    return engine, dict(engine.CONFIG), scorer, identities


def state_reference(market):
    """Independent explicit historical weights, not online recursive moments."""
    n = len(market)
    c = np.zeros(n)
    q = {63: np.zeros(n), 1008: np.zeros(n)}
    for s in range(n):
        for h in q:
            weights = (2.0 ** (-1.0 / h)) ** np.arange(s, -1, -1)
            q[h][s] = float(weights @ (market[:s + 1] ** 2) / weights.sum())
        if s >= 62:
            c[s] = np.clip(np.log(max(q[1008][s], 1e-12) / max(q[63][s], 1e-12))
                           / (2 * np.log(2.0)), -1.0, 1.0)
    return c, q


def fixture(engine, zero_market=False):
    rng = np.random.default_rng(20261029)
    T, N = 640, 64
    X = np.empty((T, N, 13))
    X[0] = rng.normal(size=(N, 13))
    for t in range(1, T):
        X[t] = .95 * X[t - 1] + np.sqrt(1 - .95 ** 2) * rng.normal(size=(N, 13))
    scale = np.where((np.arange(T) // 80) % 2 == 0, .003, .020)
    market = np.zeros(T) if zero_market else scale * rng.normal(size=T)
    state, _ = state_reference(market)
    gamma = np.zeros(26)
    gamma[0], gamma[1], gamma[13] = .003, -.0025, .0015
    R = np.zeros((T, N))
    truth = np.zeros_like(R)
    R[0] = market[0]
    for t in range(1, T):
        D = engine.basis(X[t - 1])
        truth[t] = state[t - 1] * (D @ gamma) + .0003 * D[:, 2]
        noise = rng.normal(0, .0003, N)
        noise -= noise.mean()
        R[t] = market[t] + truth[t] + noise
    return np.ascontiguousarray(R), np.ascontiguousarray(X), np.linspace(.0001, .0005, N), truth, gamma


def direct_forecast_oracle(engine, R, X, t, state):
    beta, market = engine.causal_betas(R, engine.CONFIG["beta_window"])
    residual = R - beta * market[:, None]

    def design(s):
        base = np.hstack([engine.basis(X[s], engine.CONFIG["feature_clip"]),
                          engine._zcol(beta[s + 1], engine.CONFIG["feature_clip"])[:, None]])
        return np.hstack([base, state[s] * base[:, :26]])

    grams, scores = [], []
    for j in range(1, t):
        D = design(j - 1)
        grams.append(D.T @ D / R.shape[1])
        scores.append(D.T @ residual[j] / R.shape[1])
    grams, scores = np.asarray(grams), np.asarray(scores)
    penalty = np.diag(np.r_[np.full(27, .1), np.ones(26)])
    coefs = []
    for h in (1008, 252):
        weights = (2.0 ** (-1.0 / h)) ** np.arange(t - 2, -1, -1)
        weights /= weights.sum()
        gram = np.einsum("t,tij->ij", weights, grams)
        moment = weights @ scores
        coefs.append(np.linalg.solve(gram + penalty, moment))
    coef = coefs[0].copy()
    coef[:13] = .5 * coefs[0][:13] + .5 * coefs[1][:13]
    return design(t - 1) @ coef


def make_wrapper(engine, config, variant, policy, baseline, overlay):
    engine.forecast = baseline.make_forecast(engine, "F2") if variant == "F2" else policy.make_forecast(engine)
    return overlay.VolatilityOverlay(engine, config, power=.5)


def performance(rows, runtime=False):
    if runtime:
        return {}
    days = np.arange(253, 253 + len(rows))
    result = {}
    for name, (lo, hi) in STAGES.items():
        k = (days >= lo) & (days < hi)
        if not k.any():
            continue
        g, fee, gross, market, secs = rows[k].T
        net = g - fee
        mv, nv = float(market.var()), float(net.var())
        result[name] = {"n": int(k.sum()),
            "net_sharpe": float(np.sqrt(252) * net.mean() / np.sqrt(nv)) if nv else None,
            "net_return_ann_pct": float(25200 * net.mean()),
            "net_vol_ann_pct": float(100 * np.sqrt(252 * nv)),
            "cost_ann_pct": float(25200 * fee.mean()),
            "gross_sharpe": float(np.sqrt(252) * g.mean() / g.std()) if g.std() else None,
            "net_beta": float((market - market.mean()) @ (net - net.mean()) / (len(net) * mv)) if mv else None,
            "mean_gross": float(gross.mean()), "worst_gross_daily_return": float(g.min())}
    return result


def execute(engine, scorer, wrapper, R, X, costs, out, runtime=False):
    out.mkdir(parents=True, exist_ok=False)
    before = [array_sha(a) for a in (R, X, costs)]
    started = time.perf_counter()
    rows, fsec = scorer.run(wrapper, R, X, costs)
    elapsed = time.perf_counter() - started
    pred = wrapper.forecast_output
    targets = np.asarray([r["actual_target"] for r in wrapper.records])
    virtual = np.asarray([r["virtual_target"] for r in wrapper.records])
    records = [{k: v for k, v in r.items() if k not in ("actual_target", "virtual_target")}
               for r in wrapper.records]
    decisions = np.asarray([r["decision_index"] for r in records])
    expected = []
    old = np.zeros(R.shape[1])
    moments = {h: [0.0, 0.0] for h in (63, 1008)}
    multipliers = []
    for j, (r, w) in enumerate(zip(records, targets)):
        t = r["decision_index"]
        gross = float(old @ R[t])
        assert gross > -1
        held = old * (1 + R[t]) / (1 + gross)
        fee = 0.0 if j == 0 else float(costs @ np.abs(w - held))
        expected.append([gross, fee, float(np.abs(w).sum()), float(R[t].mean())])
        if j:
            vg = float(virtual[j - 1] @ R[t])
            for h, acc in moments.items():
                d = 2.0 ** (-1.0 / h)
                acc[0], acc[1] = d * acc[0] + vg * vg, d * acc[1] + 1
        q = {h: a[0] / a[1] if a[1] else 0.0 for h, a in moments.items()}
        multipliers.append(1.0 if j < 63 else float(np.clip(
            np.sqrt(max(q[1008], 1e-12) / max(q[63], 1e-12)), .5, 2)))
        old = w
    accounting_error = difference(np.asarray(expected)[1:], rows[:, :4])
    multiplier_error = difference(multipliers, [r["multiplier"] for r in records])
    trace = {k: np.asarray(v).copy() for k, v in getattr(engine.forecast, "diagnostics", {}).items()}
    checks = {
        "finite": bool(np.isfinite(rows).all() and np.isfinite(pred).all() and np.isfinite(targets).all()),
        "solvent": bool(np.min(rows[:, 0]) > -1),
        "input_unchanged": before == [array_sha(a) for a in (R, X, costs)],
        "economic_rows": len(rows) == len(R) - 254,
        "decision_rows": len(records) == len(R) - 253,
        "decision_clock": bool(np.array_equal(decisions, np.arange(252, len(R) - 1))),
        "scorer_accounting": accounting_error <= 1e-12,
        "held_drift": max(r["supplied_held_identity_error"] for r in records) <= 1e-12,
        "warmup": bool(np.all(pred[:127] == 0)),
        "stock_bound": float(np.max(np.abs(targets))) <= .1 + 1e-12,
        "gross_bound": float(np.max(np.abs(targets).sum(axis=1))) <= 5 + 1e-12,
        "certificates": all(r["certificate_status"] in ("ok", "ok_after_recovery") for r in records),
        "multiplier_clock": multiplier_error <= 1e-12,
        "opening_free": records[0]["actual_fee"] == 0.0,
        "last_rebalance_charged": abs(rows[-1, 1] - records[-1]["actual_fee"]) <= 1e-12,
    }
    p = performance(rows, runtime)
    summary = {"checks": checks, "performance": p, "forecast_seconds": fsec,
        "rebalance_ms_mean": float(1000 * rows[:, 4].mean()),
        "rebalance_ms_p99": float(1000 * np.quantile(rows[:, 4], .99)),
        "wall_seconds": elapsed, "accounting_max_error": accounting_error,
        "multiplier_max_error": multiplier_error, "input_array_sha256": before,
        "forecast_sha256": array_sha(pred), "targets_sha256": array_sha(targets),
        "virtual_targets_sha256": array_sha(virtual), "configuration": dict(engine.CONFIG),
        "instrumented_research_runtime": True, "runtime_stress_only": runtime}
    manifest = {}
    arrays = {"forecast": pred, "targets": targets, "virtual_targets": virtual,
              "rows": rows, "decision_indices": decisions}
    arrays.update({"trace_" + k: v for k, v in trace.items()})
    for name, a in arrays.items():
        manifest[name] = atomic_array(out / (name + ".npy"), a)
    dump(out / "array_manifest.json", manifest)
    with (out / "daily.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["return_index", "gross_return", "full_cost", "net_return",
                    "closing_target_gross", "market_return", "instrumented_rebalance_seconds"])
        for t, r in zip(range(253, len(R) - 1), rows):
            g, fee, gross, m, seconds = r
            w.writerow([t, g, fee, g - fee, gross, m, seconds])
    with (out / "decisions.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]))
        w.writeheader()
        w.writerows(records)
    dump(out / "summary.json", summary)
    print(json.dumps({"case": out.name, "performance": p.get("full"),
                      "all_workflow_checks": all(checks.values()),
                      "forecast_seconds": fsec, "mean_rebalance_ms": summary["rebalance_ms_mean"]}), flush=True)
    return {"forecast": pred, "targets": targets, "virtual": virtual, "rows": rows,
            "decisions": decisions, "records": records, "trace": trace, "summary": summary}


def compare(base, alt, cut=None, exact_forecast=True, target_tolerance=1e-8, economic_tolerance=1e-8):
    nforecast = len(alt["forecast"]) if cut is None else cut + 1
    limit = len(alt["forecast"]) if cut is None else cut
    nt = int(np.sum(alt["decisions"] < limit))
    day = np.arange(253, 253 + len(alt["rows"]))
    nr = int(np.sum(day < limit))
    errors = {"forecast": difference(base["forecast"][:nforecast], alt["forecast"][:nforecast]),
              "targets": difference(base["targets"][:nt], alt["targets"][:nt]),
              "economics": difference(base["rows"][:nr, :4], alt["rows"][:nr, :4])}
    passed = errors["forecast"] <= (0.0 if exact_forecast else 1e-12)
    passed &= errors["targets"] <= target_tolerance and errors["economics"] <= economic_tolerance
    return {"pass": bool(passed), "max_differences": errors, "protected_forecast_rows": nforecast,
            "protected_decisions": nt, "protected_earning_rows": nr}


def load_actual(data, out):
    names = ("returns.csv", "characteristics.csv", "costs.csv")
    hashes = {name: sha(data / name) for name in names}
    reference = json.loads((REPO / "evidence/v2_followup_review_20261028/replay_V2_002/input_hashes.json").read_text())
    assert hashes == reference
    dump(out / "input_hashes.json", hashes)
    R = np.ascontiguousarray(pd.read_csv(data / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(data / "characteristics.csv", index_col=["day", "stock"])
                             .to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
    costs = pd.read_csv(data / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    assert R.shape == (3780, 1000) and X.shape == (3780, 1000, 13)
    return R, X, costs


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
    if not (ROOT / "prototype.py").exists():
        dump(args.out / "status.json", {"status": "EXPECTED_RED_MISSING_PROTOTYPE", "economic_runs": 0})
        raise SystemExit(3)
    local_hashes = {name: sha(ROOT / name) for name in LOCAL}
    if args.mode != "synthetic":
        if args.release is None:
            raise RuntimeError("Actual/runtime execution requires a source-bound root release")
        release = json.loads(args.release.read_text())
        assert release.get("allow_" + args.mode) is True
        assert release["source_sha256"] == local_hashes
        dump(args.out / "release_readback.json", {"path": str(args.release), "sha256": sha(args.release), "release": release})
    for name in LOCAL:
        shutil.copyfile(ROOT / name, args.out / ("executed_" + name))
    dump(args.out / "local_source_manifest.json", local_hashes)
    engine, config, scorer, identities = load_baseline(args.snapshot, args.out)
    policy = module("f3_policy", ROOT / "prototype.py")
    baseline = module("f3_reference_forecast", ROOT / "baseline_forecast.py")
    overlay = module("f3_reference_overlay", ROOT / "overlay.py")
    findings, runs = {}, []

    def run(name, variant, R, X, costs, wrapper=None, runtime=False):
        if wrapper is None:
            wrapper = make_wrapper(engine, config, variant, policy, baseline, overlay)
        r = execute(engine, scorer, wrapper, R, X, costs, args.out / name, runtime)
        runs.append(r["summary"])
        return wrapper, r

    if args.mode == "runtime":
        R0, X0, costs = load_actual(args.data, args.out)
        T, N = 25200, R0.shape[1]
        panel_path = args.out / "runtime_characteristics.npy"
        panel = np.lib.format.open_memmap(panel_path, mode="w+", dtype=np.float64, shape=(T, N, 13))
        for start in range(0, T, len(R0)):
            panel[start:min(T, start + len(R0))] = X0[:min(len(R0), T - start)]
        panel.flush()
        del panel
        X = np.load(panel_path, mmap_mode="r")
        R = np.ascontiguousarray(R0[np.arange(T) % len(R0)])
        wrapper, stress = run("runtime_F3_VTvol", "F3", R, X, costs, runtime=True)
        findings["runtime_gate"] = {"pass": bool(len(os.sched_getaffinity(0)) == 1
            and stress["summary"]["forecast_seconds"] < 3600
            and stress["summary"]["rebalance_ms_mean"] < 100),
            "rows": T, "stocks": N, "not_alpha_evidence": True,
            "production_integration_gate": False}
    else:
        if args.mode == "synthetic":
            Rz, Xz, costs, _, _ = fixture(engine, zero_market=True)
            _, f2z = run("state_zero_F2", "F2", Rz, Xz, costs)
            _, f3z = run("state_zero_F3", "F3", Rz, Xz, costs)
            findings["state_zero_equivalence"] = compare(f2z, f3z, exact_forecast=False)
            findings["state_zero_trace"] = {"pass": bool(np.all(f3z["trace"]["market_state"] == 0))}
            R, X, costs, truth, gamma = fixture(engine)
            _, base_f2 = run("conditional_F2", "F2", R, X, costs)
            cut = 400
        else:
            R, X, costs = load_actual(args.data, args.out)
            _, base_f2 = run("baseline_F2_VTvol", "F2", R, X, costs)
            old_path = REPO / "evidence/v2_score_joint_20261028/actual_001/joint_F2_VTvol/daily.csv"
            old = pd.read_csv(old_path)
            expected = old[["gross_return", "full_cost", "closing_target_gross", "market_return"]].to_numpy()
            err = difference(expected, base_f2["rows"][:, :4])
            findings["baseline_reproduction"] = {"pass": err <= 1e-8, "max_difference": err,
                "reference_path": str(old_path), "reference_sha256": sha(old_path)}
            cut = 1500
        wrapper, candidate = run("F3_VTvol", "F3", R, X, costs)
        state, q = state_reference(R.mean(axis=1))
        trace = candidate["trace"]
        state_error = difference(state, trace["market_state"])
        findings["state_reconstruction"] = {"pass": bool(state_error <= 1e-12
            and difference(q[63], trace["market_q63"]) <= 1e-12
            and difference(q[1008], trace["market_q1008"]) <= 1e-12
            and np.all(trace["market_state"][:62] == 0)
            and np.max(np.abs(trace["market_state"])) <= 1), "max_difference": state_error}
        if args.mode == "synthetic":
            oracle_errors = {str(t): difference(direct_forecast_oracle(engine, R, X, t, state),
                            candidate["forecast"][t]) for t in (127, 253, 319, 639)}
            alignment = float(trace["coefficients"][-1, 27:] @ gamma)
            corr = float(np.corrcoef(candidate["forecast"][300:].ravel(), truth[300:].ravel())[0, 1])
            findings["known_conditional_wiring"] = {"pass": bool(max(oracle_errors.values()) <= 1e-10
                and alignment > 0 and difference(candidate["forecast"], base_f2["forecast"]) > 1e-10
                and np.ptp(state[62:]) > .1), "oracle_max_errors": oracle_errors,
                "conditional_coefficient_truth_dot": alignment, "truth_correlation_diagnostic": corr}
        rng = np.random.default_rng(20261030)
        R2, X2 = R.copy(), X.copy()
        R2[cut:] = rng.normal(0, .02, R2[cut:].shape)
        X2[cut:] = rng.normal(size=X2[cut:].shape)
        _, future = run("F3_future", "F3", R2, X2, costs, wrapper)
        findings["future"] = compare(candidate, future, cut=cut)
        _, prefix = run("F3_prefix", "F3", R[:cut + 1], X[:cut + 1], costs, wrapper)
        findings["prefix"] = compare(candidate, prefix)
        if args.mode == "synthetic":
            _, zero = run("F3_zero_returns", "F3", np.zeros_like(R), X, costs, wrapper)
            findings["zero_cash"] = {"pass": bool(np.all(zero["forecast"] == 0)
                and np.all(zero["targets"] == 0) and np.all(zero["rows"][:, :4] == 0)
                and zero["summary"]["performance"]["full"]["net_sharpe"] is None
                and zero["summary"]["performance"]["full"]["net_beta"] is None)}
            _, repeated = run("F3_restart", "F3", R, X, costs, wrapper)
            findings["restart"] = compare(candidate, repeated, target_tolerance=0.0, economic_tolerance=1e-12)
        else:
            delta = (candidate["summary"]["performance"]["full"]["net_sharpe"]
                     - base_f2["summary"]["performance"]["full"]["net_sharpe"])
            dump(args.out / "economic_comparison.json", {"baseline": base_f2["summary"],
                "candidate": candidate["summary"], "net_sharpe_change": delta,
                "all_history_is_development": True, "final_selection_requires_independent_readback": True})
    findings["all_workflow_checks"] = {"pass": all(all(r["checks"].values()) for r in runs)}
    findings["source_unchanged"] = {"pass": identities == {rel: sha(args.out / "source" / rel) for rel in FILES}
        and local_hashes == {name: sha(ROOT / name) for name in LOCAL}}
    result = {"mode": args.mode, "checks": findings, "all_passed": all(f["pass"] for f in findings.values()),
              "source_commit": COMMIT, "source_sha256": local_hashes,
              "policy_variants": ["F2_VTvol", "F3_VTvol"], "production_modified": False}
    dump(args.out / "result.json", result)
    dump(args.out / "artifact_manifest.json", {str(p.relative_to(args.out)): sha(p)
        for p in sorted(args.out.rglob("*")) if p.is_file() and "__pycache__" not in str(p)})
    print(json.dumps(result, indent=2), flush=True)
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
