# C09 full discovery causality results

27 October 2026, Europe/Paris. **Executed pass within the declared scope.** No candidate source or configuration changed, and no validation or audit observations were read by this workflow.

## Execution and independent readback

`evidence/C09_causality_001` completed all nineteen fresh-process original-scorer workflows on CPU 7: baseline, identical repeat, returns-only/characteristics-only/joint suffix changes at 127, 253, 254, 1008 and 2015, prefix 1008, and append 64. The corrected fixture preserves canonical Fortran-contiguous returns and C-contiguous characteristics. The frozen worker is `b46df7ed7e3dec9677a7d855ca6b082c872a7c15ce645eaf15f5246f475cdc83`; the revised prospective plan is `32898d9ef59888b481269c41a4ae190930dc8ac05748463ce40a5050aa76d854`.

The controller produced **93 passing comparison records and 15 declared not-applicable numerical comparisons**. Empty economic ranges at early boundaries were not counted as trading coverage. The independent saved-output review in `evidence/C09_causality_admission_002/saved_evidence_review.json` completed 226 record checks and 73 numerical records: 57 nonempty protected comparisons, 15 empty ranges, and one independently reconstructed full baseline economic ledger. Every nonempty protected comparison and the independent ledger reconciliation was **exact, maximum absolute error zero**.

Readback checked actual source/configuration/scorer/protocol hashes; frozen input-file identities; nineteen distinct child PIDs in the controller namespace; all worker return codes and thread/CPU controls; declared interventions; actual array memory layouts; input and held-book integrity; output-file hashes; full forecast shapes and executed call counts; exact target/score indices; and saved baseline position limits. It inspected saved arrays directly instead of accepting a top-level pass flag.

## Connection to original discovery

The canonical baseline reproduces the original C09 forecast and target file identities exactly:

- Forecasts: `00e1a6f1c926528958f648f3da4693294b8a428bbdb8f994e1c4d3f1289f9b25`.
- Targets: `bbaa32291f9b9cab008288d32fe25a6e687e4d54e4328bbe009a7fe9e033a5c2`.

All 1,762 original economic rows match exactly after ordinary Python-float CSV parsing. Rebuilding gross returns, drifted trades, full fees, closing exposure and market returns from the baseline targets and permitted inputs also matches exactly. The original free opening and final closing-cost conventions remain intact.

The initial C09 proposal/admission was held before any worker ran while the separate C06 layout finding was resolved. That unexecuted proposal and its clarification remain in `evidence/C09_causality_admission_001`; the executed canonical-layout profile is admission 002. No C09 failed numerical run was discarded or converted into a pass.

## Reproduction and limits

The main workflow preserves its frozen rerun command and source/input copies. `evidence/C09_causality_admission_002/rerun_canonical.sh` adds the original CPU 7 affinity to that frozen rerun. The independent readback source is preserved beside its result; it intentionally refuses to overwrite the result, so preserve an existing result under a fresh name before rerunning it.

This is representative causal-path and source evidence for the fixed C09 policy. It is not proof for every history, freedom from selection overfit, or future profitability. Warmup target/economic ranges remain empty by design. Long-history runtime and protected market evaluation are separate gates; the century readback is documented separately.
