# Forecast research directed at the official net score

28 October 2026, Europe/Paris. Source reviewed: `v2-factor-risk` at
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`. This is a prospective research
specification, initially written before any prototype implementation or new
forecast/score output. Root subsequently admitted isolated research prototypes;
their prospective controller and execution records are held separately in
`evidence/v2_score_forecast_20261028/`. Claude remains the production
implementation owner. This note proposes two controlled forecast experiments;
any later execution outcome must be labeled separately from the specification.

## Decision

**The strongest new forecast question is whether to average daily estimates of
characteristic premia instead of pooling their normal equations.** It changes
the statistical weighting of common factor shocks without adding a feature,
memory parameter, or allocator modification. A secondary, cheaper-to-understand
contrast allows faster linear adaptation while retaining slow nonlinear and beta
coefficients. These are alternatives against frozen V2, not a combination chosen
after seeing their individual results.

The objective is future net Sharpe under the supplied scorer, with the beta,
causality and runtime requirements. A cleaner exposure decomposition or lower
forecast MSE has no independent promotion value. The original assignment permits
full-sample parameter tuning; every historical segment is already exposed.
Report that fact rather than reusing the words validation/audit as evidence of
new independence. The prior original-discovery search budget is historical, not
a new veto over the user's present instruction to continue score research.

## What has actually been tried

The selected forecast is a pooled exponentially weighted ridge on 27 columns:
13 standardized characteristics, 13 centered squares, and a standardized trailing
beta. All coefficients share half-life 1008 and ridge 0.1. V2 then uses the
characteristic factor-risk allocator with factor scale 0.3.

The recorded negatives matter, but their controls matter too:

| Recorded experiment | What it establishes | What remains untested |
|---|---|---|
| C03, half-life 63, discovery net Sharpe 0.106 versus C02 0.638 | Making the entire original additive forecast fast was poor in that configuration. | Different memories for different functional blocks under V2. |
| C09-family H252: full net Sharpe 0.867 versus H1008 0.885; expanding 0.777 | Uniform short/expanding memory did not beat the C09 diagonal book. | A restrained fast linear component paired with slow squares under selected V2 risk. |
| Current-panel prediction decorrelation: 1.000 with beta; factor-risk version 1.107 | Extra inverse-Gram prediction transforms were tested. | Averaging daily fitted coefficient vectors before prediction. These are different operations. |
| C05 GLS discovery 0.602 versus C02 0.638; C06 with factor portfolio 0.763 | That prior PCA-precision learner was not beneficial by itself; portfolio interaction mattered. | Date-level averaging under the actual characteristic factor representation and V2 allocator. |
| C11 interactions 0.603; C12 local hinges 0.626 versus C02 0.638 in discovery | Those added-shape specifications lost to their declared parent. | They do not demonstrate that every larger model fails, but provide weak grounds for another immediate shape expansion. |

Sources are the repository's `research/EXPERIMENT_LEDGER.md`,
`research/GLS_ALPHA_PLAN.md`, and at the reviewed Claude source
`research/v2/results/comparison.json`, `research/v2/exploration/variants.py`,
and `handoff_v2/model_v2/engine.py`. The factor-risk decorrelation run used scale
1.0, rather than the selected 0.3. These scores therefore cannot be compared as
if all differences were forecast-only interventions around V2.

The existing uncosted factor exercise reports H1008 all-26 factor-level Sharpe
1.16 for coefficient-mean exposures and 1.03 for Gram-weighted exposures. That
is suggestive of geometry affecting factor allocation, but it is a normalized,
uncosted factor-return surrogate with different exposures. It supplies neither
a forecast comparison nor a tradable score. Source: the reviewed Claude files
`research/v2/exploration/factor_level.py` and `results/factor_level.json`.

## Candidate F1: average daily ridge premia

### Why this is a new question

At matured label date j, define the exact current V2 design D_j from the
characteristics published at j-1 and the beta estimate available before j.
Use V2's unchanged residual label e_j. Let

    G_j = D_j' D_j / N
    h_j = D_j' e_j / N
    A_j = (G_j + 0.1 I)^(-1) h_j.

With EW1008 weights normalized to sum to one, current V2 estimates

    theta_pool = (G_bar + 0.1 I)^(-1) E_w[h_j].

F1 instead uses

    theta_day = E_w[A_j],
    forecast_t = D_current theta_day.

This uses daily **ridge slopes**, not unregularized unit-exposure factor returns.
The same 0.1 penalty is applied before averaging instead of after averaging.
There is no extra inverse Gram applied to the current prediction panel and no
cross-sectional standard-deviation renormalization of predictions.

The exact identity is

    theta_pool - theta_day
      = (G_bar + 0.1 I)^(-1) E_w[(G_j - G_bar) A_j].

Therefore the forecasts coincide when the historical design Gram is constant.
Their difference is driven by the covariation between characteristic geometry
and the estimated daily coefficient vector. This identity also supplies a
simple prospective end-to-end verification case.

In this market, the evidence already suggests material common shocks aligned
with characteristic loadings. Increasing the stock count does not make such a
common shock into N independent observations. Pooling gives dates and directions
with larger Gram exposure more influence. Date-level averaging removes that
particular weighting. If the weighting mainly amplifies common-shock noise, the
score may improve. If it captures useful precision or conditional information,
the score may worsen. A constant-coefficient model with independent homoscedastic
stock noise is a counterexample to assuming equal date weighting is automatically
more efficient.

This is an original local hypothesis derived from the code, not a result claimed
by the papers below. It does not assume that the simulator is a published model.

### Complete contrast

- Retain the exact 27 columns, clipping, raw causal beta label and prediction
  beta feature, half-life 1008, ridge 0.1 and 126 matured-pair warm-up.
- At forecast row t, the latest label is j=t-1; its characteristic design uses
  X[t-2] and beta computed from returns strictly before j. Predict with the
  panel X[t-1] and beta computed from returns strictly before t.
- Update `slope_sum = decay*slope_sum + A_j` and
  `mass = decay*mass + 1`. Emit zero until 126 pairs have matured, then
  `D_current @ (slope_sum/mass)`.
- Use the exact selected V2 rebalance configuration and original scorer.
  In particular, retain factor scale 0.3 and the existing beta setting. No beta
  correction, risk recalibration, leverage change or cost-horizon change is
  bundled into this candidate.
- Keep all learned moments local to a forecast invocation. No fitted state from
  the future-facing forecast call may leak into rebalance.

The arithmetic remains O(T N K^2 + T K^3), K=27, with fixed-size learned state.
It uses one 27-dimensional solve per matured date, as the current learner does;
the solve moves from the pooled moments to that day's moments. This is a
complexity statement, not a measured runtime pass. The existing scoring output
still grows with T because the forecast API requires it.

## Candidate F2: restrained fast linear adaptation

Fit two complete current V2 pooled ridge coefficient vectors with half-lives
252 and 1008, otherwise identical. Both fits include all 27 columns, so the
linear coefficients retain adjustment for squares and beta. Let P select the
first 13, linear, coordinates. Use

    theta_F2 = theta_1008 + 0.5 P (theta_252 - theta_1008).

Consequently the linear block is the equal-weight average of the two fits, and
the square and beta blocks remain exactly the slow fit. Apply the unchanged
current 27-column design to this coefficient vector. Both learners start from
zero local sufficient statistics and the same 126 matured-pair rule.

This is a specified coefficient combination, not a purported solution to one
pooled least-squares objective. It avoids a common incorrect implementation:
assigning different decays to arbitrary rows of one Gram matrix and then
silently treating a nonsymmetric or non-positive-definite matrix as a valid
joint regression.

The motivation is the observed distinction between more variable linear
relations and comparatively stable curvature, together with the damage from
making every coefficient fast. Evidence of genuine coefficient drift remains
weak; changing predictor covariance can reverse marginal slopes. The fixed
one-half coefficient attenuates the new fast component and is a design choice,
not a published optimum. No characteristic is selected by name, no local
regime date is encoded, and no mixture weights are learned from the same day's
outcome.

The new work is a second K-by-K moment state and solve, sharing each day's
already-computed Gram and score contributions. It is roughly one extra small
solve and moment update per day, not a second N-by-K design computation. Actual
forecast runtime and prefix stability must be measured. All allocation and
cost controls remain frozen V2. F2 is tested separately from F1.

## Score admission and falsification

The primary quantity is the original scorer's full-sample net Sharpe on exactly
the common earning rows 253..3778. Reproduce V2 at the pinned source first.
Neither a lower prediction MSE nor a better explanatory story can replace this
economic comparison.

An eligible candidate must be finite, causal on the configured path, executable
within the assignment's runtime, and within the existing market-beta requirement.
Among eligible candidates, a strictly higher net Sharpe is a positive
development result and grounds for nomination. A smaller score rejects that
candidate's replacement claim. Numerical equality within the declared replay
tolerance favors the simpler existing candidate. Do not introduce a 95%
significance hurdle after seeing scores or demand that every historical segment
win; neither is the assignment's objective. Conversely, do not call a small
positive difference a proven future improvement.

Report paired block intervals with the existing fixed 21/63/126-day conventions,
all existing chronological segments, actual costs, gross and net means and
volatilities, realized beta, turnover, runtime and constraint activity. Report
each candidate individually; do not average only the favorable regions or
discard a weak experiment. No F1-plus-F2 combination or weight/half-life grid
is admitted by this note. A later combination is a separately recorded research
choice because the allocator and costs make forecast effects nonadditive.

Before implementation, fix the E2E expectations for zero returns, constant
Gram equivalence for F1, fixed-coefficient/known changing-linear synthetic
paths, altered future, repeated fresh process, layout changes and prefixes.
The synthetic fixtures verify the proposed wiring and information clock; they
do not select the candidate or establish local-market alpha. Code production
and execution remain unperformed here.

## Literature: what is useful and what is not being imported

1. **Pesaran and Pick, Forecast Combination across Estimation Windows (2011).**
   The inspected author manuscript studies averaging forecasts estimated over
   different windows under parameter breaks. It supplies a bias/variance
   motivation for retaining more than one memory rather than attempting to
   date a regime exactly. Its results concern forecasting errors, not the net
   Sharpe of this strategy; F2's block split and numerical weights are ours.
   [Author manuscript, 4 March 2010](https://ap236.github.io/papers/PesaranPickAveW4Mar2010.pdf);
   [published institutional record](https://repub.eur.nl/pub/26871);
   DOI `10.1198/jbes.2010.09018`. Retrieved refs: `turn53view1`, `turn50search0`.

2. **Kozak, Nagel and Santosh, Shrinking the Cross Section.**
   The SSRN/NBER primary records describe economically motivated shrinkage of
   SDF coefficients, with greater suppression of low-variance principal-component
   contributions. This cautions against treating all estimated factor directions
   as equally reliable and against optimizing raw in-sample factor Sharpe.
   It is not an argument to remove low-variance directions mechanically or to
   identify our mean learner with their SDF estimator. F1 does not implement
   their prior. [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2945663);
   [NBER record](https://www.nber.org/papers/w24070). Primary indexed records
   retrieved as `turn53search0` and `turn50search1`; direct opens returned 403.
   No claim of a full-text read of that manuscript is made.

3. **Feng and He, Factor Investing: A Bayesian Hierarchical Approach.**
   The inspected arXiv record describes joint conditional-return/covariance
   estimation and sharing information while retaining heterogeneous coefficients.
   It supports considering estimation uncertainty jointly with portfolio use.
   Their posterior sampling model and US-equity results do not establish an
   advantage here. There is insufficient local evidence to prioritize an MCMC
   rewrite over the two cheap contrasts above.
   [arXiv:1902.01015v3](https://arxiv.org/abs/1902.01015), revised 17 September
   2020, ref `turn53view0`; published DOI `10.1016/j.jeconom.2021.11.001`.

4. **Uziel and El-Yaniv, Long-and Short-Term Forecasting for Portfolio Selection
   with Transaction Costs (2020).** The primary proceedings record explicitly
   combines long- and short-term experts while accounting for turnover costs.
   Its regret benchmark and trading setup differ from this assignment. The
   useful implication is to score combinations as complete costed policies,
   not to infer their net value from forecast error or gross paper returns.
   [PMLR record](https://proceedings.mlr.press/v108/uziel20a.html), ref
   `turn57view1`. We have not implemented or claimed its regret guarantee.

Alpha Architect was already used in the earlier project literature review as
a route to original cost research. This forecast note relies on primary sources
and the actual code rather than duplicating secondary summaries. All research
design and derivations here are AI-generated assistance; no applicant discoveries
or results have been invented.

## Executed outcome, added after the frozen specification

The subsequently admitted original-scorer prototypes yielded net Sharpe
**1.137993 for F1** and **1.291780 for F2**, against reproduced V2 **1.242503**.
F1 is rejected; F2 improves the full-development score by0.049277, with realized
beta0.04905 and observed mean rebalance time4.27ms. Its paired63-day95% interval
for the score difference is[−0.07251,+0.15736]; uncertainty does not create a new
significance gate. The gain is concentrated more in the final original segment,
and all segments remain exposed development history.

F2's actual forecast/prefix checks are exact. A canonical-layout full-scorer
future alteration also preserves protected forecasts, decisions and economics
exactly after a documented archive repair. Strict mixed-layout numerical
comparisons failed at tiny allocation/gross differences and remain failed in
the evidence; they were not erased by changing a tolerance. An original NPZ
archive truncation is disclosed, with the successful F2 replay reproducing
original full forecast/target hashes exactly and writing verified atomic NPYs.

See [forecast results](../../evidence/v2_score_forecast_20261028/RESULTS.md) and
[execution record](../../evidence/v2_score_forecast_20261028/EXECUTION.md).
Root's precommitted rule controls any single joint forecast/sizing experiment.
No F1/F2 retuning or production-package edit was made.
