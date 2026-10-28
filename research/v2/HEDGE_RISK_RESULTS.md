# Next-day hedge error, raw-risk reconstruction, ceiling and adaptive memory — results

28 October 2026. Executes `HEDGE_RISK_PLAN.md` (reviewer §2–§3) and `ADAPTIVE_PREMIUM_PLAN.md`.
Frozen books, supplied scorer path, all rows already exposed.

## §2 Next-day hedge error on frozen books (`results/hedge_risk/summary.json`)

Primary (V2 book): mean(H_corrected − H_raw) = −1.13e−7, i.e. **−1.9% of mean H_raw**.
95% block ranges: 21-day [−2.3e−7, −4e−9], 63-day [−2.6e−7, +1.1e−8], 126-day
[−2.7e−7, +2.4e−8]. By stage: −1.0e−7 / −2.1e−7 / +4.8e−9 (discovery / validation / audit).
B0 and B05 books: −1.2% and −1.1% of mean H_raw, ranges include zero.

Calibration (slope of g − p·m on m, HAC10 95%):

| Book | Raw-beta prediction | Corrected-beta prediction |
|---|---|---|
| V2 | +0.047 [+0.037, +0.056] | −0.022 [−0.032, −0.013] |
| B0 | +0.033 [+0.025, +0.042] | −0.014 [−0.023, −0.005] |
| B05 | +0.033 [+0.024, +0.042] | −0.014 [−0.022, −0.005] |

Reading: the annual correction lowers next-day hedge error slightly (sign as predicted;
significant only at 21-day blocks; nothing in the last period) and **over-corrects**: raw betas
leave positive residual exposure, corrected betas leave negative. Per the reviewer's rule, no
offset is fitted to this; a new estimator would need its own frozen rule learned from matured
portfolio outcomes.

## §3 Raw-risk reconstruction (B05 primary; V2 and B0 invariance controls)

- The joint moment's factor block reproduces the engine's F exactly (max difference 0).
- V2 and B0: added market terms are exactly zero (their policy beta is zero), as required.
- B05: mean loss(raw) − loss(residual) = **−0.0022**; 95% ranges [−0.013, +0.007] (21),
  [−0.015, +0.010] (63), [−0.018, +0.012] (126); stages +0.005 / −0.037 / +0.027.
  Added terms relative to the residual-only prediction: market square +5.8%, factor–market
  cross +0.9%. Calibration (realized g² / predicted): 1.031 residual-only, 0.988 raw.
- **The residual–market remainder outside the factor span is material**: 2p·w'E[u m] averages
  −9.3% of the residual-only prediction (|·| 9.3%), larger than the added terms and of opposite
  sign. The low-rank raw reconstruction is therefore not a complete raw-risk model.

## Disposition (reviewer §4)

The quantities are small or not reliably predictive: about 2% lower next-day hedge error with
a level overshoot, and an insignificant risk-score change with a material unmodelled
remainder. **The beta-control branch is closed.** V2 remains the candidate. No new policy was run.

## Ceiling (`results/ceiling.json`)

Bias-corrected hindsight maximum Sharpe of the daily characteristic factor returns, before
costs, constant premia: 27 factors 1.46; 26 characteristic factors 1.30; 13 linear 1.03.
V2: 1.29 gross (1.24 net), and a full-sample market-residual Sharpe of 1.08. **Under constant
premia, V2 already captures most of what these directions support.** Sub-period ceilings are
higher (first/second half 1.18 / 2.02), consistent with moving premia but noisy at k = 27.

## Adaptive premium memory (`results/adaptive_gate.json`): rejected at gate 1

Stable premium plus a learned one-year deviation: mean one-step squared error +1.96e−9
against 3.49e−4 for V2's learner (ranges symmetric around zero), so the forecast gate fails
and no policy run follows. κ is learned at mean 0.18, rising to 0.46 by the end. Its
forecasts pass the altered-future check. Both learners have slightly negative out-of-sample
R² (≈ −1e−5): their magnitudes are too large for the noise, so squared error mostly measures
scale calibration. A ranking-based gate would be a new, separately frozen experiment.
