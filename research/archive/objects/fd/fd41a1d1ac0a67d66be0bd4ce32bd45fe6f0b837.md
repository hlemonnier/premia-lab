# Independent readback of the unchanged-package real replay

28 October 2026, Europe/Paris. Reviewer: independent V2 causality/state auditor.

**Approved for descriptive reporting, with the scope below.** This review read the root's prospective replay plan, paired-ledger plan, preserved wrapper failures/amendments, replay source, paired-readback source and outputs. It independently recalculated saved-ledger metrics and verified inputs/source/artifact hashes. It did not execute either strategy, refit a model, select a variant, rerun the bootstrap or introduce new tests.

## Identity and actual performance

- Both replay CSV-input manifests agree with the original C09 canonical input manifest. Independent streaming SHA256 checks of the restored `returns.csv`, `characteristics.csv` and `costs.csv` also agree with those canonical identities.
- All successful-run source files match their manifests and the intended original packages. The V2 `.py` files match pinned `afed8d0cb017acda151c4ea262fc30db7568a4bb`; C09 matches the existing handoff. Both use the original scorer hash `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.
- Every file listed in the two successful artifact manifests exists and its SHA256 matches. No input, source or artifact identity discrepancy was found.
- Both saved ledgers have exactly 3,526 aligned earning rows, zero-based 253 through 3778. Independently recomputed stage counts and net Sharpe, annual net return, annual volatility, annual fees, realized net beta and gross exposure agree with the root summaries to at most `2.22e-16` absolute.
- C09's four comparable economic fields agree with the earlier canonical ledger to a maximum absolute difference of **`5.218048215738236e-15`**, exactly the value reported in the root summary. This passes the prospectively stated `1e-10` portability threshold and is not bitwise equality.

| Net Sharpe | C09 | Packaged V2 |
|---|---:|---:|
| Full run | 0.8848112283903203 | 1.2425030733031566 |
| Discovery | 0.7001546509305838 | 1.0980016385754545 |
| Validation | 0.6592096865251774 | 1.6568592904246344 |
| Former audit | 1.7992307122434619 | 1.1475575640626992 |

These rows reproduce the reported three-decimal values. They provide fresh execution evidence for unchanged code; they do not turn V2's exposed periods into clean confirmation.

## Paired calculation

The paired source, plan and ledger hashes match `paired_readback.json`. I independently recovered its saved-CSV Sharpe difference **0.35769184491283** and correlation **0.6954191834581044** exactly. The source uses the same sampled dates for the two ledgers, preserves the original `ddof=0` convention and resets the specified RNG seed per fixed sensitivity calculation.

The corrected block-start upper bound is `n-L+1`, which includes the legal last start `n-L` under NumPy's upper-exclusive integer draw. The original uncorrected convention is retained separately. The reported saved percentiles are:

| Block length | Convention | 95% percentile range |
|---|---|---|
| 63 | Original endpoint omission | [-0.0020303445, 0.8195337072] |
| 63 | Corrected endpoint | **[-0.0031676483, 0.8245358481]** |
| 21 | Corrected endpoint | [-0.0351108377, 0.7671686823] |
| 126 | Corrected endpoint | [-0.0321028711, 0.8809777826] |

All include zero. These are the root's saved, hash-bound interval outputs; their numerical bootstrap was not independently rerun in this peer readback. Source review finds the calculation consistent with the recorded specification.

**Scope must stay explicit:** this compares packaged V2 (`gamma=200`, stock cap 5%, gross cap 5) with original C09. It is not the missing original interval for the unlevered `fr_beta_phi03` research variant. The positive bootstrap fraction is not a posterior probability, selection-adjusted p-value or probability of future outperformance. Block-length sensitivity does not correct full-sample model selection or establish stationarity.

## Preserved harness failures

The original C09 observer failed because it omitted the required `trading_costs` forecast argument. The second observer forwarded an unsupported characteristics argument to C09 rebalance. The tracebacks support the recorded diagnoses. Both attempts produced no scored ledger; the corresponding paired invocations failed on the missing ledger. These are audit-wrapper failures, not strategy failures.

The successful third C09 attempt uses the scorer's own declared-argument adapter for both delegated calls. The failure/amendment record changes output paths and argument plumbing while preserving strategy bytes and the paired calculation's methodology. The earlier successful V2 replay was retained without repetition. Presenting all three C09 attempts and their statuses is accurate.

## Artifact

Detailed independent identities and arithmetic are in [REAL_REPLAY_PEER_READBACK.json](REAL_REPLAY_PEER_READBACK.json). This approval concerns provenance, timing scope and saved-ledger arithmetic. The separate allocator reviewer owns optimality diagnostics, and the research reviewer owns the interpretation of risk calibration and alpha claims.
