"""Tests for allocate_factor(..., beta_target=c): constraint b'w = c. Written before the change.

Expectations: (1) matches cvxpy with b'w == c on random problems, weights within 1e-5;
(2) b'w equals c within 1e-10 * |b|'cap; (3) beta_target=0 is bitwise identical to the
default call; (4) an unattainable target (|c| > |b|'cap) raises ValueError;
(5) the certificate reports status ok.
"""
import os
import sys

import cvxpy as cp
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2", "model_v2"))
from allocator import allocate_factor  # noqa: E402

fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond:
        fails.append(name)


def problem(seed, n=200, k=5):
    rng = np.random.default_rng(seed)
    B = rng.standard_normal((n, k)); A = rng.standard_normal((k, k)) * 0.005; F = A @ A.T
    L = np.linalg.cholesky(F + 1e-14 * np.eye(k))
    return dict(mu=rng.standard_normal(n) * 3e-4, h=rng.standard_normal(n) * 0.003, d=rng.uniform(1e-4, 9e-4, n),
                B=B, L=L, b=rng.uniform(0.2, 2.0, n), kappa=rng.uniform(1e-5, 4e-5, n), gamma=500.0, cap=0.02), F


for seed in range(5):
    p, F = problem(seed)
    for c in (0.05, -0.03):
        info = {}
        w = allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"], beta_target=c, info=info)
        x = cp.Variable(len(w)); y = p["B"].T @ x
        obj = p["mu"] @ x - p["gamma"] / 2 * (cp.sum(cp.multiply(p["d"], cp.square(x))) + cp.quad_form(y, cp.psd_wrap(F))) - p["kappa"] @ cp.abs(x - p["h"])
        cp.Problem(cp.Maximize(obj), [p["b"] @ x == c, cp.abs(x) <= p["cap"]]).solve(solver="CLARABEL", tol_gap_abs=1e-14, tol_gap_rel=1e-14, tol_feas=1e-14)
        check(f"seed {seed} target {c}: matches cvxpy", np.max(np.abs(w - x.value)) < 1e-5, f"{np.max(np.abs(w - x.value)):.1e}")
        check(f"seed {seed} target {c}: exposure exact", abs(p["b"] @ w - c) <= 1e-10 * np.abs(p["b"]).sum() * p["cap"], f"{p['b'] @ w - c:.1e}")
        check(f"seed {seed} target {c}: certificate ok", info.get("status") in ("ok", "ok_after_recovery"), str(info.get("status")))

p, _ = problem(9)
a = allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"])
b = allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"], beta_target=0.0)
check("target 0 identical to default", np.array_equal(a, b))
try:
    allocate_factor(p["mu"], p["h"], p["d"], p["B"], p["L"], p["b"], p["kappa"], p["gamma"], p["cap"], beta_target=10.0)
    check("unattainable target rejected", False)
except ValueError:
    check("unattainable target rejected", True)
print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
