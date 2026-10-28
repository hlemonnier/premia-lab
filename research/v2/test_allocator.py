"""Tests for factor_allocator.allocate_factor — written before the implementation.

Run: python3 test_allocator.py  (exits non-zero on any failure)
"""
import sys
import time

import cvxpy as cp
import numpy as np

import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2", "model_v2"))
sys.path.insert(0, os.path.join(ROOT, "handoff"))
from model.portfolio import allocate as allocate_diag  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond:
        failures.append(name)


def problem(n=200, k=5, seed=0):
    rng = np.random.default_rng(seed)
    B = rng.standard_normal((n, k))
    A = rng.standard_normal((k, k)) * 0.01
    F = A @ A.T
    L = np.linalg.cholesky(F + 1e-14 * np.eye(k))
    d = rng.uniform(1e-4, 9e-4, n)
    b = rng.uniform(0.2, 2.0, n)
    mu = rng.standard_normal(n) * 2e-3
    h = rng.standard_normal(n) * 0.01
    kappa = rng.uniform(2e-5, 8e-5, n)
    return dict(mu=mu, h=h, d=d, B=B, L=L, b=b, kappa=kappa, gamma=100.0, cap=0.01), F


def objective(w, p, F):
    y = p["B"].T @ w
    return (p["mu"] @ w - p["gamma"] / 2 * (w @ (p["d"] * w) + y @ F @ y)
            - p["kappa"] @ np.abs(w - p["h"]))


def reference(p, F):
    n = len(p["mu"]); w = cp.Variable(n)
    y = p["B"].T @ w
    obj = (p["mu"] @ w - p["gamma"] / 2 * (cp.sum(cp.multiply(p["d"], cp.square(w))) + cp.quad_form(y, cp.psd_wrap(F)))
           - p["kappa"] @ cp.abs(w - p["h"]))
    cp.Problem(cp.Maximize(obj), [p["b"] @ w == 0, cp.abs(w) <= p["cap"]]).solve(
        solver="CLARABEL", tol_gap_abs=1e-12, tol_gap_rel=1e-12, tol_feas=1e-12)
    return w.value


def run(p, **kw):
    from allocator import allocate_factor
    return allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"], **kw)


# 1 + 2 + 5: agreement with cvxpy, beta equality, caps
for seed in range(6):
    p, F = problem(seed=seed)
    w = run(p); ref = reference(p, F)
    caps_active = int(np.sum(np.isclose(np.abs(ref), p["cap"], atol=1e-7)))
    bands = int(np.sum(np.isclose(ref, p["h"], atol=1e-7)))
    rel = abs(objective(w, p, F) - objective(ref, p, F)) / abs(objective(ref, p, F))
    check(f"seed {seed}: objective matches cvxpy", rel < 1e-7 or objective(w, p, F) >= objective(ref, p, F),
          f"rel {rel:.1e}, caps {caps_active}, bands {bands}")
    check(f"seed {seed}: weights match cvxpy", np.max(np.abs(w - ref)) < 1e-5, f"max diff {np.max(np.abs(w - ref)):.1e}")
    check(f"seed {seed}: beta equality", abs(p["b"] @ w) <= 1e-10 * (np.abs(p["b"]).sum() * p["cap"]))
    check(f"seed {seed}: caps exact", np.all(np.abs(w) <= p["cap"]))

# 3: F = 0 reduces to the diagonal allocator
p, _ = problem(seed=11); p["L"] = np.zeros_like(p["L"])
w = run(p)
wd = allocate_diag(p["mu"], p["h"], p["d"], p["b"], p["kappa"], p["gamma"], 1.0, p["cap"])
check("zero factor risk reduces to diagonal allocator", np.max(np.abs(w - wd)) < 1e-9, f"{np.max(np.abs(w - wd)):.1e}")

# 4: no trade when holdings are already optimal
p, F = problem(seed=12); w1 = run(p); p["h"] = w1.copy(); w2 = run(p)
check("no trade at optimum", np.max(np.abs(w2 - w1)) < 1e-9, f"{np.max(np.abs(w2 - w1)):.1e}")

# 6: zero caps force zero weights
p, F = problem(seed=13); cap = np.full(len(p["mu"]), 0.01); cap[:20] = 0.0; p["cap"] = cap
w = run(p)
check("cap 0 forces 0", np.all(w[:20] == 0.0))

# 7: invalid inputs
p, _ = problem(seed=14)
bad = [("nan mu", dict(mu=np.r_[np.nan, p["mu"][1:]])), ("d <= 0", dict(d=np.r_[0.0, p["d"][1:]])),
       ("gamma <= 0", dict(gamma=0.0)), ("shape", dict(b=p["b"][:-1])), ("neg cap", dict(cap=-0.01)),
       ("neg cost", dict(kappa=np.r_[-1e-5, p["kappa"][1:]]))]
for name, change in bad:
    try:
        run({**p, **change}); check(f"rejects {name}", False)
    except ValueError:
        check(f"rejects {name}", True)

# 8: infeasible beta
p, _ = problem(n=50, seed=15); cap = np.zeros(50); cap[0] = 0.01; p["cap"] = cap; p["h"] = np.zeros(50)
w = run(p)
check("beta solvable with one movable stock: holds zero", np.all(w == 0.0) and abs(p["b"] @ w) == 0)

# 9: runtime at full size, warm-started
p, F = problem(n=1000, k=26, seed=16)
from allocator import allocate_factor  # noqa: E402
state = {}
times = []
for i in range(30):
    p["mu"] = p["mu"] + np.random.default_rng(i).standard_normal(1000) * 2e-4
    t0 = time.perf_counter()
    w = allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"], warm=state)
    times.append(time.perf_counter() - t0); p["h"] = w
check("median solve under 10 ms at n=1000, k=26", np.median(times) < 0.010, f"median {1e3*np.median(times):.2f} ms, max {1e3*max(times):.2f} ms")
p2, F2 = problem(n=1000, k=26, seed=16); w = run(p2); ref = reference(p2, F2)
check("full size matches cvxpy", np.max(np.abs(w - ref)) < 1e-5, f"{np.max(np.abs(w - ref)):.1e}")

# 10: deterministic, inputs not mutated
p, _ = problem(seed=17); snap = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in p.items()}
a = run(p); b = run(p)
check("deterministic", np.array_equal(a, b))
check("inputs unchanged", all(np.array_equal(p[k], snap[k]) if isinstance(snap[k], np.ndarray) else p[k] == snap[k] for k in p))

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
