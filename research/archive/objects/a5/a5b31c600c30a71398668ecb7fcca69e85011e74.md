# Continual Research take-home — project rules

## Goal and authority

The supplied README and scorer define the task: maximize future net Sharpe on the supplied simulated market, satisfy the beta condition, preserve causality, and meet runtime limits. Ignore the applicant's previous projects or preferred modeling methods. The planning protocol is recorded in RESEARCH_PROTOCOL.json and independently approved. On 26 October the user authorized research execution, a private GitHub repository, and commits of project work. Follow the recorded protocol during implementation.

## User-mandated verification rules

- NEVER write unit tests after implementing the code they cover.
- Strongly prefer end-to-end tests as the sole testing mechanism.
- If isolated testing is necessary: document failure modes, edge cases, and expected outcomes FIRST; write tests SECOND; implement code THIRD.
- Every E2E run must preserve setup, input identities, exact rerun command, expected outcomes, actual outcomes, and relevant logs/output files.
- Report failed, blocked, and unexecuted checks accurately. Unexecuted never means passed.

## Research discipline

- Preserve the supplied source files and scorer unchanged.
- Distinguish assignment requirements, our decisions, hypotheses, observations, and unresolved questions.
- Before any predictive experiment, record the hypothesis, split, allowed variants, metrics, and acceptance/rejection rule.
- All arrays use zero-based row indices internally. CSV day labels are one-based; always identify which convention is used.
- Global input hygiene may read shape, keys, and finiteness. Do not inspect outcome statistics, signals, or the supplied full-sample figures for the reserved audit period before the release gate.
- Fixed split: rows [0,2016) discovery; [2016,3024) chronological validation; [3024,3780) sealed internal audit. Exact score masks are frozen in RESEARCH_PROTOCOL.json. A causal online learner may learn from prior rows inside an evaluation period; its policy/hyperparameters cannot be retuned there.
- No random row-wise cross-validation or future-dependent transformations. Historical observations only for any forecast at time t.
- Preserve experiment failures and negative findings. Do not cherry-pick runs, seeds, or windows.
- Independent reviewer must inspect leakage, scorer fidelity, and evidence before release.
- Do not invent human contributions or empirical findings in the final one-page note.
- No outgoing messages or submission without the user's explicit authorization.

## Work organization

Use WORKLOG.md for the objective, decisions, completed work, and next gate. One agent owns each file during parallel work; cross-review by a different agent. Keep the deployable submission small. Scratch experiments and internal evidence stay outside the final submission folder.
