# Independent GLS helper and wrapper review

## Decision and scope

Approve the fixed helper and C05/C06 wrappers for their admitted discovery executions. This review is independent of the implementation author. No new numerical tests were added after implementation. No actual validation/audit inputs were read.

The numerical plan and verifier were written by this reviewer before the helper existed. `gls_precision_build_order_001` records plan and test hashes with `helper_exists=false`; `gls_precision_red_001` then exited1 with zero numerical checks and the explicitly expected missing helper. The implementation author subsequently wrote the helper and executed the unchanged verifier. Readback confirms `gls_precision_verify_001` exited0 with73 passing checks and no failures.

| Identity | SHA-256 |
|---|---|
| Verifier, before implementation and executed unchanged | `45e88024ff37fd532467d77b5878d87592f331b05c5130591b3225b5d33501ce` |
| Plan | `f4d1b4ea3eaed7ecf6072d4d330cce67bf653cc0a919498bc02ef956e2ddf969` |
| Live and tested helper | `0321bb41c340104e31b991d7e18437a5279182cfff955f6e4603c574a6c67c5e` |

## Numerical reasoning

With `W=D^-1 B` and `A=I+B.T W`, the implementation applies `D^-1 V - W solve(A, W.T V)`, which is the correct Woodbury precision action. Its diagonal correction `row_sum(W * solve(A,W.T).T)` correctly yields the diagonal of `W A^-1 W.T`. Dividing by the mean resulting precision diagonal gives the declared normalization. Vector/matrix shape restoration, zero-factor handling, fixed float64 outputs, no mutation and explicit invalid/unrepresentable arithmetic rejection match the specified contract.

The reference verifier constructs the dense covariance and independently uses dense inversion/solve, then checks rotations, covariance scaling, redundant factors, invalid inputs and a 1,000-stock shape. It does not duplicate the Woodbury algebra as its reference. Passing these fixtures is scoped numerical evidence, not proof of arbitrary-precision behavior for every ill-conditioned input. The actual learner's positive diagonal remainder leaves at least half the inherited marginal variance under its fixed factor shrinkage.

## Wrapper chronology and controlled comparison

At forecast row t, the newest label is day j=t−1. `strategy_gls` estimates beta, marginal variance and any refreshed factors from `returns[:j]`, excluding the label return. It applies one normalized precision to the combined matrix `[Phi,y]`, using the same daily EW mass for Gram and target moments. Ordinary feature centering, zero residual intercept, ridge0.1, half-life252 and warmup126 remain as specified. The weighted Gram is symmetrized only to remove floating-point skew.

The local factor cache starts empty on every forecast call. First learner factor fits occur at prior-history lengths20 and41, affecting forecast rows21 and42; forecasts remain zero until row127. Refresh timing depends on observed count, not total input length. The local cache is never published to the factor portfolio.

C06 gives identical common controls to the learner and portfolio wrappers. Although they share the base module's static configuration, both receive the same common values; the learner uses its own copied explicit configuration in forecasting. Only C04 rebalance creates its portfolio factor cache, from observed prefixes, and resets it on a repeated/decreasing history count. Pure diagnostics do not update either fit.

The retained zero-intercept assumption is a real limitation: ordinary centered columns are not centered under the precision metric. The implementation does not silently claim or add a weighted nuisance-intercept projection.

## Executed contrast evidence

The admitted C05 and C06 discovery runs saved byte-identical forecast arrays:

`0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0`.

This verifies that the executed C06−C05 comparison changes construction while preserving the forecast array. It does not by itself establish causal correctness. Configured altered-future checks for these wrappers remain a separate finalist gate; the relevant additional schedules are specified in `verification/GLS_CAUSALITY_EXTENSION_PLAN.md`.
