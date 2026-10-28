"""Selected causal additive characteristic strategy (C09).

Development note, 27 October 2026; frozen before the sealed internal audit.
Discovery suggested slowly changing characteristics, unstable marginal linear
relationships, and some persistent nonlinear responses. These observations do
not identify the simulator's mechanism. More flexibility did not consistently
help after costs: the fixed local-hinge extension failed its fixed parent-comparison
criterion. Twelve discovery configurations led to two frozen validation nominees.
The prior rule selected this longer-memory additive model over the more elaborate
covariance model: pooled validation net Sharpe 0.659 versus 0.399 across 1,007
scored days. Its two block Sharpes were 0.366 and 0.936, net market beta 0.00586,
and annual full trading costs 0.209%. These are development/selection observations;
we do not claim statistically established superiority or future profitability.

The forecast jointly fits all 13 normalized linear characteristics and their
13 centered squares, with ridge 0.1 and exponential forgetting of half-life
1,008 days. Each published cross-section is normalized and clipped using that
panel alone. There is no feature selection or fixed regime date. Forecast row t
uses X[t-1]; its newest training pair is X[t-2] against R[t-1], with the label's
market beta estimated before that return. Predictions remain zero until 126
pairs have matured. Sufficient statistics have fixed dimension and the learner
continues updating from past data throughout evaluation.

The portfolio estimates market betas and diagonal residual variances from the
last 252 days, with variance shrinkage and a floor. A scalar-dual convex allocator
balances forecasts, risk, and absolute changes from the actual drifted holdings,
subject to an estimated-beta hedge and 1% per-stock limits. A 100% gross cap may
scale the solution; this preserves the estimated hedge but is an approximation
to the fully gross-constrained optimum. Costs amortized over 20 days guide trade
decisions; evaluation charges full actual fees, including reversals and closing
trades under the supplied scorer. Estimated neutrality does not guarantee future
realized beta. Causality perturbations and full 25,200-row runtime workflows were
executed; finite engineering checks do not certify an absence of overfitting.

AI performed the literature search, implementations, experiment execution,
independent agent reviews, evidence reconciliation and packaging. The user
reported noticing the same broad early patterns, challenged overfit/lookahead
risk, and requested source-grounded ideas, subagents and continued experiments.
Those are the recorded human contributions; no unreported human implementation
or independent empirical discovery is attributed. The selection and detailed
evidence are retained in the private research repository.

Over decades, long memory can adapt too slowly, response shapes and market betas
can change, omitted common residual risks or interactions can matter, and trading
costs or tail losses can overwhelm a small edge. The fixed caps limit exposure
but cannot guarantee solvency under every possible future return. The tested
histories do not resolve these risks.

Required helper package: model/__init__.py, model/strategy.py and model/portfolio.py.
Helpers are unchanged research engine bytes; the literal configuration below
overrides their development defaults. NumPy and the Python standard library are
sufficient for this strategy. The supplied scorer imports forecast and rebalance
through these direct aliases; no research files or fitted binaries are needed.
"""

from model import strategy as _engine

_FROZEN_CONFIG = {
    'candidate_id': 'C09_additive_long_memory',
    'basis': 'additive',
    'alpha_half_life': 1008.0,
    'ridge': 0.1,
    'min_training_days': 126,
    'feature_clip': 4.0,
    'risk_window': 252,
    'risk_min_days': 20,
    'variance_shrinkage': 0.2,
    'variance_floor': 1e-06,
    'risk_aversion': 1000.0,
    'cost_horizon': 20.0,
    'weight_cap': 0.01,
    'gross_cap': 1.0,
}

_engine.configure(_FROZEN_CONFIG)
forecast = _engine.forecast
rebalance = _engine.rebalance
