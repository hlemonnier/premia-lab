"""F: causal characteristic-factor allocation with multihorizon factor risk.

The 13 characteristics and their squares describe a useful shared return/risk
structure. Forecasts use pooled causal ridge learners with half-lives 1008/252
and a trailing-beta column. F leaves that alpha unchanged and predicts bounded
corrections to the variances of the 26 characteristic factors. A shared Gamma
GLM with three multihorizon predictors is refitted every 126 days using matured
labels only. The old factor correlations and specific variances are retained.

Positions come from a certified diagonal-plus-low-rank risk allocator with
linear transaction costs, estimated-beta hedge, caps and a virtual-book risk
multiplier. A fixed 0.05 equal-weight market position is explicit market carry,
not stock alpha. The observed supplied-sample beta is about 0.101, not a promise
that future beta remains below 0.2.

Development Sharpe was 1.49344 versus V3 1.44473. All supplied years have been
exposed to research; bootstrap intervals for incremental performance include
zero. Do not interpret causal code or this historical score as proof against
overfitting. Unknown future changes in factor premia, volatility, correlations
or market carry can remove the advantage; estimated-beta hedging is imperfect.

Hugo directed the research toward useful ML and insisted on causal evaluation.
The AI assistant implemented the models, ran comparisons and authored the code
and evidence. No independent-person review is claimed.

Requires the adjacent model_f package and NumPy, SciPy, scikit-learn (tested
with 2.3.5, 1.17.0, 1.8.0 respectively). The supplied scorer also uses pandas.
No source data, trained-model file, local research repository or network is needed.
"""
from model_f.factor_risk import FactorPolicy
POLICY = FactorPolicy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
