# Forecast prototype execution record

28 October 2026, Europe/Paris. Production source pinned to `ce3fe4e`.

## Source ordering

1. Wrote the research specification and `PLAN.md`.
2. Wrote `run_research.py`; Python AST parsing passed.
3. Invoked the controller while `prototype.py` did not exist. Exit3,
   `EXPECTED_RED_MISSING_PROTOTYPE`, zero economic runs. Exact argv, source hash
   and absence record are in `expected_red_command.json` and `expected_red_001/`.
4. Wrote `prototype.py`; Python AST parsing passed.
5. Independent agent accepted the exact sources for E2E execution:
   `../v2_score_opportunity_20261028/forecast_source_review.json`.
6. Started the prescribed synthetic workflow. Its result is recorded below
   when the process completes; starting it is not a pass.

Reviewed hashes:

- Plan: `f887dd56bc7293571cf862d6b2419c844e37fe8473390566587cc80070259f6e`.
- Controller: `ea097d7d69be37cea7b6edc9c34d697dc3622a3c76172f20812689ccce1939ef`.
- Prototype: `7854b2f763ae1bcc716282b68791503fe29f83d0aebc64835d8d0d919c722719`.

## Exact synthetic command

Working directory: `/workspace/scratch/a83c191d516f/continual-research-takehome`.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/run_research.py --mode synthetic --out evidence/v2_score_forecast_20261028/synthetic_001 > evidence/v2_score_forecast_20261028/synthetic_001.stdout.log 2> evidence/v2_score_forecast_20261028/synthetic_001.stderr.log
```

## Synthetic001 result: failed strict aggregate expectations

Exit1 after all12 full-scorer cases completed. Every case passed its finite,
warm-up, accounting, source/input identity, cap/hedge and certification checks.
The aggregate result failed two recorded expectations:

- F1 constant-Gram forecast equivalence differs by 9.11e-18, satisfying the
  1e-12 forecast identity condition. Targets differ by 1.05e-9 and closing gross
  by 2.11e-9, exceeding the 1e-9 downstream expectation. Maximum net-return
  difference is 2.89e-12. Both forecasts and targets are nonzero.
- F1 joint-future alteration with both inputs in Fortran layout has identical
  protected forecasts, but targets differ by 1.09e-9 and closing gross by
  1.93e-9, exceeding the 1e-12 criterion. Maximum protected net-return difference
  is 9.27e-13. The first target difference is 1.39e-16 at decision285.

Both repeat and prefix comparisons pass exactly; F2's combined future/layout
check passes (only scorer economics differ by 1.31e-18). Zero controls pass.
See `synthetic_001/verification.json` and `failure_readback.json`. No tolerance
has changed, no failed record is overwritten, and neither prototype is modified.

The suspected mechanism is amplification of tiny floating-point perturbations
by the existing allocation path. This is an inference, not yet a complete
causal identification. A narrower complete-scorer follow-up is specified next.

## Prospective follow-up to separate future alteration from memory layout

Use the same synthetic moving-panel fixture, same seed, same F1 source, same
original scorer, and same row320 alteration. Keep both base and altered arrays
C-contiguous. Reuse the original comparison rule and tolerance1e-12, protecting
forecast rows<=320 and decision/economic indices<320. Run two fresh complete
scorer workflows; compare their outcomes and the repeated baseline against the
saved original baseline. Preserve exact input/source/controller identities and
commands. No new trading candidate or parameter is admitted.

If this passes, classify the combined future/layout failure separately from
future-information dependence, while retaining the failed original numerical
expectations. If it fails, diagnose before actual economics. Root must approve
this disposition and actual-data execution. No actual-market prototype run has
occurred at this record checkpoint.

## C-layout isolation: executed and passed

Independent reviewer accepted `run_c_layout_followup.py`; root authorized its
execution. Exact command, in the same working directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/run_c_layout_followup.py --out evidence/v2_score_forecast_20261028/c_layout_followup_001 > evidence/v2_score_forecast_20261028/c_layout_followup_001.stdout.log 2> evidence/v2_score_forecast_20261028/c_layout_followup_001.stderr.log
```

Exit0. The repeated baseline agrees exactly with the original saved baseline.
Future alteration alone preserves all321 protected forecast rows,68 decisions
and67 economic rows exactly (zero maximum differences). Source hashes agree.
This supports future invariance on the canonical layout; it does not rewrite
the two original failed numerical expectations or prove every layout equivalent.

## Actual research run: admitted and launched

Root's master plan was committed before actual economics at
`251bee83d182e8796b7e2a35354fd1475b7dc242`. Root admitted actual exploratory
scoring conditional on the exact canonical future/prefix comparisons, with the
strict layout/constant-Gram allocation failures explicitly retained. Those
conditions passed. Candidate/controller source and parameters remain unchanged.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/run_research.py --mode actual --out evidence/v2_score_forecast_20261028/actual_001 > evidence/v2_score_forecast_20261028/actual_001.stdout.log 2> evidence/v2_score_forecast_20261028/actual_001.stderr.log
```

Launch is not completion. Actual outcomes and any additional failures are appended
only after the process returns.

## Actual001 completion and preserved strict failures

All7 original-scorer workflows completed their per-run checks, with no source
change and all allocator certificates accepted. The aggregate process exited1:
the future alteration also changed memory layout, and the 1e-12 downstream
comparison failed for both candidates. Protected forecasts are bitwise identical
and both prefix workflows match predictions, targets and economics exactly.

- F1: maximum protected target difference2.045e-10, combined economic-field
  difference1.019e-9 (including closing gross).
- F2: maximum protected target difference1.673e-12, combined economic-field
  difference2.311e-11 (including closing gross).

No tolerance is changed. Full outcomes are in `actual_001/verification.json`.
The actual base scores are V2 1.2425030733, F1 1.1379930041 and F2 1.2917800643.
F1 loses; F2 earns a development improvement of0.0492769910. Their actual score
comparisons are preserved independently from causal/layout dispositions.

## Prospective actual canonical-future isolation for F2

Before a joint forecast/sizing experiment, perform one additional complete
original-scorer F2 run with the exact same future replacement from row1500,
seed20261029, retaining C-contiguous arrays. Compare against the saved original
F2 actual baseline: forecast rows<=1500, decisions/economics<1500, unchanged
1e-12 criterion. Verify original CSV identities, copied engine/scorer/prototype
identities, full drift/fee reconciliation, cap/hedge/certificates, and preserve
the output arrays and logs. No new parameter, score candidate, tolerance or
favorable-window selection is introduced. A pass isolates temporal dependence
on the canonical scoring path while leaving both strict mixed-layout failures
on record. Root authorization and independent source inspection precede the run.

## Actual canonical-future replay: economics completed, archive readback failed

Root authorized and an independent reviewer accepted `run_actual_c_future.py`
before execution. Command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/run_actual_c_future.py --out evidence/v2_score_forecast_20261028/actual_c_future_001 > evidence/v2_score_forecast_20261028/actual_c_future_001.stdout.log 2> evidence/v2_score_forecast_20261028/actual_c_future_001.stderr.log
```

The complete F2 canonical-future scorer replay and all per-run checks finished.
The subsequent comparison exited1 on `BadZipFile` while loading the original
F2 baseline archive. Inspection found missing ZIP central directories and
truncated payloads in the original F1/F2 baseline archives. Neither the author
nor the independent reader had intentionally rewritten them; the reader had not
yet opened them. The original CSV economics, summaries and live-array hashes
remain intact. The canonical-future archive is complete at initial inspection.
No pass is inferred from this failed comparison.

## Prospective evidence repair, authorized by root

Run exactly one unchanged-source F2 baseline again in a fresh directory. Reuse
the original reviewed controller's complete scorer function, source/configuration,
CSV loading and one-thread environment. Preserve the corrupt originals. Write
the returned arrays separately as `.npy`, using a temporary file, flush/fsync
and atomic rename. Validate saved shapes, exact values and hashes immediately.
Record original corrupt-file sizes, timestamps, ZIP integrity and disk space;
do not assert an unproved cause.

Require this replay's full forecast and target hashes to equal the original
live-array hashes in `actual_001/F2_base/summary.json`. Require CSV economics to
reproduce within the existing1e-12 controller tolerance, excluding latency.
Only after those conditions pass, compare this verified baseline with the
completed canonical-future output under the original row1500/1e-12 rule. This
is evidence repair and causal readback, not a new strategy or rescue tuning.
No negative F1 rerun is admitted.

## Evidence repair completed; F2 canonical causal gate passed

The independent opportunity reviewer accepted the evidence-repair source before
execution. Exact command:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/repair_f2_evidence.py --out evidence/v2_score_forecast_20261028/baseline_repair_001 > evidence/v2_score_forecast_20261028/baseline_repair_001.stdout.log 2> evidence/v2_score_forecast_20261028/baseline_repair_001.stderr.log
```

Exit0. The original full forecast and target array hashes match exactly.
Maximum economic CSV difference is4.4408920985e-16. Saved separate NPY arrays
are complete, with verified sizes/shapes/file hashes/value hashes in
`baseline_repair_001/verified_array_manifest.json`. The new NPZ also passes ZIP
integrity, but the independently verified NPYs are the repair deliverable.

Actual canonical-future comparison at row1500: all1,501 protected forecast
rows,1,248 decisions and1,247 economic rows match exactly. Source identity passes.
The original actual prefix also matched exactly. F2 therefore meets the scoped
canonical temporal-invariance condition; original strict mixed-layout failures
and the failed archive-readback command remain part of the record.

Archive investigation recorded sizes/timestamps/integrity in
`archive_failure_readback.json`. About30GB of scratch space was free at inspection;
storage exhaustion was not observed. No intentional rewrite was identified.
The source of truncation remains unknown. The rejected F1 archive is not repaired
by another policy run; its CSV score and original live-array hashes remain.

## Paired score readback

The prospectively specified fixed21/63/126-day paired resampling was executed:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u evidence/v2_score_forecast_20261028/analyze_scores.py > evidence/v2_score_forecast_20261028/score_analysis.stdout.log 2> evidence/v2_score_forecast_20261028/score_analysis.stderr.log
```

Exit0;2,000 draws/length, seed20261027, all legal block starts included. Full
results are in `results.json`; economic interpretation is in `RESULTS.md`.
No additional forecast parameter or selectable candidate was run.
