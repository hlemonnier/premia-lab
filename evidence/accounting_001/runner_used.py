#!/usr/bin/env python3
"""E2E synthetic accounting gate for the unchanged supplied evaluator.

Expectations were specified in verification/ACCOUNTING_PLAN.md before this
runner was implemented. This runner reads no actual market CSV files.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import sys
import traceback


SCORER_SHA256 = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"
THREAD_VARIABLES = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)
FEATURES = (
    "Woe", "Malice", "Dread", "Frolic", "Up", "Down", "Charm",
    "Strange", "Top", "Bottom", "Snap", "Crackle", "Pop",
)
ATOL, RTOL = 1e-13, 1e-12

SCHEDULED_CONTROL = '''"""Synthetic scheduled-trade control, not a candidate strategy."""
import numpy as np
CALLS = []
FORECAST_INPUT_SHAPES = []

def forecast(returns_history, characteristics_history, trading_costs):
    FORECAST_INPUT_SHAPES.append([list(returns_history.shape),
                                  list(characteristics_history.shape),
                                  list(trading_costs.shape)])
    clock = np.arange(len(returns_history), dtype=float)
    return np.column_stack([clock, -clock])

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    day = len(returns_history) - 1
    if day in (252, 253):
        target = np.array([0.5, 0.5])
    elif day == 254:
        target = np.array([-0.3, 0.3])
    else:
        raise ValueError(f"Unexpected synthetic decision day: {day}")
    CALLS.append({"day": day, "earning_day": day + 1,
                  "held": held_positions.copy().tolist(),
                  "target": target.copy().tolist(),
                  "expected_returns": expected_returns.copy().tolist(),
                  "returns_shape": list(returns_history.shape),
                  "characteristics_shape": list(characteristics_history.shape),
                  "latest_return": returns_history[-1].copy().tolist(),
                  "costs": trading_costs.copy().tolist()})
    return target
'''

HOLD_CONTROL = '''"""Synthetic buy-and-hold control with no forecast."""
import numpy as np
CALLS = []

def rebalance(held_positions):
    day = 252 + len(CALLS)
    target = np.array([0.5, 0.5]) if not CALLS else held_positions.copy()
    CALLS.append({"day": day, "earning_day": day + 1,
                  "held": held_positions.copy().tolist(),
                  "target": target.copy().tolist()})
    return target
'''


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_ready(value):
    if hasattr(value, "tolist"):
        return json_ready(value.tolist())
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(json_ready(value), indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self):
        for stream in self.streams:
            stream.flush()


class Gate:
    def __init__(self, out, summary):
        self.out, self.summary = out, summary

    def check(self, name, condition, actual, expected=None):
        item = {"name": name, "status": "PASS" if condition else "FAIL", "actual": actual}
        if expected is not None:
            item["expected"] = expected
        self.summary["checks"].append(item)
        write_json(self.out / "summary.json", self.summary)
        if not condition:
            raise AssertionError(f"Accounting gate failed: {name}")

    def numeric(self, name, actual, expected):
        actual, expected = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
        same_shape = actual.shape == expected.shape
        good = same_shape and bool(np.allclose(actual, expected, rtol=RTOL, atol=ATOL))
        error = float(np.max(np.abs(actual - expected))) if same_shape and actual.size else None
        self.check(name, good, {"shape": list(actual.shape), "max_abs_error": error,
                               "values": actual}, {"values": expected, "rtol": RTOL, "atol": ATOL})


def import_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def array_hashes(arrays):
    return [hashlib.sha256(a.tobytes(order="C")).hexdigest() for a in arrays]


def fixture(folder):
    folder.mkdir()
    returns = np.zeros((256, 2), dtype=float)
    returns[253:] = [[0.1, -0.1], [0.02, 0.04], [0.90, -0.80]]
    characteristics = np.zeros((256, 2, 13), dtype=float)
    costs = np.array([0.001, 0.002])
    with (folder / "returns.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["day", "A", "B"])
        writer.writerows([day + 1, *row] for day, row in enumerate(returns))
    with (folder / "characteristics.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["day", "stock", *FEATURES])
        writer.writerows([day + 1, stock, *characteristics[day, index]]
                         for day in range(256) for index, stock in enumerate(("A", "B")))
    with (folder / "costs.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerows([["stock", "cost"], ["A", 0.001], ["B", 0.002]])
    return returns, characteristics, costs


def expected_cases():
    reversal_cost = float(Fraction(1, 1000) * (Fraction(51, 103) + Fraction(3, 10))
                          + Fraction(1, 500) * (Fraction(52, 103) - Fraction(3, 10)))
    return {
        "scheduled_trades": {
            "source": SCHEDULED_CONTROL,
            "rows": [[0, 0, 1, 0], [0, 0.00015, 1, 0], [0.03, reversal_cost, 0.6, 0.03]],
            "held": [[0, 0], [0.55, 0.45], [51 / 103, 52 / 103]],
            "targets": [[0.5, 0.5], [0.5, 0.5], [-0.3, 0.3]],
        },
        "buy_and_hold": {
            "source": HOLD_CONTROL,
            "rows": [[0, 0, 1, 0], [0, 0, 1, 0], [0.029, 0, 1, 0.03]],
            "held": [[0, 0], [0.55, 0.45], [187 / 343, 156 / 343]],
            "targets": [[0.5, 0.5], [0.55, 0.45], [187 / 343, 156 / 343]],
        },
    }


def analytic_metrics(expected_rows):
    first, second = expected_rows[1:]
    a, b = first[0] - first[1], second[0] - second[1]
    return {
        "sharpe": math.sqrt(252) * (a + b) / abs(b - a),
        "annual_return": 252 * (a + b) / 2,
        "annual_volatility": math.sqrt(252) * abs(b - a) / 2,
        "beta": (b - a) / 0.03,
        "annual_cost": 252 * (first[1] + second[1]) / 2,
        "mean_gross": (first[2] + second[2]) / 2,
    }


def actual_metrics(rows):
    gross, cost, exposure, market, _timing = rows.T
    net = gross - cost
    centered = market - market.mean()
    return {
        "sharpe": float(np.sqrt(252) * net.mean() / net.std(ddof=0)),
        "annual_return": float(252 * net.mean()),
        "annual_volatility": float(np.sqrt(252) * net.std(ddof=0)),
        "beta": float(centered @ (net - net.mean()) / (centered @ centered)),
        "annual_cost": float(252 * cost.mean()),
        "mean_gross": float(exposure.mean()),
    }


def save_rows(path, rows, start):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["array_index", "csv_day", "gross_return", "cost", "net_return",
                         "target_gross", "market_return", "rebalance_seconds"])
        for offset, row in enumerate(rows):
            gross, cost, exposure, market, seconds = row
            day = start + offset
            writer.writerow([day, day + 1, gross, cost, gross - cost, exposure, market, seconds])


def check_report(gate, name, report, expected):
    pattern = (r"sharpe\s+(\S+)\s+return\s+(\S+)%/yr\s+vol\s+(\S+)%\s+"
               r"beta\s+(\S+)\s+cost\s+(\S+)%/yr\s+gross\s+(\S+)")
    match = re.search(pattern, report)
    gate.check(name + ".report_parse", match is not None, report.strip())
    labels = ["sharpe", "annual_return", "annual_volatility", "beta", "annual_cost", "mean_gross"]
    expected_tokens = [f"{expected['sharpe']:.2f}", f"{100 * expected['annual_return']:.1f}",
                       f"{100 * expected['annual_volatility']:.1f}", f"{expected['beta']:.2f}",
                       f"{100 * expected['annual_cost']:.2f}", f"{expected['mean_gross']:.2f}"]
    gate.check(name + ".official_report_metrics", list(match.groups()) == expected_tokens,
               dict(zip(labels, match.groups())), dict(zip(labels, expected_tokens)))


def run_control(out, scorer, arrays, name, expected, gate):
    case_dir = out / name
    case_dir.mkdir()
    control_file = case_dir / "control.py"
    control_file.write_text(expected["source"])
    control = import_file(control_file, "accounting_control_" + name)
    input_before = array_hashes(arrays)
    observed = {}

    def observe_return(frame, event, _argument):
        if event == "return" and frame.f_code is scorer.run.__code__:
            observed["raw_rows"] = np.asarray(frame.f_locals.get("rows", []), dtype=float).copy()

    previous_profile = sys.getprofile()
    try:
        sys.setprofile(observe_return)
        rows, forecast_seconds = scorer.run(control, *arrays, start=252)
    finally:
        sys.setprofile(previous_profile)
        write_json(case_dir / "calls.json", control.CALLS)
        if observed.get("raw_rows", np.array([])).size:
            save_rows(case_dir / "opening_inclusive_rows.csv", observed["raw_rows"], 252)

    save_rows(case_dir / "daily.csv", rows, 253)
    raw = observed["raw_rows"]
    gate.check(name + ".call_days", [c["day"] for c in control.CALLS] == [252, 253, 254],
               [c["day"] for c in control.CALLS], [252, 253, 254])
    gate.check(name + ".raw_shape", raw.shape == (3, 5), list(raw.shape), [3, 5])
    gate.check(name + ".returned_shape", rows.shape == (2, 5), list(rows.shape), [2, 5])
    gate.numeric(name + ".opening_inclusive_economic_rows", raw[:, :4], expected["rows"])
    gate.numeric(name + ".scored_economic_rows", rows[:, :4], expected["rows"][1:])
    gate.numeric(name + ".held_positions", [c["held"] for c in control.CALLS], expected["held"])
    gate.numeric(name + ".target_positions", [c["target"] for c in control.CALLS], expected["targets"])
    gate.check(name + ".opening_removed_once", bool(np.array_equal(rows, raw[1:])),
               {"exact_returned_slice_match": bool(np.array_equal(rows, raw[1:]))})
    gate.check(name + ".opening_trade_free", raw[0, 1] == 0.0, float(raw[0, 1]), 0.0)
    gate.check(name + ".timing_finite_nonnegative",
               bool(np.isfinite(raw[:, 4]).all() and (raw[:, 4] >= 0).all()
                    and math.isfinite(forecast_seconds) and forecast_seconds >= 0),
               {"forecast_seconds": forecast_seconds, "rebalance_seconds": raw[:, 4]})
    gate.check(name + ".caller_inputs_unchanged", array_hashes(arrays) == input_before,
               array_hashes(arrays), input_before)

    if name == "scheduled_trades":
        gate.check(name + ".forecast_full_input", control.FORECAST_INPUT_SHAPES == [[[256, 2], [256, 2, 13], [2]]],
                   control.FORECAST_INPUT_SHAPES, [[[256, 2], [256, 2, 13], [2]]])
        gate.numeric(name + ".forecast_row_delivery", [c["expected_returns"] for c in control.CALLS],
                     [[253, -253], [254, -254], [255, -255]])
        gate.check(name + ".return_history_shapes",
                   [c["returns_shape"] for c in control.CALLS] == [[253, 2], [254, 2], [255, 2]],
                   [c["returns_shape"] for c in control.CALLS])
        gate.check(name + ".characteristic_history_shapes",
                   [c["characteristics_shape"] for c in control.CALLS] == [[253, 2, 13], [254, 2, 13], [255, 2, 13]],
                   [c["characteristics_shape"] for c in control.CALLS])
        gate.numeric(name + ".latest_return_delivery", [c["latest_return"] for c in control.CALLS],
                     [[0, 0], [0.1, -0.1], [0.02, 0.04]])
        gate.numeric(name + ".cost_delivery", [c["costs"] for c in control.CALLS],
                     [[0.001, 0.002]] * 3)
    else:
        gate.check(name + ".no_forecast_path", not hasattr(control, "forecast") and forecast_seconds == 0,
                   {"has_forecast": hasattr(control, "forecast"), "forecast_seconds": forecast_seconds})
        gate.check(name + ".no_trade_cost", bool((rows[:, 1] == 0.0).all()), rows[:, 1], [0.0, 0.0])

    expected_metrics = analytic_metrics(expected["rows"])
    measured = actual_metrics(rows)
    gate.numeric(name + ".unrounded_metrics", list(measured.values()), list(expected_metrics.values()))
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        scorer.report(name, rows, forecast_seconds, 256)
    report = buffer.getvalue()
    (case_dir / "official_report.txt").write_text(report)
    print(report, end="")
    check_report(gate, name, report, expected_metrics)
    np.savez(case_dir / "positions.npz", held=np.array([c["held"] for c in control.CALLS]),
             targets=np.array([c["target"] for c in control.CALLS]),
             earning_day=np.array([c["earning_day"] for c in control.CALLS]))
    result = {"status": "PASS", "metrics": measured, "expected_metrics": expected_metrics,
              "forecast_seconds": forecast_seconds, "returned_rows": int(len(rows)),
              "control_sha256": digest(control_file), "input_hashes_after": array_hashes(arrays)}
    write_json(case_dir / "actual.json", result)
    return result


def execute(args, out, summary):
    global np
    for variable in THREAD_VARIABLES:
        os.environ[variable] = "1"
    affinity = {"requested_one_core": True}
    try:
        available = sorted(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {available[0]})
        affinity["actual"] = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError, IndexError) as exc:
        affinity["unavailable_reason"] = str(exc)

    shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
    shutil.copyfile(args.plan, out / "expectations.md")
    (out / "source").mkdir()
    shutil.copyfile(args.scorer, out / "source" / "score.py")
    rerun = [sys.executable, str(out / "runner_used.py"), "--scorer", str(out / "source" / "score.py"),
             "--plan", str(out / "expectations.md"), "--out", str(out.with_name(out.name + "_rerun"))]
    summary["rerun_command"] = shlex.join(rerun)
    (out / "rerun.sh").write_text("#!/usr/bin/env bash\nset -euo pipefail\nexec " + shlex.join(rerun) + "\n")
    (out / "rerun.txt").write_text(shlex.join(rerun) + "\n")
    source_manifest = {"original_scorer": {"path": str(args.scorer), "sha256": digest(args.scorer)},
                       "frozen_scorer": {"path": "source/score.py", "sha256": digest(out / "source" / "score.py")},
                       "runner": {"path": "runner_used.py", "sha256": digest(out / "runner_used.py")},
                       "plan": {"path": "expectations.md", "sha256": digest(out / "expectations.md")}}
    write_json(out / "source_manifest.json", source_manifest)
    gate = Gate(out, summary)
    gate.check("original_scorer_identity", source_manifest["original_scorer"]["sha256"] == SCORER_SHA256,
               source_manifest["original_scorer"]["sha256"], SCORER_SHA256)
    gate.check("frozen_scorer_identity", source_manifest["frozen_scorer"]["sha256"] == SCORER_SHA256,
               source_manifest["frozen_scorer"]["sha256"], SCORER_SHA256)

    import numpy as np
    import pandas as pd

    packages = {}
    for distribution in ("numpy", "pandas", "scipy", "cvxpy", "scikit-learn", "lightgbm"):
        try:
            packages[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            packages[distribution] = "NOT_INSTALLED"
    write_json(out / "environment.json", {"python": sys.version, "executable": sys.executable,
               "platform": platform.platform(), "packages": packages, "affinity": affinity,
               "threads": {k: os.environ[k] for k in THREAD_VARIABLES},
               "timing_limit": "Instrumented synthetic runs are not candidate-runtime evidence."})
    write_json(out / "setup.json", {"input_scope": "Generated synthetic inputs only; no actual market CSV read",
               "rows": 256, "stocks": ["A", "B"], "features": FEATURES, "start": 252,
               "returns_nonzero_rows": {253: [0.1, -0.1], 254: [0.02, 0.04], 255: [0.9, -0.8]},
               "costs": [0.001, 0.002], "rtol": RTOL, "atol": ATOL,
               "opening_observer": "Read-only sys.setprofile return-event observation of original scorer rows"})
    generated = fixture(out / "inputs")
    input_manifest = [{"path": str(p.relative_to(out)), "bytes": p.stat().st_size, "sha256": digest(p)}
                      for p in sorted((out / "inputs").glob("*.csv"))]
    write_json(out / "input_manifest.json", input_manifest)
    scorer = import_file(out / "source" / "score.py", "original_accounting_scorer")
    arrays = scorer.load(str(out / "inputs"))
    for name, actual, expected in zip(("returns", "characteristics", "costs"), arrays, generated):
        gate.check("loaded_" + name + "_exact", actual.shape == expected.shape and bool(np.array_equal(actual, expected)),
                   {"shape": list(actual.shape), "exact_numeric_match": bool(np.array_equal(actual, expected))},
                   {"shape": list(expected.shape)})
    cases = expected_cases()
    write_json(out / "expected.json", {name: {**{k: v for k, v in expected.items() if k != "source"},
                                              "metrics": analytic_metrics(expected["rows"])}
                                        for name, expected in cases.items()})
    actual_cases = {}
    for name, expected in cases.items():
        actual_cases[name] = run_control(out, scorer, arrays, name, expected, gate)
        write_json(out / "actual.json", actual_cases)
    gate.check("original_scorer_unchanged", digest(args.scorer) == SCORER_SHA256, digest(args.scorer), SCORER_SHA256)
    gate.check("frozen_scorer_unchanged", digest(out / "source" / "score.py") == SCORER_SHA256,
               digest(out / "source" / "score.py"), SCORER_SHA256)
    input_after = [{"path": item["path"], "bytes": (out / item["path"]).stat().st_size,
                    "sha256": digest(out / item["path"])} for item in input_manifest]
    gate.check("synthetic_files_unchanged", input_after == input_manifest, input_after, input_manifest)
    summary["cases"] = actual_cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scorer", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.scorer, args.plan, args.out = args.scorer.resolve(), args.plan.resolve(), args.out.resolve()
    if args.out.exists():
        parser.error(f"Refusing to overwrite evidence: {args.out}; choose a fresh --out path.")
    args.out.mkdir(parents=True)
    summary = {"scope": "Synthetic CSV-to-original-scorer accounting/interface E2E only",
               "status": "running", "started_utc": now(), "checks": [],
               "actual_market_rows_read": 0,
               "run_command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
               "unverified": ["candidate alpha", "candidate causality", "candidate beta", "candidate safety",
                              "candidate optimizer", "candidate runtime", "hidden-future performance"]}
    write_json(args.out / "summary.json", summary)
    exit_code = 1
    with (args.out / "stdout.log").open("w") as stdout, (args.out / "stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(Tee(sys.stdout, stdout)), contextlib.redirect_stderr(Tee(sys.stderr, stderr)):
            try:
                execute(args, args.out, summary)
                summary["status"] = "EXECUTED_PASS_SCOPE_ONLY"
                exit_code = 0
            except KeyboardInterrupt:
                summary["status"] = "INCOMPLETE"
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
                exit_code = 130
            except Exception:
                summary["status"] = "EXECUTED_FAIL"
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                summary["finished_utc"] = now()
                summary["exit_code"] = exit_code
                write_json(args.out / "summary.json", summary)
                passed = sum(c["status"] == "PASS" for c in summary["checks"])
                print(f"Accounting E2E: {summary['status']}; {passed}/{len(summary['checks'])} checks passed; evidence {args.out}")
                (args.out / "README.md").write_text(
                    "# Synthetic accounting E2E evidence\n\n"
                    f"Status: **{summary['status']}**. Exit code: {exit_code}. "
                    f"Recorded checks passed: {passed}/{len(summary['checks'])}.\n\n"
                    "Read expectations.md for predeclared inputs and outcomes, summary.json for all checks, "
                    "and each control folder for call/position traces, opening-inclusive rows, scored daily rows "
                    "and the official report. Inputs are fully synthetic and are included. "
                    "The supplied scorer is copied unchanged under source/.\n\n"
                    "Rerun the frozen runner/scorer/plan with the exact command in rerun.txt or `bash rerun.sh`. "
                    "Use a fresh output path if the recorded rerun destination already exists. "
                    "Dependencies used are Python, NumPy and pandas; exact versions are in environment.json.\n\n"
                    "These runs validate only the declared synthetic accounting/interface workflows. "
                    "No actual market CSV is read and no candidate, alpha, causality, beta or runtime claim is established.\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
