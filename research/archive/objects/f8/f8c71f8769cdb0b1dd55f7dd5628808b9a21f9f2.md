# Separate reviewer request — frozen GLS release

Status: **PENDING — no separate reviewer assessment has been performed in this release session.**
This file is a review brief, not a sign-off. A second implementation or same-assistant
assessment is not an independent-person/agent review.

## Exact scope

Repository: hlemonnier/continual-research-takehome.
Branch: research-gls-release-20261029.
Frozen packaged source commit: ea937ee69983dd1157b1ffdf12cce5d2149d738d.
Original GLS module Git blob: f26b3c5b8c8578525af7db19f01898140b9b7fc7.
F helper tree: d717841faec75186020c6dae18d0fc282c5dca4e.
Main remains the F submission at ebf1ff1636e263d5fa98ce724cf65dc912d3d0c3.

Review `handoff_gls/` without retuning. It should contain root strategy.py,
gls_alpha.py, README.md, requirements.txt and the six model_f helper files.
The original source dataset is not included: use the evaluator-supplied CSVs
whose hashes are in the evidence archive. No external data or API is required.

## Questions to answer independently

1. Derive the information chronology of every GLS design, residual label,
   covariance weight, factor multiplier, intercept projection and prediction.
   Check the target row, refit boundaries, final source row and session reset.
   In particular, verify that the precision for a label does not observe that
   label before choosing its weight. Distinguish the daily GLS update from the
   126-day Gamma risk refit schedule.
2. Verify that the standalone adapter invokes exactly the frozen GLS policy;
   inspect module identities, allowed dependencies and absence of research,
   saved-model, input-file or network coupling. Reproduce the original scorer
   from a fresh directory, not a shared process importing the research modules.
3. Audit the actual 25,200-day repeated-history run and late-mutation receipt.
   Check memory and BOTH average and worst-call timing, and distinguish an
   operational endurance run from genuinely unseen economic evidence.
4. Inspect the strict stock-permutation failure. The unmodified solver's gross
   exposure differs by2.8919e-10; return/fee errors are below1e-10. A separate
   verification-only KKT refinement reduces the discrepancy. Decide whether
   this is an acceptable documented numerical exception; do not relabel the
   original failed assertion as passed or use refined economic scores.
5. Assess what the matched GLS attribution controls actually establish. Weighting
   and coefficient-wise shrinkage interact; isotropic weighting underperforms
   its control without the sleeve. Distinguish positive historical evidence
   from expected future gain and from statistical significance.

Read the code first and retain your own calculations. The prior reports contain
claims to verify, not ground truth. Preserve the supplied scorer unchanged.

## Required return

Write a separate signed/attributed assessment naming the exact source commit,
reviewer identity/type, commands, environment, tests actually executed and any
unexecuted checks. List findings by severity with file/line references. Give
separate verdicts on causal correctness, technical viability, numerical
exceptions and model-selection judgment. Record whether you recommend keeping
F or selecting GLS; do not merge, retune or submit anything as part of review.

The review packet contains source, release checks, logs, daily original-scorer
rows, fit records, hashes, the attribution report and its failed-oracle records.
Large input, forecast and target tensors are regenerable and excluded. See
REPRODUCE.md for exact rerun commands.
