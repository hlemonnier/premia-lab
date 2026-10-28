# V2: characteristic factor risk

28 October 2026. Exploratory research on the full fifteen years, after the
protected C09 cycle. Every period here was already exposed, and the brief allows
tuning on the full sample. These numbers are not a clean confirmation; expect shrinkage.
The frozen C09 handoff (`handoff/`) is unchanged. The new strategy is in `handoff_v2/`.

## Findings about the market

| Question | Test | Result |
|---|---|---|
| Are the characteristics factor loadings? | Daily cross-sectional R² of residual returns on yesterday's characteristics vs PCA of residual covariance | 26% (13 linear), 33% (+ squares) vs 20% for the top 13 PCs; rank correlation of characteristic similarity with residual correlation 0.51 |
| Is C09's edge factor exposure? | Project top-k return factors out of the forecast | Audit Sharpe 1.80 → 0.67 (k=10); the edge is mostly factor premia |
| Do premia drift? | Between-segment variance of 26 factor-return means, 63-day block-shuffle null | Not established: p = 0.29 overall; linear terms borderline (p = 0.05, Frolic and Dread); squares p = 0.89. Low power |
| Do the 4/6/3 name groups matter? | Within- vs between-group characteristic correlation; group-composite forecast | Real blocks (|r| 0.28 vs 0.09, permutation p < 5e-5, stable) but composites score 0.587 net |
| Anything beyond characteristic levels? | Residualized rank IC of past returns, characteristic changes, beta, volatility, cost | Residual reversal (1–21 days) and low beta stand out; reversal decays within ~10 days |

## Scored variants (supplied scorer, full fees; paired 63-day block bootstrap vs C09)

| Variant | Net Sharpe | Δ vs C09 [95%] | Disc / Val / Audit |
|---|---|---|---|
| C09 (exact reproduction) | 0.885 | — | 0.700 / 0.659 / 1.799 |
| + beta feature | 0.923 | +0.038 [+0.01, +0.07] | 0.714 / 0.781 / 1.825 |
| + decorrelated prediction + beta | 1.000 | +0.115 [−0.10, +0.30] | 0.770 / 0.810 / 1.858 |
| Factor risk, scale 1.0, + beta | 1.199 | +0.315 [−0.17, +0.90] | 1.027 / 1.761 / 0.675 |
| **Factor risk, scale 0.3, + beta (handoff_v2)** | **1.244** | **+0.359 [0.00, +0.82]** | **1.100 / 1.657 / 1.149** |
| Factor risk, scale 0.1, + beta | 1.155 | +0.270 [−0.03, +0.64] | 1.045 / 1.375 / 1.360 |
| Same as the handoff, 5× book | 1.243 | — | 1.098 / 1.657 / 1.148 |

Negative results kept: residual reversal as a feature (0.746), reversal scaled to
its decay (0.861–0.871), 5-/20-day labels (0.858 / 0.831), 252-day and infinite
memory (0.867 / 0.777), projecting out 10 / 20 return factors (0.651 / 0.867),
group composites (0.587 / 0.854), cost horizons 5–250 days (0.869–0.880).
Full numbers: `results/comparison.json` and `results/variant_*.json`.

Why scale 0.3: the diagonal book (C09-like) holds factor bets fully, the full
factor-risk book hedges them; they earn in different periods (daily correlation
0.53) and an equal-risk blend of their returns is far more even across periods.
Scaling the factor covariance gives one book between the two, with costs netted.
The scale was picked from {0.1, 0.3, 1.0}.

## Verification

- Allocator: specification (`ALLOCATOR_SPEC.md`) and tests (`test_allocator.py`)
  written before the implementation; the first run failed on the missing module
  as expected; 38 checks then passed, including agreement with cvxpy/Clarabel
  (weights within ~1e-7) and a 1.4 ms median solve at n = 1000, k = 26. A
  separate band-heavy regime agreed to 2e-9.
- Forecast causality on the real data: inputs replaced from row c ∈ {400, 1500,
  3024, 3700} on; rows ≤ c bitwise identical (boundary row included), also with
  an altered copy in Fortran memory layout and with truncated histories.
- Clean-folder run of `handoff_v2/` with the unmodified `score.py`: Sharpe 1.24,
  beta 0.05, cost 0.18%/yr, gross 1.58, 10.5 ms per rebalance. Its daily ledger
  matches the research run to 3.4e-11 (labels computed directly rather than as
  cumulative-sum differences).
- Century-length runtime: see `results/century_v2.txt`.

## Attribution

AI (Claude) designed and ran these experiments, wrote the code and this report,
at the applicant's direction. The applicant asked for the data exploration and
chose to replace the frozen policy with one chosen on the full sample.
