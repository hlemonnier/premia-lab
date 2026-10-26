# C05/C06: covariance-weighted alpha learning — specification before implementation

**Initial state:** this document is written before `gls_precision.py`, `strategy_gls.py` or `strategy_gls_factor.py` exists. C05 and C06 are reserved by the lead before their results. C01–C04 source and configurations remain unchanged. Numerical isolation, where needed for the new Woodbury precision helper, follows a separate failure plan and executable verifier written before that helper.

## Hypothesis, evidence and controlled contrasts

The first four complete discovery configurations produced net Sharpes approximately 0.622, 0.638, 0.107 and 0.654. Faster adaptation was poor before costs as well as after them. The portfolio factor model changed return and volatility, with only a modest net-Sharpe gain. These observations do **not** establish that coefficient changes are real regimes or that latent common shocks are their cause.

The next hypothesis is that common residual return shocks, correlated with characteristic exposures, make ordinary pooled coefficient estimation noisy. A causal covariance-weighted fit can downweight cross-sectional return directions with substantial shared noise. It may instead suppress genuine predictable directions, or amplify covariance-estimation error. The experiment tests the net consequence rather than assuming the explanation is true.

- **C05 versus C02:** change only alpha learning from equal stock weighting to the specified covariance precision weighting. Keep the additive design, beta-residual label, half-life 252, ridge 0.1, warm-up 126, and the complete C02 diagonal portfolio unchanged.
- **C06 versus C05:** use exactly the same C05 forecasts with the already specified C04 factor portfolio. This exposes the interaction between coefficient estimation and portfolio risk while separating it from the first learning contrast.

Only the permitted discovery input rows `[0,2016)` may be scored now, using the original unchanged scorer and its exact 1,762-day output window. The lead controls admission and economic execution. No validation/audit or additional parameter grid is authorized by this plan.

## Exact learner configuration

The complete C02 controls are inherited without modification. Three new fixed learner controls are:

| Parameter | C05 and C06 |
|---|---:|
| `learning_factor_rank` | 10 |
| `learning_factor_shrinkage` | 0.5 |
| `learning_factor_refresh_days` | 21 |

The covariance history length is the existing `risk_window=252`. The first fit waits for the existing `risk_min_days=20`. C06 additionally carries the unchanged C04 portfolio parameters `factor_rank=10`, `factor_shrinkage=0.5`, `factor_refresh_days=21`.

The first learner factor fit occurs when the **prior-label history** has length 20, then 41, 62 and so on. Before 20 rows, use diagonal precision only. This startup choice was accepted by the lead before implementation/results and preserves all 126 matured pairs and first active forecast row **127**. There is no new training start or warm-up exclusion.

## Information clock and local covariance state

For forecast row `t`, let label day `j=t-1`. Construct the existing additive basis from `X[j-1]`, and label `y_j = R[j] - beta_before_j * mean(R[j])`. Both beta and the learner covariance use only `R[:j]`; neither may use the return being weighted. Predict from `X[t-1]`.

At each label date, obtain the same raw trailing market beta and positive shrunk residual marginal variances as the base candidate, using the prior-label history. At each scheduled learner factor refresh, center the same trailing window, remove that window's market component and divide each residual stock column by `sqrt(max(raw_variance,1e-6))`. This exactly follows C04's residual-correlation model. Retain the top ten positive eigencomponents and half their covariance, with row energy bounded by 0.5.

Store only correlation loadings in a cache **local to this forecast invocation**. At each subsequent label date, rescale them by the square root of that date's current causal marginal variances. Set `B` to these rescaled factors and `D = current_variance - row_sum(B**2)`. The positive diagonal remainder and `B B.T` therefore sum to exactly the parent marginal variances on every label date. Before the first refresh, `B` has zero columns and `D` is the base variance vector.

The learner never calls the portfolio wrapper's `rebalance`, never fills its global factor cache, and does not publish fitted coefficients or covariance objects for later `rebalance` use. Repeated forecasts initialize all local moments and factors afresh. A small local factor-estimation function may repeat the already reviewed C04 construction with explicit arguments to avoid borrowing a module's mutable portfolio configuration or cache.

## Precision weighting and ridge scale

With `Sigma = diag(D) + B B.T`, apply Woodbury:

`P Z = D^-1 Z - (D^-1 B) solve(I + B.T D^-1 B, B.T D^-1 Z)`.

The mean diagonal of precision is

`pbar = mean(D^-1 - row_sum((D^-1 B) * solve(I+B.T D^-1 B, (D^-1 B).T).T))`.

Divide the application by this strictly positive scalar: `P_normalized = P / pbar`. Hence the normalized precision has mean diagonal one. This does not make each characteristic's weighted Gram diagonal one; it fixes the overall observation-weight scale so the inherited ridge coefficient 0.1 has a comparable meaning. In the equal-variance/no-factor case, the normalized precision is exactly the identity.

Apply this single precision to the joint matrix `[Phi, y]`, then update:

`G <- decay*G + Phi.T @ (P_normalized @ Phi) / n`

`b <- decay*b + Phi.T @ (P_normalized @ y) / n`

`mass <- decay*mass + 1`.

Symmetrize each weighted Gram contribution to remove only floating-point skew. Keep the same normalized ridge solve `solve(G/mass + 0.1*I, b/mass)`. Do not change the feature centering, add an intercept, reselect terms, or residualize the label using its newly observed day's beta. Both design and label receive the same precision, not just a return rescale.

The model deliberately retains C02's zero residual intercept assumption. Ordinary cross-sectional centering is **not** precision-weighted centering; a weighted-intercept nuisance projection would change the estimator again. We do not silently apply it in this first controlled contrast. This retained assumption is a limitation to report, not evidence that an intercept has already been estimated or eliminated under the GLS metric.

The new helper API is `normalized_precision_apply(diagonal, factors, values) -> (weighted_values, mean_precision)`, with values either an n-vector or an n-by-p matrix. It has no market access or state, does not mutate inputs, supports no factors and rank-deficient factors, rejects invalid/degenerate arithmetic, and reports the scalar normalization used.

## Failure modes and observable expectations fixed before new code

1. **Precision algebra/sign mistake:** the separate preregistered helper verifier compares against an independent dense covariance solve and its precision diagonal, with zero/rank-deficient factors, rotations and scale invariance. Tests and concrete tolerances must exist before the helper implementation.
2. **Weighting only one side:** source review verifies the identical normalized precision acts on both the design and target, with one daily EW mass; the full portfolio workflow retains the original scorer and accounting.
3. **Changed ridge magnitude:** return and record the positive mean-precision scalar inside the helper; verify against dense reference. Normalization is by precision diagonal mean, not by mean covariance or an arbitrary eigenvalue.
4. **Label-day leakage:** factor estimation, beta removal and daily marginal variances for label `j` must use exactly the prior prefix `R[:j]`. Future-alteration checks cover the first local factor fit, an update, a nonupdate and later eviction. Factor fits at label j=20/41 first influence forecast rows 21/42; model output remains zero until row127.
5. **Portfolio state contamination:** forecast caches remain local. C05 delegates only the base diagonal portfolio; C06 delegates C04 portfolio initialization from actual rebalance prefixes. Fresh-process configured replays and source inspection cover both wrappers separately.
6. **Startup or total-length dependency:** diagonal before20 prior rows, factor schedule anchored to that observed count, first active forecast127. Appending/truncating input cannot shift the historical schedule. No fit to a fixed number of future warm-up observations.
7. **Nonpositive covariance or unstable inversion:** daily factor rescaling preserves parent variances and leaves at least half in D; the helper rejects nonpositive/nonfinite D, invalid shapes and unrepresentable intermediate arithmetic. Do not silently relabel an invalid precision as an ordinary fit.
8. **Input mutation or hidden state:** read-only input arrays and before/after identities remain intact. Configure resets research settings from defaults; unknown keys fail. No file reads, external model assets or returned future caches.
9. **Numerical fallback obscures economic inference:** forecast precision/fit errors fail the run. C06 retains only the previously declared factor-portfolio convergence fallback, with unchanged diagnostics. No new learner fallback is introduced.
10. **Runtime/state growth:** EW learner matrices and local trailing factor state have fixed dimensions; output predictions grow linearly with history length as required by the interface. Measure complete forecast and rebalance paths. Extrapolating a short sample is not a century-long execution.

The custom precision helper receives preimplementation numerical references. Subsequent strategy verification uses full original-scorer E2E workflows and independent source review; no postimplementation unit cases are added.

## Evaluation and interpretation

Retain the original daily gross and net results, costs, beta, fixed blocks, drawdown, turnover, concentration, gross-scaling frequency and timing. For C05, portfolio code/configuration equality with C02 is part of the controlled contrast. For C06, equality of its forecast array with C05 is expected and can be checked from the already executed complete-run artifacts without fitting another candidate.

Improvement in discovery net Sharpe would support carrying the covariance-weighted learner forward; it would not prove the hypothesized contamination mechanism or hidden-future generalization. A failure to improve is preserved and argues against additional complexity. A strong gross gain lost after costs points to an implementation/turnover question; no gain before costs argues against this forecast hypothesis. No thresholds are altered to call a preferred method successful. Selection and protected periods remain governed by the original frozen protocol.

## Attribution

The hypothesis, causal design, implementation and comparisons are AI work under the user's research instruction. The applicant's personal discoveries or judgments are not invented. The current result is a prospective experimental specification, not an empirical finding that GLS improves performance.
