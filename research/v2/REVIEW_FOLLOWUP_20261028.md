# V2 review follow-up

28 October 2026. Responds to `reviews/V2_INDEPENDENT_REVIEW_20261028.md` and executes
`research/v2/REVIEWER_NEXT_EXPERIMENTS_20261028.md`. All rows were already exposed;
results are development evidence.

## Decisions

| Reviewer item | Disposition | Evidence |
|---|---|---|
| Restart/stale risk state | Fixed: `forecast()` starts a session and resets risk state and warm start | `verification/v2_package_checks*` — failed before (target diff 1.2 pp), passes after (bitwise) |
| Characteristic layout | Fixed: `basis()` canonicalizes each panel | Fortran-layout X now bitwise identical |
| Allocator certificate | Added: caps, hedge, finiteness, duality gap; one resume-from-polished-point recovery | 3,527/3,527 real calls certified, 0 recoveries, max gap 1.3e-17 |
| Economic agreement | Real ledger identical to pre-fix package (max diff 0.0) | `v2_package_checks_after_fix.log` |
| Missing comparison entries | Regenerated: 25 variants; block starts `n-L+1`; written before printing (the old file was lost when a closed pipe killed the script) | `results/comparison.json` |
| Drift test sample mismatch | Fixed: observed and null use the same 3,465 rows. Overall p = 0.21 (was 0.29); linear terms p = 0.03 unadjusted for multiplicity. Exchangeability caveat stands; drift unresolved | `results/drift_test_stdout.txt` |
| Daily ledgers absent | Committed (`results/ledgers/net_*.npy`: day, net, gross, cost, market) | — |
| Tests-before-code evidence for the allocator | Not recoverable: the first, failing run was not saved. Stated, not claimed | — |
| Note said the applicant chose to replace C09 | Corrected: candidate under review | `handoff_v2/strategy.py` |

## Beta mechanism (`beta_diagnostics.py`, `results/beta_diagnostics.json`)

| Test | Result |
|---|---|
| Beta factor return (jointly with the 26 columns) on market return | Slope −0.048 (NW t −19.7), intercept −0.10 bp/day (t −0.77), R² 0.24 |
| Same, univariate | Slope −0.059 (t −16.2), intercept −0.42 bp/day (t −2.0) |
| Regression of realized next-year beta on estimated beta | Slope 0.82 (η ≈ 0.175) |
| Share of the beta column outside the 26-column span | 93% on average (min 87%) |
| Synthetic: constant true betas, zero alpha, positive market mean | Slope −0.046 (t −29), intercept ≈ 0: same signature |
| Market component of realized returns (ex post) | V2: beta 0.047 (t 9.5), 0.67 of 4.76 %/yr; market-removed Sharpe 1.08. C09: 0.13 of 5.18 %/yr; 0.86 |

Conclusion: conditional on the characteristics, the low-beta "premium" is explained by
market exposure arising from beta estimation error (H-beta-error), not by a separate
intercept (H-beta-return). V2's advantage over C09 survives removing realized market
exposure, but part of it is market premium.

The structural reason the 26-column risk model misses it: all risk columns are
cross-sectionally centered and residual returns are demeaned, so a beta-hedged
net-long book's exposure to beta error is invisible to it.

## R27 (frozen plan `R27_PLAN.md`)

- **Stage 1, risk gate on frozen V2 holdings: passed.** Mean loss difference R27 − R26 =
  −0.0368. 95% block ranges: 21-day [−0.080, −0.002], 63-day [−0.105, +0.011], 126-day
  [−0.126, +0.020]. By stage: discovery +0.004, validation −0.180, audit +0.060.
  Calibration (realized/predicted, scale 1): R26 1.07 / 0.96 / 1.67 / 0.82; R27 0.92 /
  0.91 / 1.12 / 0.66 (full / discovery / validation / audit). R26 matches the review's numbers.
- **Stage 2, full-fee run: failed the retention rule.** Net Sharpe 1.167 versus 1.243
  (difference −0.075; 95% ranges [−0.18, +0.03] 21-day, [−0.19, +0.03] 63-day,
  [−0.20, +0.03] 126-day; daily correlation 0.98). By stage 1.073 / 1.385 / 1.359.
  Realized beta 0.026 (V2 0.047), mean net investment 24% (V2 40%), cost 0.16%/yr,
  rebalance 4.2 ms, all certificates ok.
- **Disposition: R27 rejected.** It does what the hypothesis says: it prices the hidden
  exposure, so the book holds less of it and earns less market premium. No rescue by
  tuning.

## Matched-marginal control

Same forecast and costs; risk `diag(d + 0.3 diag(D F D'))`, which keeps V2's marginal
variances and drops correlations: net Sharpe **0.938** (1.098 → 0.690 discovery, 1.657 →
0.775 validation, 1.148 → 1.859 audit), difference −0.305 versus V2 (95% ranges
[−0.71, +0.08] 21-day, [−0.76, +0.06] 63-day, [−0.81, +0.10] 126-day). Caveat: without
correlations the book is far larger (gross 4.7, gross cap active, vol 32%, beta 0.098),
so sizing is not matched. Its period profile resembles C09's. Within that limit, V2's gain
over a C09-like book comes from the correlation structure, not from better marginal variances.

## Open, in order

1. Decide deliberately how much market exposure to hold: an explicit, measured beta
   budget instead of beta error carried implicitly. This needs its own hypothesis and plan.
2. The variance-preserving correlation-shrinkage family
   `diag(d + (1-λ) diag(A)) + λA`, with λ from past risk loss, not exposed Sharpe.
3. Premium dynamics (stable mean plus strongly shrunk deviation), only if forecast errors
   show a learnable component.
