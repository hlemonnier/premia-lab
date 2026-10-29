# Score-first challenge: the market direction deserves one clean test

29 October 2026. Independent reviewer: score2_challenge. Status: master
specification frozen; independent source review, prospective synthetic workflow
and released actual M0/M1 replay completed. **M1 net Sharpe is 1.4265608982 versus
1.3183349661 for M0.** Root's independent actual-evidence readback is complete
and agrees. The subsequently selected E2+M1 composition scores 1.4447333006 and
passes its own 25,200-row operational gate; Claude's production integration
remains separate. The original recommendation and scoped marginal diagnostic
below are retained as the prospective rationale.

## Recommendation

Admit exactly one additional-market candidate, **M1: +0.05 equal-weight market
exposure around the unchanged F2 + VTvol strategy**, as a separate experiment in
the new wave. The sleeve uses the supplied stocks, pays actual costs after
netting, and has no beta-estimation or market-premium learner. Keep the old
beta-correction experiments rejected under their original decision rules.

The justification is a positive marginal diversification contribution in the
existing return stream, not the fact that a beta allowance is unused. The local
spanning diagnostic is positive in every exposed historical segment. This makes
the low-complexity, separately costed test worth running; it does not establish
that a future market premium exists or that M1 has a higher executed net score.

The original brief's numeric condition remains binding. A candidate with higher
Sharpe and absolute whole-period net beta at or above 0.2 is not admitted.

### Released actual replay

The sole +0.05 candidate improves all exposed historical segments: full Sharpe
1.42656, discovery 1.17867, validation 1.81026 and audit 1.66450. Its full net beta
is 0.102711; all 29 actual-replay checks pass, including exact future/prefix
invariance and exact preservation of M0's forecast and inner target history.
No alternate sleeve size was run. Complete results and source/data identities
are in [M1 RESULTS.md](../../evidence/v2_score2_review_20261029/m1/RESULTS.md).

The actual target difference is 0.05/N on every decision because no outer cap
bound. The actual gross-return increment equals 0.05 times the equal-weight
market return on every earning day, to 6.18e-18. The net increment subtracts the
actual combined-book fee difference. This contributes 0.7233623 annualized
arithmetic percentage points of net return, including 0.063389 annualized basis
points of incremental trading cost. This is the intended fixed market premium;
the stock-selection policy is unchanged.

## 1. What the assignment actually permits

The original README specifies future net Sharpe, a whole-period regression beta
to the equal-weight market below 0.2, and solvency/runtime conditions. It permits
full-history parameter development. It has no standalone turnover, gross, net,
or single-stock cap. The gross-5 bound below is our inherited sizing choice.

There are 1,000 tradable stocks. Their equal-weight market is exactly replicable
by holding one-thousandth of a unit of notional in each. There is **no separate
costless index instrument**. Replication must pass through the actual stocks and
their supplied trading costs. The first trade is free, later close rebalances
are charged, and the last charged target is not earned by the supplied scorer.

The current research leader's realized net beta is 0.052720. Adding +0.05 to a
stock-replicated market sleeve would add 0.05 to gross-return beta when the
aggregate cap does not bind. Net beta need not shift by exactly 0.05: the change
in transaction costs also has a regression slope, and gross-cap binding would
change the identity. The replay must measure the actual resulting beta.

Sources: original supplied README and score.py; completed
[score report](SCORE_RESEARCH_RESULTS_20261028.md). The reviewed source baseline
for this proposed experiment remains ce3fe4e, with current production safeguards
to be preserved during later integration on Claude's branch.

## 2. The scoped marginal diagnostic

The [diagnostic plan](../../evidence/v2_score2_review_20261029/PLAN.md) was written
before these calculations. Its scope allows only moments of the already saved
joint return stream, the marginal derivative at zero added exposure and static
stock-cost summaries. It forbids a market-weight grid, an optimized hindsight
weight, a candidate score computed from saved net returns, or policy execution.
The +0.05 candidate value was stated in that plan before the diagnostic output.

Let p be the existing joint strategy's net return and m the market return.
Ignoring the incremental costs of an additional sleeve for this derivative,

    S(b) = sqrt(252) (mu_p + b mu_m)
           / sqrt(var_p + 2 b cov_pm + b^2 var_m).

The derivative at b=0 is positive exactly when

    mu_m > mu_p cov_pm / var_p.

This threshold accounts for overlap with the existing book. A positive market
mean alone is insufficient; a strongly correlated sleeve can lower Sharpe.

| Exposed historical segment | Market annualized mean | Marginal mean threshold | Sharpe derivative at zero, per unit b |
|---|---:|---:|---:|
| Full | 14.4799% | 3.1752% | +2.5756 |
| Original discovery | 10.0012% | 1.7319% | +1.7063 |
| Original validation | 23.7576% | 6.3402% | +4.4949 |
| Original audit | 12.4956% | 4.7092% | +2.0032 |

The full-history market volatility is 14.1604%; its correlation with the existing
joint net return is 0.17008. The existing Sharpe reproduces as 1.31833496609 and
net beta as 0.05272035468 using the same 3,526 earning observations.

These are exposed-development descriptive statistics. They omit incremental
fees and say nothing definitive about the market after the sample. The derivative
is local, so it is not a score estimate for the finite +0.05 candidate.

The equal-weight basket's average one-way cost is 0.00050420932, or 5.0421 bps
per unit of notional. A hypothetical paid insertion of a +0.05 basket costs
0.2521 bps of capital before netting against other stock trades. The actual first
trade is free. This is not an annual fee estimate; future drift and the combined
stock trades determine the real cost.

Exact inputs, hashes, command and numbers:
[marginal_market_diagnostic.json](../../evidence/v2_score2_review_20261029/marginal_market_diagnostic.json).

## 3. Exact M1 policy proposed for root's master plan

The control is M0 with b=0, and the sole alternative is M1 with b=0.05. Both
contain an unchanged inner F2 + VTvol instance. This inner instance already has
its own unscaled F2 virtual portfolio and EW63/EW1008 risk controller. M1 adds
one more portfolio accounting layer; it does not feed the market sleeve back
into the forecast, risk moments, base optimizer or volatility controller.

At forecast entry, reset the outer session, its previous actual target and its
previous inner target to zero; delegate forecasting to the unchanged inner
policy. At close t:

1. Earn the prior inner target's own gross return g_inner against R[t]. Drift
   that target with denominator 1+g_inner to obtain its own held positions.
2. Call the inner policy with those inner held positions, tomorrow's forecast
   and information through close t. Receive the new inner target u_t.
3. Form z_t = u_t + (b/N) 1. The basket is equal-weight in stock notional and is
   added **after** the inner volatility multiplier. It is not multiplied by a_t.
4. Return w_t = z_t min(1,5/sum(abs(z_t))). Preserve u_t, not w_t, as the inner
   previous target. The actual scorer owns the outer book's drift and fees.

The outer held positions must never be passed into the inner policy. Their
denominators differ whenever the market sleeve earns a return. Conversely,
virtual fees are never substituted for the fees of moving actual held positions
to w_t. The exact combined cost is c'abs(w_t-held_actual), with stock-level
netting. Summing standalone costs or scaling a saved net return stream is not
an implementation of this candidate.

The inner policy retains its own gross-5 bound. An outer cap binds only after
the sleeve is added and acts proportionally on the whole actual target. The
inner actual-weight bound inherited from VTvol is 0.10; the proposed pre-cap M1
bound is consequently 0.10+0.05/N. The assignment permits this. Do not clip to
0.10 and call that an equivalent strategy.

M1 has no additional warm-up. It holds its constant sleeve from the free opening
trade. The existing inner warm-up is untouched. Monotone one-day call and
session-reset contracts remain explicit. Nonfinite state or a ruined inner
book is an error, not permission to fabricate a continuing history.

## 4. Required prospective E2E expectations

Write the complete-workflow harness before the sleeve implementation, inspect
the expected missing-implementation failure, then have another reviewer inspect
the completed source before any actual-market replay.

- b=0 recovers the original joint forecast, targets and economics. Its inner
  target equals its actual target, including starts/restarts and the endpoint.
- With nonzero b and no outer cap, each new actual target minus the inner target
  is b/N exactly to declared floating-point tolerance; the inner target history
  equals the unchanged joint policy's target history.
- Each earned gross return equals the prior inner target's return plus b times
  the equal-weight market return whenever the preceding outer cap was inactive.
- Independently reconstruct actual drift and netted stock fees from returned
  targets, including sign reversals, the free opening and charged final rebalance.
  Include a deterministic fixture where sleeve trades offset an inner trade.
- A synthetic forced-cap case verifies proportional whole-target scaling and
  proves that cap scaling never contaminates the independent inner state.
- Future alteration, truncation and repeated sessions leave protected forecasts
  and targets unchanged. Include a same-layout actual-history future check.
- Known zero-return and fixed-return fixtures check the two different drift
  denominators. Invalid sequencing/nonfinite or ruined states have defined errors.
- Full actual replay records original-scorer metrics, stage diagnostics, beta,
  costs, gross/weight bounds, solver certificates, runtime and exact source/input
  identities. All old/current outcomes and negative evidence are retained.

Use the master's score rule: improvement over 1.318334966090838 by more than
1e-8, with numerical/accounting, causal, beta, solvency and runtime eligibility.
Paired time-block uncertainty describes confidence; do not add an unrecorded
significance or mean-square-error gate. No rescue by a different b after results.

## 5. Challenge to the proposed conditional combination

Root's new wave reserves two alternative execution mechanisms E1/E2, one
forecast mechanism F3 and M1. A single conditional combination is reasonable
if specified before the standalone outcomes, with these details frozen:

- E1 and E2 are alternatives within one execution family. Select at most the
  highest-scoring admitted one; never stack them opportunistically.
- F3 and M1 enter the joint candidate only if each separately beats the existing
  research leader and passes operational checks. Require at least two admitted
  families before running the single joint. Define numerical ties in advance.
- Composition order is forecast -> chosen execution/controller -> outer M1.
  Every layer observes its own portfolio history. In particular, an execution
  method that prices actual trades is actual **inside its inner book** when M1
  wraps it. It does not automatically minimize the final combined book's netted
  costs. Only the full original-scorer replay resolves the combination's value.
- Run exactly that joint, with unchanged standalone settings. If it loses,
  retain the best admitted standalone. Do not subsequently search all subsets,
  change weights, or drop one mechanism to improve the joint's score.
- Call the joint a counted adaptive development experiment. Standalone selection
  and recombination on these same exposed observations are not new confirmation.

It is also possible that M1's market return covaries unfavorably with F3 or the
new execution policy. Standalone improvement does not imply additive joint
improvement, so the combination must beat the best standalone before promotion.

## 6. Research papers and what they actually justify

[Tu and Zhou (2011), Markowitz meets Talmud](https://doi.org/10.1016/j.jfineco.2010.08.013)
studies combining an equal-weight rule with estimated sophisticated portfolio
rules under parameter uncertainty. It supports examining the omitted simple
portfolio direction; it neither calibrates our +0.05 sleeve nor establishes its
future premium in this simulated market. The publisher abstract/introduction
was inspected. The local marginal condition above is direct algebra.

[DeMiguel, Martin-Utrera and Uppal (2024), A Multifactor Perspective on
Volatility-Managed Portfolios](https://doi.org/10.1111/jofi.13395) studies conditional
factor weights, explicit transaction-cost optimization and trading diversification
from netting stock trades. It supports testing allocation jointly with real
costs. This strengthens the requirement to replay combined stock targets rather
than combine independently costed factor-return series. Its US-market empirical
result is not imported as a forecast for the simulator.

Full conditional allocation across 26 characteristic factors would add exposure
definitions, mean/covariance estimates, conditioning variables and shrinkage
choices. It is a valid later research family, but the present M1 spans one exact
tradable direction with one fixed small weight and no new statistical estimator.
The prior diagonal/full-risk blending diagnostics already showed limited
incremental promise; a different paper does not reverse that local observation.

## Attribution and outstanding work

GPT's independent research agent inspected the brief, source and prior evidence,
wrote the diagnostic scope, computed the scoped moments and proposed M1. Root
subsequently froze the master plan and authorized the prospective E2E and M1
implementation sequence. The read-only diagnostic plan and original numeric
proposal remain unchanged.

The M1 harness was written and its missing-policy failure recorded before
`sleeve.py` existed. The first complete synthetic workflow reached an output
serialization failure; it is retained. A NumPy-scalar JSON conversion repaired
only serialization, with unchanged policy, fixtures, assertions and tolerances.
The second workflow passes all 97 checks, including exact M0/reference identity,
inner-book independence, actual stock-level trade netting, forced gross-cap
behavior, future/prefix/restart equality and the original endpoint convention.
This is engineering evidence, not an estimate of M1's market performance.

The implementation and full records are in
[m1/](../../evidence/v2_score2_review_20261029/m1/). Root independently reviewed
this source and its synthetic evidence before releasing its actual-market
replay. M1's author independently
reviewed the other agents' F3 and E1/E2 sources; those scope-specific decisions
are recorded in
[forecast_source_review.json](../../evidence/v2_score2_review_20261029/forecast_source_review.json)
and
[execution_source_review.json](../../evidence/v2_score2_review_20261029/execution_source_review.json).
The later
[execution_synthetic_review.json](../../evidence/v2_score2_review_20261029/execution_synthetic_review.json)
independently verifies 68 saved arrays across 17 execution workflows and
reconstructs their accounting with maximum discrepancy 6.94e-18. All 220
prospective execution checks passed. The mathematical review also retains the
inherited E2 limitation: the gross cap is proportional scaling after the
optimizer solve, so its certificate does not establish a globally optimal
solution with an explicit gross constraint.
The actual run used one CPU and one numerical-library thread; the unchanged
source bindings and original CSV hashes were verified before launch. M0
reproduces the prior full score exactly. Root independently read back the
actual evidence and completed the one predeclared conditional composition.
No production change, external message or submission has been made.
Implementation and review responsibilities remain explicit and separate.

The final integrated research result and Claude handoff were independently
reviewed for economic claims, policy fidelity, tested causal scope and exposed
history selection. One integration clarification was resolved before finalizing:
object-wise forecast, target, scorer-column and full-Sharpe reproduction
tolerances are now explicit before any production edits. The final acceptance
and document hashes are in
[FINAL_RESULTS_HANDOFF_REVIEW.json](../../evidence/v2_score2_review_20261029/FINAL_RESULTS_HANDOFF_REVIEW.json).
All owned policy and harness sources remain unchanged from their released hashes.
