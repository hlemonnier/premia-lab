# Alpha diagnostics 001 — expectations before implementation and execution

**Status when written:** planned; no predictive diagnostic in this run has been executed.  
**Owner:** research-design / alpha-diagnostics agent.  
**Authority:** `RESEARCH_PROTOCOL.json`, the supplied README and original scorer.  
**Scope:** descriptive alpha discovery only, using cached actual rows `[0,2016)`; no portfolio backtest, candidate net-Sharpe score, validation data, audit data or supplied figures.

## Questions and competing explanations

| ID | Hypothesis to investigate | Competing explanation / reason to reject a strong claim |
|---|---|---|
| AD01 | Some lagged characteristics predict the relative cross-section of future stock returns. | Association is contemporaneous, a market-beta effect, unstable across time or driven by extreme observations. |
| AD02 | A stable nonlinear response exists even where linear association is small. | A visually attractive response is a noisy bucket pattern, unstable sign/shape, or the result of selecting the best bucket retrospectively. |
| AD03 | Signals persist long enough for a cost-aware policy to amortize trading costs. | Strong daily predictive association accompanies rapidly changing ranks/membership; gross association alone establishes no tradable edge. |
| AD04 | The thirteen characteristics contain complementary information. | Several are redundant transformations of the same state, or stock attributes/common time variation rather than distinct expected-return signals. |
| AD05 | Relations survive changes across the discovery history. | Pooling hides sign changes, nonlinear regime changes or a relationship restricted to a short interval. |

No characteristic has an assigned economic meaning. No result is assumed in advance. These diagnostics estimate relationships using discovery data; they are not an out-of-sample forecast evaluation and cannot establish achievable trading Sharpe.

## Input and chronology contract

Read only `cache/discovery/returns.npy`, `characteristics.npy`, `costs.npy` and `metadata.json`; expected shapes are `(2016,1000)`, `(2016,1000,13)`, `(1000,)`. The runner must reject a longer history rather than silently accept data outside its scope. Hash every input and record exact metadata. Do not open the original full CSVs, source figures or later cache prefixes.

Characteristics, in provided order: Woe, Malice, Dread, Frolic, Up, Down, Charm, Strange, Top, Bottom, Snap, Crackle, Pop. All row indices below are zero-based; CSV day label equals index plus one.

For feature date `s`, use `X[s]` to describe the label beginning at `t=s+1`. Horizons are fixed at `h in {1,5,20}`. The label is the arithmetic average of returns from `t` through `t+h-1`, expressed in daily-return units; it is not a compounded tradable holding return. No label may extend beyond actual row 2015. A live model at day `t` would train only on matured pairs, with latest one-day pair `X[t-2] -> R[t-1]`; the retrospective diagnostic must not be misrepresented as such a live fitted forecast.

Market-controlled labels use a stock beta estimated from the **252 observed rows through feature date `s`**, with intercept/centering against the equal-weight market. The label subtracts this past beta times the forward market-average return. Require positive trailing market variance; otherwise mark that diagnostic unavailable, without inventing a beta. This is a fixed diagnostic risk control, not a claim of exact latent-factor removal or a proposed portfolio hedge.

Predictive origins begin at `s=252`, matching the first permissible position-setting date of the provided evaluator, and allowing a full trailing beta window. Four fixed discovery blocks use **first label day** in `[0,504)`, `[504,1008)`, `[1008,1512)`, `[1512,2016)`. Require every horizon label to finish inside its block. Aggregate diagnostics pool only those same block-contained observations, avoiding hidden cross-block target overlap.

Expected origins per block and horizon:

| Horizon | Block 1 | Block 2 | Block 3 | Block 4 | Pooled |
|---:|---:|---:|---:|---:|---:|
| 1 | 251 | 504 | 504 | 504 | 1763 |
| 5 | 247 | 500 | 500 | 500 | 1747 |
| 20 | 232 | 485 | 485 | 485 | 1687 |

These are **diagnostic** label counts, not the official portfolio scoring mask. The complete final discovery return can be used as an already observed diagnostic label; the scorer's terminal omission remains unchanged in subsequent candidate backtests.

## Predeclared outputs and exposures

### Characteristic behavior and redundancy

For every characteristic and the pooled/four-block history, report distribution quantiles, daily cross-sectional location/dispersion, fraction of constant cross-sections, variability of common time means versus persistent stock means, and cross-sectional Pearson/Spearman persistence at lags 1, 5 and 20. Report fixed top/bottom decile membership retention as a signal-churn diagnostic, not turnover or trading cost. Correlation with the known cost vector is descriptive only.

Report average daily cross-sectional Pearson and rank-correlation matrices between all thirteen characteristics. Missing/undefined correlations remain explicitly unavailable. This is the only initial pairwise feature scan; no automatic interaction library or best-subset search is authorized by this run.

### Predictive relationships

For each of 13 characteristics, three horizons and both raw and market-controlled labels, record daily cross-sectional Pearson IC, Spearman IC, standardized linear slope, ten rank-quantile mean label returns, fixed top-minus-bottom spread and fixed curvature contrast `(Q1+Q10-Q5-Q6)/2`. Quantile membership uses average ranks; ties are never broken by future returns or arbitrary stock ordering, and empty buckets are reported.

No winning sign or bucket is chosen to create a strategy in this run. The predefined linear and curvature contrasts are inspected in both directions. Their signs are reported as observed. Summary statistics are based on **daily** values and the four chronological blocks; no stock-day iid standard error or nominal massive-sample significance claim is allowed. Include fixed 63-day temporal-block summaries as uncertainty/stability diagnostics, without presenting them as corrections for model selection.

Daily market-beta association is reported to explain raw-versus-controlled changes. A small contemporaneous market subtraction alone cannot remove heterogeneous stock beta; the control therefore uses the explicitly past-estimated stock betas above.

### Interpretation rules

Potentially useful evidence consists of a stable sign/shape, persistence and complementarity that survive the stated market control. Strong raw relationships disappearing under control are recorded as exposure findings. Sign reversals and inconsistent quantile shapes are recorded directly. Tiny or unstable effects remain hypotheses, regardless of apparent pooled precision. Stable curvature can motivate one later nonlinear challenger, not an unrestricted search.

## Expected workflow checks and failure modes

Before analysis, verify exact allowed paths, shape, feature order if supplied in metadata, finite inputs, nonnegative costs, and immutable input hashes. Reject any attempt to load rows beyond 2015. Use one-core numerical thread settings and record versions/process settings.

During computation, verify every origin's latest input date is earlier than its first label date, every forward label is complete inside its assigned block, and daily/summary tables cover the exact planned characteristic/horizon/target combinations. Undefined correlations are allowed only with recorded zero-variance or empty-bin explanations; silent dropping or replacing them with zero is a failure. No candidate code, weights, turnover-adjusted returns or net-Sharpe backtest is created.

At completion, verify expected origin counts and output-table row counts, recompute hashes to detect input changes, and save a manifest for produced artifacts. These are checks of the complete diagnostic workflow, not unit tests written after covered strategy implementation. Any exception preserves traceback and status; a failed run remains evidence.

## Evidence and logging

Write `evidence/alpha_diagnostics_001/` with a running/completed/failed state, copied plan and configuration, code/input/protocol hashes, exact executed command, rerun instructions, environment, stdout/stderr, daily diagnostics, summary tables, quantile shapes, characteristic/redundancy tables, explicit checks and findings limits. Source code is frozen into the evidence directory so reruns do not depend on a later edited live script.

Each planned feature/horizon/target/contrast/persistence/redundancy inspection is a **diagnostic exposure**. Record them in a run-specific exposure ledger. This run uses zero of the twelve complete pipeline slots because no portfolio is scored. A later selectable strategy derived from these findings must be admitted and counted by the lead under the frozen protocol.

## Allowed next decision

After the completed evidence is reviewed, summarize the strongest supported relationships, contrary evidence and concrete next experiments in `research/ALPHA_FINDINGS.md`. Any extra interaction, horizon, subgroup or transformation scan requires a written extension **before** observing its results. No validation or audit access is authorized by a promising discovery result.
