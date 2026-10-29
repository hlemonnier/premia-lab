# Quant Research Take-Home

Hugo Lemonnier, October 2026

I model the simulated market through the premia earned by its characteristics. I combine two estimates of those premia, turn the resulting forecasts into positions through a time-varying factor risk model and a cost-aware allocator, hedge estimated market beta, then add a small market position deliberately.

On the supplied fifteen-year history, with the unmodified `score.py` and full trading costs: **net Sharpe 1.53, beta 0.094, costs 0.23% a year**. Without the explicit market position, the same strategy scores **1.42 with beta 0.044**. These are development results, not estimates of guaranteed future performance.

## The idea

**What the market looks like.** I treated the 13 characteristics as possible factor loadings rather than as 13 unrelated trading signals. Stocks with similar characteristics share return variation, and a basis containing the characteristics and their squares captures useful structure in market-residual returns. This suggested separating two questions: what premium does each exposure earn, and how much risk does that exposure carry today?

**Why I pooled the forecast.** I used one mapping across all 1,000 stocks rather than estimating a separate expected return for each name. The model is deliberately small: a stock's expected residual return is its current exposures multiplied by estimated premia. Linear and squared exposures allow different effects near the centre and in the tails; trailing beta supplies an additional low-beta feature. The premia can drift, so I do not hold their estimates fixed over the full history.

**How the direction changed.** My initial emphasis was on finding a better return signal. Richer characteristic transformations and more flexible return models did not reliably improve the tested forecasts. I did not take those failures as proof that the problem was solved. Instead, I asked whether a useful signal was being weakened by its estimation or by the way it was turned into a portfolio.

That led first to **F**, a small model for time-varying factor variances. It improved the stock book even after removing the explicit market position. The next step was to use the risk information in the return estimator itself: observations from noisy, correlated directions should not necessarily have the same influence as cleaner ones. That produced the **GLS forecast combination** submitted here.

## Forecast: two estimates of the same premia

**The original estimate, F2.** I fit pooled ridge regressions of next-day market-residual returns on 27 columns: 13 cross-sectionally standardized characteristics, their centred squares and standardized trailing beta. The learners have half-lives of 1,008 and 252 trading days. I average their 13 linear coefficients; the squared-characteristic and beta coefficients retain the longer memory. This gives the linear effects some adaptability without making every coefficient react equally quickly.

**The second estimate, GLS.** I use the same features and labels, but weight each matured training cross-section by an inverse factor-plus-specific noise covariance estimated before its outcome. I profile out a daily nuisance intercept and regularize each coefficient in proportion to its weighted training variation. The covariance weighting and this coefficient-wise penalty form one specification: matched controls showed that replacing the penalty with uniform shrinkage largely removed the benefit.

I selected a fixed 50/50 combination of two causal estimates of the same return premia: the original F2 forecast and a covariance-weighted, coefficient-wise-regularized forecast. The historical gain survives removing the explicit market sleeve and increasing trading costs, but its added value is not statistically established.

The distinction matters: **pure GLS scored about 1.48, below F's 1.49; the fixed combination scored 1.53**. I kept the blend specified before the experiment rather than choosing a weight after seeing the results. The evidence supports combining the estimates, not claiming that GLS is the better estimator on its own or that it discovers a new information source.

For forecast row `t`, all inputs come from rows before `t`. The newest training label is the return at `t-1`, paired with characteristics at `t-2`; its covariance weights were available before that label. The new prediction uses characteristics at `t-1`. Cross-sectional transformations do not use future dates.

## From forecast to positions

**Risk.** I retain a covariance model built from the same 26 characteristic factors, plus stock-specific variances. I discount the factor component by 0.3 when allocating: this is a chosen trade-off between estimated risk and the factor exposures carrying the forecast, not a claim that the discounted matrix is the true covariance.

The F adjustment forecasts each factor's next variance from three multihorizon measurements, with half-lives of 5, 21 and 63 days relative to its baseline variance. One shared Gamma regression with three predictors and an intercept is refitted every 126 days using only matured labels. Its final variance multipliers are bounded between 0.75 and 1.5. I retain the existing factor correlations and stock-specific variances. This improved the factor-variance forecasting diagnostic in every examined period, although simpler common total-risk scaling produced a similar portfolio score.

**Costs and the hedge.** Linear trading costs create no-trade regions: a small change in the forecast should not automatically trigger a trade. I solve a constrained mean-variance problem with a linear turnover penalty, per-stock caps and an estimated-beta hedge inside the solve. I use a fixed 20-day horizon to scale the cost penalty; this is an allocation approximation, not a solved multi-period trading problem.

The stock allocator uses its internally tracked stock book after return drift. The fixed market position is added afterward, and the original scorer charges costs on the actual combined holdings and trades. This distinction matters: the internal stock book is not identical to the total portfolio once the market position is added.

**Sizing.** I track a reference stock portfolio. When its recent volatility is high relative to its longer-run level, I reduce the traded book, and vice versa, within a multiplier range of one-half to two. I re-solve the stock allocation against its drifted holdings at the new risk aversion and caps rather than merely rescaling yesterday's target. An outer gross-exposure cap provides an additional safeguard.

**Speed and numerical checks.** I use a custom dual Newton allocator with feasibility and optimality checks and a certified fallback, rather than a general-purpose optimizer at every rebalance. In an actual 25,200-day, 1,000-stock endurance replay, the complete GLS forecast took about **82 seconds** and rebalancing averaged about **5 ms per call**, below the assignment's one-hour and 100-ms-average budgets. That fixture recycled the supplied history: it tests execution and resources, not an independent future.

## The market position

On top of the estimated-beta-hedged stock book, I hold **+0.05 of the equal-weight market**. This is deliberate market exposure, not stock-selection alpha. On the supplied history it raises net Sharpe from 1.4190 to 1.5332 and measured beta from 0.0441 to 0.0941. The residual beta without it also shows that the estimated hedge is imperfect.

A flat or falling market can remove this contribution; I do not assume that the sample's market premium will persist. The ensemble's improvement over F survives removing the position, so its measured advantage is not solely a larger share of market carry. To remove the explicit position, set `POLICY.sleeve = 0.0` after the policy is created in `strategy.py`.

## What I tested and did not select

I explored residual reversal, characteristic interactions and richer shapes, latent residual factors, market-position volatility timing and several beta corrections. I also tested more flexible return predictors, including gradient boosting and a small neural network. Those tested configurations did not earn a place in the final strategy; that is not evidence that every ML or deep-learning approach would fail.

The useful changes were more targeted: forecasting factor risk and combining differently weighted estimates of the same premia. For GLS, matched controls separated covariance weighting from startup, intercept handling and regularization. The gain was not explained by startup or ridge changes alone, but it depended on the interaction between weighting and coefficient-wise shrinkage. I retained that exact specification rather than selecting a new variant from the attribution tests.

A separate standardized-correlation candidate improved F, but less than GLS in its own experiment. I did not combine the two merely because both had higher historical scores. Reviewer checks at half and double the GLS ridge strength supported local stability; I did not replace the original setting with whichever sensitivity run scored highest.

## Results

Unmodified `score.py`, full costs, supplied fifteen-year history after the scorer's startup period: **3,526 scored daily observations**. Costs below are annualized fractions of capital, not turnover.

| Portfolio | Net Sharpe | Beta | Costs / year | First / second half |
|---|---:|---:|---:|---:|
| F, previous selected model | 1.4934 | 0.1012 | 0.2552% | 1.22 / 1.81 |
| GLS combination, stock book only | 1.4190 | 0.0441 | 0.2217% | 1.18 / 1.71 |
| **GLS combination with market position — submitted** | **1.5332** | **0.0941** | **0.2312%** | **1.26 / 1.85** |

At double and triple the supplied fees, complete reruns of the submitted strategy score **1.5133 and 1.4827**, against **1.4723 and 1.4562** for F. Each replay allows its own trading decisions to respond to costs; these are not deductions from fixed positions.

All fifteen years have been examined during development, so there is **no untouched holdout**. The approximately 0.04 Sharpe improvement over F remains statistically uncertain: the paired 63-day block-bootstrap interval is roughly **-0.07 to +0.15**. Consistency across periods and stress checks uses the same history and does not make those comparisons independent. I expect some selection optimism and do not regard the historical gain as an expected future increment.

I checked causality by changing and truncating future inputs and comparing earlier forecast rows and positions, including around retraining boundaries. Standalone reproduction matched the research implementation. One strict stock-order check exceeded its gross-exposure equality tolerance by a few `1e-10`; the separate AI reviewer accepted the documented solver-rounding explanation. I retained the failed receipt rather than relabelling it as a pass or changing the trading code.

## How to run

Place `strategy.py`, `gls_alpha.py`, the entire `model_f/` directory and `requirements.txt` in the original take-home folder alongside its unchanged `score.py`, `returns.csv`, `characteristics.csv` and `costs.csv`. With dependencies installed, run:

```bash
python score.py strategy
```

The strategy uses **NumPy, SciPy, scikit-learn and the Python standard library**; the original scorer additionally uses pandas. `requirements.txt` records the tested strategy dependencies. I tested Python 3.13.5 with pandas 2.2.3. The submitted package does not include the supplied CSVs or scorer, and the strategy does not load fitted models, read research files or access the network.

## Files

| File | Contents |
|---|---|
| `strategy.py` | Public entry point and the short strategy note |
| `gls_alpha.py` | Causal covariance-weighted estimator and fixed forecast combination |
| `model_f/engine.py` | Characteristic basis, causal betas and baseline risk state |
| `model_f/allocator.py` | Cost-aware allocation, constraints and solver certificates |
| `model_f/policy.py` | F2 forecast, stock books, volatility sizing and market position |
| `model_f/factor_risk.py` | Multihorizon factor-variance forecasts and risk adjustment |
| `model_f/config.py`, `model_f/__init__.py` | Frozen configuration and package initialization |
| `requirements.txt`, `README.md` | Tested dependencies and this explanation |

## How I used AI

I used AI extensively for implementation, experiment execution, literature searches and review. GPT wrote the model and verification code and carried out much of the analysis. Claude separately reproduced and reviewed the final candidate, including chronology, sleeve removal, ridge sensitivity and the numerical exception. That is review by a different AI model, not an independent human assessment or a new market sample.

My contribution was the direction, the standards and the decisions. I asked the research to follow evidence in this simulated market rather than import assumptions from my previous projects. I required experiments and acceptance rules to be stated before execution, end-to-end causality checks, preservation of failed results and a submission-ready main branch. When richer return models stalled, I pushed for further investigation rather than accepting a claimed ceiling, and required the resulting gains to be challenged with attribution and separate review.

I chose the frozen forecast combination after considering that evidence. I also chose to retain the small, explicitly identified market position. I accepted those choices under uncertainty; I did not treat a failed significance test as a pass, claim personal authorship of the AI-written code or assume the next evaluation must reproduce the backtest.

## Where I would take the research next

The remaining question is not simply whether a larger model can raise the historical maximum. I would focus on whether a new estimator, genuinely additional feature information or better conditional risk estimation improves the decisions after costs, beyond this fixed combination. The standardized-correlation result is a possible follow-up, not an untested addition to the submitted model. Any new candidate would have its own branch, predefined comparisons and a separate review before replacing this release.

I would give more weight to genuinely new evaluation data than to another small improvement on the same fifteen years. For submission, I keep the current model frozen rather than continue choosing among increasingly exposed variants.

## What could go wrong

Premia may change faster than either memory can follow, or disappear. The covariance estimate used by GLS may become misleading, and the two forecasts may cease to complement each other. The benefit depends on the regularization geometry; a compact model is not automatically robust. Factor variances and correlations may shift outside the conditions represented in the sample.

A flat or falling market can hurt the deliberate market position. Trailing betas are noisy, so neither the estimated hedge nor the historical beta guarantees compliance on the unseen continuation. Caps, solver certificates and endurance tests also cannot guarantee survival under every extreme return path. Finally, repeated research on the full sample can make the selected Sharpe optimistic. I selected a defensible configuration, not a proven future edge or a bounded-downside replacement for F.
