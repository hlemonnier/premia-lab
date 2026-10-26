# GLS wrapper causality: schedules and expectations before its gate

This adds concrete schedules for C05/C06 to the existing causality plan. It does not claim a numerical pass. The exact candidate/configuration and chosen scenario manifest must be frozen before the eventual gate. Only discovery/synthetic inputs are allowed; no holdout is needed for debugging.

## Information boundaries

For forecast row t and label day j=t−1, beta, marginal variances and factor risk weights use exactly `R[:j]`. Learner factor fits occur at prior-history counts `20+21k`, so the first two can affect forecast rows21 and42. The first active forecast remains127. The first factor refresh after active forecasts is label146, affecting row147. A later factor refresh at label272, affecting row273, uses a truncated trailing252 window and therefore covers factor fitting after rolling eviction. Daily marginal risk itself first evicts at the earlier253-row prefix, affecting label weighting at forecast254.

C06 also adds the existing portfolio factor cache: first target253 fits from253 already observed rows; target274 refreshes; target275 reuses that refreshed model while updating current marginal variances and market beta. Repeated/decreasing rebalance history resets this cache. Forecast may not fill it.

## Concrete comparison expectations

All existing protected-output rules remain unchanged: an alteration beginning at row c must preserve forecast rows through c, targets for earning days at most c, and scorer economic rows strictly before c. The source review must separately verify local learner state and no forecast-to-portfolio contamination.

Candidate-specific boundary choices should cover first learner fit/update (rows21/42), active forecast127, active learner refresh147, rolling risk254 and factor refresh273, plus C06 portfolio refresh274/nonrefresh275. Merge the needed paths with the existing initialization/later discovery/prefix/append profile before execution. Startup cutoffs21/42 have zero forecast outputs and empty target/ledger ranges under the warmup; record that limited observable coverage rather than claiming they test active trading. Active/later cutoffs provide complementary numerical coverage. Do not expand every repeated refresh mechanically when the same code path is already covered.

For C05 and C06 economic runs, equality of already-generated forecast arrays is a separate controlled-comparison expectation. Comparing these saved arrays does not rerun or fit another candidate. The completed arrays have equal identities, recorded in the independent review.

Use the exact explicit selected config, unchanged input/scorer identity checks, fresh processes, deterministic return/characteristic/joint perturbations, and fixed float64 tolerances from `CAUSALITY_PLAN.md`. A timeout may be enlarged before execution to accommodate a longer scenario; that never relaxes a numerical tolerance or the candidate's actual runtime eligibility. Preserve any incomplete/failed execution accurately. C02's pass does not become a C05 or C06 pass through shared helper code.
