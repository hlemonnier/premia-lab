# Conditional joint execution record

29 October 2026, Europe/Paris. The actual joint workflow subsequently completed
successfully. The initial synthetic checkpoint is retained below; actual command
and outcome follow it. Long-history runtime remains separately gated.

## Construction order

1. Root's master composition rule preceded standalone outcomes in committed
   plan d2997e0d98c6407da4b503a77060966904486062.
2. E2 and M1 independently qualified; F3 failed. Root authorized the exact
   F2 -> E2 -> outer M1 composition, with no subset search.
3. Copied common.py, execution.py, forecast_reference.py, reference_overlay.py
   and sleeve.py byte-identically; dependency_manifest.json records provenance.
4. Wrote PLAN.md, E2E_SPEC.md and e2e.py while joint.py was absent. The optional
   25,200-day runtime path and full/trimmed recording equality were included.
5. The expected missing-factory run exited 3, reporting economic_runs 0.
   preimplementation_record.json preserves the source identities and command.
6. Wrote the nine-line joint.py factory. pre_review_source_manifest.json binds
   the nine source/specification files. No reviewed dependency was modified.
7. synthetic_001 passed on the first implemented run with exit 0 and no stderr.
   Both independent reviewers received the frozen sources and result.

## Completed commands

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_joint_20261029/e2e.py --mode synthetic --out evidence/v2_score2_joint_20261029/expected_red_001 > evidence/v2_score2_joint_20261029/expected_red_001.stdout.log 2> evidence/v2_score2_joint_20261029/expected_red_001.stderr.log
```

Expected/observed exit code: 3. Policy executions: 0.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_joint_20261029/e2e.py --mode synthetic --out evidence/v2_score2_joint_20261029/synthetic_001 > evidence/v2_score2_joint_20261029/synthetic_001.stdout.log 2> evidence/v2_score2_joint_20261029/synthetic_001.stderr.log
```

Observed exit code: 0. All 14 summary checks and 383 per-workflow checks across
12 scorer runs pass. The previous standalone E2, M0, all inner-book paths,
temporal/restart checks and full/trimmed recording comparisons are exact.
Known netting and outer cap cases pass; the E2 stress contains 133 outer caps
with exact inner-path preservation. Source/specification hashes remain unchanged.

Result SHA256:
`f23fa2a55efaf9bbf6c8b120bfdeded7daec33ac961baef17dc68082410fdbe5`.

Both independent reviews accepted the frozen code and evidence without required
changes. The execution owner's joint_execution_runtime_review.json separately
verified the E2 interface and all three full/trimmed decision hashes. The challenge
reviewer's joint_source_review.json and joint_synthetic_review.json verified all
171 artifact hashes and 96 atomic arrays, reconstructed all 12 workflows and
reconfirmed exact inner/M0/temporal/trimmed identities. Independent accounting
and explicit-weight VT errors were at most 9.58e-18 and 8.88e-16 respectively.
Actual scoring remains dependent on root's source-bound release.

## Release interface

Actual mode requires a root JSON release with allow_actual=true,
qualifying_components=["E2","M1"], and source_sha256 matching all nine entries
of pre_review_source_manifest.json. The root can additionally bind independent
review and synthetic result hashes. The harness verifies the pinned ce3 baseline
identities and original CSV hashes before scoring. Actual arrays use atomic NPY
and immediate readback, including all three target books, forecast and scorer rows.

Runtime requires a separate allow_runtime=true binding. It is only for the
selected composition, tiles the original data to 25,200 rows and uses the
prospectively checked trace-trimming observer. It reports computational checks
and no alpha score. Neither mode has run at this checkpoint.

## Completed actual command and frozen outcome

Root accepted both peer reviews and its source read, then released the exact
nine sources in ../v2_score2_root_20261029/JOINT_ACTUAL_RELEASE.json, SHA256
`b3c6afc2f14995b1d5c3c29a5c4c79d84d4721bf4ce341e005aaa59f236ada9b`.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_joint_20261029/e2e.py --mode actual --out evidence/v2_score2_joint_20261029/actual_001 --release evidence/v2_score2_root_20261029/JOINT_ACTUAL_RELEASE.json > evidence/v2_score2_joint_20261029/actual_001.stdout.log 2> evidence/v2_score2_joint_20261029/actual_001.stderr.log
```

Observed exit code: 0. Stderr is empty. All nine summary checks and 192 workflow
assertions across six complete runs pass. The candidate scores 1.444733300556666
against M1's 1.426560898191992, a gain of 0.0181724023646741. It passes the frozen
economic comparison; root independent readback and runtime admission are separate.
Both allocator books pass certificates and independent risk-clock checks on all
3,527 candidate decisions. E2 reproduction, M0, nested inner/virtual/controller
paths, altered-future/prefix protection and cross-history restart are exact.

The source-bound policy and all actual_001 artifacts are frozen for root readback.
The own report ../../research/v2/SCORE2_JOINT_20261029.md records full stage/cost/
beta/runtime metrics and the modest audit-period decline. The cost mechanism is
explicit: E2 prices inner trades; the original scorer charges outer combined stock
trades. No alternative composition or tuning followed this outcome.

Actual result SHA256:
`1e156b5b2c864f5d6b7a7edc2bb190f640b0ad6e4ebc19d536b68e7e7a08b30d`.
Candidate array-manifest SHA256:
`b47d435638ee44de4e8acd2c0af14f3a86dac75776118e4264f4d8caa28c8f5f`.

The 25,200-day runtime mode has not been authorized or executed at this checkpoint.

## Independent readback and runtime release

Root's separate stock-level readback reproduced the selected score exactly,
with maximum accounting error 5.20e-18. Its file is
../v2_score2_root_20261029/joint_readback_001.json, SHA256
`565c895d63e2dc7ee2e511bb47514c09fd08da841b6111c6b6cb5b007bb25e6f`.
Root then authorized the unchanged 25,200-row runtime mode in
../v2_score2_root_20261029/JOINT_RUNTIME_RELEASE.json, SHA256
`ebfd08b2ec345c0b5116bc852cbeb585c6174711a0f3974603c14915db47dc2d`.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v2_score2_joint_20261029/e2e.py --mode runtime --out evidence/v2_score2_joint_20261029/runtime_001 --release evidence/v2_score2_root_20261029/JOINT_RUNTIME_RELEASE.json > evidence/v2_score2_joint_20261029/runtime_001.stdout.log 2> evidence/v2_score2_joint_20261029/runtime_001.stderr.log
```

This command completed with exit 0 and empty stderr. It uses the original scorer
and unchanged selected policy with the prospectively checked trace observer.
All three summary checks and 31 per-workflow assertions pass. It reports no alpha
metrics. Actual_001 outputs and all nine sources remain frozen.

The 25,200-by-1,000 input produced 25,200 forecast rows, 24,947 decisions and
24,946 economic rows. Forecast time was 20.035996424994664 seconds; mean
rebalance time 7.990192503556128 ms, 99th percentile 13.269608948394305 ms and
maximum 150.26360000047134 ms. The mean-based 100 ms gate passes. Peak RSS was
3,835,208 KiB. Accounting error is zero and both books' solver/state/constraint
checks pass throughout. The performance object is empty because repeated data
provide no new alpha evidence.

Runtime result SHA256:
`f4983861a78b53f8a41dcc5b9b49d0a9ddac715a097175861db83ccc5c652bb5`.
Summary SHA256:
`dd6c08042ec5c22b73aa0bd4872b233ca648f325f4d7b7c546e6837599832a7d`.
Array-manifest SHA256:
`166213d4aa91ba52c14db857392e04f511ab8845e04b235830e314337d6e1569`.

Runtime outputs are frozen, including the deterministic 2,620,800,128-byte
characteristics memmap. Full target histories are represented by the declared
rolling hashes; final targets and scalar traces are retained. Forecast/scorer
arrays were atomically written and read back. The execution reviewer has been
asked to verify the completed runtime evidence without executing the policy.
