"""Checks for verification/V2_FAILURE_PATH_PLAN.md (items 1-4). Exit 1 on any failure."""
import importlib.util
import inspect
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
from model_v2 import engine  # noqa: E402
from model_v2.allocator import allocate_factor  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "verification"))
from v2_package_checks import fixture  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond:
        fails.append(name)


def problem(seed=0, n=150, k=6):
    rng = np.random.default_rng(seed)
    B = rng.standard_normal((n, k)); L = rng.standard_normal((k, k)) * 0.01
    return dict(mu=rng.standard_normal(n) * 5e-4, held=rng.standard_normal(n) * 0.003, d=rng.uniform(1e-4, 9e-4, n),
                B=B, L=L, beta=rng.uniform(0.3, 1.8, n), kappa=rng.uniform(1e-5, 4e-5, n), gamma=300.0, cap=0.02)


def run(p, **kw):
    return allocate_factor(p["mu"], p["held"], p["d"], p["B"], p["L"], p["beta"], p["kappa"], p["gamma"], p["cap"], **kw)


# 1. forced failure -> certified diagonal fallback
p = problem()
for target in (0.0, 0.04):
    info = {}
    try:
        w = run(p, max_iter=0, info=info, beta_target=target)
        ok = (info.get("status") == "fallback_diagonal" and np.all(np.abs(w) <= p["cap"]) and np.isfinite(w).all()
              and abs(p["beta"] @ w - target) <= 1e-10 * np.abs(p["beta"]).sum() * p["cap"])
        check(f"forced failure, target {target}: certified diagonal fallback", ok, f"status={info.get('status')} beta_err={p['beta'] @ w - target:.1e}")
    except Exception as exc:  # noqa: BLE001
        check(f"forced failure, target {target}: certified diagonal fallback", False, f"raised {type(exc).__name__}: {exc}")

# 2 + 3. engine on a synthetic scorer run, nonzero target with a binding gross cap
spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
import strategy as S  # noqa: E402
R, X, c = fixture(3, T=340, N=96)
for label, over in (("default V2", {}), ("target 0.03, gross cap 0.3", {"beta_target": 0.03, "gross_cap": 0.3})):
    engine.configure({**S._CONFIG, **over})
    finals = []
    def reb(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        w = engine.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
        b = engine._window_beta(np.ascontiguousarray(returns_history), engine.CONFIG["beta_window"])
        finals.append((float(np.abs(w).sum()), float(b @ w))); return w
    shim = type("Sh", (), {"forecast": staticmethod(engine.forecast), "rebalance": staticmethod(reb)})
    try:
        score.run(shim, R, X, c)
        statuses = {x.get("status") for x in engine.CERTIFICATES}
        check(f"{label}: no uncertified status stored", statuses <= {"ok", "ok_after_recovery", "ok_after_cold_restart", "fallback_diagonal"}, str(statuses))
        if over:
            g = np.array([f[0] for f in finals]); e = np.array([f[1] for f in finals])
            nonzero = g > 0
            check(f"{label}: gross cap respected", np.all(g <= 0.3 * (1 + 1e-12)), f"max gross {g.max():.4f}")
            check(f"{label}: nonzero target kept under binding cap", np.all(np.abs(e[nonzero] - 0.03) <= 1e-9), f"max |b'w-0.03| {np.abs(e[nonzero] - 0.03).max():.2e}, binding days {int(np.sum(g >= 0.3 * (1 - 1e-9)))}")
    except Exception as exc:  # noqa: BLE001
        check(f"{label}: engine run", False, f"raised {type(exc).__name__}: {exc}")
engine.configure(S._CONFIG)

# 4. edge cases
p = problem(1)
try:
    run({**p, "beta": np.zeros_like(p["beta"])}, beta_target=0.0); check("(a) zero betas, target 0: valid", True)
except Exception as exc:  # noqa: BLE001
    check("(a) zero betas, target 0: valid", False, f"{type(exc).__name__}: {exc}")
try:
    run({**p, "cap": 0.0}, beta_target=0.02); check("(b) zero caps, nonzero target: ValueError", False, "returned")
except ValueError:
    check("(b) zero caps, nonzero target: ValueError", True)
info = {}
w = run({**p, "cap": 0.0}, info=info)
check("(c) zero caps, target 0: zeros with status ok", np.all(w == 0) and info.get("status") == "ok", str(info.get("status")))
mx = float(np.abs(p["beta"]) @ np.full(len(p["beta"]), p["cap"]))
try:
    run(p, beta_target=mx); check("(d) target at max attainable: ValueError", False, "returned")
except ValueError as exc:
    check("(d) target at max attainable: ValueError", "strictly inside" in str(exc), str(exc))

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
