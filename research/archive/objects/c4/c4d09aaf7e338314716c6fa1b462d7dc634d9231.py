"""GLS ensemble: two causal return estimates with factor-risk allocation.
Hugo Lemonnier, October 2026.

I treated the 13 characteristics as shared return and risk exposures rather
than unrelated stock signals. I use their standardized levels, centred squares
and trailing beta to estimate slowly changing premia across all stocks. My F2
baseline uses pooled ridge learners with 1008/252-day half-lives, averaging the
linear coefficients while retaining the slow fit for squares and beta.

I selected a fixed 50/50 combination of two causal estimates of the same return premia: the original F2 forecast and a covariance-weighted, coefficient-wise-regularized forecast. The historical gain survives removing the explicit market sleeve and increasing trading costs, but its added value is not statistically established.

The second estimate weights matured observations by covariance known before
their outcomes and profiles a daily nuisance intercept. Every forecast row t
uses only rows before t. The blend was fixed before testing: pure GLS scored
below F, while the combination scored 1.53322 versus 1.49344. Attribution tests
support weighting and coefficient-wise shrinkage acting jointly, not a general
advantage for GLS independent of its penalty.

I retain F's bounded Gamma factor-variance forecasts, existing correlations
and specific risk, certified cost-aware allocator, estimated-beta hedge and
virtual-book sizing. The stock allocator uses its own drifted holdings; I add
a fixed 0.05 equal-weight market position afterward. This is explicit market
carry, not stock alpha. Without it, net Sharpe is 1.41900 and beta 0.044; with
it, beta is 0.094 and annual costs are 0.231% on the supplied history.

I directed the research, required causal tests and attribution, and selected
this frozen combination after review. GPT implemented the models and checks;
Claude separately reproduced and reviewed them as a different AI, not a human.
I accepted the documented tiny stock-order solver discrepancy without changing
the solver or relabelling the failed assertion as a pass.

All fifteen years were exposed during development. Incremental-performance
intervals include zero, and repeated selection can inflate the score. Premia,
covariances and market carry can change; the forecast combination may stop
helping. I do not assume future outperformance, beta compliance or a downside
floor. Extreme unseen returns can cause ruin despite the sizing safeguards.

Requires gls_alpha.py, all six adjacent model_f helpers, NumPy, SciPy and
scikit-learn. requirements.txt pins tested versions; the original scorer also
needs pandas. No research checkout, saved model, data-file read or network is
required by the strategy. The supplied CSVs and scorer are not redistributed.
"""
from gls_alpha import CandidatePolicy

POLICY = CandidatePolicy()

def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)

def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
