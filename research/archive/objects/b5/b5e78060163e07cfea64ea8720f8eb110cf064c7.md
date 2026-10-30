# Explicit market exposure — plan and frozen decision rules (written before execution)

28 October 2026. Follows `REVIEW_FOLLOWUP_20261028.md`. All rows are already exposed;
this is development research on the full sample, which the brief allows.

## Problem

V2 hedges raw trailing OLS betas `bhat`. Realized next-year betas regress toward the
cross-sectional mean (slope 0.82, η ≈ 0.18, `results/beta_diagnostics.json`). A book with
`bhat'w = 0` and net investment `1'w > 0` therefore carries true market exposure of about
`η·(1'w)` that neither the hedge nor the risk model sees. V2's realized beta is 0.047 and
about 0.7 of its 4.8 points of annual return is market exposure.

## One principle: corrected betas everywhere, then an explicit exposure

**Causal shrinkage.** For a decision after close t, η_t is estimated only from completed
pairs: on dates s = 252, 273, … (every 21 rows) with s + 252 ≤ t, regress the
cross-section of realized betas over rows [s, s+252) on `bhat_s` (rows [s−252, s)), and
set η_t = 1 − mean slope over all completed dates (expanding). Before the first pair
completes (t < 504), η_t = 0, i.e. no correction (a fixed default, not sized on data).
Corrected beta: `b_t = (1 − η_t)·bhat_t + η_t·mean(bhat_t)`.

**Used consistently in:** (1) forecast labels `e = r − b·m`; (2) risk-state residuals;
(3) the hedge. The forecast's beta column is unchanged by construction (standardizing an
affine transform of `bhat` gives the same column). Nothing else changes: the 27-column
forecast, 26-column risk, φ 0.3, γ 200, caps, costs and half-lives are inherited.

**Explicit exposure.** The hedge constraint becomes `b'w = β*`.

## Candidates (exactly two; no grid)

- **B0:** corrected betas, β* = 0 (a truly hedged book).
- **B05:** corrected betas, β* = 0.05. This matches V2's implicit level, so the
  comparison isolates explicit-and-measured versus implicit. It is a judgment value,
  not optimized; the in-sample market premium is not used to choose it.

## Pre-execution diagnostic (risk measurement, not a gate on Sharpe)

On the same decision dates, compare how well `bhat` and the causal `b` predict realized
next-252-day betas: cross-sectional mean squared error, averaged over dates with a
completed future window. Expected: `b` has lower error. If not, the correction is not
doing what it claims, and that is reported before the candidates are interpreted.

## Frozen decision rules

- **Measurement check (both candidates):** realized full-run net-return beta within ±0.02
  of β*. Failing this means the exposure is still not under control.
- **B0 is retained as the neutral core** if it passes the measurement check and its net
  Sharpe ≥ 1.083, V2's ex-post market-removed Sharpe (a bar that favors V2, since that
  removal uses a full-sample beta).
- **B05 replaces V2** if it passes the measurement check and its net Sharpe ≥ 1.243
  (packaged V2). Otherwise V2 stays, with the beta mechanism documented.
- Report every stage, paired 21/63/126-day block ranges versus V2, net investment, cost,
  runtime and allocator certificates, whatever the outcome. No rescue by changing β*,
  η rules or any other setting after seeing the result.
