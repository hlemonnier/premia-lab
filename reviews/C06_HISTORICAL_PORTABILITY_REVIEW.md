# C06 historical reproduction: independent evidence review

**27 October 2026, Europe/Paris.** This review reads already saved discovery ledgers and current causal/long-history outputs. It executes no candidate, accesses no protected market interval, changes no numerical tolerance, and leaves every earlier plan and failed run intact.

## Finding and disposition

The original exact historical forecast and target checksum requirements are **not met**. That failure must remain visible. The saved economic ledgers, however, agree within the numerical tolerances already frozen for causal comparisons: `atol=1e-14`, `rtol=1e-12`, using the historical values as reference. This narrower numerical reconciliation does not override an exact-checksum gate.

All three current C06 discovery baselines agree exactly with one another in forecasts, targets and economic ledgers. The saved 2,016-row forecast prefix from the 25,200-row long-history attempt agrees exactly with those current discovery forecasts, maximum absolute error zero. Therefore the observed historical mismatch is not confined to the longer input on this measured path. The long-history attempt nevertheless stopped at the historical forecast identity assertion, before any rebalance; it cannot be called a completed long-history workflow or runtime pass.

## Independent ledger measurements

The compared score mask is exactly rows `[253,2015)`, 1,762 rows in each ledger. Timing is excluded. Results are identical for current groups A, B and C:

| Economic channel | Maximum absolute historical/current difference | Number of exact differences | Exceeds frozen tolerance |
|---|---:|---:|---:|
| Gross return | 7.654467337747661e-16 | 1,704 | 0 |
| Full cost | 1.5343154806564396e-17 | 1,655 | 0 |
| Net return | 7.723856276786734e-16 | 1,697 | 0 |
| Closing target gross | 1.787459069646502e-14 | 1,194 | 0 |
| Raw market return | 0 | 0 | 0 |

The largest difference relative to its allowed `atol+rtol*abs(reference)` bound is 0.06031, or about 6.03% of that unchanged bound. Gross exposure has a maximum absolute error greater than the absolute term alone but remains below the combined absolute-plus-relative tolerance; neither component was relaxed.

Current net Sharpe recomputed from the ledger is `0.7629440478258805`, differing from the historical recomputation by `6.55e-15`. Current annualized net mean is `0.025906856670705716`, annualized net volatility `0.03395643067736232`, annualized full fees `0.006810310266232914`, and realized net-market beta `0.006330298621923452`. These are the same discovery economics to ordinary reporting precision. They do not provide an independent estimate of future alpha.

## What the available identities establish

The current worker-reported imported dependency hashes, explicit requested and consumed configuration, original scorer identity, and byte-verified frozen discovery cache hashes match the historical records. Recorded Python, NumPy, Pandas and SciPy versions, platform label and numerical-thread settings agree. CPU affinity labels vary by current group; group B uses the same numeric affinity label as the old run and has the same current outputs as groups A and C. A numeric CPU index is not a historical hardware fingerprint.

Historical forecast NPY SHA256 is `0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0`; the current discovery and saved long-history prefix share `d9ce03ba69f9a7a3419a489053c9944bcf3a79c76a5910240e721c5c60859ada`. The historical and current target NPY hashes also differ. The original forecast/target binary arrays were not persisted in the private repository and are unavailable locally after reset. A changed checksum does not measure numerical distance. This review therefore makes **no claim** that historical forecast or target values are within any tolerance.

Low-order economic differences with unchanged source and data are compatible with a numerical execution or portability difference. The old record lacks complete hardware, compiled-backend binary and execution-condition fingerprints, so BLAS, CPU dispatch, array alignment, or another specific root cause is **not established**. Current agreement across independent baselines is evidence of repeatability within the measured setting, not proof of cross-environment bitwise portability.

## Evidence-gate recommendation

1. Retain the original historical exact-checksum failures as failures. Do not replace their references, normalize their outputs, or edit their expected outcomes after the fact.
2. Report the completed same-setting causal comparisons separately from the unsuccessful historical binary reproduction. Do not label a combined reporter green if its exact historical requirement fails.
3. An exact standard-run C06 reproduction with unchanged source, configuration, input hashes and scorer can establish a newly persisted current-setting reference. If used, freeze that reference before a separate prospective long-history/reproduction attempt and document why it exists. It does not erase the old failure or measure the unavailable old forecast distance.
4. Require that separate attempt to satisfy its declared numerical identities and complete portfolio path before reporting long-history completion, runtime, or release readiness. Chronological validation and the sealed audit remain unopened until their own admission gates.

The reproducible read-only analysis, exact input-file hashes, all three group comparisons, worst-error dates, metrics, and rerun command are saved in `evidence/C06_historical_portability_review_001/analysis.py` and `evidence/C06_historical_portability_review_001/results/summary.json`. The analysis uses the original tolerance and does not fit, retune, rank, or execute a model.

## Later evidence on 27 October: exact standard reproduction and array layout

The preceding review records what was available at its execution time and remains unchanged as that historical observation. A subsequent unchanged standard-run reproduction at `evidence/discovery_C06_repro_20261027` completed successfully and reproduced **all three historical output-file hashes exactly**: forecast `0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0`, targets `b4f2365512f31aa0dbf77e1e1bcfa9c32b187aa47ab516c5c0d878c42127d886`, and held books `8cbfc1e2c61a58a2651ff9bb425a217ca18dceabcb6bd406f4883e4d0318c853`. Independent file hashing confirmed those identities. Its net Sharpe is exactly the historical `0.762944047825874`.

The historical forecast and target bytes are consequently available again through the hash-identical reproduction. The earlier statement that their numerical distance was unavailable is superseded by this recovery; it remains accurate for the original read-only analysis checkpoint. The causal-audit owner is measuring the C-order worker outputs against these recovered arrays under the original frozen tolerance, in a separate report.

A concrete input representation difference has also been identified and independently checked. The discovery return cache is Fortran contiguous, with strides `(8,16128)`. The unchanged standard runner preserves that mapping. The causality worker's ordinary `.copy()` creates a C-order return array. The original long-history fixture also used C order, with strides `(8000,8)`. Characteristic arrays use C order in both fixtures. Thus equal numeric values and cache identity did not imply an identical in-memory return layout in the different harnesses.

Exact historical reproduction on the current runtime makes a general inability to reproduce the old environment an unsupported explanation. The observed layout difference supplies a narrower, concrete mechanism consistent with floating-point reduction differences. Specific BLAS, hardware, or CPU causes remain unproven and are not asserted. A prospective long-fixture correction that preserves the original input layout, changes no candidate parameter or input value, and retains the original exact reference/gates is the appropriate narrow next check. Preserve the earlier C-order long-history failure and original combined-report failure rather than relabeling them.

The [official NumPy 2.3 summation documentation](https://numpy.org/doc/2.3/reference/generated/numpy.sum.html), in its Notes section, explains that the use of more precise partial pairwise accumulation depends on the reduced axis and its position in memory. This is primary documentation for the general numerical mechanism; it does not by itself identify the particular operation responsible for this project's last-bit differences.
