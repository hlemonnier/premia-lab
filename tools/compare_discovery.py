#!/usr/bin/env python3
"""Reconcile fixed wave-1 ledgers and report paired block-bootstrap uncertainty.

This reporting E2E does not import strategies, refit models, replay portfolios
or read original market data. See research/WAVE1_COMPARISON_PLAN.md.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shlex
import shutil
import sys
import traceback

for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"
import numpy as np

CANDIDATES = ("C01", "C02", "C03", "C04")
IDS = ("C01_linear", "C02_additive", "C03_additive_fast", "C04_additive_factor")
FILES = ("daily.csv", "target_diagnostics.csv", "config.json", "summary.json", "source_manifest.json",
         "input_manifest.json", "environment.json", "artifact_manifest.json")
PAIRS = (("C01", "C01"), ("C02", "C01"), ("C03", "C01"), ("C04", "C01"), ("C04", "C02"))
SEED, DRAWS, LENGTHS = 20261026, 1000, (21, 63)
ATOL, RTOL = 1e-12, 1e-10
SCORER_SHA = "ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96"


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean(value):
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Nonfinite reporting output")
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_numeric(path):
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        records = list(reader)
    if not records:
        raise ValueError(f"Empty ledger: {path}")
    return {key: np.array([float(row[key]) for row in records], dtype=np.float64) for key in reader.fieldnames}


def metrics(daily, mask):
    net, gross, cost, market = (daily[key][mask] for key in
                               ("net_return", "gross_return", "full_cost", "raw_market_return"))
    if len(net) == 0 or net.std() == 0 or gross.std() == 0:
        raise ValueError("Undefined Sharpe in declared reporting interval")
    centered_market = market - market.mean()
    market_ss = centered_market @ centered_market
    if market_ss <= 0 or np.any(net <= -1):
        raise ValueError("Undefined market beta or compounding wealth")
    wealth = np.concatenate(([1.], np.cumprod(1 + net)))
    return {
        "scored_days": len(net), "daily_net_mean": float(net.mean()),
        "net_sharpe": float(np.sqrt(252) * net.mean() / net.std(ddof=0)),
        "gross_sharpe": float(np.sqrt(252) * gross.mean() / gross.std(ddof=0)),
        "annual_arithmetic_net_return": float(252 * net.mean()),
        "annual_net_volatility": float(np.sqrt(252) * net.std(ddof=0)),
        "annual_full_cost": float(252 * cost.mean()),
        "realized_net_market_beta": float(centered_market @ (net - net.mean()) / market_ss),
        "mean_gross_exposure": float(daily["closing_target_gross"][mask].mean()),
        "max_drawdown": float(np.max(1 - wealth / np.maximum.accumulate(wealth))),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument("--project", type=Path)
    location.add_argument("--inputs", type=Path, help="Frozen input directory for exact rerun")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    frozen = out / "inputs"
    frozen.mkdir()
    plan = args.plan or args.project / "research/WAVE1_COMPARISON_PLAN.md"
    shutil.copyfile(plan.resolve(), out / "expectations.md")
    shutil.copyfile(Path(__file__).resolve(), out / "runner_used.py")
    summary = {"status": "RUNNING", "started_utc": now(), "checks": [],
               "scope": "Previously executed C01-C04 discovery artifacts only; no candidate fits or replay",
               "command": shlex.join([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
               "bootstrap": {"method": "paired circular moving blocks", "seed": SEED, "draws": DRAWS,
                             "block_lengths": LENGTHS, "pairs": PAIRS}}
    rerun = shlex.join([sys.executable, str(out / "runner_used.py"), "--inputs", str(frozen),
                       "--plan", str(out / "expectations.md"), "--out", str(out) + "_rerun"])
    (out / "rerun.txt").write_text(rerun + "\n")
    write_json(out / "setup.json", {"inputs": "Eight saved evidence files for each fixed candidate",
               "source_runs": [f"discovery_{key}_001" for key in CANDIDATES], "rerun": rerun,
               "requires": ["Python standard library", "numpy"], "forbidden": ["new candidate execution", "actual validation/audit observations"]})
    write_json(out / "environment.json", {"python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
               "thread_environment": {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}})
    write_json(out / "summary.json", summary)
    input_identity = {}
    exit_code = 1

    def check(name, condition, actual=None):
        summary["checks"].append({"name": name, "status": "PASS" if condition else "FAIL", "actual": clean(actual)})
        write_json(out / "summary.json", summary)
        if not condition:
            raise AssertionError(name)

    with (out / "stdout.log").open("w") as stdout, (out / "stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                pooled, blocks, diagnostics, daily_series = [], [], [], []
                common_inputs = None
                common_market = None
                dates = np.arange(253, 2015)
                for key, expected_id in zip(CANDIDATES, IDS):
                    source = (args.project.resolve() / "evidence" / f"discovery_{key}_001") if args.project else args.inputs.resolve() / key
                    destination = frozen / key
                    destination.mkdir()
                    original_manifest = json.loads((source / "artifact_manifest.json").read_text())
                    hashes = {}
                    for name in FILES:
                        source_path = source / name
                        hashes[name] = digest(source_path)
                        if name != "artifact_manifest.json":
                            check(f"{key}_{name}_original_identity", hashes[name] == original_manifest[name]["sha256"], hashes[name])
                        shutil.copyfile(source_path, destination / name)
                    input_identity[key] = {"source": str(source), "sha256": hashes}
                    run = json.loads((destination / "summary.json").read_text())
                    config = json.loads((destination / "config.json").read_text())
                    sources = json.loads((destination / "source_manifest.json").read_text())
                    inputs = json.loads((destination / "input_manifest.json").read_text())
                    check(key + "_completed_original_run", run["status"] == "EXECUTED_PASS_SCOPE_ONLY" and run["exit_code"] == 0
                          and all(x["status"] == "PASS" for x in run["checks"]), {"status": run["status"], "exit": run["exit_code"]})
                    check(key + "_candidate_identity", config["candidate_id"] == expected_id and sources["config.json"] == hashes["config.json"], config)
                    check(key + "_authority_and_window", sources["source/score.py"] == SCORER_SHA
                          and inputs["input_slice"] == [0, 2016] and run["score_slice"] == [253, 2015], sources["source/score.py"])
                    if common_inputs is None:
                        common_inputs = inputs["cache_sha256"]
                    check(key + "_same_market_input_identity", inputs["cache_sha256"] == common_inputs, inputs["cache_sha256"])
                    daily = read_numeric(destination / "daily.csv")
                    targets = read_numeric(destination / "target_diagnostics.csv")
                    check(key + "_exact_scored_dates", np.array_equal(daily["return_index"], dates), {"count": len(daily["return_index"]), "first": daily["return_index"][0], "last": daily["return_index"][-1]})
                    check(key + "_finite_ledgers", all(np.isfinite(v).all() for v in daily.values()) and all(np.isfinite(v).all() for v in targets.values()))
                    check(key + "_net_full_cost", bool(np.allclose(daily["net_return"], daily["gross_return"] - daily["full_cost"], atol=ATOL, rtol=RTOL)
                          and np.all(daily["full_cost"] >= 0)))
                    if common_market is None:
                        common_market = daily["raw_market_return"]
                    check(key + "_same_market_ledger", np.array_equal(daily["raw_market_return"], common_market))
                    check(key + "_target_dates", np.array_equal(targets["target_earning_index"], np.arange(253, 2016)))
                    check(key + "_target_fee_and_gross_reconciliation", bool(np.allclose(targets["full_trade_cost"][1:], daily["full_cost"], atol=ATOL, rtol=RTOL)
                          and np.allclose(targets["target_gross"][1:], daily["closing_target_gross"], atol=ATOL, rtol=RTOL)))
                    current = metrics(daily, np.ones(len(dates), dtype=bool))
                    check(key + "_summary_metrics_reconciliation", all(np.isclose(value, run["metrics"][field], atol=ATOL, rtol=RTOL)
                          for field, value in current.items()), current)
                    pooled.append({"candidate": key, "candidate_id": expected_id, **current,
                                   "candidate_mean_rebalance_ms": run["timing"]["all_calls_candidate_mean_ms"],
                                   "forecast_seconds": run["timing"]["forecast_candidate_seconds"], "config_sha256": hashes["config.json"]})
                    for number, saved_block in enumerate(run["blocks"], start=1):
                        mask = (dates >= (number - 1) * 504) & (dates < number * 504)
                        block_result = metrics(daily, mask)
                        check(f"{key}_block_{number}_reconciliation", all(np.isclose(value, saved_block[field], atol=ATOL, rtol=RTOL)
                              for field, value in block_result.items()))
                        blocks.append({"candidate": key, "block": number, "first_return_index": int(dates[mask][0]),
                                       "last_return_index": int(dates[mask][-1]), **block_result})
                    trace = {"candidate": key, "rebalance_calls": len(targets["target_gross"]),
                             "mean_daily_abs_turnover": float(targets["turnover_abs_weight"][1:].mean()),
                             "total_abs_turnover_charged": float(targets["turnover_abs_weight"][1:].sum()),
                             "maximum_gross": float(targets["target_gross"].max()),
                             "maximum_abs_stock_weight": float(targets["max_abs_stock_weight"].max()),
                             "maximum_abs_net_exposure": float(np.abs(targets["target_net"]).max()),
                             "mean_pre_scale_gross": float(targets["pre_scale_gross"].mean()),
                             "maximum_pre_scale_gross": float(targets["pre_scale_gross"].max()),
                             "minimum_gross_scale": float(targets["gross_scale"].min()),
                             "rescale_call_count": int(np.sum(targets["gross_scale"] < 1)),
                             "rescale_call_fraction": float(np.mean(targets["gross_scale"] < 1)),
                             "mean_pre_scale_box_saturation_fraction": float(targets["pre_scale_box_saturation_fraction"].mean())}
                    check(key + "_trading_summary_reconciliation", all(np.isclose(value, run["trading"][field], atol=ATOL, rtol=RTOL)
                          for field, value in trace.items() if field not in ("candidate", "rebalance_calls")), trace)
                    diagnostics.append(trace)
                    daily_series.append(daily["net_return"])
                write_json(out / "input_manifest.json", input_identity)
                write_csv(out / "pooled_metrics.csv", pooled)
                write_csv(out / "fixed_blocks.csv", blocks)
                write_csv(out / "portfolio_diagnostics.csv", diagnostics)
                net = np.column_stack(daily_series)
                observed = np.sqrt(252) * net.mean(axis=0) / net.std(axis=0, ddof=0)
                uncertainty = []
                index_hashes = {}
                for length in LENGTHS:
                    rng = np.random.default_rng(np.random.SeedSequence([SEED, length]))
                    starts = rng.integers(0, len(dates), size=(DRAWS, math.ceil(len(dates) / length)))
                    indices = ((starts[:, :, None] + np.arange(length)) % len(dates)).reshape(DRAWS, -1)[:, :len(dates)]
                    check(f"bootstrap_L{length}_indices", indices.shape == (DRAWS, len(dates)) and bool(np.all((indices >= 0) & (indices < len(dates)))))
                    samples = net[indices]
                    boot = np.sqrt(252) * samples.mean(axis=1) / samples.std(axis=1, ddof=0)
                    check(f"bootstrap_L{length}_finite", bool(np.isfinite(boot).all()))
                    np.save(out / f"bootstrap_indices_L{length}.npy", indices)
                    index_hashes[str(length)] = digest(out / f"bootstrap_indices_L{length}.npy")
                    draw_rows = []
                    differences = []
                    for left, right in PAIRS:
                        li, ri = CANDIDATES.index(left), CANDIDATES.index(right)
                        delta = boot[:, li] - boot[:, ri]
                        differences.append(delta)
                        low, median, high = np.quantile(delta, [.025, .5, .975])
                        uncertainty.append({"contrast": left + " minus " + right, "block_length": length, "draws": DRAWS,
                                            "observed_difference": float(observed[li] - observed[ri]),
                                            "bootstrap_mean": float(delta.mean()), "bootstrap_std_ddof1": float(delta.std(ddof=1)),
                                            "percentile_2_5": float(low), "percentile_50": float(median), "percentile_97_5": float(high),
                                            "bootstrap_fraction_positive_not_posterior": float(np.mean(delta > 0))})
                    check(f"bootstrap_L{length}_self_control_zero", bool(np.all(differences[0] == 0)))
                    for draw in range(DRAWS):
                        record = {"draw": draw}
                        record.update({candidate + "_net_sharpe": float(boot[draw, i]) for i, candidate in enumerate(CANDIDATES)})
                        record.update({left + "_minus_" + right: float(differences[i][draw]) for i, (left, right) in enumerate(PAIRS)})
                        draw_rows.append(record)
                    write_csv(out / f"bootstrap_draws_L{length}.csv", draw_rows)
                write_csv(out / "paired_sharpe_differences.csv", uncertainty)
                check("frozen_inputs_unchanged", all(digest(frozen / key / name) == expected
                      for key, item in input_identity.items() for name, expected in item["sha256"].items()))
                summary.update(status="EXECUTED_PASS_SCOPE_ONLY", pooled_metrics=pooled, portfolio_diagnostics=diagnostics,
                               paired_uncertainty=uncertainty, bootstrap_index_sha256=index_hashes)
                lines = ["# Wave 1 discovery comparison", "", "The four initial candidates do not establish a strong trading edge. These are development-sample outcomes, and the small observed improvements require much more caution than their ranking alone suggests.", "",
                         "| Candidate | Net Sharpe | Gross Sharpe | Annual net mean | Annual vol | Annual fees | Net beta |", "|---|---:|---:|---:|---:|---:|---:|"]
                for row in pooled:
                    lines.append(f"| {row['candidate']} | {row['net_sharpe']:.4f} | {row['gross_sharpe']:.4f} | {row['annual_arithmetic_net_return']:.3%} | {row['annual_net_volatility']:.3%} | {row['annual_full_cost']:.3%} | {row['realized_net_market_beta']:.4f} |")
                lines += ["", "## Paired circular moving-block uncertainty", "", "Both predeclared block lengths are reported. Intervals are 2.5th–97.5th percentile bootstrap ranges of paired Sharpe differences; the sign frequency is not a posterior probability or a selection rule.", "",
                          "| Contrast | Block length | Observed delta | 95% percentile range | Bootstrap fraction positive |", "|---|---:|---:|---:|---:|"]
                for row in uncertainty:
                    lines.append(f"| {row['contrast']} | {row['block_length']} | {row['observed_difference']:.4f} | [{row['percentile_2_5']:.4f}, {row['percentile_97_5']:.4f}] | {row['bootstrap_fraction_positive_not_posterior']:.3f} |")
                lines += ["", "## Interpretation limits", "", "The same daily block indices were used for every candidate in each draw. This preserves paired returns and within-block dependence; it does not establish stationarity, cover every dependence length, correct all research selection or predict hidden-future results. Circular joins are artificial. An interval containing zero is not proof of equivalence. No candidate was fitted or replayed by this report, and no validation/audit or later-candidate results were read.", "",
                          "`pooled_metrics.csv`, `fixed_blocks.csv` and `portfolio_diagnostics.csv` retain exact means, costs, exposure/scaling and all four fixed blocks. `bootstrap_draws_L21.csv` and `bootstrap_draws_L63.csv` preserve all draws. The frozen inputs, identities, seed and generation rule reproduce this report through `rerun.txt`. Runtime values are inherited observed measurements and are not new controlled benchmarks."]
                (out / "REPORT.md").write_text("\n".join(lines) + "\n")
                exit_code = 0
            except KeyboardInterrupt:
                summary["status"], exit_code = "INCOMPLETE", 130
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
            except Exception:
                summary["status"] = "EXECUTED_FAIL"
                summary["error"] = traceback.format_exc()
                traceback.print_exc()
            finally:
                summary.update(finished_utc=now(), exit_code=exit_code,
                               limitations=["Development sample only", "Approximate conditional bootstrap under unproven stationarity",
                                            "No complete research-selection correction", "No candidate fitting or untouched-period access"])
                write_json(out / "summary.json", summary)
    manifest = {str(p.relative_to(out)): {"sha256": digest(p), "bytes": p.stat().st_size}
                for p in sorted(out.rglob("*")) if p.is_file() and p.name != "artifact_manifest.json"}
    write_json(out / "artifact_manifest.json", manifest)
    print(summary["status"], "checks", len(summary["checks"]), "exit", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
