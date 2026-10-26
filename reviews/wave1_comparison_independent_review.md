# Independent first-wave comparison review

**Reviewer:** alpha-model agent, distinct from the reporting-code author.  
**Scope:** read-only review of `tools/compare_discovery.py`, its preimplementation plan, saved report and summary/identity evidence. No new bootstrap, candidate fit, portfolio replay, numerical unit test or holdout access was performed.

## Decision

Approve the report as a correctly scoped descriptive comparison and approximate conditional uncertainty diagnostic for the fixed C01–C04 discovery ledgers. Its conclusions are appropriately qualified. It cannot select final candidates by itself, establish equivalence or causality, correct all research selection, or establish future performance.

The current reporting source exactly matches its executed snapshot, SHA-256 `02214a34cce2dc115a0671ff908fa4d09bb940294cea393ec2ee666776ff91fe`. The current plan and frozen expectation snapshot also match. The completed reporting run records **99 passing checks**, no failed checks and exit code zero.

## Ledger arithmetic and scope

The source hard-codes exactly C01, C02, C03 and C04 and their expected identifiers. It reads only saved evidence files. It neither imports strategy modules nor loads raw market arrays. The provenance checks reconcile the original artifact hashes, configuration identity, official scorer identity, identical discovery cache identities and exact score window.

Every candidate must have the same full ordered set of 1,762 scored indices253–2014; the code does not take an intersection that could discard troublesome dates. It checks the identical market column and reconciles net returns to gross minus full fees. Target diagnostics retain all1,763 earning targets253–2015, and fee/exposure comparisons exclude the free opening call consistently with the scorer.

The report calculates annualized daily Sharpe with population standard deviation, arithmetic annual means, daily-net OLS beta against the centered raw market, actual annualized fees and compounded-net drawdown. Pooled statistics are computed from the daily series, not by averaging block Sharpes. Each fixed block uses a mask on the same continuously executed ledger; there is no independent book restart at block boundaries. The calculations reconcile with saved original summaries and target diagnostics within the predeclared tolerances.

## Paired bootstrap construction

For each fixed block length21 or63, the code draws a single `(1000,1762)` date-index matrix. Consecutive circular blocks are concatenated and truncated to the exact sample length. Indexing the complete four-column return matrix with that one index matrix preserves the pairing between candidate returns in every draw. The random streams are deterministically seeded from `[20261026, block_length]`. No stock-day independence assumption or extra unplanned pair scan appears.

Each draw computes the four separate annualized Sharpe statistics and then subtracts them for the declared candidate pairs. This is the desired **difference of Sharpes**, rather than the Sharpe of a difference portfolio. The self comparison is exactly zero by construction and is explicitly checked. Both block lengths and all five declared contrasts are retained, with full draw tables and index identities saved.

The report's percentiles and positive fractions correspond to that conditional bootstrap distribution. It accurately labels the positive fraction as a bootstrap sign frequency, not a posterior probability. It discloses unproven stationarity, artificial circular joins, incomplete dependence sensitivity and the absence of a complete research-selection correction.

## Supported interpretation

The observed C02−C01 and C04−C01/C02 differences are small relative to the reported percentile ranges. Those ranges include zero; that weakens confident ranking but does not prove equivalence. The faster C03 comparison against C01 is negative at both predeclared block lengths, including each reported upper percentile endpoint. That is useful evidence against this particular faster-memory configuration on the development data, not proof that time variation is absent or that another fixed half-life is optimal.

No report statistic changes the frozen future-validation selection rule. Later C05–C10 results do not belong to this fixed report and were not read by its execution. The report correctly keeps inherited runtime measurements distinct from a newly controlled benchmark.

No blocking correction is requested.
