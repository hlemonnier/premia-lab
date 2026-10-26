# Independent verification and reproducibility design

**Phase:** scoping and planning only.  
**Reviewer:** independent verification reviewer.  
**Status:** source inspection completed; no strategy implemented, no model fit, no E2E test executed by this reviewer, and no performance claim made.  
**Scope:** the supplied README, scorer, strategy interface and two example modules. This memo does not inspect return outcomes or prescribe an alpha model.

## 1. Rules that govern implementation

1. Never write unit tests after implementing the code they cover.
2. Prefer complete CSV-to-strategy-to-score workflows over isolated tests.
3. If an isolated check is genuinely needed, first write its failure modes, edge cases and expected outcomes; then write the check; only then implement the covered component. Record this order. A small numerical optimizer might justify this exception; a pure restatement of its implementation does not.
4. Every E2E execution, successful or failed, must produce an inspectable evidence directory with setup, input identity, exact rerun command, expectations, actual outcomes and relevant logs/output files. An interrupted run must leave an incomplete-run record, rather than vanish.
5. Keep status labels literal: **planned**, **executed/pass**, **executed/fail**, **blocked**, or **not applicable**. Source review is not an executed test. A passing finite replay does not establish future profitability or unconditional solvency.

The current phase should finish the verification specification before implementing new strategy code. Read-only structural profiling and a bounded execution of a supplied control strategy can establish the environment and scoring contract without consuming future model-selection information.

## 2. Exact source contract and important traps

| Topic | Contract observed in source | Verification implication |
|---|---|---|
| Objective | Future net Sharpe is the objective; daily net beta to the equal-weight market must be under 0.2 (`README.md:27–43,118–129,147–161`). | Rank by a locked net-score protocol; report beta separately. Do not turn turnover, leverage, aesthetics or a forecast metric into an invented headline objective. |
| Daily information | Returns and characteristics for a day arrive together after its close; positions for day `t` may use only rows before `t` (`README.md:49–57,74–95`). | Row `t` of `forecast` must remain unchanged when either data array is changed from row `t` onward. Test the boundary row itself, not only earlier rows. |
| Forecast access | `forecast` receives the complete history once and may return arbitrary additional dimensions with days first (`README.md:63–70`; `score.py:41–46`). | Check causality of every output channel and any state `forecast` leaves for `rebalance`. A correct-looking expected-return channel is insufficient if a future-informed risk model is cached globally. |
| Strategy interface | The evaluator passes only declared named arguments; `rebalance` returns one weight per stock (`strategy.py:24–35`; `score.py:26–30,58–64`). | Run the submitted module through the supplied adapter. Require numeric shape `(n,)`, finite values and no mutation of caller-owned input arrays. |
| Positional loading | The scorer converts characteristics to an array and reshapes it, and takes the cost vector in file order (`score.py:17–23`). | Explicitly verify the CSV index order, not just the set of identifiers. A valid-looking array can silently pair a stock with another stock's characteristics or cost. |
| Drift | Gross return is earned on the prior target; positions then drift as `w*(1+r)/(1+w@r)` (`score.py:51–55`). | Costs must be computed against these drifted weights. Comparing with yesterday's target understates or misstates turnover. |
| Bankruptcy | The supplied assertion is gross portfolio return `> -1` (`score.py:54`). | Preserve the assertion. Record minimum denominator and gross/net losses; do not silently clamp a catastrophic return and call the workflow valid. The code's assertion is not proof that a high-cost or previously unseen future path is economically safe. |
| Cost timing | Today's cost is charged after today's return, for the trade into tomorrow; first trade is free (`score.py:66–71`; `README.md:101–114`). | Net return at day `d` includes the post-close trade at `d`. If data at `d` change, that trade and its cost may legitimately change. Do not compare net outcomes at the perturbation boundary as if they must be invariant. |
| Exact scored rows | Loop indices are `start` through `T-2`; the first flat row is dropped (`score.py:51,71`). | Retained rows are Python indices `start+1` through `T-2`, inclusive: `T-start-2` rows. With `T=3780, start=252`, this is 3,526 rows, indices 253…3778. The final return row 3779 is never earned. |
| Last trade boundary | The trade at `T-2` pays costs and chooses positions for `T-1`, but that last day's return is not in the returned rows (`score.py:51,67–71`). | Preserve this convention for official-score parity; document it. A separate economics diagnostic may quantify the effect, but must never replace the headline evaluator silently. |
| Report formulas | Net Sharpe uses population standard deviation, `ddof=0`; beta is centered OLS with an intercept against the raw equal-weight daily return (`score.py:74–83`). | Match the exact formulas. The printed annual return is annualized arithmetic mean, not CAGR. Gross exposure is measured after rebalancing, not before today's return. |
| Equal-weight control | The supplied baseline returns target weights `1/n` (`example_equal_weight.py:5–7`) and deliberately fails the beta requirement (`README.md:165–171`). | Gross daily return equals the raw market after initialization. Net beta need not be exactly 1: drift rebalancing costs can covary with market returns. Assert gross parity, not an unjustified exact net-beta identity. |
| Continuation | The long run begins like the scorer, at day 252 with an empty book; the observed fifteen years are warm-up for subsequent scoring (`README.md:112–114`). | Emulate chronological continuation through warm-up, preserving holdings and learned state. Merely setting a local split's `start` to its test boundary resets the book and is a different experiment. The precise private evaluator is not visible. |
| Runtime | `rebalance` must average under 100 ms on one core; forecast allowance is approximately one hour per century (`README.md:59–67,189–195`). | Measure end to end under controlled thread counts, including periodic expensive refreshes. A short easy prefix cannot establish long-horizon runtime. |
| Dependencies | The evaluator provides NumPy, pandas, SciPy, CVXPY, scikit-learn and LightGBM, and no additional third-party packages (`README.md:193–195`). | The submission must import and run using only declared allowed dependencies and the standard library. A missing local package is a local environment gap, not evidence that the evaluator lacks it. |

**Index convention:** distinguish Python row indices from CSV `day` labels everywhere. If the first CSV label is 1, Python index 252 is CSV day 253. Determine and record this from metadata; do not silently equate them.

**Beta interpretation:** the prose says “under 0.2,” while the intent is to remove market exposure. Pending clarification, report both signed beta and absolute beta, target a small magnitude with margin, and avoid exploiting a large negative beta or trivial rescaling as a substitute for removing the market. No finite sample certifies the private future beta.

## 3. Prioritized acceptance gates

### G0 — Provenance, schema and environment (before strategy implementation)

**Failure modes:** changed sources; incomplete archive extraction; shuffled or duplicate rows; mismatched stock ordering; nonfinite data; unexpected feature count; incorrect day mapping; undeclared dependency or multithreaded benchmark.

**Workflow:** hash the archive and each extracted member; retain the originals; inspect metadata and full-file structure without inspecting protected evaluation outcomes. Load the three CSVs through `score.load`, compare with independently read index metadata, and record exact array shapes and ordering. Verify all return columns, per-day characteristic stock sequences and cost rows agree in order. Verify each expected day/stock pair occurs once; no dropped days, extra feature columns, nonfinite values or malformed costs. Record Python and used package versions and which optional allowed packages are absent.

**Expected outcome:** either an exact, documented schema compatible with the supplied loader or an explicit block with the affected identifiers/rows. Metadata/finiteness checks may inspect the entire file; use no full-sample return distribution, characteristic-return association or regime discovery before the split protocol is fixed.

**Evidence:** archive/member hashes, structural report, source snapshots or source hashes, environment report, command, stdout/stderr. Structural correctness says nothing about predictability.

### G1 — Supplied-scorer control workflow (before strategy implementation)

**Failure modes:** off-by-one scoring; costs deducted on the wrong day; charging the opening trade; charging a fee on target changes rather than drifted changes; substituting CAGR or sample standard deviation; treating equal-weight as a compliant candidate.

**Workflow:** execute a predeclared bounded prefix using the supplied equal-weight module and original scorer; save daily rows and independent arithmetic reconciliation. For a 504-row prefix and default `start=252`, expect 250 returned rows corresponding to Python indices 253…502, not 251 or 252. Run a hand-specified synthetic CSV workflow as described in section 4 when the harness is built.

**Expected outcome:** scoring row count, gross-market parity, cost reconstruction and report formulas agree within stated floating-point tolerances. The equal-weight control is expected to have material market beta and is not expected to qualify as a final strategy. No candidate alpha or holdout performance is inferred.

**Evidence:** exact prefix boundaries and day labels; daily gross/cost/net/gross-exposure records; reconciliation differences; unrounded metrics and printed report; environment and rerun command.

### G2 — Causality and absence of future-state leakage (hard gate for every candidate)

**Failure modes:** unshifted characteristics; fitting/scaling on the entire sequence; centered rolling windows; full-sample PCA or clusters; normalizing using future samples; startup sizing from future weeks; training on labels that have not yet matured; full-history length-dependent preprocessing; a causal forecast that seeds a noncausal global optimizer state.

**Workflow:** perform altered-future and prefix-length replays in fresh processes, with both full forecast output and actual portfolio target traces compared. See section 5. Inspect the source to check hidden file access, global caches and transformations that numerical spot checks might miss.

**Expected outcome:** all causally protected outputs agree to a documented, strict floating-point tolerance. Material deviations fail the gate even if the Sharpe is better. Explicitly record the largest absolute and relative differences; no “close enough” blanket tolerance.

**Evidence:** deterministic perturbation recipe/seed; original and altered input hashes; cutoff table; compared ranges; all output-channel differences; portfolio and state differences; source review notes.

### G3 — Executability, arithmetic and operational safety (hard gate)

**Failure modes:** NaN or incorrect-shape weights; solver failure; negative risk estimate; degenerate covariance; zero forecast; extreme exposures; division by a near-zero portfolio-growth denominator; mutated input arrays; random state or old module state leaking between runs.

**Workflow:** run the complete final interface on the declared normal data window and on deterministic synthetic edge-case histories. Include constant prices/zero cross-sectional dispersion, identical features, a market jump, a single-stock outlier, nearly collinear assets, initially insufficient learning history, and a planned model/risk refresh. Check only behavior promised by the submission; malformed input rejection need not become a large separate framework.

**Expected outcome:** finite outputs, defined cold-start/fallback behavior, finite realized score when variance is nonzero, no source/input mutation, no unhandled solver failure, and documented position-sizing response. Zero-return cash produces undefined Sharpe rather than a fabricated zero/positive score. Stress tests report the actual path and severity; do not call a pass a guarantee against all possible synthetic-market futures.

**Evidence:** scenario definitions with expected responses written before implementation; full execution traces; minimum `1 + portfolio_return`; minimum daily net return; peak exposures; fallback counts and reasons; any failure traceback.

### G4 — Validation discipline and economic reproduction (research gate)

**Failure modes:** tuning after reading the final local holdout; resetting capital/book/state at a split; reporting only gross performance; cherry-picking a good year or model; treating correlated daily or cross-sectional observations as independent; silently changing the trial budget.

**Workflow:** fix chronological folds, fit windows, state warm-up policy, training-label availability, trial budget and final local holdout before research. A replay starts at the common initialization and flows through warm-up; score masks select validation periods without resetting holdings. Candidate parameters must be chosen using the allowed development prefix for each fold; online updates may consume only matured observations as time advances. Log every trial and rationale, including failures and discarded variants.

**Expected outcome:** one reproducible candidate-selection decision supported by net metrics, beta, costs and stability diagnostics. The report separates (a) tuning on the supplied fifteen years, which the brief explicitly permits, from (b) a genuinely unconsulted local interval, if one is maintained. Do not label a repeatedly consulted interval “out of sample” without explaining that it is validation.

**Evidence:** split manifest and its creation timestamp/hash; candidate/trial ledger; configuration hashes; complete daily traces for compared strategies; precommitted selection criteria; per-period and pooled results. Pool daily net returns to compute the pooled Sharpe; do not substitute the average of fold Sharpes.

### G5 — Beta control and sizing robustness (research and feasibility gate)

**Failure modes:** equating dollar neutrality with market-beta neutrality; hedging predicted gross returns but ignoring realized net beta; accepting a value close to the limit based on a noisy short interval; increasing leverage without accounting for its effect on position drift and future costs.

**Workflow:** calculate the supplied centered net-beta formula for each declared validation period and pooled period. Report rolling/period sensitivity as diagnostics. Check market shocks through the full strategy and include realistic, predeclared cost-sensitivity and sizing comparisons. Keep the score-cost convention unchanged for the main result.

**Expected outcome:** a justified margin to the beta requirement and a defensible sizing policy. The primary optimization objective remains future net Sharpe. Costs, turnover and gross exposure explain it; they are not hidden objectives imposed on top. Gross and net betas are both useful diagnostics, but the net beta is the required quantity.

**Evidence:** unrounded signed and absolute beta, sample sizes, market variance, exposure traces, stress definitions and results. An interval with zero market variance has undefined beta; fail or label it unavailable rather than reporting zero.

### G6 — Long-horizon runtime and state growth (hard engineering gate)

**Failure modes:** timing with a multithreaded BLAS; omitting periodic retraining; a forecast that is fast on 15 years but quadratic in the number of days; unbounded caches; repeatedly copying the full history; a final dependency missing on a clean system.

**Workflow:** run the exact final module with thread-count environment variables set before Python imports. Measure the same time boundaries as `score.run`, using a fresh process and full amortized update cycles. Record CPU/OS and thread settings. Report average, median, p95, maximum, total time and forecast time; only the required average limit is the formal rebalance gate. Check scaling on multiple predeclared history lengths and, when feasible, a synthetic decades-long continuation that tests engineering rather than economic predictive performance.

**Expected outcome:** measured average rebalance time below 100 ms on one core with practical margin, and a supported forecast scaling estimate compatible with approximately one hour per 25,200 trading days. A linear projection alone must be labeled a projection. Inspect state size as the horizon grows; the input itself already includes a large `(days,1000,13)` tensor.

**Evidence:** process-level resource/timing logs, package versions, CPU/thread settings, all periodic refresh timestamps, observed history-length/runtime table and peak memory if available. No hardware-independent speed guarantee is possible from one machine.

### G7 — Clean-room submission and reviewer reproduction (final gate)

**Failure modes:** imported notebooks or workbench files; hard-coded local paths; stale fitted objects; hidden CSV reads bypassing the evaluator inputs; missing helper files; unused dependencies; human/AI contribution overclaiming; a note that promises results not established by executed runs.

**Workflow:** assemble only the submission files and allowed dependencies in a fresh directory. Copy the unmodified scorer and the supplied input data there, then run `python score.py strategy` with controlled threads. Reproduce the selected metrics from the saved final configuration. A separate reviewer reads both the submitted code and its one-page top-of-file note against the evidence ledger and causality results.

**Expected outcome:** a self-contained module plus explicitly declared helper files, no path/network dependence, no private precomputed future information, an honest note and a reproducible official score. Do not include the private full research workbench in the minimal submission unless it is needed.

**Evidence:** final file list and hashes, dependency list, exact command, complete stdout/stderr, daily trace and metrics, reviewer decision and unresolved limits. Preserve the richer research/evidence bundle separately for the user.

## 4. Predeclared golden CSV-to-score fixture

This is a proposed end-to-end accounting fixture, not an executed test and not a production strategy. It uses two stocks, 13 characteristics and 256 rows so the supplied default `START=252` remains unchanged. The first 253 return rows may be zero; characteristic values may be zero. A deterministic control module emits the targets in the table. Costs are `[0.001, 0.002]`.

| Python day index | Return vector | Target after close | Expected returned accounting |
|---|---|---|---|
| 252 | `[0, 0]` | `[0.5, 0.5]` | Initial gross return 0 and opening cost 0; this row is discarded. |
| 253 | `[0.10, -0.10]` | `[0.5, 0.5]` | Gross return 0; drifted weights `[0.55,0.45]`; cost `0.00015`; net `-0.00015`; post-trade gross 1. |
| 254 | `[0.02, 0.04]` | `[-0.3, 0.3]` | Gross return `0.03`; drifted weights `[51/103,52/103]`; cost `0.0012048543689320388`; net `0.02879514563106796`; post-trade gross `0.6`. |
| 255 | Any finite, deliberately distinctive values | Not called | This final return is not earned by `score.run`; it must not appear as a scored row. |

This single workflow detects drift-denominator errors, charge timing, paid closing/reversal notional, a mistaken free later trade, final-day misalignment and use of pre-trade exposure in the printed gross statistic. Assert exactly two returned rows. Derive report Sharpe and beta from those two rows using the official `ddof=0` and centered-beta equations. Store both the expected table and the actual trace.

A second control that returns its **drifted held positions unchanged** should incur zero trading costs after the opening trade; it catches a harness that treats normal market drift as a trade. These are complete evaluator workflows, not post-hoc unit tests of a newly implemented strategy component.

## 5. Causality replay specification

Let the complete input arrays be `R[0:T]` and `X[0:T]`. For a cutoff `c`, create deterministic altered arrays with all rows before `c` unchanged and a suffix from `c` onward changed. Test return-only, characteristic-only and joint suffix changes. Do not change `trading_costs` for this invariance claim, because those costs are known throughout the history.

### Forecast-only boundary

With a fixed candidate configuration and isolated state:

- `forecast(R,X)[:c+1]` must equal `forecast(R_alt,X_alt)[:c+1]` to floating-point precision.
- This includes row `c`, since it is the forecast used for day `c`, before day `c` is observed.
- Alter row 0 to check that forecast row 0 cannot use startup data.
- Include boundaries around first use, first model fit, first scaler/risk refresh, a rolling-window transition and each scheduled refit. Use deterministic cutoffs, not only random ones.
- Compare full-history outputs with outputs from shorter prefixes on their common range. This catches dependence on total horizon length, global fitted scaling and certain split/index errors.
- Check every forecast channel. Additional channels may contain risk estimates or configuration information; they are not exempt from causality.

### Full strategy replay boundary

`forecast` may mutate module globals, and `rebalance` may have memory. Therefore passing forecast-only comparisons is necessary but insufficient.

1. Start a fresh Python process for each replay (or equivalently prove a complete reset; process isolation is simpler).
2. Use the exact original scorer order: forecast on the full input, then rebalance serially from the same starting index and empty book.
3. Compare targets **for earning day `t` for all `t <= c`**. The target for day `c` is produced after day `c-1`, when all inputs are unchanged.
4. Compare recorded gross/net returns and costs only on scoring rows with **day index `< c`**. On day `c`, a changed return alters realized gross return and held positions; changed characteristics can alter the post-close target and its cost. Such differences are legitimate.
5. Check source/input hashes before and after each replay to catch in-place mutation. Inspect any cache or fitted object that carries information from forecast to rebalance.

Use predeclared strict absolute/relative tolerances and record maximum errors. Deterministic implementations should normally be equal at machine-level precision; a large numerical discrepancy requires explanation or failure, not relaxed thresholds selected after observing it. Do not claim finitely many suffix interventions prove the absence of every possible leak: source review remains part of the gate.

## 6. Evidence packet required at the end of each E2E run

A compact suggested layout:

```
evidence/<run_id>/
  README.md                 purpose, status, expectations, actual conclusion, known limits
  rerun.sh                  exact command, working directory and environment settings
  config.json               resolved configuration, start/end indices, score mask, seeds
  inputs.json               source archive/member hashes, generated fixture definitions
  environment.json          Python, package versions, CPU/OS, thread settings
  expected.json             predeclared invariants and tolerances
  actual.json               pass/fail per invariant and unrounded numeric results
  stdout.log
  stderr.log
  daily.csv                 day labels and indices, gross return, cost, net, exposure, market
  positions.npz             target/held arrays where necessary for verification
  comparisons.csv           invariance differences or accounting reconciliation
  source_manifest.json      exact submission/harness file hashes
```

This is a proposed artifact schema, not a claim those files already exist. Use NumPy NPZ and CSV rather than adding a third-party storage dependency. The packet may reference the immutable supplied archive by hash when redistributing hundreds of megabytes would be redundant, but it must make that dependency explicit and specify the exact extraction/slicing operation. Small synthetic inputs should be included directly.

`rerun.sh` must contain the actual command used, not a generic example. When the harness does not yet exist, its proposed command interface is only a design item. The original standalone command already exists: `python score.py example_equal_weight` or `python score.py strategy`, executed in a directory containing the input CSVs and module. Controlled single-core benchmarking should set the applicable thread-count environment variables before starting Python; record their exact values in the packet.

Begin each run by writing a `running` record; on completion atomically finalize the status. On exception, preserve the traceback and mark `executed/fail`; on interruption, mark `incomplete`. Do not discard failed experiments from the ledger.

## 7. What can be claimed now and what must wait

| Claim | Status now |
|---|---|
| The daily information and scoring conventions were inspected in the supplied code. | Source-reviewed by this reviewer. |
| The scorer drops the initial row and omits the final return row. | Established by source inspection, not yet independently executed here. |
| The uploaded CSVs are structurally valid and aligned. | Requires structural census/readback; not performed by this reviewer. |
| The environment can execute the supplied baseline. | Requires the bounded E2E run and evidence packet; not executed here. |
| A strategy is causal, solvent on tested paths, within runtime limits or beta-compliant. | Cannot yet be claimed; there is no implemented candidate. |
| A strategy will outperform in the private future. | Cannot be guaranteed by any finite local validation. |
| A final submission is portable and reproducible. | Requires the final clean-room gate. |

The useful immediate outcome is a fixed contract and a reproducible validation plan. Most serious failure risks here come from chronology, silent index alignment, stateful warm-up, drift/cost accounting and selection discipline. These should receive priority over adding test infrastructure or elaborate architecture.
