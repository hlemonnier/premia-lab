# Independent C04 factor-portfolio source and evidence review

**Reviewer:** alpha-model agent, distinct from the factor solver and wrapper author.  
**Scope:** source derivation, covariance/cache chronology, configuration delegation, preserved build order and existing numerical evidence. No new unit cases, independent optimizer execution, market-score run or validation/audit access occurred during this review.

## Decision

**Approve C04 for its preregistered discovery E2E experiment and configured causality checks.** The mathematical formulation and causal wrapper support that next step. This is not release approval or evidence that C04 improves returns, meets full-strategy runtime, remains causal under every intervention, or generalizes to the hidden continuation.

One generic helper issue was found in review and corrected before this approval: beta normalization included fixed-zero-cap stocks, allowing an irrelevant extreme beta to overflow and contaminate the Hessian. The author now normalizes only movable stocks, matching the existing diagonal solver. C04's fixed positive scalar cap could not trigger that particular path. The unchanged preimplementation verifier then passed again in `evidence/factor_verify_002/`.

Reviewed current solver SHA-256: `60af66f9797585fec4189206c50481bfd1d3554beb6442ed5c19b2399ce375e5`. The current source exactly matches the solver snapshot used by that second numerical run. Reviewed wrapper SHA-256: `9e63257c14859430b5190763c5f1fd35320c582019c941ae28b43243587a4959`.

## 1. Reduced dual is consistent with the stated primal objective

Let `L = sqrt(gamma) * B`, `Q = gamma * D` and `p = costs / horizon`. The primal maximizes

`mu @ w - 0.5 * w @ diag(Q) @ w - p @ abs(w-held) - 0.5 * ||L.T @ w||^2`

under the original stock boxes and beta equality. The implementation minimizes the convex reduced dual

`f(u) = 0.5 * u @ u + max_feasible_w ((mu-L@u)@w - 0.5*Q@(w*w) - p@abs(w-held))`.

Its gradient is correctly `u - L.T @ w(u)`. Each inner problem is the existing beta-constrained diagonal solver, so trial iterates remain box- and beta-feasible. At the fixed convergence tolerance, the factor dual is consistent with its inner primal solution; the code does not return an unconverged iterate as a successful exact solution.

Within an active quadratic segment, the inner response is the inverse diagonal on trading, unboxed coordinates, projected onto the beta equality. Thus the implemented Hessian

`I + L.T @ diag(inverse) @ L - outer(L.T@inverse_beta, L.T@inverse_beta)/(beta@inverse_beta)`

is the correct segment Hessian when the denominator is positive. With no active beta direction, the projection term vanishes. At the nonsmooth boundaries this selects a segment/generalized Hessian; backtracking checks the actual dual value. The fallback descent direction is the negative gradient. The explicit floating-point allowance in line search is a rounding allowance, while convergence still requires the fixed dual-gradient residual.

The new solver uses the full drifted held vector in its L1 cost term and retains stock-specific costs. It does not replace actual evaluator fees with the amortized optimizer penalty.

## 2. Factor construction preserves the intended marginal variances

At refresh, the wrapper reads only the supplied trailing observed window, centers stock and market returns, and removes the current window's market component. Dividing each residual column by `sqrt(max(raw_variance, variance_floor))` makes the empirical correlation diagonal at most one.

For the observation Gram matrix `Z @ Z.T / T`, the retained eigenvectors `V` give stock loadings `Z.T @ V * sqrt(shrinkage/T)`. This is algebraically the retained covariance factor: it already contains the square roots of the nonzero eigenvalues and does not require division by tiny eigenvalues. The code keeps positive eigenvalues only.

The retained row energy is at most the configured shrinkage, here 0.5. The numerical clipping enforces that upper bound. On subsequent days, multiplying those correlation loadings by the square root of the current parent's marginal variances and setting `D = parent_variance - row_sum(B**2)` preserves the parent's complete covariance diagonal. The diagonal remainder is at least half the positive parent variance. It avoids combining stale absolute factor variance with a newly smaller marginal variance.

This is a shrunk common-risk model, not a claim that the first ten factors capture all covariance or are stable alpha-free directions. Unlike a hard factor neutrality constraint, the risk penalty may retain an exposure if its forecast pays for it.

## 3. Chronology and state

`forecast` delegates to the base learner and does not populate the factor cache. Only `rebalance` estimates factors, using its causal history prefix. Under the scorer's default start, the first target has history length 253 and initializes the cache; the next scheduled refreshes occur at lengths 274, 295 and so on. Intervening days use the last already-observed factor loading matrix and current causal marginal variances and beta.

`configure` validates the factor controls, delegates all remaining controls to the base's strict configuration validator, and resets factor and diagnostic state. Unknown nonfactor keys are therefore rejected by the base. C04's explicit configuration preserves C02's additive basis and forecasting knobs. A nonincreasing history length also clears the cache, allowing the prescribed scorer to restart from its common initialization. No future numeric file access or full-history risk initializer appears in the new files.

The fixed default start remains an assumption of this wrapper's refresh anchor. Source review does not establish arbitrary call-order equivalence outside the supplied scorer contract. Configured future-alteration replays must cover initialization, a nonrefresh close, a refresh boundary and a later refresh/window boundary.

## 4. Build order and numerical evidence

The preserved records show the plan at `19:39:52 UTC`, the complete executable verifier at `19:40:55 UTC`, the absent-module red run at `19:40:59 UTC`, and the first solver/wrapper snapshot at `19:42:06 UTC`. The red run failed because the new solver did not exist; it correctly reports no numerical checks executed.

The verifier's SHA-256 is identical in its preimplementation snapshot, red run, both passing runs and current source:

`f510519c06aa8fe243505f1600885721357bc6acb8904c894280a0c1b60a1684`.

I inspected its reference formulation: the small constrained reference uses a primal epigraph problem with an independently assembled dense covariance and SciPy SLSQP; no factor-dual implementation is reused by that oracle. The zero-cost KKT reference and constructed 1,000-stock KKT solution provide separate objective/weight checks. Repeat and input-immutability checks are present. This is appropriate numerical coverage for the new algorithm, with the original diagonal implementation reused rather than assigned new postimplementation unit tests.

Both completed numerical runs record **73 passing checks**, zero failed checks and exit code zero. After the review correction, run 002 records a 15.11 ms mean, 19.02 ms p95 and 20.29 ms maximum over eight synthetic 1,000-stock solver calls on the recorded single-core setup. These timings cover the numerical component, not the full strategy, factor estimation or long-history execution. The earlier 11.87 ms measurement is preserved rather than silently replaced.

## 5. Remaining full-workflow gates

The next original-scorer run must retain full actual costs, estimated and realized beta, all fixed discovery blocks, raw and rescaled gross, factor refresh ages, covariance-diagonal error and fallback count. Any convergence `RuntimeError` in the factor solver triggers the declared diagonal fallback and must remain visible. Invalid inputs are not caught as a successful fallback. Routine fallback would undermine the intended C04 comparison even if the run completes.

The gross rescale remains inherited from C02: it preserves the hedge and boxes but does not solve the exact gross-constrained factor objective and may disrupt the no-trade region. Its frequency must be measured. Full-strategy runtime must include periodic factor estimation. C04 cannot inherit C02's empirical causality status merely because its forecast delegates to C02; its causal state and allocation path require their own evidence.

No market performance or later-period conclusion is drawn by this review.
