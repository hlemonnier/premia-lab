# V3 integration (F2 → E2 → M1): results and legitimacy review

29 October 2026. Implements the spec in [V3_INTEGRATION_SPEC.md](V3_INTEGRATION_SPEC.md), written
before the package. GPT did the research and the selection (wave 2 docs:
[results](../research/v2/SCORE2_RESEARCH_RESULTS_20261029.md),
[plan](../research/v2/SCORE2_RESEARCH_PLAN_20261029.md),
[handoff](../research/v2/SCORE2_IMPLEMENTATION_HANDOFF_20261029.md)). Claude did the
reproduction, the audit and this integration. Every number below comes from a log committed
next to this file.

## Verdict

- **No cheating found.** The forecast is causal both by reading the code and by test: replacing
  or truncating the future, and restarting in the same process, leave every earlier output
  identical. The scorer and data are byte-identical to the supplied ones. The score was
  reproduced three ways: GPT's code rerun independently, the new package through the
  integration harness, and the package from a clean folder with the unmodified `score.py`.
- **Selection was disciplined but used exposed data.** Each wave had five variants, committed
  before results. The 0.05 sleeve was fixed in advance, with no grid. All 3,780 rows had been
  seen during research, so expect shrinkage out of sample. GPT's bootstrap intervals don't
  correct for the history of earlier variants.
- **The judgment call is the market sleeve (M1).** About 0.105 of the 0.126 gain over the prior
  leader comes from deliberately holding +0.05 of the equal-weight market. That is market
  carry, not stock selection. Realized beta is 0.103, which passes the 0.2 limit. But the brief
  says "hedge the market out or build the book so it is not there". If the sleeve earned no
  market premium, the score would be 1.286, below the 1.340 of the no-sleeve book. The package
  exposes `POLICY.sleeve`. Shipping 0.05 or 0.0 is the applicant's decision.

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
| Allocator failure paths on the shipped files (6) | 0 failures | `v3_failure_paths.log` |
| Clean folder, unmodified `score.py strategy` | Sharpe 1.44, beta 0.10, 17.8 ms/rebalance | `v3_clean_folder_run.log` |
| 25,200-row one-CPU runtime | pass: mean rebalance 11.4 ms (p99 20.4, max 317); forecast 34.8 s (0.01 h per century); all solves `ok`; worst day −1.8% | `v3_runtime_check.log` |

Before the package existed, the checks failed as expected (`v3_integration_checks_before.log`,
ModuleNotFoundError). The first clean-folder attempt failed because of my run settings:
Python's isolated mode (`-I`) removed the scorer's own folder from the import path. Its log is
kept as `v3_clean_folder_run_attempt1_isolated_mode.log`. `model_v3/engine.py` and
`allocator.py` are byte copies of the hardened `model_v2` files (SHA256 `c134317d…` and
`b9d855b3…`).

**Deviation from the spec.** The spec asked that the reference rerun's target-array hashes
equal GPT's published manifest. The forecast hash matches. The target hashes don't: GPT ran in
a different environment, and the economics differ from GPT's committed `daily.csv` by at most
4.5e-13. I used the same-environment rerun as the reference. The net Sharpe agrees with GPT's
1.444733300556666 to 1e-13.

## With and without the market sleeve (same package, unmodified scorer)

| | sleeve 0.05 (packaged) | sleeve 0.0 |
|---|---:|---:|
| Net Sharpe | **1.4447** | **1.3396** (= GPT's E2 1.3395817822) |
| Realized beta | 0.103 | 0.053 |
| Annual net return / vol | 6.61% / 4.57% | 5.89% / 4.40% |
| Annual fees | 0.254% | 0.244% |
| Sharpe, first / second half | 1.19 / 1.76 | 1.12 / 1.63 |

Market-drift sensitivity of the packaged book: its annual net return is 6.61% and its Sharpe
1.4447. The simulated equal-weight market returned 14.5% a year at 14.2% volatility (Sharpe
1.02; 0.85 / 0.96 / 1.23 by thirds).

| Scenario for the market premium | Packaged book's Sharpe |
|---|---:|
| Sleeve's 0.05 earns no premium | 1.286 |
| Sleeve's premium is reversed | 1.128 |
| All 0.103 of realized beta earns no premium | 1.119 |

E2 already carries 0.053 of beta through the raw-beta hedge (the earlier corrected-beta work
documented this). So even the no-sleeve book is partly market carry.

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
- **Integration and runtime.** Two solves per day. The mean is 11 ms on one CPU, but single
  calls can reach about 0.3 s.
