"""N0: shared characteristic premia with a bounded own-residual correction.

I treated the 13 characteristics as candidate factor loadings, not economic
labels. Linear and squared exposures describe shared market-residual return
variation. To turn that representation into a causal forecast, I estimate
premia from matured observations using a pooled 27-column design that also
includes trailing beta. The original ridge estimator has long and short
memories; only its linear coefficients combine both memories.

I then separated two questions: whether factor risks vary predictably, and
whether correlated estimation errors should have equal influence. I retain
bounded multihorizon factor-variance adjustments and average the original
return forecast 50/50 with a covariance-weighted, coefficient-wise-regularized
estimate. Pure GLS performed worse than the combination. Matched controls
showed that weighting and shrinkage work jointly, not independently.

Cross-stock residual links failed after costs. Their own-history control N0
was more promising. I keep sign-stable, thresholded own-lag slopes from 504
matured dates, refit every 126 days from target row 505. The correction is
projected off the existing design, halved and capped at 20% of core alpha RMS.
The screen is heuristic, and the mostly reversal-like selected effects change.

I selected the frozen N0 own-history correction on top of the GLS ensemble because its historical gain at the supplied fees survives removing the explicit market sleeve and the largest signal sources. Its added value remains statistically uncertain; the model was discovered as a control, and selection on the same exposed history can overstate its future performance.

The cost-aware factor allocator uses an estimated-beta hedge, limits and
reference-book sizing. I add a deliberate 0.05 equal-weight market position;
it is carry, not stock alpha. Its internal stock-book cost objective is an
approximation to combined-book trading, which the original scorer charges.

Supplied-history net Sharpe is 1.55078, beta 0.09329; without the market position,
Sharpe is 1.43669. The gain over GLS is only 0.01756 and its uncertainty interval
includes zero. All fifteen years are exposed development data. Unstable
residual effects, changing premia/covariance, turnover and market carry can
erase the gain. Causality checks do not establish future performance.

I directed questions, required causal evidence and made selection decisions.
AI tools implemented and tested the code and drafted analyses. A different AI
reviewed GLS, not this N0 extension; I claim no separate N0 reviewer sign-off.
I have not measured this update on the evaluator's hidden continuation.

Run with the unchanged scorer and data. All numerical components are internal to the single
model_n0/ package; N0 is the only exposed strategy. NumPy, SciPy and scikit-learn are required; the scorer
also needs pandas. No trained file, research checkout or network is needed.
"""
from model_n0 import N0Policy

POLICY = N0Policy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
