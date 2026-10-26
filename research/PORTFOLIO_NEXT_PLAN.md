# Portfolio research: next bounded experiment

**Status:** proposed design, written before implementation or candidate scoring. No new pipeline slot is consumed or authorized by this document. The lead must assign a slot and freeze the exact configuration before an economic run. Existing discovery evidence is the only empirical input to this proposal; actual validation/audit rows remain unopened.

## C04 authorization and exact design freeze

The lead subsequently authorized implementation as **C04**, paired against C02 additive half-life252. No C04 economic execution is authorized until the lead freezes its record. C03 is separately reserved for the faster alpha-adaptation contrast. The following details replace the open covariance convention below before new optimizer code, tests or results:

- Estimate rank10 on the trailing252 **market-residual correlation** matrix at earning-day253 and then every21 closes (274,295,...). Center and market-residualize using that observed window; divide each residual column by `sqrt(max(raw variance,1e-6))`. This makes the empirical diagonal at most one.
- Keep0.5 times the leading factor covariance. Store correlation-factor loadings, with row energy at most0.5 (clip only numerical excess). Rescale those loadings each day by the square root of the parent's current shrunk variance. Set the diagonal remainder to current parent variance minus the factor diagonal. The total covariance diagonal is therefore exactly the parent's, and its remainder is at least half that variance. This resolves stale covariance/current variance incompatibility without changing C02's variance schedule.
- Implement a new reduced factor-dual optimizer using the unchanged existing beta-constrained diagonal allocator as its inner solve. A semismooth Newton direction uses the active quadratic coordinates and their beta projection; backtracking verifies descent. The optimized problem is the declared factor-risk/L1/box/beta objective. Fixed maximum80 factor iterations; fixed dual-gradient tolerance `1e-11*(1+max(abs(dual)))`.
- Reset the wrapper's causal factor cache on `configure`; never fill it from full-history `forecast`. The wrapper delegates the unmodified C02 alpha learning and parent risk estimator. Only `rebalance` populates the factor cache from its observed prefix.
- A numerical convergence `RuntimeError` in the factor optimizer triggers the existing diagonal allocator for that close, with `factor_fallback=1` recorded. Invalid inputs are not silently replaced. Any fallback frequency is reported; a routine fallback is evidence against admitting C04.
- No postimplementation unit tests are added to the original allocator. A new factor numerical verifier, with all concrete fixtures and tolerances, is written and snapshotted before `factor_portfolio.py` or `strategy_factor.py` exists; the first run must fail because the new solver is absent. The full strategy remains subject to the original scorer, causality, accounting, and timing workflows.

The refined normalization is an engineering decision made before any C04 results. It keeps the approved rank, shrinkage, window and refresh budget while preserving the comparison's marginal variances.

## Current decision

Run the common diagonal-risk policy with C01/C02 first. Its purpose is to establish whether joint adaptive characteristic forecasts can produce useful returns after full costs under estimated market neutrality. Do not mix the first alpha-family contrast with a changed hedge or risk model.

If the first comparison produces a viable alpha forecast, the next portfolio challenger should address **residual common risk**. Discovery risk diagnostics record material covariance after market removal: the leading ten components explain 21.33% of pooled residual variance, while the mean absolute off-diagonal correlation is 0.0626. These pooled retrospective statistics justify testing covariance structure; they do not estimate a causal trading risk model or select a rank. Sources: `research/RISK_FINDINGS.md`, `evidence/risk_diagnostics_001/summary.json`.

## What must be measured in the first two runs

In addition to the original scorer's net Sharpe, beta, full fees and runtime, record:

- Estimated beta exposure before and after any gross scaling.
- Allocator gross before scaling, actual gross, scale factor, and fraction of calls on which scaling binds.
- Fraction of stocks at their pre-scaling box bound; number of names traded and absolute turnover.
- Continuous daily ledger and fixed discovery-block summaries.

These are interpretations of the same executed configuration, not permission for an undisclosed parameter search. If scaling binds often, the statement that the strategy preserves the allocator's no-trade region must be withdrawn: rescaling generally moves holdings even when the unconstrained solution preserves them.

## Proposed complete-pipeline challenger: common-risk penalty

The lead chooses the parent alpha configuration using the already-recorded discovery evidence and registers that choice explicitly. The challenger changes only the risk model/optimizer needed to use it. Keep the feature basis, alpha learning, lag, beta lookback, cost horizon, risk aversion, stock cap, gross policy and official accounting identical. A selectable changed pipeline consumes one of the twelve configurations.

Proposed initial constants, selected as a compact engineering hypothesis rather than fitted to a future result:

| Quantity | Fixed proposal |
|---|---:|
| Market-beta/residual window | 252 observed days |
| Residual factor rank | 10, capped by available matrix rank |
| Factor refresh interval | 21 closes, anchored to first trading close |
| Retained off-diagonal covariance fraction | 0.5 |
| Marginal variance | Exactly the parent's current diagonal estimate, except an explicit positive floor |

### Causal estimation

At a refresh after close `s`, use only returns through `s`, with at most the last 252 rows. Fit centered stock regressions against the equal-weight market in that window. Let `E` be centered residual returns, `S = E.T @ E / T`, and `(U, lambda)` the largest ten nonnegative eigenpairs of `S`. Equivalent calculation through the `T x T` observation Gram matrix avoids a daily `1000 x 1000` eigendecomposition. Eigenvector signs have no economic meaning; the model consumes their covariance product.

Set `B = U * sqrt(0.5 * lambda)` and `D = v_parent - row_sum(B**2)`, where `v_parent` is the same positive, shrunk marginal residual variance used by the parent at that decision. Enforce a predeclared numerical floor on `D`. The modeled covariance is `diag(D) + B @ B.T`: it preserves the parent's marginal variance wherever the floor does not bind while introducing half of the estimated leading off-diagonal covariance. Any floor-induced diagonal difference must be reported. Use factor loadings frozen at the latest available refresh and current causal diagonal/beta estimates. If mixing daily current variances with stale factor loadings makes `D` materially negative, cap each factor row's squared norm at a fixed fraction of current variance, chosen and recorded before implementation; do not silently pass a nonpositive diagonal to the optimizer.

An alternative, cleaner first implementation is to refresh the entire covariance estimate every 21 closes while retaining daily beta hedging. If selected, that changes the variance-refresh convention and must be disclosed as part of the complete pipeline; it is not an exact one-component ablation of daily diagonal risk. The lead should choose one convention before writing the new code.

No eigensystem from pooled discovery diagnostics is used in historical decisions. A forecast call on the entire history must not leave a final risk cache for earlier `rebalance` calls. Any factor cache is reset at configuration and populated only by causal rebalance prefixes, or every historical factor is carried in its properly lagged forecast row.

### Allocation objective

Solve the finite-dimensional convex problem

`max mu @ w - gamma/2 * (sum(D*w*w) + ||B.T @ w||^2) - sum((cost/H)*abs(w-held))`

subject to the same estimated-beta equality and per-stock bounds as the parent. `held` is the scorer's actual drifted holding. `cost/H` is an optimizer control approximation; full `cost` continues to be charged by the unchanged official scorer.

Prefer a small factor-dual problem to a full daily generic QP. For factor dual variable `eta`, the existing beta-constrained diagonal allocator can solve the inner problem with adjusted alpha `mu-B@eta`. The reduced convex dual has quadratic term `||eta||^2/(2*gamma)` and gradient `eta/gamma - B.T@w(eta)`. This yields an implementation route with an independently interpretable convergence condition. It also creates a concrete runtime risk because each dual iteration calls the diagonal allocator. Measure the whole rebalance, including periodic factor refreshes. If the initial implementation cannot stay under the average runtime budget, reject it or preregister an improved numerical method before implementation; do not loosen correctness checks to meet timing.

Hard zero exposure to all selected principal components is not the default proposal. It can discard expected-return directions unnecessarily. A risk penalty directly reflects the stated Sharpe objective and allows an alpha forecast to pay for a risk exposure.

## Failure modes and verification before new optimizer code

If a new factor optimizer is implemented, the following specification precedes its tests and implementation. Reuse the existing full-strategy E2E harnesses; the new numerical algorithm warrants narrow preimplementation isolated references.

1. **Zero factors:** weights and objective match the existing diagonal allocator within declared float64 tolerance.
2. **Zero costs and inactive caps:** match the independently computed equality-constrained full-covariance KKT solution.
3. **Nonzero costs, drifted holdings, binding caps and heterogeneous beta:** match a small independent primal epigraph reference optimizer; require reference feasibility and successful termination before comparison.
4. **Sign/rotation invariance:** replacing factors by a sign flip or orthogonal rotation leaves the covariance, feasible optimum and objective unchanged to fixed tolerance.
5. **Rank deficiency/zero eigenvalues:** return finite valid weights without requiring a nonexistent inverse of factor covariance.
6. **Invalid arithmetic:** reject negative diagonal variance, malformed factors or nonfinite values explicitly; no overflow-and-clip acceptance.
7. **Convergence:** save termination code, residual/gap and iteration count. An unconverged iterate must not be labelled the exact optimum. Any deterministic fallback to the old allocator is specified before execution and counted/reported in the full run.
8. **Causality:** alter future returns and features across first factor initialization, a factor refresh, a nonrefresh close, and a later eviction boundary; historical forecasts and targets remain protected under the frozen causality plan.
9. **Complete runtime:** report mean, p95, max and refresh-only timings on one core, including every executed call. A prefix extrapolation is not a century run.
10. **Scorer fidelity and evidence:** unchanged official fees/position drift, input/source hashes, complete daily outputs, exact commands, failed-run retention and fresh-process reruns.

Before implementation, write concrete fixtures, thresholds and a failure-preserving evidence runner. Do not append new unit cases after seeing the implementation. Additional later checks should be complete E2E workflows or source review under the user's policy.

## Acceptance, interpretation and stopping

The discovery comparison reports the whole net-return series, pooled net Sharpe, all four fixed blocks, beta, cost, gross/concentration, drawdown, covariance/fallback diagnostics and measured runtime. A large gross Sharpe gain that disappears after costs is a negative result. A factor model that does not improve the complete outcome does not earn a place because covariance modeling sounds sophisticated.

This result may nominate a finalist but cannot establish hidden-continuation quality. The fixed finalist/validation selection rule remains authoritative. Do not try multiple ranks, refresh rates, shrinkages or risk windows without logging each exposure and spending the corresponding complete-pipeline slot. The proposal does not open the reserved periods.

## Remaining alpha-estimation question

An apparently time-varying characteristic coefficient can reflect changing true conditional returns, sampling noise from latent common shocks, or both. Correctly lagged pooled regression is causal but is not automatically statistically precise. A portfolio covariance improvement addresses risk after prediction; it does not prove that estimated coefficient sign changes are genuine regimes. A later generalized least-squares or risk-controlled coefficient estimator is a separate alpha-family/design question and must not be smuggled into this risk-only comparison.
