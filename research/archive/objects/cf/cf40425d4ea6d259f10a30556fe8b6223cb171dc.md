# Independent follow-up readback plan — before new calculations

28 October 2026, Europe/Paris. Reviewed source is frozen at
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07` on `v2-factor-risk`.
This is an audit of completed research, not a new candidate search or a strategy
implementation. Every historical period is already exposed.

## Scope and inputs

Use the exact Git-blob-verified files in `v2-followup-snapshot`, the original
CSV archive already verified in the first independent review, and that review's
literal-package C09/V2 daily ledgers. Save this plan, code, commands, input/source
identities, outputs and failures. Do not edit the supplied scorer or strategy.
The seven new commits are compared with review commit `4621880`; all seventy
changed/added files are retrieved and checked, including binary ledgers.

## 1. Ledger and statistical readback

Read all committed `net_*.npy` arrays as five rows: zero-based earning index,
net return, gross return, cost, equally weighted market return. Require finite
values, common indices 253..3778, net=gross-cost within 1e-12 and market values
matching the original return CSV's row mean within 1e-12. Report exact maximum
differences. Compare C09 and packaged-scale V2 with the earlier independent
literal-package replay; distinguish floating-point/research-loader differences
from bitwise reproduction. Economic differences <=1e-8 are the specified
portability tolerance; disclose values, not only pass/fail.

Recompute the six comparison policies: C09, V2, R27, matched diagonal, B0 and B05.
Use the original stage masks [253,2015), [2016,3023), [3024,3779), keeping the
two excluded stage-boundary observations in the full sample. Report annual
arithmetic net return, annual standard deviation (ddof=0), net Sharpe, cost,
and realized gross and net beta. Compare available JSON summaries.

For each policy fit the same descriptive intercept-plus-market regression as
Claude, with Newey-West/Bartlett covariance using 10 lags. Report coefficients,
standard errors, 95% normal/HAC intervals and the ex-post market-removed Sharpe.
The latter is an appraisal statistic, not a costed causal strategy or a proof
of stock-specific alpha. Net-vs-gross beta difference isolates fee covariance.

The key new comparison is B05 minus B0: they share the corrected forecast and
risk state and differ in the target. Regress the daily net-return difference on
market, report beta change, intercept, market-explained mean, R-squared, residual
volatility and stage results. This is incremental policy P&L, not a standalone
tradable overlay with independently charged costs. Also report V2 comparisons
as descriptive decompositions; they change several components simultaneously.

Recompute paired moving-block 95% percentile intervals for net-Sharpe differences
against V2, with 2,000 shared-index draws, seed 20261027 and lengths 21/63/126.
Use every legal block start (n-L+1). These preserve shared-day dependence under
their assumptions, but are neither model-selection corrections nor equivalence
tests. No candidate is promoted because a new statistic happens to favor it.

## 2. Beta-factor mechanism readback

Independently reconstruct the published daily 26-column basis, causal raw betas,
and clipped/centered beta column from the original float64 CSVs. Recompute the
univariate and joint beta-factor returns using the existing diagnostic's exact
253..3779 sample (3,527 observations, one more than scored earning rows).
Reproduce the existing lag-10 HAC regression and supply its confidence intervals;
fixed lag-21/63/126 sensitivity is secondary. Non-significance of an intercept
does not establish zero expected payoff or identify a unique data generator.

Measure squared-norm share of the beta column outside the 26-column span, mean
estimated beta minus one, and residual cross-sectional means. These quantities
test the precise claim that cross-sectional demeaning itself deletes beta-error
risk. Save daily diagnostic series for subsequent review. Where useful, derive
raw-factor vs residual-factor identities using the same available-date design;
these are observational regressions, never a new forecast or policy.

## 3. Independent division of work

The engineering reviewer reruns the original complete synthetic scorer workflow
under a prospective plan, audits the nonzero-target dual/certificate and checks
source/log history. The causal-beta reviewer reproduces the annual beta-MSE
diagnostic and audits the corrected forecast-to-rebalance future/prefix path.
The quantitative reviewer independently challenges economic identification and
specifies the next discriminating experiment. Root owns this saved-ledger and
factor readback. Avoid duplicating full candidate executions without a concrete
remaining risk. Any further execution must have its own prior specification.

## Expected outcomes and interpretation

Expect the headline performance and frozen-rule rejection decisions to reproduce;
failure requires an explicit diagnosis before accepting those claims. Expect the
B05-B0 beta response to be near the requested 0.05 shift, while checking the
absolute target error separately. Expect centered beta-error directions to
survive demeaning; representation depends on the factor span and residual-risk
model. These are expectations to challenge, not assertions of results. Preserve
unfavorable or failed findings and do not rescue rejected candidates by tuning.
