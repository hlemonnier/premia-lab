# Reviewer handoff to Claude: make V2 explainable, then test its missing risk direction

28 October 2026, Europe/Paris. This is a research/implementation specification,
not a report of executed new candidates. It follows the independent review of
`afed8d0cb017acda151c4ea262fc30db7568a4bb`. There is no calendar schedule.

## Research decision

Continue V2. Independent exact-package replay reproduces net Sharpe 1.242503
versus C09 0.884811. Retain both identities as benchmarks. The next work should
resolve a concrete mechanism: the beta column largely prices net stock
investment under the beta hedge, while the risk model contains only the other
26 columns. Do not use the current result as evidence that a faster premium
model is the next useful change.

Read the integrated [independent review](../../reviews/V2_INDEPENDENT_REVIEW_20261028.md)
and its three supporting reviews. Their findings supersede unsupported causal
interpretations in the original draft; they do not erase any original results.

## 1. Correct the implementation and evidence before changing the model

### Explicit run lifecycle

`handoff_v2/model_v2/engine.py:157–161` identifies the cached risk state only by
its absorbed length. Reusing the strategy on a different history of equal
length produced a material difference in an independent complete-scorer test.
The ordinary fresh/default-start path is causal and passed.

Define a scoring-session lifecycle. In the supplied interface, a forecast call
starts a new scoring run, so resetting only the rebalance risk cache at that
boundary is a simple option. Specify what direct rebalance calls, repeated
calls at one date, and explicit restarts promise. Do not pretend a length check
validates the identity of a history. Preserve the useful incremental update
for an ordinary monotone immutable-history run.

### Canonical feature panels

Canonicalize each published characteristic panel before reductions in the
shared basis function, using contiguous float64 values. This fixes the actual
X-layout discrepancy without copying a century-sized panel unnecessarily.
The independent failure is numerically tiny but the existing blanket bitwise
claim is too broad. The same helper is used in forecast and risk construction.

### Certify the existing optimizer

Keep the dual/Newton allocator. Its supplied suite passes 38/38 checks, and
all 3,527 observed actual-path objective gaps are negligible. Three strict
gradient-tolerance exceedances demonstrate that the current termination logic
lacks a final certificate. Add one using normalized hedge feasibility,
caps, finiteness, the duality gap, and documented numerical tolerances.

With `M=B@L`, factor multiplier `lam`, hedge multiplier `nu` and normalized
hedge vector `bn`, the returned scalar maximizer has

`dual - primal = gamma/2 * ||M.T@w-lam/gamma||^2 - nu*(bn@w)`.

Use a numerically meaningful value criterion; do not introduce a brittle
exception merely because a residual misses an unnecessarily tiny tolerance.
Specify deterministic fallback/recovery before implementation. No gross-cap
rewrite is warranted now: maximum observed gross was 2.6226 below 5 and maximum
stock weight 1.478% below 5%. A joint gross solve remains a later improvement
if that constraint becomes active in another design.

### Verification and portable artifacts

Follow the project's existing test-order rule: failure/expected-outcome plan,
E2E workflow, then the production fix. Reuse the independent failing workflows
as specifications; do not replace them with weak tests tailored to the patch.
Include full forecast -> rebalance -> drift -> costs -> ledger comparisons,
future mutation, prefixes, repeated sessions, alternate starts and feature
layouts. Use strict nonzero exit status on failed expectations.

Preserve the original scorer and C09. Record exact input dtypes/layouts, commands,
source hashes, full unrounded ledgers and negative outcomes. Existing research
loaders default to float32 X and many scripts contain `/home/claude` paths;
remove those hidden reproduction assumptions from the runnable research entry
points. Correct the missing later-candidate comparison artifact. The review's
packaged-V2 interval is not the original unlevered research interval.

The corrections should not change a research hyperparameter. Require economic
agreement with the old literal package within a numerical tolerance recorded
before the fix; layout canonicalization may change reduction roundoff. Then
use that corrected behavior as the implementation baseline for new experiments.

## 2. Resolve the beta/net-investment mechanism with fixed forecasts and holdings

The independent replay has already established the direct forecast-objective
identity. Reuse it; do not spend time re-deriving the same table as a new result.

- Mean net investment is +40.09% of capital (C09: +1.01%).
- The beta term is 15.43% of average forecast times target.
- Centered clipping accounts for less than 1% of the algebraic net-investment term.
- This is not a realized profit decomposition, and the other 26 coefficients
  change when beta is jointly fitted.

The competing hypotheses are:

**H-beta-return:** the beta-derived, estimated-market-neutral investment
direction carries a useful conditional payoff beyond what is represented by
the 26 characteristic directions.

**H-beta-error:** market-beta estimation error contributes to the apparent
low-beta residual premium. Under shrinkage toward one and a positive expected
market return, `r-b_hat*m` can contain a predictable term proportional to
`(1-b_hat)`. This can also produce residual realized market exposure linked to
net investment. The replay does not distinguish these hypotheses yet.

Measure the incremental span of the standardized beta column relative to the
26 existing columns using only the panel available at that date. Report its
projection residual and conditioning. If it adds essentially no new span,
an extra risk factor has little rationale. This is a diagnostic; silently
switching to a changing orthogonalized factor basis would require corresponding
covariance transport and would be a different model.

Separate the direct beta term from the joint-refit effect. Keep the existing
27-column forecast for this stage. A shadow comparison of the saved 26-column
learner and the 27-column learner may explain changed coefficients, but must
be labeled as such; deleting a single final forecast component is not equivalent
to refitting the smaller learner.

Define a past-only beta-reliability diagnostic before computing it. Include a
synthetic constant-true-premium case with noisy estimated betas and a positive
market mean so that the competing explanation can be observed with known truth.
If comparing hedge estimators on actual returns, first use fixed holdings and
published information. Avoid changing label residualization, the beta alpha
column and hedge construction simultaneously. Do not estimate reliability as
realized strategy beta divided by mean net dollars; time-varying exposures and
market covariance invalidate that shortcut.

## 3. One focused risk-model candidate

### Candidate: V2_R27_beta_risk

Hypothesis: an incremental beta-derived direction contributes common residual
risk that is missing from the 26-column characteristic model, and accounting
for it can improve the net efficiency of the existing forecast.

Use **exactly the existing V2 forecast**. Append its same centered/clipped beta
column to the risk loading basis, giving 27 columns. On absorbed return row `s`,
use `basis(X[s-1])` and beta from returns `R[:s]`; preserve the existing risk
response exactly: `e=R[s]-beta_s*R[s].mean(); e-=e.mean()`. For tomorrow's allocation after close `t`, use
`basis(X[t])` and beta from `R[:t+1]`. Thus the risk column and the corresponding
forecast column refer to the same information set.

Inherit factor/specific half-lives 126, specific shrinkage .2, variance floor,
factor scale .3, cost horizon 20, gamma 200, caps and scoring conventions from
the packaged V2. The specific-residual update changes mechanically with the
additional fitted factor. Do not also tune phi, gamma, feature transforms,
premium half-life, hedge shrinkage or leverage in this contrast.

Before a policy comparison, evaluate the 26- and 27-column risk descriptions
on the **same frozen V2 holdings**. Freeze one primary risk score now:

`loss_t = log(q_t) + g_t**2/q_t`,

where `g_t` is the next actually scored gross return on the original V2 target,
and `q_t = w' (diag(d_t)+D_t F_t D_t') w` uses **physical factor scale 1**.
Use exactly the 3,526 aligned earning indices 253 through 3778; the weights are
from the previous decision. For a nonzero book, floor `q_t` at `1e-16` in daily
capital-return-squared units, identically for R26 and R27. If the frozen book is
exactly zero, assign zero loss to both models for that day and keep the day in
the common sample. No refitting of this floor or sample convention.

The primary comparison is the mean paired difference `loss_R27-loss_R26`.
It must be negative to pass the risk gate. Report fixed 21/63/126-day paired
block uncertainty and every original stage, regardless of the sign. This
quasi-score targets a conditional second moment; it is not a profit measure
and does not require a claim of Gaussian returns to motivate that target.

Full/stage aggregate calibration ratios, inherited optimization scale .3, and
any full-matrix score are **secondary**, not alternatives from which to choose
the favorable result. If the full-matrix score is reported, define it as
`(logdet(Sigma_t)+e_t' inverse(Sigma_t) e_t)/N` with the identical published-beta
residual/de-meaning convention for both models. Low-rank determinant/Woodbury
calculations avoid a dense 1,000-stock inverse. Distinguish second moments from
centered covariance throughout.

Use this shadow diagnostic to decide whether the omitted-risk hypothesis has
support. A numerical loss gain due only to in-sample daily refitting does not
count: factors, residual variances and loadings used for each prediction must
be available before the return being scored.

If the hypothesis survives, run one complete, continuous, full-fee comparison
of the fixed candidate against V2. Preserve all original stage masks and their
now-exposed status. Record paired daily return differences, net Sharpe, costs,
gross/net exposure, realized beta, factor exposure, forecast calibration and
optimizer certificates. No stage resetting or free extra opening trades.

**Decision rule to freeze before execution:** retain R27 as a promising model
improvement only if the specified past-only primary risk score improves and full
net Sharpe improves against the fixed V2 baseline, with the task's beta/runtime
requirements met. Report all stages and paired uncertainty even if this rule
passes. A negative result rejects this version; do not rescue it by tuning phi
or selecting a convenient period. This is an exploratory retention rule, not
a claim of untouched validation or automatic final-package promotion.

### Matched-marginal control for the existing covariance claim

At fixed 26-column risk state, let `A=D F D'`. Compare the original V2 penalty
`diag(d)+.3*A` to its exact matched diagonal
`diag(d+.3*diag(A))`, with the same forecast and costs. This isolates the value
of the off-diagonal part at the existing penalty scale. It is a mechanism
control, not an additional hyperparameter search. If claiming the incremental
R27 effect specifically comes from correlations rather than marginal risk,
its own matched control must also be specified before that claim is tested.

## 4. Follow-ups ranked by what the previous evidence establishes

1. **Separate physical covariance and deliberate factor exposure.** On V2's
   existing book, current phi=.3 predicts only about 1/2.68 of realized squared
   gross return; the same unscaled matrix is close in aggregate but imperfect
   by stage. Do not call .3 a Bayesian covariance correction. If correlation
   estimation is the problem, the variance-preserving family
   `diag(d+(1-lambda)*diag(A))+lambda*A` is an interpretable next experiment.
   An adaptive rule should be estimated from prior risk loss, not a grid search
   over the exposed Sharpe. Freeze a separate specification before implementing.
2. **Correct the drift and decay diagnostics.** The drift permutation uses
   3,465 observations versus 3,526 in its observed statistic; make the samples
   identical and state a defensible dependence/heteroskedasticity null. Treat
   the 60-day full-sample-weighted IC curve as descriptive. Use formation-date
   coefficients and dependence-aware comparisons for a predictive curve.
3. **Premium adaptation if its innovations are predictable.** A stable mean
   plus strongly shrunk dynamic deviation is a better specified starting point
   than an unrestricted Kalman search. Separate factor-return noise from
   premium-process uncertainty and allow process variance to collapse to zero.
   Hierarchical uncertainty can use group information without forcing group
   members to share the same premium.
4. **Volatility targeting or actual portfolio combinations only with a distinct
   hypothesis.** The optimizer already responds to a risk forecast. Test the
   strategy's conditional variance/return, not just market volatility. A blend
   of return streams is not a costed strategy; combine positions, preserve
   drift and net trades, and fix weights using only past information.

These are dependencies and decisions, not dates. Keep improving the algorithm,
including proposing new hypotheses when results warrant them; keep each
experiment capable of disproving the explanation that motivated it.

## Reading that changes the next decision

- [Kelly, Pruitt and Su, Characteristics Are Covariances](https://www.nber.org/papers/w24540):
  distinguish characteristic-conditioned loadings from an anomaly/intercept channel.
- [Frazzini and Pedersen, Betting Against Beta](https://www.nber.org/papers/w16601)
  and [Novy-Marx and Velikov's critique](https://pure.psu.edu/en/publications/betting-against-betting-against-beta/):
  examine construction and beta estimation before importing a low-beta story.
- [Kolm and Ritter, Black-Litterman-Bayes](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3728648)
  and [Bauder et al., posterior-predictive allocation](https://arxiv.org/abs/1803.03573):
  explicit mean uncertainty and predictive risk, not an unexplained covariance discount.
- [Ledoit and Wolf, covariance shrinkage](https://econ-papers.upf.edu/papers/691.pdf):
  choose a target and loss deliberately; the proposed diagonal-preserving family
  is a project-specific adaptation, not their estimator verbatim.
- [Ledoit and Wolf, Sharpe comparisons](https://www.ledoit.net/jef2008_abstract.htm):
  dependence-aware studentized comparison, distinct from correcting adaptive selection.
- [Cederburg et al., volatility-managed portfolios](https://www.lehigh.edu/~xuy219/research/COWY.pdf):
  distinguish in-sample combinations from strategies implementable in real time.

No model change above has been implemented or scored by this review. This
handoff is AI-generated research planning; the user's own contribution remains
their direction and decisions, not these derivations or code executions.
