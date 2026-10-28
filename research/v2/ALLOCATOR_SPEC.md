# Factor-risk allocator — specification (written before the code)

## Problem

Given expected returns `mu` (n), drifted holdings `h` (n), specific variances
`d > 0` (n), factor loadings `B` (n×k), factor covariance `F` (k×k, positive
semidefinite), market betas `b` (n), per-stock linear cost rates `kappa >= 0`
(n, already divided by the cost horizon), risk aversion `gamma > 0` and box caps
`cap >= 0` (scalar or n), return the unique solution of

    maximize   mu'w - gamma/2 (w' diag(d) w + (B'w)' F (B'w)) - kappa'|w - h|
    subject to b'w = 0,  |w_i| <= cap_i.

Strict convexity comes from `d > 0`, so the solution is unique.

## Method

Introduce `y = B'w` and dualize the k + 1 equalities `y = B'w`, `b'w = 0` with
multipliers `lam` (k) and `nu`. Given the multipliers, each stock solves the same
scalar soft-threshold/clip problem as the existing C09 allocator, with shifted
alpha `mu - B lam - nu b`. The factor block solves to `y = F^+ lam / gamma` on the
range of `F`. Minimize the convex dual over `(lam, nu)` with damped Newton
steps: Hessian `[B b]' W [B b] + blockdiag(F^+/gamma, 0)`, where `W_i =
1/(gamma d_i)` for stocks strictly inside their trading region and 0 for stocks
at a no-trade band or a cap. Backtracking on the dual objective; fall back to a
gradient step if Newton fails to decrease it.

To avoid `F^+`, parametrize `F = L L'` (k×r) and dualize `z = L'B'w` instead.
The factor term is then `gamma/2 ||z||^2`, with `z = mu_z / gamma` closed form.

## Expected behaviour (tests check each)

1. **Agrees with cvxpy** (Clarabel) on random problems with n = 200, k = 5,
   active caps, active no-trade bands and a binding beta constraint: objective
   within 1e-7 relative, weights within 1e-5 absolute.
2. **Beta equality holds** to 1e-10 relative to `|b|'cap`.
3. **F = 0 reduces exactly** to the existing diagonal allocator's solution (within 1e-9).
4. **No trade when already optimal.** If `h` is the solution of the problem,
   returning it costs nothing: `w == h` within 1e-9.
5. **Caps respected exactly.** `|w_i| <= cap_i` with no tolerance.
6. **cap_i = 0** forces `w_i = 0`, whatever `h_i` is.
7. **Invalid inputs raise ValueError**: non-finite inputs, `d <= 0`, `gamma <= 0`,
   shape mismatch, negative caps or costs, `F` not symmetric PSD (smallest
   eigenvalue < -1e-12·trace).
8. **Infeasible beta** (every stock with nonzero beta capped at zero) returns the
   best feasible point with beta exposure 0 when possible, else raises RuntimeError.
9. **Runtime.** n = 1000, k = 26: median under 10 ms per solve on this machine,
   warm-started from the previous multipliers.
10. **Deterministic**: same inputs give bitwise-identical outputs; inputs are not mutated.

## Failure modes considered

- Newton on a piecewise-quadratic dual can cycle when the active set flips
  → backtracking line search on the dual objective guarantees monotone decrease.
- Singular Hessian when all stocks sit at bands or caps → Levenberg damping
  `+ 1e-12·trace` on the Hessian diagonal.
- Ill-conditioned factor covariance → caller passes `L` from an eigen-decomposition
  with eigenvalues floored at 0, so no inverse of F is ever formed.
