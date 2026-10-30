# First causal alpha candidates — specification before implementation

**State at creation:** no `submission/strategy.py` implementation or scored candidate run exists. This specification is fixed before that implementation. The lead accepted these shared controls before any candidate score. It consumes two complete discovery configuration slots when C01 and C02 are first scored, not when descriptive code is read.

## Question and evidence

Can an adaptive, regularized joint model turn the discovery characteristics into positive net returns under an explicit market hedge and trading costs? Does a restrained additive curvature basis improve on the linear benchmark with the same fitting and portfolio policy?

The existing discovery evidence supports adaptation because several linear associations change sign. It supports a curvature challenger because predefined tail-versus-center contrasts for Snap, Crackle and Pop were negative in each fixed two-year block, while shorter intervals remained noisy. Both models retain **all thirteen** characteristics; the challenger adds the same square transformation to every characteristic. We do not hand-select the attractive univariate features or hard-code past regime dates.

Only discovery rows `[0,2016)` may be scored during this phase. No validation/audit data or full-sample figures are inputs to these choices. Economic comparisons must use the unmodified scorer, full actual costs and continuous holdings, under `RESEARCH_PROTOCOL.json`.

## Frozen candidates and shared parameters

| Setting | C01 | C02 |
|---|---:|---:|
| Basis | 13 linear terms | Same 13 linear plus 13 centered squares |
| EW learning half-life | 252 days | 252 days |
| Ridge coefficient on normalized moments | 0.1 | 0.1 |
| Minimum matured training days | 126 | 126 |
| Standardized feature clipping | ±4 | ±4 |
| Trailing risk window | 252 days | 252 days |
| Minimum history for stock-beta regression | 20 days | 20 days |
| Residual-variance shrinkage to current stock median | 20% | 20% |
| Absolute daily variance floor | 0.000001 | 0.000001 |
| Risk aversion | 1,000 | 1,000 |
| Cost amortization horizon | 20 days | 20 days |
| Absolute per-stock weight cap | 0.01 | 0.01 |
| Gross exposure cap | 1.0 | 1.0 |

These are first engineering hypotheses, not selected optima. In particular, risk aversion is intentionally large enough to avoid habitual use of a postsolve gross rescale. The observed frequency and amount of that rescale must be reported. Any change selected because of scores consumes another full pipeline slot before its score is inspected.

## Exact information clock and basis

For forecast row `t`, predict from the characteristic panel `X[t-1]`. The latest completed training pair is `X[t-2] -> R[t-1]`. The market beta used to residualize the label `R[j]` is estimated from `R[:j]`, which excludes the label day. The training label is `R[j] - beta_before_j * mean(R[j])`.

Each panel is transformed independently using only that panel. For each characteristic, subtract its cross-sectional mean and divide by its population standard deviation, with a `1e-12` scale floor for constant columns. Clip the standardized value to `[-4,4]`, then subtract its cross-sectional mean again. These are the linear terms. For C02, also form each linear term's square, subtract that square's cross-sectional mean and divide by `sqrt(2)`. The last scale is fixed, not estimated from future data; it is the standard deviation of a squared standard normal variable. Since the linear term is bounded after clipping and recentering, its square is bounded as well. No full-history normalization or fitted feature selection occurs.

For each matured date with `n` stocks, update `G <- decay * G + Phi.T @ Phi / n`, `b <- decay * b + Phi.T @ y / n`, and `mass <- decay * mass + 1`, where `decay = 2**(-1/252)`. Fit `theta = solve(G / mass + 0.1 * I, b / mass)` once at each forecast date after 126 matured daily pairs. Normalize **both** moments by the same mass; this keeps the intended ridge strength stable during warm-up. No intercept is needed because every design column is centered. The first active forecast is row **127**. Earlier forecasts are exactly zero.

All learned matrices and coefficients are local to a single `forecast` invocation. Forecast does not leave a trained risk object, coefficients or future-dependent cache for `rebalance` to consume. Appending or altering future rows must leave all protected forecasts and targets unchanged.

## Causal risk and portfolio controls

`estimate_risk(returns_history)` is pure. It reads at most the final 252 already-observed rows, demeans stock and equal-weight market returns through that point, and obtains the centered OLS stock beta. Beta is not shrunk toward one. With fewer than 20 observed rows, or market variance at most `1e-12`, use beta one. This early fallback is used only for training-label residualization during initial warm-up in the ordinary scoring path. Empty history uses beta one and a 0.0004 diagonal variance prior; a nonempty fallback window uses its measured centered stock variances.

Residual variance is the population variance of centered stock returns minus the fitted beta times centered market returns. Shrink each stock variance by 20% toward the current cross-stock median, then apply the fixed `1e-6` floor. With the beta-one fallback, the same market-subtracted residual definition applies. Risk is recomputed daily; no hidden state is necessary. First regression occurs at 20 observed rows. A trailing-window eviction first occurs at 253 observed rows.

`rebalance` uses the existing, independently reviewed `portfolio.allocate` objective:

`mu @ w - 0.5 * gamma * sum(variance * w**2) - sum((cost / horizon) * abs(w - held))`

subject to the exact estimated-beta equality and absolute stock bounds. The supplied `held_positions` are already drifted; use them directly. The cost amortization is a control approximation only. The official scorer always charges the full per-stock one-way cost on the actual trade. Proportionally shrink the solved vector only if its gross exceeds 1.0. This preserves beta equality and stock bounds but generally is **not** the exact optimum with a gross constraint and can disrupt no-trade behavior. Report that limitation and the frequency of scaling.

A read-only `get_last_diagnostics()` may expose the most recent pre-scale gross, scaling factor, cap saturation, predicted alpha and estimated-beta exposure. This diagnostic state is never read by `forecast` or `rebalance`. It is not a predictive input or fitted cache.

## Failure modes and expected E2E outcomes fixed before code

1. **Same-day information or future normalization:** altered futures and prefix/append replays must match the boundaries in `verification/CAUSALITY_PLAN.md`. Add the first-active row 127, raw-beta start boundaries 20/21, first-earned target row 253 and trailing-risk eviction boundaries 253/254 before runs.
2. **Incorrect training age or ridge normalization:** source review must verify that the update ends at the latest matured pair, that both moment arrays use the same EW mass and that zero forecasts persist before row 127. Do not infer this merely from an attractive score.
3. **Correlated feature singularity:** a strictly positive ridge must keep the coefficient solve defined for constant or duplicated feature columns. Constant cross-sectional features transform to zero without nonfinite values.
4. **Risk singularity:** insufficient or zero-market-variance history takes the declared beta-one fallback; constant residuals receive the fixed positive variance floor. No division by zero or future calibration.
5. **Invalid data/configuration:** reject wrong shapes, nonfinite consumed panels, negative/nonfinite costs, invalid finite bounds and unknown configuration keys. Do not silently ignore misspelled controls. `configure` sets the same defaults plus the explicit JSON values and clears diagnostic state; it does not fit anything.
6. **Position/cost mistakes:** existing discovery E2E must confirm correct weight shapes, finite values, requested caps, drift-aware full fees, and exact scorer row counts. Report estimated beta neutrality separately from realized net beta.
7. **Scaling masks a failed allocator:** preserve pre-scale gross and scale factors. Do not describe a frequently rescaled diagonal solution as a directly constrained optimum. Exceptions propagate as failed executions, not silent cash success.
8. **State or input mutation:** inputs remain unchanged, fresh-process repeat outputs match, and `forecast` local estimates cannot influence later `rebalance` except via its selected forecast row.
9. **Runtime growth:** fixed-dimensional EW moments and trailing risk windows imply constant work per date apart from the required forecast output array. Measure actual calls; short-prefix extrapolation does not establish a completed century run.

Verification uses the already specified full scorer workflows and independent source review. No isolated unit tests are introduced after the candidate implementation. The custom allocator's prior test-before-implementation evidence remains separately preserved.

## Evaluation and stopping rule

Compare C01 and C02 on discovery daily **net Sharpe**, with fixed-block returns, costs, beta, turnover, concentration and timing retained. A negative score is a valid research outcome, not a harness failure. Neither family is accepted for final delivery from discovery results alone. C02 earns further investigation if its added basis improves net performance without a correctness failure; instability, gross-to-net erosion or beta violations determine the next bounded question rather than an unrecorded parameter search. Validation selection remains the frozen pooled-net-Sharpe rule.

## Attribution and status

The candidate design and implementation are AI work conducted under the user's request for disciplined autonomous research. No personal empirical discovery is attributed to the applicant. Initial plans, diagnostics and independent review motivated the two families. Candidate correctness, profitability, hidden-future generalization and long-horizon runtime are **unverified at this specification checkpoint**.
