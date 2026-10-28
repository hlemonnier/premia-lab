# Independent causal-beta follow-up audit plan

Written before the independent executions below, 28 October 2026 (Europe/Paris).
Reviewed source: `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`, downloaded into
`/workspace/scratch/a83c191d516f/v2-followup-snapshot` and verified by root against
GitHub blob identities. No strategy implementation or research parameter is changed.

## Scope and expected outcomes

1. **Returns-only readback of the submitted beta-correction diagnostic.** Load
   the original `returns.csv`, retain its SHA256 and numeric array hash. Recompute
   every past/future 252-day OLS-beta pair directly, using independent centered
   matrix products rather than `_EtaTracker` or `_window_beta`. For each decision
   `t = 504,525,... < T-252`, use only grid pairs `s=252,273,...` satisfying
   `s+252 <= t` to estimate eta. Evaluate raw and corrected beta forecasts against
   the next 252 days, explicitly as an ex-post outcome. Expect the saved aggregate
   metrics to agree within `1e-12`. Save per-date paired losses and maturity bounds.
   Also report all 12 phase cohorts of the 21-day grid (dates 252 days apart
   within a cohort), without choosing one, applying a significance test, or
   claiming the cohorts independent. This is a descriptive sensitivity readback,
   not a new predictive candidate or hyperparameter search.
   Source inspection also identifies a legal endpoint omitted by the submitted
   strict bound: `t=T-252` has a complete future window when it lies on the grid.
   After the exact submitted-sample readback, report the single omitted date and
   the aggregate including it as a separately labeled boundary sensitivity.

2. **End-to-end altered-future check with the new correction active.** Generate a
   deterministic synthetic market, seed `20261028`, 820 days, 96 stocks, 13 slowly
   changing characteristics, heterogeneous constant beta, nonzero costs and a
   small characteristic return component. Run the unchanged scorer and package
   in five fresh module instances using `beta_shrinkage=True`, `beta_target=.05`,
   with all other packaged settings inherited. Cases: baseline; returns and
   characteristics replaced at and after row 650; that altered case with
   Fortran-layout X only; that altered case with both arrays Fortran; and a prefix
   of length 650. Source inspection predicts
   equality of all forecasts/targets/economic scorer columns that depend only on
   rows before 650. Require exact equality, excluding the scorer timing column,
   except for targets and economic scorer columns in the both-Fortran case,
   whose maximum absolute discrepancy must be <= `1e-12`. Forecasts remain exact.
   For the complete altered cases, forecast rows through 650 and allocation
   decisions through close 649 are protected. For the truncated case, compare
   all available forecasts, allocations and scored economic rows with the same
   baseline prefix, respecting the original scorer's endpoint behavior. Retain
   source/input/output identities, exact command, source snapshot, all actual
   outcomes and any exception. Verify that eta has become nonzero by the cutoff
   so that this workflow actually exercises the new path.

   **Pre-execution amendment after independent source review:** the engineering
   reviewer observed a `2.60e-18` gross-P&L difference in its separate old-scenario
   check when return-array layout changes. The unchanged scorer computes its own
   dot product on those input views before strategy code is called. The above
   economic tolerance for the both-Fortran case isolates this known arithmetic
   issue; adding the X-only case retains a strict check of the characteristic
   canonicalization. This amendment predates all executions of this workflow.
   Also require that the future stimulus changes a later forecast and target,
   and verify copied/reviewed sources have unchanged hashes after execution.

3. **No optional expansion.** A failure is reported and diagnosed before changing
   this workflow. Do not modify production, weaken a criterion after seeing a
   failure, or write isolated tests of the already implemented helpers. Root owns
   full actual-candidate ledger readback and the other engineer owns the existing
   default-package E2E suite; do not duplicate those runs here.

## Interpretation limits

The future-beta diagnostic predicts a noisy next-year beta estimate, not latent
true beta or tomorrow's beta. Its 144 evaluation dates overlap heavily. A pass
supports the implemented correction's past-only timing and this particular MSE
comparison; it does not establish pure stock-selection alpha or identify the
cause of a market-regression slope. The synthetic E2E is a finite controlled
causality check, not a proof covering arbitrary future inputs.
