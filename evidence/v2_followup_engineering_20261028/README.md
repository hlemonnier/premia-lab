# Independent engineering follow-up evidence

Reviewed source commit: `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`.
Read `PLAN.md` first. The complete synthetic scorer workflow was reused unchanged
from the previous review after recording the expectations in this directory.

- `review_identity.json`: actual reviewed source SHA256 identities, unchanged
  runner identity, and the qualification of the runner's old literal commit metadata.
- `command.json` and `execution.json`: exact runtime, command, thread settings,
  process result and elapsed time.
- `stdout.txt` and `stderr.txt`: retained controller output.
- `run_001/commands.json` and `run_001/logs/`: ten fresh worker processes and
  their exact commands/output; twelve complete scorer executions in total.
- `run_001/results.json`: all exact equality and future-stimulus comparisons.
- `independent_readback.json`: outcome assessment and source-unchanged checks.
- `commit_history_readback.json`: the seven new pinned first-parent commits,
  changed paths, plan/result ordering and limits of within-commit chronology.
- `ledger_readback_pre_execution_review.json` and
  `latest_observer_pre_execution_review.json`: peer source-review identities
  and qualifications before the coordinator's calculations/replays.
- `latest_actual_replay_independent_readback.json`: independent full CSV
  readback of the coordinator's latest V2/B0/B05 actual replays, including final
  estimated-beta feasibility and absence of gross scaling.
- `latest_v2_vs_original_independent_readback.json`: direct latest/old V2
  economic agreement with explicit index matching.
- `observer_parse_failure_readback.json`: the pre-reviewed observer's missed
  excess brace, preserved failure identity and the one-character correction.

## Actual outcome

All ten workers exit zero. All arrays are finite and all runs trade. Twenty of
twenty-one strict bitwise comparisons pass. Restart and characteristic-layout
regressions are corrected. All protected forecast/target comparisons pass.

The failed exact comparison is the original scorer's gross P&L under Fortran
**returns**: 31 protected daily values differ, maximum `2.6020852139652106e-18`.
Costs, gross exposure and market fields match bitwise. The unchanged scorer
uses a dot product on the caller's return row; its layout-dependent last-bit
roundoff is not controlled by the strategy. This is retained as a failed
prospective expectation rather than labeled an all-pass run. It is not evidence
of future information changing trades.

The pre-existing runner writes its older reviewed commit in `environment.json`.
That literal is stale; the source copied into this run is the new pinned commit,
identified by `review_identity.json` and `run_001/input_source_manifest.json`.

Fixture and run NPZ files are reproducible local intermediates. Their identities
are retained in the run's artifact manifest; the compact source, commands and
results are the versioned evidence. No production or scorer source changed.
