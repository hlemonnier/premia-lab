# Score opportunity readback: prospective observational specification

28 October 2026, Europe/Paris. Owner: score_opportunity_audit.

## Question and scope

Prioritize the next official-scorer experiment using already exposed return
ledgers, without scoring or selecting a new predictive policy. The original
brief explicitly allows tuning over the supplied fifteen years. These data are
development history; none of the named discovery/validation/audit segments is
new confirmation now.

Pinned source is `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`, snapshot
`/workspace/scratch/a83c191d516f/v2-followup-snapshot`. Inputs are the 29 files
`research/v2/results/ledgers/net_*.npy`, `results/comparison.json`, corresponding
`variant_*.json`, four `results/candidates/*.json`, and exploration `variants.py`
and `strategy_v2.py`. Input file SHA256 and byte counts are recorded before the
calculation in `input_manifest.json`. Earlier C01-C12 outcome metadata is read
to identify experiments already tried, not rescored or ranked anew.

## Fixed methods, chosen before calculation

1. Check each ledger has shape (5,3526), finite values, identical day rows
   253..3778 and market series, and net = gross return minus paid fees.
   Day identities are exact; market and net/gross/fee reconciliation tolerance
   is absolute1e-12, matching the prior independent ledger readback.
2. Compute net/gross Sharpe with population standard deviation, annual arithmetic
   means and volatility, annual fees and beta on all rows. The unchanged-holdings
   fee-removal counterfactual is gross Sharpe minus net Sharpe, not an upper bound
   on every possible trading-policy change.
3. Compute the same summary on fixed prior stage masks [253,2015), [2016,3023),
   [3024,3779). The two boundary observations remain full-sample only.
4. For all 29 policies, report net-return correlation with V2 and coefficients of
   the descriptive full-sample regression net_j = constant + b*net_V2 + error.
   Report residual mean and standard deviation, not a selected optimal portfolio.
5. The only reference mixtures are beta_feat/fr_beta, decor_beta/fr_beta and
   fr_beta_phi03_x5/C09_engine. For each, compute the historical equal-risk
   mixture 0.5*net_a/sd_full_a + 0.5*net_b/sd_full_b, and its gross-return and fee
   components under those same fixed scalars. Full-sample standard deviations
   are hindsight normalization: these are explicitly noncausal descriptive
   series, not scored strategies, not executed blends, and not valid forecasts
   of future Sharpe. Report all three pairs, stages, pair correlation and each
   leg's risk/return; do not choose weights or select pairs after seeing scores.
   Also report fixed raw 50/50 net series for transparency about scale mismatch.
6. For V2 only, inspect conditional moments by lagged EW gross squared return
   with half-life63 (one fixed timescale) and full-sample quintiles of its
   past-only estimate, excluding first126 observations from this diagnostic.
   Quintiles use hindsight thresholds and are descriptive. Save the raw lagged
   estimate and conditional gross/net means, squared returns and fees. Do not
   evaluate a volatility-scaled policy, optimize a coefficient, or infer that
   this bucket result alone establishes timing alpha.

## Interpretation and validation

The purpose is economic prioritization, not promotion of any reference mixture.
A useful complementarity finding requires a constituent with distinct historical
returns and an improvement not wholly isolated to a single stage. It motivates
an exact scorer replay of a causally defined blend with full drift and trading
costs; it does not establish that replay result. Report disappointing results
unchanged. Cost savings of only a few hundredths of Sharpe would move standalone
cost tuning down the queue; they do not invalidate joint signal/trading changes.

The script must check shapes and identities, preserve exact inputs/source hashes,
command, environment, complete summaries and diagnostics. Parent/peer source
review will occur before execution. No postimplementation unit test is written.
This is an end-to-end saved-output analysis, with no strategy source modified.
