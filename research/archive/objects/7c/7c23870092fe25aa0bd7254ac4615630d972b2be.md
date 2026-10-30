# Independent century-workflow evidence review

27 October 2026, Europe/Paris. **Both completed workflows pass the independent saved-evidence review.** This review examined `evidence/C06_long_history_002` and `evidence/C09_long_history_001`, using their original discovery records as references. It did not execute another candidate or access protected market observations.

## Verified outcomes

| Executed workload | C06 | C09 |
|---|---:|---:|
| Synthetic input rows | 25,200 | 25,200 |
| Serial rebalance calls | 24,947 | 24,947 |
| Scored economic rows | 24,946 | 24,946 |
| Measured candidate forecast seconds | 72.6422 | 43.1908 |
| Mean candidate rebalance, all calls | 8.18954 ms | 2.18872 ms |
| Mean candidate rebalance, scored calls | 8.18918 ms | 2.18859 ms |
| Maximum candidate rebalance | 69.6254 ms | 52.6206 ms |
| Frozen CPU | 6 | 8 |

Each workflow used one numerical-library thread and a single pinned CPU. Both measured forecasts are below 3,600 seconds; both full-path and scored-call rebalance means are below 100 ms. These are executed, host-specific measurements, not century extrapolations or controlled speed comparisons across hardware/load.

## Readback work

`evidence/long_history_independent_readback_001/summary.json` records **61 passing checks**. The reviewer rehashed all 102 artifact-manifest files and all 32 frozen-source entries, verified the original candidate/configuration/protocol/scorer identities, and checked that the original reference summaries, ledgers and source manifests were preserved exactly. The corrected controller diff changes only canonical input-layout preservation and its cache recipe.

The shared input cache's full bytes were rehashed. Every repeated block was compared directly to the permitted 2,016-row discovery arrays, including the final partial block. Costs remain unchanged. The returns retain Fortran order, characteristics retain C order, and inputs are read-only float64 memory maps. No actual validation or audit rows enter the workload.

The reviewer read all 49,892 daily economic rows and 49,894 individual candidate timing values across both workflows, verified their complete day sequence and endpoint counts, reconciled net arithmetic, and independently recomputed means, timing quantiles and quarter means. Runtime source checks confirm that every target was inspected and every subsequent full fee and closing exposure was reconciled; the recorded maximum errors are zero.

All six original prefix array files—forecasts, targets and held books for each candidate—match their original discovery SHA-256 identities exactly. The original 1,762 economic rows also match exactly for each candidate. Independent reconstruction from saved prefix targets, held books and input returns reproduces prefix gross returns, drift and full fees with maximum error zero.

## Scope and retained failure

Only the original target/held prefix was saved, as specified prospectively. Later per-stock target arrays cannot be reconstructed independently from daily aggregates. The full-path fee/position checks were performed during the frozen execution; the readback independently reconstructs the saved prefix and verifies all complete daily/timing records. It does not claim an independent post-run reconstruction of unavailable later targets.

The earlier C06 century fixture's historical-byte mismatch remains a retained failed run in `evidence/C06_long_history_001`. The standard discovery reconstruction reproduced the originals exactly, and the corrected fixture preserved their input memory order. The successful replacement did not change the candidate, configuration, scorer, exact historical expectations or numerical tolerances.

Repeating discovery data is an engineering workload. It is not a century of independent returns or evidence of alpha, and no synthetic Sharpe ranking is inferred. The review identifies no remaining engineering blocker within this scope. The broader causal, protected-evaluation and final clean-package gates remain governed by their own evidence.
