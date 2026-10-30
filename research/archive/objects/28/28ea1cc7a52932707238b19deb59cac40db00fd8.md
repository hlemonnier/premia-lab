# F3 execution record

29 October 2026, Europe/Paris. The actual workflow subsequently completed and
rejected F3 on net score. The initial synthetic verification checkpoint below
is retained as execution history; the actual run is recorded afterward.

## Source ordering

1. PLAN.md and the research note specified one exact F3 + unchanged VTvol policy.
2. Root approved that policy in SCORE2_RESEARCH_PLAN_20261029.md. E2E_SPEC.md,
   e2e.py and unchanged copied baseline_forecast.py/overlay.py were written
   before prototype.py existed.
3. The missing-policy run exited 3 and preserved
   expected_red_001/status.json with economic_runs 0. The exact command and
   original source hashes are in preimplementation_record.json.
4. Implemented prototype.py, SHA256
   `cc9df99a01cf991143aa03ef37d0ab3746b47ca9b417dec42eee9e069f662921`.
5. synthetic_001 stopped after its first F2 control because a NumPy boolean
   could not be serialized to JSON. A bool cast repaired this existing endpoint
   check only. All original outputs/source/logs remain. See FAILURES.md.
6. synthetic_002 passed the same complete workflow with prototype unchanged.
   Current harness SHA256
   `dfd1d01bb9af6718e8824f7aa62b8537da3c26296753fd65f60a2eac960901ea`.

## Exact completed synthetic command

From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_forecast_20261029/e2e.py --mode synthetic --out evidence/v2_score2_forecast_20261029/synthetic_002
```

Stdout/stderr are preserved as synthetic_002.stdout.log and
synthetic_002.stderr.log. The eight complete cases retain atomic NPY arrays,
immediate readback hashes, daily/decision CSVs, source copies and commands.

Result SHA256:
`47515a30e97a134337749f8f55273adf66c53090e122385295fb5ff3ab29e80f`.
All 10 summary checks and 120 per-workflow checks pass. The pure temporal checks
are exact. The independently calculated market state differs by 1.67e-15; the
direct weighted 53-column regression oracle differs by at most 1.03e-18. The
zero-state F2 equivalence has a maximum target difference of
1.0010648351932439e-9, within the original 1e-8 downstream tolerance.

## Status and prospective execution boundary

The score2_challenge reviewer accepted the frozen source and passing workflow
without required changes, independently checking all 64 atomic arrays and
120 per-workflow checks. The binding review record is
../v2_score2_review_20261029/forecast_source_review.json. No actual-market
F3 run or 25,200-day runtime stress is authorized by synthetic success alone.
The harness requires a root release binding its six source/specification files.
Actual output will contain targets.npy, virtual_targets.npy, forecast.npy,
rows.npy, decision_indices.npy and trace arrays with complete readback manifests.
The optional long-history mode is a computational stress only, never new alpha
evidence, and runs only if selected and separately released by root.

## Actual release and completed command

The root master plan was committed as
`d2997e0d98c6407da4b503a77060966904486062` before candidate outcomes. Root then
released the six frozen local files, independent review, synthetic result and
ce3 baseline identities in ../v2_score2_root_20261029/F3_ACTUAL_RELEASE.json.
The snapshot baseline identities were also checked directly against that release.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_forecast_20261029/e2e.py --mode actual --out evidence/v2_score2_forecast_20261029/actual_001 --release evidence/v2_score2_root_20261029/F3_ACTUAL_RELEASE.json > evidence/v2_score2_forecast_20261029/actual_001.stdout.log 2> evidence/v2_score2_forecast_20261029/actual_001.stderr.log
```

The command exited 0; stderr is empty. Only the predeclared baseline, F3,
future-altered and prefix workflows ran. All six summary checks and 60
per-workflow assertions pass. Future and prefix protected forecast/target/
economic differences are exactly zero; baseline daily reproduction differs
by at most 4.44e-16 and its score is identical to the previous leader.

F3 net Sharpe is 1.2943927925112546 versus 1.318334966090838 for F2 + VTvol,
a difference of -0.02394217357958328. It fails the frozen economic rule and
does not qualify for composition. All original-period diagnostics also decline.
The optional 25,200-day stress remains unexecuted because only an economically
selected candidate would receive that separate release. No tuning was performed.

The full performance/stage/verification report is
../../research/v2/SCORE2_FORECAST_20261029.md. Key artifact SHA256 identities:

| Artifact | SHA256 |
|---|---|
| actual_001/result.json | `317efd3f6d738279f98aa831abbd54a9973dcd1fe70ab36e14e631f32c67bb37` |
| actual_001/economic_comparison.json | `eba5f3364680ce30e4a15779d66a37695e3b4a8c8e37162d25e0b90af7bdcee4` |
| actual_001/F3_VTvol/array_manifest.json | `86c92bc75616a4cbf6d4691eecde7df9bb6154fef1d748f68be9a090b3822c87` |

The per-case array manifests include atomic files, array and file hashes, shapes,
dtypes and immediate readback results. Root can independently reconstruct the
original economics from targets.npy and compare against rows.npy without
executing the policy again. The six source/specification hashes are unchanged.

## Additional independent work

At the execution owner's request, this agent reviewed the mathematical scalar
solve and E2 homogeneity logic without running a strategy or changing sources.
The separate execution_math_review.json records that narrow accepted review
and the inherited proportional gross-rescaling qualification. It does not
replace the challenge reviewer's timing/source/workflow review.
