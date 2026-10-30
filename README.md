# Quant Research Take-Home

Hugo Lemonnier, October 2026

**N0 — the only model in this submission.** This is a post-submission research update. I model the anonymous characteristics as shared return and risk exposures, rather than fitting 1,000 unrelated stock forecasts. I combine two estimates of their premia and add a bounded own-stock residual correction. This is an extension of the original hand-in, not evidence that I have improved its performance on the evaluator's unseen continuation.

At the supplied fees, the current N0 candidate has development **net Sharpe 1.55078, beta 0.09329 and annual trading costs of 0.34385%**. Without the explicit market position, its Sharpe is **1.43669**. Every comparison below uses the original scorer and the same exposed history.

## The research argument

**1. Separate common exposures from stock-specific effects.** I treated the 13 characteristics as candidate factor loadings. Their linear and squared terms describe shared variation in market-residual returns. This is a useful empirical representation, not a claim to have recovered the simulator's generator. Explaining contemporaneous returns alone would not establish predictability: the trading forecast must estimate premia from earlier observations and apply them to exposures already published.

I use a pooled 27-column design: 13 standardized characteristics, their centred squares and standardized trailing beta. The original return estimator uses ridge regression with 1,008- and 252-day half-lives. I average the linear coefficients from both memories; the squared and beta coefficients retain the slower memory. The rationale is shared information across stocks with limited adaptation over time, rather than a separate noisy mean estimate for every name.

**2. Distinguish forecasting risk from forecasting returns.** More flexible return models did not reliably improve the tested forecasts. I therefore investigated whether risk changes made otherwise useful exposures less attractive. The factor-risk extension, F, fits one shared Gamma regression with three multihorizon variance predictors, refitting every 126 days. Its variance corrections are bounded to [0.75, 1.5]; correlations and specific-risk estimation remain unchanged. F improved historical factor-variance loss and the stock-only portfolio. A simpler common-risk adjustment performed similarly, so I do not claim that factor-specific detail has proven incremental value.

**3. Use covariance information in estimation, without trusting it completely.** Correlated, heteroskedastic errors need not contribute equally to learning premia. The second estimator uses lagged inverse covariance weights and coefficient-wise ridge shrinkage on the same design. I average it 50/50 with the original forecast; that blend was specified before testing.

Pure GLS scored about 1.4818, below F's 1.4934. The combination scored 1.5332. A matched unweighted estimator with the same penalty and startup scored 1.4959. However, replacing coefficient-wise shrinkage with an isotropic penalty largely removed the weighting benefit. My conclusion is about a covariance-aware **regularized combination**, not the unconditional superiority of GLS.

**4. Ask whether residual predictability remains.** A directed cross-stock model failed after costs, but its own-history control, N0, was more promising. I normalize stock residuals by prior specific volatility and form a five-day-half-life level. Starting at forecast row 505 and every 126 days thereafter, I estimate own-lag slopes from 504 matured labels. I require sign agreement across two halves, soft-threshold correlations above `3 / sqrt(504)`, and bound slopes to [-0.25, 0.25]. This is a heuristic screen, not a calibrated universe-wide significance test.

I project this correction off the existing design and intercept, halve it, and cap its RMS at 20% of the core forecast's RMS. The selected mode uses no cross-stock predictive terms. Most retained coefficients are reversal-like, but selected names change substantially; I do not interpret them as a permanent list of predictable stocks.

I selected the frozen N0 own-history correction on top of the GLS ensemble because its historical gain at the supplied fees survives removing the explicit market sleeve and the largest signal sources. Its added value remains statistically uncertain; the model was discovered as a control, and selection on the same exposed history can overstate its future performance.

## What changed relative to the earlier approach

| Development comparison | Net Sharpe | Without explicit market position |
| --- | ---: | ---: |
| Earlier characteristic-factor strategy, V3 | 1.44473 | 1.33958 |
| Time-varying factor variances, F | 1.49344 | 1.38560 |
| Fixed two-estimator combination, GLS | 1.53322 | 1.41900 |
| GLS plus own-residual correction, N0 | 1.55078 | 1.43669 |

These are sequential historical comparisons, not an additive causal attribution or independent replications. The most recent increment is also the least secure: N0 adds only **0.01756 Sharpe** over GLS, with a paired 63-day block-bootstrap interval of approximately **[-0.01863, +0.05387]** that does not account for the complete research search.

N0's gain remains positive after removing the largest signal source and under a causal source-removal diagnostic. That argues against one source explaining the entire gain, not against selection bias generally. It adds about 19.99 basis points of annual gross mean return, of which extra trading costs consume 11.27 basis points. Higher-fee stress tests reverse the advantage, but those are sensitivity diagnostics: the assignment specifies fixed supplied fees, and turnover already pays those fees in the net score.

## Portfolio construction and chronology

I allocate through a diagonal-plus-factor covariance model. I retain the chosen 0.3 factor-risk scaling as an allocation trade-off, not an estimate of the true covariance. A custom dual Newton solver handles a linear turnover penalty, an estimated-beta constraint and position caps. The 20-day cost scaling is a practical approximation, not an exact multi-period solution.

A reference stock book controls sizing within one-half to twice the base size. The stock allocator uses its own drifted holdings; I add a fixed +0.05 equal-weight market position afterward. The original scorer charges actual combined trades. The internal stock-book cost problem therefore approximates, rather than exactly matches, the total-book cost problem. The market position is explicit carry, not stock-selection alpha, and can hurt when its premium disappears.

Forecast row `t` uses only data before `t`. For the one-day premium estimators, the newest label at `t-1` uses exposures from `t-2` and covariance information predating the label. N0 obeys the same matured-label discipline. Earlier outputs were unchanged in the executed future-mutation, prefix and reset checks. Those checks establish tested causal behaviour, not economic generalization.

A recorded 25,200-day repeated-history run took about 330 seconds for forecasting and 11.8 ms per rebalance on average. It tests execution and resources, not unseen-market performance. All supplied years have been examined; there is no untouched holdout.

## Limits and next question

The strongest working hypothesis is shared premia with time-varying risk. N0's changing, sparsely selected residual effects are a weaker extension. Premia or covariance can drift; beta hedging is estimated; the explicit market position can lose; sizing cannot guarantee survival against arbitrary shocks. A causal strategy can still be overfit through repeated development choices.

My next question would be whether residual-reversal persistence supports the additional trades at the **specified** costs, with a fixed comparison against the unchanged core. I would not hard-code successful names, claim discarded controls as independent validation, or add a larger model merely to increase the historical maximum.

## Run and files

Place this package alongside the original unchanged `score.py`, `returns.csv`, `characteristics.csv` and `costs.csv`, then run:

```bash
python score.py strategy
```

`strategy.py` is the single entry point and instantiates `model_n0.N0Policy()`. All numerical components belong to the one `model_n0/` package: `premia.py` estimates the core return forecast, `risk.py` estimates factor variances, `execution.py` handles sizing and trading, `residuals.py` builds causal residual histories, and `policy.py` adds the own-history correction. The characteristic basis, allocator and settings are supporting numerical modules, not alternative models. There is no `model_f/`, no root `gls_alpha.py`, no cross-stock mode and no selectable model switch.

The twelve-file package excludes the original data and scorer. Earlier model labels in the research narrative describe historical comparisons only; those alternative submissions are not included here. I retain the characteristic-factor and GLS calculations because they are components of N0 itself, not optional old models. It uses NumPy, SciPy and scikit-learn, with tested versions in `requirements.txt`; the scorer also needs pandas. No fitted-model file, network access or research checkout is required.
