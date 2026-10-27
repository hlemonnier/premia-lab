# Reproducing the selected strategy and research evidence

The repository contains frozen plans, all twelve development configurations, independent reviews, complete-run evidence and reproduction scripts. The selected fixed C09 policy is in `handoff/`; its top-level `strategy.py` needs the accompanying `model/` directory. The supplied scaffold in `source/` remains unchanged. Development candidates in `submission/` require their explicit named JSON configurations; their default strategy is C01, not the selected handoff.

## Exploratory-notes and frozen-attribution follow-up

Read `research/NOTES_AND_ATTRIBUTION_20261027.md` for the later descriptive
analysis of the unchanged C09 policy. It does not run a new strategy or create
an untouched confirmation sample. The admission was published in `27fdb7f0`;
the tested tool, independent review and release were published in `49fc43f2`
before the single actual attribution.

The complete preimplementation synthetic workflow can be reproduced from the
current checkout with a **new** output directory:

```bash
python tools/verify_frozen_attribution.py --project . --out evidence/frozen_attribution_synthetic_reproduction
```

It generates its own known-component inputs and invokes the attribution tool in
nine fresh processes. Original results are retained in
`evidence/frozen_attribution_synthetic_001`. The original expected missing-tool
record in `evidence/frozen_attribution_red_001` describes the preimplementation
environment. Once the implementation exists, its old command cannot reproduce
that absence. To reenact only the missing-tool behavior, pass `--expect-missing`
and `--implementation` pointing to an explicitly new, nonexistent path; label
the new result a reenactment and retain the original record unchanged.

The actual run command is in `evidence/frozen_attribution_real_001/rerun.txt`.
It uses the original `evidence/audit_C09_001` packet, authenticating artifact
manifest SHA256 `2e1aff5ae8e1257a6abef712b821e4859778dd20f0bb60f2a9903cf0c350d95b`
and every consumed file before numeric access. It needs original return and
target arrays, the original daily ledger/configuration/manifests, and four
original helper files; it does not need characteristics, forecasts or another
strategy replay. Excluded NPY files must be restored or regenerated with their
**original recorded identities** as described below. Preserve the original
metadata; do not rewrite its hashes or timings to accommodate a new replay.

The source/synthetic review is `reviews/FROZEN_ATTRIBUTION_SOURCE_REVIEW.md`.
The independent actual-output reconciliation, with its exact self-contained
command and all 146 observed checks, is
`reviews/FROZEN_ATTRIBUTION_ACTUAL_REVIEW.md`. The real packet includes the full
3,526-row decomposition, original input hashes, frozen helper source, fixed
stage summaries, expectations and logs. Fees remain the original separate
subtraction; the three components are not separately implemented portfolios.

`research/FROZEN_ATTRIBUTION_RELEASE_20261027.json` points to the preserved
release002 snapshots. Release001 is an unexecuted draft that caught the review
document before its completed source/synthetic section was saved. No actual
attribution occurred under that draft, and the diagnostic code did not change.

## Selected handoff

The four required files are `handoff/strategy.py`, `handoff/model/__init__.py`, `handoff/model/strategy.py` and `handoff/model/portfolio.py`. The outer entry point contains the complete pre-audit note and literal original C09 configuration. Both engine/helper files retain their original bytes. The handoff itself needs only NumPy and the Python standard library; research verification additionally uses the original scorer's dependencies and recorded environment.

The discovery-verified package manifest is `evidence/handoff_discovery_001/package_manifest.json`, SHA256 `97ec4469c51311730d906a68bd594ecd48b75d87bb29f0beccb6f7e3e5d8d813`. The selected configuration SHA256 is `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`. The top-level handoff entry-point SHA256 is `7f15248160efd09e65d7dcf4d79cb1c5c4897d87641f2c2057f8566c7de7d946`.

To use the employer's original command, put these four files in a clean copy of the supplied task folder, retaining the helper directory, then run `python score.py strategy`. This loads the entire supplied history; it is appropriate only after that history's recorded release. The original command reports a full-history score, which is not the separately frozen validation or audit estimate. For those estimates, use the controlled replays below.

## Reproduce an executed discovery candidate

Restore the original archive below into `source/`. Use Python 3.12 and the recorded versions in `requirements-research.txt`; each run also records its exact environment. From the repository root, prepare only the permitted discovery cache:

```bash
python tools/prepare_discovery.py \
  --project . \
  --cache cache/discovery \
  --out evidence/data_preparation_reproduction
```

This preparation validates source identities and reads numeric rows `[0,2016)` only. It does not open validation or audit outcomes. Then reproduce, for example, C06:

```bash
python tools/run_candidate.py \
  --project . \
  --strategy submission/strategy_gls_factor.py \
  --config research/configs/C06_gls_factor.json \
  --out evidence/discovery_C06_reproduction
```

Use a new output directory for every run. The runner freezes the candidate, all Python helpers, configuration, original scorer and expectations before importing them. It requests one available CPU and fixes numerical-library threads before imports. The recorded original runs used explicit `taskset` CPU assignments to avoid direct affinity contention; their environment records identify them. Timing differs with hardware and shared load.

For an exact historical code reproduction, use the source/configuration snapshots under that run's `source/candidate/` and `config.json`, plus its frozen runner, scorer, protocol and expectations as shown by `rerun.txt`. Historical commands contain the original absolute workspace paths; replace the project and output locations when reproducing on another machine, retaining the frozen source/configuration files. On a clean clone, the large `.npy` outputs are regenerated; their hashes, original ledgers and inspectable summaries are already versioned.

The source code chooses no candidate based on the final row count, and the scorer begins with an empty book at 252. Discovery produces 1,762 score rows, indices 253 through 2014, under the official endpoint convention. This is not a holdout score. Do not pass all 15 years into a candidate before the relevant protocol gate.

## Reproduce the first-wave comparison

`evidence/comparison_wave1_001/rerun.txt` points to its frozen reporting script and expected inputs. It reads completed C01–C04 daily ledgers, fits no strategy, and performs the predeclared paired moving-block bootstrap. The frozen copies of its inputs, actual bootstrap draws, summaries and report are retained. A reporting pass is separate from candidate causality and from out-of-sample validation.

## Frozen validation and reporting

The original nomination is `research/VALIDATION_NOMINATION.json`, SHA256 `fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5`. It admits only C06 and C09. The explicit original commands are preserved in `research/VALIDATION_RELEASE_RECORD.json` and each completed packet's `rerun.txt`. An exact selected validation reproduction from the project root is:

```bash
python tools/run_protected_candidate.py \
  --project . \
  --strategy submission/strategy.py \
  --config research/configs/C09_additive_long_memory.json \
  --reference evidence/discovery_C09_001 \
  --out evidence/validation_C09_reproduction \
  --mode validation --cpu 6 \
  --nomination-manifest research/VALIDATION_NOMINATION.json \
  --nomination-sha256 fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5
```

The controller validates all nominated identities and evidence before bounded numeric parsing. It reads exactly 3,024 return rows and the matching characteristic panels, preserves F-order returns/C-order characteristics, runs once continuously from start 252, and reports exactly 504/503/1,007 validation observations. The original historical prefix must remain exact. The controller records access start even if a later step fails; an incomplete protected run cannot be called unopened.

CPU numbers identify this Linux environment. On another machine choose an available single CPU and record that change; absolute timing is host-specific. Preserve all other configuration/source/mask identities. Every output directory must be new.

The fixed uncertainty report can be reproduced from the completed saved validation ledgers without executing another candidate:

```bash
python tools/report_protected_uncertainty.py \
  --project . --mode validation \
  --run C06=evidence/validation_C06_001 \
  --run C09=evidence/validation_C09_001 \
  --nomination-sha256 fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5 \
  --out evidence/validation_uncertainty_reproduction
```

The reporter validates consumed artifacts, exact score indices and original metrics. It uses the predetermined 21/63-observation moving blocks, 1,000 paired draws and seeds, with fixed fee multipliers 1/1.5/2. It consumes ledgers and source/provenance metadata, not the large model/input NPY arrays. Its saved `rerun.txt` points to its own copied inputs and plans. Preserve its full input snapshots when copying that evidence packet.

## Canonical causality, long-history and package equivalence

Use the frozen commands in these completed packets:

- C06 canonical causal workflows: `evidence/C06_causality_A_002`, `B_002` and `C_002`; strict reconciliation in `evidence/C06_causality_reconciliation_002`.
- C09 canonical causal workflow: `evidence/C09_causality_001`; readback and explicit CPU rerun in `evidence/C09_causality_admission_002`.
- Full 25,200-row workload: `evidence/C06_long_history_002` and `evidence/C09_long_history_001`, with independent readback in `evidence/long_history_independent_readback_001`.
- Protected-controller pre-access workflows: `evidence/protected_replay_discovery_001` and `evidence/protected_replay_zero_001`; the latter is entirely synthetic.
- Clean selected package: `evidence/handoff_discovery_001`, plus separate root artifact readback in `evidence/handoff_discovery_independent_readback_001`.

The long-history workload deterministically repeats discovery values and preserves canonical array layout. It is actual runtime/path evidence, not 25,200 independent market observations. Earlier C-layout fixture failures are retained separately. Do not replace the original historical references or broaden the exact equality gate to conceal a changed numerical layout.

The handoff verifier starts an isolated fresh interpreter in a clean directory, uses only the copied four-file package and original scorer, records actual import paths, and requires exact complete forecast/target/held-array hashes and all economic/net rows. Its expected missing-wrapper stage preceded wrapper implementation. The selected record is frozen at SHA256 `941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa`.

## Single-policy audit boundary

The only admitted audit policy is the selected unchanged C09. Its canonical controller uses input `[0,3780)`, continuous state from start 252 and score mask `[3024,3779)`, exactly 755 observations. A separate root audit nomination binds the selection and discovery-verified package before access. The unchanged wrapper then reproduces the entire canonical audit path as a same-policy engineering check, not a second selectable audit candidate. Use the final audit packets' frozen rerun commands after their recorded release; do not run another candidate or tune a setting on the audit.

The audit readback also requires exact identity of the entire earlier C09 validation prefix: 3,024 forecasts, 2,771 targets/held books and 2,770 economic rows. This extends the ordinary historical-prefix check without changing the selected policy. Any failure, undefined ratio, beta shortfall or unfavorable economics remains visible and cannot justify substituting another policy.

The audit is now complete. Frozen audit nomination SHA256: `b68c5db46c641f68bdaa7526464c846dd29e1b4ab65c7fd1ab6e8f775762cea4`. Use `evidence/audit_C09_001/rerun.txt` for the canonical policy, `evidence/audit_uncertainty_001/rerun.txt` for fixed saved-ledger reporting, `evidence/audit_independent_readback_002/rerun.txt` for successful complete reconciliation, and `evidence/handoff_audit_001/rerun.txt` for the exact clean package. The canonical and handoff runs score the same observations; the second is reproducibility evidence.

On a fresh clone, excluded NPY arrays must first be regenerated with the frozen run commands and checked against the original recorded hashes. Reuse original summaries/ledgers as references; do not rewrite their hashes or timings to agree with a new run. Independent readback of the original packet requires restoring its expected numerical files at their recorded locations after confirming their identities.

The first audit readback is a preserved failure at an unavailable partial characteristics-copy inventory entry. `evidence/audit_artifact_manifest_investigation_001/recover.py` restores exactly the original 214,433,792-byte prefix and SHA256 from canonical `characteristics.npy`, only if the recorded destination is missing. It uses exclusive creation and verifies all original canonical/manifest/code identities before and after. Run this recovery only when reproducing that original packet and the specific recorded artifact is absent. Do not delete an existing artifact to force recovery, rewrite the original manifest, or describe readback001 as passed. Readback002 uses the unchanged reviewer after that documented byte recovery.

The final download is `artifacts/continual_research_C09.zip`, SHA256 `cba024cae44dd84b17b17dcde48e4276e677a52883220c54da455664a770b7fa`. Its exact four members match the pre-audit package manifest. `tools/build_research_artifacts.py --project . --out artifacts_reproduction` rebuilds the shareable figure and deterministic code archive from completed saved evidence without executing a candidate. The build manifest identifies every consumed ledger/report and plotting environment.

## Inputs

Use the user's original archive named `Quant Research Take-Home-20261026T134123Z-1-001(1).zip`. Expected size: 136,015,226 bytes. Expected SHA-256:

```
ba49564fb0d8888124fdc0b680f88c843c17359a089129f1fe28e0b94e003dd6
```

The package omits the large original CSVs/figures and generated 504-day input copies to avoid duplicating the supplied dataset. Original source-file hashes and generated prefix-input hashes are retained. The runner regenerates the prefix inputs from the verified original data. Small source text files are included unchanged for review.

## Setup on a new machine

1. Extract this planning package into a working directory.
2. Place the original ZIP in a known location and verify its SHA-256.
3. Extract the original ZIP into `source/`; it creates `source/Quant Research Take-Home/` with all 12 original members. Existing small source files should match the archive, not be edited.
4. Use Python 3.12 with NumPy and pandas. Recorded versions are NumPy 2.3.5 and pandas 2.2.3. Other package versions are captured in the evidence; no optional solver or boosting package is needed for this smoke run.

From the planning directory, run (replace only the original archive path):

```bash
python -u tools/preflight.py \
  --source 'source/Quant Research Take-Home' \
  --archive '/absolute/path/Quant Research Take-Home-20261026T134123Z-1-001(1).zip' \
  --plan PREFLIGHT_PLAN.md \
  --out evidence/preflight_reproduction
```

Use a fresh output directory on each run. The runner sets numerical-library thread limits before importing NumPy/pandas and requests one-CPU affinity. The original Linux run successfully pinned affinity; unsupported affinity on another OS is reported as a failed benchmarking precondition and requires a documented alternative environment. Do not treat that as candidate-model failure.

The exact original paths/command, frozen runner, frozen expectations, environment, hashes, actual results and economic CSV rows are in `evidence/preflight_002/`. Its `rerun.txt` uses the frozen runner snapshot and frozen expectations; it assumes the original local input paths still exist. The portable command above defines reconstruction when they do not.

Expected successful conclusion: 24 checks pass, 250 scored rows for the first 504 input rows, finite data/results, correct stock/day order, unit gross exposure for the supplied equal-weight example, repeat economic rows exactly equal, and beta approximately 1. Runtime values are machine-dependent. Equal-weight is expected to fail the assignment's beta condition; this run does not validate a candidate.

## Failed preflight history

`evidence/preflight_001/` records a real early failure in the preflight inventory assumption. Its original artifacts remain historical; see `REPRODUCE_FAILURE.md` there for the separate, explicitly unexecuted reproduction setup. That expected failure is not mixed with the successful scope result in preflight 002.

## Executed gates and historical evidence

The synthetic accounting workflow executed with 44 passing checks. C01 and C02 each completed their configured 600-row causal smoke workflow with 28 fresh-process scenarios and exact protected equality; earlier interrupted smoke runs remain explicitly incomplete. New diagonal, factor, precision and exact-gross numerical components have preimplementation check records and subsequent executed evidence. All twelve actual discovery configurations completed the unmodified scorer with 20 workflow checks each.

C11's known-interaction synthetic whole-strategy workflow completed four fresh-process runs and 40 checks after its preimplementation specification/verifier and expected missing-module record. Its frozen rerun is in `evidence/interaction_workflow_001/rerun.txt`; it regenerates synthetic inputs and does not require the market CSVs. That deliberately strong fixture demonstrates capability and tested prefix invariance, not actual-market profitability or the full finalist causal gate.

C12's known-local-effect synthetic workflow completed five fresh-process paths and 55 checks, with exactly preserved protected comparisons and a zero-return control. Its negative single discovery result remains in the comparison. Canonical finalist-specific causality, actual long-history runtime, two-policy protected validation and clean C09 discovery equivalence have completed their separate gates. Consult the current worklog and continued research report for the later audit/final-package disposition rather than the frozen planning protocol's historical status fields. A reconciliation pass does not imply a significant alpha or guarantee future profitability.
