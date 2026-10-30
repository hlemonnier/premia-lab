# Independent V2 follow-up evidence

Reviewed source: `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`.

## Prospective specifications

- `PLAN.md`: saved-ledger statistics and independent beta-factor reconstruction.
- `LATEST_PACKAGE_REPLAY_PLAN.md`: bounded actual-data replays of existing V2,
  B0 and B05 after discovering that the previous real-data check predates the
  latest implementation extension.

## Executed work

- `download_manifest.json` and `reviewed_source_changes.json`: all 70 changed
  source/result files, pinned Git blob identities and local SHA-256 values.
- `ledger_readback.py/json`: 29 full ledgers, accounting/sample identities,
  six-policy performance, gross/net beta, HAC intervals and paired block ranges;
  new B05-minus-B0 incremental-return decomposition.
- `factor_readback.py/json` and `factor_daily.csv`: independent rolling-OLS and
  Frisch-Waugh-Lovell reconstruction of D1/D3, HAC sensitivity and centering
  identities; diagnostic sample has 3,527 rows, distinct from the earning sample.
- `replay_{V2,B0,B05}_002/`: fresh exact-package/source-copy replays through the
  original scorer, each with 3,526 earning rows and 3,527 decisions. Full ledgers,
  final-target observations, source/input/output hashes and unrounded results.
- `latest_v2_vs_original_direct.json`: direct old/new V2 economic comparison.
- `execution_record.json`, `replay_commands_002.json` and stdout/stderr logs:
  exact commands and process outcomes. Source reviewers approved methodology
  before execution; reviewer records are in the adjacent engineering directory.

## Failed and unexecuted work

Two initial replay launches failed at Python parsing before any economic work.
The faulty observer, commands and logs are retained in `failed_parse_attempt_001/`.
`HARNESS_FAILURES.md` describes the single-brace correction. B05's first prepared
command was not launched. Attempt002 succeeded for all three policies.

No new predictive candidate, new beta estimator or new target was run. No
century-length runtime gate was rerun. The next diagnostic handoff is a proposal
with fixed metrics, not an already-passed result. All data periods are exposed.

Additional independent complete-scorer and beta-MSE work is in the adjacent
`v2_followup_engineering_20261028/` and `v2_followup_causal_beta_20261028/`
directories. Strict scorer rounding failures and tolerance qualifications remain
explicit in their reports. Replays are instrumented; timings are not formal
uninstrumented performance certifications.
