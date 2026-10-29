# Wave 3 (Claude) — results: no variant beats V3; V3 stays

29 October 2026. Plan, committed before scoring: [WAVE3_PLAN_20261029.md](WAVE3_PLAN_20261029.md)
(commit `242ffd0`). Code: [wave3.py](wave3.py), which imports `handoff_v3` unchanged and scores
with the original scorer. Rows, summaries and logs are in `results/`.

## Scores (original scorer, rows 253..3778)

| Variant | Net Sharpe | vs V3 | Gross Sharpe | Beta | Fees/yr | Mean gross | Stages s1 / s2 / s3 | Decision |
|---|---:|---:|---:|---:|---:|---:|---|---|
| V3 (harness check) | **1.444733** | — | 1.502 | 0.103 | 0.254% | 1.83 | 1.191 / 1.840 / 1.655 | baseline, exact |
| M2 vol-managed sleeve | 1.440761 | −0.0040 | 1.499 | 0.101 | 0.255% | 1.83 | 1.196 / 1.827 / 1.650 | **fail** (gain < 0.005; worse in 2 of 3 stages) |
| H1 hybrid latent-factor risk | 1.350984 | −0.0937 | 1.412 | 0.106 | 0.284% | 2.18 | 1.174 / 1.639 / 1.508 | **fail** (worse in all stages) |
| J (M2 + H1) | not run | | | | | | | the plan runs J only if both pass |

The V3 row reproduces 1.4447333005564316 exactly, so the harness is faithful. All 7,054 solves in every run
are certified. Stage masks here use the day index of each scored row, t = 253 + i:
s1 [253, 2016), s2 [2016, 3024), s3 [3024, 3779). GPT's stage masks omit two boundary rows, so
s1 and s2 differ from GPT's figures in the third decimal.

Paired 63-day block bootstrap of the difference vs V3 (reported, not used for selection;
`results/wave3_bootstrap.json`):
- M2: −0.004, 95% interval [−0.017, +0.011], positive in 33% of draws.
- H1: −0.094, 95% interval [−0.170, −0.002], positive in 2% of draws.

## What failed and why (observations, with interpretations labeled)

- **M2.** Its average sleeve was 0.053, range 0.031–0.091. Inverse-volatility timing of the
  sleeve did not raise net Sharpe, even though market volatility clusters.
  - *Interpretation:* the market's mean return in this simulation seems to rise with its
    volatility, or the timing gain is too small to show against noise and extra trading.
- **H1.** Realized volatility rose (4.78% vs 4.57%), the book levered up (mean gross 2.18 vs
  1.83), and gross Sharpe fell.
  - *Interpretation, consistent with the pre-plan diagnostic* (past top-10 residual loadings
    capture 3.9% of later residual variance): the latent structure drifts. Carving it out of
    specific variance makes the allocator underestimate risk on new data.

## What this wave adds to the map (diagnostics, `research/v3/*.json`)

| Question | Evidence | Answer |
|---|---|---|
| Are the characteristics noisy? | lag autocorrelation 0.999 / 0.98 / 0.80 at 1 / 21 / 252 days | no; nothing to filter |
| Do premia have exploitable short-horizon persistence? | block-mean autocorrelation 0.015 / −0.054 / −0.060 at 21 / 63 / 126 days | no |
| Would richer shapes or interactions raise the ceiling? | `ceiling_shapes.json` | no causal gain; bias-corrected ceiling 1.23–1.50 vs 1.456 |
| Would weighted or rank-based estimation help? | `ceiling_estimators.json` | no; ceiling identical (1.456) or lower (1.436); characteristics are Gaussian (kurtosis 3.0) |
| Is there priced latent residual structure? | `residual_structure.json` | no premium; unstable loadings |

**Where that leaves V3** (interpretation): the stock book alone (E2) earns about 1.40 gross
Sharpe. The bias-corrected, constant-premia hindsight ceiling of its 27 directions is 1.46.
Premia do move between periods (sub-period ceilings 1.20 / 1.48 / 2.48), but neither their
own past (this wave) nor market volatility (GPT's F3) forecasts those moves. Remaining
historical-score levers:
- **costs:** at most the 0.057 gap between gross and net Sharpe;
- **more market exposure:** deliberately not used (see the plan);
- **genuinely new information:** none found in these data.

## Decision

Under the pre-registered rule, V3 (`POLICY.sleeve = 0.05`, net Sharpe 1.444733) stays the
selected candidate. No production file changed.
