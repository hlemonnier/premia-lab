# Experiment and exposure ledger

The frozen protocol admits twelve complete scored discovery configurations, two primary alpha families, at most three finalists entering validation, six explanatory ablations, and one distinct locked-audit candidate. All actual portfolio evaluations use full original costs and continuous holdings under the original scorer.

## Recovered diagnostic exposures

| Exposure | Scope | Recorded result | Pipeline slots |
|---|---|---|---:|
| Alpha diagnostic 001 | Actual rows [0,2016), all 13 characteristics, fixed 1/5/20-day horizons and four blocks; full curves retained | Supports adaptive joint estimation and restrained additive curvature; no portfolio result | 0 |
| Risk diagnostic 001 | Actual rows [0,2016), market beta, residual spectrum, known costs | Heterogeneous beta and residual common covariance; no portfolio result | 0 |
| Accounting 001 | Synthetic two-stock CSV workflow through original scorer | 44 recorded passing checks | 0 |
| Portfolio verification 001/002 | Synthetic allocator workflow and independent convex references | 54 recorded passing checks in each; failed red runs retained | 0 |

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

The first-wave economic records are `evidence/discovery_C01_001` through `discovery_C04_001`. Each completed 20 workflow checks with exit 0, 1,762 scored observations, exact full-fee reconciliation, and all declared path feasibility flags true. Their source/config snapshots are immutable. None establishes validation or hidden-future quality.

The observed additive and factor incremental net gains are small. Faster adaptation worsened gross as well as net Sharpe. Postsolve gross scaling was habitual (73.3%,79.8%,96.7%,63.2% of calls), so it materially distorts each unconstrained turnover optimum. These observations motivate the following bounded contrasts; they do not prove the proposed explanations.

| Slot | ID | Fixed contrast | State before first execution |
|---:|---|---|---|
| 5 | C05 | Same as C02, but train normalized exponentially weighted ridge moments using causal covariance precision; rank 10, shrink 0.5, refresh 21, trailing 252, all before each label | Admitted, specification/test-first helper implementation pending |
| 6 | C06 | C05 forecasts with C04 factor portfolio; all shared knobs unchanged | Admitted, pending |
| 7 | C07 | C02 forecasts and diagonal risk, with exact joint beta/box/gross/turnover convex allocation instead of postsolve scaling | Admitted, specification and new numerical tests before new solver implementation |
| 8 | C08 | C02 with risk aversion 5000 instead of 1000, chosen once to make the existing gross cap exceptional; no other change | Admitted, simpler sizing control against unnecessary solver complexity |

C05/C06 ask whether common residual shocks correlated with the characteristic design contaminate forecasts. Precision is normalized to mean diagonal 1 so the existing ridge scale remains meaningful. Before 20 prior observations use diagonal risk; factors start at 20 then 41,62,... strictly before the training label, with local forecast state only. First active forecast remains 127. Exact specification is frozen separately before code and results.

C07 and C08 ask two distinct questions: whether a correctly constrained no-trade allocation helps at the existing scale, and whether a simpler lower-risk size avoids the need for that machinery. Implementation sophistication does not confer priority in selection.

An explanatory paired moving-block bootstrap of the first four saved daily ledgers is separately preregistered (block lengths 21 and 63, seed 20261026,1000 replicates). It consumes no new portfolio configuration and may not be used to redefine the validation selection rule.

## Results that motivated the final bounded discovery contrasts

C05 completed at net Sharpe 0.602469 versus C02's 0.637567: its precision-weighted learner alone did not improve the measured result. C06, using byte-identical C05 forecasts in the factor portfolio, completed at 0.762944. That interaction is a plausible direction for more investigation, not evidence of hidden-future quality. C08 completed at 0.626206 with zero gross-rescaling events, proving the simpler sizing change removes that approximation but does not materially improve the observed Sharpe. C07 is still unscored at this admission checkpoint.

The preregistered wave 1 bootstrap completed with 99 workflow checks. C02-minus-C01 and C04-minus-C02 paired Sharpe ranges include substantial positive and negative differences at both block lengths. C03-minus-C01 ranges are negative at both lengths. These ranges are conditional development-sample diagnostics, not probabilities of future superiority or equivalence tests.

| Slot | ID | Fixed contrast decided before its first result | State |
|---:|---|---|---|
| 9 | C09 | Same as C02, with alpha half-life 1008 instead of 252; one four-year memory choice, no half-life grid | Admitted before config/run |
| 10 | C10 | Same as C06, with learning and portfolio factor ranks 50 instead of 10; shrinkage 0.5, windows 252 and refresh 21 unchanged | Admitted before config/run |

C09 challenges the earlier inference that changing univariate signs necessarily warrant fast adaptation. The poor gross result from faster learning and absence of a GLS-only improvement make estimation variance a competing explanation. Longer memory may fail under actual changes; no improvement is presumed.

C10 makes one finite expansion of the covariance representation. The stored descriptive spectrum distinguishes rank 10 and rank 50 residual-correlation variance shares; it does not establish stable live factors. C06's improvement over C05 with identical forecasts gives this risk question priority over a cost grid. Increasing learner and portfolio rank together tests the complete C06 mechanism and cannot identify which side deserves credit. With 252 observations, the additional factors may add noise or runtime; the fixed 0.5 energy bound and full runtime/fallback evidence remain required. Early estimation caps rank by available prior observations.

Ten of twelve pipeline slots are now reserved. No further pipeline or diagnostic scan is implicitly authorized by a disappointing result.

## C11 admission: test the additive assumption, before implementation or results

C07 completed at 0.679825 net Sharpe with exactly C02's forecasts, lower fees and no proportional scaling. C09 completed at 0.700155, with a weaker last block than C02. C10 completed at 0.739890, below C06's 0.762944 despite larger covariance rank. These results do not justify another risk or memory grid.

The lead proposed, and an independent alpha reviewer supported, one different conditional-mean question. Marginal curvature need not be additive when predictors correlate: for an illustrative standardized jointly Gaussian pair, E[XZ|X]=rho*X^2. Gaussianity is not established here. The already-recorded curvature and correlations motivate a bounded separability test; they do not identify the simulator's mechanism.

| Slot | ID | Fixed complete contrast | Admission state |
|---:|---|---|---|
| 11 | C11 | C02's original 26 terms plus all 78 centered strict-upper-triangle products; ridge 0.1 on original terms and 1.0 on products; identical EW252 and complete diagonal portfolio | Admitted before new code, synthetic verification and market result |

Products use the existing bounded centered linear columns, fixed unit scale, and only their currently published cross-section. The original 26 columns remain byte-identical. All pairs are included in a fixed order; no selected pairs, interaction penalty grid or new optimizer is authorized. First active forecast remains 127. This is a 104-coefficient model with estimation risk, not 78 independent bets.

A predeclared synthetic whole-strategy workflow may verify the new forecaster on a known interaction-generating process and under future alteration. It is an engineering check, not a discovery market score or a generalization result. No new isolated tests may be written after covered implementation.

Slot 12 remains unassigned. A later actual-data follow-up requires another prospective entry; no obligation to exhaust the budget.

## Protected periods

Validation [2016,3024): **not opened**. Locked audit [3024,3780): **not opened**. No current result measures performance on the employer's unseen continuation.
