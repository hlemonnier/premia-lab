#!/usr/bin/env python3
"""Preimplementation numerical verification of a new GLS precision helper."""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import time
import traceback

THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
import numpy as np

ATOL, RTOL, SEED = 1e-11, 1e-10, 20261026


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ready(value):
    if isinstance(value, np.ndarray):
        return ready(value.tolist())
    if isinstance(value, np.generic):
        return ready(value.item())
    if isinstance(value, dict):
        return {str(k): ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [ready(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(ready(value), indent=2, allow_nan=False) + "\n")


def fixtures():
    rng = np.random.default_rng(SEED)
    cases = {
        "analytic_diagonal_vector": (np.array([1., 2., 4.]), np.empty((3, 0)), np.array([1., -2., 4.])),
        "analytic_diagonal_matrix": (np.array([1., 2., 4.]), np.empty((3, 0)), np.array([[1., 2.], [-2., 0.], [4., -4.]])),
        "constant_diagonal": (np.full(7, 2.), np.zeros((7, 3)), rng.normal(size=(7, 4))),
        "one_stock": (np.array([.4]), np.array([[.2, -.3, .1]]), np.array([[2., -1.]])),
    }
    for n in (3, 7, 20):
        for p in (0, 4):
            cases[f"dense_n{n}_{'vector' if p == 0 else 'matrix'}"] = (
                np.geomspace(.01, 1., n), rng.normal(0, .1, (n, 3)),
                rng.normal(size=n if p == 0 else (n, p)))
    d, b, v = np.geomspace(.01, 1., 7), rng.normal(0, .1, (7, 3)), rng.normal(size=(7, 4))
    rotation = np.linalg.qr(rng.normal(size=(3, 3)))[0]
    cases["rotation_base"] = d, b, v
    cases["rotated_factors"] = d, b @ rotation, v
    cases["sign_flipped_factors"] = d, b * np.array([-1., 1., -1.]), v
    cases["redundant_factors"] = d, np.column_stack((b[:, 0], b[:, 0], b[:, 1], b[:, 1])), v
    for scale in (.01, 100.):
        cases[f"covariance_scale_{scale}"] = d * scale, b * np.sqrt(scale), v
    large = (np.geomspace(.01, .1, 1000), rng.normal(0, .02, (1000, 10)), rng.normal(size=(1000, 27)))
    large_rotation = np.linalg.qr(rng.normal(size=(10, 10)))[0]
    good_d, good_b, good_v = np.array([.1, .2]), np.ones((2, 1)) * .1, np.ones((2, 3))
    invalid = {
        "nonvector_diagonal": (np.ones((2, 1)), good_b, good_v),
        "empty_diagonal": (np.empty(0), np.empty((0, 1)), np.empty((0, 1))),
        "zero_diagonal": (np.array([0., .2]), good_b, good_v),
        "negative_diagonal": (np.array([-.1, .2]), good_b, good_v),
        "nan_diagonal": (np.array([np.nan, .2]), good_b, good_v),
        "infinite_diagonal": (np.array([np.inf, .2]), good_b, good_v),
        "nonmatrix_factors": (good_d, np.ones(2), good_v),
        "factor_row_mismatch": (good_d, np.ones((3, 1)), good_v),
        "nonfinite_factors": (good_d, np.array([[np.inf], [0.]]), good_v),
        "scalar_values": (good_d, good_b, np.array(1.)),
        "three_dimensional_values": (good_d, good_b, np.ones((2, 1, 1))),
        "value_row_mismatch": (good_d, good_b, np.ones((3, 1))),
        "empty_rhs_columns": (good_d, good_b, np.empty((2, 0))),
        "nonfinite_values": (good_d, good_b, np.array([np.nan, 1.])),
        "unrepresentable_precision": (np.array([1e-320, 2e-320]), np.empty((2, 0)), np.ones(2)),
    }
    return cases, large, large_rotation, invalid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    module, plan, out = (p.resolve() for p in (args.module, args.plan, args.out))
    out.mkdir(parents=True, exist_ok=False)
    summary = {"status": "RUNNING", "started_utc": now(), "seed": SEED, "checks": [],
               "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
               "scope": "Synthetic new-helper numerical verification; no market data", "atol": ATOL, "rtol": RTOL}
    write_json(out / "summary.json", summary)
    shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
    shutil.copyfile(plan, out / "expectations.md")
    frozen_module = out / "helper_used.py" if module.exists() else out / "deliberately_absent_helper.py"
    if module.exists():
        shutil.copyfile(module, frozen_module)
    rerun = shlex.join([sys.executable, str(out / "runner_used.py"), "--module", str(frozen_module),
                       "--plan", str(out / "expectations.md"), "--out", str(out) + "_rerun"])
    (out / "rerun.txt").write_text(rerun + "\n")
    identity = {"runner_sha256": digest(out / "runner_used.py"), "plan_sha256": digest(out / "expectations.md"),
                "module_sha256": digest(frozen_module) if frozen_module.exists() else None,
                "module_present_before_run": frozen_module.exists()}
    write_json(out / "identity.json", identity)
    write_json(out / "setup.json", {"seed": SEED, "input_kind": "fixed synthetic fixtures", "rerun": rerun,
                                    "requires": ["numpy", "Python standard library"], "forbidden_input": "actual market observations"})
    exit_code = 1

    def check(name, condition, **actual):
        summary["checks"].append({"name": name, "status": "PASS" if condition else "FAIL", **ready(actual)})
        write_json(out / "summary.json", summary)
        if not condition:
            raise AssertionError(name)

    def run_valid(fn, name, inputs, expected=None, expected_mean=None):
        arrays = tuple(np.array(x, dtype=np.float64, copy=True) for x in inputs)
        before = [x.copy() for x in arrays]
        for x in arrays:
            x.setflags(write=False)
        weighted, mean_precision = fn(*arrays)
        weighted = np.asarray(weighted)
        valid = (weighted.shape == arrays[2].shape and weighted.dtype == np.float64
                 and np.isfinite(weighted).all() and np.ndim(mean_precision) == 0
                 and np.isfinite(mean_precision) and mean_precision > 0)
        check(name + "_contract", bool(valid), output_shape=weighted.shape, dtype=str(weighted.dtype), mean_precision=mean_precision)
        repeat, repeated_mean = fn(*arrays)
        check(name + "_repeat_and_inputs", bool(np.array_equal(weighted, repeat) and mean_precision == repeated_mean
              and all(np.array_equal(x, old) for x, old in zip(arrays, before))))
        if expected is not None:
            check(name + "_reference", bool(np.allclose(weighted, expected, atol=ATOL, rtol=RTOL)
                  and np.isclose(mean_precision, expected_mean, atol=ATOL, rtol=RTOL)),
                  max_weighted_error=float(np.max(np.abs(weighted - expected))),
                  actual_mean_precision=mean_precision, expected_mean_precision=expected_mean)
        return weighted, float(mean_precision)

    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                affinity = None
                if hasattr(os, "sched_getaffinity"):
                    allowed = sorted(os.sched_getaffinity(0))
                    os.sched_setaffinity(0, {allowed[0]})
                    affinity = sorted(os.sched_getaffinity(0))
                write_json(out / "environment.json", {"python": sys.version, "numpy": np.__version__,
                           "platform": platform.platform(), "threads": {k: os.environ[k] for k in THREADS},
                           "cpu_affinity": affinity})
                if not frozen_module.exists():
                    summary["status"] = "EXPECTED_RED_MISSING_MODULE"
                    raise FileNotFoundError("Helper intentionally absent before implementation; no numerical check has run")
                spec = importlib.util.spec_from_file_location("gls_precision_under_test", frozen_module)
                helper = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(helper)
                fn = helper.normalized_precision_apply
                cases, large, rotation, invalid = fixtures()
                write_json(out / "inputs.json", {"valid": cases, "large": large, "large_rotation": rotation, "invalid": invalid})
                results = {}
                for name, inputs in cases.items():
                    d, b, values = inputs
                    covariance = np.diag(d) + b @ b.T
                    mean_precision = float(np.diag(np.linalg.inv(covariance)).mean())
                    expected = np.linalg.solve(covariance, values) / mean_precision
                    actual, actual_mean = run_valid(fn, name, inputs, expected, mean_precision)
                    results[name] = (actual, actual_mean)
                base, base_mean = results["rotation_base"]
                for name in ("rotated_factors", "sign_flipped_factors"):
                    a, m = results[name]
                    check(name + "_basis_invariance", bool(np.allclose(a, base, atol=ATOL, rtol=RTOL)
                          and np.isclose(m, base_mean, atol=ATOL, rtol=RTOL)))
                for scale in (.01, 100.):
                    a, m = results[f"covariance_scale_{scale}"]
                    check(f"scale_{scale}_invariance", bool(np.allclose(a, base, atol=ATOL, rtol=RTOL)
                          and np.isclose(m * scale, base_mean, atol=ATOL, rtol=RTOL)))
                for name, inputs in invalid.items():
                    arrays = tuple(np.array(x, copy=True) for x in inputs)
                    before = [x.copy() for x in arrays]
                    for x in arrays:
                        x.setflags(write=False)
                    try:
                        fn(*arrays)
                    except ValueError as exc:
                        check(name, all(np.array_equal(x, old, equal_nan=True) for x, old in zip(arrays, before)),
                              expected="ValueError", actual=str(exc))
                    else:
                        check(name, False, expected="ValueError", actual="returned without rejection")
                large_result, large_mean = run_valid(fn, "universe_1000", large)
                rotated = (large[0], large[1] @ rotation, large[2])
                run_valid(fn, "universe_1000_rotation", rotated, large_result, large_mean)
                timings = []
                for _ in range(16):
                    tick = time.perf_counter()
                    fn(*large)
                    timings.append((time.perf_counter() - tick) * 1000)
                write_json(out / "timings.json", {"calls": 16, "mean_ms": float(np.mean(timings)),
                           "p95_ms": float(np.quantile(timings, .95)), "max_ms": max(timings), "raw_ms": timings,
                           "scope": "Helper only; no full-strategy runtime claim"})
                np.save(out / "large_weighted_values.npy", large_result)
                write_json(out / "actual_results.json", {"small_cases": results, "large_mean_precision": large_mean,
                           "large_weighted_sha256": digest(out / "large_weighted_values.npy")})
                check("frozen_sources_unchanged", digest(frozen_module) == identity["module_sha256"]
                      and digest(out / "runner_used.py") == identity["runner_sha256"]
                      and digest(out / "expectations.md") == identity["plan_sha256"])
                summary["status"], exit_code = "EXECUTED_PASS_SCOPE_ONLY", 0
            except KeyboardInterrupt:
                summary["status"], exit_code = "INCOMPLETE", 130
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
            except Exception:
                if summary["status"] != "EXPECTED_RED_MISSING_MODULE":
                    summary["status"] = "EXECUTED_FAIL"
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                summary.update(finished_utc=now(), exit_code=exit_code,
                               unverified=["GLS strategy causality", "alpha quality", "full scoring workflow", "century runtime"])
                write_json(out / "summary.json", summary)
    print(summary["status"], "checks", len(summary["checks"]), "exit", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
