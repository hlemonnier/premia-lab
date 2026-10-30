# Two forecast prototypes: prospective execution plan

28 October 2026, Europe/Paris. Authority: the user asks to improve the official
score; root admitted exactly F1 and F2 for research prototypes and requires source
review before actual-data execution. Production package/source/scorer are preserved.
Source is `ce3fe4e76271709422165d6f24e2fbecd9d0fe07` in `v2-followup-snapshot`.

## Hypotheses and frozen candidates

F1 averages causal daily 27-column ridge slopes, using ridge .1 and half-life
1008, rather than solving on pooled EW normal equations. F2 fits the unchanged
pooled learner at half-lives 252 and 1008, mixes their first 13 linear
coefficients equally, and retains the slow 13 quadratic and beta coefficients.
The full formulas and motivation are in
`research/v2/SCORE_FORECAST_RESEARCH_20261028.md`.

Both preserve V2 basis/label timing, 126-pair warm-up, factor risk scale .3,
risk aversion 200, cost horizon 20, weight cap .05, gross cap 5, raw beta and
zero estimated-beta target. No risk or execution changes. Baseline V2 uses
the unmodified current engine. There is no combined F1/F2 or parameter grid.

The primary metric is full-sample net Sharpe from the unchanged scorer,
earning indices 253..3778, compared with V2 (about 1.242503). All history is
development history. Positive net-Sharpe differences are nomination evidence;
negative differences reject replacement. Beta must meet the existing absolute
.2 requirement; finite accounting and runtime/causality are eligibility gates.
No significance threshold or every-period-win condition is added.

## Verification fixed before prototype implementation

The E2E controller is written before `prototype.py`. Its first invocation must
record a missing-prototype result before economics. No later isolated tests are
added. Subsequent workflows use the original scorer and the exact unchanged V2
allocator. Source/scorer/input hashes, commands, environment, predictions,
positions, economic rows, failures and numerical deviations are retained.

Synthetic workflows (seed 20261028, T=420, N=64, 13 characteristics, fees .0005):

1. A fixed cross-sectional panel and zero-market, nonzero stock-return paths
   make the full design Gram constant (beta fallback is one). F1 forecasts must
   agree with V2 to 1e-12 and scorer economics/targets to 1e-9. The fixture must
   have nonzero forecasts; an all-cash identity is not an adequate check.
2. A moving-panel fixture with a known changing linear component and stable
   quadratic component exercises both algorithms. For each candidate run the
   original scorer, repeat in the same process/session, alter all input rows
   from 320 onward, and truncate at 360. Altered futures include C/Fortran layout.
   Forecast rows <=320 are protected; decision indices <320 and economic indices
   <320 are protected. Prefix predictions and decisions must match their full
   counterparts. Protected forecasts/positions/economics tolerance is 1e-12;
   timing columns are excluded. No future scoring outcome chooses a parameter.
3. On exact-zero returns, both produce exactly zero forecasts, targets and
   economics; Sharpe/beta are recorded as undefined if relevant.

All fixtures require finite arrays, source identity, valid earning/decision
counts, scorer-independent return/fee reconciliation and certified solves. A
failure remains recorded; an implementation correction requires source-review
and a fresh named run, not replacement of the failed evidence.

## Actual-data execution after root review

Load the original CSVs as C-contiguous float64 arrays. Record their byte hashes.
Run baseline V2, F1 and F2 sequentially through the unchanged scorer, with state
reset at every forecast invocation. Record all daily economics and decisions,
forecast hash/array, scorer/scaffold/prototype identities, certificate summaries,
gross scaling, cap/estimated-beta checks and one-core BLAS environment.

Compare baseline's daily [day,net,gross,fee,market] against the pinned committed
V2 ledger to 1e-8. Verify source copies remain unchanged. Report full and original
stage statistics, observed forecast/rebalance times, beta, cost and gross. Actual
full-path causality for both candidates uses a future alteration from row1500
and a prefix of 1500 rows; forecast rows <=1500 and earlier decisions/economics
are protected. The original full scorer is run on each actual modified path.

The original scorer's first free trade, drift and final endpoint are unchanged.
The final characteristic/return rows must not enter earlier forecasts. Gross
return and cost independently reconcile using saved targets/held positions,
including the final scored close. Complete replay beats inferred score from
rescaled returns. Any century runtime claim remains unverified until executed;
observed runtime and linear extrapolation are labeled as such.

No schedule is imposed. The experiment ends after the two fixed candidates and
their required checks; results determine the next research decision.
