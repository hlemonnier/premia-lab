# Wave 1 discovery comparison

The four initial candidates do not establish a strong trading edge. These are development-sample outcomes, and the small observed improvements require much more caution than their ranking alone suggests.

| Candidate | Net Sharpe | Gross Sharpe | Annual net mean | Annual vol | Annual fees | Net beta |
|---|---:|---:|---:|---:|---:|---:|
| C01 | 0.6223 | 0.7162 | 4.323% | 6.946% | 0.652% | 0.0172 |
| C02 | 0.6376 | 0.7501 | 4.404% | 6.907% | 0.777% | 0.0212 |
| C03 | 0.1065 | 0.3514 | 0.752% | 7.059% | 1.727% | 0.0282 |
| C04 | 0.6542 | 0.8820 | 2.358% | 3.605% | 0.822% | 0.0076 |

## Paired circular moving-block uncertainty

Both predeclared block lengths are reported. Intervals are 2.5th–97.5th percentile bootstrap ranges of paired Sharpe differences; the sign frequency is not a posterior probability or a selection rule.

| Contrast | Block length | Observed delta | 95% percentile range | Bootstrap fraction positive |
|---|---:|---:|---:|---:|
| C01 minus C01 | 21 | 0.0000 | [0.0000, 0.0000] | 0.000 |
| C02 minus C01 | 21 | 0.0152 | [-0.1692, 0.2042] | 0.544 |
| C03 minus C01 | 21 | -0.5159 | [-0.9340, -0.1484] | 0.001 |
| C04 minus C01 | 21 | 0.0319 | [-0.5179, 0.5400] | 0.551 |
| C04 minus C02 | 21 | 0.0166 | [-0.4202, 0.4450] | 0.543 |
| C01 minus C01 | 63 | 0.0000 | [0.0000, 0.0000] | 0.000 |
| C02 minus C01 | 63 | 0.0152 | [-0.2171, 0.2241] | 0.506 |
| C03 minus C01 | 63 | -0.5159 | [-0.9510, -0.1091] | 0.007 |
| C04 minus C01 | 63 | 0.0319 | [-0.4511, 0.4801] | 0.533 |
| C04 minus C02 | 63 | 0.0166 | [-0.4271, 0.4433] | 0.533 |

## Interpretation limits

The same daily block indices were used for every candidate in each draw. This preserves paired returns and within-block dependence; it does not establish stationarity, cover every dependence length, correct all research selection or predict hidden-future results. Circular joins are artificial. An interval containing zero is not proof of equivalence. No candidate was fitted or replayed by this report, and no validation/audit or later-candidate results were read.

`pooled_metrics.csv`, `fixed_blocks.csv` and `portfolio_diagnostics.csv` retain exact means, costs, exposure/scaling and all four fixed blocks. `bootstrap_draws_L21.csv` and `bootstrap_draws_L63.csv` preserve all draws. The frozen inputs, identities, seed and generation rule reproduce this report through `rerun.txt`. Runtime values are inherited observed measurements and are not new controlled benchmarks.
