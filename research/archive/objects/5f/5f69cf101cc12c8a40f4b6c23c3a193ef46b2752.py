#!/usr/bin/env python3
"""Preimplementation numerical contract checks; see PORTFOLIO_PLAN.md.

All inputs are synthetic. This is isolated optimizer verification, not evidence
of candidate alpha, scorer fidelity, or complete-strategy runtime.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import time
import traceback

sys.dont_write_bytecode = True
THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for variable in THREAD_VARIABLES:
    os.environ[variable] = "1"
affinity_error = None
try:
    os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
except (AttributeError, OSError) as exc:
    affinity_error = repr(exc)

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, minimize


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def serializable(value):
    if isinstance(value, np.ndarray):
        return serializable(value.tolist())
    if isinstance(value, np.generic):
        return serializable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return "NaN" if np.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {str(key): serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    return value


def save_json(path, value):
    Path(path).write_text(json.dumps(serializable(value), indent=2, allow_nan=False) + "\n")


def inputs(mu, *, held=None, var=None, beta=None, cost=None, gamma=1.0,
           horizon=1.0, cap=1.0):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)
    return {
        "expected_returns": mu,
        "held_positions": np.zeros(n) if held is None else np.asarray(held, dtype=float),
        "variances": np.ones(n) if var is None else np.asarray(var, dtype=float),
        "betas": np.ones(n) if beta is None else np.asarray(beta, dtype=float),
        "trading_costs": np.zeros(n) if cost is None else np.asarray(cost, dtype=float),
        "risk_aversion": gamma,
        "cost_horizon": horizon,
        "weight_cap": np.asarray(cap, dtype=float) if np.ndim(cap) else float(cap),
    }


def beta_normalized(data):
    beta = data["betas"]
    caps = np.broadcast_to(data["weight_cap"], beta.shape)
    active = caps > 0
    scale = np.max(np.abs(beta[active]), initial=0.0)
    result = np.zeros_like(beta)
    if scale:
        result[active] = beta[active] / scale
    return result


def fixtures():
    cases = []
    def add(name, expected, mu, **kwargs):
        cases.append({"name": name, "inputs": inputs(mu, **kwargs),
                      "expected_weights": np.asarray(expected, dtype=float), "reference": False})
    add("zero_alpha_empty", [0, 0, 0], [0, 0, 0], beta=[1, -0.7, 0],
        var=[0.5, 1, 2], cost=[0.1, 0.2, 0.3], gamma=2, horizon=2)
    add("no_trade_nonzero_feasible", [0.2, -0.2], [0.22, -0.43],
        held=[0.2, -0.2], var=[0.5, 1], cost=[0.1, 0.1], gamma=2, horizon=2)
    add("all_betas_zero", [0.4, -0.4, 0], [0.5, -0.5, 0.05], beta=[0, 0, 0], cost=[0.1] * 3)
    add("zero_cost_analytic", [0.1, -0.1], [0.3, 0.1], held=[0.8, -0.7])
    add("signed_betas", [0.1, 0.1], [0.3, -0.1], beta=[1, -1])
    add("signed_betas_with_cost", [0.3, 0.3], [0.6, 0.2], beta=[1, -1], cost=[0.1, 0.1])
    add("mixed_zero_beta_asset", [0.1, -0.1, 0.5], [0.3, 0.1, 0.5], beta=[1, 1, 0])
    add("drifted_holdings_cost_center", [0.2], [0.1], held=[0.4], beta=[0], cost=[0.1])
    add("holdings_outside_box", [0.25], [0], held=[2], beta=[0], cost=[0.3], cap=0.25)
    add("drifted_holdings_not_hedged", [0.2, -0.2], [0, 0], held=[0.4, -0.2], cost=[0.5, 0.5])
    add("binding_cap_hedged", [0.2, -0.1, -0.1], [3, 0, 0], cap=[0.2, 0.4, 0.4])
    add("limited_hedge_capacity", [0.2, -0.1], [5, 0], beta=[1, 2], cap=[1, 0.1])
    add("all_zero_caps", [0, 0], [3, -1], held=[0.2, -0.3], cap=[0, 0])
    add("irrelevant_huge_beta_fixed_asset", [0, 0.1, -0.1], [1, 0.3, 0.1],
        beta=[1e300, 1, 1], cap=[0, 1, 1])
    add("uniformly_tiny_betas", [0.1, -0.1], [0.3, 0.1], beta=[1e-200, 1e-200])
    add("small_positive_variance", [1, -1], [1e-8, 0], var=[1e-12, 1e-12])
    add("large_cost_plateau", [0.2, -0.2], [0.3, 0.1], held=[0.2, -0.2], cost=[10, 10])
    add("horizon_one", [0.3, -0.3], [0.5, -0.5], cost=[0.2, 0.2], horizon=1)
    add("horizon_two", [0.4, -0.4], [0.5, -0.5], cost=[0.2, 0.2], horizon=2)
    add("financial_scale_quadratic", [0.05, -0.05], [3e-4, 1e-4], var=[0.001, 0.001], gamma=2, cap=0.1)
    data = inputs([0.8, -0.2, 0.5, -0.4], var=[0.7, 1.2, 0.5, 2.0],
                  beta=[1.2, -0.5, 0, 0.8], held=[1.1, -2, 0.3, 0.1], gamma=1.7, cap=10)
    a = data["risk_aversion"] * data["variances"]
    b = data["betas"]
    kkt = np.block([[np.diag(a), b[:, None]], [b[None, :], np.zeros((1, 1))]])
    expected = np.linalg.solve(kkt, np.r_[data["expected_returns"], 0])[:-1]
    cases.append({"name": "independent_kkt_linear_system", "inputs": data,
                  "expected_weights": expected, "reference": False})
    rng = np.random.default_rng(20261026)
    for number in range(12):
        n = 3 + number % 4
        beta = rng.uniform(-2, 2, n)
        if number % 4 == 0:
            beta[0] = 0
        caps = rng.uniform(0.08, 0.5, n)
        if number % 5 == 0:
            caps[-1] = 0
        data = inputs(rng.uniform(-1.2, 1.2, n), held=rng.uniform(-0.6, 0.6, n),
                      var=rng.uniform(0.2, 2, n), beta=beta,
                      cost=rng.uniform(0.02, 0.3, n), gamma=0.7 + 1.1 * (number % 3),
                      horizon=1 if number % 2 else 3, cap=caps)
        cases.append({"name": f"independent_primal_reference_{number:02d}",
                      "inputs": data, "reference": True})
    rng = np.random.default_rng(271828)
    n = 1000
    beta = rng.normal(0.5, 0.6, n)
    expected = rng.normal(0, 0.001, n)
    expected -= beta * (beta @ expected) / (beta @ beta)
    expected *= 0.003 / np.max(np.abs(expected))
    var = rng.uniform(0.05, 1, n)
    held = rng.normal(0, 0.003, n)
    cost = rng.uniform(0, 0.001, n)
    gamma, horizon, multiplier = 4.0, 5.0, 0.017
    mu = gamma * var * expected + multiplier * beta + (cost / horizon) * np.sign(expected - held)
    large = {"name": "known_kkt_1000_assets", "inputs": inputs(mu, held=held, var=var,
             beta=beta, cost=cost, gamma=gamma, horizon=horizon, cap=0.01),
             "expected_weights": expected, "reference": False, "constructed_multiplier": multiplier}
    cases.append(large)
    return cases


def invalid_fixtures():
    changes = [
        ("nan_alpha", "expected_returns", np.array([np.nan, 0.])),
        ("infinite_holdings", "held_positions", np.array([np.inf, 0.])),
        ("zero_variance", "variances", np.array([0., 1.])),
        ("negative_variance", "variances", np.array([-1., 1.])),
        ("nan_beta", "betas", np.array([np.nan, 1.])),
        ("negative_cost", "trading_costs", np.array([-0.1, 0.])),
        ("wrong_vector_length", "betas", np.array([1.])),
        ("matrix_alpha", "expected_returns", np.array([[0., 0.]])),
        ("empty_alpha", "expected_returns", np.array([])),
        ("zero_risk_aversion", "risk_aversion", 0.),
        ("negative_risk_aversion", "risk_aversion", -1.),
        ("array_risk_aversion", "risk_aversion", np.array([1.])),
        ("zero_horizon", "cost_horizon", 0.),
        ("infinite_horizon", "cost_horizon", np.inf),
        ("negative_cap", "weight_cap", -1.),
        ("nan_cap", "weight_cap", np.nan),
        ("wrong_cap_length", "weight_cap", np.array([1.])),
        ("overflowing_risk", "variances", np.array([1e308, 1e308])),
        ("underflowing_risk", "variances", np.array([1e-300, 1e-300])),
    ]
    result = []
    for name, key, value in changes:
        data = inputs([0., 0.])
        data[key] = value
        if name == "overflowing_risk":
            data["risk_aversion"] = 1e308
        if name == "underflowing_risk":
            data["risk_aversion"] = 1e-300
        result.append({"name": name, "inputs": data, "expected_exception": "ValueError"})
    return result


def objective(data, weights):
    a = data["risk_aversion"] * data["variances"]
    k = data["trading_costs"] / data["cost_horizon"]
    return float(0.5 * (a * weights) @ weights - data["expected_returns"] @ weights
                 + k @ np.abs(weights - data["held_positions"]))


def primal_reference(data):
    n = len(data["expected_returns"])
    a = data["risk_aversion"] * data["variances"]
    k = data["trading_costs"] / data["cost_horizon"]
    mu, held = data["expected_returns"], data["held_positions"]
    caps = np.broadcast_to(data["weight_cap"], (n,))
    magnitude = float(np.sum(np.abs(mu) * caps + 0.5 * a * caps**2 + k * (caps + np.abs(held))))
    scale = max(magnitude, 1e-12)
    def fun(value):
        w, z = value[:n], value[n:]
        return (0.5 * (a * w) @ w - mu @ w + k @ z) / scale
    def jac(value):
        return np.r_[a * value[:n] - mu, k] / scale
    eye = np.eye(n)
    epigraph = np.block([[-eye, eye], [eye, eye]])
    constraints = [LinearConstraint(epigraph, np.r_[-held, held], np.inf)]
    b = beta_normalized(data)
    if np.any(b):
        constraints.append(LinearConstraint(np.r_[b, np.zeros(n)][None, :], 0., 0.))
    bounds = Bounds(np.r_[-caps, np.zeros(n)], np.r_[caps, np.full(n, np.inf)])
    initial = np.r_[np.zeros(n), np.abs(held) + 1e-6]
    result = minimize(fun, initial, jac=jac, method="SLSQP", bounds=bounds,
                      constraints=constraints, options={"ftol": 5e-13, "maxiter": 2000})
    w, z = result.x[:n], result.x[n:]
    info = {"success": bool(result.success), "status": int(result.status),
            "message": str(result.message), "iterations": int(result.nit), "weights": w,
            "objective": objective(data, w), "objective_scale": scale,
            "beta_residual": float(b @ w),
            "max_epigraph_violation": float(np.max(np.maximum(np.abs(w - held) - z, 0.))),
            "max_bound_violation": float(np.max(np.maximum(np.abs(w) - caps, 0.)))}
    if not result.success or abs(info["beta_residual"]) > 1e-9 or max(info["max_epigraph_violation"], info["max_bound_violation"]) > 1e-9:
        raise RuntimeError(f"Independent reference failed: {serializable(info)}")
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--expected-missing-module", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / "runner_used.py").write_bytes(Path(__file__).read_bytes())
    (out / "expectations.md").write_bytes(args.plan.read_bytes())
    command = shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]])
    rerun_module = out / "portfolio_used.py" if args.module.exists() else args.module.resolve()
    rerun = [sys.executable, str(out / "runner_used.py"), "--module", str(rerun_module),
             "--plan", str(out / "expectations.md"), "--out", str(out) + "_rerun"]
    if args.expected_missing_module:
        rerun.append("--expected-missing-module")
    (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
    summary = {"scope": "Isolated synthetic portfolio optimizer verification",
               "started_utc": datetime.now(timezone.utc).isoformat(), "run_command": command,
               "rerun_command": shlex.join(rerun), "status": "RUNNING", "checks": [],
               "expected_missing_module": args.expected_missing_module,
               "unverified": ["alpha", "full strategy E2E", "actual-cost backtest", "long-history runtime"]}
    log = []
    code = 1
    def record(name, passed, detail):
        item = {"name": name, "status": "PASS" if passed else "FAIL", **detail}
        summary["checks"].append(item)
        line = json.dumps(serializable(item), allow_nan=False)
        log.append(line)
        print(line, flush=True)
    try:
        environment = {"python": sys.version, "platform": platform.platform(),
                       "numpy": importlib.metadata.version("numpy"), "scipy": importlib.metadata.version("scipy"),
                       "threads": {key: os.environ[key] for key in THREAD_VARIABLES},
                       "cpu_affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
                       "affinity_error": affinity_error}
        save_json(out / "environment.json", environment)
        cases, invalid = fixtures(), invalid_fixtures()
        save_json(out / "inputs.json", {"valid": cases, "invalid": invalid,
                                       "nonfinite_encoding": "NaN and infinity are explicit string markers in invalid fixtures"})
        save_json(out / "identity.json", {"runner_sha256": digest(__file__), "plan_sha256": digest(args.plan),
                                          "module_exists": args.module.exists(),
                                          "module_sha256": digest(args.module) if args.module.exists() else None})
        if args.expected_missing_module:
            if args.module.exists():
                raise RuntimeError("Red-stage run requires the allocator to be absent")
            raise FileNotFoundError("Expected preimplementation failure: allocator does not exist; numerical cases NOT RUN")
        (out / "portfolio_used.py").write_bytes(args.module.read_bytes())
        spec = importlib.util.spec_from_file_location("portfolio_under_verification", args.module)
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot import allocator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        allocate = module.allocate
        actual = []
        for case in cases:
            data = case["inputs"]
            copies = {key: value.copy() if isinstance(value, np.ndarray) else value for key, value in data.items()}
            try:
                w = np.asarray(allocate(**data))
                repeated = np.asarray(allocate(**data))
                n = len(data["expected_returns"])
                caps = np.broadcast_to(data["weight_cap"], (n,))
                if w.shape != (n,) or not np.isfinite(w).all():
                    raise AssertionError(f"Invalid weights shape/finiteness: {w.shape}")
                b = beta_normalized(data)
                beta_error = abs(float(b @ w))
                beta_tolerance = 5e-11 * max(1., float(np.abs(b) @ caps))
                bound_error = float(np.max(np.maximum(np.abs(w) - caps, 0.)))
                unchanged = all(np.array_equal(data[key], value) if isinstance(value, np.ndarray)
                                else data[key] == value for key, value in copies.items())
                detail = {"beta_error": beta_error, "beta_tolerance": beta_tolerance,
                          "bound_error": bound_error, "inputs_unchanged": unchanged,
                          "deterministic": bool(np.array_equal(w, repeated)), "dtype": str(w.dtype),
                          "objective": objective(data, w)}
                passed = (w.dtype == np.float64 and beta_error <= beta_tolerance
                          and bound_error <= 2e-12 * max(1., float(np.max(caps)))
                          and unchanged and np.array_equal(w, repeated))
                if case["reference"]:
                    reference = primal_reference(data)
                    gap = abs(detail["objective"] - reference["objective"]) / reference["objective_scale"]
                    detail["normalized_objective_gap"] = gap
                    detail["reference_success"] = reference["success"]
                    passed &= gap <= 2e-8
                    actual.append({"name": case["name"], "weights": w, "reference": reference})
                else:
                    difference = float(np.max(np.abs(w - case["expected_weights"])))
                    tolerance = 1e-9 if n == 1000 else 2e-10
                    detail["max_weight_error"] = difference
                    detail["weight_tolerance"] = tolerance
                    passed &= difference <= tolerance
                    actual.append({"name": case["name"], "weights": w,
                                   "expected_weights": case["expected_weights"]})
                record(case["name"], bool(passed), detail)
            except Exception:
                record(case["name"], False, {"exception": traceback.format_exc()})
        for case in invalid:
            try:
                allocate(**case["inputs"])
                record(case["name"], False, {"expected": "ValueError", "actual": "returned normally"})
            except ValueError as exc:
                record(case["name"], True, {"expected": "ValueError", "actual": str(exc)})
            except Exception:
                record(case["name"], False, {"expected": "ValueError", "exception": traceback.format_exc()})
        large = cases[-1]
        times = []
        for _ in range(32):
            started = time.perf_counter()
            allocate(**large["inputs"])
            times.append(time.perf_counter() - started)
        mean_ms = float(1000 * np.mean(times))
        one_core = environment["cpu_affinity"] is not None and len(environment["cpu_affinity"]) == 1
        record("synthetic_allocator_runtime", bool(one_core and mean_ms < 100),
               {"calls": 32, "mean_ms": mean_ms, "p95_ms": float(1000 * np.quantile(times, .95)),
                "max_ms": float(1000 * np.max(times)), "one_core": one_core,
                "scope": "Allocator only, 1000-asset synthetic known optimum"})
        save_json(out / "actual_results.json", actual)
        save_json(out / "timings.json", {"seconds": times})
        passed = all(item["status"] == "PASS" for item in summary["checks"])
        summary["status"] = "PASS_SCOPE_ONLY" if passed else "FAIL"
        code = 0 if passed else 1
    except Exception:
        summary["status"] = "EXPECTED_RED_FAILURE" if args.expected_missing_module and not args.module.exists() else "FAIL"
        summary["exception"] = traceback.format_exc()
        log.append(summary["exception"])
        print(summary["exception"], file=sys.stderr, flush=True)
    finally:
        summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
        summary["exit_code"] = code
        save_json(out / "summary.json", summary)
        (out / "run.log").write_text("\n".join(log) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
