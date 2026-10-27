# C12: local additive characteristic responses

**Prospective specification, 27 October 2026 (Europe/Paris).** This restores the previously approved, unexecuted C12 design after a workspace reset. No C12 market result has been observed. The independent verifier must preserve its controller and expected missing-module run before the candidate implementation is written. The prior interrupted work is not a verification pass.

## Question and admission

Do simple local response shapes add useful conditional-mean information beyond the thirteen linear and thirteen global-quadratic columns in C02, after the unchanged scorer charges full trading costs? This is the twelfth and final configuration in the original discovery budget, within the existing additive characteristic family. It does not admit a search over knots, penalties, selected characteristics, holding horizons, or portfolio policies. All thirteen characteristics receive exactly the same extension.

The motivation comes from the distinction between a global quadratic and a response that changes slope locally. Freyberger, Neuhierl, and Weber's July 2018 [institutional working paper](https://bfi.uchicago.edu/wp-content/uploads/we6b7o-WP_2018-50.pdf), especially Section II and the appendix, studies nonparametric additive characteristic functions with spline expansions. C12 is a deliberately simpler fixed-hinge ridge adaptation, not a replication of their rank transformation, quadratic splines, or adaptive group LASSO. Counterevidence matters: Gu, Kelly, and Xiu's [September 2019 author manuscript](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), Section 3.2, reports that its additive spline GLM did not improve on purely linear methods. Neither study identifies this anonymous simulator or guarantees an edge here.

## Exact basis

Call the unchanged C02 `base._basis(panel, config)` with `basis="additive"`. Retain its first 26 columns byte-for-byte: the thirteen panel-standardized, clipped, recentered linear columns `z_j`, followed by thirteen centered-square columns `q_j = (z_j**2 - panel_mean(z_j**2))/sqrt(2)`. Reusing this output preserves the original operations and clipping convention.

For each characteristic `j = 0,...,12`, append three columns in the order `a = -1, 0, +1`; the appended block is **feature-major**, so columns `26 + 3*j + k` correspond to the three knots in that order. Define

```text
Q(a)    = 0.5 * erfc(a / sqrt(2))
phi(a)  = exp(-a*a/2) / sqrt(2*pi)
m1(a)   = phi(a) - a*Q(a)
m2(a)   = (1+a*a)*Q(a) - a*phi(a)
s2(a)   = m2(a) - m1(a)**2 - Q(a)**2 - phi(a)**2/2
h_j,a   = maximum(z_j-a, 0) - panel_mean(maximum(z_j-a, 0))
u_j,a   = (h_j,a - Q(a)*z_j - phi(a)/sqrt(2)*q_j) / sqrt(s2(a))
```

Use these analytic formulas, evaluated in ordinary double precision, rather than coefficients fitted to any project data. The reference standard deviations are approximately `0.11811820495718785`, `0.10614888300004365`, and `0.11811820495718879`. Small last-bit differences from algebraically equivalent evaluations are not market-driven parameter choices.

The standard normal is a **fixed reference convention**, not an assumption that the observed characteristics are normally distributed. Under that convention the new terms remove the components along the existing linear and square directions, then scale the remaining novelty to unit variance. They need not be empirically orthogonal or unit-variance in a realized cross section. The three local terms are mutually correlated. Adding them preserves the same functional span as adding the three centered hinges to the original terms; this does not assert empirical rank 65 on every panel.

There are 65 columns in total. Raw hinge novelty after projection onto the existing two directions has standard deviation only about 0.106–0.118 under the reference distribution. Scaling makes the meaning of the new ridge penalty explicit instead of accidentally shrinking that small remaining direction almost entirely away. All three local directions receive `local_ridge = 0.3`; the original 26 retain `ridge = 0.1`. The illustrative scalar retention `1/(1+0.3)` applies only to one isolated unit-variance direction. It is not the joint retention of the correlated design, a fitted optimum, or evidence of predictive power.

## Estimator and information clock

Copy the C02 causal exponentially weighted sufficient-statistic algorithm with only the basis width and ridge diagonal changed. Set `alpha_half_life=252`, `min_training_days=126`, `feature_clip=4`. At forecast row `t`, the newest completed pair is `X[t-2] -> R[t-1]`; estimate that label's market beta using `R[:t-1]`, strictly before the label return. Apply coefficients to `X[t-1]`. The first potentially active forecast is row 127. The final input row is not a training label or forecast feature for an earlier decision. Keep moments, fitted coefficients, and training mass local to each `forecast` invocation.

No full-sample transforms, rank recomputation over time, future-dependent tuning, future-trained global cache, cross-validation over shuffled rows, or feature selection is permitted. The cross-sectional panel mean is contemporaneously observable under the assignment information convention and is not a time-series fit.

## Unchanged portfolio and exact configuration

Delegate `rebalance`, `estimate_risk`, and current-call diagnostics to the unchanged C02 base. The forecast module may configure it but must never fill a fitted object later consumed by rebalance. Preserve these values:

| Setting | Value |
|---|---:|
| candidate_id | C12_local_additive |
| basis | additive |
| alpha_half_life | 252.0 |
| ridge, local_ridge | 0.1, 0.3 |
| min_training_days | 126 |
| feature_clip | 4.0 |
| risk_window, risk_min_days | 252, 20 |
| variance_shrinkage | 0.2 |
| variance_floor | 0.000001 |
| risk_aversion | 1000.0 |
| cost_horizon | 20.0 |
| weight_cap, gross_cap | 0.01, 1.0 |

The existing gross-rescaling approximation remains documented. A twenty-day optimizer cost amortization never changes the evaluator's full realized cost charge. No simultaneous covariance, execution, leverage, or optimizer modification is part of this experiment.

## Verification and execution gates

1. An independent agent records failure modes, edge cases, expected outcomes, and the synthetic E2E controller before candidate implementation. Preserve the first expected missing-module failure, including its command and environment. Do not count it as a green run.
2. Implement only `submission/strategy_local_additive.py` and `research/configs/C12_local_additive.json`; do not edit shared candidate modules or the official scorer. A different agent reviews the information clock, basis, penalties, source closure, and evidence.
3. Run the previously approved five-case synthetic workflow: known local signal on features 0/2/4 using knots -1/0/+1; unchanged repeat; joint future alteration at cutoff 400; prefix 384; exact zero-return cash control. The independent plan owns exact fixture generation and masks. The known signal's protected truth correlation must be at least 0.90; this deliberately strong fixture is a wiring check, never evidence of market profitability. The cash control requires exactly zero forecasts, positions, and economics, with Sharpe and beta undefined rather than manufactured as zero. Save scorer reconciliation, full costs, identities, masks, expected/actual outcomes, and failures.
4. Root may authorize one exact discovery run only after the prospective synthetic gate and independent source review pass. Use only input rows `[0,2016)` and the frozen score mask `[253,2015)`. Neither chronological validation nor the sealed audit is opened by this plan. An exact interrupted-run retry is not a new tuned configuration, but its interruption and identity must be recorded.

## Metrics, comparison, and falsifier

Primary contrast: C12 versus C02 net annualized Sharpe on exactly the same discovery score mask with the unchanged official scorer. Report gross and net Sharpe, net annualized mean and volatility, actual cost drag, realized market beta, mean rebalance runtime, gross scaling, and stability across the already fixed discovery partitions when the standard runner provides them. Do not invent a new favorable partition or optimize against it. C06 remains the already observed discovery leader and is an additional reference, not the paired alpha-only control.

C12 is an informative negative result if its net Sharpe does not exceed C02, even if gross performance improves. A positive primary contrast is only grounds to consider continued evaluation, conditional on the existing beta, runtime, accounting, and causality gates. It is not sufficient evidence of a tradable edge, a statistically established improvement, or a reason to suppress C01–C11. No threshold, penalty, or acceptance rule may be revised after seeing C12 performance. Candidate nomination and protected evaluation follow the already frozen research protocol separately.

No C13 is admitted by a failure. Any additional predictive design would need a visible protocol decision before execution, not a renamed rerun or an uncounted diagnostic.

## Overfit interpretation

This specification is fixed before C12 implementation and execution, but it follows eleven observed discovery configurations and exploratory reasoning. It therefore reduces additional discretion without turning discovery into an untouched holdout. A future-perturbation pass detects no tested information leak; it cannot certify freedom from selection overfit. The effective number of research choices exceeds a simple count of independent models and is not known. A Deflated Sharpe Ratio or PBO number is not reported without a justified selection experiment and dependence treatment. Chronological validation and the sealed audit remain the relevant checks on an unchanged selected policy.

There is no calendar execution schedule. Each next action depends on the evidence gate above.
