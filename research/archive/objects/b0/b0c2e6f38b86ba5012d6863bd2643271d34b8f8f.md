# R1 integration specification — 2026-10-29

Research replay, not yet production: B0 1.4447333005566665; R1 1.4576547036224103; I1 1.0303575847433648; C5 1.442386789905901; C80 1.3731118966337454; Cmix 1.437483508634006. Cached B0 matches all four economic columns of the original replay exactly. R1 is the sole candidate passing the registered development score gate.

This document precedes the standalone R1 implementation, not the research implementation. Do not retune any hyperparameter. The research implementation used float32 ML features, label days starting at row 2, and early_stopping=False. These are implementation details, not post-result changes.

## Candidate implementation

Preserve the upstream V3 F2 forecast, fixed 0.05 market sleeve, risk factor covariance, optimizer, caps and E2 multiplier policy. Compute R1 risk multipliers in forecast using a rolling buffer rather than full-history basis/risk tensors. At action day s, include labels only through s. Latest training pair is features[s-1] against squared residual[s]/d[s-1]. The prediction for action day s uses features[s] (all published) and affects holdings for day s+1. Refit at target rows 253+126*k. Return a forecast tensor exposing both F2 alpha and the next-action risk multiplier, so altered-future tests inspect both. ML features are 13 standardized characteristics, standardized trailing beta and log baseline specific variance. The risk multiplier is 0.5+0.5*clip(predicted_ratio,0.5,2). Both virtual and traded stock books use it. No precomputed data-dependent parameters in the submission.

## End-to-end checks and expected outcomes

1. Full original scorer replay: exact same economic rows and target positions as research R1, tolerance 1e-10. All allocator certificates valid; no ruin or nonfinite outputs.
2. Prefix runs: prefix forecast alpha/risk channels and all common executed positions match the full run. Treat the last, untraded forecast boundary carefully; row t uses source data strictly before t.
3. Return-only, characteristic-only and joint future mutation: modify source rows from 630 and/or 2016. Forecast rows through the boundary inclusive remain unchanged; positions chosen before mutation remain unchanged. Include a mutation immediately before a scheduled refit.
4. A repeat run of the same prefix after a different run must reproduce its forecasts and positions: state resets are mandatory.
5. Measure complete forecast time, including risk-model fits, and original uncached sequential rebalance time on one BLAS/OpenMP thread. Cached research timings alone do not establish deployable timing. Keep average rebalance below 100 ms; report projected forecast time per century as an extrapolation, not a century run.
6. No independent reviewer agent was available in this session; do not label same-session checks an independent review. Do not submit, merge or replace production based solely on the small development gain.

## Important negative evidence already observed

The paired 63-day circular block bootstrap (3000 draws, seed 20261029) gives a Sharpe-gain interval [-0.0074093,0.0340631], positive in 89.2% of draws. This is not corrected for overall research selection. R1 improves two stages but worsens the last (1.633865 vs 1.654664). Its unweighted next-day residual-variance QLIKE is worse by 0.0089924 on scored rows: do not claim uniformly superior risk forecasting. The historical portfolio gain is real under this replay, but stronger future-performance evidence has not been established.
