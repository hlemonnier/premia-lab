# C06 independent source audit

Review date: 27 October 2026, Europe/Paris. This is source reasoning before the new full-discovery numerical gate. No completion or numerical pass is implied.

## Scope and finding

The reviewer read the committed seven-file C06 dependency closure: `strategy_gls_factor.py`, `strategy_gls.py`, `strategy_factor.py`, `strategy.py`, `gls_precision.py`, `factor_portfolio.py`, and `portfolio.py`. The supplied scorer, exact C06 JSON configuration, frozen protocol, existing two causality plans, and unchanged fresh-process controller/worker were also inspected. File hashes are frozen in the admission evidence.

**No implementation timing violation was found in that closure.** The source supports a causal information flow under the original scorer contract. The numerical gate remains required: source reasoning is not a substitute for executed protected-output comparisons.

## Information flow

For output forecast row `t`, `strategy_gls.forecast` uses the most recently matured pair consisting of characteristics at `t-2` and return at `t-1`. Label residualization and precision construction receive `returns[:t-1]`, strictly before that label. Current features are characteristics at `t-1`. Cross-sectional centering, scaling, clipping and square construction use that one published panel only, with no whole-history normalization. All13 existing characteristics enter; no future-dependent subset selection is performed by this source.

The EW Gram matrix, response moment, mass, number of matured days and learner factor cache are local variables created inside each forecast call. Learner loadings refresh at prior-history counts20,41,..., use only the trailing252 observations already available, and get rescaled by current causal marginal variance. The first nonzero-capable forecast is127 after126 matured daily pairs. The first active learner refresh is forecast147; a refresh with window eviction is forecast273. The global learner configuration contains fixed controls, not learned state.

`strategy_gls_factor.configure` passes consistent common controls to learner and portfolio, and `strategy_factor.configure` resets the portfolio cache and last-history marker. The shared base module is configured twice with the same common controls; it does not acquire fitted state from either operation. `forecast` delegates only to the learner. It cannot populate the portfolio factor cache. `rebalance` delegates only to the portfolio and receives original-scorer history through the current close.

The portfolio estimates beta and residual variances from its supplied trailing history. Its cache first fills at earning-day target253, refreshes at274, and is reused at275 while beta/marginal variance update. Repeated or decreasing history length clears the cache. The scorer's actual path advances history length by one; the current numerical gate exercises that ordinary path, not arbitrary external API call sequences. Cache reset logic is source-reviewed without claiming a numerical repeated-history test.

The precision and portfolio helpers operate only on supplied arrays/scalars and contain no fitted global state or market-file access. The allocation uses actual drifted holdings, positive diagonal risk plus low-rank factors, estimated-beta equality and stock boxes, with a documented diagonal fallback on factor solver nonconvergence. A final proportional gross rescale preserves the estimated-beta hedge; it is an approximation to the full gross-constrained trading objective. That quality limitation is not lookahead. Full actual costs remain charged by the unchanged scorer.

## File, state and clock review

The imported candidate closure has no file/network reads, process spawning, dynamic imports, wall-clock decisions, random sampling, external learned artifacts, or use of total future input length to choose a historical refit date. Output-array allocation and loop length depend on total days, but every emitted historical row uses the same prior-only recurrence. NumPy/SciPy imports and deterministic numerical solvers are dependencies; their implementation internals are not audited here. Candidate source does not inspect validation/audit files or supplied figures.

The original scorer deliberately passes all history to `forecast` once, so merely accepting that argument is not sufficient evidence of causality. The row-wise source reasoning and full future-alteration/prefix/append runs are the relevant checks. Rebalance receives the next earning day's forecast and history ending at the current close; no target is shifted back after seeing its earned return.

## Harness and accounting boundary review

The unchanged controller copies the bounded discovery cache, verifies its hashes, freezes sibling candidate modules/config/scorer/protocol/plan, and launches a new interpreter for every scenario. Arrays are marked read-only and checked by before/after hashes. The worker's transparent adapter records complete forecast/target outputs while the unchanged scorer runs. On failure, exception-only traceback inspection can retain partial rows; unsuccessful workers do not become passes. No normal-path tracing changes the model or book state.

Protected forecasts include row `c`; protected earning-day targets include `c`; protected economics stop strictly before `c`. This distinction is correct because row `c` can affect its own closing cost while its earning-day target was chosen earlier. Prefix and append comparisons respect the scorer's dropped opening row and unearned final input return. Numerical comparisons exclude wall times. Empty ranges are reported not applicable. The saved-output reporter additionally checks actual masks/scenarios and actual hashes rather than trusting status labels.

## Overfitting is a separate question

The discovery leader's Sharpe was selected after eleven configuration results and earlier feature/risk diagnostics. That makes discovery performance optimistic as an estimate of unseen continuation, irrespective of causal code. Fixed half-lives, basis, risk settings and other choices were influenced by research evidence; the complete exposure ledger matters more than a simplistic count of eleven independent trials. No deflated-Sharpe, PBO or other no-overfit certificate is inferred from this audit.

Marginal linear sign changes can also arise from changing cross-characteristic covariance even with stable joint coefficients. Characteristic persistence is distinct from forecast persistence and persistence of predictive value. These observations motivate controlled, preregistered comparisons; they do not establish an edge. The internal untouched validation/audit split is a stricter research control than the assignment's fixed-parameter tuning allowance and remains binding.

## Release status

Source review: **no timing violation found in the inspected closure**. Full-discovery numerical gate: **not run at document creation**. Long-history performance and clean-folder execution: separate pending gates. Validation/audit outcomes remain unopened. Final reporting must link actual completed evidence and preserve any interrupted/failed runs; finite tested-path success cannot justify universal no-lookahead or no-overfit claims.
