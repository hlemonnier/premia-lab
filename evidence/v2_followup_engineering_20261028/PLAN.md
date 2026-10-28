# V2 follow-up engineering review: prospective verification plan

28 October 2026, Europe/Paris. Reviewer: independent allocator/engineering agent.
Reviewed commit: `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`.

## Scope and fixed workflow

Re-execute the original independent complete-scorer synthetic workflow that
previously demonstrated the restart-state and characteristic-layout defects.
Reuse its `run_e2e.py` byte for byte; do not edit the production package or write
new unit tests. This workflow constructs deterministic two-history inputs,
executes ten fresh worker processes and twelve full scorer runs, and preserves
forecasts, positions, drift/cost ledgers and source/input identities.

Source snapshot: `/workspace/scratch/a83c191d516f/v2-followup-snapshot`.
Original workflow: `evidence/v2_causality_review_20261028/run_e2e.py` in the main
local repository. Original scorer remains unchanged. New run directory is
`evidence/v2_followup_engineering_20261028/run_001`.

## Expectations fixed before execution

1. All worker processes exit zero and produce finite, nontrivial trading runs.
2. Repeated fresh runs have bitwise-identical forecasts, positions and economic
   ledger fields.
3. Replacing the future after row 300 leaves protected forecasts, positions and
   ledger fields bitwise identical; the future stimulus changes later forecasts
   and targets. This must hold for ordinary layout and Fortran R/X layouts.
4. Truncating the history preserves the common forecasts, targets and economic
   ledger prefix.
5. A scoring session on a different same-length starting history reproduces
   its cold control, both for the custom-start case that failed in the previous
   review and for the ordinary default-start control.

This fixes expected outcomes before executing the workflow on the new package.
The original workflow records equality statistics but does not itself turn an
equality failure into a nonzero controller exit. The independent readback must
inspect every expectation, not infer success from exit code alone.

## Metadata caveat and limits

The unchanged old runner writes its old pinned commit as a literal string in
`environment.json`. That stale metadata will be explicitly superseded by this
plan and a separate review identity record; the copied source hashes identify
what actually ran. The old literal must not be mistaken for the executed source.

This workflow uses the default packaged policy and 340 synthetic rows. It does
not test the beta-correction option, which requires more than 504 rows. The
separate causal-beta reviewer owns that flags-on workflow. The coordinator owns
actual candidate ledgers and statistical readback. No new forecast candidate,
parameter search, or modified strategy is executed here.

Also inspect the affine beta-target dual algebra, final certificate enforcement,
gross-cap transformation, and supported degenerate inputs from source. Report
source-derived defects separately from executed failures. Rerun Claude's existing
allocator suites unchanged only if useful to resolve a specific remaining claim;
record the exact additional command before executing it.
