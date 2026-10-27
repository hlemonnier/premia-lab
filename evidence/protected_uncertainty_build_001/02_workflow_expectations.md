# Saved-ledger uncertainty reporting: workflow expectations before code

27 October 2026, Europe/Paris. This specifies implementation and verification of the unchanged `research/PROTECTED_UNCERTAINTY_PLAN.md` (SHA256 `ff7526bf7b869400274aed83e8c7f2d9a4e1f10a561da0591423e0cbafeef132`). No protected outcome has been read for this reporter's development. Root owns nomination, protected-access release and selection. This reporter cannot execute a candidate or change a selection rule.

## Modes and admission

- `validation`: exactly C06 and C09 completed protected-controller packets, from the same root-frozen validation nomination. Require its supplied SHA before parsing outcome summaries/ledgers. Full ledger indices are253 through3022 inclusive; report A `[2016,2520)`, B `[2520,3023)` and pooled `[2016,3023)`. Bootstrap only the1,007 pooled observations.
- `audit`: exactly the one selected policy's completed audit packet. Require its supplied audit nomination SHA, matching selected candidate/config and copied selection record. Full ledger indices are253 through3778 inclusive; report and bootstrap `[3024,3779)`,755 observations.
- `zero-check`: only the protected controller's completed deterministic3024-row synthetic-zero packet, with no protected access flags and no nomination. Verify metadata identifies a synthetic fixture before opening its outcome summary. Two explicitly synthetic aliases, ZERO_A and ZERO_B, refer to this one zero ledger to exercise paired reporting; this is not a C09 execution or a comparison of actual models.

Actual validation/audit execution still requires root's explicit session release. The reporter checks supplied frozen identities and does not create an approval manifest itself. Metadata mismatches, wrong modes, extra/missing candidates, duplicate/missing/out-of-order day indices, nonfinite numbers, altered consumed files, or incomplete/failed controller status fail the report. Record protected outcome-read start before parsing any real outcome summary or ledger. No fallback to a different interval or candidate is permitted.

## Expected arithmetic and reporting

Require the original daily CSV columns and complete scorer row sequence. Net must equal saved gross minus full fees. Validate masks against the unchanged protocol. Verify consumed source/summary/config/input/ledger artifacts against the controller's manifests, and preserve exact consumed files and their hashes. Large model/input arrays are not consumed by a saved-ledger report; their recorded identities and completed controller integrity checks remain provenance, not a claim that this reporter re-executed or rehashed those arrays.

Use the original hash-identified metric helper to recompute A/B/pooled or audit metrics from the corresponding daily rows and reconcile them with the controller summary. Preserve the population-standard-deviation convention, full-cost Sharpe/mean/volatility, realized market beta, drawdown, full fees and actual measured runtime. Zero-variance ratios remain null with reasons. Runtime is identified as full-replay candidate latency or period-specific instrumented scorer latency, without conflating them.

For each fixed block length21 and63, initialize `numpy.random.default_rng(20261027 + L)` and draw exactly1,000 independent sets of ordinary moving-block starts uniformly from0 through `N-L` inclusive. Draw `ceil(N/L)` starts per replicate, concatenate each block's consecutive row indices, and truncate toN. Both validation candidates use the identical sampled indices. Audit resets the same specified generator for its ownN. Preserve start matrices, seeds, algorithm, sample sizes and full replicate results.

Compute annual arithmetic net mean and net Sharpe per replicate. Report empirical linear-interpolation quantiles0.025/0.975 over finite results and explicitly count all undefined replicates. No finite results means null bounds, not zero. Paired validation differences are C06-minus-C09 using each shared sample, undefined whenever either Sharpe is undefined. The synthetic aliases use the analogous paired calculation solely to check the null path.

Cost sensitivity uses exactly fee multipliers1,1.5,2 with original gross/market/decisions held fixed. The1.0 case must reproduce the reported original full-cost metrics. Stress results do not become selectable strategies, trigger a candidate rerun, or change the primary ranking.

## Pre-access end-to-end verification

Write this contract, implement the reporter, obtain a different agent's source review, then run it only on `evidence/protected_replay_zero_001` after that complete synthetic replay passes. Expected outcome: all mean/fee/volatility/drawdown values are exactly zero; every reported Sharpe and beta is null; for each length and synthetic alias,1,000 annual-mean replicates are finite zeros and1,000 Sharpe replicates are undefined; all1,000 paired Sharpe differences are undefined; the corresponding mean percentile interval is `[0,0]` and ratio intervals have null bounds with disclosed counts. Every cost multiplier leaves zero economics and undefined ratios.

This is a complete saved-output workflow using the real reporting path, not a postimplementation isolated unit-test suite. The synthetic case cannot establish actual-market uncertainty or selection quality. Source review checks the nonwrapping block construction, shared indices, masks, identity routing, ratio logic and absence of model execution. No actual protected packet is opened until root's separate release.

Every run uses a new output directory and retains setup, exact command/rerun, code, both plans, consumed evidence identities/files, environment, results, full replicate records, block-start matrices, checks and logs. Preserve failures and unavailable outcomes. Wide uncertainty changes claim strength, never the fixed model or rule. No statistic is described as a no-overfit certificate or probability of a true winner.
