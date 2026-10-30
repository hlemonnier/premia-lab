# Discovery research checkpoint — eleven completed configurations

## Conclusion

The engineering path is functioning, market exposure is controlled on the executed discovery histories, and the research has rejected several plausible but weak changes. **We have not yet established a strong trading edge.** The leading development result is C06 at net Sharpe 0.762944; validation and the internal audit remain closed. More numerical machinery has not automatically improved the score.

Eleven of the twelve available discovery configurations have now been scored. The final interaction challenger also failed to improve its benchmark. We are closing this discovery checkpoint without spending the remaining slot on another variation of a weak result. The research has produced working candidate strategies and reproducible evidence, while their future performance remains unresolved.

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
| C11 | C02 plus all 78 pairwise characteristic products |0.603346|0.722123|4.1666%|6.9058%|0.8199%|+0.022222|10.46|

Exact records, source identities, ledgers and reproduction commands are in `evidence/discovery_C01_001` through `discovery_C11_001`. All eleven completed with exit 0 and 20 recorded workflow checks each. Every declared path feasibility flag passed; this is not a universal future guarantee. The [experiment ledger](EXPERIMENT_LEDGER.md) preserves the prospective admissions and their chronology. The [C06 evidence](../evidence/discovery_C06_001/summary.json), [C11 evidence](../evidence/discovery_C11_001/summary.json) and [first-wave paired comparison](../evidence/comparison_wave1_001/REPORT.md) support the principal conclusions below.

The timing column measures candidate calls on one pinned CPU with one numerical thread, including actual periodic updates. Independent runs used different pinned CPUs while sharing the host. Elapsed-time outliers are retained, including a 10.85-second C07 call with ordinary iteration count; its precise host cause is unverified. The contract concerns average time. Forecast century numbers elsewhere are extrapolations, not executed century tests.

## Findings and their limits

**Fast adaptation was a poor response to the apparent changing signals.** C03 worsened gross as well as net Sharpe, more than doubled C02's fees, and traded more. The first-wave paired block bootstrap gives a C03-minus-C01 Sharpe range below zero under both predeclared block lengths. This is evidence against this 63-day design on development history. It does not prove coefficients never change.

**The original curvature contrast did not translate into a material additive gain.** C02 improved net Sharpe over C01 by only 0.0152. Its paired 95% bootstrap ranges span−0.169 to+0.204 at block length 21 and−0.217 to+0.224 at length 63. We cannot treat that small observed gain as established superiority. C04's 0.0166 net increment over C02 is similarly uncertain. These conditional resampling ranges assume the development sample is informative and do not correct the whole research search or predict hidden-future performance.

**GLS and factor risk have an interaction worth retaining, but neither is a demonstrated solution.** GLS alone, C05, was worse than C02. C06 used byte-identical C05 forecasts with factor risk and produced the best current score. It reduced realized volatility and net market beta while preserving more return per unit risk in this comparison. Increasing both covariance ranks to 50 reduced return, risk and costs but did not improve the frozen primary metric. The joint rank change cannot separate learning effects from portfolio effects.

**The gross-cap approximation was real, and two fixes have now been measured.** Baseline postsolve scaling occurred on roughly 63–97% of first-wave calls. C07 integrates beta, stock boxes, transaction costs and the gross budget into one convex solution; it has no proportional rescaling and lowers C02 fees from 0.7773% to 0.4979% per year. Its forecasts are byte-identical to C02. The net-Sharpe improvement is modest. C08 uses a much simpler size change and eliminates scaling entirely, but leaves Sharpe near C02. Removing an implementation approximation does not by itself create alpha.

**Longer memory helped the pooled number while weakening the last block.** C09's four block Sharpes are 1.189,0.817,0.644 and 0.181, versus C02's 1.142,0.611,0.532 and 0.393. Its lower turnover and fees contribute to the gain. It does not dominate across time and does not establish stable true coefficients.

**The fixed interaction extension did not improve the conditional-mean model.** C11 preserved C02's original 26 linear/squared terms and its entire diagonal portfolio, adding all 78 centered pairwise products with a fixed stronger ridge penalty. Net Sharpe fell by 0.034221 to 0.603346; gross Sharpe also fell, while annual fees rose from 0.7773% to 0.8199%. Its four block Sharpes were 1.111, 0.537, 0.545 and 0.362, with only the third slightly above C02. This result argues against this specific full-quadratic extension. It does not prove that the true process is additive or that every interaction model would fail. No pair selection or interaction-penalty search was performed.

## What is implemented and verified

The source repository contains causal exponentially weighted characteristic learners, deterministic market-beta and residual-risk estimation, stock-specific drift-aware trading costs, a diagonal optimizer, a factor optimizer, a precision-weighted learner and an exact gross-budget optimizer. The custom numerical components' verification plans and executable tests were written before implementation; expected-red runs and subsequent passing checks were preserved.

C01 and C02 each completed a causal smoke workflow using 28 fresh processes on 600 allowed discovery rows (one baseline and 27 comparison scenarios). Protected forecasts, targets and economic ledgers matched exactly under the declared alterations, prefixes and append. These passes do not establish the unexecuted configuration-specific gates for later candidates. The original accounting workflow, source/cache integrity, actual full-fee reconciliation and all actual discovery paths have separate records.

C11's complete synthetic workflow was specified and its verifier written before candidate implementation. An expected missing-module run was preserved. After implementation and independent source review, four fresh-process workflows completed with 40 passing checks: baseline, repeat, joint future alteration at row 400 and prefix truncation at row 384. All 12 protected numerical comparisons matched exactly. Forecast correlation with the deliberately strong synthetic lagged interaction signal was 0.997914. This verifies that the implementation can learn that fixture and obey its tested information clock; the fixture's extremely high Sharpe is not market evidence. The [synthetic record](../evidence/interaction_workflow_001/summary.json) and [independent review](../reviews/interactions_verification_review.md) state the scope precisely.

The implementation and empirical research are AI work under the user's direction. No personal applicant discovery is invented. Source changes, rejected configurations, interrupted runs and corrective reviews remain in the record.

## Decision and next gate

C06 is the provisional discovery leader. Its combination of covariance-weighted learning and factor risk warrants further examination, but the development score was selected after several experiments. We cannot interpret it as an unbiased estimate of future performance. The current outcome supports retaining the best fixed candidates for further checks, not claiming a strong edge or adding a broad parameter search.

Slot 12 remains unassigned, and no validation shortlist has yet been frozen. The next work is exact finalist/configuration causality and long-history runtime verification on permitted or synthetic inputs, followed by a frozen shortlist of at most three candidates. The prescribed comparison then ranks eligible candidates on pooled daily net Sharpe across the two validation blocks. Only the selected, fixed candidate may enter the locked audit. The original simplicity tie rule and beta requirement remain unchanged.

Validation input rows `[2016,3024)` and audit input rows `[3024,3780)` remain economically uninspected. Their official score masks are recorded separately in the protocol. Neither a full finalist engineering gate, an actual century runtime test, nor a clean final-submission replay has been completed. This checkpoint is a private research deliverable and is not an employer-ready final package.
