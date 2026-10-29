# Wave 4 (Claude) — results: no new information, no real construction gain; V3 stays

29 October 2026. Plan and addendum, both committed before their runs:
[WAVE4_PLAN_20261029.md](WAVE4_PLAN_20261029.md) (commits `5586eeb` and `ae727f4`). Code:
`wave4_newinfo.py`, `wave4_grid.py`, `wave4_ext.sh`, `wave4_beta_bootstrap.py`. Outputs are in
`results/wave4/`.

## Block 1 — new information: nothing passes the gate (incremental IC Sharpe ≥ 1.0, both halves > 0)

| Signal (causal) | IC Sharpe alone | Incremental over F2 (1st / 2nd half) |
|---|---:|---|
| Cost as illiquidity characteristic | 0.12 | 0.08 (0.05 / 0.11) |
| Characteristic changes, 1 day (causal ridge) | −0.14 | −0.06 (−0.32 / 0.19) |
| Characteristic changes, 21 days | 0.22 | 0.18 (0.16 / 0.19) |
| Lead-lag of daily factor returns | 0.11 | 0.07 (0.20 / −0.06) |
| Market lead-lag (stock reaction to yesterday's market) | 0.05 | −0.02 (−0.06 / 0.01) |

For reference, F2's own IC Sharpe is 1.36 (`ml_incremental.json`).

## Block 2 — cost and risk construction: apparent gains are market share, not construction

**Net Sharpe with the 0.05 sleeve** (rows: factor_risk_scale; columns: cost_horizon):

| frs \ ch | 5 | 10 | 20 | 40 | 80 |
|---|---:|---:|---:|---:|---:|
| 0.2 | | 1.4060 | 1.4073 | 1.3781 | 1.3418 |
| 0.3 | | 1.4502 | **1.4447** (V3) | 1.4109 | 1.3731 |
| 0.5 | 1.4904 | 1.4718 | 1.4675 | 1.4230 | 1.3814 |
| 0.7 | 1.5240 | 1.4526 | | | |
| 1.0 | 1.5405 | 1.4052 | | | |

**The same construction without the sleeve** (stock book only; V3's own sleeve-0 book is
1.3396):

| frs \ ch | 5 | 10 | 20 |
|---|---:|---:|---:|
| 0.3 | | 1.3396 | 1.3396 |
| 0.5 | 1.3338 | 1.3353 | 1.3439 |
| 0.7 | 1.3481 | 1.3014 | |
| 1.0 | 1.3520 | 1.2401 | |

**Market share of variance** (`results/wave4/market_share.txt`): the sleeve-0.05 scores rise
with the market's share of book variance.

| Book | Market share of variance | Net Sharpe | Beta |
|---|---:|---:|---:|
| V3 | 10.2% | 1.4447 | 0.103 |
| (10, 0.5) | 16.3% | 1.4718 | 0.090 |
| (5, 0.7) | 19.1% | 1.5240 | 0.074 |
| (5, 1.0) | 27.2% | 1.5405 | 0.071 |

The reported beta *falls* across these cells, because the stock book shrinks while the sleeve
stays at 0.05 notional. So beta alone hides the growing market share.

**Decision under the addendum rule:**
- The best sleeve-0 cell is (5, 1.0) at 1.3520, +0.012 over 1.3396.
- Its neighbor (10, 1.0) is 1.2401, which fails the flatness requirement.
- The sleeve-0 surface is flat within ±0.015, apart from that drop.
- **No construction change is selected.** The risk-matched sleeve applies only to a selected
  construction, so it was not run.

**Interpretation.** The construction knobs mainly trade stock-book size against cost and risk
penalties. The stock book's Sharpe barely moves. The historical score rises when the fixed
sleeve becomes a larger part of a smaller book. That is the same market-exposure lever
documented for M1, reached indirectly.

## Block 3 — robustness of V3's future score (no selection)

- **20-year future paths** (stationary bootstrap, mean block 63, 2,000 paths):
  - V3: beta median 0.103, 95th percentile 0.111, 99th 0.114, P(beta > 0.2) = 0. Net
    Sharpe 5th / 50th / 95th percentiles 1.09 / 1.45 / 1.80.
  - Sleeve-0 book: beta 95th percentile 0.061. Sharpe 0.98 / 1.34 / 1.69.
  - This captures sampling noise under stationarity only. It does not capture structural
    change in the market, such as premium decay or a shift in the market premium.
- **Cost stress** (allocator re-optimized against the higher costs): net Sharpe 1.4447 at
  ×1 costs, 1.4310 at ×1.5, 1.4124 at ×2. Fees are not where V3's risk lies.

## Overall

Across waves 3 and 4 and the ML test, nothing in these data adds stock-selection signal beyond
F2, and no construction change improves the stock book. The one lever that reliably raises the
historical score is the market's share of risk. Its present level (10%, beta 0.103) is a
deliberate choice already documented. V3 stays.
