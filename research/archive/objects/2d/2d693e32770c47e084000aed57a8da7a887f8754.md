# Exploratory notes, causality review and frozen-portfolio attribution

27 October 2026, Europe/Paris. This follow-up preserves the selected C09 strategy
and adds an explanation of its realized returns. It follows the completed
[protected research cycle](CONTINUED_RESEARCH_20261027.md), rather than reopening
model selection on the now-exposed audit. There is no calendar execution schedule.

## Decision and new finding

**Retain the tested C09 handoff. Its audit result is positive under the supplied
accounting model, and its earnings are materially associated with common
stock risks beyond the equal-weight market.** Under the single prespecified
rank-ten attribution, the audit's annual arithmetic gross return consists of
about 7.75 percentage points from the residual-factor span and 2.26 points from
the remainder, before 0.33 points of full trading costs. The factor component was
much smaller in validation. Describing C09 as purely stock-specific alpha would
overstate what the evidence establishes.

The current candidate is the longer-memory additive model: all thirteen linear
characteristics and their centered squares, ridge shrinkage, a 1,008-day
coefficient-estimation half-life, a prior-estimated market-beta constraint, and
diagonal residual risk with drift-aware linear trading costs. The full model
definition and limitations remain in the unchanged [handoff note](../handoff/strategy.py).

The repository already contained a more advanced checkpoint than the early chat
excerpt: twelve discovery configurations, frozen validation selection, the sole
selected audit, and exact clean-folder execution were completed in
`4e2a17816ce674c6a781771ca1e6cbe24c1d19c6`. This follow-up recovered that state and
independently checked it. It did not recreate those observations as new trials.

| Original completed evidence | C09 result | Interpretation |
|---|---:|---|
| Discovery net Sharpe, 1,762 observations | 0.700155 | Development result after a twelve-policy research process |
| Pooled validation net Sharpe, 1,007 observations | 0.659210 | Selected by the frozen rule; C06 scored 0.398603 |
| Separate audit net Sharpe, 755 observations | 1.799231 | Positive evidence for the already selected, unchanged policy |
| Audit annual arithmetic net return / volatility | 9.6761% / 5.3779% | Supplied accounting convention, after full fees |
| Audit realized net-market beta | 0.005666 | Required empirical market-exposure check |
| Audit annual costs / maximum drawdown | 0.3331% / 7.0197% | Observed costs and path risk in that sample |

The prescribed audit bootstrap ranges for net Sharpe were [0.655, 3.172] and
[0.630, 3.032] for 21- and 63-observation blocks. Earlier validation ranges and
the paired finalist difference included zero. These are conditional empirical
percentile ranges, not probabilities of future profitability or a correction for
every research decision. The [original report](CONTINUED_RESEARCH_20261027.md)
retains the complete comparison and uncertainty conventions.

## What the supplied notes are worth

The [original attachment](user_exploration_notes_20261027.md) is preserved byte
for byte, including its distinction between the user's `[me]` points and outside
reviews D1/D3. It explicitly says that returns, characteristics and figures had
not been inspected. Its value is methodological scrutiny and a hypothesis list;
it is not independent numerical confirmation of the market findings.

The strongest points are the matured-label boundary, dependence between
stock-day observations, market beta versus dollar neutrality, position drift,
and the distinction between proportional costs and quadratic-cost control
formulas. Those issues are addressed in the existing implementation and evidence.
The notes also motivated the new examination of common-factor earnings below.

Several claims need narrower wording:

| Claim in the notes | Correction and implication |
|---|---|
| A strong same-day characteristic/return link means the characteristic uses returns | Shared states and publication conventions can also produce the correlation. The causal one-day lag remains necessary, but the simulator's mechanism is not identified. |
| Marginal sign changes mean the true effect changes | With fixed joint coefficients, changing predictor covariance can change a marginal sign. Fast adaptation is not justified by that observation alone. |
| An equal-weight market overlay ignores stock betas | An overlay sized from the book's estimated beta can hedge beta correctly. Its weaknesses are trading costs, cap violations and failure to optimize jointly, not mathematical impossibility. |
| Ignoring off-diagonal covariance is wrong | A diagonal estimate is a strong regularization choice with omitted-risk costs. Richer estimates can also add estimation error. C09 versus C06 does not isolate covariance alone. |
| Each stock has an independent no-trade band proportional to cost | Equality constraints couple the decisions through their multipliers. The selected gross-cap scaling can also disturb the optimizer's pre-scale inaction decisions. |
| Annualized Sharpe differences below about 0.3 are mostly noise | The quoted error expression mixes sampling frequencies, and paired differences have their own uncertainty. Use the recorded paired daily-block analysis. |

For example, under a fixed centered linear model,

\[
\operatorname{Cov}_t(X_j,Y)=\sum_k\beta_k\operatorname{Cov}_t(X_j,X_k).
\]

A marginal sign reversal therefore need not be a structural coefficient reversal.
Likewise, C09's 1,008-day learning half-life, the characteristic's autocorrelation,
the future payoff's decay, and the fixed twenty-day cost-control horizon are
different quantities. None should be substituted for another.

The [full notes review](USER_NOTES_REVIEW_20261027.md) supplies the beta-overlay
formula, constrained no-trade condition, daily-to-annual Sharpe-error derivation,
and a point-by-point map to completed and unexecuted work. It also distinguishes
the employer's stated runtime estimate for its particular naive cvxpy example
from an unsupported general runtime claim.

## What the literature changed

SSRN, arXiv and Alpha Architect were used to identify methods and competing
explanations, with technical claims traced to primary sources. Access limitations
are retained in the [follow-up review](LITERATURE_FOLLOWUP_20261027.md).

**Characteristic-associated returns may reflect changing factor exposures.**
Kelly, Pruitt and Su's [Characteristics Are Covariances](https://www.nber.org/papers/w24540)
models observable characteristics as instruments for dynamic latent loadings.
Its framework distinguishes that channel from a characteristic-associated
intercept. The implication here is a hypothesis, not a claim that this simulator
implements IPCA: blindly projecting out every common direction may remove useful
expected return, while treating every characteristic association as independent
stock-selection alpha is also unwarranted.

**PCA variance is not the same as predictive relevance.** Lettau and Pelger's
[Estimating Latent Asset-Pricing Factors](https://cepr.org/publications/dp12926)
shows why ordinary PCA can miss low-variance factors important for expected
returns. The negative C10 rank experiment is evidence about that particular
change; it does not exhaust all conditional-risk hypotheses. This distinction
does not justify an unrestricted search for profitable low-variance directions.

**Information decay must refer to the object being measured.** Alpha Architect's
[information-decay discussion](https://alphaarchitect.com/information-decay/)
led to Flint and Vermaak's [primary study](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3986499).
That work concerns the persistence of factor exposures; expected-return
implications also need risk-premium estimates. Feature autocorrelation alone
does not establish how long predictive payoff survives. The linear-cost
[de Lataillade et al. paper](https://arxiv.org/abs/1203.5957) supports threshold and
inaction behavior within its stated setting, without providing a turnkey
solution to this thousand-stock constrained portfolio.

The earlier literature-informed local-additive experiment, C12, is already a
recorded negative result: net discovery Sharpe 0.625698 versus 0.637567 for its
C02 parent. Its fixed local hinges did not earn validation admission. Literature
was a source of falsifiable questions, not a reason to rescue the model by
choosing new knots, penalties or feature subsets after the result.

## New attribution: how it was defined

The [prospective plan](FROZEN_ATTRIBUTION_PLAN_20261027.md) was published in
`27fdb7f0c28f2db3474ecb712eb5d013e4182c46` before implementation. The completed
synthetic checks, independent source review and root release were published in
`49fc43f2489f4a75050702f1f2297413d7abe088` before the actual attribution.

The calculation reads C09's existing targets and the canonical return ledger.
It never calls a forecast or rebalance and does not generate another policy.
For earning day `t`, opening weights are `targets[t-253]`. Risk estimates use
only `R[:t]`. The explanatory span is the already examined C04 construction:
rank ten, trailing 252 days, factor shrinkage 0.5, correlation-loading refresh
every 21 days, and daily rescaling by current prior-estimated marginal variance.
No rank, window or subperiod was selected from attribution results.

Let \(w_t\) denote the opening book, \(m_t\) the realized equal-weight return,
\(b_t\) the prior beta estimate, and \(Q_t\) an orthonormal basis for that
prespecified loading span. Define \(e_t=r_t-b_tm_t\). The exact gross accounting is

\[
w_t^\top r_t
= (w_t^\top b_t)m_t
+ w_t^\top Q_tQ_t^\top e_t
+ w_t^\top(e_t-Q_tQ_t^\top e_t).
\]

The three terms are estimated market exposure, the residual-factor component,
and the remainder. Full original fees remain a separate subtraction. The day's
realized factor scores are used for after-the-fact attribution; they are not
trading inputs. A tiny estimated-market term is partly constructional because
the same prior beta estimator defines C09's hedge. Original realized net beta
remains the separate empirical exposure check.

## Actual attribution results

All values below are annual arithmetic percentage-point contributions to the
original portfolio return. They are additive accounting components of one
portfolio, not separately tradable strategies with separately allocated fees.

| Component | Discovery | Validation | Audit |
|---|---:|---:|---:|
| Estimated market component | Approximately 0 | Approximately 0 | Approximately 0 |
| Residual common-factor span | +3.1537 | +1.4153 | **+7.7465** |
| Remainder | +2.2244 | +1.4694 | +2.2627 |
| Total gross return | +5.3781 | +2.8847 | +10.0092 |
| Full original trading costs | −0.5880 | −0.2088 | −0.3331 |
| **Original net return** | **+4.7901** | **+2.6759** | **+9.6761** |

Source: [actual attribution summary](../evidence/frozen_attribution_real_001/summary.json)
and its complete `daily_attribution.csv`. The original stage masks and counts
remain 1,762 discovery, 1,007 validation and 755 audit observations. The two
boundary observations outside those masks remain in the full 3,526-row ledger.

The factor component's contribution to gross-return variance, measured as
`Cov(component,gross)/Var(gross)`, is 71.01% in discovery, 52.62% in validation
and 67.38% in audit. The remainder's corresponding contributions are 28.99%,
47.38% and 32.62%. These are additive covariance allocations that include
cross-component covariance. In general they may be negative or exceed one;
they are not independent or PCA-explained risk shares.

**The important interpretation is the difference in composition.** The audit's
larger gross mean is concentrated in the residual-factor component. The
remainder is positive in all three stage summaries and its means are more
similar, but no significance or durability claim follows from those signs.
The assignment's market-beta condition does not require neutrality to every
other factor, so common-factor earnings are not disqualifying. They do expose
an important dependence of the favorable audit on realized common-factor
conditions.

This diagnostic does not identify a risk premium, economic mispricing, or the
simulator's true factors. The remainder may contain omitted common risks,
nonlinear exposure and estimation error. Removing the displayed factor
component would require different holdings and costs; subtracting its reported
mean is not a valid net-performance counterfactual. This follow-up admits no
such rehedged policy and makes no component-Sharpe or component-significance
claim.

## Verification, information exposure and deliverable

The independent E2E plan and executable verifier preceded the attribution tool.
The missing-tool stage is preserved as an expected red record. The first
implemented synthetic workflow passed 258 checks across nine fresh processes.
Its independent Hadamard/Fourier oracle has nonzero market, top-ten-factor and
eleventh-direction remainder contributions. It tests target indexing, the
current-day risk boundary, exact repeated/future-altered/truncated prefixes,
zero-variance behavior and deliberately corrupted packets. The source reviewer
also reconciled 278 saved artifact identities. These are engineering results,
not actual-market alpha evidence.

The one actual attribution completed all 3,526 economic rows with zero strategy
executions. Its per-row scalar-dot calculation of opening target times realized
return matched the original gross ledger exactly. Maximum component accounting error was approximately
\(2.08\times10^{-17}\). The factor rank stayed ten and cached correlation
loadings were at most twenty days old. The complete input identities, frozen
helper copies, expectations, commands and logs remain in the evidence packet.
See the [source and synthetic review](../reviews/FROZEN_ATTRIBUTION_SOURCE_REVIEW.md)
and the separate [actual-output reconciliation](../reviews/FROZEN_ATTRIBUTION_ACTUAL_REVIEW.md).
That independent readback passed all 146 checks, including nineteen output-file
identities, eleven consumed-input identities, the original stage metrics,
cutoff/refresh records and unchanged policy files. Its independently batched
targets-times-returns calculation agreed within \(3.82\times10^{-17}\), without
refitting factors or executing the policy.

The fresh C09 source and compact-ledger review also passed 63 checks without
executing another strategy. No new release-blocking future-data path was found.
Forecast `t` still uses `X[t-1]`, its newest completed training pair is
`X[t-2] -> R[t-1]`, and learned forecast state remains local. The recorded full
causality workflows and century-length runtime executions are prior completed
evidence, not newly rerun checks in this follow-up.

There is no finite certificate of "no overfit." Future-input alteration tests
address implementation dependence on unavailable information. Frozen choices,
negative-result retention and initially untouched chronological periods address
selection bias. All supplied periods are now exposed; another redesigned policy
could be researched honestly as exploratory work, but could not reuse the same
audit as clean confirmation. The employer's continuation remains unseen.

The selected [four-file archive](../artifacts/continual_research_C09.zip) remains
8,709 bytes, SHA256
`cba024cae44dd84b17b17dcde48e4276e677a52883220c54da455664a770b7fa`.
Neither its code nor its complete pre-audit note changed. New notes and AI
analysis are attributed in [the contribution ledger](../DECISIONS.md), without
retroactively rewriting who implemented or discovered the tested policy.
