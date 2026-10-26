# C10: one bounded expansion of the residual factor rank

## Admission, hypothesis and scope

The lead admitted slot10 in `research/EXPERIMENT_LEDGER.md` before this plan, configuration or C10 results. This plan freezes one contrast against C06. It authorizes no rank grid, retuning, further pipeline, validation access or audit access. The shared implementation and original scorer remain unchanged.

The recorded discovery spectrum distinguishes the variance captured by rank10 and rank50, but pooled retrospective components are not live trading estimates. C06 improved over C05 while their saved forecasts were byte-identical. These observations motivate testing whether a larger causal residual covariance representation helps the complete GLS-plus-factor pipeline. They do not establish that more factors are stable, that the learner needs them, or that discovery gains will persist.

**C10 versus C06 changes exactly three configuration entries:**

| Key | C06 | C10 |
|---|---:|---:|
| `candidate_id` | `C06_gls_factor` | `C10_gls_factor_rank50` |
| `learning_factor_rank` | 10 | 50 |
| `factor_rank` | 10 | 50 |

Both learning and portfolio rank change together. Therefore this complete-pipeline contrast cannot attribute a result to the learner or the portfolio individually; C10 forecasts are not expected to equal C06 forecasts. No new source, solver, objective, basis, fitting window, fee convention or fallback policy is introduced.

## Exact fixed controls and information clock

The candidate entry point remains `submission/strategy_gls_factor.py`. Its dependency closure remains `strategy_gls.py`, `gls_precision.py`, `strategy_factor.py`, `factor_portfolio.py`, `strategy.py` and `portfolio.py`. Before execution, compare these seven live source hashes against the frozen C06 run. The original scorer must retain SHA-256 `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

All other C06 configuration keys are identical: additive basis; alpha half-life252; ridge0.1;126 matured training pairs; feature clip4; risk window252; risk minimum20; variance shrinkage0.2 and floor1e-6; risk aversion1000; cost horizon20; per-stock bound0.01; gross cap1; both factor shrinkage controls0.5; both refresh intervals21. The executable JSON, not rounded prose, is the exact configuration record.

For label day j, learner beta, variance and covariance use only returns strictly before j. Learner factor refresh starts with20 observed prior rows, then41,62,...; the factor cache is local to each forecast invocation. The first potentially nonzero forecast remains row127. Portfolio factors initialize from the first actual rebalance prefix of253 rows, then refresh at274,295,..., and are never filled by full-history forecasting. Rows and slice boundaries use the frozen zero-based convention.

The existing estimator requests `min(configured_rank, len(trailing_window))` eigencomponents. With configured rank50, the first learner requests20 components, the next41, and the next50 at prior-history62. It retains only eigenvalues above the existing1e-12 threshold, so its actual numerical rank can be lower, especially after centering and market residualization. The portfolio first requests50 because its253-row prefix is already capped to a252-row trailing window. This startup rule is inherited source behavior, not a changed warmup or use of future rows.

Factor row energy is bounded by0.5 in correlation units. Daily rescaling preserves the inherited marginal variances; the diagonal remainder is at least half of those variances apart from rounding. Normalized precision still divides by the mean diagonal of the inverse covariance. The portfolio still applies its existing beta/box/cost-aware factor solver, followed by the same gross scaling. Only its previously declared convergence `RuntimeError` may trigger the unchanged diagonal fallback; learner precision errors remain run failures.

## Execution and predeclared evidence

Use only cached discovery arrays for rows `[0,2016)`. The unchanged official scorer starts at252, retains scored returns253 through2014 inclusive (1762 observations), and calls rebalance1763 times. Holdings continue across all four fixed descriptive blocks. Full original costs and the original opening-trade waiver remain unchanged.

Before numerical execution, save an admission record containing this plan, the exact C06/C10 configurations and their hashes, the exact three-key difference, unchanged dependency hashes, official scorer identity, and expected output scope. This is a mechanical configuration/source identity review, not a new unit test of existing model code. Preserve a failure rather than overwriting the record or silently changing the candidate.

Execute once on CPU3 with single-threaded numerical libraries under the existing runner:

```sh
taskset -c 3 python -u tools/run_candidate.py --project . --strategy submission/strategy_gls_factor.py --config research/configs/C10_gls_factor_rank50.json --out evidence/discovery_C10_001
```

The runner freezes its source, requested/effective configuration, scorer, common workflow expectations, protocol, environment, input identities and exact rerun command. Retain forecasts, daily ledgers, target/holding arrays, target diagnostics, official report, logs, all check outcomes and artifact hashes. The separate admission record links this C10-specific hypothesis to the run. Do not replace failed evidence or run another variant in the same directory.

Expected engineering outcomes are finite outputs, unchanged inputs/frozen sources, exact scored dates and accounting, observed box/gross limits, finite beta estimates and traceable factor diagnostics. Record fallback count/frequency, refresh count/ages, actual rank, diagonal identity error, factor energy bound, dual-gradient diagnostics, pre-scale gross and rescaling frequency. The regular schedule implies84 portfolio refreshes over1763 calls with ages0–20; a deviation requires explanation from saved diagnostics, not an edited schedule.

Measure forecast wall time, all-call candidate rebalance average and quantiles, instrumented official timing and maximum call latency. The assignment's measured average rebalance limit is strictly below100ms; an average at or above100ms is an engineering failure even if the accounting workflow exits successfully. Record any fallback explicitly; routine fallback is contrary evidence for this factor design. Do not reduce rank, change refresh, loosen tolerance, hide slow days or rerun with a changed model to rescue the result. The runner's straight-line forecast extrapolation is not a century execution.

## Evaluation and acceptance rule

The primary development comparison is pooled daily net Sharpe versus the already recorded C06 value0.762944047825874, under identical full-fee accounting. Also report gross Sharpe, annual arithmetic net mean/volatility/full fees, realized net market beta, drawdown, turnover, exposures, four fixed block metrics and all runtime/fallback evidence. A positive discovery difference is evidence for consideration only; no minimum Sharpe or requirement that every block be positive is added. A worse result is retained and argues against this added rank/complexity.

Engineering eligibility is separate from economics. A timing failure, nonfinite output, unsafe tested path or material unexplained solver fallback blocks release regardless of the observed Sharpe. Current configured altered-future checks and a long-history runtime gate remain unexecuted for C10 and cannot be inherited from C06 or a rank10 source review. The lead decides which candidate receives those gates before any finalist freeze. The frozen protocol, including pooled validation Sharpe and its predeclared tie rule, continues to govern eventual selection.

Do not extend the already completed C01–C04 bootstrap to C10 under its old plan. The discovery contrast changes both factor ranks and was chosen after prior development results; acknowledge that selection history. Validation `[2016,3024)` and audit `[3024,3780)` remain closed. This experiment alone cannot establish a strong or durable edge, identify the mechanism, or demonstrate hidden-continuation performance.
