# Independent evidence execution record

29 October 2026, Europe/Paris. Working directory for every command:
`/workspace/scratch/a83c191d516f/continual-research-takehome`.

Commands below are the actual executed invocations. Expected outcomes and
source-review acceptance were frozen beforehand in `REPLAY_PLAN.md` and the
peer-review JSON; these execution notes do not change those gates. Each mode's
own `invocation.json` records its process arguments, actual affinity/thread
settings, versions and source identities. Root's copied release binds the mode
and, where required, its preceding successful result.

## Replay: completed, exit 0

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v3_evidence_audit_20261029/audit_replay.py --mode replay --out evidence/v3_evidence_audit_20261029/replay_001 --release evidence/v3_root_review_20261029/REPLAY_RELEASE.json > evidence/v3_evidence_audit_20261029/replay_001.stdout.log 2> evidence/v3_evidence_audit_20261029/replay_001.stderr.log
```

Runner session `98488`, terminal exit code `0`. External stderr is empty.
`replay_001/result.json` SHA256:
`8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66`.
All arrays/source copies in this completed packet are immutable.

The original large forecast and all three target streams were restored exactly:
both policies match their original published file and raw-array SHA256 values.
The original per-asset reference is consequently available again, not inferred
from a small P&L difference.

## Temporal: completed, exit 0

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v3_evidence_audit_20261029/audit_replay.py --mode temporal --out evidence/v3_evidence_audit_20261029/temporal_001 --release evidence/v3_root_review_20261029/TEMPORAL_RELEASE.json --reference evidence/v3_evidence_audit_20261029/replay_001/research --prerequisite evidence/v3_evidence_audit_20261029/replay_001/result.json > evidence/v3_evidence_audit_20261029/temporal_001.stdout.log 2> evidence/v3_evidence_audit_20261029/temporal_001.stderr.log
```

Runner session `78570`, terminal exit code `0`. Root release SHA256:
`77b795637637b0af43ee4be7a2fb30c9e8325efbc8a9cbf739f12be5ec41a9bc`.
The successful replay result is bound as its prerequisite.
All fifteen existing checks passed. Both external and existing-script stderr
are empty. `temporal_001/result.json` SHA256:
`9d91f352f5bd650f76f58e2d84fc534ce8a111a24ce93a135b5f5c5322125e11`.
The completed temporal packet is immutable.

## Runtime: completed, exit 0

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 1 python evidence/v3_evidence_audit_20261029/audit_replay.py --mode runtime --out evidence/v3_evidence_audit_20261029/runtime_001 --release evidence/v3_root_review_20261029/RUNTIME_RELEASE.json --prerequisite evidence/v3_evidence_audit_20261029/temporal_001/result.json > evidence/v3_evidence_audit_20261029/runtime_001.stdout.log 2> evidence/v3_evidence_audit_20261029/runtime_001.stderr.log
```

Runner session `27593`, terminal exit code `0`. Root release SHA256:
`1cdbfb0b9f263924ad7246be0d1ac8be70e84ad4eb92f9b3c0c9afcc7ec5c2c3`.
The passed temporal result is bound as its prerequisite. External and
existing-script stderr are empty. Result SHA256:
`241cd9b1f78191f9d2cfb19a7f3c886fb2dcba769988b731a10a68ffa1f30ca1`.

The unchanged existing worker reports mean rebalance `12.4171169667271 ms`,
p99 `33.50172565005775 ms`, maximum `295.59632399968905 ms`, and forecast
`60.57106748699971 s`. The wrapper verifies 24,947 decisions, 24,946 scored and
earned rows, last day 25,198, all 49,894 certificates `ok`, positive gross
solvency, finite arrays and unchanged input/source/CPU-thread bindings. No alpha
score is computed from the repeated history. The completed packet is immutable.

One supporting file-write/syntax-check tool request was delayed during this
run, then completed with exit `0`. The runtime process was left unchanged;
subsequent reads showed no failure record or stderr, and it completed without
a retry. This records an observed tool-response delay, without inferring its
cause or relabeling it as a numerical policy failure.

## Lossless runtime packaging: completed, exit 0

```sh
taskset -c 1 python evidence/v3_evidence_audit_20261029/package_runtime_evidence.py --runtime evidence/v3_evidence_audit_20261029/runtime_001 --out evidence/v3_evidence_audit_20261029/runtime_packaging_001 > evidence/v3_evidence_audit_20261029/runtime_packaging_001.stdout.log 2> evidence/v3_evidence_audit_20261029/runtime_packaging_001.stderr.log
```

Runner session `75064`, terminal exit code `0`; stderr empty. All five gzip
round trips exactly match their original bytes. Manifest SHA256:
`414ca37bd2ccbc5f84fc150885e574e87953e04a7556a74ecf0385c7f093c1ae`.
Compressed total `3,117,406` bytes; original total `12,036,749` bytes. The full
runtime forecast is explicitly regenerable and is not included in these five
compressed copies. No original packet, source or policy was changed by packaging.

No additional policy executions, candidates, cuts, repairs or tests followed.
