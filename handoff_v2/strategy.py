"""Characteristic factor-risk strategy (V2). Draft note, 28 October 2026.

WHAT I CAME TO BELIEVE
The thirteen characteristics behave like factor loadings. Yesterday's thirteen
values and their squares explain about a third of each day's cross-sectional
residual return variance (26% for the linear terms alone), more than the top
thirteen principal components of residual covariance (20%), and stocks with
similar characteristics co-move. The forecast therefore earns mostly factor
premia, not stock-specific mispricing: removing the top return-factor
directions from C09's forecast cut its audit Sharpe from 1.80 to 0.67. Those
premia are small against factor volatility; a block-shuffle test cannot reject
constant premia (p = 0.29), so I do not claim they drift. Stocks with low
trailing beta earn more residual return. The four-temper / six-quark /
three-elf name groups are real correlation blocks (within-group |r| 0.28 versus
0.09), but group composites forecast worse (net Sharpe 0.59): members of one
group carry different premia.

WHAT I BUILT
Forecast: C09's causal ridge learner (13 standardized characteristics and their
centered squares, ridge 0.1, 1,008-day half-life) plus one column, each stock's
trailing market beta. Row t uses X[t-1]; the newest training pair is X[t-2]
against the market-residual return of day t-1.
Risk: Sigma = diag(d) + 0.3 D F D', with D today's characteristic basis, F an
exponentially weighted (126-day) covariance of daily characteristic factor
returns, d the variance they leave unexplained. A diagonal book (C09) holds the
factor bets fully; a full factor-risk book hedges them away. They earn in
different periods (daily correlation 0.53), and the 0.3 weight keeps part of
both. Allocation: an exact dual-Newton solver maximizes forecast minus risk minus
20-day-amortized linear costs around the drifted book, with an estimated-beta
hedge and 5% stock caps; it agrees with cvxpy to about 1e-9 and runs in about
1.5 ms. Mean rebalance is about 8 ms; the risk state is absorbed one day at a
time from history through today.

EVIDENCE (supplied scorer, full fees; every period has now been examined)
                 full run  2009-16*  2016-20*  2020-24*   cost/yr   beta
  C09 (handoff)    0.885    0.700     0.659     1.799     0.42%    0.009
  This strategy    1.243    1.098     1.657     1.148     0.18%    0.047
  (*row ranges [253,2015), [2016,3023), [3024,3779); labels are indicative)
Paired 63-day block bootstrap of the full-run difference: +0.36,
95% range [0.00, +0.82]. This version was chosen on the full fifteen years
among about two dozen variants, and the factor-risk weight from {0.1, 0.3, 1.0}
(1.155, 1.244, 1.199), so expect shrinkage. C09's sealed audit (1.80) remains
the only untouched estimate in this research, and most of it came from factor
exposure in a favorable period.

WHAT COULD GO WRONG OVER DECADES
Premia can change sign; the 1,008-day memory adapts slowly. If loadings stop
meaning what they meant, the factor model misprices risk. Realized beta grows
with book size (0.009 at one-fifth this size); estimated low-beta stocks tend
to have higher true betas, so a long-low-beta tilt can leave positive realized
beta. Costs are not the binding constraint here (0.18% a year).

WHERE THE AI DID THE WORK AND WHERE I DID
[To be written by the applicant in their own words.] Record so far: AI (Claude)
wrote the code, ran the experiments and drafted this note; the applicant
directed the review, asked for the data exploration, and chose to replace the
frozen C09 policy with an improved one chosen on the full sample.

Required files: model_v2/__init__.py, model_v2/engine.py, model_v2/allocator.py.
NumPy and the Python standard library only.
"""

from model_v2 import engine as _engine

_CONFIG = {
    "alpha_half_life": 1008.0, "ridge": 0.1, "min_training_days": 126, "feature_clip": 4.0,
    "beta_window": 252, "factor_half_life": 126.0, "specific_half_life": 126.0,
    "specific_shrinkage": 0.2, "variance_floor": 1e-6, "factor_risk_scale": 0.3,
    "risk_aversion": 200.0, "cost_horizon": 20.0, "weight_cap": 0.05, "gross_cap": 5.0,
}

_engine.configure(_CONFIG)
forecast = _engine.forecast
rebalance = _engine.rebalance
