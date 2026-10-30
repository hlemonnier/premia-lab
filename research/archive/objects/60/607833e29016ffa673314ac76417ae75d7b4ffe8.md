# E2 improves the score to 1.339582 by optimizing actual stock trades

29 October 2026, Europe/Paris. Two alternatives under the prospective
[wave-two master plan](SCORE2_RESEARCH_PLAN_20261029.md). This research retains
the ce3 engine and the first wave's F2 + VTvol reference, net Sharpe 1.3183349661.
Production integration must preserve the later c51 allocator safeguards.

## Question and motivation

The first wave's more aggressive inverse-variance controller had a better gross
score but a worse net score than inverse-volatility sizing. The leading joint
portfolio paid 0.336406% annual fees, versus 0.207145% for unscaled F2. Those
observations motivate two different ways of charging actual trade costs when
the desired portfolio size changes. No smoothing-window or penalty grid is run.

Both alternatives maintain the identical independent F2 virtual portfolio. It
has its own drift denominator, risk state and optimizer state. Its already
earned gross returns drive the fixed EW63/EW1008 second moments, 63-observation
startup and clipped square-root multiplier a_star. The scorer's actual held
positions never enter that reference portfolio.

## E1: a cost-aware scalar projection

Let v be the new virtual target, h the actual drifted holdings, c the stock
costs, and q63 the causal short second moment. After warm-up, minimize

    .5*200*max(q63,1e-12)*(a-a_star)^2 + c' abs(a*v-h)/20

over [.5,min(2,5/||v||1)]. The coefficients 200 and 20 are the inherited risk
aversion and cost horizon. Their use here is a chosen tracking objective, not
a calibrated utility forecast. The scalar prices the full actual stock trade,
including trade netting with changing stock selection. It is not a penalty on
abs(a-a_previous), and it does not debit virtual fees from actual returns.

The strictly convex objective is solved by sorting its absolute-value
breakpoints and locating the first derivative crossing. Left/right derivatives
and box KKT conditions certify the result. Negative stock weights, repeated
breakpoints, zero costs and zero targets are covered. The feasible desired
multiplier is a comparator: at the same h, the optimized objective cannot be
worse. This local property does not guarantee lower fees over a different
future portfolio path.

## E2: optimize the actual stock portfolio at the desired risk scale

A second independent engine sees the same F2 forecast and published risk
inputs, but optimizes around actual h. It uses gamma=200/a_star, stock cap
.05*a_star, cost horizon 20 and zero raw-estimated-beta target. The actual gross
limit remains 5. Its risk/optimizer state is separate; only the two allocation
coefficients change daily, without resetting accumulated risk history.

Substituting w=a*x into a zero-cost quadratic objective explains gamma/a and
the scaled stock cap. The corresponding costed identity additionally requires
actual h=a*virtual h, which generally fails when size changes. Optimizing the
actual stock trades rather than scaling a virtual optimizer's solution is E2's
economic change.

The inherited engine first solves the stock-cap/beta-constrained objective and
then proportionally reduces gross if necessary. E2 therefore does not claim
global optimality for a QP with an explicitly optimized gross constraint. Exact
zero-cost scaling is required only when the virtual gross cap is nonbinding;
otherwise a fixed actual gross 5 cap is not a homothetic constraint for a<1.

## Prospective engineering evidence

The [owned plan](../../evidence/v2_score2_execution_20261029/PLAN.md), complete
scorer harness and optional 25,200-row runtime path were written before the new
policy. The expected missing-policy failure is retained in
[pre_implementation_manifest.json](../../evidence/v2_score2_execution_20261029/pre_implementation_manifest.json).
Independent mathematical and state/timing/source reviews preceded execution.

The first synthetic workflow passed all 220 specified checks. Its 15 named
policy cases and two direct reference cases include future alteration, prefix
and restart equivalence, actual drift/full fees/opening/endpoint, zero returns,
zero costs, state separation, scalar KKT conditions and an extreme gross-cap
case. Canonical-layout future/prefix/restart comparisons are exact. Zero-cost
E1 matches exactly; E2's largest weight difference is 7.98e-16 and economic
difference 2.66e-15. No failed tolerance was relaxed. The independent synthetic
review also verified 136 artifact hashes, 68 atomic arrays and all 17 complete
accounting streams; its maximum reconstructed discrepancy was 6.94e-18.

The complete [synthetic result](../../evidence/v2_score2_execution_20261029/e2e_001/result.json)
has SHA256 `e6c3631ad15f4a72494082331e49daf9dc4ac0c11201444e6f805e56f5dfdee6`.
Policy source SHA256 `64dbb239848661fee97004e363d79a1568f02656e6b5e8ce5d76933faf338d1f`.

Actual arrays are designed to be saved atomically as individual NPY files,
reopened and checked against full hashes. Every policy emits target weights,
virtual weights, forecasts and original-scorer rows, plus CSV economics and
decisions. This preserves independent stock-level reconstruction and avoids
relying on the prior truncated NPZ checkpoints.

## Original-market outcomes: E2 wins this execution family

The master plan was committed as `d2997e0d98c6407da4b503a77060966904486062`
before these scores. Root released the unchanged source after the independent
reviews. The sole baseline/E1/E2 batch completed on CPU 2 with one-core BLAS,
exit code zero and empty stderr. No policy, parameter or tolerance changed.

| Policy | Net Sharpe | Change vs reference | Gross Sharpe | Annual net mean | Annual net vol | Annual fees | Net beta |
|---|---:|---:|---:|---:|---:|---:|---:|
| F2 + VTvol | 1.318335 | — | 1.397145 | 5.7865% | 4.3893% | 0.3364% | 0.05272 |
| E1: scalar projection | 1.329123 | +0.010788 | 1.391944 | 5.8274% | 4.3844% | 0.2659% | 0.05267 |
| **E2: actual-book optimization** | **1.339582** | **+0.021247** | **1.397175** | **5.8946%** | **4.4003%** | **0.2442%** | **0.05298** |

E2 is the selected execution alternative under the frozen rule. Both variants
improve the reference, so E1 remains a positive but lower-ranked result. E2's
qualification for a later composition is a root decision under the master
plan; no combination was tested in this execution packet.

E1 saves 7.05 basis points of annual fees while giving up 2.97 basis points of
annual gross mean return. Its annual net mean therefore improves by 4.09 basis
points. E2 saves 9.23 basis points of annual fees, a 27.4% reduction, while
annual gross mean improves by 1.58 basis points. Annual net mean rises by 10.81
basis points. E2's gross Sharpe is essentially unchanged, whereas net Sharpe
improves. This is consistent with the intended execution mechanism; the small
changes in actual holdings still change both returns and risk.

| Policy | Original discovery | Original validation | Original audit |
|---|---:|---:|---:|
| F2 + VTvol | 1.103512 | 1.633970 | 1.593029 |
| E1 | 1.124469 | 1.647160 | 1.570662 |
| E2 | 1.126129 | 1.671238 | 1.586043 |

The gain is in the first two exposed periods; the final period is slightly
lower. None is fresh confirmation data. The paired 63-day interval for E1
minus the reference is [-0.001427,+0.023559]. For E2 it is
[+0.010130,+0.033602]; the 21-day and 126-day intervals are also positive.
These are fixed-policy paired resampling descriptions, not corrections for
the complete research search and not guarantees of future superiority.

## Actual verification and operational scope

- The reference's net Sharpe reproduces exactly. Its maximum daily CSV
  comparison error is 4.44e-16, well inside the predeclared 1e-8 tolerance.
- Forecast and virtual-target hashes are identical across all three policies.
  F2 forecast hash: `10e86d588bbba22a3ed0f61673cc80a0d100df2b62d983711bc2365087747927`.
  Virtual-target hash: `5d8bb12d46e76b1b5dd95a7c33f764496417c5f3bec136d6a2ffbc7147fc8850`.
- The replay observer reconstructs actual accounting with zero floating-point
  difference on all three paths. Root's separate original-market readback is
  complete: every target and scorer array matched its frozen manifest, and an
  independent reconstruction from the original stock returns and costs differed
  by at most 5.21e-18 across these three paths. It reproduced the scores and paired
  intervals, including E2's 63-day interval [0.01013038494, 0.03360231472]. The
  evidence is `evidence/v2_score2_root_20261029/standalone_readback_001.json`, SHA256
  `af16207ccedc0cb380e332041f4d90260dd1af75db21d0fdb195c6db30c57926`.
- Every one of the 3,527 virtual solves is certified for each policy. E2's
  3,527 additional actual solves are all certified; maximum actual duality gap
  is 1.67e-17. E1's largest scalar KKT residual is 5.49e-19.
- E2's maximum actual gross is 3.03122 and maximum stock weight is 0.016534;
  no gross-5 post-scaling is needed on this actual path. Mean stock net is
  0.45528, and whole-sample realized net beta is 0.052981.
- Measured mean instrumented rebalance times are 3.83 ms for the reference,
  4.04 ms for E1 and 7.01 ms for E2. E2's p99 is 9.84 ms; its maximum is
  140.78 ms. The task's stated limit applies to the mean, not every call.
  Forecast takes about 2.58 seconds per actual run.
- The optional 25,200-row stress remains unexecuted in this packet. The short
  observed timings and extrapolation are not presented as that runtime gate.

The [machine-readable results](../../evidence/v2_score2_execution_20261029/actual_001/results.json)
have SHA256 `cbb3cb6e1ef0aced17fcce7a3963f13ebd69499c955a6936ced7849952f3abe6`.
[Execution record](../../evidence/v2_score2_execution_20261029/execution_record.json)
contains the exact command and release/source identities. Atomic arrays and
their full verification records are under each actual policy directory.

## Research sources

[Garleanu–Pedersen](https://www.nber.org/papers/w15205) motivates partial trading
toward a changing aim portfolio when costs matter; their quadratic-cost
solution is not a derivation of E1's proportional-cost projection.
[Boyd et al.](https://arxiv.org/abs/1705.00109) describes single/multiperiod
convex trading objectives that jointly price forecasts, risk and transactions;
E2 remains single-period.
[Lobo–Fazel–Boyd](https://stanford.edu/~boyd/papers/portfolio.html) supplies the
convex proportional-cost portfolio context. These sources motivate the
experiments and their tractability, not expected future performance in this
simulated market.
