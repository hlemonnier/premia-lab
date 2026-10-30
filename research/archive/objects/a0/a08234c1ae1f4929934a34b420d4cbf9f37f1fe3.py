"""GLS candidate: covariance-aware regularized return estimation with F risk.

The characteristics and their squares describe useful shared return/risk
structure. The frozen GLS learner retains the same 27-column return design,
but weights matured cross-sections by lagged factor-plus-specific covariance.
It profiles a daily nuisance intercept and uses coefficient-wise ridge shrinkage.
Slow/fast EW learners (1008/252-day half-lives) are combined as before, and their
prediction is blended 50/50 with F2. Covariances and labels precede the target.

Portfolio construction remains F: causal three-predictor Gamma adjustments of
factor variances, a certified factor-risk allocator with linear trading costs,
estimated-beta hedging, position limits and virtual-book sizing. The explicit
0.05 equal-weight market holding is carry, not stock-selection alpha.

Historical net Sharpe was 1.53322 versus F 1.49344. Matched controls support
covariance weighting and coefficient-wise regularization acting jointly, not a
penalty-independent GLS advantage. The gain survives removal of the explicit
market holding and higher fees. All fifteen supplied years were examined during
research; incremental-performance intervals include zero. Neither causal code
nor low model complexity establishes freedom from selection overfit. Future
factor premia, correlations and variance dynamics can change; estimated-beta
hedging does not guarantee the future beta condition and leverage entails ruin
risk on sufficiently extreme unseen paths.

Hugo directed the research and required causal evaluation and attribution.
AI assistants implemented the models and verification. Separate reviewer
sign-off is not implied by this note. This is a frozen candidate, not an automatic
replacement for the selected F release.

Required: gls_alpha.py, the adjacent model_f package, NumPy, SciPy and
scikit-learn. requirements.txt pins the tested versions. The supplied scorer
also needs pandas. No data files, fitted models, caches or network are read by
the strategy. The original scorer and user data remain external to this package.
"""
from gls_alpha import CandidatePolicy

POLICY = CandidatePolicy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
