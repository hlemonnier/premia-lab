# Review of the user's exploratory notes

**Review date:** 27 October 2026, Europe/Paris.  
**Baseline:** published commit `4e2a17816ce674c6a781771ca1e6cbe24c1d19c6`.  
**User attachment:** `takehome_exploration_notes(1).md`, SHA256 `21c6bbbf95f93267f6afa8280f52517f07f23ff43d867ab8529fe6330ee4b2ef`.  
**Scope:** source, mathematical and existing-evidence review. No new market experiment, parameter selection, strategy implementation or protected-period replay was performed for this document. The frozen handoff is unchanged.

## Assessment

The notes are useful as a methodological challenge and hypothesis inventory. They explicitly say that the author had not opened the returns, characteristics or figures, so they cannot be treated as independent empirical confirmation of the project's discoveries. Attribution should retain the distinction between the user's own points and the ideas labelled D1/D3; the three outside reviews themselves were not supplied for this review.

The most valuable points are the matured-label boundary, the separation of beta neutrality from dollar neutrality, linear trading costs around drifted holdings, dependence between stock-day observations, and the danger of removing the very characteristic signal being estimated. Most are already implemented or explicitly considered in the completed research. Some categorical criticisms need revision: a diagonal risk model can be a defensible regularization choice, an appropriately sized equal-weight market hedge can work, and correlation does not identify how a characteristic was constructed.

The recovered project is beyond the early checkpoint discussed in the request. Twelve discovery configurations have been evaluated. Frozen C09 won the specified validation comparison with net Sharpe 0.659210 against C06's 0.398603, then earned 1.799231 on the separately reserved 755-observation audit. The complete history, including weak validation uncertainty and unsuccessful alternatives, is in [the continued research report](CONTINUED_RESEARCH_20261027.md). These periods are now exposed. This review does not convert a new idea into permission to change the evaluated policy and claim the same audit as fresh confirmation.

## What the notes add, and what the project already covers

| Point from the notes | Evidence already available | Assessment and remaining limitation |
|---|---|---|
| A forecast for day t may train only on completed labels | [C09 source audit](../reviews/C09_CAUSALITY_SOURCE_AUDIT.md), [causal results](../reviews/C09_CAUSALITY_RESULTS.md), [engine](../handoff/model/strategy.py) | Implemented: prediction uses X[t−1]; newest pair is X[t−2] with R[t−1]. Source inspection and finite future-alteration workflows support this boundary. |
| Rank-deficient covariance makes an unregularized inverse unsafe | [Risk findings](RISK_FINDINGS.md), [factor experiment](C04_FINDINGS.md), [rank contrast](C10_RISK_RANK_PLAN.md) | Addressed through a positive diagonal baseline and explicit factor challengers. The selected model remains diagonal; the existence of residual covariance alone did not establish a better predictive portfolio. |
| Characteristic scale, persistence and redundancy should be measured | [Alpha findings](ALPHA_FINDINGS.md) and its referenced discovery tables | Measured on discovery. Values were near cross-sectionally standardized; one-day rank persistence was about 0.999 and twenty-day persistence about 0.98. These are characteristics, not measured alpha half-lives. |
| Signal effects should be checked at several horizons and by subperiod | [Alpha findings](ALPHA_FINDINGS.md) | Fixed 1/5/20-day labels and chronological blocks were examined. The complete 0…20-lag curve proposed in the notes was not run. Overlapping labels are dependent. |
| The 4/6/3 names could indicate different processes | [Redundancy and persistence findings](ALPHA_FINDINGS.md) | Broad correlation structure was observed, but no formal test establishes these name groups as distinct simulator mechanisms. Names remain hypothesis prompts. |
| Raw and residual returns answer different questions | [Alpha findings](ALPHA_FINDINGS.md), [GLS plan](GLS_ALPHA_PLAN.md) | Raw and market-controlled diagnostics exist; covariance-weighted learning was tested. Those exercises do not identify every expected-return component associated with latent factors. |
| Nonlinear effects require joint estimation | [C11 findings](C11_INTERACTION_FINDINGS.md), [C12 specification](LOCAL_ADDITIVE_PLAN.md), [continued results](CONTINUED_RESEARCH_20261027.md) | All-feature additive, all-pair quadratic interaction and fixed local-hinge contrasts were evaluated. C11/C12 did not beat their declared additive parent. There is no evidence-based reason to retrospectively select their best-looking terms. |
| Static cost heterogeneity must enter decisions | [Risk findings](RISK_FINDINGS.md), [allocator](../handoff/model/portfolio.py) | Each stock's cost enters the absolute-trade penalty; the scorer charges full actual fees. Weak simple cost/risk correlations do not establish independence or justify always choosing cheap names. |
| Dollar neutrality is insufficient | [Risk findings](RISK_FINDINGS.md), [allocator](../handoff/model/portfolio.py) | The portfolio directly constrains estimated beta. Dollar neutrality is not separately imposed by the selected policy or required by the employer. |
| Rehedging should consider actual position drift | [Allocator](../handoff/model/portfolio.py), [accounting specification](../verification/ACCOUNTING_PLAN.md) | Actual drifted holdings enter the cost-aware solve. The selected proportional gross-cap step is a disclosed approximation and can disturb a pre-scaling no-trade decision. |
| Different candidates need uncertainty on their differences | [Wave-one comparison plan](WAVE1_COMPARISON_PLAN.md), [protected uncertainty plan](PROTECTED_UNCERTAINTY_PLAN.md) | Fixed paired time-block resampling was used. Validation uncertainty does not establish C09's statistical superiority, despite its deterministic selection under the declared rule. |
| Verify performance and compute claims rather than repeat them | [Long-history readback](../reviews/LONG_HISTORY_INDEPENDENT_READBACK.md), [handoff audit](../reviews/HANDOFF_AUDIT_RESULTS.md) | C09 completed a 25,200-row engineering workload: about 43.19 seconds for forecast and 2.19 ms mean rebalance on that host. Repeated data test runtime, not independent alpha. |

The risk-spectrum work did not implement a Marchenko–Pastur selection rule, characteristic-to-cluster mapping, or a comprehensive cluster-stability study. The original full-sample figures were intentionally not used to select the model. None of those omitted diagnostics invalidates the existing causal accounting path; none should be claimed as completed.

## Corrections to the notes

### 1. Same-day correlation is not evidence of feature construction

A relationship between X[t] and R[t] can arise because returns enter the characteristic, because both respond to a common state, or because of a measurement/publication convention. Correlation alone does not identify which explanation is true. It is a timing diagnostic, not a mechanism test. Regardless of its origin, an after-close X[t] cannot be used to earn R[t]. The project's one-day lead is therefore necessary even when a contemporaneous relationship is large.

The same caution applies to changing marginal signs. Under a fixed multivariate linear model, Cov(X_j,Y) = Σ_k Cov(X_j,X_k)β_k. A changing predictor covariance can change a marginal sign without a changing structural β. Sampling variation or common shocks can do so as well. The weak performance of the faster learner and the selection of longer-memory C09 are consistent with an estimation-noise problem; they do not prove that the true coefficients are constant. See [the longer-memory admission](LONG_MEMORY_PLAN.md).

C09's **1,008-day half-life** controls the exponential forgetting of observations in coefficient estimation. It is not a claim that the forecast's future payoff lasts 1,008 days. The **twenty-day cost horizon** is a separate fixed trading-control approximation, and the observed **characteristic persistence** is a third measured quantity. Keeping these three meanings separate is necessary when explaining why the model trades slowly.

### 2. An equal-weight market hedge is mathematically valid when sized correctly

Let m be equal weights and b be the estimated stock-beta vector against the same market. For an initial portfolio w, the overlay

    w_hedged = w − [(bᵀw)/(bᵀm)] m

has bᵀw_hedged = 0 whenever bᵀm is nonzero. With internally consistent unshrunk regressions against the equal-weight portfolio, bᵀm equals one up to arithmetic. Thus a market overlay need not ignore stock betas; the hedge coefficient can use the book's beta directly.

The legitimate objections are turnover in many names, possible cap violations, gross/net dollar exposure, and the fact that such an overlay does not jointly optimize forecast, risk and cost. Removing the net dollar position instead of the beta exposure would be wrong. C09 uses a beta equality inside the allocator, which addresses those trade-offs more directly. Its measured *net-return* beta must still be evaluated because a hedge of estimated gross exposure does not eliminate the covariance of trading costs with market returns.

### 3. Ignoring off-diagonals is a modeling trade-off, not a categorical error

Residual covariance exists in the discovery data. An unregularized matrix with 1,000 names and 252 observations is also poorly identified: an uncentered second moment has rank at most 252, and a centered sample covariance has rank at most 251. Adding covariance structure can reduce omitted-risk bias while increasing estimation error. A positive diagonal model is a strong regularization choice with a known blind spot, rather than an assertion that stocks are independent.

[Ledoit and Wolf's primary abstract](https://ledoit.net/honey_abstract.htm) explains how sample-covariance estimation error can damage portfolio optimization and motivates shrinkage. It does not prove that a diagonal target is optimal here. In this project C06's covariance learner/factor portfolio had the higher discovery score but lower protected validation score than diagonal C09. This comparison changes several components and does not isolate the causal contribution of off-diagonals; it does defeat the claim that richer covariance must improve the chosen objective.

Marchenko–Pastur thresholds would require a declared null and treatment of heterogeneous variance and dependence. A large eigenvalue is evidence against a particular noise model, not proof of a tradable factor or a persistent risk exposure.

### 4. Linear costs create inaction regions, but the regions are coupled

For the static objective implemented by the allocator,

    maximize μᵀw − (γ/2) wᵀΣw − Σ_i k_i |w_i − h_i|,

where h is the drifted book and k_i = cost_i / 20 in C09, an interior unchanged coordinate satisfies a subgradient condition. With equality constraints Aw = 0 and multipliers λ,

    |μ_i − γ(Σh)_i − (Aᵀλ)_i| ≤ k_i

is the corresponding no-trade condition at the unchanged book, provided that book is feasible and no active bounds add further terms. If only one coordinate stays unchanged while others trade, use the solved w in the risk gradient. Beta multipliers and off-diagonal covariance link these conditions across stocks. They are not independent intervals determined by costs alone; a previously infeasible beta exposure can force trades even if every unconstrained stock would stay put.

The existing diagonal allocator solves for the beta multiplier and implements this threshold logic. The twenty-day cost amortization is an approximation, not an estimated optimal dynamic horizon. The subsequent gross scaling may create trades that the pre-scale solution would avoid, as the frozen handoff note explicitly discloses. [C07](C07_FINDINGS.md) tested a joint gross constraint but did not establish a generally superior complete strategy.

[de Lataillade et al.](https://arxiv.org/abs/1203.5957) analyze predictor thresholds under linear costs and connect them to no-trade bands. Their one-market problem supports the mechanism, not the exact constrained multi-asset rule above, which follows from the project's objective. Quadratic-cost partial-adjustment formulas should not be presented as solutions to this absolute-cost objective.

### 5. The quoted Sharpe standard error mixes frequencies

For an illustrative IID Gaussian calculation, let s be the daily Sharpe, q = 252, N the number of daily observations, and S = √q s the annualized daily Sharpe. The delta-method approximation is

    SE(S) ≈ sqrt[(q/N) × (1 + S²/(2q))]
          = sqrt[(1/Y) × (1 + S²/(2q))],  Y = N/q.

Putting annualized S into sqrt[(1 + S²/2)/Y] instead corresponds to using annual observations under that simple approximation, not annualizing a daily estimator. For S = 1 and Y = 14 the daily-estimator expression is about 0.268; the quoted expression is about 0.327. This conversion is mathematical illustration, not an error estimate for our dependent returns. [Lo's paper](https://traders.berkeley.edu/papers/The-Statistics-of-Sharpe-Ratios.pdf), equation 9 and its time-aggregation/non-IID discussion, explains why frequency and dependence matter.

A marginal Sharpe standard error also does not determine the standard error of a *paired difference*. Highly correlated strategies can have an accurately estimated small difference. The note's blanket implication that differences below about 0.3 are mostly noise is therefore too strong. Use the recorded paired time-block comparisons and their assumptions; do not choose an uncertainty formula because it favors a candidate.

### 6. Residualization needs an explicit target

The note's warning is correct for the intended signal span. If expected returns satisfy μ = Xθ and M_X projects orthogonally to the full span of X, then M_Xμ = 0: projecting that span out removes the modeled signal. This differs from projecting out an unwanted market exposure or using a separate, carefully justified nuisance model.

Market-residual labels, full latent-factor residual labels and GLS-weighted regression are distinct choices. GLS changes the loss weighting; it does not mechanically delete the entire factor span. A characteristic can predict common-factor expected returns as well as idiosyncratic returns. Projecting out all common factors can therefore remove useful prediction. High realized common variance does not by itself tell us which component of the conditional mean should be retained. C09 removes its estimated market component from labels and targets a market hedge; it does not enforce characteristic neutrality.

### 7. Several practical statements need narrower wording

- **Sharpe is scale-free only under the relevant scaling assumptions.** Multiplying a fixed net-return series by a positive constant preserves its Sharpe. Scaling this strategy's targets changes drift denominators, constraint activity and subsequent trading decisions, so exact invariance is not guaranteed by the scorer. C08 was an actual sizing contrast, rather than an appeal to scale invariance.
- **A zero-beta book does not require zero dollars.** Adding dollar neutrality is an additional portfolio constraint with possible opportunity and turnover costs. It may be a useful hypothesis, but it is not implied by the employer's beta requirement.
- **A full-sample constant can pass a future-input perturbation check.** Such a check does not reconstruct how the constant was selected. Historical in-sample performance remains selection-contaminated even if the eventual executable contains no future-data access. Frozen research choices and initially untouched evaluation address this separate risk.
- **Do not relax equality after a convenient failure.** Tolerances should be specified prospectively, and discrepancy causes investigated. The project's canonical-layout reruns preserved the original exact checks; they did not loosen them to obtain a pass.
- **Protect the boundary row as well.** If inputs change from row c onward, forecast rows through c must remain unchanged because row c uses information through c−1. Net-return comparisons stop before c, since the changed day's return and its closing trade can legitimately differ. Checking only forecasts strictly before c would miss a one-row leakage error.
- **There is no universal cvxpy runtime for 1,000 variables.** The supplied README estimates roughly one second per call for its particular naive cvxpy example; that is an employer-provided estimate, not a local benchmark or a universal limit. Solver, sparsity, warm starts, formulation and hardware matter. This provenance differs from the unsupported two-to-five-millisecond claim that the notes correctly question.
- **Pooling is a variance-control assumption.** Stock-specific parameters do not intrinsically decay. Pooling reduces estimation burden and assumes some shared mapping; any cluster or stock-specific alternative needs its own evidence.

## What deserves future research

Three questions are useful if a genuinely new evaluation sample becomes available:

1. **Common-factor prediction versus residual alpha.** Decompose forecast payoffs using risk loadings estimated only from prior observations. Measure which components have stable conditional means before deciding to hedge them away. A full IPCA or new factor-regression system should follow that diagnostic, not precede it.
2. **Predictive decay versus characteristic persistence.** Fix a small horizon set and a label-maturation rule. Investigate whether payoff decay differs enough across signal components to justify different trading thresholds. A persistent input, persistent fitted forecast and persistent future payoff are separate quantities.
3. **Estimation noise versus genuine coefficient drift.** Compare a tightly specified adaptive alternative with the frozen longer-memory benchmark, with attribution of turnover and coefficient uncertainty. Apparent marginal sign changes are insufficient evidence for fast regime switching.

These are research proposals, not executed tests or an expansion of the current twelve-configuration cycle. Resampling known days, replaying another slice, examining the already reported audit, or changing its name cannot create a genuinely untouched confirmation sample. With the present information, the sound deliverable is the frozen reviewed C09 and an honest account of its evidence. Methodological notes and reproducibility can still improve without changing the evaluated policy.

## Review record and attribution

This review read the attachment, AGENTS.md, discovery alpha/risk reports, C09 configuration and all three substantive handoff source files, the recorded comparison/literature plans, and the completed research report. It did not load original market arrays, run a strategy, or add tests. Numerical values above are attributed to existing recorded results and have not been represented as a new independent replay.

The external checks used the author/publisher record for Lo and an accessible copy of his primary paper, the Ledoit–Wolf author abstract, and the arXiv primary record for linear-cost trading. The Ledoit PDF requests failed during this review; no claim depends on having read that full text. The equations for the market hedge, covariance rank, coupled static subgradient conditions and annualization conversion are the reviewer's mathematical deductions, with their assumptions stated.

The user is the source of the exploratory document and the personal observations labelled `[me]`; D1/D3 ideas retain their stated outside-review origin. AI produced this reconciliation and the project's implemented research. No empirical result, code contribution, or discovered simulator mechanism is retrospectively attributed to the user by this document.
