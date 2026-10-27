# Preserve canonical input layout in verification fixtures

27 October 2026, Europe/Paris. Corrective E2E fixture plan, written before the controller edits and replacement runs. No candidate, scorer, configuration, score window, perturbation recipe, tolerance or market selection rule changes.

## Observed failure and independent evidence

The first C06 century workflow stopped before rebalance because its forecast prefix did not match the historical `.npy` hash. The legacy causality worker's 2,016-row baselines had exactly the same differing forecast hash as that century prefix; all protected future comparisons within that representation were exact. The original combined historical reconciliation correctly failed and is retained.

The standard discovery runner was then rerun unchanged as `evidence/discovery_C06_repro_20261027`. Its forecasts, targets and drifted held books reproduce all three original C06 file hashes exactly, and its net Sharpe is identical. Thus the historical arrays have been reconstructed exactly; earlier unavailable-array and unverified hardware-portability explanations are superseded.

The concrete fixture difference is memory order. The canonical discovery return file is Fortran-contiguous with strides `(8,16128)`. The legacy causality worker's default `.copy()` and the initial century fixture convert it to C-contiguous layout. Numerical values, source and configuration are unchanged. NumPy reductions and linear algebra can accumulate floating-point arithmetic differently under different strides. Current C-layout versus canonical reconstructed F-layout maxima are about `5.21e-18` for forecasts and `1.51e-15` for targets, all within the already fixed causal tolerances. Those observations support the representation explanation; they are not a threshold change or evidence of lookahead.

## Required correction and unchanged expectations

1. Keep all original failed/complete packets and their frozen controller/worker copies unchanged. Do not relabel the old byte-identity failure as a pass. The existing C-layout causality observations remain a separate tested representation.
2. Correct only verification input construction. Copies of canonical returns and characteristics preserve their original C/F order. Prefix truncation preserves that order. Synthetic append explicitly preserves the original order as well. Perturbation values and protected masks remain byte-identical numerically. Record actual shape, strides and contiguity in new worker evidence.
3. The century cache creator derives `fortran_order` from the source array instead of defaulting all arrays to C. Include the source layout in the cache recipe so the old incompatible cache cannot be silently reused. Use a new cache and evidence directory. Read-only flags, bounded memory use, deterministic tiling and source-array hashes stay unchanged.
4. A different reviewer inspects the narrow controller diff before execution. The existing exact historical array-hash and economic gates remain binding, alongside their existing future-alteration checks. No new postimplementation isolated tests are written; execute the already specified complete E2E workflows against the corrected fixtures.
5. Rerun the same 39 C06 scenarios on canonical layout in new group directories and preserve the same cutoffs, prefix/append recipes and numerical tolerances. Freeze the corrected worker identity before the C09 19-scenario profile begins. The C09 prelaunch admission records the worker change transparently.
6. Repeat C06's full century workflow using the original historical C06 reference, not a more convenient new target. Require all original forecast/target/held-book hashes and prefix economics. A later nominee uses the same corrected controller with its own original record. If exact reproduction still fails, preserve the failure and investigate it before releasing protected evaluation.

Successful replacement runs will establish canonical-layout causal/reproduction/runtime evidence under their stated scope. They will not erase the earlier fixture failure, certify all histories, or establish alpha. Protected validation and audit remain closed until the full admission gate is satisfied.
