# V2 independent review: reproduced improvement, unresolved mechanism, next research

28 October 2026, Europe/Paris. Reviewed branch: `v2-factor-risk`, commit
[`afed8d0cb017acda151c4ea262fc30db7568a4bb`](https://github.com/hlemonnier/continual-research-takehome/commit/afed8d0cb017acda151c4ea262fc30db7568a4bb).
Comparator: unchanged C09 at `fb8c7024edbc432262709965dbeadc3da02547e1`.

## Decision

**Continue developing V2. Its historical improvement is reproducible, and its
characteristic-conditioned risk model is a worthwhile advance. The current
mechanistic explanation and statistical confidence are overstated.** Fix the
two reproduced lifecycle/layout defects, retain the allocator, and direct the
next research toward the beta-derived net-investment payoff and the covariance
model that prices its risk. A Kalman filter is not the first change I recommend.

This review independently retrieved all 48 branch additions and verified their
Git blob identities; recovered the original input archive and checked its
canonical CSV hashes; replayed the exact packaged V2 and C09 with the unchanged
scorer; and used three separate reviewers for quantitative reasoning, allocator
mathematics, and causality/reproducibility. Production strategy files were not
modified. Newly written code is confined to observational audit workflows.

The complete supporting reviews are [quantitative research](V2_QUANT_RESEARCH_REVIEW_20261028.md),
[allocator](V2_ALLOCATOR_REVIEW_20261028.md), and
[causality](V2_CAUSALITY_REVIEW_20261028.md). The implementation handoff is
[REVIEWER_NEXT_EXPERIMENTS_20261028.md](../research/v2/REVIEWER_NEXT_EXPERIMENTS_20261028.md).

## 1. The reported trading result is real in the supplied historical sample

The independent replay used the original CSV loader, float64 arrays and the
literal packaged configuration: gamma 200, 5% stock caps, gross cap 5, cost
horizon 20, factor scale 0.3. It did not substitute Claude's research module.

| Metric | Original C09 | Packaged V2 |
|---|---:|---:|
| Full-run net Sharpe | 0.884811 | **1.242503** |
| Discovery net Sharpe | 0.700155 | **1.098002** |
| Validation net Sharpe | 0.659210 | **1.656859** |
| Previously reserved audit net Sharpe | **1.799231** | 1.147558 |
| Full annual arithmetic net return | 5.1845% | 4.7550% |
| Full annual net volatility | 5.8595% | **3.8270%** |
| Full annual trading costs | 0.42495% | **0.17557%** |
| Full realized net-market beta | 0.008838 | 0.046496 |
| Average closing gross exposure | 0.86087 | 1.58379 |
| Mean net stock investment across decisions | 1.0066% | **40.0862%** |

Both scored 3,526 economic observations, indices 253 through 3778. The original
stage masks have 1,762/1,007/755 observations, with two boundary observations
retained in the full ledger but excluded from stage tables. Both replays match
the committed three-decimal Sharpe summaries. C09's economic fields match the
canonical ledger within `5.218048215738236e-15`; this is numerical reproduction,
not a claim of bitwise identity across the input layouts and environment.

Sources: [V2 replay summary](../evidence/v2_real_review_20261028/run_v2_001/summary.json),
[C09 replay summary](../evidence/v2_real_review_20261028/run_c09_003/summary.json),
and [independent peer readback](../evidence/v2_causality_review_20261028/REAL_REPLAY_PEER_REVIEW.md).

The improvement is mainly a more favorable return/risk/cost combination, not a
higher full-run arithmetic return. V2 wins substantially in the earlier two
stages and loses to C09 in the last one. That pattern merits explanation; neither
the pooled score nor the old audit alone resolves which policy is better over
an unknown continuation. Every V2 development period was already exposed.

### Recomputed uncertainty

The committed `comparison.json` has 22 entries and omits the selected later
factor-scale variants, although 25 variant summary files exist. Thus the brief's
selected-candidate interval lacked its committed calculation and daily ledger.

Using the newly replayed **packaged V2**, the net Sharpe difference is
`+0.3576918449`; its daily net-return correlation with C09 is `0.6954191835`.
The prespecified saved-ledger readback gives:

| Moving-block construction | 95% percentile range for V2 minus C09 |
|---|---:|
| Original 63-day endpoint convention | [−0.002030, +0.819534] |
| Corrected 63-day endpoint convention | **[−0.003168, +0.824536]** |
| Corrected 21-day blocks | [−0.035111, +0.767169] |
| Corrected 126-day blocks | [−0.032103, +0.880978] |

Each uses 2,000 shared-index draws and seed 20261027. The original comparator
omits the last legal block start; the corrected version uses `n-L+1` as its
upper-exclusive bound. The endpoint defect is small here. All fixed sensitivity
ranges include zero. An interval whose lower limit rounds to zero must not be
described as convincingly positive.

This is not an exact reconstruction of Claude's uncommitted interval for the
unlevered research variant. Nor does a block bootstrap remove selection across
the many inspected variants or manufacture fresh validation. Paired resampling
is appropriate to preserve cross-strategy dependence; the remaining assumptions
about time dependence, changing regimes and selection still matter. A bootstrap
positive-difference fraction is not a probability that V2 will outperform.
[Plan and results](../evidence/v2_real_review_20261028/paired_readback.json).

## 2. New finding: the beta feature largely prices net investment

The forecast adds a standardized, centered trailing beta to the 26 original
columns. The allocator hedges almost the identical beta vector. Ignoring clipping,
let `b` be that vector and `z=(b-mean(b))/std(b)`. On a feasible portfolio,

\[
b^\top w=0
\quad\Longrightarrow\quad
z^\top w=-\frac{\bar b}{s_b}\,\mathbf1^\top w.
\]

Therefore the direct beta-column term in the objective is a preference for
**beta-hedged net stock investment**. It does not need to represent an independent
stock-specific anomaly. A negative learned beta coefficient rewards a net-long
stock book under this constraint.

This identity is measurable in the existing policy, with no additional forecast
fit or changed holdings. Observing the original solves gave:

| Mean per-decision forecast-objective term | Value |
|---|---:|
| Entire forecast times target | 0.00043615795 |
| Direct beta-column contribution | **0.00006730829** |
| Net-investment term from the algebra | 0.00006784108 |
| Centered clipping correction | −0.00000053280 |
| Prediction/hedge beta difference term | approximately zero |

The beta term is 15.43% of the average predicted objective; clipping changes
the net-investment term by less than 1%. The maximum identity discrepancy is
`6.78e-20`. Mean net stock investment is about +40.1%, versus +1.0% for C09.
These are **forecast-objective and exposure descriptions**, not a claim that
15.43% of realized profits came from beta, or that the beta column alone caused
the change in net investment. Adding beta also refits all other coefficients.

### Two competing explanations we should now separate

One possibility is a useful, predictable payoff to a beta-neutral net-investment
direction. Another is error in the estimated market betas used in the labels
and hedge. In an illustrative model with

\[
E[b^{true}\mid\widehat b]\approx\eta\mathbf1+(1-\eta)\widehat b,
\]

and no additional conditional beta-error/market covariance, subtracting
`b_hat * market_return` leaves an expected term proportional to
`eta * (1-b_hat) * expected_market_return`. A positive market premium can then
look like a low-estimated-beta effect. An estimated-beta-neutral portfolio can
retain true exposure related to net investment. This is a hypothesis, not a
finding that the current alpha is spurious.

The original *Betting Against Beta* literature and the later *Betting Against
Betting Against Beta* critique make estimation and construction choices worth
examining. Their empirical explanations for real equities are not evidence
about this simulator. Relevant primary sources are [Frazzini and Pedersen](https://www.nber.org/papers/w16601)
and [Novy-Marx and Velikov](https://pure.psu.edu/en/publications/betting-against-betting-against-beta/).

Blindly shrinking hedge betas or adding dollar neutrality is not a free fix.
For `b_eta=(1-eta)b+eta*1`, a hedge to `b_eta` deliberately changes the relation
between raw estimated beta and net investment. For `0<eta<1`, hedging both
vectors forces dollar neutrality and can remove the direction just introduced.
Measure the mechanism first. The increase from beta .0093 to .0465 when scaling
V2 by five is also approximately ordinary scaling, not proof of worsened
estimation quality by itself.

## 3. New finding: phi=.3 is not a well-calibrated risk forecast on the chosen book

At each decision, the review recorded the original risk prediction on the
unchanged final holdings. It aligned that prediction with the next actually
scored gross return. This uses only prior information in the risk estimate.

The table reports `mean(realized gross return squared) / mean(predicted second
moment)`. A ratio near one is an aggregate calibration description; it is not
a proof of correct conditional covariance.

| Existing V2 holdings | Current factor scale .3 | Same holdings, unscaled factor matrix |
|---|---:|---:|
| Full run | **2.6755** | **1.0703** |
| Discovery | 2.5004 | 0.9601 |
| Validation | 3.7239 | 1.6738 |
| Audit | 1.9778 | 0.8167 |

The full-run annualized square-root second moment is approximately 3.84% in the
realized gross returns, 2.34% under the current matrix, and 3.71% with its factor
term unscaled. Squared mean return is only 0.66% of the observed full second
moment, so variance-versus-second-moment terminology cannot explain the gap.

**This weakens the explanation that .3 corrects an overestimated factor
covariance.** It looks more like an empirically chosen investment penalty or
regularizer that changes the exposures we want to hold. That may still improve
Sharpe. A statistically better calibrated risk matrix and a more profitable
mean-variance policy are different claims.

The unscaled calculation holds V2's positions fixed. It does not execute the
phi=1 strategy and does not overturn its previously observed lower Sharpe. The
full-run calibration also hides a substantial validation miss. Use this result
to distinguish model roles, not to declare phi=1 the new winner.

### Why the Bayesian explanation needs correction

For an uncertain conditional mean `D theta` with posterior covariance `V_theta`,
the law of total variance contributes the positive semidefinite term
`D V_theta D'` to predictive risk, in addition to innovation covariance.
Uncertain means may also be shrunk toward a prior. This does not imply multiplying
an otherwise correct factor covariance by .3.

Likewise, full factor risk does not imply factor neutrality; expected premia can
justify factor exposure even at phi=1. And the inverse matrix
`(diag(d)+phi DFD')^-1` does not generally create a common scalar blend of the
phi=0 and phi=1 portfolios. Costs and constraints make the claimed equivalence
still less accurate. See the explicit derivations in the quantitative review.
The [Black-Litterman-Bayes paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3728648)
and [Bayesian posterior-predictive allocation](https://arxiv.org/abs/1803.03573)
provide relevant frameworks; neither validates this particular factor discount.

## 4. What the structural research establishes, and what it does not

**The R-squared comparison motivates a conditional risk model. It does not
identify compensated factor premia.** The characteristic regressions refit
slopes on each day's realized returns, in a changing characteristic span. The
PCA comparator is static and fitted over the full sample, with a different
variance normalization. Neither statistic is an out-of-sample mean forecast.
Characteristic similarity and comovement are supporting descriptive evidence,
not identification of the true generator. IPCA explicitly distinguishes dynamic
characteristic-conditioned loadings from characteristic-associated intercepts;
that distinction has not been resolved by these regressions.
[Kelly, Pruitt and Su](https://www.nber.org/papers/w24540).

**The projection experiment is not a factor-neutral portfolio experiment.**
`variants.py:138–142` obtains PCs from standardized residuals and applies the
projection to raw-return forecasts without restoring stock-volatility scaling.
Even correctly projecting a forecast would not make the resulting positions
factor neutral after diagonal risk weighting, beta constraints, costs and caps.
The score change is sensitivity to a forecast transformation. The previous
frozen-position attribution is better evidence about where C09 earned its
observed payoffs, while still not identifying risk compensation versus alpha.

**The factor-risk ablation changes several things.** It changes the definition
of specific risk, its time weighting/window, and the off-diagonal term. The
missing matched control is a diagonal matrix with the same marginal variances
as the full characteristic model. The covariance contribution must be separated
from better marginal estimates. Reusing the same observable basis in mean and
risk is not intrinsically circular; misspecification, timing and selection are
the relevant issues.

**The drift p-value is not ready for reliance.** The observed statistic uses
3,526 rows, but its 55 shuffled 63-day blocks contain only 3,465 rows, dropping
the last 61 and moving segment boundaries. Equal means alone also do not make
time blocks exchangeable under changing volatility and dependence. A roughly
1-bp standard error is an indication of resolution, not a power study. Retain
the sensible conclusion that drift is unresolved, but correct the test before
using its numerical p-values. [Chung and Romano](https://arxiv.org/abs/1304.5939)
explain why equality of parameters and equality of distributions require
different permutation arguments; their independent-sample theorem is not a
turnkey theorem for this time-series implementation.

**The 60-day decay result is descriptive.** It uses full-sample premium weights
and an independent-day t-statistic. It does not establish a causal payoff
half-life or the optimal twenty-day cost horizon. A useful replacement freezes
the actually available premium estimate at each formation date and uses
matched, matured horizon outcomes with dependence-aware comparison.

## 5. Engineering findings and their actual importance

| Finding | Evidence and scope | Requested action |
|---|---|---|
| Risk-state identity/restart defect | A different history of the same initial length reuses `_STATE`. Full-scorer reproduction changed a target by 2.831 percentage points and a daily gross return by 9.87 bp. Ordinary fresh and repeated default-start runs passed. | Define and reset the risk-state lifecycle for each scoring session; handle repeated/restarted calls explicitly. |
| Characteristic layout not canonicalized | Fortran-layout characteristics changed a protected forecast by 1.72e−18, targets by 4.68e−10 and gross daily returns by 3.0e−12. | Canonicalize each feature panel before reductions in the shared basis function; preserve exact future/prefix comparisons. |
| Solver can return without a final certificate | Three of 3,527 real calls exceeded its extremely tight factor residual tolerance; no hedge tolerance failed. Maximum computed duality gap was only 3.96e−18. | Add a cheap, numerically meaningful final feasibility/value certificate and a documented failure path. Retain the solver. |
| Gross and stock caps are inactive in this replay | Maximum pre-scaling gross 2.6226 versus cap 5; maximum absolute stock weight 1.478% versus cap 5%. | Do not spend the next research effort rewriting the gross-constrained solver; it cannot explain this historical improvement. |
| Committed verification is narrower than the brief | Existing causality script checks the research forecast, prints failures without a failing exit code, and lacks packaged rebalance/position coverage. Original portable commands and several ledgers are absent. | Provide a packaged E2E command with strict exit status and exact source/input identities. |

Source details and exact reproduction commands are in the two engineering
reviews. The original supplied allocator test suite passed 38/38 checks; it was
rerun unchanged, rather than written after the fact. An independent prospective
E2E plan then covered ten fresh processes and twelve complete synthetic scorer
executions. It preserved both failing cases and passing controls. These results
support the causal ordinary path; they do not imply that the restart defect is
future leakage in Claude's published fresh-process backtest.

The brief's claim that Claude wrote its tests before implementation is not
independently established by the committed bundle: the original missing-module
run and its creation-order evidence are absent. Rerunning the supplied suite
verifies its current outcomes, not that historical sequence.

The literal runtime assertions for a century were not rerun by this review.
The real-data observational replay was fast, but instrumentation makes its timing
unsuitable as a new formal performance gate. Its original clean sources,
commands, environment and ledgers are retained. Two attempts at the C09 audit
wrapper failed on argument forwarding before producing a ledger; the wrapper
was corrected to use the scorer's declared-argument adapter, and a fresh third
attempt succeeded. [Failure record](../evidence/v2_real_review_20261028/HARNESS_FAILURES.md).

## 6. The next algorithm I would ask Claude to implement

**My first focused model experiment is to represent the beta-derived direction
in the conditional risk model while keeping the mean forecast fixed.** The
forecast has 27 columns; the current risk model has 26. The direct extra column
is quantitatively material and economically different from its informal name.
If it carries common residual risk, that risk is currently forced into the
specific-residual treatment or left inadequately represented.

This is a concrete hypothesis, not a guarantee of a better Sharpe. First use
fixed V2 holdings to examine that direction's risk and the beta-estimation
alternative. Then, if the omitted-risk hypothesis survives, run one fixed
27-column risk candidate with identical mean forecasts, inherited windows,
cost treatment and position-size convention. Do not combine it with a Kalman
filter, a new hedge estimator and a volatility overlay in the same experiment.

Alongside it, complete the matched-marginal covariance control. An interpretable
alternative shrinkage family for `A=DFD'` is

\[
\Sigma_\lambda=
\operatorname{diag}\{d+(1-\lambda)\operatorname{diag}(A)\}+\lambda A,
\quad 0\leq\lambda\leq1.
\]

It preserves every marginal variance and changes correlation confidence. It
fits the existing low-rank allocator. It is a proposed application of the
[Ledoit-Wolf shrinkage principle](https://econ-papers.upf.edu/papers/691.pdf), not
their estimator reproduced verbatim. Our new calibration evidence means that
an adaptive lambda is a conditional follow-up, not automatically the first
candidate or a justification for .3. If pursued, learn its specified rule from
past risk forecasts, not the maximum exposed Sharpe.

A compact premium state-space model is worth retaining as a later hypothesis:
stable premium plus a strongly shrunk dynamic deviation, with observation
noise and process noise separated and the process variance allowed to collapse
toward zero. The data do not currently demonstrate a learnable premium-drift
component. Group structure might inform shrinkage of uncertainty while retaining
different group-member coefficients; poor equal-weight composites do not reject
that idea. The [Bayesian hierarchical factor paper](https://arxiv.org/abs/1902.01015)
is a useful reference for explicit estimation uncertainty, not evidence that
this more complex model will win here.

Volatility targeting also needs a strategy-level hypothesis: its own predictable
variance and conditional return, after the existing dynamic risk allocator.
Market volatility ranging from low to high is not sufficient. The primary
[Cederburg et al. study](https://www.lehigh.edu/~xuy219/research/COWY.pdf) shows why
in-sample volatility-managed combinations need not translate into implementable
out-of-sample gains. No empirical result from that paper is imported into our
simulator.

Finally, the fivefold packaging scale adds essentially no observed Sharpe and
uses more absolute beta exposure. Treat scale as a separate sizing decision
under the actual scoring objective, rather than an alpha improvement. Keep
every variant and outcome, and use the exposed data actively for development
without calling it new untouched confirmation.

## 7. Direct answers to the brief's seven questions

| Question | Review answer |
|---|---|
| Characteristics are loadings and edge is factor premia? | Plausible conditional-risk descriptors; the stated tests do not identify compensated premia or exclude common predictable alpha. |
| Drift test and low power? | Useful multivariate idea, but sample mismatch and a stronger null than stated. Fix the test; low resolution is not a measured power curve. |
| Is phi=.3 defensible? | As a transparently selected empirical portfolio penalty, potentially. As a covariance calibration or Bayesian uncertainty derivation, not supported. New same-book calibration argues against the overestimated-risk story. |
| Allocator flaw? | Correct dual and scalar mathematics; missing final convergence certification. Supplied oracles and real value gaps support retaining it. |
| Missed lookahead? | No future-data path found in the ordinary fresh run. Confirmed restart-state and numerical-layout defects have narrower, explicitly reproduced scopes. |
| Best single next change? | Investigate and model the beta-hedged net-investment direction in risk, with unchanged mean forecast and a matched covariance control. This is my research judgment, not an observed future gain. |
| Is paired bootstrap appropriate? | Yes for preserving shared-day dependence in a fixed comparison; no as a selection correction or a reliable posterior. Corrected packaged-V2 sensitivity intervals all include zero. |

## Evidence and authorship

This independent review and its new audit analyses are AI-generated research
assistance. Claude's implementation and prior experiments remain attributed to
Claude; applicant direction is not rewritten as code authorship. The handoff
note still contains an applicant placeholder and should describe V2 as a
candidate under review unless the applicant has actually selected it.

All public research searches used generic methodological terms. The archive,
CSV and private result contents were not sent to public search services. Primary
sources were used for technical claims. Some SSRN/NBER items were available via
indexed abstracts rather than full downloads; direct-access failures and source
scope are retained in the quantitative review. Full texts opened include the
institutional Ledoit-Wolf covariance paper and the author-hosted Cederburg paper.
