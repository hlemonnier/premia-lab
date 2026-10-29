# Prospective independent V3 evidence closure

29 October 2026, Europe/Paris. This extends the static SCOPE.md only after root
authorization. No implementation, setting, source scorer or input is changed.

## Purpose and permitted executions

The committed V3 checks establish equality to Claude's same-environment rerun,
but do not persist that rerun's provenance or arrays. The historical target-hash
precondition failed and stays failed. Original large research arrays were not
Git-persisted and are unavailable in the current reset workspace. This packet
cannot measure per-asset differences against those unavailable original arrays;
small economic differences do not imply small position differences.

Run exactly these three modes, sequentially on one CPU with OPENBLAS, OMP and
MKL thread settings equal to one, only after a peer source review and root
release binding this plan, the new harness and the source/input bindings:

1. **Replay.** Execute the unchanged pinned research F2->E2->M1 joint and the
   unchanged shipped V3 package, each once, on the original inputs under the
   original scorer. Save their forecasts, all three target streams, decision
   indices, full scorer rows and controller/state-clock traces. Reconstruct
   actual stock-level drift and fees independently. Compare both with the
   original published winner daily CSV and with each other.
2. **Temporal.** Run Claude's existing unchanged v3_integration_checks.py against
   the new saved research reference. It repeats its already declared cuts at
   600, 2000 and 3500 and its existing restart workflow. Capture full invocation,
   source/data identities, environment, stdout/stderr and JSON result. No new
   cut point, altered-return rule or candidate is introduced.
3. **Runtime.** Run Claude's existing unchanged v3_runtime_check.py once on its
   25,200-row tiled input. Execute that file as a module, retaining its namespace
   after its normal SystemExit so an external observer can save rows, forecasts,
   final book vectors, certificate counts/statuses and actual process settings.
   The policy and runtime script bytes are unchanged; observation is after
   score.run returns and therefore does not enter its timers. No alpha score is
   computed from repeated data.

Each mode requires a new empty output directory; failure, partial output and
traceback are preserved. No automatic policy repair or extra run is permitted.
Temporal mode must bind the passed replay result by the SHA256 supplied in its
root release, and verify every reference file/raw-array hash against that
result. Runtime mode similarly binds the passed temporal result. Root can
therefore release the modes successively without altering the frozen harness.
Syntax compilation and pre-execution identity checks are allowed without an
economic run. All outputs use atomic NPY writes plus file/raw-array SHA256 and
immediate reopen verification. Source copies and exact rerun invocation are
retained with every output packet.

## Frozen sources and data

Production commit: 978824d4b6140c43566ebd61a3ee8157f4080e35. Research commit:
9e56aa755d20c5876485188f4c50ce959f6d63f3, nine policy/specification sources bound
by its pre_review_source_manifest.json. Historical engine: ce3fe4e, with the
five SHA256 identities in common.SOURCE_HASHES. Original scorer SHA256:
ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96.

Original inputs and original published daily CSV identities are frozen in
bindings.json. Root verified the production commit, Git blob and SHA256
identities against the downloaded source_manifest.json; the independent peer
also recomputed the seven consumed production files' Git blob and SHA256
identities. The wrapper enforces the resulting SHA256 bindings before and after
execution. Every consumed source is copied byte for byte into the packet.
CPU affinity, thread variables, Python,
NumPy, pandas, platform, process id, source hashes and command arguments are
saved before execution and checked again after it.

## Expected outcomes and exact acceptance limits

- Original dimensions: returns (3780,1000), characteristics (3780,1000,13), costs
  (1000,); finite inputs; exact original input/source hashes.
- Full decision indices exactly 252..3778, 3,527 decisions; scorer rows exactly
  (3526,5), earning indices 253..3778. Free opening, charged endpoint, no forced
  liquidation. Population-standard-deviation net Sharpe.
- Same-environment research versus package: forecasts and decision indices
  exactly equal; max absolute difference <=1e-8 for each target stream and for
  each of the four economic columns; full net-Sharpe difference <=1e-8. Keep all
  observed errors, including acceptable nonzero ones. Controller moments and
  multiplier differences <=1e-12; integer counts/risk clocks exactly equal.
- Each replay versus original published CSV: four economic columns <=1e-8 and
  net Sharpe <=1e-8. Timing columns are excluded. Record published array-manifest
  hash comparisons separately as identity diagnostics. If regenerated arrays
  match original raw-array SHA256 values with matching dtype/shape, exact
  original identity is recovered; the companion package/reference can then be
  compared numerically against that restored array. If neither matches, the
  original per-asset difference remains unmeasured. A tiny P&L difference is
  never a substitute for this bridge.
- Independent stock-level accounting error <=1e-12. Reconstruct from previous
  targets and original returns/costs, using gross denominator and the scorer's
  opening/endpoint convention. Finite, solvent paths; actual gross <=5+1e-10,
  virtual cap <=.05+1e-10, inner cap <=.05*a+1e-10, outer <=.10005+1e-10.
  Realized full net beta absolute value <.2. Both risk states end at t+1 at each
  decision, and controller multiplier stays within [.5,2].
- Exactly 7,054 accepted certificate records in each actual replay, with statuses
  ok/ok_after_recovery for ce3 or additionally ok_after_cold_restart and
  fallback_diagonal for the hardened package. Retain full scalar certificate
  records and counts; no claim of explicit-gross-constrained global optimality.
- Temporal mode: child exit 0; all 15 existing check records true; the same
  frozen source/data bindings before and after execution.
- Runtime mode: exact input dimensions (25200,1000), 24,947 decisions and
  24,946 rows, 49,894 accepted certificates; finite forecasts/rows and positive
  1+gross daily returns; one actual CPU affinity entry and all three thread
  settings 1; mean rebalance <100ms and forecast <3600s. Record p99 and maximum
  separately. Repeated-input hash and final book checks are observed after the
  unchanged script completes. No Sharpe or alpha conclusion from this mode.

Root's release and peer review must precede execution. Passing this new packet
closes its own evidence questions; it cannot retroactively satisfy the original
failed cross-environment exact target-hash gate or prove universal absence of
lookahead/overfitting.
