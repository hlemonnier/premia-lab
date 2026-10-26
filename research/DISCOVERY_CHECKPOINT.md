# Discovery research checkpoint — ten completed configurations

## Conclusion

The engineering path is functioning, market exposure is controlled on the executed discovery histories, and the research has rejected several plausible but weak changes. **We have not yet established a strong trading edge.** The leading development result is C06 at net Sharpe 0.762944; validation and the internal audit remain closed. More numerical machinery has not automatically improved the score.

This checkpoint precedes C11's market outcome. Its purpose is to preserve what the first ten complete comparisons actually support, including contrary evidence.

## Complete comparison

All candidates used the same actual input rows `[0,2016)`, continuous positions from the official start 252, and the unchanged scorer's 1,762 observations at indices 253–2014. Costs are charged in full on drifted holdings by the original evaluator. The first opening trade is free; the official final-row omission is preserved. Annual means and costs are arithmetic; volatility and Sharpe use population daily standard deviation.

| ID | Controlled design | Net Sharpe | Gross Sharpe | Net mean/year | Volatility/year | Full fees/year | Net market beta | Candidate mean ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| C01 | Linear ridge, half-life 252, diagonal risk |0.622345|0.716196|4.3227%|6.9459%|0.6519%|+0.017223|9.68|
| C02 | Add all 13 squared terms |0.637567|0.750111|4.4038%|6.9072%|0.7773%|+0.021230|14.69|
| C03 | C02, half-life 63 |0.106491|0.351449|0.7517%|7.0590%|1.7267%|+0.028195|11.17|
| C04 | C02 forecasts, rank 10 factor portfolio |0.654213|0.881974|2.3581%|3.6045%|0.8218%|+0.007565|24.97|
| C05 | C02 portfolio, causal GLS learning |0.602469|0.707081|3.3847%|5.6180%|0.5880%|+0.016346|11.60|
| C06 | C05 forecasts, C04 factor portfolio |0.762944|0.963122|2.5907%|3.3956%|0.6810%|+0.006330|27.85|
| C07 | C02 forecasts, exact joint gross constraint |0.679825|0.746039|5.1172%|7.5272%|0.4979%|+0.023539|25.75|
| C08 | C02, risk aversion 5000 |0.626206|0.691187|1.1916%|1.9029%|0.1236%|+0.006259|7.81|
| C09 | C02, half-life 1008 |0.700155|0.786047|4.7901%|6.8416%|0.5880%|+0.014404|9.39|
| C10 | C06, learner/portfolio factor ranks 50 |0.739890|0.959189|1.7307%|2.3391%|0.5144%|−0.000089|27.88|

Exact records, source identities, ledgers and reproduction commands are in `evidence/discovery_C01_001` through `discovery_C10_001`. All ten completed with exit 0 and 20 recorded workflow checks. Every declared path feasibility flag passed; this is not a universal future guarantee.

The timing column measures candidate calls on one pinned CPU with one numerical thread, including actual periodic updates. Independent runs used different pinned CPUs while sharing the host. Elapsed-time outliers are retained, including a 10.85-second C07 call with ordinary iteration count; its precise host cause is unverified. The contract concerns average time. Forecast century numbers elsewhere are extrapolations, not executed century tests.

## Findings and their limits

**Fast adaptation was a poor response to the apparent changing signals.** C03 worsened gross as well as net Sharpe, more than doubled C02's fees, and traded more. The first-wave paired block bootstrap gives a C03-minus-C01 Sharpe range below zero under both predeclared block lengths. This is evidence against this 63-day design on development history. It does not prove coefficients never change.

**The original curvature contrast did not translate into a material additive gain.** C02 improved net Sharpe over C01 by only 0.0152. Its paired 95% bootstrap ranges span−0.169 to+0.204 at block length 21 and−0.217 to+0.224 at length 63. We cannot treat that small observed gain as established superiority. C04's 0.0166 net increment over C02 is similarly uncertain. These conditional resampling ranges assume the development sample is informative and do not correct the whole research search or predict hidden-future performance.

**GLS and factor risk have an interaction worth retaining, but neither is a demonstrated solution.** GLS alone, C05, was worse than C02. C06 used byte-identical C05 forecasts with factor risk and produced the best current score. It reduced common exposure and risk while preserving more return per unit risk in this comparison. Increasing both covariance ranks to 50 reduced return, risk and costs but did not improve the frozen primary metric. The joint rank change cannot separate learning effects from portfolio effects.

**The gross-cap approximation was real, and two fixes have now been measured.** Baseline postsolve scaling occurred on roughly 63–97% of first-wave calls. C07 integrates beta, stock boxes, transaction costs and the gross budget into one convex solution; it has no proportional rescaling and lowers C02 fees from 0.7773% to 0.4979% per year. Its forecasts are byte-identical to C02. The net-Sharpe improvement is modest. C08 uses a much simpler size change and eliminates scaling entirely, but leaves Sharpe near C02. Removing an implementation approximation does not by itself create alpha.

**Longer memory helped the pooled number while weakening the last block.** C09's four block Sharpes are 1.189,0.817,0.644 and 0.181, versus C02's 1.142,0.611,0.532 and 0.393. Its lower turnover and fees contribute to the gain. It does not dominate across time and does not establish stable true coefficients.

## What is implemented and verified

The source repository contains causal exponentially weighted characteristic learners, deterministic market-beta and residual-risk estimation, stock-specific drift-aware trading costs, a diagonal optimizer, a factor optimizer, a precision-weighted learner and an exact gross-budget optimizer. Their custom numerical components were specified and checked before their implementations; missing-module red runs and subsequent independent numerical references are preserved.

C01 and C02 each passed 28 fresh-process causal smoke scenarios on 600 allowed discovery rows. Protected forecasts, targets and economic ledgers matched exactly under the declared alterations, prefixes and append. These passes do not establish the unexecuted configuration-specific gates for later candidates. The original accounting workflow, source/cache integrity, actual full-fee reconciliation and all actual discovery paths have separate records.

The implementation and empirical research are AI work under the user's direction. No personal applicant discovery is invented. Source changes, rejected configurations, interrupted runs and corrective reviews remain in the record.

## Next question and protected data

C11 is prospectively admitted to test the additive conditional-mean assumption: all 78 centered pairwise products join C02's original 26 terms, with stronger interaction shrinkage and no selected pairs. Correlation can make a product effect look like marginal curvature; the illustrative Gaussian identity motivates a test, not a claim about this simulator. The complete 104-coefficient specification and synthetic whole-strategy verification precede its actual-market score.

Eleven of twelve discovery slots are reserved; only ten are scored at this checkpoint. Slot 12 is unassigned. Validation rows `[2016,3024)` and audit rows `[3024,3780)` remain economically uninspected. The next release decisions require exact finalist/configuration causality and runtime evidence, a frozen shortlist, the prescribed pooled validation comparison, and only then the single-candidate audit. This checkpoint is not an employer-ready final package.
