# Independent review of frozen-position attribution

27 October 2026, Europe/Paris. Reviewer: independent causality/source agent. This document records staged review; a completed specification review is not an executed tool or market-analysis pass.

## Preimplementation specification review

**Status: the bounded descriptive design is acceptable, subject to the prospective verifier, implementation and execution gates below.** The selected C09 policy, its configuration and its four-file handoff must remain unchanged. All historical periods are already exposed; no result from this extension is clean confirmation for a new policy.

Read `research/FROZEN_ATTRIBUTION_PLAN_20261027.md`, the two follow-up literature/notes documents, original scorer, and the existing `submission/strategy.py` and `submission/strategy_factor.py` risk functions. No market arrays, new attribution outputs or model executions were used for this specification judgment.

### Indexing and prior-information state

The saved target at index zero is chosen after close 252 and first earns return 253. The opening book for scored return row `t` is therefore `targets[t-253]`. Using `targets[t-252]` would use a target chosen after seeing that return. Using the saved drifted book would explain after-return holdings rather than the opening book. Reconciliation of opening target times realized returns against the original gross ledger must precede interpretation.

For that earning day `t`, C09's original risk call receives exactly `R[:t]`, ending at `t-1`. Its trailing risk window and marginal-variance shrinkage must be unchanged. C04's cache epoch is `max(0,(history_length-253)//21)`, so when the explanatory estimator first visits earning row 253 it refreshes on 253, 274, 295, and so forth. Between refreshes, reuse the stored correlation loadings and rescale with the current prior-estimated marginal variances. Recomputing factors on every day, fitting them on the full packet, or silently shifting the refresh epoch would change the explanatory lens.

The requested preimplementation clarifications have been adopted in the root plan: factor rank 10, shrinkage 0.5, refresh every 21 days, window 252, and thin-SVD rank tolerance `float64_epsilon * max(number_of_stocks, number_of_loading_columns) * largest_singular_value`, retaining only singular values strictly above the threshold. Empty or numerically zero spans need an explicitly empty basis. These values must not be chosen from attribution outcomes.

### Mathematical decomposition and interpretation

Let `e = r - beta * m` and let the columns of Q be an orthonormal basis for the fixed explanatory loading span. The algebra

`w'r = (w'beta)m + w'QQ'e + w'(e-QQ'e)`

is correct. The factor scores use realized row `t` solely for descriptive attribution. They are not an admissible same-day forecast. The loading basis and opening book must be determined before row `t`.

This is a Euclidean projection onto C04's current rescaled factor-loading span. It is not IPCA estimation, a fitted price-of-risk model, or an identification of the simulator's economic factors. A small remainder can coexist with no independent tradable alpha; a large remainder can contain omitted common risks, nonlinear exposures and estimation error. The prior beta is the same beta used to construct the frozen hedge, so a near-zero estimated-market component is substantially constructional and does not independently establish realized future beta neutrality.

For each original stage mask, `Cov(component,gross)/Var(gross)` is an additive covariance contribution when all terms use the same sample and denominator convention. Contributions sum to one if gross variance is nonzero. They can be negative or greater than one. They are not nonnegative independent-risk percentages, PCA variance-explained percentages, or portfolio weights. Component volatilities do not add, and neither component Sharpe ratios nor selected mean percentages should be introduced after seeing outcomes.

### Prospective verification requirements

The independent verifier should use the complete CLI workflow and written expectations before the tool exists. Known-component fixtures need nonzero market, factor and remainder contributions, changing predetermined opening positions, an independently established factor span/rank, and enough assets that rank ten does not automatically capture every residual direction. A correct sum-to-gross identity alone would not detect an implementation that sends the whole residual to the factor bucket or always uses a zero span.

The fixture must make the target-index shift economically detectable. A known periodic factor construction with more than ten independent residual directions is one possible design, not a required change to the admitted specification. Zero returns must retain zero components and null undefined covariance ratios. Malformed identity data must fail before numeric interpretation. A modified future and a truncated packet must preserve all earlier descriptive rows whose own realized returns have not changed, with fixed tolerances set before execution. Since attribution uses return `t`, a suffix mutation beginning at `c` protects attributed economic rows strictly before `c`; it does not protect row `c` itself.

Only an independent implementation review and a completed prospective synthetic workflow can release the one declared canonical attribution. No source-review approval substitutes for that execution evidence.

## Cross-review of the user-note reconciliation

The mathematical corrections in `research/USER_NOTES_REVIEW_20261027.md` are sound within their stated assumptions: an equal-weight overlay can hedge estimated beta when correctly sized; centered sample covariance has rank at most 251 with 252 observations; constraint multipliers couple static no-trade conditions; the annualized daily Sharpe standard-error illustration needs the daily/annual frequency conversion; residualization and GLS are different operations; and scaling portfolio targets need not preserve exact scorer Sharpe because the drift denominator and subsequent trades change.

The document correctly treats diagonal residual risk as a regularization trade-off rather than claiming that residual correlations vanish. It also correctly distinguishes a 1,008-day learning half-life, characteristic persistence and the 20-day cost-control horizon. Its no-trade expression is valid at an unchanged feasible interior book, with its explicit warning to evaluate the risk gradient at the solved portfolio when other coordinates move. The caveat about gross rescaling disturbing that local no-trade result is necessary and accurate.

One wording correction was requested and applied in the notes: the original assignment README itself describes its particular naive cvxpy example as taking about one second per call. That is an employer-provided estimate for that example, not a local benchmark and not a universal statement about cvxpy or 1,000-variable programs. It should not be described as having the same unsupported provenance as an invented two-to-five-millisecond claim. No strategy change follows from this clarification.

## Cross-review of the literature follow-up

`research/LITERATURE_FOLLOWUP_20261027.md` appropriately separates primary-source claims, limitations of abstract-only access, and project-specific inferences. This reviewer independently retrieved the primary arXiv abstracts for [linear-cost trading](https://arxiv.org/abs/1203.5957) and [attention factors](https://arxiv.org/abs/2510.11616), and the [CEPR latent-factor record](https://cepr.org/publications/dp12926). Their narrow methodological descriptions match the note: proportional costs support threshold/inaction behavior in the cited single-market setting; covariance-dominant PCA can miss expected-return-relevant weak factors; attention factors are a much larger proposed architecture rather than a small improvement established for this simulator.

Direct NBER retrieval returned HTTP 403. A subsequent search retrieved the indexed primary [NBER 24540 abstract](https://www.nber.org/papers/w24540) and the [SSRN 3032013 record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3032013); these support the distinction between characteristic-instrumented dynamic loadings and characteristic-associated intercepts. The versions report different empirical factor counts, as the note already acknowledges. This does not support importing either count into the simulated market.

The indexed primary [Flint–Vermaak SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3986499) concerns the persistence of factor exposures and says that expected-return implications also require risk-premium estimates. The note correctly refuses to identify this with predictive-alpha decay. Its label-maturation rule `s+H <= t-1` is correct for the stated forward target. No full manuscripts, real-market Sharpe estimates, or independent reproductions are claimed by this cross-review.

The proposed decomposition is a narrower explanatory exercise than IPCA, weak-factor optimization or a new residual learner. It can clarify where the frozen policy's realized P&L is recorded under one prespecified, causally updated factor-span construction. Its correlation loadings refresh every 21 observations, but daily marginal-variance rescaling can change the final span between refreshes. It cannot by itself determine whether those earnings are risk compensation, stock-specific mispricing or durable alpha.

## Implementation and execution review

The separate prospective `verification/FROZEN_ATTRIBUTION_E2E_PLAN.md` has now been read before the implementation exists. It specifies 420 synthetic days, sixteen Hadamard stock directions, eleven complete-period residual frequencies with distinct amplitudes, the top-ten known factor span, changing target weights, and all three nonzero known P&L components. This resolves the concern that a purely additive identity could pass a meaningless projection. The altered-future case begins at row 337, a refresh boundary, and explicitly checks that row's prior-estimated span against its changed realized return. Repetition, truncation, degenerate risk, wrong manifest digest, tampered bytes, malformed indices and falsified gross accounting are also declared prospectively. These are useful independent whole-workflow expectations rather than component tests that mirror the implementation.

The 404-line `tools/verify_frozen_attribution.py` was then reviewed while the implementation was being prepared. Its oracle is the independently specified Hadamard projection and never imports the implementation or helper risk estimator. It explicitly checks all three nonzero components, rank, opening-target indexing, current-day prior-estimation boundary, exact protected prefixes, original fee preservation, fixed stage summaries, null degenerate ratios, output hashes and unchanged handoff. Each scenario runs in a fresh subprocess. The malformed inputs are new synthetic packets with deliberate corruption; actual research evidence is not rewritten. No blocking mathematical or control-flow defect was identified in this verifier review, and no extra test was introduced by this reviewer.

The preserved `evidence/frozen_attribution_red_001` records the missing-implementation stage with six checks and one subprocess. Its status is `EXPECTED_RED_MISSING_IMPLEMENTATION`; the controller succeeds because the missing tool is expected, not because an attribution ran successfully. The original rerun path later contains the implemented tool, so reproducing that absence requires the original preimplementation checkout or an explicit fresh nonexistent `--implementation` path. That portability distinction should be documented separately; the original evidence must not be rewritten to make its past environment appear current.

Implementation source and the executed green synthetic workflow remain pending. At this stage no attribution tool source, successful attribution result or canonical numeric attribution is approved or represented as executed.
