"""Checks for verification/V3_INTEGRATION_SPEC.md. Exit 1 on any failed expectation.

python verification/v3_integration_checks.py --data DIR --reference DIR [--report FILE]
--reference holds forecast.npy, targets.npy, inner_targets.npy, virtual_targets.npy, rows.npy
from the independent rerun of GPT's research code.
"""
import argparse, importlib.util, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails, report = [], {}


def check(name, cond, detail):
    report[name] = {"pass": bool(cond), **detail}
    print(("PASS " if cond else "FAIL ") + name + " " + json.dumps(detail, default=float), flush=True)
    if not cond:
        fails.append(name)


def load_package():
    sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
    for k in [k for k in sys.modules if k == "strategy" or k.startswith("model_v3")]:
        del sys.modules[k]
    import strategy
    return strategy


def scorer():
    spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def run(S, score, R, X, c, start=252):
    """Score the package and capture forecast and the three target streams."""
    pol = S.POLICY
    outer, inner, virtual, decisions = [], [], [], []
    def reb(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        w = S.rebalance(held_positions=held_positions, expected_returns=expected_returns, returns_history=returns_history,
                        characteristics_history=characteristics_history, trading_costs=trading_costs)
        outer.append(np.array(w, copy=True)); inner.append(pol.inner.target.copy()); virtual.append(pol.virtual.target.copy())
        decisions.append(len(returns_history) - 1); return w
    fc = {}
    def fwd(returns_history, characteristics_history):
        fc["v"] = np.array(S.forecast(returns_history=returns_history, characteristics_history=characteristics_history), copy=True)
        return fc["v"]
    shim = type("Sh", (), {"forecast": staticmethod(fwd), "rebalance": staticmethod(reb)})
    rows, fsec = score.run(shim, R, X, c, start=start)
    return {"forecast": fc["v"], "outer": np.array(outer), "inner": np.array(inner), "virtual": np.array(virtual),
            "decisions": np.array(decisions), "rows": rows, "fsec": fsec, "certs": list(pol.certificates)}


def sharpe(rows):
    net = rows[:, 0] - rows[:, 1]; return float(np.sqrt(252) * net.mean() / net.std())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--reference", required=True)
    ap.add_argument("--report"); a = ap.parse_args()
    try:
        S = load_package()
    except Exception as exc:  # noqa: BLE001
        check("package_importable", False, {"error": f"{type(exc).__name__}: {exc}"})
        print("SOME CHECKS FAILED"); return 1
    score = scorer()
    R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
    c = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    ref = {k: np.load(os.path.join(a.reference, f"{k}.npy")) for k in ("forecast", "targets", "inner_targets", "virtual_targets", "rows")}
    base = run(S, score, R, X, c)
    # 1-3 fidelity
    check("forecast_exact", base["forecast"].shape == ref["forecast"].shape and np.array_equal(base["forecast"], ref["forecast"]),
          {"max_abs_diff": float(np.abs(base["forecast"] - ref["forecast"]).max())})
    check("decision_indices", np.array_equal(base["decisions"], np.arange(252, 3779)), {"n": int(len(base["decisions"]))})
    for k, r in (("virtual", "virtual_targets"), ("inner", "inner_targets"), ("outer", "targets")):
        d = float(np.abs(base[k] - ref[r]).max())
        check(f"{k}_targets_within_1e-8", d <= 1e-8, {"max_abs_diff": d})
    for j, name in enumerate(("gross_return", "fee", "closing_gross", "market_return")):
        d = float(np.abs(base["rows"][:, j] - ref["rows"][:, j]).max())
        check(f"economics_{name}_within_1e-8", d <= 1e-8, {"max_abs_diff": d})
    s_pkg, s_ref = sharpe(base["rows"]), sharpe(ref["rows"])
    check("net_sharpe_within_1e-8", abs(s_pkg - s_ref) <= 1e-8, {"package": s_pkg, "reference": s_ref, "diff": s_pkg - s_ref})
    # 5 certificates and bounds
    ok_status = {"ok", "ok_after_recovery", "ok_after_cold_restart", "fallback_diagonal"}
    st = [x["status"] for x in base["certs"]]
    n = R.shape[1]
    check("all_solves_certified", set(st) <= ok_status and len(st) == 2 * len(base["decisions"]),
          {"solves": len(st), "statuses": sorted(set(st))})
    check("outer_bounds", float(np.abs(base["outer"]).max()) <= 0.10 + 0.05 / n and float(np.abs(base["outer"]).sum(axis=1).max()) <= 5 + 1e-12,
          {"max_weight": float(np.abs(base["outer"]).max()), "max_gross": float(np.abs(base["outer"]).sum(axis=1).max())})
    check("virtual_bound", float(np.abs(base["virtual"]).max()) <= 0.05, {"max_weight": float(np.abs(base["virtual"]).max())})
    # 4 causality on the packaged entry point
    rng = np.random.default_rng(29); good = True; worst = 0.0
    for cut in (600, 2000, 3500):
        R2 = R.copy(); X2 = X.copy(); R2[cut:] = rng.normal(0, .03, R2[cut:].shape); X2[cut:] = rng.normal(0, 1, X2[cut:].shape)
        alt = run(S, score, R2, X2, c)
        k = base["decisions"] <= cut - 1
        same = (np.array_equal(base["forecast"][:cut + 1], alt["forecast"][:cut + 1])
                and all(np.array_equal(base[s][k], alt[s][k]) for s in ("outer", "inner", "virtual")))
        good &= same
        tr = run(S, score, R[:cut], X[:cut], c)
        m = tr["decisions"].size
        same_t = (np.array_equal(base["forecast"][:cut], tr["forecast"][:cut])
                  and all(np.array_equal(base[s][:m], tr[s]) for s in ("outer", "inner", "virtual")))
        good &= same_t
        worst = max(worst, float(np.abs(base["outer"][k] - alt["outer"][k]).max()))
    check("future_alteration_and_prefix_exact", good, {"max_protected_outer_diff": worst})
    # restart: score history A (first 900 rows) then B (full) in one process vs B fresh (= base above, fresh process state)
    S2 = load_package()
    run(S2, score, R[:900] * 1.5, X[:900][:, ::-1], c)
    again = run(S2, score, R, X, c)
    check("cross_history_restart_exact", all(np.array_equal(again[s], base[s]) for s in ("forecast", "outer", "inner", "virtual"))
          and np.array_equal(again["rows"][:, :4], base["rows"][:, :4]), {})
    report["observed"] = {"package_sharpe": s_pkg, "forecast_seconds": base["fsec"], "rebalance_ms": float(1e3 * base["rows"][:, 4].mean())}
    if a.report:
        json.dump(report, open(a.report, "w"), indent=1, default=float)
    print("ALL PASS" if not fails else "SOME CHECKS FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
