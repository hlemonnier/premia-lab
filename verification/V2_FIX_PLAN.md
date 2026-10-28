# V2 engineering fixes — failure modes and expected outcomes (written before the fix)

28 October 2026. Follows `reviews/V2_INDEPENDENT_REVIEW_20261028.md`. Applies to
`handoff_v2/`. No research hyperparameter changes.

Executable check: `verification/v2_package_checks.py --pkg <handoff dir> --data <csv dir>`;
exits nonzero if any expectation fails. It is run against the unfixed package
first (expected to fail checks 1–3) and then against the fixed package.

## Failure modes and expectations

1. **Stale risk state across scoring runs.** Score synthetic history A (start 252,
   through 300 rows), then, in the same process, score independent history B with
   `start=299`. Expected after fix: B's forecasts, every target and every economic
   ledger row are **bitwise identical** to a fresh-process run of B with the same
   arguments. Mechanism: the scorer calls `forecast` once at the start of each run,
   so `forecast` resets the rebalance risk state and solver warm start.
   Contract: one scoring session = one `forecast` call followed by `rebalance`
   calls on an append-only history. A history that shrinks also resets. Direct
   `rebalance` use without `forecast` keeps the length-based incremental cache.
2. **Characteristic memory layout.** Same synthetic run with characteristics in
   Fortran order versus C order (returns unchanged). Expected after fix: forecasts,
   targets and ledgers bitwise identical. Mechanism: `basis` canonicalizes each
   2-D panel to C-contiguous float64 before any reduction.
3. **Allocator certificate.** Every `allocate_factor` call returns a status record:
   factor residual `||M'w - lam/gamma||_inf`, normalized hedge residual, cap check,
   finiteness and duality gap `gamma/2 ||q||^2 - nu e`. Status `ok` requires
   finite output, caps exact, hedge within the existing tolerance and
   `|gap| <= 1e-12 * max(|primal|, 1e-12)`. If not `ok` after the first pass, the
   joint Newton solve resumes from the polished point (up to 100 further
   iterations), then the hedge is re-polished; the status reports which path ran.
   A residual exceeding the old gradient tolerance alone is not a failure when
   the gap criterion holds. Expected: every call on the real-data run has status
   `ok` (possibly after recovery); the number of recoveries is reported.
4. **Economic agreement with the old package (real data).** Daily net returns of
   the fixed package versus the unfixed package on the full real run:
   `max |difference| <= 1e-9` (layout canonicalization may change roundoff only;
   real inputs are already C-contiguous, so equality is expected).
5. **Causality (real data, packaged entry point).** Inputs replaced from row
   c ∈ {400, 1500, 3024, 3700}; forecast rows ≤ c bitwise identical, also with
   characteristics *and* returns in Fortran order, and with truncated histories.
