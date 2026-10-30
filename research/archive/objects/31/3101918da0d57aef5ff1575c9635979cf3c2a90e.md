# Accounting gate: expectations recorded before implementation

**Scope:** execute the unchanged supplied scorer on fully synthetic CSV inputs and deterministic control strategies. This is an E2E evaluator/harness check, not alpha research, candidate validation, or a unit test written after implementing a covered strategy.

**Input access:** only the supplied `score.py` and the synthetic fixture defined below. No actual market CSV, protected period, or full-sample figure is needed. The supplied scorer SHA-256 is `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

## Workflow

1. Freeze this plan and the runner in a new evidence directory. Record a running status before importing numerical dependencies or executing the scorer.
2. Generate a 256-row, two-stock, thirteen-characteristic fixture as actual `returns.csv`, `characteristics.csv`, and `costs.csv` files. Preserve their hashes and the exact generating specification.
3. Import a byte-for-byte copy of the original scorer, call its `load` on those CSVs, then run each control through the original `run` and `report` functions with `start=252`.
4. Observe original scorer locals at the return event, without changing them, to retain the otherwise discarded opening row. This observation is needed to verify the free first trade directly; the returned rows alone cannot establish its cost because the opening row is discarded. These instrumented timings are descriptive, never candidate-runtime evidence.
5. Compare loaded data, control-call traces, unfiltered and returned rows, independently calculated expected metrics, and printed official metrics against the expectations below.
6. Save pass/fail per check, actual traces, environment, stdout/stderr, input and source hashes, and an exact rerun command using the frozen runner, frozen plan and frozen scorer. Preserve failures with a nonzero exit status.

## Fixture, fixed before the runner is written

- Return shape `(256, 2)`; stock order `A, B`; CSV day labels `1 ... 256`; Python row index is label minus one.
- Characteristic shape `(256, 2, 13)`; columns in the supplied order: Woe, Malice, Dread, Frolic, Up, Down, Charm, Strange, Top, Bottom, Snap, Crackle, Pop. All values are zero, with day-major then stock-major CSV rows.
- Costs `[0.001, 0.002]` in stock order.
- All returns are zero except:

| Python row | Stock A | Stock B |
|---:|---:|---:|
| 253 | 0.10 | -0.10 |
| 254 | 0.02 | 0.04 |
| 255 | 0.90 | -0.80 |

The distinctive final row is a sentinel. The original scorer must not earn it.

### Control 1: scheduled rebalancing and reversal

The control returns `[0.5,0.5]` after days 252 and 253, then `[-0.3,0.3]` after day 254. Its optional forecast is a clock marker: row `t` is `[t,-t]`. It is not a return forecast or alpha signal. The marker verifies that day `d` receives forecast row `d+1`. The control declares all five documented arguments and records them without modifying inputs.

| Day index | Earning weights | Gross return | Drifted weights | Target | Cost | Net | Target gross |
|---:|---|---:|---|---|---:|---:|---:|
| 252 | `[0,0]` | 0 | `[0,0]` | `[0.5,0.5]` | 0, opening trade free | 0 | 1 |
| 253 | `[0.5,0.5]` | 0 | `[0.55,0.45]` | `[0.5,0.5]` | 0.00015 | -0.00015 | 1 |
| 254 | `[0.5,0.5]` | 0.03 | `[51/103,52/103]` | `[-0.3,0.3]` | 0.0012048543689320388 | 0.02879514563106796 | 0.6 |

The cost on day 254 is exactly `0.001 * (51/103 + 3/10) + 0.002 * (52/103 - 3/10)`. This independently specifies both drift and reversal notional.

### Control 2: buy and hold without further trading

The control declares only `held_positions`. On its first call it returns `[0.5,0.5]`; afterwards it returns an unchanged copy of the drifted held positions passed in. No `forecast` is defined. This exercises the optional-forecast path and declared-argument adapter.

| Day index | Earning weights | Gross return | Drifted/returned weights | Cost | Net | Target gross |
|---:|---|---:|---|---:|---:|---:|
| 252 | `[0,0]` | 0 | Opening target `[0.5,0.5]` | 0 | 0 | 1 |
| 253 | `[0.5,0.5]` | 0 | `[0.55,0.45]` | 0 | 0 | 1 |
| 254 | `[0.55,0.45]` | 0.029 | `[187/343,156/343]` | 0 | 0.029 | 1 |

Normal market drift is not a trade. All costs after the initial trade must be zero for this control.

## Exact score/report expectations

For each control:

- There are three `rebalance` calls, with current day indices `[252,253,254]`. The full-history call's histories have lengths `[253,254,255]`; targets earn days `[253,254,255]` respectively.
- The observed unfiltered scorer rows have shape `(3,5)`, including opening day 252.
- The returned scorer rows have shape `(2,5)`, days `[253,254]`, CSV labels `[254,255]`. No row earns the final day 255.
- The market returns in the two retained rows are `[0,0.03]`.
- Net Sharpe uses population standard deviation, `ddof=0`. For two net values `a,b`, the independent expected Sharpe is `sqrt(252) * (a+b) / abs(b-a)`.
- Centered beta for this two-point fixture is `(b-a)/0.03`. Buy-and-hold beta is exactly `29/30`; its Sharpe is exactly `sqrt(252)`.
- Annual arithmetic return is `252*(a+b)/2`; annual volatility is `sqrt(252)*abs(b-a)/2`; yearly cost is `252*mean(cost)`; mean gross uses the after-close targets.
- Compare all economic rows, weights and unrounded metrics with `rtol=1e-12, atol=1e-13`. The clock marker and row indices are exact. Runtime fields need only be finite and nonnegative.
- Compare parsed official printed metrics with the independent expectations rounded to the scorer's stated display precision. Printed rounding is not a numerical-model tolerance.
- The loaded fixture equals its generating specification; all input arrays and source/scorer bytes remain unchanged after execution.

## Failure modes and expected handling

| Failure mode | Observable outcome that must detect it |
|---|---|
| File ordering or reshape error | Loaded array/stock/day/feature expectations disagree. |
| Initial trade charged | Observed opening row has nonzero cost. |
| Opening row retained in score | Returned row count or row alignment differs. |
| Final sentinel earned | Returned row count, final day, or economic values differ. |
| Wrong history/forecast alignment | Recorded history lengths or `[d+1,-(d+1)]` marker differ. |
| Fee charged on yesterday's targets instead of drifted holdings | Scheduled day-253 cost differs from 0.00015. |
| Wrong drift denominator | Held-position trace differs from the specified rational values. |
| Wrong buy/sell or reversal notional | Scheduled day-254 cost differs. |
| Reinvesting/deducting costs in a different NAV convention | Exact next earning weights or later cost/net values differ. |
| Normal drift treated as a trade | Buy-and-hold later cost is nonzero. |
| Wrong gross-exposure date | Day-254 scheduled gross differs from 0.6. |
| Sample rather than population standard deviation | Sharpe/volatility reconciliation fails. |
| Uncentered beta or gross rather than net beta | Independent expected beta and printed beta disagree. |
| Scorer or caller input mutated | Before/after hashes differ. |
| Exception or interrupted run | Failure/incomplete status and traceback remain; never report a pass. |

## Evidence requirements and limits

`evidence/accounting_001` will include this frozen plan, the frozen runner and scorer, generated CSV inputs, control-module sources, setup/manifest/environment records, exact rerun instructions, expected and actual results, official reports, per-call position/forecast traces, opening-inclusive rows, returned daily ledgers, stdout/stderr and a final status.

A pass establishes the declared synthetic accounting and interface paths only. It does not validate the candidate's alpha, causality, market beta, solvency, optimizer or speed. No isolated numerical unit tests are being introduced here.

**Status at creation:** expectations specified; runner not yet implemented; E2E not yet executed.
