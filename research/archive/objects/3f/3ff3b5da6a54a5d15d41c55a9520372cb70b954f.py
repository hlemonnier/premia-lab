"""Stage 1 of R27_PLAN.md: score R26 and R27 risk descriptions on frozen V2 holdings.

python research/v2/r27_shadow.py --data DIR --out results/r27_shadow.json
Runs packaged V2 once through the unmodified scorer to capture its targets, then
replays two shadow risk states (physical factor scale 1) day by day.
"""
import argparse
import importlib.util
import inspect
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
import strategy as V2  # noqa: E402
from model_v2 import engine  # noqa: E402

STAGES = {"discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}


def capture_targets(R, X, c):
    spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
    score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
    targets = {}
    def reb(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        w = V2.rebalance(held_positions=held_positions, expected_returns=expected_returns, returns_history=returns_history,
                         characteristics_history=characteristics_history, trading_costs=trading_costs)
        targets[len(returns_history) - 1] = np.array(w, copy=True); return w
    shim = type("S", (), {"forecast": staticmethod(V2.forecast), "rebalance": staticmethod(reb)})
    rows, _ = score.run(shim, R, X, c)
    return targets, rows


def block_ci(x, L, draws=2000, seed=20261027):
    n = len(x); rng = np.random.default_rng(seed); nb = int(np.ceil(n / L))
    starts = rng.integers(0, n - L + 1, size=(draws, nb))
    idx = (starts[:, :, None] + np.arange(L)).reshape(draws, -1)[:, :n]
    means = x[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    c = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy()
    targets, rows = capture_targets(R, X, c)
    net = rows[:, 0] - rows[:, 1]
    T, n = R.shape
    states = {}
    for name, flag in (("R26", False), ("R27", True)):
        cfg = {**engine.CONFIG, "risk_beta_column": flag, "factor_risk_scale": 1.0}
        states[name] = (engine._RiskState(n, 27 if flag else 26, cfg), cfg)
    out = {k: [] for k in ("t", "g", "q26", "q27", "spec26", "spec27")}
    for t in range(252, 3778):                       # decision after close t, earns R[t+1]
        w = targets[t]
        for name, (st, cfg) in states.items():
            while st.upto < t + 1:
                st.absorb(R, X, st.upto)
        g = float(w @ R[t + 1])
        beta = engine._window_beta(R[:t + 1], engine.CONFIG["beta_window"])
        qs = {}
        for name, (st, cfg) in states.items():
            L, d = st.model()
            D = engine.risk_loadings(X[t], beta, cfg)
            spec = float(w @ (d * w)); y = L.T @ (D.T @ w)
            qs[name] = (spec + float(y @ y), spec)
        out["t"].append(t); out["g"].append(g)
        out["q26"].append(qs["R26"][0]); out["q27"].append(qs["R27"][0])
        out["spec26"].append(qs["R26"][1]); out["spec27"].append(qs["R27"][1])
    o = {k: np.array(v) for k, v in out.items()}
    zero = np.array([not np.any(targets[t]) for t in o["t"]])
    def loss(q):
        q = np.maximum(q, 1e-16); l = np.log(q) + o["g"] ** 2 / q; l[zero] = 0.0; return l
    l26, l27 = loss(o["q26"]), loss(o["q27"]); dl = l27 - l26
    earn = o["t"] + 1
    res = {"n": int(len(dl)), "zero_books": int(zero.sum()),
           "primary_mean_loss_diff_R27_minus_R26": float(dl.mean()),
           "risk_gate_pass": bool(dl.mean() < 0),
           "block_ci_95": {L: block_ci(dl, L) for L in (21, 63, 126)},
           "stage_mean_loss_diff": {s: float(dl[(earn >= lo) & (earn < hi)].mean()) for s, (lo, hi) in STAGES.items()},
           "calibration_ratio_realized_over_predicted": {
               m: {s: float((o["g"][k] ** 2).mean() / o[q][k].mean()) for s, k in
                   [("full", slice(None))] + [(s, (earn >= lo) & (earn < hi)) for s, (lo, hi) in STAGES.items()]}
               for m, q in (("R26", "q26"), ("R27", "q27"))},
           "mean_specific_share": {"R26": float((o["spec26"] / o["q26"]).mean()), "R27": float((o["spec27"] / o["q27"]).mean())},
           "v2_capture_sharpe": float(np.sqrt(252) * net.mean() / net.std())}
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
