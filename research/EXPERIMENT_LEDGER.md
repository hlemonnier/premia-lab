# Experiment and exposure ledger

The frozen protocol admits twelve complete scored discovery configurations, two primary alpha families, at most three finalists entering validation, six explanatory ablations, and one distinct locked-audit candidate. All actual portfolio evaluations use full original costs and continuous holdings under the original scorer.

## Recovered diagnostic exposures

| Exposure | Scope | Recorded result | Pipeline slots |
|---|---|---|---:|
| Alpha diagnostic001 | Actual rows [0,2016), all 13 characteristics, fixed 1/5/20-day horizons and four blocks; full curves retained | Supports adaptive joint estimation and restrained additive curvature; no portfolio result | 0 |
| Risk diagnostic001 | Actual rows [0,2016), market beta, residual spectrum, known costs | Heterogeneous beta and residual common covariance; no portfolio result | 0 |
| Accounting001 | Synthetic two-stock CSV workflow through original scorer | 44 recorded passing checks | 0 |
| Portfolio verification001/002 | Synthetic allocator workflow and independent convex references | 54 recorded passing checks in each; failed red runs retained | 0 |

## First candidate pair: admitted before execution

Detailed constants and exact transformations are frozen in `ALPHA_MODEL_PLAN.md` and the JSON configurations before their first numerical runs. No claimed optimality for these starting choices.

| Slot | ID | Hypothesis / controlled contrast | Data | State |
|---:|---|---|---|---|
| 1 | C01 | Causal exponentially weighted joint ridge on all linear characteristics; trailing market hedge, diagonal risk and amortized trade-cost policy | Discovery only | Executed: net Sharpe 0.622345, beta +0.017223 |
| 2 | C02 | Same as C01 plus the same fixed quadratic basis for all 13 features; tests additive nonlinear incremental value | Discovery only | Executed: net Sharpe 0.637567, beta +0.021230 |
| 3 | C03 | Same as C02 with alpha half-life 63 instead of 252; tests faster response to the changing feature effects observed in the prior diagnostic blocks | Discovery only | Executed: net Sharpe 0.106491, beta +0.028195 |
| 4 | C04 | Same alpha and controls as C02, adding trailing rank-10 residual correlation risk with 50% offdiagonal shrinkage and 21-day refresh; preserves parent marginal variance | Discovery only | Executed: net Sharpe 0.654213, beta +0.007565 |

Engineering acceptance is distinct from profitability. Record pooled net Sharpe, fixed block results, beta, actual fees, runtime, controls and contrary evidence; no discovery Sharpe floor is imposed. A changed configuration based on results needs a new ledger entry before execution. Exact unchanged reruns are provenance checks, not new configurations.

### Admission rationale for C03 and C04

C03 is a single predetermined adaptation contrast, not a half-life grid. The quarter-year half-life is one quarter of the first benchmark's 252-day half-life. Existing diagnostics showed sign changes in fixed multi-year blocks and substantial shorter-period instability. All other settings remain identical to C02. A better discovery score is evidence to carry forward, not validation or a guarantee of a long-run improvement.

C04 was specified from the already-recorded residual covariance spectrum before any candidate portfolio result. Its exact estimator and solver are documented in `PORTFOLIO_NEXT_PLAN.md`. New numerical checks were written before its implementation; 73 fixed checks subsequently passed and another agent reviewed the source, including a numerical edge correction. This does not count as actual-market performance. Full costs, estimated-beta equality, box limits and gross-scaling rule remain as in C02.

All four economic runs use the frozen official scorer and independent fresh interpreters. Each is pinned to a distinct CPU with numerical-library threads set to one. Concurrent machine activity remains a runtime caveat; complete runtime gates may later require a quiet rerun of an unchanged candidate.

## Second-wave admission, after first-wave inspection and before new results

The first-wave economic records are `evidence/discovery_C01_001` through `discovery_C04_001`. Each completed 20 workflow checks with exit0, 1,762 scored observations, exact full-fee reconciliation, and all declared path feasibility flags true. Their source/config snapshots are immutable. None establishes validation or hidden-future quality.

The observed additive and factor incremental net gains are small. Faster adaptation worsened gross as well as net Sharpe. Postsolve gross scaling was habitual (73.3%,79.8%,96.7%,63.2% of calls), so it materially distorts each unconstrained turnover optimum. These observations motivate the following bounded contrasts; they do not prove the proposed explanations.

| Slot | ID | Fixed contrast | State before first execution |
|---:|---|---|---|
| 5 | C05 | Same as C02, but train normalized exponentially weighted ridge moments using causal covariance precision; rank10, shrink0.5, refresh21, trailing252, all before each label | Admitted, specification/test-first helper implementation pending |
| 6 | C06 | C05 forecasts with C04 factor portfolio; all shared knobs unchanged | Admitted, pending |
| 7 | C07 | C02 forecasts and diagonal risk, with exact joint beta/box/gross/turnover convex allocation instead of postsolve scaling | Admitted, specification and new numerical tests before new solver implementation |
| 8 | C08 | C02 with risk aversion5000 instead of1000, chosen once to make the existing gross cap exceptional; no other change | Admitted, simpler sizing control against unnecessary solver complexity |

C05/C06 ask whether common residual shocks correlated with the characteristic design contaminate forecasts. Precision is normalized to mean diagonal1 so the existing ridge scale remains meaningful. Before20 prior observations use diagonal risk; factors start at20 then41,62,... strictly before the training label, with local forecast state only. First active forecast remains127. Exact specification is frozen separately before code and results.

C07 and C08 ask two distinct questions: whether a correctly constrained no-trade allocation helps at the existing scale, and whether a simpler lower-risk size avoids the need for that machinery. Implementation sophistication does not confer priority in selection.

An explanatory paired moving-block bootstrap of the first four saved daily ledgers is separately preregistered (block lengths21 and63, seed20261026,1000 replicates). It consumes no new portfolio configuration and may not be used to redefine the validation selection rule.

## Protected periods

Validation [2016,3024): **not opened**. Locked audit [3024,3780): **not opened**. No current result measures performance on the employer's unseen continuation.
