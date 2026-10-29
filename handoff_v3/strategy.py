"""V3: characteristic factor-risk strategy with adaptive premia, cost-aware execution and a fixed
market position. Draft note, 29 October 2026; candidate under review.

WHAT I BUILT
Forecast: two causal pooled ridge learners on V2's 27 columns (13 standardized characteristics,
their centered squares, trailing beta), half-lives 1,008 and 252 days. The linear coefficients
are the average of the two; squares and beta use the slow fit. Row t uses X[t-1].
Sizing: a virtual reference book (V2 allocator, gamma 200, 5% caps) whose recent versus long-run
volatility sets a multiplier a in [0.5, 2]. The traded stock book is the same allocator solved
against its own drifted holdings with gamma 200/a and caps 0.05a, beta-hedged to zero on raw
trailing betas. Every solve is certified; failures fall back to a certified diagonal problem.
Market position: on top of that book, +0.05/N in every stock, a deliberate equal-weight market
holding. This is market carry, not stock selection; POLICY.sleeve = 0.0 removes it.

EVIDENCE (supplied scorer, full fees; all rows already examined during research)
                      net Sharpe   beta   cost/yr   first/second half
  V2                    1.243      0.047   0.18%
  stock book alone      1.340      0.053   0.24%     1.12 / 1.63
  with market sleeve    1.445      0.103   0.25%     1.19 / 1.76
The sleeve's +0.105 is market exposure. The simulated market returned 14.5%/yr (Sharpe 1.02).
A common-market-mean sensitivity, holding measured betas, volatility, nonmarket means,
positions and costs fixed, favors the no-sleeve book below about 4.4% a year (at a zero
market mean: 1.12 with the sleeve, 1.17 without). This is arithmetic, not a replay on an
altered market. Variants were pre-registered in waves of five with the 0.05 fixed in advance,
but all history is exposed development data: causality checks pass, yet future Sharpe and
beta remain unknown.

WHAT COULD GO WRONG OVER DECADES
A falling or flat market removes the sleeve's contribution and the 0.05 of beta carried
implicitly by raw-beta hedging. The 252-day learner can chase short-lived premia. Raw betas
are noisy, so realized beta grows with book size. Costs are small but rise with turnover.

CONTRIBUTIONS
[To be written by the applicant. Research and selection of this policy: GPT. Reproduction,
audit and production integration: Claude. See verification/V3_INTEGRATION_RESULTS.md.]

Required files: model_v3/__init__.py, engine.py, allocator.py, policy.py. NumPy and the
Python standard library only.
"""

from model_v3 import engine as _engine
from model_v3.policy import ScorePolicy

_CONFIG = {
    "alpha_half_life": 1008.0, "ridge": 0.1, "min_training_days": 126, "feature_clip": 4.0,
    "beta_window": 252, "factor_half_life": 126.0, "specific_half_life": 126.0,
    "specific_shrinkage": 0.2, "variance_floor": 1e-6, "factor_risk_scale": 0.3,
    "risk_aversion": 200.0, "cost_horizon": 20.0, "weight_cap": 0.05, "gross_cap": 5.0,
}

_engine.configure(_CONFIG)
POLICY = ScorePolicy(dict(_engine.CONFIG), sleeve=0.05, outer_gross_cap=5.0)


def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)


def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
