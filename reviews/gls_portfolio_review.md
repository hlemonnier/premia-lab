# Independent C05/C06 design and source review

**Reviewer:** portfolio-research agent, independent of the GLS specification/implementation author and helper verifier author. **Decision:** approved for the lead's admitted discovery and configured-causality executions. This is source review; no new numerical test, scored model or validation/audit access was performed by this reviewer.

## Chronology and state

`strategy_gls.forecast` constructs the matured design from `X[t-2]` and label from `R[t-1]`. Its beta and precision estimates receive only `returns[:t-1]`, excluding that label return. Correlation-factor refreshes are anchored to prior-label history lengths20,41,..., with diagonal precision beforehand. The schedule depends on the observed count, not total future input length. Predictions remain zero until126 pairs have matured, first active row127.

The covariance loadings, epoch, Gram matrix, moment and EW mass are all local to the forecast invocation. No learner covariance state is copied into the portfolio cache. Rebalance delegation therefore consumes only C02/C04's ordinary observed-history state. Numerical future-alteration/prefix evidence remains a separate required gate.

## GLS algebra and normalization

The helper applies the Woodbury expression for `(diag(D)+B B.T)^-1` to the combined matrix containing both design and label. Its trace normalization subtracts the row diagonal of `D^-1 B (I+B.T D^-1 B)^-1 B.T D^-1` from `D^-1`, then divides by the positive mean. These matrix orientations and signs are correct. New arrays are created before arithmetic updates; caller inputs are not intentionally mutated. Rank-deficient factors are valid because the inner matrix contains an identity.

Both `Phi.T P Phi` and `Phi.T P y` use that exact same normalized precision. One EW mass increment per date preserves the declared temporal weighting and ridge scale. Symmetrizing the numerical Gram contribution does not introduce later observations. The factor covariance retains the parent's current marginal variance, with at least half remaining diagonal under the fixed shrinkage.

The zero residual intercept is explicitly retained. Ordinary cross-sectional centering is not weighted centering; adding weighted-intercept elimination would be a different estimator. Retaining and documenting this assumption is an acceptable controlled first comparison, not a claim that an intercept was fitted under the GLS metric.

## Wrapper configuration and portfolio identity

C05 delegates directly to the existing base `rebalance`, `estimate_risk` and diagnostics. C06 filters learner-only and portfolio-only keys before their respective configure calls; both receive the same common controls. Although they share the base module, the fixed common settings agree, and the learner's forecast uses its own copied configuration with explicit arguments to the base basis/risk functions. C06 delegates the entire portfolio to unchanged C04 and resets that portfolio cache through configuration.

The fresh-process research workflow prevents cross-candidate module state from being inherited. This review does not claim support for arbitrarily interleaving separately configured candidates in one interpreter without reconfiguration.

## Limits and next evidence

No source blocker was found for the fixed C05/C06 configurations. The helper's separate preimplementation numerical evidence is reviewed by its assigned independent reviewer; this review does not substitute for that execution. The official discovery workflow must establish full-cost results, validity, beta and measured timing. C05/C06 forecast equality should be checked from saved complete-run artifacts. Configured causality and any later validation/audit remain separate gates.

The experiment can test whether covariance weighting helps. A score increase would not by itself establish that observed coefficient changes were caused by common-shock contamination, or guarantee continuation performance.
