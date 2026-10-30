# A higher-scoring candidate: partial fast/slow forecasts plus causal risk sizing

28 October 2026, Europe/Paris. Baseline production source:
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`. The experiment family was committed
before scoring the supplied market at `251bee83d182e8796b7e2a35354fd1475b7dc242`.

## Decision

**Nominate F2 + VTvol as the new research leader for Claude's production
integration.** Its official net Sharpe is **1.3183349661**, versus reproduced
V2 **1.2425030733**: **+0.0758318928**, approximately **6.1%**. Realized net
market beta is **0.052720**, within the assignment condition. These are actual
original-scorer replays with full drift and fees, not scaled saved-return series.

The decision follows the user's score-first instruction and the supplied brief.
The four standalone alternatives and exactly one conditional joint alternative
were specified before their results. The joint condition was met by F2 and
VTvol; their combination was then genuinely executed and beat both constituents.
No further exponent, window, coefficient-mixing or beta-target search was run.

The production handoff remains unchanged in this research branch. The isolated
prototype, complete evidence and exact integration instructions are available;
see [SCORE_IMPLEMENTATION_HANDOFF_20261028.md](SCORE_IMPLEMENTATION_HANDOFF_20261028.md).
This is a development-score improvement, not a measured score on the employer's
unseen future. All fifteen years have already been examined.

## 1. Every permitted result, including the rejected hypothesis

All rows use the same original scorer: opening at zero-based row 252, earning
rows 253..3778, population-standard-deviation Sharpe and actual closing rebalance
fees. The endpoint charges the final rebalance; it does not force liquidation.

| Policy | Net Sharpe | Change vs V2 | Annual net return | Annual net vol | Annual fees | Net beta |
|---|---:|---:|---:|---:|---:|---:|
| V2 control | 1.242503 | — | 4.7550% | 3.8270% | 0.1756% | 0.04650 |
| F1: average daily ridge slopes | 1.137993 | -0.104510 | 4.1332% | 3.6320% | 0.1451% | 0.03158 |
| F2: partial fast/slow coefficients | 1.291780 | +0.049277 | 5.1265% | 3.9686% | 0.2071% | 0.04905 |
| V2 + inverse-volatility sizing | 1.277109 | +0.034606 | 5.4953% | 4.3029% | 0.3080% | 0.05209 |
| V2 + inverse-variance sizing | 1.274191 | +0.031688 | 6.2839% | 4.9317% | 0.4367% | 0.05736 |
| **F2 + inverse-volatility sizing** | **1.318335** | **+0.075832** | **5.7865%** | **4.3893%** | **0.3364%** | **0.05272** |

The stronger inverse-variance controller has a higher gross Sharpe than the
inverse-volatility controller (1.36435 versus 1.35028), but loses that ranking
after actual costs. Its annual fees are 0.4367% versus 0.3080%. This is a useful
local example of why the net scorer, rather than an appealing gross-return
formula, must choose the policy.

F1's economic hypothesis failed. Averaging daily ridge coefficient estimates
did not beat pooling their normal equations. Its lower fees and lower beta do
not compensate for the score loss, and its penalty was not retuned to rescue it.

The joint policy adds 0.02655 Sharpe beyond F2 and 0.04123 beyond VTvol. The two
standalone gains are not simply additive: 0.04928 + 0.03461 exceeds the joint
gain of 0.07583. The combination changes positions, risk states observed by the
controller and actual costs; its own replay is essential.

Source: [independent actual readback](../../evidence/v2_score_opportunity_20261028/actual_readback_001.json),
[forecast results](../../evidence/v2_score_forecast_20261028/results.json),
[overlay results](../../evidence/v2_score_overlay_20261028/actual_001/results.json),
[joint results](../../evidence/v2_score_joint_20261028/actual_001/results.json).

## 2. Why these experiments had better expected value than another beta exercise

An independently planned readback of all 29 existing ledgers first examined
economic headroom. Deleting every recorded fee on V2's unchanged gross-return
path would increase its Sharpe only to 1.289755, a gain of 0.047252. This is a
fixed-holdings counterfactual, not a bound on joint signal/trading improvements.
It nevertheless demotes standalone fee optimization as the primary route to a
large improvement of the existing path.

Likewise, the actual historical complementarity between diagonal and full-factor
books is insufficient to promise a better portfolio. The fixed same-forecast
equal-risk reference mixture scores 1.22186, even using hindsight normalization.
The decorrelated-forecast version reaches 1.25617, only 0.01366 above V2. Neither
is an executed strategy. A costly ensemble implementation was therefore not
the leading next experiment.

The more useful observation was variation in V2's risk-return relation. In the
single predeclared EW63 lagged-risk diagnostic, low- and high-risk buckets have
annualized net means of 4.56% and 2.96%, with volatilities of 2.41% and 4.56%.
Intermediate bucket means are roughly flat. Bucket boundaries use hindsight
and are not trading rules. They motivated a separate continuous, causal sizing
formula whose parameters were fixed before its score was computed.

Separately, the current forecast applied one 1008-day coefficient memory to all
13 linear terms, 13 squares and beta. Earlier uniformly fast forecast failures
did not test restrained fast adaptation of only the linear block under the
selected V2 allocator. The initial observations of less stable linear relations
and more persistent nonlinear shape motivated this controlled contrast without
establishing that true coefficients necessarily drift.

Source: [opportunity audit](SCORE_OPPORTUNITY_AUDIT_20261028.md).

## 3. Winning forecast: preserve slow curvature, partially adapt the linear terms

F2 fits two complete pooled ridge regressions with half-lives 252 and 1008.
Both jointly use all 27 original columns and ridge 0.1. Let P select the first
13 linear-characteristic coordinates. The combined coefficient is

    theta_F2 = theta_1008 + 0.5 P (theta_252 - theta_1008).

Thus only the linear block is averaged. Squares and beta retain the slow fit.
The one-half mixing weight is fixed, not estimated from this experiment's
returns. No characteristic is selected by its realized outcome or name.

The design, clipping, label residualization, 126 matured-pair warm-up, factor
risk model and allocator settings otherwise remain V2. Forecast row t uses
X[t-1] and information available before t; its newest training label is t-1
paired with X[t-2]. Each forecast invocation resets its sufficient statistics
and the existing risk/solver session state.

This is a coefficient combination, not an assertion that an asymmetric
elementwise-forgetting Gram matrix solves a valid joint least-squares problem.
The two separate symmetric moment systems avoid that implementation error.

The exact prototype is [prototype.py](../../evidence/v2_score_forecast_20261028/prototype.py).
The local hypothesis and its counterarguments are documented in
[SCORE_FORECAST_RESEARCH_20261028.md](SCORE_FORECAST_RESEARCH_20261028.md).

## 4. Winning sizing: a causal multiplier on the F2 virtual book

Maintain the F2 strategy's unscaled virtual portfolio v separately from the
actual traded portfolio. At close t, its previous target earns g_t=v'R[t] and
drifts using its own denominator 1+g_t. Its next target comes from the unchanged
base allocator around that virtual drifted book.

Two normalized EW second moments of these earned gross returns are updated
through close t, with half-lives 63 and 1008. For either h,

    S_h <- 2^(-1/h) S_h + g_t^2
    M_h <- 2^(-1/h) M_h + 1
    q_h = S_h / M_h.

After 63 earned observations, use

    a_t = clip(sqrt(max(q_1008,1e-12) / max(q_63,1e-12)), 0.5, 2).

Before then a_t=1. The empty opening at row 252 is excluded from the count;
the first eligible multiplier is computed after close 315 for earning row 316.
Return a_t times the new F2 virtual target, with proportional reduction only
if actual gross exceeds 5. No full-sample risk normalization is used.

The official scorer drifts the actual positions and charges the actual stock
trades. Virtual costs are not substituted for actual fees and are not inserted
into the drift denominator. This distinction is why a multiplied net-return
ledger cannot verify the strategy. The joint controller observes its own F2
virtual gross-return path, not the old V2 path.

On the actual joint run, the multiplier ranges from 0.65662 to 1.64509, averaging
1.15596. Neither multiplier bound nor the gross cap binds. Mean actual gross
is 1.82364; maximum individual stock weight is 1.6441%. All 3,527 virtual
allocator calls are certified. Average instrumented rebalance time is 3.40 ms,
with p99 7.08 ms; the assignment limit is an average, not a per-call maximum.
The current joint century runtime gate has not been run. Measured short-run
timings and forecast extrapolation must not be relabeled as that check.

Implementation: [joint.py](../../evidence/v2_score_joint_20261028/joint.py),
[overlay.py](../../evidence/v2_score_joint_20261028/overlay.py).

## 5. What the historical comparison does and does not establish

| Policy | Original discovery | Original validation | Original audit |
|---|---:|---:|---:|
| V2 | 1.098002 | 1.656859 | 1.147558 |
| F2 | 1.117706 | 1.528936 | 1.498744 |
| VTvol | 1.087012 | 1.757166 | 1.298085 |
| Joint | 1.103512 | 1.633970 | 1.593029 |

The joint's main improvement is in the final historical segment. It is roughly
flat in the first and slightly lower in the middle. This is not three new
confirmations. Every segment has been exposed during development, and no
requirement that every segment improve was added after the result.

For joint minus V2, the fixed 63-day paired block interval is
[-0.08197,+0.21792]; the 21- and 126-day intervals also include zero. The interval
against F2 is [-0.06141,+0.11359] at 63 days. These are conditional, fixed-policy
resampling descriptions and do not correct the entire prior research search.
They do not prove a future advantage, nor do they trigger a new 95% significance
veto absent from the prospectively recorded score-based rule.

The candidate improves the available official score and has a simple
economically motivated, causal implementation. That supports nomination. It
does not supply access to the hidden evaluation history or a guaranteed future
Sharpe of 1.318. No inference of a pure stock-selection premium is needed for
this decision, and the modest realized beta is reported rather than erased.

## 6. Independent checks and failures retained

A separate reviewer reconstructed stock-level returns, drift and actual fees
for V2, F2, both overlays and the joint policy using the original return/cost
files and exact hash-matched targets. Maximum joint accounting discrepancy is
2.26e-17. Its EW moments and multiplier clocks reproduce exactly; reconstructed
actual-target hashes match the scorer run. The independent CSV score table and
paired intervals reproduce the owners' figures.

The F2 canonical actual-future check protects 1,501 forecast rows, 1,248
decisions and 1,247 economic observations at cut 1500, all exactly unchanged.
The prefix comparison is exact. The joint synthetic workflow passes all 22
specified checks, including F2 control equivalence, its virtual-book identity,
future/prefix/restart behavior and actual fee/drift accounting. The standalone
overlay synthetic workflow passes 38 checks.

The record also contains failures and limitations:

- Strict tests combining future alteration with a changed return-array memory
  layout failed downstream allocation/gross tolerances, despite identical
  protected forecasts. Separate same-layout future tests pass. The combined
  layout tests remain failed; their thresholds were not silently relaxed.
- The F1 constant-Gram synthetic forecast identity holds to about 9e-18, while
  downstream optimizer decisions amplify roundoff beyond the first tolerance.
- Original F1 and F2 NPZ checkpoint archives were truncated. Their CSV outcomes
  and hashes were retained. An unchanged F2 replay repaired its evidence in
  verified atomic NPY files and reproduced both original full forecast and
  target hashes exactly. The initial cause remains unknown; disk space was
  available. F1's score is independently verified from CSV, but its independent
  stock-level saved-target check remains blocked. Rejected F1 was not rerun.

These are explicitly scoped dispositions, not an assertion that every test in
the research history passed. Detailed commands, source ordering and failures
remain in each evidence packet and the independent readback.

During publication, Claude's branch advanced to `c51d31f`, with allocator
fallback/final-check fixes and a separate learned adaptive forecast option.
An independent [static readback](../../evidence/v2_score_forecast_20261028/concurrent_head_readback.json)
found unchanged temporal clocks. The handoff explicitly preserves those fixes
and distinguishes the new adaptive option from our F2. The measured 1.318335
remains the ce3-based research result; faithful integration on the new head must
reproduce it rather than inherit that score without execution.

## 7. Research literature and next useful questions

- [Pesaran and Pick, Forecast Combination across Estimation Windows](https://ap236.github.io/papers/PesaranPickAveW4Mar2010.pdf)
  motivates combining estimation memories under uncertainty. F2's block split
  and weights are our local design, not their estimated optimum.
- [Moreira and Muir, Volatility Managed Portfolios](https://www.nber.org/papers/w22208)
  motivates investigating risk that is not rewarded by proportional returns.
  [Cederburg et al.](https://www.lehigh.edu/~xuy219/research/COWY.pdf) supplies
  essential counterevidence about implementable timing. The controller therefore
  uses past-only scaling and pays actual costs.
- [Tu and Zhou](https://ink.library.smu.edu.sg/lkcsb_research/1105/) provides the
  strategy-combination perspective. Local diagnostics demoted another blend
  despite that plausible prior.
- [Feng and He, arXiv:1902.01015](https://arxiv.org/abs/1902.01015) supplies
  heterogeneous-coefficient/estimation-risk context. No Bayesian sampler or
  empirical US-market result is imported into this simulator.
- [Alpha Architect's research index](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/)
  points to the Cederburg paper. The technical claim above rests on the primary
  paper, not the secondary summary.

After faithful production integration, the next score question should concern
how to preserve the demonstrated gross timing benefit while reducing the extra
trading it causes, or how conditional factor allocation differs from one common
size multiplier. The [DeMiguel, Martin-Utrera and Uppal publisher record](https://doi.org/10.1111/jofi.13395)
is relevant to the latter; its full publisher HTML was inspected after an earlier
access failure. Neither question has been tested here, and
neither authorizes a fresh unrecorded grid of smoothing parameters.

The prior beta-calibration questions remain intellectually useful but are not
blocking gates for this score improvement. This wave is complete: four fixed
standalone alternatives and one conditional joint alternative, all reported.

## Attribution

The user set the score-first objective and directed the research. GPT and its
research agents designed and executed these isolated prototypes and independent
checks. Claude wrote the baseline and remains the intended production
implementer. No applicant contribution, submission, hidden-market result or
human-authored discovery is invented by this report.
