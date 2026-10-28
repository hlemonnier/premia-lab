# Corrections to earlier V2 claims

28 October 2026. Adopted from `reviews/V2_FOLLOWUP_INDEPENDENT_REVIEW_20261028.md` and
`research/v2/REVIEWER_NEXT_DECISION_20261028.md` §1. These supersede wording in
`REVIEW_FOLLOWUP_20261028.md` and `EXPLICIT_BETA_RESULTS.md`; the original files are left
unchanged as a record.

| Earlier claim (Claude) | Corrected statement |
|---|---|
| Centering the risk columns and residuals makes the beta-error exposure invisible to the 26-column model | Wrong. With an equal-weight market and one OLS window, mean(bhat) = 1 and the residuals are already centered; the beta-error loading η(1 − bhat) is itself centered and survives. What holds: about 93% of the beta column's squared norm lies outside the 26-column span, so that common direction is largely unrepresented by the factors. Specific risk captures some of it per stock, not its common covariance. |
| True betas drift about 17% toward one | Shrinkage improves forecasts of noisy next-year beta *estimates* in this sample. A slope below one also arises with constant latent betas and measurement noise; drift and noise are not separated. |
| The market regression shows there is no low-beta premium | Strong market loading is detected (t ≈ −20); the intercept is unresolved (95% ≈ [−0.37, +0.16] bp/day). The zero-alpha simulation shows a possible channel, not the generator. |
| The pure stock-selection edge is about 1.1 Sharpe | A full-sample market-residual series has Sharpe 1.08–1.10. No costed, causal market-neutral policy at that level has been shown (B0, the causal neutral attempt, scored 1.044). |
| Market exposure is now controlled precisely | The target increment is reproduced almost one for one (B05 − B0: beta +0.050, market R² 0.999); both corrected books sit about 0.014 below their absolute targets, within the ±0.02 tolerance. |
| B05 is a statistical tie with V2 | The difference (−0.012, 95% ≈ [−0.11, +0.08]) is unresolved; equivalence needs a margin fixed in advance. B05 fails the point-estimate rule. |
| "Corrected betas win on 97% of dates" | 139/144 overlapping dates (adjacent windows share 231 days): a descriptive frequency, not 144 independent successes. |
| The matched-diagonal control shows the gain comes from correlations | It shows the historical effect of removing correlations at the same penalty (0.938); it does not separate correlation geometry from the resulting sizing, cost and cap changes. |
