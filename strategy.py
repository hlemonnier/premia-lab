"""GLS ensemble: two causal return estimates with the unchanged F risk model.

The 13 characteristics, their centered squares and trailing beta describe useful
shared return/risk structure. F2 estimates their premia using pooled ridge
learners with 1008/252-day half-lives. The second estimator weights each matured
cross-section by its lagged factor-plus-specific noise covariance, profiles a
daily nuisance intercept and uses coefficient-wise ridge shrinkage. Covariance
inputs precede their training labels; predictions use only earlier source rows.

We selected a fixed 50/50 combination of two causal estimates of the same return premia: the original F2 forecast and a covariance-weighted, coefficient-wise-regularized forecast. The historical gain survives removing the explicit market sleeve and increasing trading costs, but its added value is not statistically established.

The blend was fixed before testing; pure GLS scored below F. Matched controls
support covariance weighting and coefficient-wise shrinkage acting jointly,
not a penalty-independent GLS advantage. No reviewer-tested ridge variation
has replaced the original configuration.

Construction remains F: bounded three-predictor Gamma adjustments to factor
variances, unchanged correlations/specific risk, a certified cost-aware
allocator, estimated-beta hedge, limits and virtual-book sizing. A fixed 0.05
equal-weight market sleeve is explicit market carry, not stock-selection alpha.

Development net Sharpe was 1.53322 versus F 1.49344, with beta about 0.094.
All fifteen years were exposed during research. Incremental-performance
intervals include zero; causal code and small model size do not rule out
selection overfit. Premia, volatility, correlations and market carry may change.
Neither future outperformance, beta compliance nor a downside floor is assured;
extreme unseen returns can cause ruin despite historical sizing checks.

Hugo directed the research, required causal testing and attribution, and chose
this frozen ensemble after review. GPT implemented the model and verification;
Claude, a different AI model, reproduced and reviewed it and accepted the tiny
stock-order solver discrepancy. This is not an independent human review or a
new market sample. Selection under uncertainty is not a statistical-test pass.

Requires gls_alpha.py, the adjacent model_f package and NumPy, SciPy and
scikit-learn; requirements.txt pins tested versions. The original scorer also
needs pandas. No research checkout, data-file read, saved fitted model,
prediction cache or network is required by the strategy.
"""
from gls_alpha import CandidatePolicy

POLICY = CandidatePolicy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
