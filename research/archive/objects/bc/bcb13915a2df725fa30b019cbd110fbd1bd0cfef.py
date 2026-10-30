"""Observe the exact latest package through the unchanged scorer.

No model edits or additional optimizer calls. See LATEST_PACKAGE_REPLAY_PLAN.md.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

COMMIT = "ce3fe4e76271709422165d6f24e2fbecd9d0fe07"
OVERRIDES = {"V2": {}, "B0": {"beta_shrinkage": True, "beta_target": 0.0},
             "B05": {"beta_shrinkage": True, "beta_target": 0.05}}
LEDGERS = {"V2": "fr_beta_phi03_x5", "B0": "V2_B0_beta_neutral", "B05": "V2_B05_explicit_beta"}
STAGES = {"full": (253, 3779), "discovery": (253, 2015),
          "validation": (2016, 3023), "audit": (3024, 3779)}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--policy", choices=OVERRIDES, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    clean = args.out / "clean"
    files = ["handoff_v2/strategy.py", "handoff_v2/model_v2/__init__.py",
             "handoff_v2/model_v2/engine.py", "handoff_v2/model_v2/allocator.py",
             "source/Quant Research Take-Home/score.py"]
    for rel in files:
        target = clean / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.snapshot / rel, target)
    identities = {rel: sha(clean / rel) for rel in files}
    write_json(args.out / "source_manifest.json", {"commit": COMMIT, "sha256": identities})
    shutil.copyfile(__file__, args.out / "executed_observer.py")
    write_json(args.out / "input_hashes.json", {
        name: sha(args.data / name) for name in ("returns.csv", "characteristics.csv", "costs.csv")})
    sys.path.insert(0, str(clean / "handoff_v2"))
    strategy = load_module("observed_strategy", clean / "handoff_v2/strategy.py")
    from model_v2 import engine
    score = load_module("original_score", clean / "source/Quant Research Take-Home/score.py")
    engine.configure({**engine.CONFIG, **OVERRIDES[args.policy]})
    write_json(args.out / "environment.json", {
        "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
        "platform": platform.platform(), "argv": sys.argv, "configuration": engine.CONFIG,
        "instrumented_runtime": True,
    })
    R = np.ascontiguousarray(pd.read_csv(args.data / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(args.data / "characteristics.csv", index_col=["day", "stock"])
                             .to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    costs = pd.read_csv(args.data / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    original_allocate = engine.allocate_factor
    latest = {}

    def observe_allocate(*positional, **keywords):
        w = original_allocate(*positional, **keywords)
        # The exact engine call supplies beta as positional argument 5.
        latest["pre_gross"] = float(np.abs(w).sum())
        latest["allocator_beta"] = np.array(positional[5], copy=True)
        latest["pre_beta"] = float(positional[5] @ w)
        return w

    engine.allocate_factor = observe_allocate
    observations = []

    def observe_rebalance(held_positions, expected_returns, returns_history,
                          characteristics_history, trading_costs):
        w = strategy.rebalance(held_positions=held_positions, expected_returns=expected_returns,
                               returns_history=returns_history, characteristics_history=characteristics_history,
                               trading_costs=trading_costs)
        # Pure reads of state already consumed by the real decision; no eta update.
        slopes = engine._STATE.eta.slopes
        eta = 1.0 - float(np.mean(slopes)) if engine.CONFIG["beta_shrinkage"] and slopes else 0.0
        raw = engine._window_beta(np.ascontiguousarray(returns_history, dtype=np.float64),
                                  engine.CONFIG["beta_window"])
        corrected = (1.0 - eta) * raw + eta * raw.mean()
        cert = engine.CERTIFICATES[-1]
        gross = float(np.abs(w).sum())
        observations.append({
            "decision_index": len(returns_history) - 1,
            "pre_gross": latest["pre_gross"], "post_gross": gross,
            "gross_scale": gross / latest["pre_gross"] if latest["pre_gross"] else 1.0,
            "net_dollars": float(w.sum()), "max_abs_weight": float(np.max(np.abs(w))),
            "raw_estimated_beta": float(raw @ w), "corrected_estimated_beta": float(corrected @ w),
            "pre_hedge_beta": latest["pre_beta"],
            "post_hedge_beta": float(latest["allocator_beta"] @ w),
            "post_target_error": float(latest["allocator_beta"] @ w - engine.CONFIG["beta_target"]),
            "eta": eta, "certificate_status": cert["status"],
            "certificate_gap": cert["gap"], "all_finite": bool(np.isfinite(w).all()),
        })
        return w

    shim = type("ObservedPackage", (), {"forecast": staticmethod(strategy.forecast),
                                        "rebalance": staticmethod(observe_rebalance)})
    started = time.perf_counter()
    rows, forecast_seconds = score.run(shim, R, X, costs)
    wall_seconds = time.perf_counter() - started
    pr, fee, gross_exposure, market, seconds = rows.T
    day = np.arange(253, 253 + len(rows))
    ledger = pd.DataFrame({"return_index": day, "gross_return": pr, "full_cost": fee,
                           "net_return": pr - fee, "closing_target_gross": gross_exposure,
                           "market_return": market, "instrumented_rebalance_seconds": seconds})
    ledger.to_csv(args.out / "daily.csv", index=False)
    with (args.out / "decisions.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(observations[0]))
        writer.writeheader()
        writer.writerows(observations)
    obs = pd.DataFrame(observations)
    expected = np.load(args.snapshot / f"research/v2/results/ledgers/net_{LEDGERS[args.policy]}.npy")
    actual = np.vstack((day, pr - fee, pr, fee, market))
    diffs = np.max(np.abs(actual - expected), axis=1)
    summaries = {}
    for name, (lo, hi) in STAGES.items():
        mask = (day >= lo) & (day < hi)
        net = (pr - fee)[mask]
        m = market[mask]
        summaries[name] = {"sharpe": float(np.sqrt(252) * net.mean() / net.std()),
                           "ret_pct": float(25200 * net.mean()),
                           "vol_pct": float(100 * np.sqrt(252) * net.std()),
                           "net_beta": float(np.cov(net, m, ddof=0)[0, 1] / np.var(m))}
    summary = {"policy": args.policy, "rows": len(rows), "decisions": len(observations),
               "configuration": dict(engine.CONFIG), "performance": summaries,
               "max_differences_from_committed_day_net_gross_fee_market": diffs.tolist(),
               "max_pre_gross": float(obs.pre_gross.max()), "max_post_gross": float(obs.post_gross.max()),
               "gross_scaled_decisions": int(np.sum(obs.pre_gross > engine.CONFIG["gross_cap"])),
               "max_abs_target_beta_error": float(obs.post_target_error.abs().max()),
               "max_abs_weight": float(obs.max_abs_weight.max()),
               "mean_net_dollars": float(obs.net_dollars.mean()),
               "certificate_statuses": obs.certificate_status.value_counts().to_dict(),
               "max_abs_certificate_gap": float(obs.certificate_gap.abs().max()),
               "forecast_seconds": forecast_seconds, "instrumented_wall_seconds": wall_seconds,
               "source_unchanged": identities == {rel: sha(clean / rel) for rel in files},
               "checks": {"earning_rows": len(rows) == 3526, "decision_rows": len(observations) == 3527,
                          "committed_ledger_tolerance": bool(np.all(diffs <= 1e-8)),
                          "all_certified": bool(obs.certificate_status.isin(["ok", "ok_after_recovery"]).all()),
                          "all_finite": bool(obs.all_finite.all()),
                          "stock_caps": bool(obs.max_abs_weight.max() <= engine.CONFIG["weight_cap"]),
                          "gross_cap": bool(obs.post_gross.max() <= engine.CONFIG["gross_cap"] + 1e-12),
                          "final_target_hedge": bool(obs.post_target_error.abs().max() <= 1e-11)}}
    write_json(args.out / "summary.json", summary)
    write_json(args.out / "artifact_manifest.json", {
        str(p.relative_to(args.out)): sha(p) for p in sorted(args.out.rglob("*")) if p.is_file()})
    print(json.dumps(summary, indent=2))
    if not all(summary["checks"].values()) or not summary["source_unchanged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
