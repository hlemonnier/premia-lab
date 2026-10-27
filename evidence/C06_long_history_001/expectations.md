# Full long-history strategy workflow

Prospective engineering contract, 27 October 2026, Europe/Paris. Written before the new controller. This is an end-to-end execution of an unchanged candidate through the unchanged supplied scorer. It is not an isolated unit test and does not admit an alpha configuration or inspect protected market rows.

## Scope and input recipe

The first candidate is the exact C06 configuration and source identified by `evidence/discovery_C06_001`. Generate exactly 25,200 rows (100 times 252) by repeating the verified 2,016-row discovery arrays in their original order, truncating the last repetition. Keep the 1,000 original costs unchanged. The first 2,016 rows are exactly the historical discovery inputs. All synthetic rows derive from permitted discovery data; actual validation and audit arrays are not read. Repetition creates artificial discontinuities and dependence: synthetic performance is not evidence of alpha and no synthetic Sharpe ranking is computed.

Materialize inputs as float64 read-only memory maps. Write in bounded chunks, flush, hash all files and record the deterministic recipe and source hashes. Avoid full duplicated arrays because the execution environment has an 8 GiB memory limit. Run a fresh process, one pinned CPU, with all numerical libraries restricted to one thread. Record host contention and actual elapsed time; do not substitute an extrapolation for this executed century.

## Workflow and expected outcomes

1. Freeze the strategy directory, exact candidate configuration, controller, this plan, original scorer and research protocol in a new non-overwriting evidence directory. Verify the imported dependency closure against the historical discovery source manifest and verify the official scorer SHA-256. Preserve setup, exact rerun command, identities, environment, stdout/stderr and any failure.
2. Call `score.run` once with start 252 and all 25,200 rows. Forecast must be called exactly once and return finite `(25200,1000)` values. Its first 2,016 rows must reproduce the historical discovery forecast `.npy` SHA-256 exactly. This also checks invariance under a much longer synthetic suffix.
3. Execute the complete serial rebalance path from an empty book. Expected target earning indices are 253 through 25,199 inclusive: 24,947 calls. Official scored indices are 253 through 25,198 inclusive: 24,946 rows. Preserve the official omitted endpoint and free first opening trade. Full drift-aware fees on every subsequent closing trade must reconcile exactly to scorer output.
4. Every target has shape `(1000,)`, is finite, respects the unchanged configured stock and gross limits within the already established 1e-12 arithmetic tolerance, and does not mutate the supplied held book. Inspect all calls, including late history and periodic factor refreshes; do not omit slow calls or fallback events from timing.
5. Preserve candidate-only forecast and rebalance elapsed times separately from instrumented scorer timings. The measured century forecast must take less than 3,600 seconds. Both the full-path candidate mean and scored-call candidate mean rebalance must be below 100 ms; report the maximum and quantiles without treating the average requirement as a maximum requirement. Report earlier/later quarter means to reveal history-dependent growth.
6. Save the first 1,763 targets and drifted held books, compare their `.npy` SHA-256 identities to historical C06, and require the first 1,762 economic rows to equal the saved discovery ledger numerically, excluding timings. Preserve a compact daily ledger for the entire artificial path, complete timing records, source/input/output hashes and a machine-readable check summary. Large reproducible arrays remain excluded from Git under the existing policy.
7. Rehash frozen source and inputs at completion. A mismatch, nonfinite value, infeasible book, failed economic reconciliation, incomplete endpoint sequence, runtime breach or unavailable expected comparison is a failed/incomplete gate. It never becomes a pass because an economic number looks favorable. Keep failures rather than overwriting them.

The controller must not alter source code, retune a candidate or open another market period. An exact retry after infrastructure interruption is allowed and must preserve the failed attempt. A later unchanged nominee may use this same workflow only with its own historical discovery identities; no changed configuration is hidden inside a runtime check.

## Limits

The repeated input is a workload and tested-path safety fixture, not a century of independent market observations. Measured runtime is host-specific and concurrent processes may affect wall time even when each is pinned separately. This gate does not prove causal correctness on every conceivable input, no overfitting, or future profitability. The independent full-discovery perturbation audit, chronological validation and locked audit remain separate gates.
