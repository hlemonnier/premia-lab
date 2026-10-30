# Selected C09 handoff: clean-folder discovery equivalence

**27 October 2026, Europe/Paris.** The selected C09 handoff completed the original-scorer discovery workflow with exact agreement to the saved canonical C09 run. This is packaging verification of the already selected policy. It adds no model, fitted parameter, validation candidate, or audit observation.

## Prospective construction and review

The root approved `verification/HANDOFF_ENGINEERING_PLAN.md` before the verifier and wrapper. Its SHA-256 is `f9b052fbd78b732397a1f9d0154e7fe342b7b2095ca4cda15ebf6922c68bc10f`. The verifier was written and frozen before the wrapper; root independently inspected its complete source and authorized the selected package only after the expected missing-wrapper run. The source is `tools/verify_handoff.py`, SHA-256 `2b3c12d17b599940d37b19ac0609442d9b963a465ce7db139b45f9107dd5b739`.

`evidence/handoff_build_order_001` preserves the pre-wrapper plan/controller snapshots, construction record, and observed expected-red result. `evidence/handoff_red_001` exited **1**, with status `EXPECTED_RED_MISSING_WRAPPER`, zero strategy/scorer workflows, and no numeric input access. Its 12 recorded artifact hashes were read back successfully. The expected failure establishes the construction order; it is not a strategy pass.

Root selected C09 using the previously frozen validation rule, recorded in `research/VALIDATION_SELECTION.json`, SHA-256 `941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa`. The chosen configuration remains `research/configs/C09_additive_long_memory.json`, SHA-256 `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`.

Root independently reviewed the exact four-file package, literal configuration, unchanged helper bytes, direct function aliases, and full explanatory note before green execution. A documentation-only correction changed “paired discovery criterion” to “fixed parent-comparison criterion,” avoiding any implication that the C12 comparison was a statistical paired-test rejection. Both note versions and their hashes are preserved in `evidence/handoff_implementation_001`; no executable policy changed. The final note and package were frozen before the green replay and have not subsequently changed.

## Executed workflow and identities

`evidence/handoff_discovery_001` contains the complete original-scorer run, setup, command, fresh-destination rerun command, frozen controller/package/configuration/reference files, environment, worker logs, full output arrays, economic ledger, timing array, and artifact manifest. The canonical reference was `evidence/discovery_C09_repro_20261027`; inputs were the original discovery cache on `[0,2016)`.

The worker ran in a fresh isolated interpreter on CPU 7 with numerical-library thread counts set to one. The clean folder contained only the deployment package and the unchanged supplied scorer. All imported project modules resolved inside its local `model/` package. Read-only float64 returns retained Fortran layout and strides `(8,16128)`; characteristics retained C layout and strides `(104000,104,8)`. No validation or audit numeric inputs were opened by this workflow.

The controller exited **0**, status `EXECUTED_PASS_SCOPE_ONLY`: **15 controller checks and 26 worker checks passed**, with one forecast and one original-scorer workflow. Saved-evidence readback by the controller's author rehashed all **36** recorded artifacts, reconciled the expected counts, checked the original output identities, and confirmed that the current handoff still matched the frozen package. This author readback is separate from root's independent source review and any independent final evidence review.

| Output | Executed result |
|---|---|
| Forecasts | `(2016,1000)`, exact original C09 `.npy` hash |
| Targets | `(1763,1000)`, earning indices 253–2015, exact original hash |
| Held books | `(1763,1000)`, exact original hash |
| Economic ledger | 1,762 rows on `[253,2015)`, all gross returns, full costs, net returns, closing exposures, and market returns exact |
| Accounting | Empty opening book; free opening trade recorded; complete drift/gross reconciliation; all subsequent fees including closing costs retained |
| Integrity | Source, scorer, literal/actual configuration, frozen controls, input bytes, and final package unchanged |

The exact output SHA-256 identities are:

- Forecasts: `00e1a6f1c926528958f648f3da4693294b8a428bbdb8f994e1c4d3f1289f9b25`.
- Targets: `bbaa32291f9b9cab008288d32fe25a6e687e4d54e4328bbe009a7fe9e033a5c2`.
- Held books: `bbfb2c76e6c72943c342a507163528b9dd0b408c795ede0b34a4abb8b355f0ae`.

The replay reproduced discovery net Sharpe `0.7001546509305844` and net market beta `0.014403642679765905` exactly. These repeat existing discovery observations and supply no new independent performance evidence. Measured candidate forecast time was `3.2396843010010343` seconds; mean rebalance time `2.2797880124752083` milliseconds; maximum `14.816764998613507` milliseconds. The already executed canonical 25,200-row runtime gate remains the long-history evidence; no discovery extrapolation replaces it.

## Frozen package and next gate

The discovery-verified package manifest is `evidence/handoff_discovery_001/package_manifest.json`, SHA-256 **`97ec4469c51311730d906a68bd594ecd48b75d87bb29f0beccb6f7e3e5d8d813`**. The audit nomination must bind that hash in `handoff_package_manifest_sha256` before audit access.

| Package member | SHA-256 |
|---|---|
| `strategy.py` | `7f15248160efd09e65d7dcf4d79cb1c5c4897d87641f2c2057f8566c7de7d946` |
| `model/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `model/strategy.py` | `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7` |
| `model/portfolio.py` | `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` |

The main green summary hash is `095fa56f8b52758e504bfbdd035204a878a1dcda638d63a355f08c72353c423f`; its complete artifact-manifest hash is `0127583d2e174abf30e3381b4cd289f490a6fa4b24b4a383d9343f1e88e2f306`.

The full audit wrapper replay remains **unexecuted** in this record. It requires root's explicit release, a completed canonical selected-engine audit, the exact bound discovery-verified package, and all `[0,3780)` forecast/target/held/economic outputs compared exactly. No post-audit model or wrapper change, additional candidate, or relaxed tolerance is authorized. Finite causal and packaging checks do not establish absence of overfitting or future profitability.
