# Allocation research for the official net-Sharpe objective

28 October 2026, Europe/Paris. Source baseline: `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`.
This research responds to the user's instruction to prioritize the evaluated
score. All supplied-history stages are now development data. The README permits
parameter choice on that history, while future dependence, ruin, the beta
condition and runtime remain real constraints. A prettier risk decomposition is
not a substitute for a higher official score.

## Decision after looking at the opportunity evidence

**Prioritize a bounded causal size controller on the unchanged V2 book.** Freeze
two variants, inverse volatility and inverse second moment, and test the complete
scorer with actual drift and actual trading costs. Keep forecasts, factor-risk
geometry and virtual V2 trading decisions unchanged. The exact specification,
preimplementation harness and source-review packet are in
[the pilot plan](../../evidence/v2_score_overlay_20261028/PLAN.md).

My initial preference was an executed mixture of the diagonal and full-factor
books. The independent ledger readback changed that ranking. Preserve this
change in judgment rather than promoting the original idea after contrary data.

| Existing-policy pair | Daily correlation | Hindsight equal-risk Sharpe | Fixed raw half-half Sharpe |
|---|---:|---:|---:|
| beta feature / full factor risk | .50830 | 1.22186 | .96545 |
| decorrelated beta forecast / full factor risk | .53261 | 1.25617 | 1.04718 |

V2 scores 1.24250. Even the second pair's hindsight equal-risk reference improves
only about .014; it also combines different forecasts. The first, cleaner
same-forecast comparison loses. These reference series use full-sample risk
normalization and separately charged leg costs; neither is an executed
implementable aggregate book. This is insufficient headroom to prioritize a
complex mixture ahead of the observed conditional-risk opportunity.

The fixed lagged-EW63 diagnostic places V2 in risk buckets with realized
annualized volatility increasing from about 2.4% to 4.6%, while average returns
do not increase proportionally. The lowest/highest bucket Sharpes are roughly
1.90/.65. This motivates testing size changes; it does not establish that a
causal controller earns a higher score. Bucket cutoffs used future information
and are excluded from the controller. Exact observations are in the
[opportunity packet](../../evidence/v2_score_opportunity_20261028/results.json).

## Why cost optimization is not the leading standalone opportunity

V2 already has an absolute-cost penalty around drifted holdings, producing
no-trade behavior. Its annual fee charge is about .1756%, and the unchanged-book
counterfactual obtained by removing every fee moves Sharpe from 1.24250 to 1.28975:
only+.04725. This exact counterfactual includes the change in standard deviation;
fee/vol alone gives a nearby but different .04588.

This is not an upper bound on every possible new trading policy: a better policy
can also alter gross returns and risk. It is a useful bound on the fee-removal
story for this fixed book. Cost horizons 5,60,120 and 250 were already tried on
C09 and did not improve its score. Revisiting execution becomes more valuable
if a new forecast creates an economically strong, short-lived signal or the
new size controller incurs material extra costs.

[Gârleanu and Pedersen](https://nbgarleanu.github.io/DynTrad.pdf) explain how
expected signal persistence changes the dynamic trading target. Their closed
form uses quadratic trading costs, whereas this scorer charges proportional
costs. We should retain the persistence question, without transplanting their
partial-adjustment formula as an optimum for this task. The arXiv paper
[de Lataillade et al.](https://arxiv.org/abs/1203.5957) directly treats linear
costs and motivates threshold/no-trade behavior, with a much simpler position
setting than our coupled thousand-stock allocator. Neither paper warrants
another arbitrary buffer on top of the current exact absolute-cost optimizer.

## The admitted size-controller experiment

Let v_t be the unchanged V2 target after close t. The virtual book earns
g_t=v_(t-1)'r_t and drifts with denominator 1+g_t. It then calls the exact V2
rebalance using its own drifted holdings. Never feed the actual overlay holdings
to the virtual engine; that would change the base trading policy and confound
the size intervention.

For h in{63,1008}, update normalized exponential second moments using only
already earned virtual gross returns:

`S_h <- 2^(-1/h)*S_h + g_t^2`,
`M_h <- 2^(-1/h)*M_h + 1`, and `q_h=S_h/M_h`.

The opening call has earned no return and does not update these states. With
the scorer's start 252, observations begin at row 253. Multiplier a_t remains 1
for fewer than 63 earned observations. At count 63, close 315, and every close
thereafter, define `z=max(q1008,1e-12)/max(q63,1e-12)` and test exactly:

* **VTvol:** `a_t=clip(sqrt(z),.5,2)`.
* **VTvar:** `a_t=clip(z,.5,2)`.

The long-memory numerator supplies a causal reference level; it is not a
full-sample volatility normalization. This is an intentionally simple adaptive
rule, not a claim that EW1008 estimates a structural long-run risk level or that
either exponent is universally optimal. No return-mean fit, learned regime
date, additional target-beta choice, or window/clip grid is admitted here.

Return the actual target `a_t*v_t`, with the original gross limit 5 enforced by
common proportional scaling. The official scorer then computes actual drift
and actual fees. Each base stock cap is .05, so the overlay's mathematical stock
bound can reach .10; there is no assignment-level stock cap, and actual maximum
weights are reported. A scalar preserves the estimated zero-beta equality;
realized net beta is measured independently and can change.

The wrapper's actual cost is `c'abs(actual_target-actual_held)`, not the virtual
V2 cost multiplied by a_t. Base and actual drift denominators also differ.
The multiplier's changes therefore carry a real trading charge, and its score
cannot be inferred by multiplying V2's saved net returns. The recorded
terminal target incurs the scorer's closing charge even though its next return
is never earned; preserve that endpoint behavior.

### Literature that informs, and challenges, this experiment

[Moreira and Muir's institutional manuscript](https://law.yale.edu/sites/default/files/area/workshop/leo/leo17_moreira.pdf)
motivates reducing risk when volatility rises without a proportional increase
in expected returns. The manuscript also considers inverse-volatility scaling
and leverage limits. We use that economic hypothesis, not their ex-post
normalizing constant, fitted spanning portfolio or stock-market performance
as evidence for this simulator. Our two exponents and bounded causal reference
level are explicitly development choices.

[Cederburg, O'Doherty, Wang and Yan](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
provide the necessary challenge: apparent gains in volatility-managed spanning
regressions need not survive real-time implementation, and unstable combination
weights can drive disappointing performance. Their
[SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3357038)
also provides a primary abstract. This argues for the complete scorer replay and
simple frozen weights, not for declaring volatility management either proven or
useless before testing it here.

### Admission and failure interpretation

Full official net Sharpe is the primary economic selection criterion. An
alternative must beat the fixed-one replay of current V2, keep abs(realized net
beta)<.2, remain finite/solvent, pass the causal workflow and fit the observed
runtime budget. Report all original stages and paired 21/63/126-day block
intervals. A95% significance hurdle is not an additional assignment objective.
The historical stages remain exposed; prospective rules do not make them fresh
confirmation. Tiny gains require proportionate skepticism but remain visible.

Reject a failing version as specified; do not rescue it by shortening the risk
window, shifting the first active date, choosing another clip, or changing the
slow anchor after seeing its result. The leading economic failure mechanisms
are forecasted-risk delay, a genuine positive conditional risk premium, scale
changes that buy/sell after noise, and extra trading costs. The pilot can
distinguish actual gross-return improvement from the fee increment.

## What remains useful in portfolio combination

Covariance scale .3 is not the same object as blending positions from scale 0 and
scale 1. Even without costs, inverse covariance is nonlinear in that scale;
constraints and holdings-dependent trading costs add further differences.
The independent mixed-book tests remain conceptually valid, although the
current ledger headroom has moved them down the queue.

If pursued later, maintain each virtual subbook's own target and drift it with
its own return denominator. Combine newly computed targets using predeclared
past-only risk scales, and let the actual scorer charge the net aggregate trade.
A raw half-capital mixture is dominated by the much more volatile diagonal leg:
beta_feat/fr_beta has a variance ratio about 259.5. That is why an equal-capital
score is not a clean test of useful risk diversification.

[Tu and Zhou's institutional record](https://ink.library.smu.edu.sg/lkcsb_research/1105/)
supports portfolio combination as a response to parameter uncertainty. It does
not identify the best weights for these two policies. No learned tangency mix
or another optimizer over our already-selected strategy library is introduced.

## Covariance research reserve: a distinct question, not another admitted run

Pure PCA rotation is not a new risk model. For orthogonal Q,
`Dtilde=DQ` and `Ftilde=Q'FQ` give exactly the same `D F D'`. A score change from
a supposedly pure rotation indicates numerical behavior, incorrect coordinate
transport, or another unstated modeling choice. Truncation and eigenvalue
shrinkage are genuine choices and must be stated as such.

The matched-diagonal control deleted stock-level off-diagonal covariance. It
did not test the separate question of shrinking correlations among the 26
estimated factor returns. A future simple probe could keep V2 fixed and use
`F_new=.5*F+.5*diag(diag(F))` before the existing factor scale .3. This retains
cross-stock common risk through D, remains positive semidefinite, and changes
relative directions rather than just scaling every factor eigenvalue equally.
The exploration engine in `research/v2/exploration/strategy_v2.py` already has
an unused `factor_shrinkage` interface, but none of its recorded 25 variants
exercises it. This is not a current `handoff_v2` CONFIG key. This reserve is not
authorized as a fifth candidate by this document.

The drawback is basis dependence: diagonal shrinkage in named characteristic
coordinates is not invariant to arbitrary rotations and may destroy useful
factor correlations induced by the feature geometry. More elaborate shrinkage
should use a declared loss and coordinate convention rather than a vague
promise that a covariance estimator is better.

[Ledoit and Wolf](https://www.econ.uzh.ch/apps/workingpapers/wp/econwp137.pdf)
provide a primary portfolio-loss treatment of nonlinear eigenvalue shrinkage.
Their large-dimensional results do not automatically carry over to a 26-factor
EW estimator, nonstationary characteristic exposures, correlated expected
returns and our proportional-cost constraints. We would judge a candidate on
official net Sharpe; a covariance-loss improvement alone would not promote it.

## Executed allocation pilot

The synthetic E2E passed 38/38 predeclared checks, including exact direct/fixed
V2 targets, unchanged virtual targets under each overlay, future/prefix/reset
behavior and exact actual fee/drift reconciliation. Both actual alternatives
then completed with the source-bound unchanged scorer:

| Policy | Net Sharpe | Discovery / validation / audit | Fees/year | Net beta |
|---|---:|---|---:|---:|
| Fixed-one V2 control | 1.242503 | 1.098002 / 1.656859 / 1.147558 | .175566% | .046496 |
| VTvol | **1.277109** | 1.087012 / 1.757166 / 1.298085 | .307982% | .052090 |
| VTvar | 1.274191 | 1.064625 / 1.806735 / 1.346022 | .436717% | .057363 |

VTvol is the higher-scoring member of this two-candidate family. Its gain is
.034606 net Sharpe, with paired 63-day interval[-.059673,+.128229]; VTvar's gain
is .031688 with interval[-.134782,+.185188]. Both pass the recorded development
contender rule, not a claim of statistically established future superiority.
The inverse-volatility choice incurs less additional trading cost than the
inverse-second-moment choice. The selection did not require a new window or
clipping search.

All 10,581 base solves are certified. Forecast and virtual-target identities are
exactly shared across the three runs. Actual stock-level accounting reconciles,
there is no aggregate gross scaling, and instrumented mean rebalance time is
about 3.2 ms. VTvol multipliers span .6806–1.7943; VTvar hits the lower cap 22 times
and upper cap 560 times. VTvol's annual volatility increases from 3.827% to 4.303%:
the experiment improves the mix of risk across time, rather than targeting a
lower unconditional volatility. Its slow reference level is causal and changes
through the sample.

Results and complete daily/decision ledgers are in
[actual_001/results.json](../../evidence/v2_score_overlay_20261028/actual_001/results.json).
The parent plan's conditionally admitted combination with winning forecast F2
was then executed separately. It scores 1.318335, above V2, F2 alone and VTvol
alone, with all costs included and net beta .05272. The underlying F2 virtual
book, rather than the original V2 book, drives the joint moments. No parameters
were changed. Its full/stage results, uncertainty and evidence are in
[the joint result](../../evidence/v2_score_joint_20261028/RESULTS.md). This does
not alter either individual family's frozen sources or outcomes.

## Evidence status and provenance

The pilot PLAN and policy specification preceded the overlay runs. This report
now includes their completed results. The pilot directory preserves the
preimplementation harness, its expected missing-module failure, exact source
hashes and independent source review. Before execution, the reviewer requested
source-bound E2E admission, a 1e-8 numerical tie guard and preservation of all
synthetic output cases; these evidence changes retained every existing test
assertion/tolerance and left the overlay implementation unchanged. Original
pre-review files and hashes remain available. Century-length runtime is not
claimed from this pilot.

Primary papers opened: full institutional PDFs for Moreira–Muir, Cederburg et
al., Ledoit–Wolf and Gârleanu–Pedersen; arXiv abstract for de Lataillade et al.;
institutional abstract/metadata for Tu–Zhou. Direct NBER landing-page access
returned 403, so the accessible Yale author manuscript was used. No quoted
real-market Sharpe uplift is transferred to the simulated market.
