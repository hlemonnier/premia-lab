"""Characteristic factor-risk strategy (V2). Candidate under review; draft note, 28 October 2026.

WHAT I CAME TO BELIEVE
The thirteen characteristics are useful conditional risk descriptors: yesterday's
values and their squares explain about a third of each day's cross-sectional
residual return variance, and the off-diagonal covariance they imply matters for
portfolio construction (keeping V2's marginal variances but dropping correlations
cuts net Sharpe from 1.24 to 0.94). Whether their payoffs are compensated factor
premia or characteristic-linked intercepts is not identified. Low trailing beta
predicts higher market-residual return. Conditional on the characteristics, the
beta factor's return loads strongly on the market (t about -20); its intercept is
unresolved (95% range about -0.37 to +0.16 bp/day), and a zero-alpha synthetic
market can reproduce the pattern, so estimation error is one sufficient channel,
not an identified mechanism. Shrinking betas toward their mean improves forecasts
of next-year beta estimates in this sample. Under the beta hedge, the beta feature
mostly prices net stock investment (V2 averages +40% net long, C09 +1%). About 0.7
of V2's 4.8 points of annual return is linear market exposure; a full-sample
market-residual series has Sharpe 1.08 (C09: 0.86). That is a descriptive
statistic, not a traded market-neutral strategy. Premium drift is unresolved
(block-shuffle p = 0.21). The 4/6/3 name groups are real correlation blocks, but
members carry different premia.

WHAT I BUILT
Forecast: C09's causal ridge learner (13 standardized characteristics and their
centered squares, ridge 0.1, 1,008-day half-life) plus each stock's trailing
market beta. Row t uses X[t-1]; the newest training pair is X[t-2] against the
market-residual return of day t-1.
Risk: diag(d) + 0.3 D F D', with D today's characteristic basis, F an
exponentially weighted (126-day) second moment of daily characteristic factor
returns and d the residual second moment. The 0.3 is an empirically chosen
exposure penalty, not a calibrated covariance: on the selected book it
understates realized gross second moment by 2.7x (scale 1: 1.07x).
Allocation: an exact dual-Newton solver for forecast minus risk minus 20-day
amortized linear costs around the drifted book, with an estimated-beta hedge and
5% caps; each solve is certified (caps, hedge, duality gap; 3,527 of 3,527 on the
real run, largest gap 1.3e-17), and an uncertified solve falls back to a certified
diagonal problem rather than being traded; the final book is checked after the
gross cap. forecast() starts a scoring session and
resets the risk state; characteristic panels are canonicalized before use.

EVIDENCE (supplied scorer, full fees; all rows already examined during research)
                 rows 253-3778  253-2014  2016-3022  3024-3778  cost/yr   beta
  C09 (handoff)      0.885       0.700     0.659      1.799     0.42%    0.009
  This strategy      1.243       1.098     1.657      1.148     0.18%    0.047
Paired block bootstrap of the difference: +0.36, 95% ranges [-0.00, +0.82]
(63-day), [-0.04, +0.77] (21), [-0.03, +0.88] (126). Selected on the full sample
among about 25 variants; expect shrinkage. Rejected under frozen rules: adding the
beta column to the risk model (better risk score, net Sharpe 1.167); correcting
betas with past-only shrinkage and holding zero beta (realized -0.014, Sharpe 1.044)
or an explicit 0.05 (realized 0.036, Sharpe 1.231; difference with V2 unresolved).
Moving the target from 0 to 0.05 adds market return almost one for one (99.9% of
the difference is the market); both corrected books sit about 0.014 below target.

WHAT COULD GO WRONG OVER DECADES
Premia can change; the 1,008-day memory adapts slowly. About 0.04-0.05 of realized beta
is carried implicitly (corrected betas remove most of it); it earned this sample's
market premium and would lose if the market drifts down.
Realized beta also grows with book size. The 0.3
penalty was chosen, not estimated. Costs are not binding (0.18% a year).

WHERE THE AI DID THE WORK AND WHERE I DID
[To be written by the applicant in their own words.] Record so far: AI (Claude)
wrote the code, ran the experiments and drafted this note; an independent AI
review (GPT) audited it and specified the follow-up tests; the applicant directed
both and decides whether this candidate replaces C09.

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
