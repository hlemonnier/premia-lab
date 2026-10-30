# V2 follow-up: market exposure is demonstrated; the mechanism and decision claims need narrower language

28 October 2026, Europe/Paris. Independent quantitative research review of
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07` on `v2-factor-risk`, following the
review at `afed8d0cb017acda151c4ea262fc30db7568a4bb`.

This report is a source, mathematics and literature review. Numerical observations
below are read from the pinned committed results; root's independent ledger
readback supplies the separate reproduction evidence. No new trading candidate,
new fitted hedge or new Sharpe experiment was executed by this reviewer.

## Decision

**Retain V2 under the existing retention rules. Keep the explicit-beta capability
as a useful research instrument, and reject the tested R27 and B05 replacements
under their recorded rules. Do not reinterpret their failure as proof that beta
correction or richer risk models are unhelpful.**

The strongest new evidence is the contrast **B05 versus B0**: it changes only the
exposure target in the corrected pipeline. The target increment of 0.05 produces
a realized-beta increment of approximately 0.05024. That is compelling evidence
of useful relative control on this historical sample. Both candidates retain an
absolute error of about -0.014, so the level is not precisely calibrated.

The main scientific correction is more substantial: centering does **not** make
beta-estimation error invisible. The present report explains why. The next
discriminating measurement should align beta validation with the one-day,
portfolio-weighted decision and distinguish the covariance of residual returns
from the covariance of the actual portfolio return. Selecting another exposure
target from the observed -0.014 error would be an unplanned rescue.

### Cross-review of root's completed independent ledger readback

I subsequently inspected `evidence/v2_followup_review_20261028/ledger_readback.py`
and its saved JSON. The incremental comparison subtracts B0 net/gross/fee rows
from B05 while preserving the identical day and market rows. The intercept OLS,
HAC construction, R-squared and annual percentage-point conversions are
consistent. Root's result strengthens the relative-control interpretation:
B05-minus-B0 has beta 0.05023853 and market R-squared 0.99926136. Its annual
arithmetic mean difference is +0.716801 percentage point, comprising a fitted
market term +0.727450 and intercept -0.010649. This is a difference between two
complete policy P&Ls, not an independently traded overlay.

The gross/net beta differences are about 1.5e-5, too small to explain the
approximately -0.014 level offset. Root's separate latest-package replays find
no gross scaling and final estimated-target errors below 7e-13 on B0/B05.
These facts rule out those particular implementation explanations on the
observed paths. They do not uniquely identify the horizon mismatch: static
unconditional beta can also reflect conditional-mean/exposure effects. The
appropriate remaining question is exposure-model calibration, not an already
proven single source of bias. No numerical run was repeated by this reviewer
during the cross-review.

## 1. Centering is not the reason beta-error risk is missing

The new follow-up states that all risk columns and residual returns are centered,
and therefore a beta-hedged net-long book's exposure to beta-estimation error is
invisible to the risk model. This reasoning is incorrect.

Let `m` be the equally weighted stock-market return, as in `engine.py`. In an
ordinary same-window OLS beta estimate with an intercept,

\[
\frac1N\sum_i\widehat b_i
=\frac{\operatorname{Cov}(m,N^{-1}\sum_i r_i)}{\operatorname{Var}(m)}=1.
\]

The implementation's fallback is also a vector of ones. Thus, apart from
floating-point error, the raw residual already has zero cross-sectional mean:

\[
\overline{r-\widehat b m}=m-\overline{\widehat b}m=0.
\]

The additional `e -= e.mean()` does not remove a hidden common market-error
component in this construction. The corrected beta preserves this mean too.

Under the illustrative shrinkage model used in the discussion,

\[
b^{\rm true}-\widehat b\simeq\eta(\mathbf1-\widehat b).
\]

This error loading is itself centered. Consequently the component
`eta*(1-bhat)*m` survives cross-sectional demeaning. A centered beta column can
represent it. **R27 is itself centered and uses the same demeaning; its reported
risk improvement is incompatible with the claimed theorem of invisibility.**

For a centered characteristic matrix D, `D'1=0` means the factor covariance
annihilates a *uniform loading direction*. It does not mean it annihilates every
net-long portfolio. Write `w=c*1+w_perp`: `D'w=D'w_perp`. The beta hedge couples
net investment to the non-uniform component, and the factor part can price the
projection of beta error into its span.

The valid evidence is the **93.2% squared Euclidean residual share** of the beta
column after projection onto the 26 columns. This says the beta column adds
substantial loading span. It is neither a 93.2% share of portfolio risk nor proof
that zero beta-error risk is represented by R26. It supports an omitted-direction
hypothesis without the erroneous centering explanation.

Sources: `handoff_v2/model_v2/engine.py` (`causal_betas`, `_window_beta`,
`_correct`, `_RiskState.absorb`); `research/v2/beta_diagnostics.py`
(`beta_factor`); `research/v2/results/beta_diagnostics.json`, D3.

## 2. The market regression supports a channel; it does not uniquely identify it

The joint beta-characteristic coefficient has reported market slope -0.0480,
Newey-West t-statistic -19.68, and intercept -0.104 basis points per day with
t-statistic -0.766. This is strong evidence of market comovement in that
residual-factor series. It is not proof that its only economic source is beta
measurement error.

The two proposed hypotheses are not mutually exclusive. A factor may have both
a market loading and a nonzero conditional premium. A nonsignificant intercept
does not establish a zero intercept, particularly when the desired claim is
economic equivalence. The reported statistics support “no incremental constant
intercept detected in this specification,” not “no separate premium exists.”

There are further identification limits:

- The dependent variable is a daily characteristic regression coefficient of
  `r-bhat*m`, jointly with the other characteristics. It is not the return of a
  separately executed, costed low-beta strategy. The observed slope concerns a
  factor whose estimated market component was already subtracted.
- Attenuation of next-year beta on current estimated beta can reflect
  measurement error, changing true betas, or both. The 0.825 slope does not
  estimate the share due exclusively to noisy measurement.
- The zero-alpha constant-beta simulation proves that the proposed channel can
  generate the signature. It does not identify that data-generating process in
  the supplied market.
- The joint regression's market term is -0.276 bp/day against mean coefficient
  -0.380 bp/day. It explains much of that sample mean, not literally all of it.
  The uncertainty in the remaining term is the reason not to claim certainty.

The literature on conditional performance evaluation is relevant because a
static market regression does not generally resolve time-varying exposures and
conditional means. Ferson and Schadt explicitly motivate conditioning on public
information. Their empirical mutual-fund results are not evidence about this
simulator. [Primary publisher abstract](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1996.tb02690.x).

Recommended wording: **“The joint beta factor has a large negative market loading
after estimated-beta residualization; its constant intercept is not statistically
resolved. A zero-alpha simulation and forward-beta shrinkage support beta error
as an important plausible channel. Other conditional-premium explanations have
not been excluded.”**

## 3. Ex-post market removal is a diagnostic, not a traded 1.1-Sharpe core

`market_component()` fits one full-sample regression

\[
y_t=\widehat a+\widehat\beta m_t+\widehat u_t
\]

and reports Sharpe on `y_t-beta_hat*m_t`. The intercept is deliberately retained.
The approximately 1.08–1.10 values are therefore descriptive residual-return
Sharpes using a hindsight hedge coefficient. They do not establish a realizable
pure stock-selection strategy with that Sharpe.

The distinction matters for four reasons. The full-sample coefficient was not
known at each decision; the hypothetical market hedge incurs no modeled trading
cost; the actual stock portfolio would drift and trade differently under an
implemented hedge; and a single-market residual can still contain other common
premia, nonlinear market exposure or conditional timing effects. “Pure
stock-selection” is an identification claim beyond this one-factor regression.

It is valid to report that about 0.67 percentage point of V2's 4.76% annualized
arithmetic net return is its *sample linear market component*. It is not valid
to subtract Sharpe numbers as additive profit contributions. Sharpe depends on
both the means and the covariances of its components.

This distinction also limits the B0 retention interpretation. The original rule
compares an actually traded B0 to V2's hindsight market-removed series. B0 fails
that recorded bar. That is a valid protocol disposition; it is not proof that
the best implementable neutral core is worse than 1.083. B0 also has residual
negative market beta in a sample with a positive market premium.

Sources: `research/v2/beta_diagnostics.py:market_component`,
`research/v2/EXPLICIT_BETA_PLAN.md`, `research/v2/EXPLICIT_BETA_RESULTS.md`.

## 4. Beta correction improves the stated annual diagnostic, but solves a different loss

The committed diagnostic compares cross-sectional MSE of forecasts for realized
betas over the following 252 days. Its reported average MSE decreases from
0.043134 to 0.039296, an improvement of approximately 8.9%. Corrected estimates
win on 139 of 144 dates (96.5%). Those are useful descriptive results.

The date grid advances by 21 days while the outcome window spans 252 days.
Adjacent outcomes overlap heavily; 144 dates are not 144 independent replications.
The correction's expanding training pairs overlap too. There is no implication
that this is a 97% probability of successful future exposure control.

More importantly, the forecast target is an annual, equally weighted stock-level
beta statistic. The strategy needs the next return's exposure of a changing
long-short portfolio. With beta error covariance V, stock-level mean MSE is
related to `trace(V)/N`; the relevant portfolio error is `w'Vw`, plus directional
bias. Improvement in one does not imply improvement in the other. Shared beta
errors can survive stock diversification.

The correction can be causal and still be miscalibrated for the decision horizon.
This is a modeling mismatch, not by itself lookahead. The source uses completed
future windows for the calibration pairs; the separate causality reviewer is
responsible for the detailed timing audit and execution evidence.

The results distinguish **control slope** from **control level**:

| Fixed corrected pipeline | Target beta | Realized net beta |
|---|---:|---:|
| B0 | 0 | -0.0138551 |
| B05 | 0.05 | 0.0363835 |
| Difference | 0.05 | 0.0502385 |

The target increment works very well in this comparison. Both levels share a
negative offset. Calling that “within the prespecified 0.02 tolerance” is correct;
calling it “precise control of true market exposure” is too strong. Gross-return
beta should also be separated from net-return beta when auditing a position
constraint, because costs may themselves covary with the market.

The old beta literature distinguishes cross-sectional shrinkage and empirical
regression tendencies; neither label proves a single underlying cause. More
recent beta-forecast research compares actual prediction methods and market-neutral
portfolio outcomes. Those designs motivate validating the hedge on its intended
use, not copying an estimator because it wins on other equity data.
[Vasicek primary record](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1973.tb01452.x),
[Blume primary record](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1975.tb01850.x),
[Hollstein, Prokopczuk and Wese Simen, SSRN 3069518](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3069518).

## 5. A residual-risk model is not automatically the risk model of a nonzero-beta book

This is the next important modeling distinction. Fix the information set at a
decision and write

\[
r=bm+e,\quad p=b^\top w,\quad c=\operatorname{Cov}(e,m\mid\mathcal F_t).
\]

Then the actual portfolio's conditional variance is

\[
\operatorname{Var}(w^\top r\mid\mathcal F_t)
=w^\top\Sigma_e w+2p\,c^\top w+p^2\sigma_m^2.
\]

For a fixed target `p=beta_star`, the last term is constant across feasible
positions. Omitting that term inside the fixed-target optimizer does not change
the optimum. **The cross term is generally not constant.** Its omission is
justified only if the relevant residual-market covariance is zero or immaterial.
Noisy or horizon-misaligned betas are exactly a reason that orthogonality can fail.

The mean side has a similar but simpler decomposition:

\[
E[w^\top r\mid\mathcal F_t]
=w^\top\mu_e+\beta_*\mu_m.
\]

Here the market term is constant for a fixed target, so using the corrected
residual mean is coherent *within that fixed-target problem*. Across targets,
the market mean and market variance matter. “Use corrected betas everywhere”
does not by itself establish an optimal explicit market budget.

The equivalent second-moment identity replaces conditional covariances by
`E[ee']`, `E[em]` and `E[m^2]`; it should be used if the loss being scored targets
second moments, as the R27 quasi-score does. Do not silently mix a covariance
interpretation with uncentered accumulated factor products.

Simply adding a market factor with the old raw beta loading will not repair V2:
its raw estimated-beta constraint makes `b'w` approximately zero, eliminating
that market term on the selected book. A better loading estimate, an additional
beta-error direction, or explicit uncertainty/cross-covariance modeling is needed
for the risk in that direction to be represented.

Sources: direct algebra above; the pinned engine residualizes returns before
building the factor/specific risk state, and passes only that covariance to the
allocator. This report does not claim that the omitted cross term is empirically
material before it is measured.

## 6. What each intervention identifies, and what to retain

**B05 versus B0 is a clean target-only contrast.** Its corrected labels, residual
risk state and forecast mechanism are identical. Their changing portfolios and
future drift/cost paths are legitimate consequences of the exposure intervention.

**B05 versus V2 is not a pure explicit-versus-implicit contrast.** It changes
forecast labels, factor/specific residual risk, the hedge loading and its target.
The beta *feature column* being affine-invariant does not keep its fitted
coefficient or the other 26 coefficients fixed: the response changed. The plan's
“nothing else changes” and “isolates explicit-and-measured versus implicit” need
this qualification.

**R27 failed the recorded full-policy retention rule.** Accept that result. Its
frozen-book primary risk loss improved in the aggregate, but the stage differences
were +0.004, -0.180 and +0.060; two of the three block interval conventions include
zero. The strongest improvement is concentrated in validation. This supports a
useful representation in some conditions, not uniformly superior calibration.
Its lower beta/net investment is consistent with charging more for the extra
direction, but lower market carry is not automatically the entire cause of its
Sharpe decrease.

**The matched-diagonal ablation is meaningful.** At fixed marginal variances and
other policy settings, removing off-diagonal terms reduced the observed Sharpe.
Its much larger gross, volatility, transaction costs and binding cap are
consequences of that intervention, rather than an unrelated confounder. However,
the result does not separately identify better portfolio direction from changed
risk sizing and nonlinear cap/cost effects. Nor does it establish that the full
V2-versus-C09 improvement comes exclusively from correlations. The paired
uncertainty intervals include zero.

For a later geometry-versus-sizing question, a second contrast could impose the
same *past-only predicted* risk budget under one common risk evaluator. Matching
full-sample realized volatility after seeing results would not provide an
implementable comparison. That second contrast needs its own specification; it
should not replace the completed fixed-penalty result.

**B05 is unresolved against V2, not statistically proven equivalent.** The
recorded intervals permit moderate losses and gains. An equivalence or
noninferiority claim requires an economically justified margin specified before
the comparison. Selecting that margin around the observed -0.012 difference
would move the goalposts. Lakens explains the distinction between nonsignificance
and equivalence; its elementary testing examples are not a ready-made
time-series-Sharpe procedure.
[Primary article](https://journals.sagepub.com/doi/full/10.1177/1948550617697177).

The scoring objective is future net Sharpe subject to the stated beta bound, not
an intrinsic preference for beta zero. Transparency of an exposure is valuable,
but does not establish higher expected Sharpe. Conversely, a point-estimate
retention screen is a development rule, not proof that the incumbent maximizes
future performance. Keep the incumbent now and preserve B05 as an instrument
for controlled experiments; do not sell a post-result override as validation.

## 7. Proposed next discriminating measurement, before another policy search

This is a proposed specification, not an executed experiment or a modification
of any completed retention rule.

### Primary book and timing

Use V2's original frozen targets as the primary book. B0 and B05 are prespecified
secondary books. Capture each target and the raw/corrected beta vectors from the
exact already-tested policy, without changing positions. Align the decision at
close t with the next actual scored gross return `g[t+1]` and market `m[t+1]`.
Use the same 3,526 earning rows and original stage masks.

At every decision record raw and corrected predicted portfolio beta, eta, net
investment, gross exposure, costs and whether the final post-cap target preserves
the intended equality. Retain quantities before and after any scaling.

### Primary horizon-aligned beta score

For each fixed book compare raw and currently corrected predictions
`p_raw=w'b_raw`, `p_cor=w'b_cor` on the **next** return. One concrete common-mean
convention is the arithmetic stock-return mean over the same last 252 published
rows, projected onto the current fixed weights; use the corresponding market
mean. Both beta forecasts use exactly those same means. Define

\[
H^{(j)}_{t+1}
=\left[g_{t+1}-w_t^\top\overline r_t
-p^{(j)}_t(m_{t+1}-\overline m_t)\right]^2.
\]

Freeze the primary comparison as the mean paired difference `H_corrected-H_raw`
on V2. Report the 21/63/126-day paired block sensitivity and all stages, and the
two secondary books regardless of sign. This is a one-step hedge-error score
under a specified shared mean convention; it is not a claim to observe latent
instantaneous true betas. The noisy mean convention is a limitation to disclose,
not an alternative to select after seeing which one wins.

As complementary calibration diagnostics, regress `g-p*m` on a constant and m
with dependence-aware intervals; show gross and net versions separately. Report
the B05-minus-B0 target/realized slope and common level error. Compare these
one-day findings to the already-computed equal-stock annual-beta MSE. This
distinguishes useful long-horizon shrinkage from correct exposure control on the
actual traded direction.

### Shadow raw-risk reconstruction

Before changing allocation, use the existing 126-day factor-state weighting and
only completed observations to estimate joint market/factor second moments.
Use the current corrected beta loading and its corresponding corrected residual
state together. On the frozen books compare that state's residual-only
predictions with a raw-return reconstruction that includes the market term and
cross term. The raw-beta construction is an invariance control: on V2's original
raw-beta-neutral positions, adding only that same raw-beta market direction must
have negligible effect. A joint covariance
of the market and existing factor-return vector gives a positive-semidefinite
low-rank construction; report residual-market covariance outside that span as
an unresolved approximation rather than assuming it is zero.

Score predicted raw second moments using the already established `log(q)+g^2/q`
convention, with the same floor and zero-book treatment. Decompose the prediction
change into the market square term and the cross term. This is a risk diagnostic
only. A subsequent policy change requires its own frozen hypothesis, controls
and costs. Do not choose a favorable beta target or correction strength here.

### Decision implications

- If annual-beta MSE improves but the portfolio one-step score does not, change
  the calibration target/horizon before declaring the hedge solved.
- If raw-risk cross terms are material and forecastable, the next allocator
  experiment should isolate that correction with the forecast frozen.
- If these effects are small, stop spending policy runs on a 0.012 Sharpe
  difference. Return to the covariance or mean-forecast research questions with
  this measurement limitation documented.
- A corrected beta target of `0.05+0.014` selected from the current error would
  be an unplanned offset fit, not a new independently justified result.

Engle, Ledoit and Wolf combine dynamic covariance modeling with shrinkage and
explicitly discuss losses connected to portfolio decisions. Their particular
DCC model is not proposed as the next implementation. The useful lesson here is
to evaluate the risk estimator on the decision it serves, while keeping scale
calibration and portfolio efficiency distinct.
[Institutional full paper](https://www.econ.uzh.ch/dam/jcr:28fa9939-753e-4f5c-932d-945872f30cfd/jbes_2019.pdf).

## Source access and boundaries

Pinned project sources and committed JSON results were read locally. No private
inputs or results were sent to public search. Ferson–Schadt's publisher abstract
and the full institutional Engle–Ledoit–Wolf PDF were opened. The beta-estimation
papers were available through primary publisher/SSRN indexed records; Liverpool's
full PDF returned HTTP 406 and EconStor presented an access challenge, neither
was bypassed. Lakens's primary full text was search-indexed, while direct opening
timed out. These scopes support the limited methodological statements above,
not a claim to have read every full paper or reproduced their empirical results.

All derivations and this review are AI-generated research assistance. They do
not alter attribution of Claude's implementation or the applicant's decisions.
