# V2 follow-up review: the beta control works; the alpha interpretation is not settled

28 October 2026, Europe/Paris. Reviewed source:
[`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`](https://github.com/hlemonnier/continual-research-takehome/commit/ce3fe4e76271709422165d6f24e2fbecd9d0fe07),
`v2-factor-risk`. This follows the independent review of `afed8d0` and the
review commit `4621880`. All historical periods are already exposed.

## Decision

**Keep V2 as the current candidate under the recorded rules. Accept the useful
engineering fixes and the faithfully executed negative experiments. Preserve
B05 as a controlled research instrument, without promoting it after seeing its
result. Correct the scientific claims before using the updated handoff note.**

The strongest new evidence is B05 versus B0, which changes only the beta target
inside the corrected pipeline. My independent readback finds that the market
explains **99.926% of the variance of their incremental net return**. Increasing
the target by .05 changes realized beta by .05024 and adds approximately .72
percentage point of annual arithmetic return, almost entirely market carry.
This is useful exposure control; it has not created a new selection signal.

In the reported full-sample regression metric, both versions undershoot their
target by approximately .014. Fresh exact-package replays establish that no gross
cap binds and the estimated-beta equality is satisfied to about 7e-13. Trading
cost covariance is also much too small to explain the offset. The remaining
question is exposure-model calibration, including horizon and conditional
mean/exposure effects; no historical solver failure was found. The next
specified measurement is therefore **one-day hedge error on
the actual frozen portfolios**, followed by a coherent raw-risk reconstruction.

No new strategy candidate was implemented or selected in this review. The next
handoff is [REVIEWER_NEXT_DECISION_20261028.md](../research/v2/REVIEWER_NEXT_DECISION_20261028.md).

## 1. Independent evidence and reproduced results

All seventy changes since the prior review commit were retrieved at the pinned
head and checked against their Git blob identities. I independently verified all
29 committed five-row daily ledgers: finite data, identical earning indices
253..3778, net=gross-cost, and market returns matching the original CSV. The four
new candidates' JSON performance figures reproduce from those ledgers.

| Policy | Full net Sharpe | Discovery / validation / audit | Net beta | Ex-post market-residual Sharpe |
|---|---:|---|---:|---:|
| C09 | .884811 | .700 / .659 / 1.799 | .008838 | .863167 |
| V2 | **1.242503** | 1.098 / 1.657 / 1.148 | .046496 | 1.082722 |
| R27 beta risk | 1.167016 | 1.073 / 1.385 / 1.359 | .025947 | 1.069159 |
| Matched diagonal | .937547 | .690 / .775 / 1.859 | .098067 | .894427 |
| Corrected beta, target 0 (B0) | 1.044469 | 1.018 / 1.161 / 1.106 | -.013855 | 1.100678 |
| Corrected beta, target .05 (B05) | 1.230593 | 1.129 / 1.490 / 1.339 | .036383 | 1.098880 |

The last column is a descriptive regression statistic, not a traded neutral
strategy. Its interpretation is addressed below. Stage masks remain the original
ones, with two boundary observations retained in the full sample but excluded
from the stage comparisons.

Paired 63-day moving-block percentile intervals, 2,000 draws and seed 20261027,
give the following net-Sharpe differences against V2:

| Alternative minus V2 | Point difference | 95% range |
|---|---:|---:|
| R27 | -.07549 | [-.18474, +.02567] |
| Matched diagonal | -.30496 | [-.76200, +.05655] |
| B0 | -.19803 | [-.34254, -.05532] |
| B05 | -.01191 | [-.10884, +.07549] |

The fixed 21- and 126-day sensitivities are also retained. These are fixed-policy
comparisons under block-resampling assumptions. They do not correct prior model
selection, prove stationarity, or turn exposed history into new validation.
For B05, the difference is unresolved; statistical equivalence has not been
demonstrated. The recorded point-estimate rule nevertheless clearly retains V2.

Sources: [readback plan](../evidence/v2_followup_review_20261028/PLAN.md),
[independent calculations](../evidence/v2_followup_review_20261028/ledger_readback.json),
[verified source identities](../evidence/v2_followup_review_20261028/download_manifest.json).

### Latest code was replayed, not inferred from stale verification logs

The committed real-data engineering verification predates the later affine-beta
extension. To close that gap, I ran V2, B0 and B05 at the current pinned head in
three fresh processes, with unchanged source copies and the original scorer.
The CSV loader uses C-contiguous float64 arrays, matching `run_candidate.py`.
Observers return original arrays unchanged and do not advance estimation state.

Each run has 3,526 economic rows and 3,527 certified decisions. Current V2 reproduces
the original independent package to a maximum net-return difference 6.36e-12;
its daily closing gross differs by at most 2.50e-10. This is numerical agreement,
not a claim of cross-environment bitwise identity. Differences from Claude's
committed research ledgers are at most 3.44e-10 in daily economic fields; source
identity and every actual difference are retained. No runtime claim beyond the
instrumented replays is made; the century gate was not rerun.

Sources: [latest-package plan](../evidence/v2_followup_review_20261028/LATEST_PACKAGE_REPLAY_PLAN.md),
[V2 replay](../evidence/v2_followup_review_20261028/replay_V2_002/summary.json),
[B0 replay](../evidence/v2_followup_review_20261028/replay_B0_002/summary.json),
[B05 replay](../evidence/v2_followup_review_20261028/replay_B05_002/summary.json),
[direct old/new V2 comparison](../evidence/v2_followup_review_20261028/latest_v2_vs_original_direct.json).

## 2. New finding: B05 adds an almost pure market-return increment to B0

B05 and B0 share corrected forecast labels, fitted mean forecasts, residual-risk
estimation and hedge estimator. Their target is the controlled difference; all
subsequent changes in holdings, drift and costs are legitimate consequences.

Regress their daily net-return difference on an intercept and the market:

| Incremental B05-minus-B0 statistic | Independently calculated value |
|---|---:|
| Realized beta increment | .05023853 |
| Market R-squared | .99926136 |
| Annual arithmetic net-return increment | +.716801 percentage point |
| Fitted market contribution to that increment | +.727450 percentage point |
| Remaining intercept, annualized | -.010649 percentage point |
| Residual annual volatility | .019342% |

The target mechanism responds almost one-for-one. The intervention's extra return
is market exposure rather than an improvement in the underlying selection
forecast. The tiny negative residual intercept should not be oversold as a new
significant anomaly; the main economically large fact is the near-perfect market
tracking. This is an incremental policy comparison. It is not a separately
executed market overlay with independently charged trading/financing costs.

B05-versus-V2 is a different experiment. Changing betas in labels, risk residuals
and the hedge changes several parts of the policy. An unchanged standardized
beta feature column does not keep fitted coefficients fixed after the response
variable changes. The claim that this isolates explicit versus implicit exposure
is too strong. B05-versus-B0 is the clean contrast.

## 3. Relative control is strong; the reported exposure level still misses its target

Both corrected candidates satisfy the stated full-sample tolerance of .02. That
acceptance check is real. It does not make realized exposure exact:

| Policy | Target | Realized net beta | HAC10 reference interval | Largest pre-gross exposure |
|---|---:|---:|---:|---:|
| B0 | 0 | -.013855 | [-.022583, -.005127] | 2.39622 |
| B05 | .05 | .036383 | [.027678, .045089] | 2.39402 |

The intervals are normal/HAC reference intervals for the static regression,
conditional on that specification and exposed selection; they are not universal
confidence guarantees for latent conditional betas. The stable negative offset
also appears in all three stages. Conditional-mean/timing effects can also affect
an unconditional regression beta, so this offset alone does not uniquely identify
an error in latent next-day conditional beta.

Crucially, actual replays show zero gross-scaling calls in both policies, versus
a gross limit of 5. Maximum post-trade estimated-beta target errors are 6.38e-13
and 6.69e-13. Net versus gross regression beta differs by only approximately
1.5e-5. Neither optimizer feasibility, final scaling nor fee covariance explains
the .014 level error in these runs.

The independent causal-beta reviewer exactly reproduced the annual diagnostic:
MSE falls from .04313413 to .03929553, about 8.9%, and the corrected estimate wins
on 139/144 dates. The dates step 21 days while outcomes span 252 days, sharing 231
days between adjacent windows. This is not 144 independent successes or 97%
probability of correct future control. Reassuringly, all twelve predeclared
phase cohorts with nonoverlapping future windows within each cohort have negative
mean MSE differences; different cohorts overlap one another. No independence or
significance claim is made from that sensitivity. Including the omitted final
legal grid date produces 145 observations and changes no conclusion.

The diagnostic predicts noisy next-year stock-beta estimates with equal stock
weights. The portfolio needs next-day exposure of endogenous signed positions.
For the conditional error second-moment matrix M=E[delta delta'], stock-average
MSE reflects trace(M)/N while a published frozen portfolio's exposure MSE is w'Mw,
including bias. These are different losses.

Finally, “true betas drift 17% toward one” is not identified. A slope below one
also occurs with constant latent betas and noisy measurements. Claude's own
constant-true-beta simulation illustrates that possibility. The supported result
is improved prediction of future-window beta estimates, not a measured 17%
physical reversion of true betas.

Source: [independent causal-beta review](V2_FOLLOWUP_CAUSAL_BETA_20261028.md).

## 4. Centering does not delete the beta-error direction

This is a substantive mathematical correction. With the equally weighted market
and the same OLS window for every stock,

\[
\overline{\widehat b}=1,
\qquad
\overline{r-\widehat b m}=m-\overline{\widehat b}m=0.
\]

The independent direct-window calculation confirms maximum deviations of 6.67e-16
for mean beta from one, and 1.93e-17 for the raw residual cross-sectional mean.
The explicit demeaning step is almost redundant in this construction.

Under the illustrative shrinkage relation, beta error has loading

\[
\delta=\eta(\mathbf1-\widehat b),
\]

which is itself centered. Its common component `delta*m` survives demeaning.
R26 can represent its projection into the characteristic span; specific risk
also captures some individual unexplained variation, though not the full common
covariance. R27 is centered too and can add this direction explicitly.

The valid omitted-span observation is that 93.203% of the beta column's squared
Euclidean norm remains outside D26, on average. This does not mean 93.203% of
portfolio risk is omitted or that R26 sees none of the direction.

The beta-factor market regression itself reproduces independently, using direct
rolling OLS and Frisch-Waugh-Lovell rather than the submitted joint-regression
implementation. The joint factor's market slope is -.048013, with HAC10 interval
[-.052796,-.043231]. Its intercept is -.10393bp/day, with interval
[-.36996,+.16210]bp/day. Fixed longer-lag sensitivities leave the same qualitative
conclusion: substantial market comovement; unresolved constant intercept.

A significant slope does not uniquely identify estimation error as the only
cause, and a nonsignificant intercept does not establish no conditional premium.
The two channels may coexist. The zero-alpha simulation is a useful constructive
example, not identification of the simulator's hidden generator.

Source: [factor readback](../evidence/v2_followup_review_20261028/factor_readback.json).

## 5. The 1.1 market-residual Sharpe is not a demonstrated pure stock-selection strategy

The code fits one full-sample market coefficient, then computes Sharpe on
`net_return-beta_hat*market`. It retains the fitted intercept. That is a useful
descriptive appraisal statistic, but the coefficient was not known at every
decision and no additional hedge costs or changed portfolio-drift path are
scored. A one-market residual may also contain other common premia, nonlinear
market exposure or conditional timing effects.

Thus “market-residual Sharpe approximately 1.08–1.10 in this sample” is supported.
“A tradable pure stock-selection edge of 1.10 is established” is not. V2's fitted
market mean contribution of .6733 percentage point to 4.7550% annual arithmetic
return is a valid sample decomposition; differences in Sharpe are not additive
profit contributions.

B0 really failed its prespecified 1.083 threshold. That compares an actually
traded policy with a hindsight-adjusted series, a deliberately demanding
development bar. It is not a scientific theorem that causal neutrality destroys
alpha. B0 still has negative market exposure in a positive-market sample.

Conditional performance evaluation is the relevant literature distinction:
[Ferson and Schadt](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1996.tb02690.x)
motivate accounting for public information and changing exposures. Their mutual
fund results are not imported into this simulated market.

## 6. Explicit beta changes the required risk accounting

For a fixed decision information set, write `r=b*m+e`, target `p=b'w`,
`c=Cov(e,m)` and `sigma_m²=Var(m)`. Then

\[
\operatorname{Var}(w^\top r)
=w^\top\Sigma_e w+2p\,c^\top w+p^2\sigma_m^2.
\]

At a fixed beta target the final term is constant across feasible positions. The
cross term generally is not. Correcting betas using a year-ahead shrinkage rule
does not establish conditional residual-market orthogonality at the next-day
decision horizon. The current engine supplies a residual-risk matrix to the
optimizer; the relevance of the omitted cross term has not yet been measured.

The mean decomposition is `w'mu_e+p*mu_m`; its market term is constant within a
fixed-target allocation. Across targets, both market mean and raw risk matter.
This explains why explicit control is useful without demonstrating an optimal
choice of target or a complete physical risk forecast.

Use the second-moment counterpart of this identity when evaluating uncentered
factor products with the `log(q)+g²/q` loss. Do not mix covariance and second
moment estimates. Estimate any added market/cross moments jointly so the final
matrix stays positive semidefinite, and disclose residual-market covariance
outside the chosen low-rank span. Merely adding a market factor with the original
raw beta has almost no effect on V2, because that same estimated beta is hedged
to zero; it is a useful invariance check, not the proposed fix.

## 7. What the two risk experiments establish

**R27 was implemented faithfully and rejected correctly.** Its frozen-book risk
loss improves on average by approximately .0368, but by-stage differences are
+ .004, -.180, +.060; the benefit is concentrated in validation. The63/126-day
intervals include zero. It fails the full net-Sharpe replacement rule. The lower
beta/net investment is consistent with repricing the added direction, but does
not prove that surrendered market carry explains the entire score decline.

**The matched-diagonal comparison is a valid policy ablation.** Greater gross
exposure, volatility and cap activation are consequences of removing off-diagonal
terms at the fixed penalty, not an unrelated confounder that invalidates the
control. It establishes a negative historical effect of that intervention.
It does not separately identify correlation geometry from endogenous sizing,
costs and caps, or prove that every V2-versus-C09 gain comes from correlations.
The paired intervals also include zero. A later geometry comparison could use
a common past-only risk budget; rescaling on full-sample realized volatility
would not supply an implementable control.

The rejection decisions remain intact. B05's small point gap makes it worth
preserving, not equivalent by proof. An equivalence claim would need a meaningful
margin specified beforehand; see [Lakens](https://journals.sagepub.com/doi/full/10.1177/1948550617697177).
Choosing that margin to encompass the observed result would move the goalposts.

## 8. Engineering disposition and remaining boundaries

Independent complete-scorer synthetic workflows confirm the restart and feature
layout fixes and the corrected-path timing. Future mutation, prefixes and
characteristic-layout changes preserve protected decisions. Original-scorer
return-layout reduction can still change gross P&L by a few 1e-18; this is recorded
as a failed strict bitwise expectation in one workflow, not as strategy leakage.

The affine-target dual, gradient and gap are correct. Retain the allocator.
Two failure-path issues remain: an ultimately `not_certified` solution is still
returned/traded, and the certificate precedes gross scaling. Scaling by a<1
changes a nonzero target to a*target. Neither issue occurred in the three fresh
actual replays, so neither explains their reported results. Require a final
post-processing feasibility check and a defined response to failed certification
before treating the nonzero-target interface as generally robust.

Git history supports plan-commit-before-result-commit ordering for both model
experiments. Within an implementation commit, saved red/green logs do not
independently establish their historical creation order. The repaired comparison
contains 25 variants; the drift sample mismatch is fixed, but exchangeability
assumptions and low-resolution/multiplicity limitations remain.

Two initial root observer launches failed at Python parsing because of one extra
brace, before importing any strategy or producing economics. The source and
logs are retained; corrected attempt 002 completed all three actual replays.
These are audit-harness failures, not failures of Claude's strategy.
[Failure record](../evidence/v2_followup_review_20261028/HARNESS_FAILURES.md).

Supporting reviews: [engineering](V2_FOLLOWUP_ENGINEERING_20261028.md),
[causal beta](V2_FOLLOWUP_CAUSAL_BETA_20261028.md),
[quantitative research](V2_FOLLOWUP_QUANT_RESEARCH_20261028.md).

## Next research decision

Freeze V2 positions and evaluate the raw versus annually corrected beta on
next-day portfolio hedge error using one common past-only mean convention.
Use V2 as the primary book and B0/B05 as fixed secondary controls. This tests
the actual decision direction and horizon, whereas the current diagnostic
tests equal-stock year-ahead MSE. The accompanying handoff fixes the loss,
sample, uncertainty conventions and interpretation before execution.

Then assess raw-risk reconstruction on those same books, including market/cross
terms, before a new allocator candidate. If these quantities are small or not
predictable, stop spending policy runs on the .012 Sharpe gap and return to
mean/covariance research. Do not add .014 to the target simply because this
sample's bias was -.014.

[Engle, Ledoit and Wolf](https://www.econ.uzh.ch/dam/jcr:28fa9939-753e-4f5c-932d-945872f30cfd/jbes_2019.pdf)
explicitly connect covariance loss to portfolio decisions; this motivates
testing the estimator on the use it serves, not importing their DCC estimator.
[Hollstein, Prokopczuk and Wese Simen](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3069518)
provide relevant beta-forecast comparisons, without validating our chosen
shrinkage rule or transferring their equity-market results to the simulator.

This review and its derivations are AI-generated research assistance. Claude's
implementation remains attributed to Claude; no applicant contributions or
submission decision are invented. Root opened the Ferson–Schadt publisher
abstract and the institutional Engle–Ledoit–Wolf full paper; SSRN and Lakens
statements are supported by primary indexed records, with direct-access limits
recorded in the supporting quantitative review.
