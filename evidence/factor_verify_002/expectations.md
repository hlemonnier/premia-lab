# Factor portfolio solver: preimplementation contract

**Order:** this specification, then all numerical reference fixtures and executable checks, then new solver/wrapper implementation. Existing diagonal allocator is reused unchanged and receives no new unit cases after its implementation. No market data is used by this numerical verifier.

## API and objective

`allocate_factor(mu, held, diagonal_variances, factors, betas, costs, risk_aversion, cost_horizon, weight_cap, max_iterations=80) -> (weights, diagnostics)`

Minimize `0.5*gamma*(sum(D*w*w)+sum((B.T@w)**2)) - mu@w + sum((cost/H)*abs(w-held))` subject to `beta@w=0` and `abs(w)<=cap`. `D` is strictly positive; `B` is a finite `(n,k)` matrix and may have zero columns or be rank-deficient. Caps may be a scalar or an n-vector. All inputs are unchanged. Degenerate or invalid derived arithmetic is explicitly rejected, not clipped into apparent success. The returned diagnostics identify iteration count, inner solves, dual-gradient residual and convergence. Unconverged results raise `RuntimeError`; no silent exact-optimum claim.

The wrapper estimates correlation factors as recorded in `research/PORTFOLIO_NEXT_PLAN.md`; alpha and beta/variance estimation are delegated to the base C02 implementation. It uses only the prefix supplied to `rebalance`, resets cache on configuration, preserves the parent's marginal variance and passes actual drifted holdings into the optimizer. Full costs remain charged by the official scorer. The inherited gross scaling remains approximate and must be reported.

## Predeclared numerical cases

1. Zero factor columns and nonzero zero-valued factors reduce to the existing diagonal solution; no new claim about that existing solver is made.
2. No costs, inactive caps: compare against the full dense covariance equality-constrained analytical KKT solution for a fixed six-stock fixture with nonzero signed betas and two factors.
3. Zero betas, costs and factors yield the ordinary unconstrained quadratic optimum; mixed zero betas and zero caps are also covered.
4. Six fixed-seed small convex problems, each with heterogeneous variances/costs/betas/caps, drifted holdings that may start outside the box, rank-deficient or ordinary factors, and possible binding boxes: compare the primal objective against independent SciPy SLSQP on `(w,z)` epigraph variables. Do not use the factor-dual algorithm for the oracle.
5. Sign flips and a fixed orthogonal factor rotation preserve output weights to numerical tolerance.
6. Large transaction costs and a feasible held book keep the exact no-trade optimum.
7. A fixed-seed 1,000-stock, ten-factor constructed KKT optimum uses nonzero costs and known trade signs. Match its known feasible solution and record mean, p95, max over eight single-core calls including complete solver calls. Fixed fixture parameters are in the verifier before implementation.
8. Reject factor shape mismatch, NaN/inf factors, nonpositive diagonal variance, negative costs, invalid risk aversion/horizon/caps and nonpositive or noninteger max_iterations.
9. Exact same-input repeats and input-array identity/hash comparisons establish determinism/immutability on these fixtures.

## Fixed acceptance tolerances

- Finite float64-compatible stock vector of expected size; maximum box excess `<=2e-12*max(1,max(cap))`.
- Beta normalized over movable stocks: absolute exposure `<=5e-11*max(1,sum(abs(beta_normalized)*cap))`.
- Small analytic and no-factor solutions: max weight difference `<=2e-9`; constructed 1,000-stock KKT solution `<=1e-8`.
- Sign/orthogonal rotation weights: max difference `<=2e-9`.
- Independent-reference objective error normalized by a fixed fixture-derived scale `<=5e-8`. The reference must itself terminate successfully and satisfy feasibility to1e-8.
- Solver diagnostics must say converged with finite gradient residual. Exact repeated calls must return exactly equal weights; input arrays must remain unchanged.
- Synthetic 1,000-stock solver mean below100ms on one recorded CPU, with all numerical threads set to one. This is a component feasibility check and cannot replace complete strategy or long-history timing.

No thresholds or fixtures may be changed after implementation to obtain a pass. Preserve failures, fix implementation if justified, and rerun the identical verifier in a new evidence directory. All numerical tests are written before the new solver implementation. Further candidate verification uses complete E2E workflows and source review.

## Evidence

Record plan/test/implementation timestamps and hashes; absent-module red run; exact scripts and inputs; setup/environment/thread/CPU; expected/actual per-case values; exact rerun command; logs; code identities and final status. Build-order snapshots preserve the actual preimplementation verifier. Every test run has a new output directory and no overwrite.
