# Protected continuous replay: expectations before controller implementation

**27 October 2026, Europe/Paris.** This plan precedes `tools/run_protected_candidate.py`. It implements the frozen research protocol and `research/PROTECTED_EVALUATION_ADMISSION_PLAN.md`; it admits no new model, parameter, search, or calendar schedule. Actual protected access remains blocked until the lead freezes the concrete nomination/selection manifest and explicitly releases that execution.

## Purpose and failure modes

The controller replays one exact nominated policy through the unchanged official scorer, from an empty book at start252. It must prevent unauthorized protected numeric access, candidate/configuration substitution, altered source data, extra score periods, reset holdings or learned state at evaluation boundaries, incorrect endpoints, forgotten costs or drift, finite/output failures, and fabricated variance-based metrics. Evidence must identify every numeric input range actually accessed, including incomplete attempts. An interrupted protected attempt is never described as unopened.

First document this plan, then implement the controller, then obtain independent source review. Before any protected run, execute only the two prescribed complete workflow checks: bounded-discovery parity and a deterministic zero-return3024-row workflow. These are engineering runs of an existing exact C06 configuration, not additional selectable alpha configurations. Do not add a postimplementation isolated unit-test suite.

## Frozen replay modes and masks

| Mode | Numeric inputs | Reported score intervals | Expected scored counts |
|---|---|---|---|
| discovery-parity | Existing verified discovery rows `[0,2016)` only | discovery `[253,2015)` |1,762 |
| synthetic-zero |3,024 fully synthetic rows | validation A `[2016,2520)`, B `[2520,3023)`, pooled `[2016,3023)` |504,503,1,007 |
| validation | Canonical source rows `[0,3024)` after approval | Same validation masks |504,503,1,007 |
| audit | Canonical source rows `[0,3780)` after separate selected-policy approval | audit `[3024,3779)` |755 |

The full scorer always starts252 and executes continuously through its original endpoint. For input length D it returns D−254 economic rows for return indices253 through D−2, and emits D−253 targets earning on253 through D−1. No boundary resets, second free trade, or mean of block Sharpes is permitted. Pooled validation metrics are computed from the1,007 pooled daily rows. Validation row3023 and audit row3779 are final input rows not earned under the supplied scorer. The gap between score windows is fixed by the protocol, not adjusted for a favorable result.

## Protected-access manifest

For actual validation/audit, require both `--nomination-manifest` and its exact `--nomination-sha256`. Validate them before parsing any protected numeric source row. The root-owned manifest must contain:

- `schema_version:1`, `status:"ROOT_APPROVED_PROTECTED_REPLAY"`, and `stage:"validation"` or `"audit"`, matching the mode.
- Exact `protocol_sha256`, `scorer_sha256`, `admission_plan_sha256`, `replay_plan_sha256`, `controller_sha256`, and `metric_helper_sha256`.
- A nonempty `candidates` list of at most three frozen candidates for validation, or exactly one for audit. Each record supplies `candidate_id`, `strategy_path`, `config_path`, `config_sha256`, `source_sha256` mapping project-relative Python paths to hashes, `discovery_reference`, `discovery_reference_sha256` mapping relative evidence paths to hashes, `simplicity_rank`, `engineering_gate_status:"PASSED"`, and an `evidence` list.
- Evidence roles must include `source_review`, `causality`, `long_history`, and `controller_verification`, with exact project-relative `path` and `sha256`. An evidence item for an executed JSON gate also supplies its expected `status`, which must match the file and have exit_code0. Review prose is frozen by hash; the root's approval owns its interpretation.
- Audit additionally supplies `selected_candidate_id` and `selection_record:{path,sha256}`. The selection record must itself identify that candidate and its exact configuration hash. The controller does not select or retune a candidate.

Require the requested strategy/configuration/candidate to match one manifest record exactly, every nominated source and evidence hash to match, and the selected source closure to contain the entry point and all historical referenced candidate files. No source code is loaded from an unlisted sibling. The canonical discovery reference must be a completed original evidence packet whose source/config/scorer identities agree with the chosen policy. Freeze its summary, source/input manifests and daily ledger inside the new evidence packet. For audit, the selection record is also copied and hashed.

The nomination status is not a self-approval mechanism: the lead must create the manifest after the required engineering gates and explicitly authorize the actual run. In the pre-access controller checks, no such manifest is supplied or fabricated. Absence/mismatch is a hard stop before protected numeric parsing, not permission to fall back to an unrestricted mode.

## Numeric input construction and identity

The canonical raw source hashes are fixed from recovered input evidence: returns `6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d`, characteristics `46b9df20aebb324bd0026090d54f04bd6835283881dd73e728e90f16a5279a08`, costs `ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186`. Full-file hashing is permitted hygiene; numeric parsing is bounded by the approved mode. Never call the supplied unrestricted `score.load`.

For actual protected replay, parse only D return rows and D×1,000 characteristic rows, preserving exact day/stock/feature order. Use the same13 feature names and stock identifiers as the verified discovery cache. Validate dimensions, float64, finiteness, nonnegative costs and row alignment. Preserve canonical **Fortran-contiguous returns, C-contiguous characteristics**, and the original cost vector. Use a separate run-owned input folder, record source/output hashes, shape, strides and C/F flags, then reopen arrays read-only. The first2,016 numeric panels must be identical to the verified discovery cache before model execution. Do not inspect full-sample figures or numeric source rows beyond the approved length.

The discovery-parity mode copies the three byte-verified discovery cache files without changing their layout. Synthetic-zero mode creates exactly3,024×1,000 zero returns in F order,3,024×1,000×13 zero characteristics in C order, and1,000 positive costs equal to0.00001. These inputs contain no project observations. The constant characteristic fixture intentionally exercises the complete pipeline and undefined metrics, not predictive capacity.

## Complete workflow and reconciliation

Run in a fresh process pinned to one recorded CPU, numerical-library threads set to one before NumPy/SciPy import. Freeze controller, plans, protocol, nomination where applicable, metric helper, exact config, complete chosen source closure, original scorer and original discovery-reference identities. The metric helper is a copied, hash-identified `tools/run_candidate.py`; import only its existing general utility/summary functions, never invoke its discovery main or alter it.

Configure the frozen candidate once. Require its reported configuration to equal the requested values. Invoke original scorer.run once, with its original interfaces and start252. Save full forecasts, targets, drifted held books, daily economics, target-day indices and candidate timing. Verify finite outputs and exact shapes, the complete target/day sequences, input and held-position immutability, gross/net solvency, stock caps and gross cap within1e−12, and full fees/closing gross reconciled against captured targets. Preserve the waived opening cost as a diagnostic; do not charge it or waive another trade.

For discovery parity and both actual protected modes, require the first2,016 forecasts and first1,763 targets/held books to reproduce the original discovery NPY hashes exactly. Require the first1,762 gross/full-cost/gross-exposure/market/net ledger values to reproduce the original daily CSV exactly, excluding timings. Save the prefix arrays separately so this result is reviewable. If a longer input changes an earlier decision, retain the failure and stop; do not rewrite the reference or loosen the gate.

Reconcile full-run gross returns from prior targets and same-day returns and full fees from the next target minus drift. Use the already fixed `atol=1e−14,rtol=1e−12` for independent vectorized arithmetic, while captured scorer fee/exposure comparisons remain exact. The algebra uses the original gross-return denominator; costs do not enter that denominator. Report mask-specific economics using the copied existing population-standard-deviation metric helper. Undefined net/gross Sharpe or beta is null with reasons; never replace an undefined ratio by zero. The official textual report is called only for intervals with defined required ratios, with a clear skip reason otherwise.

Report actual candidate mean/max rebalance latency separately from adapter timing, forecast latency, path controls and feasibility. Pooled validation abs(beta)<0.2 and mean candidate rebalance<100ms are reported without introducing a new Sharpe floor. A completed evaluation can report an ineligible candidate; it must not suppress that result or retry with different settings. Selection remains the root-owned unchanged protocol step.

## Pre-access E2E expectations and exact scope

1. **Discovery parity, exact C06:** use the original C06 config and historical reference on2016 canonical discovery rows. Require all execution/accounting/input/source checks and exact historical forecast/target/held/economic identities. Report discovery metrics only. This verifies the new adapter without opening validation.
2. **Synthetic zero, exact C06:** execute3024 synthetic rows through the same entry point/config/scorer. Require2771 targets,2770 scorer rows, the fixed504/503/1007 validation masks, and exactly zero forecasts, targets, held books and four economic channels. All interval Sharpes and betas must be null with defined zero-variance reasons; fees and net returns must be exactly zero despite positive costs. Historical market-prefix comparison is not applicable to different synthetic values and must be labeled as such, not passed.

Both must finish with explicit scope-limited pass statuses and exit0 before the controller is eligible for protected admission. Their fixture/manifest/source identities, commands, logs and failed attempts are retained. Audit-mask arithmetic is source-reviewed here; this3024-row synthetic workflow must not be described as an executed audit workflow.

## Evidence, failures and reruns

Every run refuses to overwrite an output directory. Preserve setup/expectations, exact original command and frozen rerun command, environment/affinity/library versions, source/config/input/reference manifests, nomination/selection records when applicable, per-check expected/actual outcomes, daily/target output, metrics, final integrity, and artifact hashes. Serialize JSON without NaN/Infinity. Record protected numeric-access start before any approved source parse; failures after that point remain exposed/incomplete, never unopened.

Rerun commands use the frozen sources, helper, plans, protocol, reference and supplied manifest in a fresh output folder. Exact protected reruns require the same explicit root-approved manifest; they do not permit another candidate or a new parameter choice. No email, external submission, deployment, or schedule is authorized by this plan.
