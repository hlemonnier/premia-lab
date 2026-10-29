# M1 actual-market result

29 October 2026. Frozen candidate M1: +0.05 equal-weight stock basket around the unchanged F2+VTvol policy. **No tuning or additional sleeve sizes were run.**

## Outcome

M1 improves the official full-history net Sharpe from **1.318334966090838** to **1.426560898191992**, a gain of **0.108225932101154**. It clears the frozen score threshold and all checks implemented in this actual replay. Root's independent actual-evidence readback is complete and agrees. M1 was not separately run through a century-length replay: the subsequently selected E2+M1 composition scored **1.444733300556666** and passed its own 25,200-row operational gate. Production integration remains separate; this record does not claim production promotion.

| Exposed historical segment | M0 net Sharpe | M1 net Sharpe | Difference |
|---|---:|---:|---:|
| Full | 1.3183349661 | 1.4265608982 | +0.1082259321 |
| Discovery | 1.1035119417 | 1.1786691069 | +0.0751571651 |
| Validation | 1.6339700633 | 1.8102604044 | +0.1762903412 |
| Audit | 1.5930290673 | 1.6644954621 | +0.0714663948 |

All periods are exposed development. The historical labels do not constitute an independent holdout. Paired uncertainty, if reported by the master comparison, is descriptive and is not an additional admission rule.

Root's independently reviewed readback verifies the saved array manifests and
reconstructs M1's stock-target accounting with maximum error 6.94e-18. Its
predeclared paired moving-block bootstrap uses 2,000 draws and seed 20261027.
The 95% percentile intervals for the net-Sharpe difference against the prior
leader are:

| Block length | Interval |
|---|---:|
| 21 observations | [0.029080, 0.183728] |
| 63 observations | [0.027593, 0.176129] |
| 126 observations | [0.022621, 0.174402] |

These intervals are not adjusted for research selection and do not create a
new independent confirmation. The complete independent record is
`evidence/v2_score2_root_20261029/standalone_readback_001.json`, SHA256
`af16207ccedc0cb380e332041f4d90260dd1af75db21d0fdb195c6db30c57926`.

## What changed economically

| Full-period metric | M0 | M1 |
|---|---:|---:|
| Net annualized arithmetic return | 5.7865071695% | 6.5098694966% |
| Net annualized volatility | 4.3892541109% | 4.5633309485% |
| Annualized trading cost | 0.3364064134% | 0.3370403032% |
| Realized net beta | 0.052720354680 | 0.102711096967 |
| Mean closing gross | 1.8236404524 | 1.8342634126 |
| Maximum closing gross | 3.1599302046 | 3.1719645412 |

The annualized net return increases by 0.7233623271 percentage points. Incremental annualized costs are 0.0633889790 basis points of capital. These are actual differences between separately executed, stock-level-netted paths. They are not the sum of standalone estimated trading costs.

M1's forecast and independent inner targets are exactly M0's. The outer gross cap does not bind on any decision. The gain therefore belongs to the deliberately added fixed market direction and its actual incremental trading costs; it is not a new stock-selection or market-timing alpha claim. No beta shrinkage, premium estimate or hindsight weight search was introduced.

The requested actual-book attribution is recorded in
[actual_book_attribution.json](actual_book_attribution.json). It verifies every
earning day that `gross_M1 - gross_M0 = 0.05 * market`, with maximum discrepancy
6.18e-18. The actual net-return difference equals that increment minus
`fees_M1 - fees_M0`, with maximum discrepancy 6.29e-18. Annualized arithmetic
contributions are +0.7239962169 percentage points from the gross market basket,
minus 0.0006338898 percentage points of incremental actual fees, yielding
+0.7233623271 percentage points of net return.

The incremental-cost regression slope on the market is 0.000009257713.
Consequently the net-beta increment is 0.049990742287, slightly below the gross
increment of 0.05. This follows from the actual fee difference. No fitted-beta
return subtraction is used to manufacture an alpha estimate.

## Verification and timing

- M0: all 20 actual-replay checks pass. Its original net Sharpe is reproduced exactly; saved original economic columns differ from the prior CSV replay by at most 4.44e-16 due to the CSV float round trip.
- M1: all 29 actual-replay checks pass. The unchanged-source gate also passes.
- Actual future alteration and prefix truncation preserve protected forecasts, actual targets, inner targets and scorer economic columns exactly.
- Saved-target accounting reconstruction error is 0.0. The free opening and charged final non-earning rebalance are retained. All allocator certificates pass.
- Full net beta 0.102711096967 is below the 0.2 constraint. Targets and returns are finite, all observed gross daily returns exceed -1, and stock/gross bounds pass.
- One CPU, CPU 3, with numerical-library thread counts fixed at one. M1 instrumented mean rebalance 3.290056 ms; forecast 2.584562 seconds. These figures cover supplied-history execution; the century-length gate is not part of this harness.

## Provenance and reproducibility

The root master plan was published in commit `d2997e0d98c6407da4b503a77060966904486062` before actual scores. Root independently accepted M1's source and synthetic evidence in `evidence/v2_score2_root_20261029/M1_SOURCE_EVIDENCE_REVIEW.json`, then released only M0/M1 and their predeclared causality checks in `M1_ACTUAL_RELEASE.json`.

All original CSV hashes, ce3 baseline sources, reference sources, root review, owned/master plans and release bindings were verified before launch. The exact command, one-thread environment, source/data identities, execution timestamps and 63.65-second total wall time are retained in [actual_001_execution.json](actual_001_execution.json). Stdout and stderr are retained beside it.

The source-bound prospective synthetic result is `synthetic_002/result.json`. Actual sources remained frozen:

- Policy: `91f6c27a11d18e23ac937dd7f4962210ee081bd011e963431e2a495b16a8648b`.
- Harness: `0095e461a0a9d1818bb53944d6cb0716c91196ffd7f217edf128b7c8b4521e3d`.
- Plan: `f8a0e5e084ca928ed418841689da9c0bc21949ecd51f4ceb834115a2d867d58a`.
- Actual result: `98495701d57df8397b1aac70e54ab72727e8f8bb2cbffeb84c4e107e8ab17b5c`.

[actual_001/result.json](actual_001/result.json) contains complete metrics/checks. Each workflow saves atomic `targets.npy`, `inner_targets.npy`, `rows.npy` and `forecast.npy`, their readback manifests, complete decisions and daily economics. M0/M1 targets have shape 3527×1000 and original scorer rows have shape 3526×5. The data and source manifests, executed source copies and full artifact hashes are retained in `actual_001/`.
