# Reporting uncertainty without changing selection

Prospective reporting plan, 27 October 2026, Europe/Paris. Written before validation or audit outcome access. This analyzes the saved outputs of the already frozen policies; it admits no new candidate or retuning. The protocol's pooled validation net-Sharpe ranking and beta eligibility remain unchanged.

## Fixed report

Report each admitted candidate's validation A, B and pooled metrics, with the pooled score calculated from daily rows. The sole selected policy later receives the same report on its 755 audit observations. Preserve full original fees, realized market beta, mean/volatility, drawdown and actual runtime alongside Sharpe. The audit cannot select a different policy.

For uncertainty use an ordinary paired moving-block bootstrap of the saved daily gross/cost/market observations. Block lengths are fixed at 21 and 63 observations; draw contiguous blocks uniformly from all valid nonwrapping starts, concatenate until reaching the original sample length and truncate the last block. Use exactly 1,000 replicates for each length and `numpy.random.default_rng(20261027 + block_length)` separately for validation and audit. Both validation candidates use the same sampled row indices. These are dependence-aware reporting resamples, not shuffled training/validation folds and not new model executions.

For each candidate report the empirical 2.5% and 97.5% quantiles of annualized arithmetic net mean and annualized net Sharpe. For validation also report the paired C06-minus-C09 Sharpe-difference quantiles. Use the original population-standard-deviation convention. If a ratio is undefined in a replicate, count and disclose it; do not invent a numeric zero or conceal a lack of finite replicates. A deterministic synthetic zero-return check must produce undefined ratio reporting.

Report cost sensitivity at exactly 1.0, 1.5 and 2.0 times the saved fee series, holding the recorded decisions fixed: `net_k = gross - k*fee`. This is an ex-post cost-estimation stress, not a rerun with a different allocator or an additional selectable pipeline. The original 1.0 cost case remains the sole selection input. No new cost grid is admitted.

## Interpretation and safeguards

The resampling assumes the observed dependence and distribution are informative; the two block lengths expose some sensitivity rather than proving the right dependence model. A development or selected-validation confidence range is conditional on the exposed research path and does not correct all model-selection optimism. The single fixed audit is a separate later check, but a short audit cannot guarantee future stationarity or the employer's hidden continuation. Do not convert bootstrap frequencies into a probability that a candidate is the true winner or publish a numerical no-overfit certificate.

Record source ledger hashes, exact masks, seed, algorithm, replicate counts, undefined counts and full machine-readable results. Independent review must confirm that no result-driven rule change occurred. Failure or wide uncertainty changes the strength of the claim, not the frozen model or selection rule.
