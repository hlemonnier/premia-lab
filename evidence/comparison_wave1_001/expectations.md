# Wave 1 comparison and paired uncertainty: specification before reporting code

## Fixed scope and purpose

Summarize the already completed official discovery runs C01, C02, C03 and C04. The reporting workflow may read only their saved daily ledgers, target diagnostics, configurations, result summaries and provenance manifests. It must not import a candidate, refit a model, replay a portfolio, access original market files or read validation/audit data. C08 and every later candidate remain outside this fixed report.

The recorded pooled net Sharpes are approximately 0.622, 0.638, 0.106 and 0.654. The report must preserve that weak evidence honestly. It is intended to quantify how little confidence a small observed difference deserves, not to choose a winner from an uncertainty statistic or alter the frozen future validation selection rule.

## Data and reconciliation expectations

- Require completed successful evidence (`EXECUTED_PASS_SCOPE_ONLY`, exit0, no failed checks) for exactly the four admitted candidate IDs.
- Verify each copied ledger, config and metadata file against its original artifact manifest; verify the config hash against its source manifest and the official scorer hash against the frozen authority. All four input manifests must agree on the exact discovery cache identity.
- Require each daily ledger to contain exactly one row per array index253 through2014 inclusive, in order, with finite numeric values, net equal to gross minus full cost, nonnegative full costs and the same raw market-return column across candidates. No date intersection that silently drops inconvenient rows is allowed.
- Recompute pooled daily net/gross Sharpe using population standard deviations, arithmetic annual return, annual volatility, net market beta, annual full fees, closing gross exposure and compounded-net maximum drawdown. Reconcile them with the saved summaries within fixed `atol=1e-12, rtol=1e-10`.
- Target diagnostics must contain all1763 earning-day targets253 through2015. Reconcile charged fees and target gross after excluding the free opening call. Report charged absolute turnover, net/stock exposures, pre-scale gross, gross-rescale count/fraction, minimum scale and box saturation. Preserve the fact that the last selected target is not earned by the official scorer.
- Report the four original chronological discovery blocks, intersected with scored days: `[253,504)`, `[504,1008)`, `[1008,1512)`, `[1512,2015)`. Keep the original continuous holdings; this report does not create new subperiod replays.

Any mismatch fails this reporting workflow with preserved logs and partial evidence. A candidate's weak or negative performance is not a reporting failure.

## Paired circular moving-block bootstrap, fixed before implementation

Use daily net returns from all four aligned ledgers. For each bootstrap draw and each block length, draw consecutive **circular** blocks starting at uniformly sampled original day indices, concatenate enough blocks to cover the original1762 observations, and truncate to1762. Use exactly the same sampled day-index vector for all candidates within a draw. This preserves contemporaneous covariance between strategies and within-block temporal dependence; stocks are never treated as independent draws.

Fixed settings:

- Bootstrap draws: **B =1000** for each block length.
- Block lengths: **21 and63 trading days**, both reported as predeclared sensitivity cases.
- Seed: **20261026**, with deterministic independent streams constructed from `[seed, block_length]` using NumPy SeedSequence.
- Statistics: annualized daily net Sharpe for each candidate, then paired differences **C01−C01, C02−C01, C03−C01, C04−C01, and C04−C02**. The self comparison is an explicit zero control; no unplanned pair scan follows.
- For every difference report the observed value, bootstrap mean/standard deviation, 2.5th/50th/97.5th percentiles, and the fraction of bootstrap differences strictly above zero. Save all1000 draws and the sampled-index identity for each block length. No resampling choice, seed or block length is selected after seeing these outputs.
- Require all bootstrap statistics to be finite. Require the self comparison to be exactly zero on every draw and the draw-index matrices to have shape `(1000,1762)` with indices in the declared range. Check paired indices are shared by construction. Save the full index matrices for exact local inspection; their seed, generation rule and hash make them reproducible if large arrays are excluded from Git.

These are approximate conditional uncertainty diagnostics, not posterior probabilities, formal proof of alpha, guarantees of coverage under regime change or estimates of hidden-continuation performance. Circular blocks create an artificial end-to-start join. The series may be nonstationary, the two block lengths do not exhaust dependence choices, and the report does not correct for all prior research selection. The fraction positive is explicitly labelled as a bootstrap sign frequency, never as the probability that a candidate truly wins. A percentile interval containing zero must not be interpreted as proof of equivalence. A nonzero interval must not override the design's untouched validation/audit gates.

## Artifacts and execution

Write `tools/compare_discovery.py` only after this specification. Use an E2E reporting run into `evidence/comparison_wave1_001`: freeze the runner, this plan and all selected input files; record hashes, original and exact frozen rerun commands, environment, expectations, checks, actual results and logs. Produce compact CSVs for pooled metrics, fixed blocks, diagnostics and bootstrap differences; a Markdown report must distinguish observed results from bootstrap qualifications. Preserve inputs unchanged and reject an existing output directory. No isolated unit tests are added after implementation.
