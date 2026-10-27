# Frozen validation: performance and uncertainty

27 October 2026, Europe/Paris. This review uses only the prospectively specified validation metrics, paired bootstrap and fixed-decision fee stresses. It makes no selection-rule change and reads no audit outcomes.

**C09 has the higher pooled validation net Sharpe:0.6592 versus0.3986 for C06. Both satisfy the reported beta and runtime eligibility conditions. The planned uncertainty ranges are wide and include zero for both policies; the paired ranges also include no difference.** The point ranking therefore supports the frozen decision procedure while leaving substantial uncertainty about future profitability and relative performance.

## Execution and provenance

Both frozen protected-controller packets completed with scope-limited pass status, exit0 and closed artifact manifests before the unchanged uncertainty reporter ran. The reporter source SHA256 is `859829789c827670529b6065c914e9c60bf158b2d3badbdda3403222dc3a213c`; validation nomination SHA256 is `fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5`.

The report completed with **291 checks passed, exit0**. It verified consumed source/artifact identities, exact full day sequences, shared canonical inputs and market observations, fixed masks, original metric reconciliation, the nominated configurations and preserved snapshot bytes. The complete results are in [validation_uncertainty_001/summary.json](../evidence/validation_uncertainty_001/summary.json), SHA256 `69e22c5cfe9803a2c7079dd06ae25eb8470f889cf43015358f9b80c507af222b`. Both block-start matrices and all replicate results are retained in that packet.

## Full-cost validation results

All indices are zero-based with exclusive upper bounds. A is `[2016,2520)` with504 observations; B is `[2520,3023)` with503; pooled validation is `[2016,3023)` with1,007. The pooled Sharpe is calculated from the pooled daily series, not averaged from the block Sharpes.

| Metric | C06 | C09 |
| --- | ---: | ---: |
| Validation A net Sharpe |0.5173 |0.3662 |
| Validation B net Sharpe |0.3124 |0.9358 |
| Pooled net Sharpe |0.3986 |0.6592 |
| Pooled gross Sharpe |0.5716 |0.7107 |
| Annual arithmetic net return |1.4826% |2.6759% |
| Annual net volatility |3.7195% |4.0593% |
| Annual full fees |0.6440% |0.2088% |
| Realized net market beta |0.00467 |0.00586 |
| Maximum pooled drawdown |5.9350% |6.3592% |
| Full-replay mean candidate rebalance |8.454ms |2.130ms |

C09 combines a higher pooled gross Sharpe with lower recorded fees. The relative ordering changes across the two validation blocks: C06 is ahead in A and C09 in B. This is observed variation, not a reason to select a favorable block or alter the pooled ranking. Runtime figures are actual candidate measurements for the complete replay on this environment; period-specific instrumented scorer timing is retained separately in the machine-readable metrics.

## Prespecified bootstrap ranges

Each block length used exactly1,000 ordinary moving-block replicates, with nonwrapping starts, truncation to the original1,007 observations and identical sampled indices for both candidates. Seeds were20261048 for21-day blocks and20261090 for63-day blocks. The table reports empirical2.5%/97.5% quantiles using linear interpolation. Every reported metric and paired difference had1,000 finite replicates; undefined counts were zero.

| Quantity |21-day blocks |63-day blocks |
| --- | ---: | ---: |
| C06 annual net mean |[−2.994%,5.694%] |[−1.128%,5.682%] |
| C09 annual net mean |[−0.842%,6.840%] |[−0.089%,6.386%] |
| C06 net Sharpe |[−0.847,1.484] |[−0.308,1.563] |
| C09 net Sharpe |[−0.202,1.700] |[−0.021,1.673] |
| Paired Sharpe difference: C06 minus C09 |[−1.231,0.695] |[−0.939,0.552] |

Both prespecified block choices leave zero inside each policy's net-mean and Sharpe range. Both paired ranges cross zero. These conditional resampling results do not establish a clear separation in underlying performance, and they are not probabilities that either policy is the true winner. They do not correct all prior development or validation selection optimism. The frozen selection criterion remains the observed eligible pooled net Sharpe.

## Fixed-decision fee sensitivity

The same saved gross returns and decisions were retained; only the recorded fee series was multiplied by the three predeclared factors. No allocator was rerun, and the1.0 case remains the sole selection input.

| Fee multiplier |C06 pooled net Sharpe |C09 pooled net Sharpe |
| --- | ---: | ---: |
|1.0× |0.3986 |0.6592 |
|1.5× |0.3121 |0.6335 |
|2.0× |0.2255 |0.6077 |

At2.0× fees, annual arithmetic net returns are0.8386% for C06 and2.4672% for C09. These remain positive point estimates for this recorded path. The stress is conditional on fixed historical decisions and does not estimate the behavior of a policy reoptimized for different trading costs.

## Scope of the conclusion

The reporting workflow passed its engineering checks, and validation favors C09 by the frozen point-estimate criterion. The uncertainty evidence supports a measured claim: promising positive net validation performance with substantial sampling and selection uncertainty. Root owns the selection record and any later single-policy audit release. This review introduces no candidate, diagnostic search, parameter change, alternative cost grid or audit access.
