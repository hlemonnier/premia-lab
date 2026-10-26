# Independent portfolio allocator review

**Decision:** REQUEST CHANGES — one concrete numerical failure-handling defect; the declared optimizer mathematics and existing synthetic evidence otherwise support the intended normal-scale implementation.  
**Scope:** read-only review of `submission/portfolio.py`, `verification/PORTFOLIO_PLAN.md`, the frozen numerical verifier, build-order records and completed `portfolio_verify_001` artifacts.  
**No new tests were written or executed. No market outcomes were read.**

## 1. Required correction: intermediate overflow can return a wrong feasible optimum

`portfolio.py:97–103` suppresses overflow inside the scalar Lagrangian solution. Clipping an overflowed intermediate is not always equivalent to clipping the correctly computed scalar optimum, because a large transaction-cost term may cancel part of the intermediate before division. The beta check alone cannot detect the resulting error.

A concrete finite-input counterexample, derived from the code without executing a new test:

- `risk_aversion = cost_horizon = 1`
- `variances = [1e308, 5e307]`
- `expected_returns = [1.5e308, 1.7e308]`
- `betas = [1, -1]`
- `held_positions = [0, 0]`
- `trading_costs = [1.7e308, 0]`
- `weight_cap = 1.5`

All current input, scaled-risk, effective-cost, held-gradient and cap-gradient checks pass: cap gradients are `[1.5e308,7.5e307]`, both finite.

The equality requires `w1=w2=x`. For nonnegative x, the primal objective divided by `1e308` is

\[
0.75x^2-1.5x,
\]

so the unique constrained optimum is `[1,1]`; it is inside the box. Negative x cannot improve it.

Following the actual branch logic:

1. At multiplier zero, the weights are `[0,1.5]`, with normalized exposure `-1.5`.
2. The bracketing trial is `-1.7e308`, producing the opposing exposure and a bracket.
3. The first midpoint is `-8.5e307`. The first shifted alpha is mathematically `2.35e308`, which overflows. Subtracting its finite cost after overflow leaves infinity, so clipping produces `w1=1.5`.
4. The second adjusted alpha is `8.5e307`; division by `5e307` and clipping also gives `w2=1.5`.
5. Exposure is exactly zero, so the implementation returns `[1.5,1.5]`, although `[1,1]` has a strictly better primal objective.

This violates the stated policy of explicitly rejecting numerically unrepresentable derived arithmetic. It is an extreme-scale failure, not an observed issue in the supplied market or a claim that realistic candidate values reach this range.

**Requested fix:** reject unrepresentable intermediate scalar-solve arithmetic explicitly, with the documented numerical/invalid-input exception, rather than silently accepting an overflow-and-clip result. Alternatively use a demonstrably stable equivalent formula, but explicit rejection is the smaller correction consistent with the existing contract. Preserve the already-written verifier and run it unchanged after the implementation change; no post-implementation unit cases are requested.

## 2. Mathematical method: approved within representable arithmetic

For diagonal coefficients `a_i>0`, effective costs `k_i>=0` and normalized hedge vector `b`, the Lagrangian at multiplier lambda has scalar objective

\[
\tfrac12 a_i w_i^2-(\mu_i-\lambda b_i)w_i+k_i|w_i-h_i|.
\]

Its unconstrained minimizer is held weight `h_i` when `|mu_i-lambda*b_i-a_i*h_i| <= k_i`; otherwise it is the appropriate `(mu_i-lambda*b_i ∓ k_i)/a_i`. Clipping that **correctly represented** scalar minimizer to the interval is valid even when held weights lie outside the new box.

The resulting `b @ w(lambda)` is continuous and nonincreasing. Its opposite infinite limits bracket zero whenever a movable asset has nonzero beta; zero is always primal-feasible. Strict convexity gives a unique weight vector even if the dual multiplier is not unique on a plateau. The sign of the implementation's bracket and bisection updates is correct.

Normalizing beta over movable assets preserves the equality, correctly ignores irrelevant zero-cap assets and avoids dropping a uniformly small nonzero hedge vector. The all-zero-beta and all-zero-cap branches are appropriate. Input arrays are read without mutation, each result owns a new weight vector, and the deployed module has no market-file access or mutable cross-call state.

The internal residual tolerance is approximately `64*eps*sum(abs(b)*cap)`, with a subnormal floor. This is a numerical equality tolerance in normalized beta units. It does not establish the future realized net-return beta condition; risk-estimate error and trading costs remain full-strategy questions.

## 3. Existing references and results are meaningful

The independent SciPy reference expresses the primal using separate epigraph variables `z` and inequalities `z>=w-h`, `z>=h-w`, the beta equality and weight box. It does not copy the dual-threshold implementation. Its objective scaling is defined from the fixture before solving, and successful termination plus feasibility are checked before comparison.

The zero-cost KKT-system solution is a separate analytical reference. The 1,000-asset case constructs an interior beta-neutral weight vector and alpha satisfying the primal stationarity conditions, including the correct L1 subgradient. Small fixtures separately exercise binding caps, signed/zero/tiny betas, holdings outside the box, no-trade behavior and cost horizons.

The completed summary contains **54 passing checks**, including 19 declared invalid-input cases and the allocator-only timing check. The saved 1,000-asset timing mean is approximately **5.42 ms over 32 calls on one recorded CPU**, with all six thread controls set to one. This is component timing on a synthetic fixture, not a whole-strategy or long-horizon result. No alpha or hidden-future claim follows from it.

## 4. Test-order and artifact identity

The records establish the required sequence:

1. Plan recorded at 14:45:40 UTC while verifier and allocator were absent.
2. Verifier recorded before implementation; its final preimplementation revision was recorded at 14:49:18 UTC with allocator still absent.
3. Final expected-red run finished at 14:49:44 UTC, with exit code 1, no numerical checks executed and the missing allocator stated explicitly.
4. Initial allocator recorded at 14:51:27 UTC.
5. Completed verification began at 14:51:32 UTC.

Current plan, verifier and allocator hashes match their run-001 frozen artifacts and recorded identities. The final verifier hash is `72e417e521c72ecc5f9d109180c5f2744d97787068403c160b111fea815de60b`; the reviewed initial allocator hash is `176e4a4f42124dd76a0f4fa26db2c0427b1a4ea46c9805aa820155283aff918c`. The final preimplementation test revision changed red-run reproduction handling, not numerical cases. This review has added no tests.

Two artifact qualifications:

- The first red run's historical rerun command points to the subsequently created live allocator. The second red run fixes this. Add an explicit reproduction note to the first red artifact using its own frozen runner and an intentionally absent module path; retain the original command unchanged.
- The verifier writes its final summary/log in `finally` and does not explicitly classify `KeyboardInterrupt`. The completed existing evidence is valid, but interruption-safe checkpoint persistence is not established by this code. Do not claim it has been verified.

## 5. Integration boundary

The cost horizon is an optimizer approximation; the official scorer must continue charging full actual costs. Any subsequent gross scaling preserves beta equality algebraically but generally loses optimality for this exact box/L1 objective. Both facts are already disclosed in the component plan and should remain visible in the strategy's interpretation.

After the overflow correction, unchanged-verifier rerun and source readback, the allocator can be approved for integration under its numerical contract. Full-strategy causality, actual-cost scoring, realized beta, safety and complete-call runtime remain separate unexecuted gates.
