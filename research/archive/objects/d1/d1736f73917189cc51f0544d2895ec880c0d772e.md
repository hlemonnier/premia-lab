# GLS implementation review

## Scope and independence

Reviewed the frozen original GLS implementation (blob f26b3c5b8c8578525af7db19f01898140b9b7fc7), F payload, risk-state update and original scorer. All baseline source blobs and original data/scorer hashes match the previous evidence. This is a same-session source review with separately written dense covariance and cashflow implementations. No independent person or separate reviewer agent is claimed.

## Information flow

For output target t, the newest regression label is u=t-1. The regression design is X[u-1] plus beta[u], where beta[u] uses return rows strictly before u. The risk state absorbs only through u-1. F's multiplier baseline[u] also uses only information available before u. Thus the label's precision matrix is predictable: it does not observe the label-day return before choosing that label's weight. Prediction uses X[t-1] and beta[t]. All learner and policy state is reinitialized per forecast session.

The F covariance calculation may be applied to all source dates in advance, but its per-row computation and training manifests remain causal. Source code and altered-future tests check row dependencies; merely computing an entire tensor in one function does not itself establish or violate causality.

## Exact objective and intercept meaning

For each day u, let D_u denote the27-column design, y_u the market-residual return and W_u the inverse lagged covariance. The profiled day-level precision is

    P_u = W_u - (W_u 1)(1' W_u)/(1' W_u 1).

The learner accumulates EW sufficient statistics G=sum(weight*D'P D/N)/mass and h=sum(weight*D'P y/N)/mass, then solves (G+Lambda)theta=h. The intercept is a separate nuisance intercept for each historical cross-section. It is not one pooled intercept, is not added to the forecast and is not a market-timing alpha. The fast/slow coefficients and50/50 F2 blend are frozen.

The low-rank precision action follows Woodbury with covariance diag(d)+M M'. Division of the allocation factor L by sqrt(0.3) removes the allocation-specific discount and recovers the estimated noise covariance. All specific variances are positive via the frozen floor; the covariance is positive definite even when factor loadings are rank deficient.

The diagonal-relative penalty0.1*diag(G) and trace-scaled penalty0.1*trace(G)/27*I have the same total penalty trace at a fixed positive G, but distribute it differently across coefficients. Both are invariant to a common positive rescaling of the complete weighted loss. Comparing full-dimensional precision against an absolute0.1*I without normalization would confound covariance units with regularization strength; that misleading comparison is deliberately absent.

## Why this is feasible GLS, not a free efficiency guarantee

The covariance is estimated, factor premia may drift, and its residual model may be misspecified. The weighting changes both cross-sectional directions and the relative influence of dates with different forecast noise. No assumption that all stock-days are independent is used for uncertainty; complete daily vectors are resampled. The D_D control removes the entire factor-risk component, including its diagonal contribution. Therefore G_D minus D_D is NOT a pure off-diagonal-correlation ablation. No matched-total-diagonal control was registered or added after results.

## Numerical exception

The separate dense implementation rebuilds betas, characteristic bases and EW covariance moments rather than calling the GLS statistics code. Raw forecast difference is below8e-19. At the original solver's finite stopping accuracy, two1e-10 cross-implementation portfolio comparisons fail by a few1e-10. Tightening the Newton gradient alone does not eliminate the line-search/active-set path sensitivity. These failed receipts are preserved.

A verification-only dense primal KKT refinement keeps the objective and test tolerances unchanged and brings forecast, position and economic comparisons within the frozen tolerances. It is applied symmetrically to the oracle and GLS in the diagnostic only. All empirical scores and normal causal checks use the original unmodified allocator. Neither the default failed comparisons nor the tightened-only failed comparisons are relabeled passed.

## Findings

No lookahead or algebraic defect was found in the inspected original GLS path. This conclusion is limited to source review and executed checks. A predicted covariance is not automatically the true noise covariance; causality does not rule out research selection overfit. Contribution attribution must be based on the fixed matched contrasts, not only on the higher score of original GLS versus F. Main and the original GLS source remain unchanged.
