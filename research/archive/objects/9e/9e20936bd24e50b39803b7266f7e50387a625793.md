# Independent score opportunity challenge — 29 October 2026

Owner: score2_challenge. This is a read-only diagnostic and prospective proposal,
not authorization to run a new trading policy. Root approval is required before
implementation or new actual-market scoring.

## Objective and facts already available

The original README defines the objective as future net Sharpe and requires
whole-period net-return beta to the equal-weight market below 0.2. There is no
other portfolio concentration/leverage constraint apart from avoiding ruin.
The equal-weight market is replicable with the supplied stocks, paying their
actual per-stock costs. There is no separate costless index instrument.

The completed research leader is F2 + VTvol, full-development net Sharpe
1.318334966090838 and realized beta 0.05272035468. All original historical stages
have already been exposed to development. They are not new validation samples.
Prior beta correction and explicit-target experiments remain rejected under
their recorded rules; the present review will not change their disposition.

## Allowed diagnostic before any new numbers

Read the existing joint daily ledger and supplied static stock costs. Reconcile
its published summary using exactly its scoring rows, then calculate only:

1. Mean, variance and covariance of the existing joint net return and same-row
   equal-weight market return, with full and the original three stage masks.
2. The local derivative of gross-cost-omitted portfolio Sharpe with respect to
   adding a small fixed market exposure, evaluated at zero addition. This is a
   descriptive spanning diagnostic, not an executed score or admissible policy.
3. The cost summary of the equal-weight stock basket, including exact average
   cost and simple deterministic turnover bounds. Do not infer actual net costs
   from market returns; actual drift and stock-level netting require a replay.

No coefficient search, optimized in-sample market weight, saved-net-series
candidate Sharpe, strategy execution, factor refit, or threshold fitting is
allowed in this diagnostic. Any new candidate will have one exact specification
and prospective E2E expectations before code. Record consumed-file hashes and
the exact command. Preserve negative findings.

## Independent challenge

Assess whether the unused beta allowance has positive marginal score value,
without treating unused risk capacity as a reason to fill it automatically.
Compare expected implementation value of one simple market sleeve with further
nonlinear forecasting and cost-aware sizing. Read primary work on portfolio
combination and conditional factor allocation. Any extrapolation from external
markets to the supplied simulator must be labelled as a hypothesis.

The candidate proposal may retain exactly one fixed additional market exposure
of +0.05 to the existing F2+VTvol book, subject to a whole-book gross cap and the
existing beta admission condition. This is a hypothesis to be reviewed, not an
outcome-selected target or an authorization to run. A dynamic market-premium
estimator is not allowed in this bounded proposal because its estimation and
turnover risks add several unneeded choices.

## Later review role

Independently inspect other owners' prospective harnesses and implementations
for causal indexing, actual holdings/costs, restart behavior, objective units,
and faithful scorer use. No edits to other owners' files, original source,
production strategy or repository refs. Report static review separately from
executed verification.
