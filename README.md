# Continual Research take-home

Private research workspace for the supplied anonymous simulated stock market. The objective is future net Sharpe under the assignment's causal, market-beta and runtime requirements.

## Status

Ten complete discovery configurations have been executed under the frozen protocol. The best current development score is C06's 0.762944 net Sharpe, with realized net market beta 0.006330. This is a modest in-development result, not validation or evidence of a strong hidden-future edge. One fixed full-quadratic interaction challenger, C11, is admitted and not yet scored at this checkpoint. Validation and locked audit remain unopened.

Read [the current research checkpoint](research/DISCOVERY_CHECKPOINT.md) for the complete comparison, contrary evidence, limitations and next gate. `submission/` currently holds development candidates; its default `strategy.py` is the C01 benchmark, not a selected employer hand-in. Use the explicit JSON configuration and runner when reproducing a named candidate.

## Start here

- [Master plan](Continual_Research_Master_Plan.md): requirements, research design, exact score windows and release gates.
- [Frozen protocol](RESEARCH_PROTOCOL.json): machine-readable discovery/validation/audit masks and experiment budget.
- [Worklog](WORKLOG.md): current objective, decisions, completed work and next gate.
- [Project rules](AGENTS.md): information access and user-mandated testing policy.
- [Reproduction guide](REPRODUCE.md): original archive identity and phase-0 preflight instructions.
- [Experiment ledger](research/EXPERIMENT_LEDGER.md): prospective admissions, results, diagnostic exposures and remaining budget.
- [Source register](SOURCE_REGISTER.md): task sources, provenance and limits on completed checks.
- `reviews/`: independent requirements, research, verification and artifact reviews.
- `evidence/`: actual executed-run records, including failures.
- `source/Quant Research Take-Home/`: unchanged supplied brief, scorer and examples.

## Data

Restore the large CSVs and supplied figures from the original archive described in REPRODUCE.md. They are excluded from Git; source hashes identify the exact inputs. Cached arrays and bulky derived numerical arrays are also excluded. Small inspectable results, configuration, source snapshots and rerun instructions remain versioned.

Discovery may inspect rows `[0,2016)` only. Validation and audit data remain closed until their protocol gates. Full-file input hygiene has already checked identity, shape, ordering and finiteness.

## Verification discipline

Prefer complete E2 E workflows and save inspectable evidence for every run. If isolated testing is needed, specify failures and outcomes, write the tests, then implement the covered component. Never write unit tests after the implementation they cover. Never describe an unexecuted check as passed.

The employer-facing hand-in will be a compact strategy module and declared helpers. This repository also preserves the research trail needed to understand and reproduce it.

`RESEARCH_PROTOCOL.json` and `PACKAGE_MANIFEST.json` preserve the planning freeze; their historical status fields are not the current run dashboard. Executed candidate identities and checks live in the individual `evidence/` manifests and the current worklog.
