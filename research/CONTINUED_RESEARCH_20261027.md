# Continued alpha research, protected evaluation and selected strategy

27 October 2026, Europe/Paris. This report continues the earlier [eleven-candidate checkpoint](DISCOVERY_CHECKPOINT.md). Exact specifications, failed attempts and numerical evidence remain in the private repository. There is no fixed execution timetable; each protected stage follows its recorded evidence gate.

## Decision and strength of evidence

The frozen validation rule selects **C09, the longer-memory additive characteristic model with a diagonal risk allocator**. Its pooled validation net Sharpe is **0.659210**, compared with **0.398603** for C06, the more elaborate covariance-weighted learner and factor portfolio that led discovery. Both satisfy the tested beta, arithmetic, position and runtime conditions. The selected configuration is unchanged from discovery.

This is an observed ranking of complete policies, with substantial statistical uncertainty. The fixed bootstrap ranges include zero for both policies and for their paired Sharpe difference. The result does not establish that nonlinear terms, longer memory, or a particular risk-model component caused the improvement. In particular, the protected finalists are both additive policies; their comparison is not a fresh linear-versus-nonlinear ablation.

The final internal audit and packaging disposition are recorded in the audit section below when their separately authorized workflows finish. Neither validation nor internal audit can establish performance on the employer's unseen continuation.

## What the controlled discovery experiments found

All twelve admitted selectable discovery configurations were executed on the same 1,762 daily observations, zero-based return indices `[253,2015)`, using the original full-cost scorer. There was no extra configuration after the twelfth slot. These are development results influenced by the research process; the complete table is essential context for interpreting the best number.

| Candidate | Main fixed change | Net Sharpe | Annual full fees | Net market beta |
|---|---|---:|---:|---:|
| C01 | Joint linear characteristic benchmark, half-life 252 | 0.622345 | 0.652% | 0.017223 |
| C02 | Add all thirteen centered squares | 0.637567 | 0.777% | 0.021230 |
| C03 | C02 with half-life 63 | 0.106491 | 1.727% | 0.028195 |
| C04 | C02 with rank-10 factor portfolio risk | 0.654213 | 0.822% | 0.007565 |
| C05 | Covariance-weighted learning, diagonal portfolio | 0.602469 | 0.588% | 0.016346 |
| C06 | Covariance-weighted learning plus factor portfolio | 0.762944 | 0.681% | 0.006330 |
| C07 | Exact joint gross-constrained portfolio | 0.679825 | 0.498% | 0.023539 |
| C08 | Higher risk aversion, 5,000 | 0.626206 | 0.124% | 0.006259 |
| C09 | C02 with learning half-life 1,008 | 0.700155 | 0.588% | 0.014404 |
| C10 | C06 with rank 50 | 0.739890 | 0.514% | −0.000089 |
| C11 | All 78 pair interactions, stronger shrinkage | 0.603346 | 0.820% | 0.022222 |
| C12 | Fixed local additive hinges on all characteristics | 0.625698 | 0.833% | 0.021764 |

Sources are each candidate's `evidence/discovery_Cxx_001/summary.json`, original daily ledger and frozen source/configuration manifests. Every complete discovery run passed its twenty workflow checks. That establishes executed accounting/path scope, not predictive success or independent causality verification by itself.

The modest C02 improvement over C01 does not establish nonlinear superiority. Faster forgetting was markedly worse and incurred much higher fees. Covariance weighting helped in combination with the factor portfolio in discovery, but not by itself. Higher covariance rank, all interactions and the later local-shape extension did not improve their stated comparisons. Lower fees or a more exact optimizer alone did not guarantee a higher score.

The early diagnostic observations also need careful language. Persistent characteristics need not imply persistent expected returns. A marginal linear relationship can reverse because other characteristics' covariance changes; it need not identify a changing structural coefficient. Local response patterns motivated bounded tests, without identifying the hidden simulator's formula.

### Literature-inspired C12: a preserved negative result

The twelfth specification was written and published before implementation and market execution. It retained C02's original 26 columns and added three fixed local hinge terms at −1, 0 and +1 for each of the thirteen characteristics: 39 new columns, 65 total. A fixed normal-reference residualization/scaling convention separated the new columns from the existing linear/quadratic terms. Original ridge remained 0.1 and new-term ridge was fixed at 0.3; memory and the entire portfolio policy were unchanged. All characteristics received all terms, with no outcome-driven feature, knot or penalty selection.

The independent synthetic verifier and expected missing-module stage preceded implementation. Five complete synthetic workflows passed 55 checks, twelve protected numerical comparisons were exact, and the known-truth forecast correlation was 0.988107. The deliberately strong synthetic signal tested capability and information timing; it supplied no actual-market alpha evidence. A cash control preserved zero forecasts, positions, returns and fees, with undefined ratios retained as null.

The single C12 market run produced net Sharpe **0.625698**, below C02's **0.637567**. Gross Sharpe was also slightly lower, **0.747485 versus 0.750111**, while annual fees rose from **0.777254% to 0.833189%**. C12 failed the predeclared parent-improvement admission criterion. There was no local-basis retuning or thirteenth model, and C12 did not enter protected validation.

## What the literature contributed

The source reviews retain the exact versions, access limitations and relevant counterevidence in [the alpha review](LITERATURE_ALPHA_REVIEW_20261027.md) and [the portfolio review](LITERATURE_PORTFOLIO_REVIEW_20261027.md). The sources motivate hypotheses and methods; none demonstrates an edge in this anonymous simulated market.

| Source | Relevant idea | Consequence for this project |
|---|---|---|
| Freyberger, Neuhierl and Weber, [Dissecting Characteristics Nonparametrically](https://bfi.uchicago.edu/wp-content/uploads/we6b7o-WP_2018-50.pdf), institutional working-paper version | Flexible additive characteristic responses can represent shapes missed by a linear specification. | Motivated the bounded local-additive C12 test. Our fixed hinge/ridge design is an adaptation, not a replication of their estimator. Direct SSRN access was limited; institutional primary text was used. |
| Gu, Kelly and Xiu, [Empirical Asset Pricing via Machine Learning](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), author version | Their additive spline/group-regularized model did not simply outperform their linear model; interaction-rich methods had different results. | Recorded contrary evidence before treating additive flexibility as a likely improvement. Their data and forecasting task do not establish performance here. |
| de Lataillade et al., [Optimal Trading with Linear Costs](https://arxiv.org/abs/1203.5957) | Linear transaction costs can produce a no-trade region, so every forecast change need not trigger a trade. | Supports cost-aware trading around actual holdings. Its single-asset assumptions do not supply a direct solution to this 1,000-stock constrained portfolio. |
| Alpha Architect, [Can Smart Rebalancing Improve Factor Portfolios?](https://alphaarchitect.com/can-smart-rebalancing-improve-factor-portfolios/), and the linked [CFA Institute publication page](https://rpc.cfainstitute.org/research/financial-analysts-journal/2024/smart-rebalancing) | Rebalancing can prioritize stronger signals and account for the economic cost of trading. | Useful context for the existing cost-aware allocator. The public primary abstract was available; inaccessible full text was not treated as reviewed. No new grid of turnover buffers was admitted. |
| Gârleanu and Pedersen, [Dynamic Trading with Predictable Returns and Transaction Costs](https://nbgarleanu.github.io/DynTrad.pdf) | Signal persistence and trading costs interact in a dynamic trading problem. | Kept characteristic persistence, forecast persistence and payoff persistence conceptually separate. Quadratic-cost formulas were not transplanted into the scorer's absolute-cost problem. |
| Bailey and López de Prado, [The Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) | Selection and nonnormal returns can inflate a reported best Sharpe. | Preserved the research exposure trail and separate chronological evaluation. Twelve selectable pipelines were not assumed to be twelve independent total research trials; no unsupported numerical “no-overfit” certificate was calculated. |

## Implementation lookahead and research overfitting are different risks

The chosen learner computes row `t` from information published before day `t`. Its current characteristics come from `X[t−1]`; the newest matured training pair is `X[t−2]` against `R[t−1]`. The beta used to residualize that label is estimated before the label return. Transformations use the already published cross-section, and learned forecast state stays local to the forecast call. Rebalance receives only prior history and current drifted holdings. Independent source reviews inspected these paths and dependencies.

For C06, the canonical causal verification executed 39 fresh processes covering suffix changes, repeats, truncation and append scenarios. Independent reconciliation passed 1,209 checks; all 120 nonempty protected numerical comparisons were exactly equal. For C09, nineteen fresh processes completed; independent saved-output review found all 57 nonempty protected comparisons exact. Empty early trading ranges were explicitly not counted as economic coverage. Original discovery baselines and economic ledgers also reconciled exactly.

These tests found no lookahead on the exercised paths. They cannot prove correct behavior for every possible history. They also cannot remove research overfitting: a causally implemented policy can still be selected because it happened to perform well in an exposed sample. The predeclared budget, complete negative-result record, frozen two-policy nomination, untouched validation at nomination and single-policy audit address that separate problem. They reduce opportunities for selection optimism without eliminating it.

### A real verification failure and its resolution

The initial C06 verification copies converted canonical Fortran-contiguous returns to C order. Their own protected comparisons were exact, but their historical byte-identity gate failed. The first long-history attempt also stopped at the forecast-prefix hash before any rebalance. These failures remain preserved and are not counted as passes.

An unchanged standard discovery rerun reproduced the original forecast, target and held-book hashes and exact Sharpe. Saved C/F-layout differences were tiny and within the already fixed arithmetic tolerances. The issue was isolated to verification input layout; memory order can affect floating-point reduction arithmetic, as documented for [NumPy summation](https://numpy.org/doc/2.3/reference/generated/numpy.sum.html). A prospective fixture correction preserved canonical layout and reran the original gates against the original references. It changed no model, parameter, scorer, perturbation, score mask or tolerance. Canonical reruns reproduced the historical bytes exactly.

## Protected validation: complete results and selection

The nomination was committed as `c79f7b1165f976a003a0d26f177f9eda4fef4561` before numeric validation access. The fixed uncertainty reporter and its completed zero workflow were committed as `6b9ea857b2329f31451cabe0a482c36d45441fd1` before release. The controller was separately source-reviewed and verified on discovery parity and a complete synthetic-zero path. A lead-agent saved-output readback passed 125 checks; the uncertainty zero workflow passed 151 checks and independent artifact review.

Both exact policies replayed continuously from the original empty book at start 252 on input `[0,3024)`. No learner or holdings reset occurred at a validation boundary, and no extra free trade was introduced. The original scorer's last-row convention yields validation A `[2016,2520)` with 504 observations, B `[2520,3023)` with 503, and pooled `[2016,3023)` with 1,007. Pooled metrics use the daily pooled series, not an average of block Sharpes.

| Metric | C06 | Selected C09 |
|---|---:|---:|
| Validation A net Sharpe | 0.517307 | 0.366159 |
| Validation B net Sharpe | 0.312408 | 0.935789 |
| Pooled net Sharpe | 0.398603 | **0.659210** |
| Pooled gross Sharpe | 0.571599 | 0.710686 |
| Annual arithmetic net return | 1.482585% | 2.675944% |
| Annual net volatility | 3.719451% | 4.059321% |
| Annual full fees | 0.643988% | 0.208760% |
| Realized net market beta | 0.004670 | 0.005858 |
| Maximum drawdown | 5.934971% | 6.359150% |
| Full-replay mean candidate rebalance | 8.454 ms | 2.130 ms |

Both passed the unchanged eligibility rules. C09's pooled advantage was 0.260607 Sharpe, outside the 0.000001 tie tolerance, so the simplicity/runtime tie-breakers were not used. No minimum Sharpe or requirement that each short block be profitable was added. The selected identity/configuration and evidence are frozen in [VALIDATION_SELECTION.json](VALIDATION_SELECTION.json). The reversal from the discovery ranking is retained, rather than selecting the development leader by discretion.

### Fixed uncertainty and cost sensitivity

The planned ordinary moving-block bootstrap uses nonwrapping contiguous blocks of 21 and 63 observations, 1,000 replicates each, fixed seeds `20261027 + block_length`, and identical sampled validation indices for both candidates. All reported validation replicate ratios were finite. The following are empirical 95% percentile ranges conditional on the observed sample and research path; they do not correct all prior selection optimism or quantify the probability that one policy is truly best.

| Quantity | 21-observation blocks | 63-observation blocks |
|---|---:|---:|
| C06 net Sharpe | [−0.847, 1.484] | [−0.308, 1.563] |
| C09 net Sharpe | [−0.202, 1.700] | [−0.021, 1.673] |
| Paired C06 minus C09 Sharpe | [−1.231, 0.695] | [−0.939, 0.552] |

The ranges include zero. Positive point estimates and a deterministic selection do not establish a stable underlying alpha or statistically reliable relative superiority. The two fixed block lengths also show sensitivity to the dependence assumption; they do not identify a uniquely correct resampling model.

| Saved fee multiplier, fixed decisions | C06 net Sharpe | C09 net Sharpe |
|---|---:|---:|
| 1.0 | 0.398603 | 0.659210 |
| 1.5 | 0.312063 | 0.633473 |
| 2.0 | 0.225502 | 0.607738 |

These stresses subtract multiples of the recorded fee series while preserving gross returns and decisions. They are cost-estimation sensitivities, not new optimizer runs or selectable candidates. They do not model additional market impact or a changed market. The original 1.0 case alone determined selection. Complete matrices, replicates, ledger identities and results are retained in `evidence/validation_uncertainty_001`, with the independent interpretation in `reviews/VALIDATION_UNCERTAINTY_REVIEW.md`.

## Long-history engineering and final package

Both retained models completed actual 25,200-row original-scorer workflows on deterministic repetitions of discovery inputs, with 24,947 targets and 24,946 scored economic rows. C06's forecast took 72.64 seconds and mean rebalance 8.19 ms; C09 took 43.19 seconds and 2.19 ms. All original discovery forecast/target/held/economic prefixes were exact, with full fees checked throughout execution. A separate 61-check saved-artifact review covered input construction, identities, timing and historical reconciliation. These host-specific runtime measurements are comfortably inside the stated budgets, without guaranteeing another machine's timing. Repeated discovery observations supply no independent alpha evidence.

The selected handoff is intentionally small: a top-level `strategy.py`, an empty package initializer, and byte-identical original `model/strategy.py` and `model/portfolio.py` helpers. The wrapper uses a literal original C09 configuration and direct function aliases. It adds no learner or optimizer. Its complete note, including honest contribution attribution, is written before audit. A clean-directory workflow with a fresh isolated interpreter must reproduce the original discovery arrays and economics exactly before the package is frozen for audit. The unchanged package then reproduces the sole selected canonical audit as an engineering rerun, not another candidate selection.

## Locked audit and final disposition

At this report's pre-audit checkpoint, the audit remains closed. The separately frozen selected-policy audit and unchanged clean-package replay must be completed before reporting an audit score or claiming final packaging equivalence. This section will be updated with their actual evidence; pending work is not a pass.

## Contribution and interpretation boundary

The user reports noticing the same broad early patterns, emphasized protection from lookahead and overfitting, and requested continued literature-grounded experiments and subagents. AI performed the implemented research, code, executions, independent-agent review, evidence reconciliation and packaging. No unreported human coding, independent numerical replication or discovery of the simulator is attributed.

All market results concern the supplied simulated market and its specified fee convention. The task's unseen future remains unobserved. A small positive historical edge can be overwhelmed by response changes, adaptation lag, omitted common risks, beta-estimation error, costs or tail events. The strategy's market hedge uses estimated betas; low realized beta in the tested windows does not guarantee the same in future data. The repository preserves the evidence needed to assess those limits, including failures, unfavorable alternatives and the exact choices made before protected access.
