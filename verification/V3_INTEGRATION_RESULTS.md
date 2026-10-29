# V3 integration (F2 → E2 → M1): results and legitimacy review

29 October 2026. Implements the spec in [V3_INTEGRATION_SPEC.md](V3_INTEGRATION_SPEC.md), written
before the package. GPT did the research and the selection (wave 2 docs:
[results](../research/v2/SCORE2_RESEARCH_RESULTS_20261029.md),
[plan](../research/v2/SCORE2_RESEARCH_PLAN_20261029.md),
[handoff](../research/v2/SCORE2_IMPLEMENTATION_HANDOFF_20261029.md)). Claude did the
reproduction, the audit and this integration. GPT then independently reviewed the integration
(`review/v3-integration-audit-20261029`, commit `9cb6aec`) and accepted it with `POLICY.sleeve = 0.05`.
This document applies the corrections from that review's handoff
(`reviews/V3_CLAUDE_HANDOFF_20261029.md`). Numbers come from logs committed next to this
file, except those attributed to GPT's replay, which are on the review branch.

## Verdict

- **No look-ahead or scoring error found.** Reading the code found none. In tests, replacing
  or truncating the future, and restarting in the same process, left every earlier output
  identical. The scorer and data are byte-identical to the supplied ones.
- **Two full-precision reproductions, plus a rounded clean-folder run.** GPT's code rerun here
  and the package through the integration harness agree with each other exactly. A later
  independent replay by GPT (see below) recovered the original positions exactly. The
  clean-folder CLI run confirms that the package runs with the unmodified `score.py`. It
  prints only the rounded score (1.44), so it is not a third full-precision comparison.
- **Causality is not the same as no overfitting.** Each wave had five variants, committed before
  results, and the 0.05 sleeve was fixed in advance with no grid. Still, all 3,780 rows are
  exposed development data, and there is no untouched holdout. The causality checks catch
  temporal leakage on the paths tested. They don't remove what the researchers had already
  seen, and they don't establish future Sharpe or future beta. GPT's bootstrap intervals
  don't correct for the history of earlier variants.
- **The market sleeve (M1) is a deliberate market exposure, and the selected policy keeps it.**
  - What it is: holding +0.05 of the equal-weight market.
  - In the sequence prior leader (1.318) → E2 (1.340) → E2 + sleeve (1.445), it supplies about
    0.105 of the last 0.126, roughly 83%. That is a sequential comparison, not a unique
    decomposition of the Sharpe.
  - Realized beta is 0.103, under the brief's 0.2 limit. The brief states no second, zero-beta
    threshold.
  - Market regression explains about 10% of V3's net-return variance, so the book is not
    mostly market. Beta times the mean market return is about 22.6% of its mean net return.
  - Decision (Hugo, on GPT's review): keep `POLICY.sleeve = 0.05` and describe the exposure
    openly. The market sensitivity below shows when the no-sleeve book would do better.

## Frozen checks: all pass

| Check (spec item) | Result | Log |
|---|---|---|
| Forecast exactly equal to the reference (1) | max diff 0.0 | `v3_integration_checks_after.log` |
| Virtual / inner / outer targets ≤ 1e-8 (2) | max diff 0.0 / 0.0 / 0.0 | same |
| Gross return, fee, closing gross, market ≤ 1e-8 (3) | all 0.0 | same |
| Net Sharpe ≤ 1e-8 (3) | 1.4447333005564316, diff 0.0 | same |
| Altered future and truncation at 600, 2000, 3500 (4) | identical | same |
| Cross-history restart in the same process (4) | identical | same |
| Every solve certified, all bounds respected (5) | 7,054 of 7,054 `ok`; max \|w\| 0.0165; max gross 3.04 | same |
| Allocator failure paths on the shipped files (6) | 0 failures; scope below | `v3_failure_paths.log` |
| Clean folder, unmodified `score.py strategy` | runs; rounded output Sharpe 1.44, beta 0.10, 17.8 ms/rebalance | `v3_clean_folder_run.log` |
| 25,200-row one-CPU runtime | pass: mean rebalance 11.4 ms (p99 20.4, max 317); forecast 34.8 s (0.01 h per century); all solves `ok`; worst day −1.8% | `v3_runtime_check.log` |

Before the package existed, the checks failed as expected (`v3_integration_checks_before.log`,
ModuleNotFoundError). The first clean-folder attempt failed because of my run settings:
Python's isolated mode (`-I`) removed the scorer's own folder from the import path. Its log is
kept as `v3_clean_folder_run_attempt1_isolated_mode.log`. `model_v3/engine.py` and
`allocator.py` are byte copies of the hardened `model_v2` files (SHA256 `c134317d…` and
`b9d855b3…`).

**Reference deviation, since resolved.** The spec required the reference rerun's target-array
hashes to equal GPT's published manifest. My original integration rerun matched the forecast
hash but not the target-array hashes. Its economics differed from the committed `daily.csv` by
at most 4.5e-13, and its net Sharpe by about 2.3e-13. I used that same-environment rerun as the
reference, a documented deviation from the prerequisite.

GPT then ran an independent replay of the pinned research and the unchanged package
(`review/v3-integration-audit-20261029`, commit `9cb6aec`, `reviews/V3_INDEPENDENT_REVIEW_20261029.md`).
It recovered the original forecast and all three target streams byte for byte and reproduced
the original economic rows exactly (net Sharpe 1.444733300556666). It also reran the fifteen
checks above against that exact reference, and they all passed. This resolves current
fidelity. The precise cause of the earlier discrepancy was not established; I had attributed
it to a different machine, but that was never shown.

**Scope of the failure-path and certificate evidence.**
- The failure-path checks exercise the inherited allocator and engine, which are byte copies
  of the V2 files. They do not force every fallback through the new `Book` / `ScorePolicy`
  wrapper. GPT's source review found that wiring correct, and normal runs certify every solve.
- One inherited fixture, "nonzero target kept under binding cap", logged `binding days 0`, so
  it never exercised the binding branch it names. That nonzero-beta mode is disabled in V3.
- Certificates cover each solved subproblem. They don't prove global optimality after a
  proportional gross-cap reduction.

**Runtime across replays.** GPT's independent century run on one CPU found a mean rebalance of
12.4 ms, p99 33.5 ms and max 296 ms, with 49,894 of 49,894 solves `ok`. GPT's separate
actual-sample package replay had a mean of 15.9 ms and one call at 936 ms. No cause for that
call has been established. The brief limits the mean. The century data are tiled history, so
they test runtime capacity, not financial performance.

## With and without the market sleeve (same package, unmodified scorer)

| | sleeve 0.05 (packaged) | sleeve 0.0 |
|---|---:|---:|
| Net Sharpe | **1.4447** | **1.3396** (= GPT's E2 1.3395817822) |
| Realized beta | 0.103 | 0.053 |
| Annual net return / vol | 6.61% / 4.57% | 5.89% / 4.40% |
| Annual fees | 0.254% | 0.244% |
| Sharpe, first / second half | 1.19 / 1.76 | 1.12 / 1.63 |

**Common-market sensitivity.** The simulated equal-weight market returned 14.48% a year at
14.2% volatility (Sharpe 1.02; 0.85 / 0.96 / 1.23 by thirds). The table applies the same
assumed annual market mean ν to both books with
S(ν) = [μ + β(ν − μ_market)] / σ.

| Assumed annual market mean | V3, sleeve 0.05 | E2, no sleeve |
|---|---:|---:|
| Observed +14.48% | 1.4447 | 1.3396 |
| 0% | 1.1188 | 1.1652 |
| −14.48% | 0.7928 | 0.9909 |

- **What is held fixed:** each book's observed beta (0.103 and 0.053), volatility, nonmarket
  mean, positions and costs.
- **This is descriptive arithmetic, not a replay on a different market.** Under another market
  process, the forecasts, risk estimates, positions and fees would all adapt.
- **Crossing point:** the two books tie at about 4.44% a year. That figure has no uncertainty
  interval and is not a timing rule. Recomputed here from `v3_sleeve_comparison.json`; it
  matches GPT's table.

My earlier figure of 1.286 removed only the sleeve's mean contribution. It kept the inner
book, total volatility and costs fixed, and I then compared it with the no-sleeve book's
unchanged 1.340, which still assumed the observed premium on its own 0.053 beta. That
comparison applied different market assumptions to the two books, so the table above replaces
it.

## What the package does (`handoff_v3/`)

- **F2 forecast.** Two pooled ridge learners on V2's 27 columns, with half-lives 1,008 and 252
  days. The linear coefficients are averaged; squares and beta use the slow learner.
- **Virtual F2 book.** γ = 200, cap 0.05. Its earned returns set a volatility multiplier
  a = clip(√(q1008/q63), 0.5, 2).
- **E2 inner book.** Solved against its own drifted holdings, with γ = 200/a and cap 0.05·a.
- **Outer book.** Inner + 0.05/N per stock. Explicit state objects; `forecast()` resets the
  session.
- **Engineering.** Certified solves with recovery, cold restart and diagonal fallback;
  final-book checks; NumPy only.

## Failure modes to state in the note

- **Forecast instability.** The fast learner (252-day half-life) can chase short premium swings.
- **Market-premium reversal.** The sleeve, and the implicit 0.05 of beta, lose if the market
  drifts down.
- **Beta-estimation error.** Hedges use raw trailing betas, so realized beta grows with book
  size.
- **Cost sensitivity.** Fees are small (0.25%/yr) but rise with turnover if premia change faster.
- **Integration and runtime.** Two solves per day. The mean is 11–16 ms on one CPU, but single
  calls have reached 0.3 s, and once 0.9 s.
- **Risk model.** The 0.3 factor-risk multiplier is a chosen penalty, not a calibrated variance
  forecast. Development Sharpe is not future Sharpe.
