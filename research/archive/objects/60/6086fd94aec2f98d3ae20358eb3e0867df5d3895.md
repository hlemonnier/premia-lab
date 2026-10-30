# Selected C09 audit: performance and uncertainty

27 October 2026, Europe/Paris. This review covers only the selected C09 policy's prospectively specified audit metrics, moving-block bootstrap and fixed-decision fee stresses. Root released reporting after the canonical audit controller completed; the reporter executes no model and changes no selection rule.

**C09 produced a net Sharpe of 1.7992 after full recorded costs over the 755 audit observations. Both prespecified bootstrap ranges for net mean and Sharpe remain above zero. The recorded path also remains positive at twice the original fees.** This supports a positive result on the reserved simulated-market audit, with uncertainty about performance outside this period and cost model.

## Execution and provenance

The unchanged reporter SHA256 is `859829789c827670529b6065c914e9c60bf158b2d3badbdda3403222dc3a213c`. It consumed only the completed `audit_C09_001` packet under audit nomination SHA256 `b68c5db46c641f68bdaa7526464c846dd29e1b4ab65c7fd1ab6e8f775762cea4`, after root's pre-access commit `5522f41eb6b6b72b69b9a5f01268031ecea3869a` and explicit reporting release.

The reporter completed with **153 checks passed, exit 0**, status `EXECUTED_PASS_SCOPE_ONLY`. It verified the selected configuration, nomination and selection record, consumed source and artifact identities, complete ledger indices, fixed audit mask, original metric reconciliation and unchanged consumed snapshots. A subsequent readback verified the sizes and SHA256 hashes of all 44 artifacts listed in the reporting packet's closed manifest.

The authoritative results are [audit_uncertainty_001/summary.json](../evidence/audit_uncertainty_001/summary.json), SHA256 `6e36eaf4740acc5309b2c94306992bdcbbc57314a466c1fb6afa787ec94d7ba9`. The packet retains both block-start matrices, every replicate, the consumed ledgers and source identities, frozen plans, logs, environment and exact rerun command. Its artifact-manifest SHA256 is `3d3a40598d77b10c99adb3da36cf77de05aef0da16d863eacef83df51f8fbf3a`.

## Full-cost audit results

The score mask is the fixed zero-based interval `[3024,3779)`, encompassing return indices 3024 through 3778 inclusive: 755 observations. The original scorer's endpoint convention explains the unscored final input row. The policy continued its already specified causal online updates during the continuous replay; its configuration and selection remained fixed.

| Metric | C09 audit |
| --- | ---: |
| Net Sharpe | 1.7992 |
| Gross Sharpe | 1.8612 |
| Annual arithmetic net return | 9.6761% |
| Annual net volatility | 5.3779% |
| Annual full fees | 0.3331% |
| Realized net market beta | 0.005666 |
| Maximum audit drawdown | 7.0197% |
| Mean gross exposure | 0.8055 |
| Full-replay mean candidate rebalance | 2.265 ms |
| Full-replay maximum candidate rebalance | 6.676 ms |
| Full-replay candidate forecast time | 6.295 s |

The controller reports passing beta, mean-rebalance runtime, solvency and position-control conditions. Runtime measurements above cover the complete replay on this environment; the separate audit-period instrumented scorer mean is 2.343 ms. These are the original saved measurements, with no performance rerun for this report.

## Prespecified uncertainty ranges

Each block length used exactly 1,000 ordinary moving-block replicates with nonwrapping starts, concatenation and truncation to 755 observations. The seeds were 20261048 for 21-observation blocks and 20261090 for 63-observation blocks. The intervals below are the empirical 2.5% and 97.5% quantiles with linear interpolation. Every reported metric had 1,000 finite replicates and zero undefined replicates.

| Quantity | 21-observation blocks | 63-observation blocks |
| --- | ---: | ---: |
| Annual arithmetic net mean | [3.572%, 16.822%] | [3.395%, 17.086%] |
| Net Sharpe | [0.655, 3.172] | [0.630, 3.032] |

Both fixed block choices yield positive lower endpoints, while the ranges remain broad. These are conditional resampling ranges for the selected policy on this observed period. They are not a probability of future profit or a numerical guarantee against overfitting. Only C09 was admitted to the audit, so this report makes no audit-period claim of superiority over another policy.

## Fixed-decision fee sensitivity

The saved gross returns and trading decisions were held fixed, and only the recorded fee series was multiplied. The original 1.0 case remains the sole primary cost case; no allocator was rerun.

| Fee multiplier | Net Sharpe | Annual arithmetic net return | Annual fees |
| --- | ---: | ---: | ---: |
| 1.0× | 1.7992 | 9.6761% | 0.3331% |
| 1.5× | 1.7682 | 9.5095% | 0.4997% |
| 2.0× | 1.7372 | 9.3430% | 0.6662% |

Positive results at all three prespecified fee levels support robustness to this particular cost perturbation. They do not establish capacity, fill quality or costs beyond those represented by the supplied simulated-market ledger, and they do not describe a policy reoptimized for different fees.

## Scope of the conclusion

The reserved audit provides positive evidence for the already selected policy under the official accounting and frozen reporting procedure. The bootstrap assumes that the observed distribution and dependence are informative; two fixed block lengths cannot establish stationarity or cover every form of serial dependence. The reporting procedure does not correct all optimism from the preceding research path, and a 755-observation audit cannot guarantee the hidden continuation or real-market performance.

The engineering pass establishes that this report followed its declared scope and preserved its evidence. The audit outcome changes the strength of the performance claim, without changing the model, parameters, selection rule, score mask, bootstrap choices or fee grid. No further candidate or diagnostic search was performed for this review.
