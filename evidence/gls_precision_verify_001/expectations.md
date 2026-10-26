# GLS precision application: failure modes and expectations before implementation

## New component and ordering

The new helper is `submission/gls_precision.py`, with API

`normalized_precision_apply(diagonal, factors, values) -> (weighted_values, mean_precision)`.

The helper does not yet exist at specification time. This specification is written first, the numerical verifier second, an expected missing-module run third, and the helper implementation only afterward. These are isolated tests for a new numerical primitive, not tests retrofitted to implemented strategy code. No market data or existing candidate fits are needed.

For a positive diagonal vector D and loading matrix B, let `Sigma = diag(D) + B B.T`. The desired result is `solve(Sigma, V) / mean(diag(inv(Sigma)))`, together with the positive finite scalar `mean_precision = mean(diag(inv(Sigma)))`. V may be an n-vector or an n-by-p matrix. D is nonempty; B may have zero columns; p must be positive for a matrix. All inputs and results are finite real float64 arrays/scalars. The helper neither estimates covariance nor reads files or mutable market state.

## Failure modes and fixed expected results

1. **Wrong inverse or normalization:** independent dense covariance inversion/solve on fixed seeded small matrices must agree with both returned outputs. The reference constructs the full covariance directly; it does not reproduce Woodbury or any proposed helper algebra.
2. **Diagonal-only special case:** with D `[1,2,4]`, no factor columns and V `[1,-2,4]`, mean precision is `7/12`, and normalized output is `[12/7,-12/7,12/7]`. Matrix right-hand sides must follow the same row weighting. A common positive diagonal and zero factors must preserve V exactly to tolerance.
3. **One stock:** normalization cancels scalar covariance, leaving V unchanged and reporting its reciprocal covariance.
4. **Zero or redundant factors:** zero columns and linearly dependent loading columns are valid; the positive diagonal keeps Sigma positive definite. Dense references must still agree.
5. **Basis dependence:** orthogonal rotation or column-sign flips of B must leave results unchanged, because B B.T is unchanged.
6. **Covariance scaling:** multiplying D by a and B by sqrt(a) must leave the normalized output unchanged; mean precision scales by `1/a`. Fixed positive scales are 0.01 and 100.
7. **Invalid input:** reject nonvector/empty/nonpositive/nonfinite D; nonmatrix B, mismatched B rows, nonfinite B; scalar/3-D/mismatched/empty-column/nonfinite V. Explicit `ValueError` is the declared rejection. A diagonal whose reciprocal/mean precision is unrepresentable, such as `[1e-320,2e-320]` without factors, must be rejected rather than returning infinities or silently zeroing weights.
8. **Mutation/nondeterminism:** make each actual test input read-only, check its contents remain identical, and require an identical repeat to match. This protects the caller's published panels and risk estimates.
9. **Full-universe engineering:** a fixed 1,000-stock, rank-10, 27-right-hand-side synthetic case must return finite output of matching shape and positive finite mean precision, agree under factor rotation, and repeat deterministically. Record 16 single-core calls and their mean/p95/maximum runtime without claiming this component timing verifies full forecast or rebalance limits. No arbitrary standalone performance threshold is introduced.

## Fixtures, tolerances and evidence

Use a fixed NumPy generator seed `20261026`. Dense-reference cases use n in `[3,7,20]`, with both vector and matrix right-hand sides and diagonal values geometrically spaced from 0.01 to 1.0. Loading scales and the complete generated arrays are saved in `inputs.json`; fixed analytic, zero-factor, redundant-factor, rotation, covariance-scaling and invalid cases are named separately. No fixture is selected after inspecting helper outputs.

Use float64 `atol=1e-11`, `rtol=1e-10` for numerical agreement, fixed before implementation. Require finite outputs and exact shape agreement independently of allclose. The identical repeat is checked for exact equality; source/control changes require a new evidence directory. Positive mean precision and normalized right-hand-side shape are explicit expectations. Tolerances are not to be widened to excuse a bug.

Every execution saves the setup, seed, full synthetic inputs, exact command and frozen rerun command, verifier/plan/helper identities, environment/thread/CPU metadata, expected and actual per-case results, logs and final status. Preserve the missing-module run as an expected red checkpoint with no numerical pass claim. Its reproduction points to a deliberately absent helper path. Completed numerical verification is scoped to these fixtures, not unseen-market alpha, covariance-estimation quality, full-strategy causality or the whole runtime contract.
