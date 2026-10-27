# Continual Research take-home

Private research workspace for the supplied anonymous simulated stock market. The objective is future net Sharpe under the assignment's causal, market-beta and runtime requirements.

## Status

C09 is selected by the frozen validation rule: pooled net Sharpe **0.659210**, versus **0.398603** for discovery leader C06, with both policies passing the tested beta/runtime requirements. Both uncertainty ranges and the paired difference include zero; a reliable hidden-future edge is not established. All twelve discovery configurations and their unfavorable results are retained. The literature-informed C12 local-shape extension failed its fixed parent comparison and did not enter validation.

Read [the continued research report](research/CONTINUED_RESEARCH_20261027.md) for the complete comparison, literature, contrary evidence and uncertainty. The selected [handoff](handoff/strategy.py) contains a fixed C09 wrapper and three helper-package files; its clean-directory discovery replay is exact. The single-policy audit remains unopened at this checkpoint. `submission/` retains development candidates; its default `strategy.py` is still C01. Use `handoff/` for the selected fixed policy and explicit JSON configurations for research comparisons.

## Start here

- [Master plan](Continual_Research_Master_Plan.md): requirements, research design, exact score windows and release gates.
- [Frozen protocol](RESEARCH_PROTOCOL.json): machine-readable discovery/validation/audit masks and experiment budget.
- [Worklog](WORKLOG.md): current objective, decisions, completed work and next gate.
- [Project rules](AGENTS.md): information access and user-mandated testing policy.
- [Reproduction guide](REPRODUCE.md): original input identities, candidate reruns and verification evidence.
- [Experiment ledger](research/EXPERIMENT_LEDGER.md): prospective admissions, results, diagnostic exposures and remaining budget.
- [Source register](SOURCE_REGISTER.md): task sources, provenance and limits on completed checks.
- `reviews/`: independent requirements, research, verification and artifact reviews.
- `evidence/`: actual executed-run records, including failures.
- `source/Quant Research Take-Home/`: unchanged supplied brief, scorer and examples.

## Data

Restore the large CSVs and supplied figures from the original archive described in REPRODUCE.md. They are excluded from Git; source hashes identify the exact inputs. Cached arrays and bulky derived numerical arrays are also excluded. Small inspectable results, configuration, source snapshots and rerun instructions remain versioned.

Discovery used rows `[0,2016)`. Two frozen policies have completed validation on the original masks within `[2016,3024)`. The audit remains closed pending the selected-policy freeze/release. Full-file input hygiene checked identity, shape, ordering and finiteness; it did not substitute for protected-period admission.

## Verification discipline

Prefer complete E2E workflows and save inspectable evidence for every run. If isolated testing is needed, specify failures and outcomes, write the tests, then implement the covered component. Never write unit tests after the implementation they cover. Never describe an unexecuted check as passed.

The employer-facing hand-in will be a compact strategy module and declared helpers. This repository also preserves the research trail needed to understand and reproduce it.

`RESEARCH_PROTOCOL.json` and `PACKAGE_MANIFEST.json` preserve the planning freeze; their historical status fields are not the current run dashboard. Executed candidate identities and checks live in the individual `evidence/` manifests and the current worklog.
