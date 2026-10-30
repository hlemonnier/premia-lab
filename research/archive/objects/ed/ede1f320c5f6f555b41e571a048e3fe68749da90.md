# Score research, wave 2: 1.444733 net Sharpe

29 October 2026, Europe/Paris. Root integrated research decision.

## Decision

The selected research policy is **F2 forecast -> E2 execution -> fixed M1 market
sleeve**. Its unchanged-original-scorer net Sharpe is **1.444733300556666**,
versus **1.318334966090838** for the previous F2 + VTvol leader and
**1.242503073307361** for original V2. The gains are +0.126398 Sharpe (+9.59%)
and +0.202230 (+16.28%), respectively. These percentages describe relative
changes in Sharpe, not investment returns.

The full historical score, actual stock-level accounting and causal workflows
have been reproduced. The selected prototype also passes its separately
authorized century-runtime workflow. Claude's production package has not yet
integrated this research policy; its score must be reproduced after integration.

The objective is the official future net Sharpe under the brief's beta,
information, solvency and runtime conditions. All supplied historical periods
are exposed development data. The original labels discovery/validation/audit
below identify fixed historical masks, not fresh confirmation samples.

## 1. Complete outcome set

The master plan was committed at `d2997e0d98c6407da4b503a77060966904486062`
before new policy scores. It admitted exactly four standalone alternatives and
one conditional composition of individually improving families. E2 beat E1,
M1 qualified, and F3 failed. The sole composition therefore included E2 and M1
with the unchanged F2 forecast. No sleeve-weight, feature-subset, window,
penalty or subsequent subset grid was run.

| Policy | Full net Sharpe | Change from prior leader | Annual fees | Realized net beta | Decision |
|---|---:|---:|---:|---:|---|
| F2 + VTvol reference | 1.318335 | — | 0.336406% | 0.052720 | Reproduced reference |
| E1 scalar cost projection | 1.329123 | +0.010788 | 0.265873% | 0.052665 | Improved; E2 higher |
| E2 actual-book allocation | 1.339582 | +0.021247 | 0.244151% | 0.052981 | Selected execution family |
| F3 conditional characteristic premia | 1.294393 | -0.023942 | 0.344646% | 0.053234 | Rejected |
| M1 fixed +0.05 market sleeve | 1.426561 | +0.108226 | 0.337040% | 0.102711 | Best standalone |
| **F2 -> E2 -> M1** | **1.444733** | **+0.126398** | **0.253792%** | **0.102978** | **Selected composition** |

Source: root's independently reconstructed
[standalone results](../../evidence/v2_score2_root_20261029/standalone_readback_001.json)
and [joint results](../../evidence/v2_score2_root_20261029/joint_readback_001.json).
Annual fees and returns use arithmetic daily means times 252, not CAGR.

| Historical diagnostic | Prior leader | E1 | E2 | F3 | M1 | Selected joint |
|---|---:|---:|---:|---:|---:|---:|
| Original discovery | 1.103512 | 1.124469 | 1.126129 | 1.089820 | 1.178669 | **1.199035** |
| Original validation | 1.633970 | 1.647160 | 1.671238 | 1.570834 | 1.810260 | **1.842364** |
| Original audit | 1.593029 | 1.570662 | 1.586043 | 1.576991 | **1.664495** | 1.654664 |

The joint improves all three periods versus the prior leader. It does not
dominate M1 in every period: its final-segment Sharpe is slightly lower.
The frozen selection metric is the full original score, so the joint clears
the predeclared requirement to beat best standalone M1 by more than 1e-8.

## 2. What changed economically

### E2 makes changing portfolio size cheaper

The previous controller computed a new virtual F2 portfolio and multiplied its
target by a causal volatility ratio. That multiplication did not optimize the
resulting trade against the actual drifted holdings. E2 maintains the exact
same independent F2 virtual book and its EW63/EW1008 gross-return moments,
then solves a second allocation problem around its own actual held positions.
At desired multiplier a, risk aversion is 200/a and the stock cap is 0.05*a.
The cost horizon remains 20 and the gross cap remains 5.

The frictionless quadratic scaling motivates gamma/a. Actual transaction
costs, inherited constraints and the distinct held book determine the actual
solution; it is not simply a times the virtual solution. Risk and warm-start
state are independent between the two books and are reset only at a new
forecast session, not at each daily parameter change.

E2 alone leaves gross Sharpe practically unchanged: 1.397175 versus 1.397145.
Annual fees fall from 0.336406% to 0.244151%, a reduction of about 27.4%, and
net Sharpe rises to 1.339582. This is useful implementation improvement without
a new predictive signal. E1 also improves net performance but less strongly.

The inherited allocator first solves its stock-cap/beta problem and then
proportionally reduces gross if necessary. Its convergence certificate does
not prove optimality for a different optimization problem with an explicit
gross constraint. The factor scale 0.3 remains a chosen penalty, not a calibrated
risk forecast. Neither qualification is hidden by the better observed score.

### M1 deliberately holds a small market component

M1 adds 0.05/N to each of the N supplied stocks after the independent inner
policy produces its target. These are actual stock trades, with actual cost
netting. There is no separate free index instrument. The inner portfolio keeps
its own drift denominator, risk state and sizing history; combined outer
holdings never feed back as if they were the inner book.

The +0.05 weight was fixed before the scoped marginal-Sharpe diagnostic and
before M1 was scored. The diagnostic examined only the derivative at zero:
the market mean must exceed the existing mean times covariance divided by
existing variance. That threshold incorporates overlap with the strategy;
unused beta capacity alone would not justify the trade. No weight optimization
was performed. See the
[research challenge](SCORE2_RESEARCH_CHALLENGE_20261029.md).

There was no outer gross-cap binding on either actual M1 or joint path. M1's
standalone gross-return increment equals 0.05 times the market return each
day, verified to 6.18e-18; the actual combined fee difference gives its net
increment. Around E2, the selected joint adds 0.723996 annual arithmetic
percentage points of gross return, pays 0.009642 additional percentage points
of fees, and retains 0.714354 points net. This is intentional market exposure,
not newly identified stock-selection alpha.

The joint's net beta is 0.102978, versus E2's 0.052981. Its observed stage betas
are 0.102400, 0.101359 and 0.106966. The total future portfolio must satisfy the
brief's beta condition; the current historical beta does not guarantee future
compliance. The gross-5 and stock caps are our construction choices, not
additional requirements imposed by the evaluator.

The +0.05 sleeve is an increment of market notional around the unchanged raw-
beta policy; the resulting total beta is about 0.103. The earlier corrected-
beta experiment targeted total beta 0.05 while changing labels, risk residuals
and the hedge. Those rejected outcomes remain intact; this is a separately
specified policy with a different total exposure.

### Their combination improves the net result, with non-additive costs

Relative to M1, the joint adds 9.908 annualized basis points of net mean return:
8.325 bps from lower actual fees and 1.584 bps from higher gross mean return.
Its gross Sharpe is slightly lower, 1.502307 versus 1.502602. The net score gain
is therefore chiefly execution improvement. Relative to the previous leader,
annual fees fall by 8.261 bps, or 24.56%.

E2 prices trades of its independent inner book. The scorer charges netted
trades of the final joint book. This is not one optimizer that jointly minimizes
all combined transaction costs. The additional market-sleeve fee depends on
the surrounding strategy: about 0.964 bps per year around E2, versus 0.063 bps
around the old reference. Adding separately costed return series would miss
this difference; the selected score comes from the actual composed stock targets.

### F3 was a failed research hypothesis

F3 appended 26 strongly shrunk interactions between existing characteristics
and one causal market-volatility state. It left beta un-interacted, preserved
the F2 partial fast/slow combination, and applied tenfold ridge shrinkage to
the interactions. Its label clock, future-alteration checks and optimizer
checks passed, but its score fell to 1.294393. Both gross mean deterioration
and slightly higher fees contributed. No new state, penalty, window or feature
subset was tried to rescue it. This rejects that fixed implementation on this
development sample; it does not establish that every conditional-premium model
must fail.

## 3. What the research literature contributed

- [Gârleanu and Pedersen, Dynamic Trading with Predictable Returns and
  Transaction Costs](https://www.nber.org/papers/w15205), also available on
  [SSRN](https://ssrn.com/abstract=1444706), motivates partial adjustment and
  attention to signal persistence when trading is costly. Its quadratic-cost
  analytical result is not a theorem for our proportional-cost E1 objective.
- [Boyd et al., Multi-Period Trading via Convex Optimization](https://arxiv.org/abs/1705.00109)
  provides the return/risk/cost allocation framework. E2 uses a single-period
  adaptation around actual holdings; this project does not claim to implement
  that paper's full multi-period controller.
- [DeMiguel, Martin-Utrera and Uppal, A Multifactor Perspective on
  Volatility-Managed Portfolios](https://doi.org/10.1111/jofi.13395),
  [SSRN version](https://ssrn.com/abstract=3982504), motivates conditional
  relative exposures and attention to netted stock trades. Our F3 failure is
  retained despite that favorable motivation; their empirical results do not
  predict a gain in this simulated market.
- [Tu and Zhou, Markowitz Meets Talmud](https://ink.library.smu.edu.sg/lkcsb_research/1105/)
  motivates considering a simple equal-weight direction alongside an estimated
  portfolio. It neither calibrates the +0.05 weight nor proves its future return.

As a later interpretation cross-check, the Alpha Architect summaries
[on volatility-managed portfolios](https://alphaarchitect.com/the-performance-of-volatility-managed-portfolios/)
and [transaction costs](https://alphaarchitect.com/transaction-costs/) were used
as pointers back to primary papers. The author-hosted
[Cederburg et al. paper](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
shows why attractive in-sample spanning results need not translate into a
real-time strategy. The author-hosted
[Frazzini, Israel and Moskowitz paper](https://pages.stern.nyu.edu/~afrazzin/pdf/Trading%20Cost%20of%20Asset%20Pricing%20Anomalies%20-%20Frazzini%2C%20Israel%20and%20Moskowitz.pdf)
supports studying cost-aware implementation with limited style drift. These
cross-checks occurred after the fixed trials; they did not define another
candidate or change the supplied cost schedule.

## 4. Causality, scorer fidelity and failures retained

Prospective specifications and E2E harnesses preceded policy implementations.
Missing-policy failures were recorded first. Another researcher inspected
sources and saved synthetic evidence before root released each actual run.
The master commit and subsequent source-bound releases identify the exact
versions used.

The joint synthetic workflow passes 14 summary checks and 383 workflow
assertions across 12 runs. Two independent reviewers verified the unchanged
dependencies, internal book separation, costs, controller clocks and the
runtime observation adapter. The actual workflow passes 9 summary checks and
192 assertions across 6 runs. Standalone E2 and M0 reproduce exactly; the
joint preserves inner E2 targets, virtual F2 targets and controller states.
Altered-future, prefix and cross-history restart comparisons are exact over
their protected ranges. Both 3,527-solve books are certified.

Root separately reconstructed the saved stock targets against the original
returns and costs without importing a policy. It verifies file and raw-array
hashes, shapes and dtypes. Maximum joint accounting discrepancy is 5.20417e-18.
It independently reproduces the score, beta, annual fees and stage results.

The original endpoint convention is preserved: zero-based first decision 252,
3,527 decisions through 3778, 3,526 earned rows 253..3778, free opening, charged
final rebalance, and no forced liquidation. The last target does not earn a
subsequent return in the supplied scorer. Drift uses gross portfolio return in
the denominator; fees are separately subtracted as the scorer specifies.
Sharpe uses population standard deviation, ddof=0. Stage masks omit two
boundary rows that remain in the full score.

F3 and M1 each first encountered a NumPy-scalar JSON serialization failure in
their synthetic harnesses. Those records remain; the repairs changed only
serialization, with unchanged policy, fixtures and thresholds. The initial
root readback source review required input/array identity assertions before
execution; that correction and acceptance are preserved. Earlier wave mixed-
layout numerical failures remain recorded and are not retroactively declared
passed. Passing the declared temporal scenarios is evidence about those paths,
not a universal proof that every possible implementation issue is absent.

## 5. Effect size and uncertainty

The fixed paired moving-block procedure uses 2,000 draws, seed 20261027 and
block lengths 21, 63 and 126, including the final legal block start. Reported
bounds are 95% percentile intervals.

| Comparison | Observed Sharpe difference | 21-day interval | 63-day interval | 126-day interval |
|---|---:|---:|---:|---:|
| Joint minus prior F2 + VTvol | +0.126398 | [0.046424, 0.202522] | [0.045126, 0.194149] | [0.041123, 0.191659] |
| Joint minus M1 | +0.018172 | [0.007456, 0.029299] | [0.007364, 0.029751] | [0.008205, 0.030607] |

These intervals describe resampling variability for fixed policies on exposed
history. They do not adjust for all prior variants, family selection, the
conditional joint, or research guided by earlier results. They are not
out-of-sample confirmation and do not establish a future score. The decision
uses the predeclared score-first rule; it adds no retrospective significance
veto and makes no claim of zero overfitting.

## 6. Operational evidence and integration boundary

On the original 3,780-row history, joint forecast time is 2.897 seconds; mean
rebalance time is 7.811 ms, p99 11.446 ms and maximum 138.104 ms on one CPU.
The brief's rebalance requirement concerns the mean, not every individual call.
The largest observed absolute stock weight is 0.016484 and gross exposure is
3.043265; no outer cap binds. The worst daily gross return is -1.7854%, and
the tested paths remain solvent.

The separately authorized **25,200-row by 1,000-stock** workflow completed
successfully on CPU 1 with all three numerical-library thread settings at one.
It produced 25,200 forecast rows, 24,947 decisions and 24,946 economic rows.
Forecasting took **20.036 seconds**; mean rebalance time was **7.990 ms**,
p99 **13.270 ms**, maximum **150.264 ms**. Peak recorded RSS was 3,835,208 KiB,
about 3.66 GiB. All 3 summary checks and 31 workflow assertions pass, including
both allocator books' certificates, clocks, bounds and unchanged sources.

The runtime observer trims completed diagnostic copies only after recording
hashes; synthetic full/trimmed equality was established before using this
mode. Original-scorer accounting reconstruction is exact on this runtime path.
Its `performance` object is empty: repeated original data test computation
and state stability, and provide no additional evidence of future alpha.
The complete [runtime result](../../evidence/v2_score2_joint_20261029/runtime_001/result.json)
has SHA256 `f4983861a78b53f8a41dcc5b9b49d0a9ddac715a097175861db83ccc5c652bb5`.

The research engine remains pinned at ce3. The observed current production
head is `c51d31fe63c68255f2220935a8bc615c62bd1d0c`. Preserve its resumed solve,
cold restart, certified fallback-or-raise and final-book safeguards. Implement
the exact selected policy as an explicit mode, then reproduce its economics,
causal tests and runtime on that integrated package. Do not replace production
with historical research engine copies or inherit this score without execution.

Exact integration directions are in
[SCORE2_IMPLEMENTATION_HANDOFF_20261029.md](SCORE2_IMPLEMENTATION_HANDOFF_20261029.md).
The component reports and evidence retain all results, including rejected F3.
The complete publication/restoration method is in
[EVIDENCE_RESTORATION.md](../../evidence/v2_score2_root_20261029/EVIDENCE_RESTORATION.md).
GPT agents performed these research implementations and independent reviews;
Claude remains the production implementer. No applicant contribution, outgoing
message or completed submission is invented.
