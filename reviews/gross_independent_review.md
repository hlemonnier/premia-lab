# Independent C07 exact-gross allocator review

**Reviewer:** alpha-model agent, distinct from the allocator/wrapper author.  
**Scope:** numerical derivation, source, wrapper/configuration equality, preserved build order and existing numerical evidence. No new unit cases, optimizer executions, actual-market runs or holdout inspection were performed by this reviewer.

## Decision

**Approve the fixed C07 implementation for its admitted discovery and configured causality E2E runs.** No blocking source issue was found. This does not establish an improvement over C02, full-strategy runtime, unseen-history convergence or final release readiness.

Reviewed solver SHA-256: `2a2d1fb7dfb6b9bcd1d8509e3b73b957d34d158eb198648c8ba78bdc2fe9cac8`. Current source matches the snapshot in `evidence/gross_verify_001/`. Wrapper SHA-256: `891bafcd0eff4c9b58c77fa3c12bfa851f71a1588113977f1fd0c2b43b54129b`.

## Scalar objective and reflected two-knot solution

For fixed beta and gross multipliers, the scalar minimization is

`0.5*a*w*w - m*w + k*abs(w-held) + nu*abs(w)`,

with `a>0`, `k>=0`, `nu>=0`, followed by a symmetric stock box. Reflecting negative held weights maps the two absolute-value knots to zero and `h=abs(held)>=0` without changing the quadratic coefficient. Differentiating on the three open intervals gives the implemented solutions `(x+k+nu)/a`, `(x+k-nu)/a`, and `(x-k-nu)/a`; the intervening subgradient ranges yield the exact zero and held-position plateaus. Multiplying back by the held sign restores the original coordinate.

The conditions handle coincident knots when held is zero: the middle interval is empty and the zero/held plateaus jointly give the usual threshold at `k+nu`. With zero cost or zero gross multiplier, the same formula reduces continuously. Clipping the unique unboxed minimizer to the stock box is exact for this scalar convex objective. The active derivative is `1/a` only in moving, unboxed intervals; a plateau or bound has derivative zero.

## Inner beta equality

The beta vector is normalized only over movable stocks, with fixed-zero-cap entries set to zero. For each fixed nonnegative gross multiplier, portfolio beta is continuous and nonincreasing in the beta multiplier, with derivative `-sum(inverse*b*b)` on an active segment.

The initial signed step goes in the correct direction to remove exposure. The code establishes a bracket with positive exposure at its lower endpoint and negative exposure at its upper endpoint. Each Newton proposal is accepted only when finite and strictly inside that bracket; otherwise it bisects. Subsequent updates preserve the bracket orientation. A small residual, rather than an iteration count alone, is required to return. Unresolved brackets or numerical limits raise and do not silently produce a feasible-looking substitute.

If all movable beta entries vanish, exposure is zero and no beta root is needed. If all caps vanish, the reused diagonal solver produces the only feasible book. The accepted zero-beta behavior does not require dividing by a zero derivative.

## Outer gross budget and derivative

For an active gross constraint, the derivative after enforcing beta equality is

`-sum(inverse*sign(w)^2) + sum(inverse*b*sign(w))^2 / sum(inverse*b^2)`.

This follows from differentiating beta neutrality jointly with the scalar response. It is nonpositive by Cauchy–Schwarz. The implementation uses that derivative only for a finite, interior Newton proposal; plateau or unreliable derivative cases retain the bracket and use bisection.

The declared upper endpoint `nu >= max(abs(mu)+k)` makes the all-zero portfolio an optimum at beta multiplier zero. It therefore provides a feasible gross endpoint for every nonnegative budget under the specified representable arithmetic. The code checks that endpoint rather than assuming its computed book is valid.

The original diagonal optimum is returned unchanged when gross is nonbinding within the fixed tolerance. A zero gross budget returns the unique zero book directly. Otherwise a positive multiplier is paired with gross equality to the fixed numerical tolerance. The final function checks finiteness, stock bounds, normalized beta residual and gross excess. It performs **no proportional postsolve scaling**. For the zero-budget special case, the reported zero multiplier is an implementation convention, not a claim that this is the unique optimal KKT multiplier.

## Controlled strategy contrast and chronology

`strategy_gross.py` delegates forecasting and risk estimation to the unchanged base strategy. Its explicit configuration matches C02 in every numerical control and basis; only the candidate identifier changes. The only intended portfolio-policy difference is solving the gross cap jointly with the existing beta, box and drift-aware L1 cost objective.

Configure passes through the base's strict validation and clears diagnostic state. The new optimizer stores no learned market state. `rebalance` passes the actual drifted held vector into the objective and returns the solver's weights directly. Full actual fees remain the original scorer's responsibility. The diagnostic `gross_scale=1` is accurate here; `gross_unconstrained_target` separately exposes how often the exact constraint changes the original unconstrained-gross solution.

Candidate output and future-alteration E2E runs remain necessary. Identical delegated forecasts should also reconcile with the C02 forecast artifact after the complete runs; this review did not execute either forecast.

## Build order and numerical evidence

The recorded sequence is plan at `20:48:33 UTC`, complete verifier at `20:49:40 UTC`, absent-solver red execution at `20:50:12 UTC`, then implementation snapshot at `20:52:44 UTC`. The red run explicitly has zero numerical checks. Independent primal reference fixtures were also validated before the implementation.

The verifier hash is identical in current source, preimplementation snapshot, red run and passing run:

`4b4ffc4e0329e29fad1a85629bd5ee0babfdbfd87fe1f17a0c2f00e7cba23bce`.

I inspected the independent reference: it uses primal weights, trade epigraph variables and separate gross epigraph variables, with beta equality, stock boxes and the gross bound in SciPy SLSQP. Its objective does not reuse the new two-multiplier solver. Hand solutions and constructed small/1,000-stock KKT solutions provide additional reference paths. The original diagonal solver is only reused for its established unconstrained-gross result and validation; no new tests were retrofitted to that old implementation.

`evidence/gross_verify_001/summary.json` records **86 passing checks**, no failed checks and exit code zero. The current solver matches the tested snapshot. Eight synthetic 1,000-stock complete-solver calls measured **4.00 ms mean**, **6.11 ms p95** and **7.14 ms maximum**. This is component timing; it excludes forecasting, causal risk estimation, instrumentation and the variety of active sets encountered in a full historical replay.

## Remaining gates and interpretation

The complete C07 discovery run must preserve the original fee accounting, target and daily ledgers, beta/cap residuals, fixed-block performance, iterations/evaluation counts, and all mean/tail timings. A later numerical convergence exception remains a failed execution, not an acceptable hidden fallback. Any implementation fix and exact rerun must preserve the failed evidence and source identities.

An exact solution to the specified one-period objective need not improve realized net Sharpe. The gross constraint is still an internal sizing policy, the diagonal covariance remains incomplete, and the cost horizon remains an approximation to a longer-horizon control problem. This experiment tests whether removing the known rescaling distortion improves the complete strategy; the numerical checks alone do not answer that economic question.
