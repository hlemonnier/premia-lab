"""Executable checks for verification/V2_FIX_PLAN.md. Exits 1 on any failed expectation.

python verification/v2_package_checks.py --pkg handoff_v2 [--data DIR] [--old-ledger FILE] [--skip-real]
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORE = os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py")


def load_score():
    spec = importlib.util.spec_from_file_location("score", SCORE)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def load_strategy(pkg):
    sys.path.insert(0, os.path.abspath(pkg))
    for k in [k for k in sys.modules if k == "strategy" or k.startswith("model_v2")]:
        del sys.modules[k]
    import strategy
    return strategy


def fixture(seed, T=340, N=96):
    rng = np.random.default_rng(seed)
    m = 0.0004 + 0.01 * rng.standard_normal(T)
    b = rng.uniform(0.4, 1.6, N)
    X = np.zeros((T, N, 13)); X[0] = rng.standard_normal((N, 13))
    for t in range(1, T):
        X[t] = 0.98 * X[t - 1] + 0.2 * rng.standard_normal((N, 13))
    R = b * m[:, None] + 0.02 * rng.standard_normal((T, N))
    R[1:] += 0.002 * X[:-1, :, 0] - 0.001 * X[:-1, :, 4]
    c = rng.uniform(2e-4, 8e-4, N)
    return np.ascontiguousarray(R), np.ascontiguousarray(X), c


def record(strategy, score, R, X, c, start):
    """Run the scorer while capturing forecasts and targets."""
    targets = []
    orig = strategy.rebalance

    def wrapped(**kw):
        w = orig(**kw); targets.append(np.array(w, copy=True)); return w
    params = __import__("inspect").signature(orig).parameters
    wrapped.__signature__ = __import__("inspect").Signature(list(params.values()))
    shim = type("S", (), {})()
    shim.forecast = strategy.forecast
    fc = {}

    def fwrap(**kw):
        out = strategy.forecast(**kw); fc["v"] = np.array(out, copy=True); return out
    fwrap.__signature__ = __import__("inspect").signature(strategy.forecast)
    shim.forecast = fwrap; shim.rebalance = wrapped
    rows, _ = score.run(shim, R, X, c, start=start)
    return fc["v"], np.array(targets), rows


def child(args):
    """Fresh-process run of fixture B, saved to a file."""
    score = load_score(); S = load_strategy(args.pkg)
    R, X, c = fixture(2)
    f, w, rows = record(S, score, R, X, c, start=args.start)
    np.savez(args.child_out, f=f, w=w, rows=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", required=True); ap.add_argument("--data")
    ap.add_argument("--old-ledger"); ap.add_argument("--skip-real", action="store_true")
    ap.add_argument("--child-out"); ap.add_argument("--start", type=int, default=252)
    ap.add_argument("--report")
    args = ap.parse_args()
    if args.child_out:
        child(args); return 0
    results = {}; ok_all = True

    def check(name, cond, detail):
        nonlocal ok_all
        ok_all &= bool(cond); results[name] = {"pass": bool(cond), **detail}
        print(("PASS " if cond else "FAIL ") + name + " " + json.dumps(detail, default=float), flush=True)

    score = load_score()
    tmp = os.path.join(ROOT, "verification", "_tmp_child.npz")

    # 1. stale state: A then B(start=299) in one process vs fresh B
    S = load_strategy(args.pkg)
    RA, XA, cA = fixture(1); RB, XB, cB = fixture(2)
    record(S, score, RA[:300], XA[:300], cA, start=252)
    f1, w1, r1 = record(S, score, RB, XB, cB, start=299)
    subprocess.run([sys.executable, __file__, "--pkg", args.pkg, "--child-out", tmp, "--start", "299"], check=True)
    fr = np.load(tmp); os.remove(tmp)
    # rows[:, 4] is the scorer's wall-clock timing column; compare the economic columns 0..3
    check("restart_same_length_history", np.array_equal(f1, fr["f"]) and np.array_equal(w1, fr["w"]) and np.array_equal(r1[:, :4], fr["rows"][:, :4]),
          {"max_target_diff": float(np.abs(w1 - fr["w"]).max()), "max_gross_return_diff": float(np.abs(r1[:, 0] - fr["rows"][:, 0]).max())})

    # 2. characteristic layout
    S = load_strategy(args.pkg)
    fC, wC, rC = record(S, score, RB, XB, cB, start=252)
    S = load_strategy(args.pkg)
    fF, wF, rF = record(S, score, RB, np.asfortranarray(XB), cB, start=252)
    check("characteristic_fortran_layout", np.array_equal(fC, fF) and np.array_equal(wC, wF) and np.array_equal(rC[:, :4], rF[:, :4]),
          {"max_forecast_diff": float(np.abs(fC - fF).max()), "max_target_diff": float(np.abs(wC - wF).max())})

    # 3. certificate present on the synthetic run
    S = load_strategy(args.pkg)
    eng = sys.modules.get("model_v2.engine")
    has = hasattr(eng, "CERTIFICATES")
    if has:
        eng.CERTIFICATES.clear(); record(S, score, RB, XB, cB, start=252)
        st = [c["status"] for c in eng.CERTIFICATES]
        check("allocator_certificate_synthetic", len(st) > 0 and all(s in ("ok", "ok_after_recovery") for s in st),
              {"calls": len(st), "recoveries": st.count("ok_after_recovery"), "failed": len(st) - st.count("ok") - st.count("ok_after_recovery")})
    else:
        check("allocator_certificate_synthetic", False, {"reason": "engine exposes no CERTIFICATES record"})

    if not args.skip_real:
        import pandas as pd
        R = np.ascontiguousarray(pd.read_csv(f"{args.data}/returns.csv", index_col="day").to_numpy(np.float64))
        X = np.ascontiguousarray(pd.read_csv(f"{args.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
        c = pd.read_csv(f"{args.data}/costs.csv", index_col="stock")["cost"].to_numpy()
        # 4. economic agreement + real-data certificates
        S = load_strategy(args.pkg); eng = sys.modules.get("model_v2.engine")
        if hasattr(eng, "CERTIFICATES"):
            eng.CERTIFICATES.clear()
        rows, _ = score.run(S, R, X, c)
        net = rows[:, 0] - rows[:, 1]
        sharpe = float(np.sqrt(252) * net.mean() / net.std())
        if args.old_ledger:
            old = np.load(args.old_ledger)
            check("economic_agreement_with_old_package", np.abs(net - old).max() <= 1e-9, {"max_abs_daily_net_diff": float(np.abs(net - old).max()), "sharpe": sharpe})
        np.save(os.path.join(ROOT, "verification", "_last_real_net.npy"), net)
        if hasattr(eng, "CERTIFICATES"):
            st = [c["status"] for c in eng.CERTIFICATES]; gaps = [c["gap"] for c in eng.CERTIFICATES]
            check("allocator_certificate_real", all(s in ("ok", "ok_after_recovery") for s in st),
                  {"calls": len(st), "recoveries": st.count("ok_after_recovery"), "max_abs_gap": float(np.max(np.abs(gaps)))})
        # 5. causality on the packaged forecast
        S = load_strategy(args.pkg); base = S.forecast(returns_history=R, characteristics_history=X)
        rng = np.random.default_rng(7); good = True; worst = 0.0
        for cut in (400, 1500, 3024, 3700):
            R2 = R.copy(); X2 = X.copy()
            R2[cut:] = rng.normal(0, .03, R2[cut:].shape); X2[cut:] = rng.normal(0, 1, X2[cut:].shape)
            for lab, a in (("altered", (R2, X2)), ("altered_both_fortran", (np.asfortranarray(R2), np.asfortranarray(X2))), ("truncated", (R[:cut], X[:cut]))):
                out = S.forecast(returns_history=a[0], characteristics_history=a[1]); up = cut if lab == "truncated" else cut + 1
                same = np.array_equal(base[:up], out[:up]); good &= same
                worst = max(worst, float(np.abs(base[:up] - out[:up]).max()))
        check("packaged_forecast_causality", good, {"max_protected_diff": worst})

    if args.report:
        json.dump(results, open(args.report, "w"), indent=1, default=float)
    print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
