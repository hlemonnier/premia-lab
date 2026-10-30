# C09 full discovery causality gate

**Prospective execution profile, 27 October 2026, Europe/Paris.** This plan is written before any C09 workflow in this continued-work session. It applies the existing `verification/CAUSALITY_PLAN.md` and the independently reviewed canonical-layout correction in `verification/INPUT_LAYOUT_CORRECTION_PLAN.md` to the exact previously scored C09 policy. The earlier unexecuted profile remains preserved in `evidence/C09_causality_admission_001`. It is not a new selectable model, alpha variant, or holdout evaluation.

## Candidate and information boundary

Use `submission/strategy.py` with `research/configs/C09_additive_long_memory.json`: C02's unchanged 26-column additive basis and diagonal portfolio, with the already admitted 1,008-day coefficient half-life. All remaining settings stay fixed. The directly imported project dependency closure is `strategy.py` plus `portfolio.py`; incidental additional modules copied by the existing harness are also frozen and checked but are not C09 imports.

At forecast row `t`, the newest pair is `X[t-2] -> R[t-1]`; beta for that label is estimated from `R[:t-1]`. Prediction uses only `X[t-1]`. The first potentially nonzero forecast is row 127. For an earning-day target `t`, the original scorer supplies return history ending at `t-1`. All fitted forecasting state is local to the invocation; no coefficients or learned object seed rebalance. Source review also covers deterministic preprocessing, absence of file/network reads, state reset, and the portfolio's use of actual drifted holdings.

## Failure modes and fixed expectations

Detect future-dependent forecasts, changed protected targets/economics, full-length-dependent fitting, reused mutable fitted state, input/held-book mutation, incorrect intervention masks, unrecorded worker failures, and substituted source/configuration/input identities. A changed suffix must actually change its declared inputs and leave the earlier prefix exact. A suffix error does not prove prefix leakage; an unavailable comparison remains unverified.

For alteration at `c`, protect forecast rows `[0,c+1)`, targets for earning days `<=c`, and economic score rows `<c`. Cutoff-day closing costs are outside that last mask and may change. For prefix length `p`, protect forecasts `[0,p)`, targets through `p-1`, and economics `[253,p-1)`. For appended synthetic rows, protect the entire original common interval, including forecasts `[0,2016)`, targets 253 through 2015 and economic rows 253 through 2014. The final supplied return remains unearned in the original 2,016-row replay.

Current-environment deterministic equality is expected and will be reported explicitly when observed. The unchanged verifier's numerical acceptance remains `atol=1e-14`, `rtol=1e-12`; neither is enlarged after results. Report maximum errors and distinguish exact equality from tolerance acceptance. Empty numerical ranges are `NOT_APPLICABLE`, not active portfolio coverage. With the profile below, the 18 nonbaseline cases generate 108 comparison records; 15 numerical records have declared empty masks and 93 are expected to pass if the workflows are sound. Index checks on empty arrays still establish the correct empty mask, not an economic observation.

## Exact scope: nineteen fresh processes on CPU 7

Use all and only permitted discovery input rows `[0,2016)`, with one baseline, one identical repeat, three alteration modes at each of five cutoffs, one prefix, and one append:

| Cases | Boundary | Purpose |
|---|---|---|
| baseline and repeat | 2,016 rows | Complete unchanged replay and process-state determinism |
| returns / characteristics / joint suffixes | 127 | First active forecast; no traded protected targets |
| returns / characteristics / joint suffixes | 253 | First target; no protected scored economic row |
| returns / characteristics / joint suffixes | 254 | First full-cost economic observation and risk-window eviction |
| returns / characteristics / joint suffixes | 1008 | Later-history dependence |
| returns / characteristics / joint suffixes | 2015 | Final supplied-row behavior |
| shorter prefix | 1,008 rows | Invariance to absent later observations |
| synthetic append | 64 rows | Invariance to added later observations |

Return suffixes are multiplied by 0.5. Characteristic suffixes are reversed in time; for a one-row suffix the existing worker substitutes the first permitted panel. The joint case combines these interventions. The append takes the first 64 permitted panels in reverse order, scaling their returns by 0.5. It does not read actual validation or audit rows.

Each scenario runs a fresh Python interpreter under the corrected fixture controller, CPU 7 affinity and one numerical-library thread. Use a 600-second child timeout. That timeout is a failure/incompleteness boundary, not an assignment-runtime pass. Require nineteen distinct worker PIDs within this one controller's PID namespace and each child's recorded parent PID equal to this controller's PID. Do not compare numeric PIDs globally against separately launched execution namespaces.

From the project root, using the primary runtime Python resolved and saved in the admission manifest:

```sh
taskset -c 7 python -u tools/verify_causality.py --project . --strategy submission/strategy.py --config research/configs/C09_additive_long_memory.json --out evidence/C09_causality_001 --days 2016 --cuts 127 253 254 1008 2015 --prefix-days 1008 --append-days 64 --timeout-seconds 600
```

Save a CPU-affinity wrapper for the controller's exact frozen rerun. Output directories must not overwrite earlier evidence. Root approval of this plan is required before launch.

## Expected identities and admission record

- `strategy.py`: `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7`
- `portfolio.py`: `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475`
- C09 configuration: `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`
- Original scorer: `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`
- `returns.npy`: `563cbcab745cc6ffc9d04739fd49a64a7881e3cfee81f2a157080a6336c3ba04`
- `characteristics.npy`: `5b95d6c1ceb7c8a9209ca76fc6e7116f4b496933fe64771029a1192737fed1f4`
- `costs.npy`: `8a80bf28efe25c9e33e05c5a0d89b3787459fbcf51f7b4f378c2ba0c8e992ee1`

Before launch, preserve this revised plan, source review, exact command, configuration, existing causal plan, layout correction plan, protocol, corrected verifier, and historical C09 summary/daily/source/input/environment identities in `evidence/C09_causality_admission_002`. The corrected verifier SHA-256 is `b46df7ed7e3dec9677a7d855ca6b082c872a7c15ce645eaf15f5246f475cdc83`; the correction plan SHA-256 is `9de0b82594939ab1c906b2ead82837c7c8a6ccf272753a06c97fd3b44d26739c`. Verify the imported source, config, scorer and protocol against `evidence/discovery_C09_001/source_manifest.json`. The controller freezes its complete source and input copy before executing the baseline. No candidate source changes are part of this gate.

## Saved-evidence reconciliation

Before reporting a pass, inspect the saved files rather than relying only on a controller boolean. Require all nineteen declared scenarios and exact masks; complete worker return codes, source/config/scorer identities, before/after input hashes and held-book checks; exact shapes and date sequences; verified saved-output hashes; declared process controls; and final frozen-artifact integrity. Directly compare every saved protected numeric array to the matching current baseline. Baseline targets must respect the frozen stock/gross bounds. Baseline saved consecutive targets and the permitted returns/costs must reconcile the scorer's drift-aware full fees and economics at the fixed tolerances. Do not claim the worker saved unprotected future targets that it intentionally omits.

Preserve setup, dependencies, source/input hashes, expected and actual outcomes, every worker manifest, command, PID record, stdout/stderr, status, protected arrays, daily ledgers and summary. Large reproducible binary arrays remain subject to the existing repository policy; their hashes do not imply they survive a later workspace reset.

## Canonical representation and historical reproducibility

The earlier profile's provisional historical-portability discussion is superseded before execution. The root's standard C06 discovery rerun reproduced every original forecast/target/held-book hash exactly. The old causality worker and first century fixture had instead changed the canonical Fortran-contiguous returns into C-contiguous copies. Original failed records remain preserved; this is a verification-fixture correction, not a model change or a relaxed numeric gate.

The corrected worker preserves each source array's C/F order for complete copies, prefixes and synthetic append. It records source and consumed shapes, strides and contiguity. For C09, require Fortran-contiguous returns and C-contiguous characteristics in every case, with the original values/intervention recipes unchanged. The frozen discovery returns file itself must keep its original identity. Prefix and append leading dimensions legitimately change strides; contiguity/order must remain canonical.

Current protected comparisons must pass their original masks and tolerances; exactness is additionally reported. Separately require the current baseline's forecast and target `.npy` serializations to match the original C09 hashes in `evidence/discovery_C09_001/summary.json`, and the original economic ledger to match numerically exactly when parsed as ordinary Python floats. Do not replace those historical references with a more convenient target. The worker does not save held books, so their historical reproduction belongs to the standard discovery and century workflows rather than an invented comparison here.

If canonical historical byte or economic equality still fails, preserve it as a failed gate and require explicit root investigation/disposition before nomination or holdout access. An unavailable historical array does not prevent comparing its recorded cryptographic identity; it does prevent claiming a numeric distance unless an exact-hash reconstruction is available. No tolerance enlargement, candidate change, or automatic admission follows a failure. Root's canonical standard-runner C09 reconstruction and the unchanged-source century workflow remain separate requirements.

## Interpretation and next gates

A complete pass supports no detected lookahead on the stated paths plus the independent source audit. It cannot prove universal causality, absence of adaptive selection overfit, or hidden-future profitability. This profile does not itself provide the long-history runtime gate or authorize validation/audit access. Those remain governed by the prospective protected-evaluation admission plan, explicit portability disposition, and a concrete frozen nomination manifest. There is no calendar execution schedule.
