# Portfolio allocator: contract and verification plan

This plan is written **before the verification code and before the allocator implementation**. The isolated numerical checks are necessary because a wrong optimizer can produce plausible whole-strategy results while violating the declared convex objective or beta constraint. The eventual strategy still requires complete scorer E2E validation. No market data is used by this work.

## API and optimization contract

```python
allocate(expected_returns, held_positions, variances, betas, trading_costs,
         risk_aversion, cost_horizon, weight_cap) -> numpy.ndarray
```

For `a = risk_aversion * variances` and `k = trading_costs / cost_horizon`, return the unique minimizer of

\[
\frac12\sum_i a_i w_i^2-\sum_i\mu_iw_i+\sum_i k_i|w_i-h_i|
\]

subject to `betas @ w = 0` and `-weight_cap <= w <= weight_cap`. This is equivalent to maximizing the alpha, risk and turnover objective specified by the project owner. Positive diagonal risk gives strict convexity. Zero is feasible for every allowed cap vector. The beta multiplier can be nonunique on a no-trade plateau while the optimal weights remain unique.

`held_positions` means the already drifted holdings supplied by the official scorer, not yesterday's target weights. It may lie outside the new box and need not satisfy the beta constraint. The cost horizon is a portfolio-control approximation; **the official scorer continues to charge full one-way costs on actual trades**. There is no gross cap in this module. Any subsequent uniform scaling preserves beta neutrality but changes the exact optimization problem and must be disclosed by the strategy owner.

## Inputs and failure handling

- The first five arguments are finite float-convertible one-dimensional vectors of the same nonzero length. Inputs are never mutated.
- Variances must be strictly positive. The caller must choose and apply any variance floor; the allocator does not silently change its objective by flooring again.
- Costs are nonnegative. Betas may be positive, negative or zero; all-zero betas are valid.
- Risk aversion and cost horizon are finite positive scalars.
- The cap is a finite nonnegative scalar or a same-length vector. Zero caps are valid and fix those positions to zero.
- The derived diagonal risk and effective cost coefficients must be finite, with strictly positive risk. Numerically unrepresentable derived quantities are rejected explicitly.
- Reject malformed or invalid inputs with `ValueError`. If numerical root finding cannot certify the declared constraint, raise a numerical/solver error rather than return an apparently successful zero book.
- Return a new finite float64 vector, obeying the box and a numerically verified beta equality. No hidden state, randomness, imports of market files, or dependencies beyond numpy belong in the deployed module.

## Proposed numerical method

With a scalar equality multiplier, the objective separates into one-dimensional bounded quadratics with an absolute-deviation cost around held weights. Each one-dimensional solution is a clipped soft threshold. The resulting beta exposure is a continuous nonincreasing function of the multiplier. Bracket its zero and solve by bisection. Handle all-zero betas, all-zero caps, no-trade plateaus and zero-cost cases without a daily general-purpose QP. Normalize the beta scale to avoid treating uniformly tiny nonzero betas as a missing constraint; ignore fixed-zero-cap assets when selecting that scale.

This description states the mathematical method. Independent reference checks must express the primal problem directly, rather than copy the multiplier/threshold implementation.

## Failure modes, cases and expected outcomes

All examples below use unit risk coefficients unless stated otherwise. The verification script will save its concrete numerical fixtures so the exact inputs are inspectable.

| Case | Failure being checked | Expected result |
|---|---|---|
| Zero alpha, empty holdings | Spurious trades or hedge demand | Exactly zero weights |
| Feasible nonzero holdings inside no-trade band | Trading despite costs covering the marginal gain | Preserve the holdings |
| All-zero betas | Degenerate equality and unnecessary root finding | Independent bounded cost-aware optima |
| Mixed zero/nonzero betas | Ignoring unconstrained assets | Hedge the nonzero-beta block; optimize zero-beta asset independently |
| Signed betas | Assuming every beta is positive | Correct hedge, including equal-sign holdings when betas have opposite signs |
| Zero costs | Wrong risk factor or sign in hedge multiplier | Match an independently solved equality-constrained quadratic KKT system |
| Nonzero drifted holdings | Penalizing trades from zero or previous targets | Match the declared absolute-change objective |
| Holdings initially outside the box | Incorrect threshold/clipping interaction | Reach the correct bounded optimum |
| Binding caps with hedge | Clipping an unconstrained hedge without re-solving | Bound-satisfying beta-neutral optimum |
| Heterogeneous caps and limited hedge capacity | Missing feasible compensation limit | Correct constrained solution |
| Zero caps, including all zero | Artificial dual degeneracy | Fixed weights remain exactly zero |
| A huge beta on a zero-cap asset | Normalization dominated by an irrelevant asset | Same active solution as if that fixed asset were removed |
| Uniformly tiny nonzero betas | An absolute exposure threshold silently drops the equality | Same weights as the equivalent ordinary-scale beta vector |
| Very small valid positive variance | Division/threshold instability | Finite capped solution; no hidden variance-floor change |
| Large cost, no-trade plateau | Root degeneracy | Correct unique weights without unnecessary trades |
| Cost horizon 1 versus 2 | Wrong direction of cost amortization | Known hand solutions with the effective cost halved |
| Generated small convex problems | Combined errors missed by hand cases | Agree in objective with independent SciPy epigraph optimization |
| Determinism and immutability | State leakage or argument mutation | Identical repeated economic output; arguments unchanged |
| 1,000-asset known KKT optimum | Wrong scaling and slow non-vectorized implementation | Match constructed primal optimum; record one-core timings |
| Invalid shapes, NaNs/infinities, nonpositive risk/horizon, negative costs/caps | Plausible outputs from invalid inputs | Explicit `ValueError` |

Illustrative exact outcomes to be encoded before implementation:

- `mu=(0.3,0.1), beta=(1,1), costs=0, caps=1` gives `(0.1,-0.1)`.
- `mu=(0.3,-0.1), beta=(1,-1), costs=0, caps=1` gives `(0.1,0.1)`.
- `mu=(0.6,0.2), beta=(1,-1), h=0, effective_cost=(0.1,0.1)` gives `(0.3,0.3)`.
- `mu=(3,0,0), beta=(1,1,1), costs=0, caps=(0.2,0.4,0.4)` gives `(0.2,-0.1,-0.1)`.
- `mu=(5,0), beta=(1,2), costs=0, caps=(1,0.1)` gives `(0.2,-0.1)`.
- With a zero-beta single asset, `mu=0.1, h=0.4, effective_cost=0.1, cap=1` gives `w=0.2`.
- `mu=(0.5,-0.5), beta=(1,1), h=0, costs=(0.2,0.2)` gives `(0.3,-0.3)` at horizon 1 and `(0.4,-0.4)` at horizon 2.

## Independent references and tolerances

For small reference cases, use SciPy SLSQP on primal variables `(w,z)`, with linear epigraph inequalities `z >= w-h` and `z >= h-w`, a linear beta equality, the weight box, and nonnegative `z`. Use the smooth diagonal quadratic objective and its gradient. Normalize that reference objective by a positive, fixture-derived bound on its magnitude; never tune a tolerance after seeing allocator output.

Predeclared thresholds:

- All outputs finite, correct shape and float64-compatible; box error at most `2e-12 * max(1, max(cap))`.
- Beta residual, using betas normalized over assets with positive caps, at most `5e-11 * max(1, sum(abs(normalized_beta) * cap))`.
- Hand and analytic/KKT expected weights: maximum absolute difference at most `2e-10` for small cases and `1e-9` for the 1,000-asset constructed case.
- Small-case independent reference objective: absolute difference in the normalized minimization objective at most `2e-8`. The reference itself must report successful termination and satisfy its constraints.
- Exact repeated weights and no argument mutation.
- The 1,000-asset timing check records setup, thread settings, CPU affinity, mean, p95 and maximum over 32 calls. Expected mean below 100 ms on one core; this is allocator-only synthetic evidence, not a substitute for timing complete strategy calls.

## Required order and retained evidence

1. Save this plan and its hash/timestamp while the allocator and verifier do not exist.
2. Write and snapshot `tools/verify_portfolio.py`, its fixture definitions and hash/timestamp while the allocator still does not exist. Execute a preimplementation run: missing module is an expected red-stage failure, with checks explicitly unexecuted.
3. Only then implement `submission/portfolio.py`.
4. Execute the frozen verification without adding new post-implementation unit tests. Preserve failed runs, change implementation when warranted, and execute a distinct run directory for each attempt.

Each run retains its plan, exact verifier and allocator snapshots if present, source hashes, concrete inputs, exact command and rerun command, environment, expected results, actual per-case results, logs, termination status and relevant numerical outputs. An independent agent reviews the implementation and artifacts before integration is claimed complete. Later full-strategy E2E checks remain owned by the main research workflow.
