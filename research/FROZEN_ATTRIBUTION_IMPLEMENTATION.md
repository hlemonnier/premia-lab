# Frozen-policy attribution implementation record

27 October 2026, Europe/Paris. This record describes the implementation of
`tools/attribute_frozen_policy.py`. It does not change a candidate or add a
selectable portfolio configuration.

## Ordering and executed evidence

The root [admission](FROZEN_ATTRIBUTION_PLAN_20261027.md), independent
[E2E plan](../verification/FROZEN_ATTRIBUTION_E2E_PLAN.md), and executable
controller preceded this implementation. The controller preserved
[`frozen_attribution_red_001`](../evidence/frozen_attribution_red_001/summary.json)
with the expected missing-tool rejection.

The unchanged controller then executed
[`frozen_attribution_synthetic_001`](../evidence/frozen_attribution_synthetic_001/summary.json):
258 recorded checks across nine fresh processes, status
`EXECUTED_PASS_SCOPE_ONLY`, exit code zero. The tool's source SHA256 is
`ffb438980341e8729ff25cdbd56644fb32f1aabc81f17f87fd1aef2a16d81463`, identical to
the implementation snapshot in that evidence packet. No controller or
implementation changes were needed to obtain this synthetic pass.

The workflow includes a known Hadamard-factor decomposition, exact repetition,
altered-future and truncation comparisons, a changed-current-day boundary check,
zero/degenerate risk, and expected rejections for incorrect manifest identity,
modified bytes, malformed indices and inconsistent saved gross returns. It
checks the selected handoff's identity before and after. Synthetic success is
engineering evidence and contains no actual-market alpha result.

At the time this record was written, independent source review and root release
were still required before processing the canonical market packet. That future
run, if released, must have its own evidence record; it is not implied by the
synthetic status above.

## Identity and isolation

The command requires the packet's artifact-manifest hash. Every consumed file's
size and hash is checked before numeric input parsing. C09's configuration and
the four original helper source hashes are pinned. Real mode additionally pins
the original canonical inventory and metadata and requires `--allow-canonical`;
synthetic mode rejects that flag and requires a synthetic input-kind tag.

Only the original return matrix, saved targets and daily ledger are consumed as
numeric inputs. Characteristics, forecasts, cost arrays and raw CSVs are not
needed. The full original fees come directly from the authenticated ledger.
The original packet remains read-only and the tool writes to a fresh external
directory. The four helpers are copied into a private package in that directory.
Both forecast and rebalance entrypoints are replaced in process with explicit
failure functions; the recorded execution count must remain zero.

The output includes original metadata, consumed-file identities, helper and tool
snapshots, both prospective plans, environment, exact commands, logs, daily
results, checks, summaries and an artifact manifest. A rejected workflow retains
its failed status, error and available evidence.

## Information clock and arithmetic

For return row `t`, opening weights are exactly `targets[t-253]`. Risk estimation
uses only `returns[:t]`. The residual correlation loadings refresh at rows 253,
274, 295 and so on, following the original C04 epoch rule. Current prior-estimated
marginal variances rescale those loadings each day.

`factor_history_stop_exclusive` dates the cached **correlation** loadings.
`factor_variance_history_stop_exclusive` and `risk_history_stop_exclusive` both
equal `t`. Consequently, a nonzero `factor_age_days` does not mean that the final
loading span is unchanged: the daily variance rescaling can alter it between
correlation refreshes. The thin SVD retains singular values strictly greater
than `eps(float64)*max(n_stocks,n_loading_columns)*largest_singular_value`.
An empty or all-zero span is handled without division by zero.

Opening target times realized returns must reconcile to saved gross before the
component calculation. Estimated market payoff, the residual-factor projection
and the remainder then reconcile independently to that same gross. Original
full costs are subtracted once and reconcile to original net. The fixed
absolute/relative tolerances are `1e-12` and `1e-10`. They were specified before
implementation and are not command-line controls.

The three stage masks are unchanged: discovery `[253,2015)`, validation
`[2016,3023)`, and audit `[3024,3779)`. The complete daily table retains boundary
rows excluded from those stage summaries. Annual arithmetic means and
population volatilities are reported; covariance contributions use matching
population covariance and variance. Empty-stage metrics and zero-variance
ratios are null. No component Sharpe, significance claim or percentage share of
mean return is produced.

## Interpretation limits

This is ex post attribution under one prespecified prior-estimated span. A
component can contribute negatively or more than one to gross covariance; these
are not independent risk shares. Near-zero estimated market attribution is
partly constructional because C09 hedges the same prior beta estimate. The
original realized net beta remains the empirical market-exposure check.

The remainder can contain omitted common factors, nonlinear exposures and
estimation error. It is not identified as economic alpha. This analysis cannot
promote a new policy, remove selection optimism or create a fresh confirmation
period from data already inspected.
