# Current portfolio review

**Reviewer:** portfolio-research agent, independent of the original allocator author and the current alpha-model author.  
**Scope:** source and completed evidence review; no new numerical test or portfolio scoring was executed. No actual validation/audit values or supplied full-sample figures were read.

## Decision

The corrected diagonal allocator can be integrated into the first causal benchmark under its documented contract. The prior numerical verifier and source inspection support its intended normal-scale behavior; complete strategy causality, realized beta, actual-cost performance, and runtime still require E2E execution on the frozen candidate.

The next portfolio research question should be whether causal residual-covariance modeling improves an otherwise identical forecast after costs. The concrete proposed boundary is recorded in `research/PORTFOLIO_NEXT_PLAN.md`; it is not implemented or empirically approved by this review.

## Independent source readback

The corrected `at_multiplier` raises on overflow, invalid operations and division errors before accepting a clipped scalar optimum. This implements the correction requested in `reviews/portfolio_independent_review.md`: intermediate infinity cannot silently reach clipping and masquerade as a valid constrained optimum. The existing solution uses the correct cost subgradient about the supplied drifted holding, clips each scalar convex minimizer to its own box, and resolves the continuous monotone estimated-beta exposure by bracketing and bisection.

Normalizing beta on movable assets preserves its equality, handles zero/tiny/signed betas, and prevents a fixed-zero-cap asset from dominating normalization. A pure NumPy function with no mutable market state or external reads is a suitable component for the research strategy. This mathematical/source assessment does not guarantee representability for every extreme floating-point input; explicit rejection remains part of the contract.

The completed `portfolio_verify_002` artifacts report 54 passing predeclared checks and allocator-only mean 7.851 ms over 32 synthetic 1,000-asset calls. The plan/verifier/implementation order and the previous red stage are retained. These are existing results, not an independently rerun timing measurement. Whole-strategy calls and periodic work must still be timed separately.

## Design cautions for the first candidate pair

### Gross scaling changes trading behavior

The allocator optimizes the stated diagonal quadratic/L1 objective under beta and stock boxes. A postsolve multiplication of every weight by a scale below one preserves the beta equality and boxes, but generally breaks that objective's optimum and no-trade bands. If the optimizer returns `held` on a name, whole-book scaling can nevertheless trade that name. Record how often this happens before explaining low turnover as the effect of optimal no-trade regions.

A fixed risk-aversion parameter high enough to avoid routine gross clipping is a reasonable starting engineering policy. Its economic quality remains unknown until the candidate run. No parameter adjustment is made by this review.

### Beta neutrality is an estimate, not a future guarantee

Raw trailing stock beta is preferable for the first transparent comparison. If a later candidate shrinks beta toward one, enforcing only the shrunk beta equality does not imply neutrality against the unshrunk estimate unless net dollar exposure is also zero. Report both in that case. Even exact estimated neutrality can have realized net beta because exposure estimates change, residuals are imperfectly modeled, and trading costs can covary with the market.

The original requirement is about the slope of net returns, not a daily dot product. Keep the official measurement and the estimated risk-control diagnostic separate.

### Market removal leaves substantial common risk

The existing discovery residual spectrum supports a risk-model experiment. A signed mean off-diagonal correlation close to zero is not evidence of independence. In the stored diagnostics, absolute correlation and the spectrum reveal material structure. Portfolio and alpha conclusions must not treat a thousand stocks as a thousand independent bets.

### Causal training targets need historical beta timing

For the matured pair `X[t-2] -> R[t-1]`, a market-residual target should use beta available at `t-2`, before that label. It must not use a beta recomputed on the entire supplied forecast array. This is a timing requirement, separate from whether market residualization is the best statistical estimator.

### Covariance and coefficient instability are distinct

Several characteristic ICs change sign across discovery blocks. This motivates testing adaptation; it does not identify all changes as true regimes. Unmodeled common return shocks can make a slow-moving characteristic look predictive for a while. A better portfolio risk model reduces some exposure to such shocks, but an improvement in coefficient estimation would be another research intervention and deserves its own declared comparison.

## Candidate source review status

At this document's creation, `submission/strategy.py` is being implemented by another agent and has not been reviewed here. The conclusions above approve the recovered allocator component and define concrete integration cautions. They do not approve an unseen candidate or claim a causality pass.

### Subsequent independent C01/C02 source review

The completed base source has now been inspected, without an additional numerical run. The implementation agrees with the main causal requirements: at forecast row `t`, the design for its newly observed label is `X[t-2]`, the label return is `R[t-1]`, and the residualizing beta sees `returns[:t-1]` only. Prediction uses `X[t-1]`; its per-panel centering/scaling is local to that panel. All Gram/moment/coefficients stay local to forecast. Rebalance estimates its risk from the supplied prefix and consumes no object fitted from the future. The first forecast after126 matured pairs is row127.

The shared beta and marginal-variance implementation is transparent: centered trailing252 beta,20% median residual-variance shrinkage and a1e-6 floor. The gross rescale is explicitly documented and exposes its binding frequency through the read-only diagnostic dictionary. The configuration interface resets defaults and rejects unknown keys, which helps keep nominal C01/C02 settings distinct and reproducible. Source inspection supports execution of these configurations; tested numerical causality and complete-run evidence remain separate gates.

## C04 implementation handoff

The lead authorized C04 as a fixed rank10, half-retained common-risk challenger of C02. Its precise correlation normalization,21-close refresh, daily marginal-variance preservation and fallback policy were recorded before the new numerical test code and implementation. New files are `submission/factor_portfolio.py`, `submission/strategy_factor.py` and `research/configs/C04_additive_factor.json`.

The required order is preserved in `evidence/factor_build_order_001/`: plan at19:39:52 UTC, complete verifier at19:40:55 with solver/wrapper absent, expected absent-module red run at19:40:59, then implementation at19:42:06. These are tool-clock provenance timestamps, not a newly inferred submission deadline. The verifier SHA-256 is `f510519c06aa8fe243505f1600885721357bc6acb8904c894280a0c1b60a1684` and was unchanged during the completed numerical run.

`evidence/factor_verify_001/` completed with exit0 and73 passing checks. It includes an independent dense KKT solution, six small primal epigraph reference optimizations, nonzero costs and drifted holdings, boxes and signed/zero beta, factor sign/rotation invariance, a known1,000-stock optimum, input rejection and deterministic repeats. The eight recorded single-core synthetic solver calls averaged11.87ms, p95 14.14ms, maximum14.93ms. This is solver-only evidence, excludes actual factor estimation and forecast, and makes no alpha-performance claim.

This agent wrote both the new C04 implementation and its preimplementation verifier, so this handoff is **not independent approval of C04**. Another agent has been asked to review its mathematics, chronology and evidence. The original scorer's complete workflow, frozen-config causality, refresh-inclusive runtime, fallback frequency and economic comparison still need execution by their assigned owners. No C04 market scoring was executed by this agent.

### Independent review correction

The alpha-model agent's independent source review found the fixed C04 mathematics and chronology correct, plus one generic numerical issue: outer-dual beta normalization included fixed-zero-cap assets. An irrelevant huge beta there could overflow normalization and produce `0*inf` in the Hessian. The fixed C04 uses a strictly positive scalar cap and cannot reach this path, but the generic API was corrected to normalize only movable assets, matching the unchanged inner allocator.

The correction adds no isolated test. The **same** preimplementation verifier completed again in `evidence/factor_verify_002/`, exit0 and73 passing checks. The current helper SHA-256 is `60af66f9797585fec4189206c50481bfd1d3554beb6442ed5c19b2399ce375e5`. The corrected run's eight solver calls averaged15.11ms, p95 19.02ms, max20.29ms. The previous run remains preserved; variation in recorded wall timing is not a strategy performance result. Independent readback and final review are recorded by the other agent in `reviews/factor_independent_review.md` when completed.
