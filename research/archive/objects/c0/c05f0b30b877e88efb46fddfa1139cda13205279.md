# Independent preflight review

## Review scope and current status

Reviewed `PREFLIGHT_PLAN.md`, `tools/preflight.py`, frozen runners and evidence for `preflight_001` and `preflight_002`. This is an independent code/artifact review, not another strategy implementation or an additional E2E execution. No market outcomes after the first 504 array rows were examined; the full source files were streamed only for cryptographic identity checks.

At this review's initial checkpoint, run 002 was still in progress and had not produced its final summary or scoring outputs. The completion addendum below records subsequent inspection of the completed evidence; completion is not inferred merely from code review.

## Findings

### Source identity: independently verified

The reviewer independently computed SHA-256 for all 12 original source files and for each corresponding decompressed ZIP member. Every current source file matched both its original archive member and the SHA-256 recorded in `preflight_002/source_manifest.json`. The supplied README, scorer, strategy scaffold, examples, CSVs and figures are unchanged. Figures were hashed as bytes, not viewed.

This strengthens the runner's recorded archive-size/CRC comparison. It does not establish byte identity with remote Drive CSV files, which remains correctly unverified.

### Data-access restriction: respected by the runner

The complete returns/characteristics files are used for dimensions, exact identifiers/order, numerical finiteness and source hashes. The script does not compute full-sample return moments, correlations, predictive associations or feature distributions. Only the first 504 rows feed the supplied scorer and economic outputs. The published full-sample figures are not opened.

Reading the full files for those declared structural checks is within the written preflight scope. It should not be described as never accessing later file bytes; the accurate claim is that later **economic outcomes are not analysed**.

### Ordered reshape and prefix integrity: sound design

The code checks day labels 1 through 3780; returns columns must be unique; costs must have exactly the same stock ordering. Characteristics are checked row by row against the Cartesian day-major/stock-major order induced by returns, and their thirteen feature columns must appear in the declared order. This directly addresses the original loader's otherwise-unchecked reshape assumption.

The prefix is written as CSV, loaded by the original scorer, and compared numerically against its original values, including characteristics and costs. The explicit numerical equality checks guard against unintended changes from the output precision settings. No independent custom backtest is substituted for the supplied evaluator.

### Replay convention: matches the supplied code

For 504 data rows and `START=252`, the expected output is 250 scored rows: array indices 253 through 502, corresponding to CSV day labels 254 through 503. The first selected book is formed after array row 252; the first trade is free; final array row 503 is not earned; closing costs at array row 502 remain included. The planned row labels are correct.

Equal-weight gross exposure of one and net beta near one are appropriate smoke expectations. The strategy's assignment beta failure is explicitly labelled `FAIL_BY_DESIGN`, while candidate validation is `NOT_RUN`. This is an infrastructure check, not evidence for an admissible research strategy.

### Runtime and repeatability claims: appropriately limited

The runner sets six thread controls before numerical-library imports and records one-CPU affinity. Two executions of the stateless supplied equal-weight example occur in the same process; only economic columns are compared exactly, with timing differences allowed. This supports the stated **in-process** repeatability claim. It is not a fresh-process candidate-state, long-horizon, or complete-environment verification.

The environment correctly records missing `cvxpy` and `lightgbm`; their absence does not invalidate a numpy/pandas equal-weight smoke run but prevents claiming readiness for every allowed submission dependency.

### Evidence issue requiring an addendum for failed run 001

Run 001 correctly records `FAIL`, exit code 1 and the overbroad 14-file inventory failure before any market-data analysis. Its frozen runner and expectations are preserved. However, its stored `rerun.txt` points at the subsequently changed live `tools/preflight.py`; that command now encounters the new mandatory archive argument instead of reproducing the original failure.

Invoking the frozen `preflight_001/runner_used.py` directly is also insufficient: that older code locates `PREFLIGHT_PLAN.md` relative to its parent directory, so its preserved location changes that dependency path.

Preserve the historical artifacts unchanged. Add explicit reconstruction instructions that copy the frozen run-001 runner into `tools/preflight.py` inside a new temporary reproduction directory and copy run-001 `expectations.md` to that directory's `PREFLIGHT_PLAN.md`. Execute that frozen runner against the original source with a fresh output directory. The source manifest identifies the original 14-file inventory, including incidental files. If those incidental files are no longer present, reproduce their recorded presence in a separate source copy rather than changing the pristine source.

The supplemental `evidence/preflight_001/REPRODUCE_FAILURE.md` now provides that layout, setup and exact command. It copies the twelve verified source members into a temporary tree and adds two harmless incidental fixtures, so reproduction does not depend on historical transient files still existing. It clearly distinguishes reproducing the same counting defect from recreating those incidental files' original contents. This corrects the documentation issue while preserving the historical evidence.

The supplementary procedure has not been executed. Do not describe it as rerun-verified. No extra E2E execution is required merely to document this correction.

## Boundaries on conclusions

Even after run 002 passes, the defensible conclusion is that source identity, input structure and the specified short supplied-example workflow have passed their scope. Candidate alpha, candidate causality, future beta compliance, strategy solvency, multi-decade behavior and runtime, remote CSV byte identity, and the full final dependency environment remain unverified.

## Completion addendum

Run 002 completed at 2026-10-26 13:55:52 UTC with exit code 0 and status `PASS_SCOPE_ONLY`. The independent reviewer inspected the completed artifacts and confirmed:

- All 24 recorded checks have `PASS` status.
- The preserved `runner_used.py` SHA-256 matches `runner_sha256.txt`.
- Each of the three saved prefix input files matches both its recorded byte count and SHA-256 in `input_manifest.json`.
- Both saved scoring CSVs contain exactly 250 rows. Recorded array indices run from 253 to 502; CSV day labels run from 254 to 503.
- The four saved economic columns are exactly identical between the two repetitions. Timing is intentionally excluded from this comparison.
- The original scorer report, execution log, final summary, frozen plan and frozen rerun command are present.
- Equal-weight net beta is 0.9999892123827355, appropriately near one and explicitly failing the assignment beta requirement by design. No candidate strategy validation is claimed.

No new strategy or further E2E run was executed during this review. The review supports the narrow successful preflight conclusion. The failed-run-001 reproduction documentation issue is resolved by the explicit, unexecuted supplementary procedure above; original evidence is preserved.
