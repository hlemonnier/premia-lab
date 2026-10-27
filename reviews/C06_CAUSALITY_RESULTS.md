# C06 causality and historical reproduction: completed disposition

27 October 2026, Europe/Paris.

**Result: the canonical-layout C06 gate passed within its specified scope.** All39 fresh-process workflows completed, every nonempty protected numeric comparison was exactly equal, and all three baselines reproduced the original discovery forecast/target file hashes and daily economics exactly. Source review found no timing violation in the imported candidate/helper closure. These findings support no detected lookahead on the inspected and executed paths; they do not establish absence of research overfitting or an investable edge.

## Evidence that supports the result

The binding execution profile is `verification/C06_FULL_DISCOVERY_CAUSALITY_PLAN.md`, supplemented by the preserved PID-scope clarification and `verification/INPUT_LAYOUT_CORRECTION_PLAN.md`. Replacement admission is `evidence/C06_causality_admission_003/admission.json`. Its39 workers are divided across `evidence/C06_causality_A_002`, `evidence/C06_causality_B_002` and `evidence/C06_causality_C_002`. The independently reviewed saved-output reconciliation is `evidence/C06_causality_reconciliation_002/summary.json`.

| Completed evidence | Actual outcome |
| --- | --- |
| Three baselines and36 comparison scenarios | All39 workers completed with exit0 |
| Original controller comparisons | 192 passed;24 empty components not applicable;0 failed |
| Independent direct numeric comparisons | 120 passed;24 empty components not applicable |
| Nonempty protected numeric discrepancies | Exact equality everywhere; maximum absolute error0 |
| Independent identity, mask, layout, process and comparison checks | All1,209 passed |
| Original discovery forecast hash, each baseline | `0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0` |
| Original discovery target hash, each baseline | `b4f2365512f31aa0dbf77e1e1bcfa9c32b187aa47ab516c5c0d878c42127d886` |
| Original daily gross return, full cost, exposure, market return and net | Exact equality for all1,762 scored discovery rows |

The120 numeric checks and72 index checks account for the192 controller passes. They are engineering assertions, not independent observations or alpha trials. Empty components arise where the protected target/score range precedes active trading, including the127/147 warmup-boundary scenarios and the253 first-target boundary; they are not credited as trading-path coverage.

All actual market inputs came from discovery rows `[0,2016)`. The fixed cutoff union was127,147,253,254,273,274,275,1008,2015. Every cutoff had return-only, characteristic-only and joint future alterations. Prefix lengths were504,1008,2015, with a64-row synthetic append in each group. Baseline and repeat initialization used separate interpreters. Worker IDs were checked within their controller namespaces, with distinct `(group, PID)` identities and matching parent records across all39 invocations.

For an alteration beginning at row `c`, every forecast channel through row `c` and every target for earning day `<=c` was protected; economics were compared strictly before `c`. This respects the supplied scorer's closing-cost timing. Exact scenario masks, actual transformed-input hashes, source/config/scorer/protocol identities, all worker input layouts and actual saved output arrays were checked directly, not inferred from status labels alone.

## The retained failure and why the fixture was corrected

The initial39 workflows, in group001 directories, also produced exact within-run protected-output invariance. Their original combined historical reconciliation nevertheless failed its exact forecast-byte requirement. That failed report is preserved at `evidence/C06_causality_reconciliation_001`; it has not been renamed a pass.

The discovery return file is Fortran contiguous. The standard discovery runner preserves that representation, while the old causality worker's default array copies converted returns to C order; the first century fixture also used C order. Numeric input values and all candidate/source/configuration identities were unchanged. The current C-layout2016-row forecast matched the first2016 rows of the C-layout25200-row workload exactly, so the historical hash mismatch did not indicate a length-specific future-data effect.

The unchanged standard C06 discovery rerun in `evidence/discovery_C06_repro_20261027` then reproduced the original forecast, target and drifted-held-book hashes exactly. That recovered hash-identical historical arrays and ruled out the earlier unresolved historical-portability concern for the standard workflow. Comparing the C-layout verification baseline with those original-equivalent arrays yielded maximum forecast error `5.204170427930421e-18` and target error `1.5061736580168628e-15`. Every value lay inside the already fixed `atol=1e-14, rtol=1e-12`. Maximum historical net-ledger discrepancy was `7.723856276786734e-16`; exposure discrepancy was `1.787459069646502e-14`, which is covered by the combined absolute-plus-relative tolerance, not by an assertion that it is below the absolute tolerance alone.

The separate diagnostic report `evidence/C06_causality_current_disposition_001` preserves this distinction: current C-layout invariance passed, standard historical reproduction passed, and the original C-versus-F exact-byte assertion failed. It does not waive or rewrite the original gate.

The root then wrote the corrective fixture plan before edits. A different agent reviewed the narrow fix: preserve source element order in initial and prefix copies, explicitly preserve F/C order when appending, and record actual shape, strides, dtype and contiguity. No candidate, scorer, configuration, perturbation values, protected mask, tolerance or alpha-selection rule changed. The corrected verifier SHA256 is `b46df7ed7e3dec9677a7d855ca6b082c872a7c15ce645eaf15f5246f475cdc83`; before/after code, plan and review are preserved in `evidence/C06_causality_layout_correction_001`.

The same39 complete workflows were rerun against the canonical representation in new group002 directories. This time the original exact historical gate and all future invariants passed. The successful replacements do not erase the initial fixture failure or create another selectable alpha configuration.

## Source reasoning and remaining limits

`reviews/C06_CAUSALITY_SOURCE_AUDIT.md` records the independent review. Forecast row `t` consumes the most recent matured pair `X[t-2] -> R[t-1]`, with label beta and precision constructed from history before that label. Panel transformations use the one published characteristic cross section. Learner fitted state is local to `forecast`; portfolio factor state is initialized and advanced only by serial `rebalance` on available history. The dependency closure has no market-file/network reads or future-fitted object transferred into portfolio decisions. The unchanged original scorer still applies position drift, free opening trade, full subsequent closing costs and its original endpoint convention.

The executed paths are representative rather than exhaustive. Startup refreshes that only produce zero warmup forecasts were source-reviewed; arbitrary external API call sequences and every conceivable future history were not numerically enumerated. Century runtime, protected validation, locked audit and clean-folder execution are separate gates with their own evidence; this report does not infer their outcomes.

C06 was selected for further engineering after discovery comparisons and diagnostic choices. Exact causal behavior does not remove that selection optimism. The configuration budget, complete exposure ledger, chronological finalist freeze and untouched audit remain necessary. No new market data, candidate variant or parameter tuning occurred in this causality work.
