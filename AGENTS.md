# Submission branch contract

`main` is the ready-to-submit F package, not a research workspace. The root must retain `strategy.py`, its short opening note, `model_f/`, README.md and requirements.txt. Use research branches for experiments, raw data, caches, results and alternate candidates. The former main snapshot is preserved on research-archive-pre-submission-20261029; the original assignment and historical research/audit records remain there and on existing research branches.

Never retune or change the audited F executable code while doing packaging/documentation work. A future model release needs its own explicit selection decision and validation before updating frozen source identities. Keep uncertainty and AI/human contributions honest. Do not convert the prior failed statistical promotion test into a claimed pass.

Before implementation, document failure modes and expected outcomes, then write E2E checks. Never write unit tests after the implementation they cover. Preserve original scorers and inputs. Report failed and unexecuted checks accurately.

Before updating main: run `python .github/scripts/check_submission.py`; for any executable change also reproduce the original scorer with private data on the research branch and rerun applicable causal/runtime checks. Commit only the allowlisted submission and maintenance files. The archive must contain only the nine handoff files. CI metadata and this maintenance file are export-ignored. Passing CI does not imply statistical superiority or enforced branch protection.

Never submit externally or send a message to the evaluator without explicit authorization.
