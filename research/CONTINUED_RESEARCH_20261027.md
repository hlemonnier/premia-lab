# Continued alpha research, protected evaluation and selected strategy

27 October 2026, Europe/Paris. This report continues the earlier [eleven-candidate checkpoint](DISCOVERY_CHECKPOINT.md). Exact specifications, failed attempts and numerical evidence remain in the private repository. There is no fixed execution timetable; each protected stage follows its recorded evidence gate.

## Decision and strength of evidence

The frozen validation rule selects **C09, the longer-memory additive characteristic model with a diagonal risk allocator**. Its pooled validation net Sharpe is **0.659210**, compared with **0.398603** for C06, the more elaborate covariance-weighted learner and factor portfolio that led discovery. Both satisfy the tested beta, arithmetic, position and runtime conditions. The selected configuration is unchanged from discovery.

This is an observed ranking of complete policies, with substantial statistical uncertainty. The fixed bootstrap ranges include zero for both policies and for their paired Sharpe difference. The result does not establish that nonlinear terms, longer memory, or a particular risk-model component caused the improvement. In particular, the protected finalists are both additive policies; their comparison is not a fresh linear-versus-nonlinear ablation.

The separately reserved audit is now complete: the unchanged selected C09 earned **1.799231 net Sharpe after full costs**, with realized net-market beta **0.005666**, over 755 observations. Both prespecified audit bootstrap ranges remain above zero. The final package reproduced the complete canonical audit exactly. This supplies positive evidence for this fixed policy under the supplied simulated-market cost model. Neither validation nor internal audit establishes performance on the employer's unseen continuation.

![Protected performance and uncertainty](../artifacts/research_summary.png)

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

The selected handoff is intentionally small: a top-level `strategy.py`, an empty package initializer, and byte-identical original `model/strategy.py` and `model/portfolio.py` helpers. The wrapper uses a literal original C09 configuration and direct function aliases. It adds no learner or optimizer. Its complete note, including honest contribution attribution, was written before audit. The clean-directory discovery workflow passed 15 controller and 26 worker checks, reproducing the original arrays and all 1,762 economic/net rows exactly. A separate lead-agent artifact review passed 53 checks. That package was frozen before audit and remained unchanged afterward.

The final archive, [continual_research_C09.zip](../artifacts/continual_research_C09.zip), contains exactly those four files. Its 8,709 bytes have SHA256 `cba024cae44dd84b17b17dcde48e4276e677a52883220c54da455664a770b7fa`. Every archived member was compared to the frozen package manifest. Source data and research evidence are outside the small handoff. The [archive manifest](../artifacts/handoff_archive_manifest.json) records exact file identities.

## Locked audit and final disposition

Selection and the discovery-verified handoff were committed as `f57491f606b64f1c457dda53d3bd310bf9c14b7b`. The sole audit nomination, its explicit release and independent readback source were then committed as `5522f41eb6b6b72b69b9a5f01268031ecea3869a`, before audit access. Only C09 was evaluated. No candidate, setting, source, note, cost convention or score window changed after either protected result.

The canonical run executed once continuously on `[0,3780)`, with 3,527 targets and 3,526 complete economic rows. Its fixed audit mask was `[3024,3779)`: 755 observations, including full closing costs under the original endpoint rule. It passed all 102 controller checks.

| Fixed C09 audit metric | Result |
|---|---:|
| Net Sharpe | **1.799231** |
| Gross Sharpe | 1.861206 |
| Annual arithmetic net return | **9.676070%** |
| Annual net volatility | 5.377893% |
| Annual full fees | 0.333119% |
| Realized net market beta | **0.005666** |
| Maximum audit drawdown | 7.019703% |
| Mean gross exposure | 0.805479 |
| Full-replay mean candidate rebalance | 2.264577 ms |

The original beta and runtime conditions pass. These are audit-period outcomes, not a comparison with an unexecuted C06 audit. All dollar/percentage-return descriptions are fractions of the scorer's capital convention; annual return here is the arithmetic daily mean times 252, not an annual realized cash-flow claim.

The unchanged reporter passed 153 checks on the saved audit ledger. Both fixed bootstrap lengths used 1,000 finite replicates, with the prescribed generator reset for the audit sample.

| C09 audit empirical 95% range | 21-observation blocks | 63-observation blocks |
|---|---:|---:|
| Annual arithmetic net mean | [3.572%, 16.822%] | [3.395%, 17.086%] |
| Net Sharpe | [0.655, 3.172] | [0.630, 3.032] |

Both Sharpe and mean ranges stay above zero under these specified resampling assumptions. That strengthens the positive-after-cost interpretation relative to the selected validation result. The ranges are still broad; 755 observations, dependence assumptions and possible response changes limit what they establish about future decades. They are not a no-overfit certificate, and they do not erase the earlier model-selection process.

| Audit fee multiplier, fixed decisions | Net Sharpe | Annual arithmetic net return |
|---|---:|---:|
| 1.0 | 1.799231 | 9.676070% |
| 1.5 | 1.768240 | 9.509511% |
| 2.0 | 1.737247 | 9.342951% |

The fee stress leaves a positive point estimate at twice recorded costs. It remains an ex-post sensitivity of saved decisions, not a rerun with new allocation choices or a claim about real-market capacity. Complete results are in `evidence/audit_C09_001`, `evidence/audit_uncertainty_001` and `reviews/AUDIT_UNCERTAINTY_REVIEW.md`.

### Independent audit reconciliation and preserved artifact failure

The first independent readback stopped at a missing inventory entry before loading a numeric array. The original inventory had captured a 214,433,792-byte partial characteristics copy that was no longer present. Its recorded SHA256 exactly matched the first 214,433,792 bytes of the retained canonical characteristics file. The investigation and failed readback remain preserved; the specific infrastructure origin is unresolved.

The lead authorized exact byte reconstruction at that recorded path, using exclusive file creation and the original expected size/hash. Before/after checks confirmed that all three canonical inputs, the original artifact manifest, summary, controller, reviewer and nomination were unchanged. No manifest entry was removed, reference rewritten, model rerun or tolerance relaxed.

The **same frozen reviewer** then completed `evidence/audit_independent_readback_002` with **182 checks passed**. It verified full input/source/output identities, complete drift/fees/net/market accounting, selected policy/package bindings, the exact 755-row mask and reported metrics. Crucially, it reserialized the earlier prefix directly from the full audit arrays: all **3,024 validation forecasts, 2,771 targets and held books, and 2,770 economic rows** matched their earlier validation identities exactly. The original discovery prefix also remained exact. Recovery details are in `evidence/audit_artifact_manifest_investigation_001`; readback 001 remains a failure, not a retroactive pass.

### Final clean-package replay

The unchanged four-file package then replayed the completed canonical audit in a fresh isolated directory. All 20 controller and 26 worker checks passed. Every forecast, target and held-book array, and all 3,526 economic/net rows, matched exactly, including full costs. Its fixed audit metrics were identical. Mean candidate rebalance was 2.191670 ms and forecast time 6.226206 seconds in that replay; those are new timing measurements of the same observations, not another independent performance sample.

The wrapper, helpers, configuration, note and verifier retained their frozen hashes. Exact run/readback records are in `evidence/handoff_audit_001`, `evidence/handoff_audit_readback_001` and `reviews/HANDOFF_AUDIT_RESULTS.md`. The tested package is ready for review; no external submission was made.

The current evidence supports a fixed, low-beta candidate with positive audit performance after the supplied full fees. Any further research must acknowledge that discovery, validation and this audit are now exposed. A changed strategy would need new genuinely unseen evaluation data for another clean confirmation; this audit cannot be reused as though its outcomes were unknown.

## Contribution and interpretation boundary

The user reports noticing the same broad early patterns, emphasized protection from lookahead and overfitting, and requested continued literature-grounded experiments and subagents. AI performed the implemented research, code, executions, independent-agent review, evidence reconciliation and packaging. No unreported human coding, independent numerical replication or discovery of the simulator is attributed.

All market results concern the supplied simulated market and its specified fee convention. The task's unseen future remains unobserved. A small positive historical edge can be overwhelmed by response changes, adaptation lag, omitted common risks, beta-estimation error, costs or tail events. The strategy's market hedge uses estimated betas; low realized beta in the tested windows does not guarantee the same in future data. The repository preserves the evidence needed to assess those limits, including failures, unfavorable alternatives and the exact choices made before protected access.
