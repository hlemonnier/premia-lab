# Score opportunities: portfolio risk timing outranks another blend search

28 October 2026, Europe/Paris. Pinned implementation:
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`. Independent observational readback of
all29 committed daily ledgers and the earlier C01–C12 reported discovery results.

## Decision

**The most concrete untested score opportunity in these ledgers is bounded,
causal variation in total portfolio risk.** V2's past squared returns distinguish
future risk levels, while the high-risk bucket does not earn a compensating
return in this sample. A fixed, exact-scorer replay of this idea has a stronger
economic motivation than further explicit-beta refinement or another attempt
to explain risk calibration alone.

The much-discussed diagonal/factor diversification is real but offers limited
additional headroom over V2: the clean same-forecast equal-risk reference blend
scores1.222, below V2's1.243, even with hindsight risk normalization. The version
using decorrelated diagonal forecasts reaches1.256, only0.0137 above V2. Those
are descriptive series, not executed policies. Low correlation by itself is
insufficient evidence that an actual blend will improve V2.

The official objective remains future net Sharpe with the required market-beta,
causality and runtime conditions. The brief explicitly permits tuning on the
full supplied sample. Every period here is development history; the old stage
names do not restore an untouched validation set. No purity-of-alpha condition,
minimum gross, aesthetically preferred leverage or extra Sharpe hurdle is added.

## 1. What was measured

A [prospective plan](../../evidence/v2_score_opportunity_20261028/PLAN.md) fixed
the input identities, three reference pairs, stage masks, accounting checks,
one lagged-risk timescale and interpretation before calculation. Parent source
review preceded execution. The saved-output workflow exited0 and reconciled
all29 five-row arrays: dates253..3778, finite economic fields, net=gross-fees,
and a common market series. Tolerances match the prior independent ledger audit.

The complete numbers are in
[results.json](../../evidence/v2_score_opportunity_20261028/results.json), with
source/input hashes and the environment. The
[execution record](../../evidence/v2_score_opportunity_20261028/EXECUTION.md)
contains the exact command. This review ran no strategy and changed no production
source. All three mixtures and all five buckets are reported, including results
that weaken the proposed blend.

## 2. Standalone cost saving has a small ceiling on the existing V2 path

| V2 full-sample quantity | Exact readback |
|---|---:|
| Net Sharpe |1.242503 |
| Gross Sharpe, identical holdings |1.289755 |
| Difference from deleting all recorded fees |**0.047252** |
| Annual arithmetic net return |4.755036% |
| Annual recorded trading fees |0.175566% |
| Annual net volatility |3.826982% |
| Annual gross volatility |3.822899% |

The exact score difference is0.04725; dividing annual fees by net volatility gives
only an approximation because fees also affect measured return variance. Even
the impossible elimination of every paid fee would not transform this particular
holdings path into a Sharpe1.5 strategy. Standalone fee reduction is therefore
not the leading opportunity for a large score gain.

This is a fixed-holdings counterfactual, not an upper bound on every possible
cost-aware strategy change. A better trade policy can change which forecasts
are held, their risk and their persistence; those joint effects remain possible.
The prior cost-horizon scan was also on the diagonal C09-like policy, not V2.

## 3. Diversification exists, but V2 already captures much of its value

The three pairs were fixed before calculation. The equal-risk reference is
`0.5*r_a/sd_full(a) + 0.5*r_b/sd_full(b)`, rescaled by a common constant to V2's
overall risk units. Each full-sample standard deviation contains future
information. Fees are the corresponding linear combination of the separately
scored legs' fees, not netted aggregate-book trading costs. No forecast claim,
market-feasible hedge or executed strategy is inferred from these numbers.

| Fixed pair | Net correlation | Variance ratio, first/second | Equal-risk reference Sharpe | Raw50/50 Sharpe |
|---|---:|---:|---:|---:|
| beta_feat / fr_beta |0.50830 |259.5296 |**1.22186** |0.96545 |
| decor_beta / fr_beta |0.53261 |168.5494 |**1.25617** |1.04718 |
| V2 / C09 |0.69542 |0.42658 |**1.15526** |1.11012 |

`beta_feat` and `fr_beta` share the same forecast family; portfolio construction
is the cleaner comparison. `decor_beta` also alters the forecast geometry.
The enormous variance ratios explain why adding nominally equal subbook weights
does not give equal risk. They do not identify a stable future normalization.

| Reference series | Discovery | Validation | Audit |
|---|---:|---:|---:|
| Actual V2 |1.09800 |1.65686 |1.14756 |
| beta_feat / fr_beta, hindsight equal risk |0.95816 |1.59670 |1.52289 |
| decor_beta / fr_beta, hindsight equal risk |0.98353 |1.58665 |1.58880 |
| V2 / C09, hindsight equal risk |0.96430 |1.34082 |1.66103 |

The mixtures trade some earlier-period score for later-period score. The
decorrelated mixture's full-sample advantage is0.013662, despite hindsight
normalization. This makes an expensive blend implementation a weaker first
choice than the low-correlation headline initially suggested. An actual blend
may nevertheless gain or lose from causal rescaling, trade netting and drift;
only a complete official-scorer replay can determine that.

The descriptive regression of C09 on V2 leaves annual residual mean0.1216% and
residual volatility4.2106%, a ratio0.0289. For decor_beta those figures are
0.4167%,3.2041%, ratio0.1301. These retrospective single-regressor appraisals are
not traded residual alpha and have no selection-adjusted significance claim.
They reinforce that low correlation alone should not dictate the next experiment.

## 4. A stronger mechanism: high realized risk is predictable without higher returns

For V2, the sole fixed predictor is a normalized EW mean of previous gross
squared returns, half-life63. The estimate at an observation excludes that
observation. The first126 economic observations are removed from this
diagnostic. Five buckets use full-sample quintile thresholds on the remaining
lagged estimates. Thus the **estimates are past-only but the bucket thresholds
are descriptive hindsight thresholds**, not an implementable timing policy.

Each bucket contains680 observations:

| Lagged-risk bucket | Net mean, %/year | Net vol, %/year | Net Sharpe | Fees, %/year | Next gross second moment |
|---|---:|---:|---:|---:|---:|
| Lowest |4.5601 |2.4059 |1.8954 |0.0907 |2.3288e-6 |
| Second |4.6998 |3.2335 |1.4535 |0.1307 |4.1808e-6 |
| Third |4.6312 |3.6889 |1.2554 |0.1514 |5.4264e-6 |
| Fourth |5.0850 |3.9272 |1.2948 |0.1850 |6.1510e-6 |
| Highest |2.9553 |4.5581 |0.6484 |0.2273 |8.2429e-6 |

The conditional second moment rises materially, while mean return does not.
The return pattern remains economically visible before fees: annual gross means
are4.6507%,4.8306%,4.7826%,5.2700%,3.1826%. The high-risk weakness therefore is
not merely the extra transaction-cost charge.

This supports testing a smooth, bounded, past-only risk multiplier with a fixed
formula. It does not prove its score will improve. Chronological composition,
estimation error, changing alpha, noisy conditional means and the incremental
trades required by resizing can all erase a diagnostic advantage. No bucket
cutoff, high-volatility trading suspension or result-fitted scaling exponent is
recommended from this table.

The complete actual-book replay must recompute position drift and costs. Scaling
the saved net-return series is insufficient: V2 trades around drifted holdings,
and a multiplier changes both the actual book and the next trade. A controller
must define whether V2's state is an independent virtual book or is recomputed
around actual holdings. Those are different policies.

## 5. Deduplication: avoid rediscovering already tested ideas

The following reported discovery scores are from the original C01–C12 packets,
all on the same1,762 earning observations253..2014. They are not comparable to
V2's full-sample score without matching sample and policy.

| Candidate | Principal change | Discovery net Sharpe |
|---|---|---:|
| C01 | Linear,252-day memory |0.6223 |
| C02 | Additive squares,252-day memory |0.6376 |
| C03 | Faster63-day memory |0.1065 |
| C04 | PCA factor allocation |0.6542 |
| C05 | Covariance-weighted alpha learning |0.6025 |
| C06 | Covariance-weighted learning + factor allocation |0.7629 |
| C07 | Exact gross constraint |0.6798 |
| C08 | Higher risk-aversion scalar |0.6262 |
| C09 | Slower1008-day memory |0.7002 |
| C10 | Rank50 version of C06 |0.7399 |
| C11 | Pairwise characteristic interactions |0.6033 |
| C12 | Local additive hinge extensions |0.6257 |

Later full-sample research already tested252-day/near-expanding memory,5-/20-day
labels, residual reversal and persistence scaling, grouped characteristics,
projection away from return factors, prediction decorrelation, beta features,
several cost horizons and factor-risk scales0.1/0.3/1.0. R27, matched diagonal,
B0 and B05 are the four followups. All29 ledgers are retained in the diagnostic.

Most negative forecast/cost variations ran on the C09-like diagonal policy.
Their failures do not prove these changes fail under V2; conversely, combining
all of them with V2 creates many new model choices. The clean next question
needs a mechanism, not simply a list of negative variants to cross with a winner.

V2's low-scale and5x versions have return correlation0.999988 and Sharpe1.24403
versus1.24250. Constant leverage is not a plausible route to a material gain in
this setting. The matched-diagonal intervention's higher exposure is endogenous
to its changed risk geometry; it does not invalidate the experiment, but neither
does it isolate pure direction from sizing and cap effects.

## 6. Recommended next coding questions

**First: a single bounded causal total-risk controller around V2, scored exactly.**
Use a fixed lagged-risk estimator, explicit startup rule and one prespecified
multiplier formula. Preserve the baseline mean forecast and make state/drift/cost
handling explicit. Compare official net Sharpe, beta and solvency/runtime with
V2, with stage diagnostics reported rather than turned into new independent
objectives. Reject a score loss; do not rescue it by fitting bucket thresholds.
The separate allocation specification should own exact implementation details.

**Second: heterogeneous forecast persistence with shrinkage toward V2's slow
baseline.** The slower global learner previously helped, while fast global
adaptation was very damaging. That motivates estimating which coefficient
directions deserve adaptation instead of accelerating every feature together.
A compact, regularized fast/slow or mean-reverting coefficient model is a new
question; a generic larger nonlinear model repeats lower-value explored work.
The forecast-research specification should own the exact candidate and paper
support. This second recommendation is a mechanism-based research hypothesis,
not an outcome of a new score run in this packet.

The fixed two-book blend is a lower-priority alternative, not a discarded idea.
If implemented, causal normalization and aggregate trade accounting are mandatory,
and its score must be measured rather than imported from the reference series.

No calendar is imposed. No new candidate is promoted by this readback. Its role
is to direct computation toward a larger plausible gain in the official score.

## Subsequent bounded-wave outcome

The separate prospective research wave subsequently tested two forecast and two
size alternatives, then its pre-admitted conditional joint. Independent saved-
output accounting now verifies **F2+VTvol net Sharpe1.318335**, versus V2's
**1.242503**, a gain of**0.075832**. Actual stock-level drift, fees, virtual/actual
target hashes and moment clocks reconcile. Both selected components improve
the point score separately; the joint improves on each. F1 loses and remains
rejected. The joint's63-day paired difference interval is[−0.081966,+0.217923],
so future superiority is unresolved despite the development-score improvement.

The complete table, forensic evidence, preserved numerical failures and F1's
unavailable stock-level readback are documented in the
[independent pilot readback](../../evidence/v2_score_opportunity_20261028/ACTUAL_READBACK_RESULTS.md).
This outcome was not known when the opportunity diagnostics above were specified.
