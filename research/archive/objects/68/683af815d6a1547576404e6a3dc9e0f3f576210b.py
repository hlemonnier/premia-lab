"""Replay an unchanged submission with the original scorer and observational hooks.

See PLAN.md, written before this harness. This is an audit workflow, not a new
strategy, a new forecast fit, or a parameter-selection experiment.
"""
import argparse
import csv
import hashlib
import importlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_info


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(2**20), b""):
            h.update(b)
    return h.hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def array_info(a):
    h = hashlib.sha256()
    for lo in range(0, len(a), 16):
        h.update(a[lo:lo + 16].tobytes(order="C"))
    return dict(shape=list(a.shape), dtype=str(a.dtype), strides=list(a.strides),
                c_contiguous=bool(a.flags.c_contiguous), f_contiguous=bool(a.flags.f_contiguous),
                logical_c_order_sha256=h.hexdigest())


def metrics(rows):
    net = rows[:, 0] - rows[:, 1]
    mc = rows[:, 3] - rows[:, 3].mean()
    return dict(n=len(rows), sharpe=float(net.mean() / net.std() * np.sqrt(252)),
                gross_sharpe=float(rows[:, 0].mean() / rows[:, 0].std() * np.sqrt(252)),
                annual_net=float(net.mean() * 252), annual_vol=float(net.std() * np.sqrt(252)),
                annual_cost=float(rows[:, 1].mean() * 252),
                beta=float(mc @ (net - net.mean()) / (mc @ mc)),
                mean_gross=float(rows[:, 2].mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", choices=["c09", "v2"], required=True)
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--scorer", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--expected-inputs", type=Path, required=True)
    ap.add_argument("--baseline-ledger", type=Path)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    clean = out / "clean"
    clean.mkdir()
    for src in args.package.rglob("*.py"):
        if "__pycache__" in src.parts:
            continue
        dst = clean / src.relative_to(args.package)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    shutil.copyfile(args.scorer, clean / "score.py")
    shutil.copyfile(__file__, out / "replay.py")
    write_json(out / "source_manifest.json", {
        str(p.relative_to(clean)): digest(p) for p in sorted(clean.rglob("*.py"))})
    expected = json.loads(args.expected_inputs.read_text())["source_sha256"]
    actual = {name: digest(args.data / name) for name in expected}
    assert actual == expected, (actual, expected)
    write_json(out / "input_csv_hashes.json", actual)
    write_json(out / "environment.json", dict(
        python=sys.version, executable=sys.executable, platform=platform.platform(),
        numpy=np.__version__, pandas=pd.__version__, threadpools=threadpool_info(),
        thread_env={k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        argv=sys.argv, cwd=os.getcwd()))
    spec = importlib.util.spec_from_file_location("original_score", clean / "score.py")
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    R, X, cost = scorer.load(str(args.data))
    assert R.shape == (3780, 1000) and X.shape == (3780, 1000, 13)
    write_json(out / "loaded_arrays.json", {name: array_info(a) for name, a in [("returns", R), ("characteristics", X), ("costs", cost)]})
    sys.path.insert(0, str(clean))
    strategy = importlib.import_module("strategy")
    engine = strategy._engine if args.policy == "v2" else None
    original_forecast = strategy.forecast
    original_rebalance = strategy.rebalance
    held, targets, observations = [], [], []
    capture = {}
    allocation = {}

    def observe_forecast(returns_history, characteristics_history):
        if engine is None:
            pred = original_forecast(returns_history, characteristics_history)
        else:
            solve = np.linalg.solve
            betas = engine.causal_betas
            coefficients = []

            def observed_solve(a, b):
                ans = solve(a, b)
                assert a.shape == (27, 27) and b.shape == (27,)
                coefficients.append(ans.copy())
                return ans

            def observed_betas(*a, **kw):
                ans = betas(*a, **kw)
                capture["betas"] = ans[0]
                return ans

            np.linalg.solve = observed_solve
            engine.causal_betas = observed_betas
            try:
                pred = original_forecast(returns_history, characteristics_history)
            finally:
                np.linalg.solve = solve
                engine.causal_betas = betas
            coefs = np.zeros((len(returns_history), 27))
            first = int(engine.CONFIG["min_training_days"]) + 1
            assert len(coefficients) == len(returns_history) - first
            coefs[first:] = coefficients
            capture["coefs"] = coefs
            np.save(out / "existing_forecast_coefficients.npy", coefs)
        np.save(out / "forecasts.npy", pred)
        return pred

    if engine is not None:
        original_allocate = engine.allocate_factor

        def observed_allocate(mu, h, d, B, L, beta, kappa, gamma, cap, warm=None, **kw):
            w = original_allocate(mu, h, d, B, L, beta, kappa, gamma, cap, warm=warm, **kw)
            capv = np.broadcast_to(np.asarray(cap, dtype=float), w.shape)
            M = B @ L
            theta = warm["theta"]
            r = M.shape[1]
            lam = theta[:r]
            bs = float(np.max(np.abs(beta[capv > 0])))
            bn = beta / bs if bs else np.zeros_like(beta)
            nu = theta[r] if bs else 0.0
            q = M.T @ w - lam / gamma
            e = float(bn @ w)
            risk_d = float((d * w) @ w)
            risk_f = float(np.square(M.T @ w).sum())
            P = float(mu @ w - gamma / 2 * (risk_d + risk_f) - kappa @ np.abs(w - h))
            s = mu - M @ lam - nu * bn
            U = float(s @ w - gamma / 2 * risk_d - kappa @ np.abs(w - h) + lam @ lam / (2 * gamma))
            formula_gap = float(gamma / 2 * (q @ q) - nu * e)
            allocation.clear()
            allocation.update(
                factor_residual=float(np.max(np.abs(q), initial=0.0)),
                factor_tolerance=float(kw.get("tol", 1e-13) * (1 + np.max(np.abs(lam), initial=0.0) / gamma)),
                hedge_residual=abs(e),
                hedge_tolerance=float(max(64 * np.finfo(float).eps * float(np.abs(bn) @ capv), np.nextafter(0.0, 1.0))),
                primal=P, dual=U, dual_gap=U - P, gap_formula=formula_gap,
                gap_identity_error=abs((U - P) - formula_gap),
                pre_gross=float(np.abs(w).sum()), cap_excess=float(np.max(np.abs(w) - capv)),
                predicted_specific=risk_d, predicted_factor_scaled=risk_f,
                beta=beta.copy(), pre_weights=w.copy())
            return w

        engine.allocate_factor = observed_allocate

    def observe_rebalance(held_positions, expected_returns, returns_history,
                          characteristics_history, trading_costs):
        today = len(returns_history) - 1
        held.append(np.array(held_positions, copy=True))
        w = original_rebalance(held_positions, expected_returns, returns_history,
                               characteristics_history, trading_costs)
        targets.append(np.array(w, copy=True))
        rec = dict(decision_index=today, forecast_index=today + 1,
                   net_dollars=float(w.sum()), gross=float(np.abs(w).sum()),
                   forecast_objective=float(expected_returns @ w))
        if engine is not None:
            rec.update({k: v for k, v in allocation.items() if k not in ("beta", "pre_weights")})
            scale = min(1.0, engine.CONFIG["gross_cap"] / allocation["pre_gross"]) if allocation["pre_gross"] else 1.0
            rec["gross_multiplier"] = scale
            assert np.array_equal(w, allocation["pre_weights"] * scale)
            rec["predicted_specific"] *= scale * scale
            rec["predicted_factor_scaled"] *= scale * scale
            rec["predicted_factor_unscaled"] = rec["predicted_factor_scaled"] / engine.CONFIG["factor_risk_scale"]
            bp = capture["betas"][today + 1]
            bm = float(bp.mean())
            sd = max(float(bp.std()), 1e-12)
            z0 = (bp - bm) / sd
            clip = np.clip(z0, -engine.CONFIG["feature_clip"], engine.CONFIG["feature_clip"])
            z = clip - clip.mean()
            cf = float(capture["coefs"][today + 1, -1])
            bhedge = allocation["beta"]
            rec["hedge_beta_dot_target"] = float(bhedge @ w)
            rec["beta_coefficient"] = cf
            rec["beta_forecast_objective"] = float(cf * (z @ w))
            rec["beta_net_dollar_term"] = float(-cf * bm / sd * w.sum())
            rec["beta_estimator_difference_term"] = float(cf / sd * ((bp - bhedge) @ w))
            rec["beta_hedge_tolerance_term"] = float(cf / sd * (bhedge @ w))
            rec["beta_clipping_term"] = float(cf * ((z - z0) @ w))
            rec["beta_identity_error"] = abs(rec["beta_forecast_objective"] - sum(rec[k] for k in (
                "beta_net_dollar_term", "beta_estimator_difference_term", "beta_hedge_tolerance_term", "beta_clipping_term")))
            rec["characteristics_forecast_objective"] = rec["forecast_objective"] - rec["beta_forecast_objective"]
        observations.append(rec)
        return w

    strategy.forecast = observe_forecast
    strategy.rebalance = observe_rebalance
    rows, forecast_seconds = scorer.run(strategy, R, X, cost)
    assert rows.shape == (3526, 5) and np.isfinite(rows).all()
    assert len(targets) == 3527
    np.save(out / "targets.npy", np.asarray(targets))
    np.save(out / "held.npy", np.asarray(held))
    with (out / "daily.csv").open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["return_index", "gross_return", "full_cost", "net_return", "closing_target_gross", "market_return", "instrumented_rebalance_seconds"])
        for day, row in zip(range(253, 3779), rows):
            wr.writerow([day, row[0], row[1], row[0] - row[1], row[2], row[3], row[4]])
    with (out / "decision_observations.csv").open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(observations[0]))
        wr.writeheader()
        wr.writerows(observations)
    indices = np.arange(253, 3779)
    masks = {"full": np.ones(len(rows), dtype=bool),
             "discovery": (indices >= 253) & (indices < 2015),
             "validation": (indices >= 2016) & (indices < 3023),
             "audit": (indices >= 3024) & (indices < 3779)}
    summary = {name: metrics(rows[mask]) for name, mask in masks.items()}
    expected_sr = [1.243, 1.098, 1.657, 1.148] if engine is not None else [.885, .700, .659, 1.799]
    summary["rounded_sharpe_matches_published"] = {name: round(summary[name]["sharpe"], 3) == val for name, val in zip(masks, expected_sr)}
    summary["forecast_seconds_instrumented"] = forecast_seconds
    summary["rebalance_seconds_instrumented_mean"] = float(rows[:, 4].mean())
    summary["net_dollars"] = {"mean": float(np.mean([r["net_dollars"] for r in observations])),
                              "min": float(np.min([r["net_dollars"] for r in observations])),
                              "max": float(np.max([r["net_dollars"] for r in observations]))}
    if engine is not None:
        summary["allocator"] = {
            "calls": len(observations),
            "factor_tolerance_failures": sum(r["factor_residual"] > r["factor_tolerance"] for r in observations),
            "hedge_tolerance_failures": sum(r["hedge_residual"] > r["hedge_tolerance"] for r in observations),
            "absolute_value_gap_gt_1e_10": sum(abs(r["dual_gap"]) > 1e-10 for r in observations),
            "max_factor_residual": max(r["factor_residual"] for r in observations),
            "max_dual_gap": max(r["dual_gap"] for r in observations),
            "min_dual_gap": min(r["dual_gap"] for r in observations),
            "max_gap_identity_error": max(r["gap_identity_error"] for r in observations),
            "max_beta_identity_error": max(r["beta_identity_error"] for r in observations),
            "gross_scaling_calls": sum(r["gross_multiplier"] < 1.0 for r in observations)}
        # The row earned today uses the risk predicted with yesterday's target.
        pred_d = np.array([r["predicted_specific"] for r in observations[:-1]])
        pred_f = np.array([r["predicted_factor_scaled"] for r in observations[:-1]])
        summary["risk_calibration"] = {}
        for name, mask in masks.items():
            actual2 = float(np.mean(rows[mask, 0] ** 2))
            forecast2 = float(np.mean((pred_d + pred_f)[mask]))
            summary["risk_calibration"][name] = dict(
                mean_realized_gross_squared=actual2, mean_predicted_second_moment=forecast2,
                ratio=actual2 / forecast2, mean_specific=float(pred_d[mask].mean()),
                mean_scaled_factor=float(pred_f[mask].mean()))
        summary["beta_forecast_description"] = {k: float(np.mean([r[k] for r in observations])) for k in (
            "beta_coefficient", "beta_forecast_objective", "beta_net_dollar_term",
            "beta_estimator_difference_term", "beta_hedge_tolerance_term", "beta_clipping_term",
            "forecast_objective", "characteristics_forecast_objective")}
    if args.baseline_ledger:
        original = pd.read_csv(args.baseline_ledger)
        old = original[["gross_return", "full_cost", "closing_target_gross", "raw_market_return"]].to_numpy()
        new = rows[:, :4]
        assert old.shape == new.shape
        summary["baseline_comparison"] = dict(exact=bool(np.array_equal(old, new)),
            max_abs=float(np.max(np.abs(old - new))), within_1e_10=bool(np.all(np.abs(old - new) <= 1e-10)))
    write_json(out / "summary.json", summary)
    write_json(out / "artifact_manifest.json", {str(p.relative_to(out)): dict(bytes=p.stat().st_size, sha256=digest(p))
        for p in sorted(out.rglob("*")) if p.is_file() and "__pycache__" not in p.parts and p.name != "artifact_manifest.json"})
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
