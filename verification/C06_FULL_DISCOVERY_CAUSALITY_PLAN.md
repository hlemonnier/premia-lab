# C06 full discovery causality gate

Date: 27 October 2026, Europe/Paris. This is the prospective execution profile for the unchanged C06 candidate. Raw evidence timestamps use UTC. The plan is written before this execution; no pass is claimed here.

## Purpose and authority

Apply the existing `CAUSALITY_PLAN.md` and `GLS_CAUSALITY_EXTENSION_PLAN.md` to the complete permitted discovery input `[0,2016)`. Use the unchanged `tools/verify_causality.py`, unchanged supplied scorer, and exact `research/configs/C06_gls_factor.json`. This is verification of an already scored configuration, not another selectable model or an alpha-ranking run. No validation or audit outcomes may be read.

The earlier conversation described interrupted work whose temporary files became unavailable after workspace resets. None of those unavailable outputs is counted as a pass. This new packet starts from byte-verified committed source and the original discovery cache. Earlier committed evidence remains authoritative for the original discovery experiment.

## Failure modes and expected outcomes

The gate detects a protected forecast, target, or economic ledger changing when only its future input changes; future-informed transformations or risk state; full-length-dependent fitting schedules; carried process/module state; input mutation; and evidence that silently drops scenarios, mismatches masks, or substitutes source. Source review separately examines prohibited file/network access and forecast-to-portfolio state contamination.

Forecast row `t` must use observations before `t`. The latest fit pair is `X[t-2] -> R[t-1]`, with label beta and precision estimated from `R[:t-1]`. Rebalance for earning day `t` sees history of length `t`, ending at `t-1`. The original scorer's first trade is free; closing costs are charged in full; its final input return is not earned.

If rows `[c:]` change, all forecast channels at rows `[0,c+1)` and targets for earning days `<=c` must agree. Gross return, costs, net return, exposure and market-return ledgers are compared only on score days `<c`. Cutoff-day costs can legitimately differ. For a prefix of length `p`, compare all forecast rows `[0,p)`, targets through earning day `p-1`, and score rows `[253,p-1)`. The 64-row synthetic append must preserve all outputs on the original common masks.

Default expectation is exact deterministic equality. The existing harness additionally reports fixed roundoff tolerances `atol=1e-14`, `rtol=1e-12`; no tolerance will be enlarged after inspecting results. Exact equality and maximum errors will be reported independently. Empty ranges are not applicable, never active trading coverage. A worker error or timeout makes its unavailable comparisons unverified; a suffix failure alone is not proof of prefix leakage.

## Frozen scope: 39 fresh interpreters

Three independent controller invocations each run a baseline, repeat, three cutoffs with return-only/characteristic-only/joint alterations, one shorter prefix, and a synthetic append: 13 workers per group, 39 total. Extra baselines/repeats/appends are explicit duplicated infrastructure, not independent statistical alpha trials.

| Group | CPU | Cutoffs | Prefix length | Append |
| --- | --- | --- | --- | --- |
| A | 2 | 127, 147, 253 | 504 | 64 synthetic rows |
| B | 3 | 254, 273, 274 | 1008 | 64 synthetic rows |
| C | 4 | 275, 1008, 2015 | 2015 | 64 synthetic rows |

The union covers first active forecast127; first active learner factor refresh147; initial traded target253; first marginal-risk rolling eviction254; learner factor refresh after window eviction273; portfolio refresh274 and reuse275; a later midpoint1008; and the final input row2015. Learner startup refreshes at prior-history counts20 and41 produce only warmup-zero forecasts and no traded targets. Their control flow is source-reviewed rather than counted as active numerical coverage. Candidate-independent startup cutoffs0/1/251/252 and every repeated refresh are not separately executed here. The scope is representative, not exhaustive.

Return suffixes are multiplied by0.5. Characteristic suffixes are reversed in time; a one-row suffix is replaced with the first permitted panel. Joint scenarios apply both. The unchanged worker verifies nonidentity changed-element counts, exact protected input prefix equality, finite shapes and nonnegative fixed costs. Synthetic append reuses the first64 discovery panels in reverse order and halves their returns. No actual hidden observations enter these scenarios.

Each worker is a new Python process; one BLAS/OpenMP thread and one pinned CPU are fixed before numerical imports. Worker timeout is600seconds, a safety stop rather than a runtime-eligibility threshold. The unchanged original scorer drives the complete serial book. Candidate source/configuration and bounded cache are frozen inside each group before workers begin.

## Inputs and identities

Expected discovery array-file SHA256 identities:

- `returns.npy`: `563cbcab745cc6ffc9d04739fd49a64a7881e3cfee81f2a157080a6336c3ba04`
- `characteristics.npy`: `5b95d6c1ceb7c8a9209ca76fc6e7116f4b496933fe64771029a1192737fed1f4`
- `costs.npy`: `8a80bf28efe25c9e33e05c5a0d89b3787459fbcf51f7b4f378c2ba0c8e992ee1`
- Original scorer: `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

The admission manifest records current hashes for the seven imported candidate/helper files, config, protocol, both existing plans, this supplemental plan, verifier, and original C06 summary/daily/source/input records. Candidate dependency hashes, config, scorer and protocol must agree with `evidence/discovery_C06_001/source_manifest.json`. All three groups must freeze an identical candidate file set; later unrelated new candidate modules do not invalidate the frozen dependency closure. No live module is modified to facilitate this gate.

## Exact execution and evidence

From the project root, use the primary runtime Python with `taskset -c CPU`, the unchanged verifier, `--project . --strategy submission/strategy_gls_factor.py --config research/configs/C06_gls_factor.json --days 2016 --cuts CUTS --prefix-days PREFIX --append-days 64 --timeout-seconds 600`, and unique output directories `evidence/C06_causality_A_001`, `evidence/C06_causality_B_001`, `evidence/C06_causality_C_001`. Admission records resolve the executable and complete exact commands before launch. Each group retains its own exact frozen rerun command; a same-affinity wrapper is retained beside it.

Every controller/worker retains setup, input/source identities, frozen candidate/config/scorer, expected masks, actual per-check comparisons, protected arrays, daily ledgers, environment, return code, stdout/stderr and immutable completed status. The three input snapshots are verification copies of discovery only. Large binary evidence may remain reproducible untracked artifacts under the existing repository policy; committed hashes and logs must not claim unavailable bytes remain present after an environment reset.

## Independent saved-output reconciliation

A separate reporter, written before these runs complete, reads the saved evidence without fitting a model or inspecting another market interval. It must verify:

1. Exactly the39 declared scenarios and their complete expected masks exist; each worker actually completed with exit0 and all input/position checks. Worker PIDs must be distinct within and across groups.
2. All three controller manifests, frozen inputs/source/config/protocol/scorer/runner/worker/plan files match their recorded hashes; worker source/config/scorer identities and before/after input identities agree. The supplemental plan and admission identities remain unchanged. A controller's boolean status alone is insufficient.
3. Every saved forecast, target index/array, score index and economic array has its exact expected shape/mask. Every protected numeric array is compared directly against its group's baseline; wall timing is excluded from numerical invariance assertions. Each changed suffix actually changed the promised fields.
4. The three baselines agree exactly on all forecasts/targets/economics. Baseline forecast and target `.npy` serializations match the original C06 output hashes in its committed summary; baseline economic daily columns match the original C06 daily ledger, excluding runtime columns. This connects this gate to the model that produced the discovery result, not merely three self-consistent new runs.
5. A final outcome lists completed, failed, unavailable and empty checks separately, with exact-error maxima and remaining limitations. No unavailable comparison is inferred from source review or shared helper ancestry.

## Interpretation and remaining gates

A pass supports no detected lookahead on these tested paths plus the independent source audit. It is not a proof for all histories, and it does not establish an investable edge or absence of research overfitting. Eleven configurations and prior diagnostic/design decisions were already exposed on discovery. Selection among them is adaptively optimistic even if every decision is temporally causal. Protected chronological validation, one frozen audit candidate, long-history runtime and final clean-folder reproducibility remain separate gates. No result from this causality run permits a model change, budget expansion, or hidden-period retuning.
