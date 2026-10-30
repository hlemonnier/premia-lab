# V2 allocator: independent mathematical and implementation review

28 October 2026, Europe/Paris. Reviewed snapshot: `afed8d0cb017acda151c4ea262fc30db7568a4bb` on `v2-factor-risk`. Scope: the allocator, its portfolio geometry, the supplied numerical verification and precise changes that would improve reliability or the objective. No strategy code was changed. The source review is independent of Claude's implementation.

## Verdict

**The low-rank dual formulation is correct and worth retaining. The supplied numerical examples reproduce successfully. “Exact allocator” is nevertheless too broad a description of the implementation as it stands: convergence is not certified on every return path, and the final gross-cap transformation is not the optimum of the stated objective with a gross constraint.**

These are distinct judgments. The review has not established that a material allocator error explains V2's historical gain. The unchanged supplied suite passed all 38 checks in this environment. The coordinator's separate end-to-end replay records factor optimality and beta residuals across the real trading path; that evidence, rather than an assumption that missing checks imply bad trades, should determine the practical severity.

The most useful engineering improvement is a cheap primal–dual certificate on the returned book, followed by a convergent repair or an explicit failure when necessary. The most useful optional mathematical improvement is to impose gross exposure inside the optimizer, if the cap actually binds often enough to affect decisions. A wholesale solver rewrite is not justified by the present evidence.

**Actual-path update:** the coordinator's unchanged-policy replay has now completed, and this reviewer independently read its raw decision records. Three of 3,527 solves exceeded the implementation's very strict factor-gradient tolerance, but the largest measured primal–dual gap was only `3.96e-18`; none exceeded the prespecified `1e-10` value flag. Every hedge met its stated tolerance, and neither the gross nor the stock caps ever bound. There is no evidence of an economically significant optimizer error in this replay. Consequently gross-cap integration is a low priority for this candidate, while risk calibration and the beta feature's economic interpretation deserve the research attention. Section 8 records the exact readback.

## 1. Independent derivation

Write `M = B L`, so the factor term is `||M' w||²`. The allocator solves

\[
\max_{|w_i|\le c_i,\ b^\top w=0}
\mu^\top w-\frac{\gamma}{2}\sum_i d_iw_i^2
-\frac{\gamma}{2}\|M^\top w\|^2
-\sum_i\kappa_i|w_i-h_i|.
\]

Because `d_i > 0`, its objective is strictly concave. Its feasible set is nonempty: `w = 0` satisfies the beta equality and every nonnegative symmetric cap. “Infeasible beta” in the supplied specification is therefore an inaccurate name for the degenerate case where beta-bearing stocks cannot move; that case can restrict the optimum to zero but cannot make this particular feasible set empty.

Introduce `z = M' w`, multiplier `lambda`, and a multiplier `nu` for the beta equality. Maximization over `z` gives `z = lambda/gamma` and a dual term `||lambda||²/(2 gamma)`. With beta normalized to `bn`, the convex dual is

\[
g(\lambda,\nu)=\frac{\|\lambda\|^2}{2\gamma}
+\sum_i\max_{|w_i|\le c_i}
\left[(\mu_i-M_i\lambda-\nu b_{n,i})w_i
-\frac{\gamma d_i}{2}w_i^2-\kappa_i|w_i-h_i|\right].
\]

This is what `allocator.py` implements. In its scalar maximization, let `s_i = mu_i - M_i lambda - nu bn_i`. The unconstrained optimum is

\[
w_i=\begin{cases}
(s_i-\kappa_i)/(\gamma d_i),&s_i-\gamma d_i h_i>\kappa_i,\\
(s_i+\kappa_i)/(\gamma d_i),&s_i-\gamma d_i h_i<-\kappa_i,\\
h_i,&\text{otherwise}.
\end{cases}
\]

Clipping that one-dimensional concave optimum to the box is valid, including when drift has put the held position outside the new cap. The factor and hedge gradients are

\[
\nabla_\lambda g=\lambda/\gamma-M^\top w,
\qquad \partial_\nu g=-b_n^\top w.
\]

Away from a kink, with `A = [M, bn]`, the Hessian is

\[
A^\top\operatorname{diag}\left(
\frac{\mathbf{1}\{\text{trading, inside cap}\}}{\gamma d_i}
\right)A+\operatorname{blockdiag}(I/\gamma,0).
\]

The source's gradient, Hessian and factor regularization agree with these expressions. At a band or cap boundary a generalized derivative is needed; selecting one of the endpoint derivatives is not itself a mathematical error. The small Hessian damping and Armijo search are sensible numerical choices for the resulting piecewise-quadratic dual. Passing `L`, rather than an arbitrary covariance, also makes the represented factor covariance positive semidefinite by construction.

Relevant source: [allocator.py](https://github.com/hlemonnier/continual-research-takehome/blob/afed8d0cb017acda151c4ea262fc30db7568a4bb/handoff_v2/model_v2/allocator.py), especially the scalar maximization at line 67, dual at line 78, gradient at line 83 and Hessian at line 98. This derivation is the reviewer's algebra, not an additional empirical result.

## 2. The material solver weakness: a feasible answer is not necessarily an optimal answer

The main Newton loop can stop because it reaches `max_iter`, or because its line search fails. At either exit it proceeds without recording the reason or requiring the factor gradient to satisfy the requested tolerance (`allocator.py`, lines 93 and 116). The beta-only polishing stage can then change `nu` and all corresponding weights while keeping `lambda` fixed (line 120). That does enforce the beta constraint when it converges. It does **not** generally preserve

\[
\lambda=\gamma M^\top w.
\]

Consequently a cap-respecting, beta-neutral returned vector is not sufficient evidence that the joint factor-risk problem was solved. A successful monotone line search also does not prove that the fixed iteration budget reached the optimum. None of this establishes that the issue is economically material in the current replay; that requires the actual residuals.

### A certificate is available almost for free

For the returned scalar-optimal `w` and its final dual multipliers, define

\[
q=M^\top w-\lambda/\gamma,\qquad e=b_n^\top w.
\]

The difference between the dual objective and the primal objective evaluated at this vector is exactly

\[
g(\lambda,\nu)-P(w)
=\frac{\gamma}{2}\|q\|^2-\nu e.
\]

For a feasible book, this is a duality gap. With beta equality only satisfied to floating-point tolerance, log the raw exposure and the `nu e` correction separately; an insignificant negative computed gap can be roundoff or residual feasibility, rather than a violation of weak duality. A useful scale-sensitive upper error allowance includes `|nu e|`. When a feasible candidate's dual gap is small, strict concavity also bounds its distance to the optimum using `gamma * min(d)`.

**Requested change for Claude:** after beta polishing, recompute the factor residual, beta residual and primal–dual gap. Return a status describing convergence. If the factor condition fails, resume the joint solve from the polished point, or use a robust dual fallback. A silent return after exhausting iterations is inappropriate for a routine advertised as exact. The internal tolerance should be related to an economically meaningful objective gap as well as a raw gradient, rather than asserting that every tiny residual exceedance changes a trade materially.

The diagnostics themselves require matrix-vector products and scalar arithmetic, not another optimizer or another strategy variant. They can be recorded during the existing scorer workflow.

## 3. Warm starts are carried in a changing coordinate system

The factor covariance is eigendecomposed daily in `engine.py`, line 141, and its square root uses the eigenvectors as columns. Eigenvectors can change sign, rotate in a near-degenerate subspace, or change ordering. The allocator reuses the previous `theta` solely when its shape matches (`allocator.py`, line 89).

An old factor multiplier is therefore expressed in yesterday's coordinate basis. Reusing its raw numeric coordinates in today's basis is only an initial guess; it is not an invariant warm start. Correct convergence removes the discrepancy, so this is primarily a performance and convergence-robustness issue. Combined with an uncertified early exit, however, it can make the returned approximation depend on arbitrary eigenvector choices.

A simple improvement is to initialize the factor part from today's `gamma * M' h`, or transport the previous primal solution into the new factor basis. The beta multiplier also needs its normalization understood if beta scaling changes. Compare total work and final gaps before claiming one initialization is better. A future E2E test should preserve the same covariance while applying equivalent orthogonal rotations/sign changes to its square root and verify equivalent trading decisions within a specified objective tolerance.

## 4. Gross exposure belongs in the objective when it is a binding constraint

The allocator's stated problem contains stock caps and the beta equality. The engine then rescales the entire answer when gross exceeds the configured limit (`engine.py`, line 170). This preserves the equality and caps, but changes both risk and cost relative to the held book. In particular, a stock that optimally stayed at its drifted holding can be forced to trade by the rescaling. The result is not the optimum of the original objective augmented by `||w||_1 <= G`.

**Concrete improvement:** dualize the gross constraint with `eta >= 0`. Each scalar subproblem then has two absolute-value penalties,

\[
\max_{|w_i|\le c_i}\ s_i w_i-\gamma d_i w_i^2/2
-\kappa_i|w_i-h_i|-\eta|w_i|.
\]

There are only two kinks, at `h_i` and zero, plus the cap boundaries. The scalar solution remains analytic by considering intervals or candidate roots. A monotone search over `eta`, with the factor/beta subproblem solved consistently, or a coupled semismooth method can enforce the gross constraint and its complementary slackness.

This is a tractable extension of the existing structure, not a reason to move every daily solve to a general-purpose package. Its research priority depends on how often gross binds and how much extra turnover the present rescaling creates. If the cap is inactive throughout the actual path, improving it has no historical payoff and should be ranked below a substantive modeling experiment.

## 5. Two portfolio-construction interpretations to correct

### Fivefold size is a static equivalence, not a dynamic identity

If `w`, `h`, stock caps and gross cap all scale by `a`, and risk aversion changes from `gamma` to `gamma/a`, the one-period objective scales by `a`. Thus the one-period optimum scales exactly. The scorer does not maintain `h_scaled = a h` over time: it divides drifted holdings by `1 + a r_p` instead of `1 + r_p`. Future trading and costs therefore differ. The observed near-equality of Sharpe at onefold and fivefold size is an empirical result, not exact scale invariance.

The assignment rewards Sharpe and imposes a realized beta limit. Increasing book size with almost no Sharpe benefit consumes beta and loss headroom. Size should be selected from a defensible exposure/error budget; matching a visually attractive annual return is not a research improvement. This does not imply that the observed fivefold book is close to ruin, nor does it substitute a synthetic historical worst day for a future risk bound.

### A beta forecast is tightly coupled to the hedge and dollar exposure

Without clipping, the standardized beta feature is proportional to `b - mean(b)`. Under the same exact `b' w = 0` hedge,

\[
a\left(\frac{b-\bar b\mathbf 1}{s_b}\right)^\top w
=-\frac{a\bar b}{s_b}\mathbf 1^\top w.
\]

Its allocation contribution is therefore closely related to a dollar-exposure preference under that hedge. Clipping and differing numeric estimators qualify the exact identity, but do not make the relationship irrelevant.

Separately, with estimated market residual labels,

\[
e_{i,t}=r_{i,t}-\widehat b_{i,t}m_t
=(b_{i,t}^{true}-\widehat b_{i,t})m_t+\epsilon_{i,t},
\]

beta-estimation error can itself create a relationship between estimated beta and the label. For example, regression of extreme estimated betas toward one combined with a positive market mean can produce an apparent low-estimated-beta effect. This is a competing explanation, not a finding that V2's improvement is spurious. The next analysis should separate dollar exposure, residual-market exposure and the incremental expected-return information in the beta feature, using estimators based only on past data.

## 6. Existing verification independently reproduced

The original `research/v2/test_allocator.py` was executed unchanged after documenting the replay plan. No new unit tests were written. Its command, source hashes, versions, complete stdout/stderr, exit status and source-unchanged readback are in [the evidence packet](../evidence/v2_allocator_review_20261028/README.md).

Actual result: **38 supplied checks passed, process exit 0.** In the six `n=200` oracle cases, reported relative objective discrepancies were at most approximately `1.3e-10`, and the largest absolute weight discrepancy was approximately `5.0e-7`. The full-size reference weight discrepancy was `5.3e-10`; zero factor risk reproduced the baseline diagonal allocator within `2.6e-16`. The local median solve time was `0.83 ms`, with one-thread numerical libraries. Timing is specific to this environment and those problems.

Versions: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, cvxpy 1.9.3 and Clarabel 0.11.1. Dependencies were isolated under `/tmp`; production and test source hashes were unchanged after execution. The first dependency-install attempt was blocked by sandbox network permissions; the approved isolated retry succeeded. This setup event is not a failed numerical test.

The supplied cases put many of 200 stocks at caps and only a few at no-trade bands. They provide useful convex-oracle evidence for those regimes. They do not certify every input, every daily state transition, or the warm-started path on the supplied market. The brief mentions an additional no-cap/band-heavy check, but this reviewer has not treated an absent saved execution as a reproduced check. Similarly, the source comment and specification assert pre-implementation ordering; replaying their present versions does not independently prove that historical ordering.

## 7. Action order for Claude

1. **Certify final optimizer output.** Add the final factor/beta/gap checks and a documented convergence/fallback result after writing the relevant E2E failure cases. Preserve the old book and results as the comparison reference. Determine practical severity from the complete trading-path diagnostics.
2. **Use the gross-cap evidence to decide whether to integrate it.** If binding and economically material, implement the extra absolute-value penalty and complementary-slackness solution. If inactive, deprioritize this change.
3. **Resolve the beta feature/hedge interaction.** A measurement-error-aware beta estimate and residual-label comparison have a clearer mechanism than adding a faster premium model merely because some marginal coefficients changed sign.
4. **Retain the factor-risk allocator architecture.** The mathematics is sound and the supplied numerical agreement reproduces. Improve its certification and objective fidelity instead of discarding it on stylistic grounds.

No new predictive experiment, candidate selection, or strategy replacement was executed in this allocator review. New empirical claims should come from the coordinator's separate end-to-end record and explicitly proposed future experiments.

## 8. Actual-path readback and resulting priorities

The source of these additional observations is the coordinator's independently executed, unchanged V2 package and original scorer, in [the real replay packet](../evidence/v2_real_review_20261028/run_v2_001/summary.json). The observational harness was reviewed before execution: coefficient row alignment, the 3,527 decisions versus 3,526 scored rows, beta decomposition, dual-gap algebra and the prior-close risk alignment were checked. One plan/code naming discrepancy in the absolute-gap flag was corrected before execution. Its executed copy matches the final harness. This reviewer's source readback record is [saved separately](../evidence/v2_allocator_review_20261028/replay_harness_source_review.json).

The decision CSV was then independently aggregated with the ordinary CSV reader. Its SHA256 is `3a6ee63d7c8063d248785354becc08d2d0c11ed98c767831097c5b23825777f1`; the complete readback is [recorded here](../evidence/v2_allocator_review_20261028/real_replay_independent_readback.json).

| Observation | Independent readback |
|---|---:|
| Original allocator calls | 3,527 |
| Factor residual above the code's own tolerance | 3 |
| Affected zero-based decision rows | 385, 1293, 3674 |
| Maximum factor residual | `6.9721901981635885e-12` |
| Hedge residual above the code's own tolerance | 0 |
| Absolute computed duality gap above `1e-10` | 0 |
| Maximum / minimum computed gap | `3.957337929572091e-18` / `-5.421010862427522e-19` |
| Maximum direct gap-versus-identity discrepancy | `6.510761824278542e-19` |
| Calls with gross rescaling | 0 |
| Maximum unscaled gross versus cap | `2.622571370569782` versus `5` |
| Maximum absolute stock weight versus cap | approximately `0.01478144388566135` versus `0.05` |

The actual objectives ranged from about `6.80e-5` to `6.26e-4`. The reported gaps are negligible on that scale. Small negative computed gaps and the direct-versus-algebraic discrepancy are at floating-point subtraction scale. The three strict residual exceedances do demonstrate why returning without checking final residuals is a real code-quality issue, but they do not demonstrate a material trading error or explain V2's historical improvement.

Two more results matter economically. First, the beta-feature forecast contribution is overwhelmingly its net-dollar term: the coordinator's mean direct contribution is `6.7308e-5` per day versus `6.7841e-5` for the dollar term, with the difference almost entirely clipping. Mean net dollar exposure is approximately `0.40086`. These are contributions to the model's forecast objective, not realized profits or a stand-alone beta-feature Sharpe.

Second, the current risk objective's mean predicted portfolio second moment is approximately `2.1819e-6`, while the corresponding realized squared gross return averages `5.8377e-6`, a ratio of `2.6755`. This causal risk-forecast comparison is descriptive on already selected positions. It establishes that the model used for sizing substantially understates this sample's realized second moment; it does not by itself identify the cause or justify a particular alternative allocation. The factor scale should therefore be described as a chosen relative risk penalty, not automatically as a calibrated covariance estimate.

The resulting priority is clear: retain the allocator, add cheap convergence certification, and move the substantive research effort to risk/premium calibration and beta-measurement error. Integrating an inactive gross constraint or rewriting an already accurate solver would consume work without addressing the strongest observed weakness.
