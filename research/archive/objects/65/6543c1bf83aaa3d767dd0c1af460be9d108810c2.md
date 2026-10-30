# V2 independent quantitative research review

28 October 2026, Europe/Paris. Review target: `v2-factor-risk` at
`afed8d0cb017acda151c4ea262fc30db7568a4bb`, compared with C09 at
`fb8c7024edbc432262709965dbeadc3da02547e1`.

This review reads the submitted brief, pinned source, and committed numerical
summaries. It derives the economic and statistical implications and consults
primary research. It does **not** claim to have rerun strategies, recomputed
their ledgers, or reproduced the reported tests. Separate engineering and
replay reviews cover those activities. All proposed experiments below are
unexecuted. No production source was changed.

## Verdict

**The characteristic-based risk model is a credible research advance. The
current evidence does not establish either the claimed economic mechanism or
the best way to regularize that risk model.** Keep developing it. Do not replace
its unexplained choices with a more complicated premium model before isolating
what is already improving performance.

The most useful new question is more specific than “should we add Kalman?”:

> Does V2 improve because it models conditional covariances, because it changes
> marginal risk and portfolio scale, or because the beta feature prices a
> beta-hedged net-investment direction?

Those explanations imply different next algorithms. The existing comparison
does not distinguish them. An ambitious next step is a calibrated conditional
risk model with separate treatment of net investment and premium uncertainty,
not another unrestricted Sharpe search.

## 1. Findings requiring correction

### 1.1 The “one change” factor-risk comparison changes several things

In `research/v2/exploration/variants.py:155–165,191–196`, the beta-only strategy
uses C09's allocator and risk estimates; the factor-risk variants switch to
`strategy_v2`. That module changes market-residual marginal variance to
characteristic-factor residual variance, changes estimation to EW statistics
with a 126-day half-life, and adds characteristic factor risk
(`strategy_v2.py:30–35,78–99,106–124`).

Consequently, the improvement from the beta-only result to the factor-risk
result is **not an isolated estimate of the value of off-diagonal covariance**.
The V2 family also produces a much smaller book at the original risk aversion.
This can change cap activity and effective trading thresholds, even when one
tries to describe all effects in Sharpe units.

The missing controls are:

1. V2's forecast, state construction and allocator with `F=0`: identifies the
   effect of the changed specific-risk state, but deliberately understates
   total marginal variance if interpreted as a covariance forecast.
2. The matched marginal-diagonal model
   `diag(d + diag(D F D'))`: preserves V2's marginal risks and removes only
   cross-stock covariances.
3. V2's full covariance `diag(d) + D F D'`, with the same forecast, risk history,
   trading rules and portfolio-size convention as control 2.

These are mechanism controls, not invitations to select the best of three
additional backtests. Retain all outcomes and compare the forecasts of risk as
well as net trading performance. The already exposed data is usable for this
development, with that status recorded.

### 1.2 Lower factor covariance is not a Bayesian response to noisy alpha

The packaged risk construction is explicit at
`handoff_v2/model_v2/engine.py:139–146`: eigenvalues of the factor second moment
are multiplied by 0.3. That reduces the risk charged to common exposures.

Suppose, as an illustrative model, that

\[
r=D\theta+\varepsilon,\qquad
E[\theta\mid\mathcal I]=\bar\theta,\qquad
\operatorname{Var}(\theta\mid\mathcal I)=V_\theta,
\]

with conditional innovation covariance \(\Sigma_\varepsilon\) independent of
the parameter uncertainty. Then the law of total variance gives

\[
E[r\mid\mathcal I]=D\bar\theta,\qquad
\operatorname{Var}(r\mid\mathcal I)
=\Sigma_\varepsilon+D V_\theta D^\top.
\]

Mean uncertainty therefore contributes a **positive semidefinite extra risk
term**, along with any prior-induced shrinkage of the mean. A robust
ellipsoidal mean set similarly produces a penalty proportional to
\(\sqrt{w^\top D V_\theta D^\top w}\). Neither derivation says to multiply an
otherwise correct factor covariance by 0.3.

There are legitimate reasons why a smaller factor term might work: the
estimated factor covariance may be noisy or systematically overstate future
risk; the daily cross-sectional factor coefficients contain measurement error;
the remaining risk specification may be wrong; or 0.3 may be an empirical
preference for a different exposure pattern. Those hypotheses require
different tests. Calling this “Bayesian” would not identify which one is true.

Also, \(\phi=1\) does not mathematically “hedge factors away.” A mean-variance
optimizer can hold substantial, deliberately rewarded factor exposure under a
full covariance. The actual exposure depends on expected returns, covariance,
costs and constraints. A risk penalty is not a factor-neutrality constraint.

The Bayesian factor-investing framework of Kolm and Ritter is relevant because
it models prior beliefs and factor views explicitly, rather than treating a
covariance discount as implicit confidence. Their SSRN abstract was retrieved;
the full paper was not downloaded. The posterior-predictive derivation above
is supplied here independently. [Primary source: SSRN 3728648](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3728648).

### 1.3 Risk scaling is not equivalent to blending endpoint books

Even without costs or constraints,

\[
w_\phi\propto (\Delta+\phi DFD^\top)^{-1}\mu.
\]

This is generally not \(a w_0+(1-a)w_1\) for one common scalar \(a\). Different
covariance eigenmodes change by different amounts. With turnover penalties,
caps and drift, the discrepancy is greater. A combination of already realized
return streams also does not establish the costs of a strategy that combines
positions and rebalances them.

The reported endpoint correlation and blended return stream are useful
exploration. They do not derive 0.3 or verify an implementable combination.
The code and dated input/output record of that particular blend were not
present among the fetched V2 files, so its exact weighting timing remains
unverified in this review.

### 1.4 The selected candidate's bootstrap output is missing

`research/v2/results/comparison.json` contains 22 variants. It includes
`fr_beta` but omits `fr_beta_phi03`, `fr_beta_phi01` and
`fr_beta_phi03_x5`. There are 25 `variant_*.json` files, including those three.
Thus the selected V2's claimed paired range `[0.00, +0.82]` is not supported by
that committed comparison artifact. This is an evidence gap, not proof that
the number is false. Recover the exact ledger, rerun command, output and
source identity, or explicitly label the interval as reported but unreproduced.

The comparator also samples starts from `rng.integers(0, n-L)`
(`compare.py:19–21`), excluding the last legal start `n-L`. That is a minor
endpoint defect; the correct upper-exclusive bound for all non-circular
length-L blocks is `n-L+1`.

## 2. The beta feature has a much sharper interpretation than the brief gives

The forecast adds a centered, standardized trailing beta at
`engine.py:94–99,107–114`; the portfolio hedges the corresponding current
trailing beta at `engine.py:165–169`. Apart from their numerical implementation,
both estimates use the same published return window for that decision.

Let \(b_p\) be the beta in the prediction and \(b_h\) the beta in the hedge.
Ignoring clipping for a moment, the additional characteristic is

\[
z_\beta=\frac{b_p-\bar b_p\mathbf1}{s_p}.
\]

For any feasible book with \(b_h^\top w=0\),

\[
w^\top z_\beta
=-\frac{\bar b_p}{s_p}\,\mathbf1^\top w
+\frac{(b_p-b_h)^\top w}{s_p}.
\]

When the two beta estimates coincide, its direct contribution to the alpha
objective is exactly a coefficient on **net dollar exposure**. For equal-weight
market OLS betas calculated on the same universe, their cross-sectional mean
is one, up to numerical effects. The low-beta signal can therefore express a
return on beta-hedged net investment, often interpreted as a zero-beta
intercept direction. This is a legitimate possible payoff, but is more precise
than declaring an independent stock-selection anomaly.

There are two qualifications:

1. The code clips standardized beta at four. If clipping changes the vector by
   \(\delta\), re-centering adds the residual term
   \(w^\top\delta-\bar\delta\,\mathbf1^\top w\). Its magnitude should be measured.
2. Adding beta refits all 26 characteristic coefficients jointly. A change in
   performance can come from changed characteristic coefficients as well as
   from the direct beta-column objective. Merely deleting the final forecast
   component does not reproduce the 26-column model.

This gives a focused diagnostic using an unchanged replay: log net dollars,
gross exposure, the beta coefficient, the difference between the two beta
estimators, and the clipping contribution. Reconcile the identity in the
forecast objective. That is not itself a realized-P&L attribution or a
counterfactual strategy test.

The proposed beta-shrinkage fix also needs this algebra. With
\(b_\eta=(1-\eta)b+\eta\mathbf1\), imposing \(b_\eta^\top w=0\) implies

\[
b^\top w=-\frac{\eta}{1-\eta}\,\mathbf1^\top w.
\]

It introduces a particular raw-estimated-beta exposure dependent on net
investment. Hedging both the raw and shrunk vectors would force dollar
neutrality for \(0<\eta<1\), potentially removing the return direction just
added. Do not add this as an unexamined “safety” improvement. First evaluate
hedge forecast calibration and the associated return channel.

The change from realized beta about 0.009 to about 0.047 at five times the
book size is almost exactly the change expected from ordinary linear scaling.
It does **not**, on its own, show that hedge quality deteriorated. Compare beta
per unit of scale or risk and the full time path. The task's absolute beta
constraint still makes leverage an independent decision.

Frazzini and Pedersen's primary account motivates investigating beta-neutral
low-beta portfolios in real markets, but its financing explanation is not
evidence about this anonymous simulator. [Primary research account: Betting Against Beta](https://www.aqr.com/insights/research/journal-article/betting-against-beta).

## 3. What the structural diagnostics establish

### Characteristics are useful risk descriptors; the generator is unidentified

`structure.py:58–63` fits a fresh cross-sectional regression each day using
that day's realized residual returns and yesterday's characteristics. This is
a contemporaneous fitted explanatory statistic. The 26-column R² is computed
separately in `factor_level.py:37–44`.

The PCA comparator at `structure.py:68–74` is a **full-sample static** covariance
PCA, not rolling PCA. It uses fixed stock directions, while the characteristic
space changes every day. The ratio of total PCA variance and the average of
daily fitted R² ratios also use different normalizations. Consequently,
“33% is greater than 20%” is not a matched predictive comparison and does not
prove which data-generating mechanism produced returns.

The characteristic similarity/residual-correlation association
(`structure.py:78–88`) is additional descriptive support, but stock pairs share
stocks and are not independent observations. No claim of hundreds of thousands
of independent pieces of evidence is justified.

The result is enough to motivate a conditional characteristic risk model. It
does not distinguish compensated risk, a predictable common payoff,
characteristic-associated intercepts, omitted nonlinear factors, or a mixture.
Kelly, Pruitt and Su's IPCA framework explicitly separates dynamic
characteristic-conditioned loadings from characteristic-associated intercepts;
our simple regressions have not performed that identification. The retrieved
author research page and NBER abstract support this conceptual distinction;
no factor count from their empirical US equity application is imported here.
[Author source](https://sethpruitt.net/research),
[NBER source](https://www.nber.org/papers/w24540).

### Projecting the forecast is not a clean factor-exposure intervention

`variants.py:135–142` estimates PCs of **standardized** residual returns, then
projects the raw stock-return forecast onto the complement of those correlation
eigenvectors. In return units, the corresponding factor loadings generally
require multiplication by the stock standard deviations. That rescaling is
missing in this projection.

Moreover, even if the projected forecast satisfied \(B^\top\mu=0\), the chosen
positions need not satisfy \(B^\top w=0\). Diagonal risk weighting, beta
constraints, trading costs and caps change the forecast-to-position map. The
observed Sharpe reduction demonstrates sensitivity to this forecast
transformation, not the P&L of an otherwise identical factor-neutral book.
The earlier frozen-position attribution is stronger evidence about where the
original book earned its observed return, while remaining a descriptive
decomposition rather than an identification of risk premia.

### “Decorrelating” the forecast changes its economic meaning

The learner already solves joint ridge normal equations
(`variants.py:118–125`). If \(E[r\mid D]=D\theta\), the fitted \(D\hat\theta\)
is the natural model forecast. Multiplying the coefficients again by an
inverse current Gram matrix (`variants.py:132–134`) produces a different
forecast. The code also rescales its cross-sectional standard deviation to
match the original, which the abbreviated formula in the brief omits.

In the idealized homoskedastic unconstrained case, a diagonal-risk allocator
applied to \(D\theta\) does give factor exposure proportional to
\(D^\top D\theta\). That is the consequence of the chosen risk objective,
not proof that the mean model is incorrectly correlated. Under heterogeneous
specific risks the relevant matrix is \(D^\top\Delta^{-1}D\), and constraints
change the relation further. A factor-risk allocator already treats common
exposures jointly. The negative factor-risk-plus-decorrelation result is
consistent with redundant adjustments, but does not prove that explanation.

Using the same observable basis in mean and risk is not intrinsically circular.
The estimators must use only available information, and their joint fit must
be evaluated honestly. The relevant risk is model misspecification and
selection, not the mere reuse of published characteristics.

## 4. Drift, persistence and uncertainty

### The drift test needs a correct sample and a better stated null

There is a concrete sample mismatch. `drift_test.py:13` takes 3,526 rows. Its
block construction at lines 24–27 keeps only 55 complete 63-day blocks: 3,465
rows. The observed statistic therefore includes 61 terminal observations that
none of the permutations contains, and the six segment boundaries change.
Use the same rows in observed and simulated statistics, with a recorded
terminal-block convention.

Preserving the entire 26-vector in each block is good: it retains local
cross-factor dependence. But the asserted null of merely constant means is
too weak for this permutation design. Exchangeability of blocks, or an
appropriate stationary approximation, is stronger. Changes in volatility,
correlations or dependence can matter even under constant means. The
within-segment `variance/n` denominator is not an independent-data theorem
once observations are dependent; block calibration may account for some local
dependence but does not automatically solve nonstationarity.

For a corrected analysis, define the constant-mean null with a time-varying
noise process allowed, use an appropriate dependent/wild bootstrap or a
validated studentized construction, and report prespecified block-length
sensitivity rather than selecting the favorable length. Retain the global
multivariate question; if reporting named individual effects, account for the
26-factor family and the two group-level inspections. An unadjusted 0.05
among many inspected components is not convincing evidence of a special
drifting feature.

The reported order-of-magnitude comparison between 1 bp/day and a segment's
standard error is a useful warning about low resolution. It is **not a power
calculation**. A power study must specify an alternative, inject a step or
smooth drift under a defined noise model, and measure rejection frequency.
Failure to reject does not establish constant premia. Conversely, an
unidentified drift process does not make a Kalman filter automatically useful.

Chung and Romano's primary paper illustrates the difference between a
permutation test valid under identical distributions and one valid under a
weaker equality-of-parameters null. It is methodological support, not a
turnkey proof for this block time-series design.
[arXiv:1304.5939](https://arxiv.org/abs/1304.5939).

### The 60-day signal result is descriptive and its t-statistic is naive

`rev_decay.py:12` estimates the premium weights from the **full sample** and
uses them at every historical formation date. The comment correctly labels
this as descriptive. The t-statistic at line 24 is `mean/std * sqrt(n)` with
no dependence correction. Slowly changing signals and persistent volatility
make an independent-day standard-error interpretation inappropriate without
further evidence.

The diagnostic also uses each future day's separately formed market-residual
return. It does not represent holding yesterday's actual beta hedge unchanged
for 60 days. Its IC persistence therefore does not determine the existing
20-day transaction-cost amortization horizon.

A useful replacement is to freeze the actually available coefficient estimate
at each formation date, evaluate fixed prespecified horizons, retain matched
formation dates, and measure realized holdings/payoffs with the actual hedge
and fees where a trading claim is made. Use time-block uncertainty for the
paired horizon comparison. The preliminary curve can motivate that experiment;
it cannot supply its expected answer.

### The paired bootstrap is reasonable for a fixed comparison, insufficient for selection

Shared-day resampling is the right starting point when strategies share a
forecast core: their dependence is valuable information, not a defect. But
63 days is one dependence assumption, percentile intervals are not
studentized, and the full-run series spans adaptive learning and possible
changing regimes. Report these as conditional descriptive intervals. The
fraction of bootstrap differences above zero, labeled `P(>0)` in
`compare.py:36–45`, is not a posterior probability that V2 is better and not a
selection-adjusted p-value.

Ledoit and Wolf specifically propose studentized time-series inference for
differences of Sharpe ratios under more general return behavior. Their primary
abstract and indexed manuscript were retrieved; direct PDF retrieval failed.
[Primary abstract](https://www.ledoit.net/jef2008_abstract.htm).

If the goal is selection-aware inference, preserve the joint ledger of every
considered candidate and use an explicitly defined simultaneous comparison or
selection procedure. Hansen's SPA paper is relevant to benchmark comparisons
across many forecasts, but its loss-differential framework cannot simply be
renamed a Sharpe test. Neither it nor a deflated Sharpe calculation accounts
for unrecorded adaptive model invention. A new chronological replay on exposed
data can still reveal stability and implementation failures; it does not
recreate an untouched holdout.
[Primary SPA abstract](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID264569_code244328.pdf?abstractid=264569).

## 5. Recommended research sequence, without a calendar

### First: identify the mechanism of the current improvement

Complete the beta/net-dollar diagnostic and the matched covariance controls
above. Preserve C09 and V2 as benchmark identities. Use the same cost model,
continuous holdings, forecast core and scoring convention. Report both net
Sharpe and risk-forecast calibration; a covariance model should be able to
explain more than a larger optimized Sharpe.

Also report net dollars, forecasted versus realized portfolio variance,
characteristic exposures, cap activity, turnover, gross scaling, and return
contributions. The one-dimensional beta feature may be doing a more useful
and simpler job than its current name suggests. Resolve that before imposing
new neutrality constraints or adding another mean estimator.

### Best next model change: preserve marginal variance while regularizing correlations

My preferred next algorithmic experiment, conditional on the mechanism checks,
is a diagonal-preserving shrinkage of the characteristic covariance. Let
\(A_t=D_tF_tD_t^\top\). Use

\[
\Sigma_{\lambda,t}
=\operatorname{diag}\bigl(d_t+(1-\lambda_t)\operatorname{diag}(A_t)\bigr)
+\lambda_t A_t,\qquad0\leq\lambda_t\leq1.
\]

Every value has the same marginal variance \(d_t+\operatorname{diag}(A_t)\).
Only correlation confidence changes. It is positive semidefinite and retains
the low-rank-plus-diagonal form needed by the current allocator. Computationally,
use the adjusted diagonal and \(\sqrt{\lambda_t}L_t\); no dense 1,000-stock solve
is needed. This is a proposed adaptation of the shrinkage principle, not a
claim to implement the Ledoit-Wolf estimator verbatim.

Choose the update rule for \(\lambda_t\) from prior one-step risk calibration,
such as a fixed, causal likelihood/proper-score procedure on return innovations,
with all windows, bounds and update timing specified before execution. Do not
choose it using the best full-sample strategy Sharpe. First compare the two
fixed endpoints under the matched controls; then evaluate one explicit adaptive
rule if calibration supports it. A risk-model loss and the final trading
objective answer different questions and both should be reported.

Ledoit and Wolf provide the primary rationale for combining a noisy covariance
estimate with a structured target. Their primary abstract and indexed
manuscript were retrieved. This proposal is deliberately tailored to the
available low-rank engine and does not import their empirical equity results.
[Primary source](https://www.ledoit.net/honey_abstract.htm).

### Then: model premium uncertainty before making adaptation faster

A compact alternative to a freely tuned Kalman filter is a stable premium
component plus a strongly shrunk dynamic deviation. Grouping can share
uncertainty or process variance while retaining different member coefficients;
the failure of equal-weight group composites does not reject hierarchical
shrinkage. However, the group structure should not be used to invent many
post-hoc submodels.

If a state-space model is attempted, observation noise must be separated from
premium-state uncertainty, update timing must use matured labels, and the
process-noise estimate must be allowed to collapse toward zero. Compare one
specified model with the existing EW learner. Estimate its parameters on past
data under a stated likelihood or forecast-loss rule; do not choose a state
variance by maximizing the exposed audit Sharpe. A state-space model adds a
useful hypothesis only if its forecast errors demonstrate a learnable dynamic
component.

### Volatility targeting is a conditional proposal, not an obvious upgrade

Market volatility varying over time is not sufficient. The relevant question
is whether the **strategy's own** conditional variance is predictable and
whether its conditional expected return grows more slowly than that variance.
The optimizer already adjusts exposures using a changing risk matrix, so an
extra overlay can duplicate that response and create turnover.

Moreira and Muir's primary NBER abstract motivates reducing risk when variance
is high and expected returns fail to rise proportionately. An Alpha Architect
discussion led to Cederburg et al.; their author-hosted full paper was opened.
It shows why attractive spanning-regression results need not translate into
implementable, superior strategies. These papers support a local test, not a
universal recommendation. Any overlay should be evaluated as an actual causal
position policy, with fees and constraints, rather than a rescaled return
series.
[Moreira–Muir](https://www.nber.org/papers/w22208),
[Cederburg et al.](https://www.lehigh.edu/~xuy219/research/COWY.pdf),
[Alpha Architect discovery route](https://alphaarchitect.com/the-performance-of-volatility-managed-portfolios/).

## 6. Additional precision in the handoff note

- `engine.py:135–143` estimates a factor **second moment**, not a centered
  covariance; `U2` is likewise a residual second moment. The distinction may be
  numerically small but must be named correctly or empirically quantified.
- Scripts are present for the decay and drift calculations, but their quoted
  numerical stdout is not retained among the fetched result files. The
  selected-phi bootstrap is absent from the committed comparison output, and
  the exact equal-risk blend implementation/output was not found. Recovering
  those records is an evidence task, not a reason to assert the claims are false.
- A family with only three inspected values does not establish a “smooth
  curve” or future robustness. It provides a coarse sensitivity observation.
- The factor-level comparison normalizes exposures by their Euclidean norm
  (`factor_level.py:72–81`), not by risk or tradable book size, and omits costs.
  Its relative performance cannot be directly promoted to stock-level net Sharpe.
- Synthetic calendar labels in the note are unnecessary when the task gives
  row indices. State the actual row ranges and annualization convention.
- Describe the improvement as an exposed-sample development result. The
  existing positive C09 audit is useful evidence about the old policy; its
  superiority in that one period does not logically forbid a better new model.

## Source-access record and scope

Primary sources were searched on 28 October 2026. Opened full text: Cederburg et
al. (2020), author-hosted 23-page journal paper. Opened records/abstracts:
arXiv 1203.5957 (linear-cost trading), arXiv 2112.09959 (mean-covariance robust
risk), and Seth Pruitt's author research page. Retrieved indexed primary
abstracts/manuscripts: Kelly–Pruitt–Su, Kolm–Ritter, Ledoit–Wolf, Hansen,
Chung–Romano, Moreira–Muir, and Frazzini–Pedersen's research account. Direct
retrieval of the Kolm–Ritter–Simonian PDF returned 403; Ledoit–Wolf's Sharpe PDF
returned 502; an old Kan–Zhou author PDF URL returned 404. No claim of reading
those full inaccessible texts is made.

No numerical result in those papers establishes the simulator's structure or
predicts the gain of a proposed change. The recommendations combine explicit
local code findings, algebra, and clearly identified methodological inference.

## 7. Later evidence: independent readback of the unchanged packaged replay

This section was appended after the research coordinator completed the real
replay in `evidence/v2_real_review_20261028/run_v2_001`. It is distinct from the
source-only assessment above. I did not execute another strategy. I read the
saved decision observations and daily ledger, checked their hashes plus the
summary and replay-source hashes against that run's artifact manifest, and
independently recomputed the arithmetic below. All four identities matched.

The 3,527 decisions have forecast indices 253 through 3,779. The 3,526 scored
return rows have indices 253 through 3,778. Joining each opening target to its
forecast-index return, and excluding the final unearned target, gives the
correct prior-close risk/next-day-return alignment. The full and three stage
Sharpes and the reported calibration ratios reconcile to the saved summary.

### The beta/net-investment interpretation is quantitatively relevant

Across all 3,527 decisions, mean net stock investment is **+0.400862 of
portfolio capital**, ranging from −0.200351 to +0.742084. Over only the 3,526
decisions whose next return is scored, the mean is +0.400867. This is net stock
investment, not a claim that 40% of the portfolio is held in cash.

The mean direct beta-column contribution to the **forecast objective** is
`6.730828806974213e-5` per day, decomposed as:

| Term in the algebraic identity | Mean daily forecast-objective contribution |
|---|---:|
| Net-investment term | `6.784108395377068e-5` |
| Clipping/re-centering correction | `-5.327958840285156e-7` |
| Difference between forecast and hedge beta estimators | `-1.1547210328802209e-20` |
| Finite hedge-tolerance correction | `-1.3679989533288263e-20` |

The maximum row-level identity discrepancy is `6.776263578034403e-20`.
Clipping offsets about 0.785% of the mean net-investment term. Thus the
previously derived net-investment mechanism is not merely a theoretical
possibility: it describes the direct beta-column objective on this actual
book to numerical accuracy, with a small measured clipping correction.

This beta-column term is about **15.43% of the mean total forecast objective**.
That is neither its realized-return share nor a counterfactual marginal Sharpe.
Joint coefficient refitting remains a separate effect.

### The 0.3 matrix substantially understates this book's realized second moment

For each existing opening target, the replay records the predicted specific
second moment and the scaled factor second moment. Holding those same targets
fixed, the unscaled factor second moment is obtained by division by 0.3. This
requires no different trading decisions and no new model fitting.

| Scored period | Realized squared gross return / predicted second moment, phi 0.3 | Same-book ratio with factor scale 1 |
|---|---:|---:|
| Full | **2.67555** | **1.07026** |
| Discovery | 2.50045 | 0.96013 |
| Validation | 3.72393 | 1.67378 |
| Audit | 1.97778 | 0.81665 |

The annualized square root of the full-run mean realized squared gross return
is 3.83550%. The corresponding square roots of the average model second
moments are 2.34485% at phi 0.3 and 3.70746% at scale 1. These are aggregate
root-second-moment comparisons, not a claim of exact conditional volatility
calibration or a confidence interval.

The squared full-run gross mean accounts for only 0.656% of its second moment;
the maximum corresponding stage share is 1.129%. Confusing variance with second
moment therefore cannot explain an understatement of 2.68 times. The
scale-1 aggregate match is substantially better, but validation still
underpredicts and audit overpredicts. A single favorable aggregate ratio is
not sufficient to certify the risk model.

This evidence materially weakens the explanation that phi 0.3 is correcting
an overstated factor covariance. On the actual selected book it makes the
risk statistic much smaller than the realized gross second moment. It may
still be a useful empirical portfolio regularizer or preference, but should
be presented as such rather than as a calibrated physical risk forecast.

It does **not** follow that the phi-1 trading policy would have a better Sharpe.
That policy would choose different exposures and incur different costs. Nor
does the same-book scale-1 comparison establish that every covariance entry
is correct. It simply separates risk calibration from the effect of choosing
a different portfolio objective.

### Updated research priority

The strongest next quant direction is now to separate the beta-hedged
net-investment payoff from the other characteristic signals and identify its
risk. The matched-marginal covariance controls remain necessary to interpret
the V2 improvement. The new evidence makes a blind continuation of the phi
grid less attractive, and weakens the case for immediately adding generic
premium dynamics or volatility scaling.

One falsifiable alternative to a structural low-beta premium is regression
of true beta toward one. Under the illustrative relation

\[
E[b_{\mathrm{true}}\mid\hat b]
=\eta\mathbf1+(1-\eta)\hat b,
\]

a return model \(r=\alpha+b_{\mathrm{true}}m+\varepsilon\) produces a residual
label containing \(\alpha+\eta(\mathbf1-\hat b)m+\varepsilon\). A positive
conditional market mean can then create apparent low-beta residual returns;
an estimated-beta-neutral book can retain true market exposure related to
its net investment. This is a hypothesis, not an identification from the
observed realized beta. Dividing average realized beta by average net dollars
would not be a valid estimate of eta for this changing portfolio.

For Claude, the targeted sequence is:

1. Separate the direct beta objective from changes in the other 26 fitted
   coefficients, using declared comparison rules and actual portfolio replays
   whenever a return claim is made.
2. Evaluate hedge calibration using information available at each historical
   decision, and distinguish expected residual return from compensation for
   remaining market exposure. This need not impose dollar neutrality, which
   would suppress the observed direction by construction.
3. If the beta-derived direction is retained, test whether it needs its own
   loading in the risk model. The current mean has 27 columns while risk has
   only the original 26. One added, causally formed beta direction with an
   unchanged mean forecast is a focused hypothesis about omitted common
   residual risk, not a generic increase in model complexity.
4. Use matched marginal risks to judge any covariance regularization. The
   diagonal-preserving proposal above remains a useful control and candidate,
   but these measurements do not yet favor its adaptive version over the
   unscaled model. Keep statistical risk forecasts separate from empirically
   chosen optimization penalties in the report.

No new policy, beta shrinkage coefficient, covariance intensity or premium
state parameter was selected in this readback.
