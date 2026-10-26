# Exact gross-budget allocator: preimplementation contract

**Candidate:** C07, authorized by the lead after the first four discovery results. The new allocator/wrapper have not been implemented at creation of this plan. All numerical fixtures and executable checks must be written and snapshotted next, and the absent-module red stage executed, before implementation. Do not modify the existing diagonal allocator or old candidates.

## Research question and complete configuration

C02's diagonal risk/alpha/gamma1000/cost horizon20/stock cap0.01/gross cap1 remain unchanged. C07 replaces its frequent proportional gross rescale by the exact joint gross constraint in the same convex objective. The first-wave runs showed that rescaling was routine and therefore changed the intended no-trade solution. This is an observed reason to spend a construction slot, not evidence that the new policy must improve net Sharpe. The lead owns the economic run/freeze; no market scoring is authorized by this verification plan.

## Exact primal and API

`allocate_gross(mu,held,variance,beta,cost,gamma,horizon,cap,gross_cap,max_iterations=96) -> (weights,diagnostics)`

Minimize

`0.5*gamma*sum(variance*w*w) - mu@w + sum((cost/horizon)*abs(w-held))`

subject to `beta@w=0`, `abs(w)<=cap`, `sum(abs(w))<=gross_cap`.

Variance is strictly positive, costs/caps/gross cap nonnegative, gamma/horizon positive and finite. All vectors share nonzero length; cap may be scalar or a stock vector. Inputs are unchanged. Zero gross cap has the exact feasible solution zero. The existing diagonal solver may supply the unconstrained-gross solution and shared input validation; its code is reused unchanged and receives no new direct unit tests.

The new solver returns the unique strict-convex primal optimum with finite weights and diagnostic feasibility/convergence evidence. It raises on invalid/unrepresentable arithmetic or unresolved numerical convergence. It never silently rescales an unconverged weight vector. The C07 wrapper has no fallback to proportional scaling: an unresolved numerical path fails that run and is reported.

## Scalar prox and dual method

Let `a=gamma*variance`, `k=cost/horizon`, beta multiplier `lambda`, gross multiplier `nu>=0` and `m=mu-lambda*beta`. Each coordinate minimizes

`0.5*a*w*w - m*w + k*abs(w-held) + nu*abs(w)`

on its stock box. Reflect negative holdings using `s=sign(held)` (use+1 at zero), `x=s*m`, `h=abs(held)`. Before clipping, its minimizer is:

| Range of x | Reflected solution |
|---|---|
| `x < -k-nu` | `(x+k+nu)/a` |
| `-k-nu <= x <= nu-k` | 0 |
| `nu-k < x < a*h+nu-k` | `(x+k-nu)/a` |
| `a*h+nu-k <= x <= a*h+nu+k` | h |
| `x > a*h+nu+k` | `(x-k-nu)/a` |

Multiply by s and clip to the symmetric box. The derivative with respect to m is1/a in moving, unboxed quadratic segments and zero in a kink/box plateau. Coincident knots have no harmful discontinuity in weights; bracketing remains authoritative even if a boundary derivative is not useful.

For each fixed nu, normalized beta exposure is a continuous nonincreasing function of lambda. Bracket zero and use Newton only when its proposed point stays inside the bracket; otherwise bisect. Ignore fixed-zero-cap assets when normalizing beta. The final beta residual, not an iteration flag alone, certifies the equality.

The constrained gross is continuous and nonincreasing in nu. If the existing diagonal optimum already fits gross, return it unchanged. Otherwise use an outer bracket with a guaranteed all-zero upper endpoint `nu >= max(abs(mu)+k)` and a safeguarded Newton update. On an active quadratic region, write u=1/a on movable trading coordinates, zero elsewhere, b=normalized beta and s=sign(w). Then

`d gross / d nu = -sum(u*s*s) + (sum(u*b*s))**2 / sum(u*b*b)`

with the second term zero if its denominator is zero. This is the gross derivative after enforcing beta neutrality. Boundary plateaus use bisection. Fixed maximum96 outer/inner iterations; no performance-dependent tolerance change.

Internal target tolerances are64 machine eps times the attainable normalized beta bound, and128 eps times `max(1,gross_cap,sum(cap))` for gross. Every accepted solution preserves boxes and satisfies both final constraints. Record gross multiplier, budget binding, beta/gross residuals, scalar evaluations and iterations. Reuse of the parent alpha and risk functions makes this a portfolio-policy comparison, not a changed forecast.

## Numerical cases frozen before implementation

The new verifier will include all concrete numbers/seeds below before implementation:

1. Nonbinding gross reproduces the existing diagonal solution; zero gross and zero stock caps return the only feasible zero book.
2. Two-stock beta equality with active gross: `mu=(0.3,-0.1), beta=(1,1), a=(1,1), costs=0, gross=0.1, cap=1` gives `(0.05,-0.05)`.
3. Zero-beta, zero-cost L1 edge: `mu=(2,1), a=(1,1), gross=1, cap=10` gives `(1,0)`.
4. Feasible no-trade book `held=(0.2,-0.2), mu=0, a=1, beta=1, cost=0.5`: gross0.6 preserves holdings; gross0.2 gives `(0.1,-0.1)`.
5. Known signed four-stock interior KKT optimum satisfying beta and active gross, with explicit positive gross multiplier.
6. Six fixed-seed small convex problems including heterogeneous/signed/zero beta, held positions outside boxes, positive/zero costs, zero caps and active/inactive gross. Independent SciPy SLSQP uses primal `(w,z,q)` variables, separate trade and gross epigraph inequalities, beta equality and `sum(q)<=gross_cap`. Require a valid reference solve before comparing objectives.
7. Sign-flipping mu/held/beta appropriately produces the corresponding reflected optimum; stock permutation gives the same reordered optimum.
8. Fixed-seed1,000-stock known KKT optimum with nonzero costs, gross1, beta equality and no binding stock cap. Record complete solver timing over eight single-core calls.
9. Invalid gross cap, malformed inputs, negative risk/costs/caps, and nonpositive/noninteger iteration limit explicitly raise ValueError.
10. Identical repeated calls give identical weights and every input array remains unchanged.

## Fixed verification tolerances

- Finite stock vector of correct shape; stock-box excess at most2e-12*max(1,max(cap)).
- Normalized beta residual at most5e-11*max(1,sum(abs(b)*cap)).
- Gross excess at most2e-11*max(1,gross_cap). No postsolve scaling is allowed to meet this check.
- Hand/KKT expected weight maximum error at most2e-9 for small cases and1e-8 for the1,000-stock case.
- Independent primal objective error after a positive fixture-derived scale at most5e-8; reference termination success and its own constraint feasibility1e-8 required.
- Sign/permutation error at most2e-9; exact repeated output and unchanged inputs.
- Eight synthetic1,000-stock full-solver calls average below100ms on one recorded CPU with numerical threads fixed to one. This is a component gate, not a full candidate or century measurement.

Preserve failure evidence and change implementation only when justified; never change these tests/tolerances to obtain a pass. Later verification uses the original scorer's E2E workflow and configured causality. No candidate is admitted solely because its isolated checks pass.

## Evidence

Record plan/verifier/implementation hashes and timestamps, absent-module red run, concrete fixtures, independent reference outcomes, expected/actual checks, setup/environment/CPU/threads, full logs, exact rerun commands and final status in separate non-overwritten directories. No actual market observations are required for this numerical verifier.
