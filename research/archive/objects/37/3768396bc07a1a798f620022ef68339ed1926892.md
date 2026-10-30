# F selected as the main model — 29 October 2026

## Authority and decision

Hugo explicitly authorized promoting F to the main model and supplied the README rationale. This record supersedes earlier current-selection labels, but preserves every earlier experimental result and statistical conclusion.

We selected a parsimonious, causally fitted factor-variance adjustment because its historical improvement survives removing the explicit market sleeve and increasing trading costs, while improving the factor-variance forecasting diagnostic. The incremental Sharpe remains statistically uncertain, and a simpler total-risk scaling control performs similarly.

The earlier release audit passed technical checks but withheld promotion under a preregistered significance rule. That rule still fails. This is an explicit user-authorized decision under uncertainty after additional mechanism checks, not a retroactive statistical pass or a newly untouched validation sample. No threshold, model parameter, sleeve, training schedule, forecast or trading rule was changed to obtain promotion. No claim of a guaranteed or expected future +0.05 Sharpe is made.

## Exactly what is selected

The source is `handoff_f/` at audited commit `b78de17a13161d65de4031a33dad2d7bde60c70f`. Its Python files and dependency pins are copied using their existing Git objects without code edits. `handoff/` is the canonical selected package and `handoff_f/` is an identical named copy. Package READMEs are updated to reflect selection.

The previous main handoff, C09, is retained unchanged as `handoff_c09/`. V3 is retained unchanged as `handoff_v3/`. Earlier branches, source data, the original scorer, historical evidence and decision rules are not overwritten. Historical `submission/` defaults and C09 reproduction instructions are not instructions for the selected F model; use the current README and `handoff/README.md`.

## Promotion verification

Code and dependency Git identities match the audited release. The existing original-scorer release runner was executed again on the complete supplied history: net Sharpe 1.493439947872387, 3,526 scored days, all 7,054 allocation solves certified `ok`. All four daily economic columns match the archived standalone release exactly; separately reconstructed cashflows differ by only 1.04e-16. The receipt preserves successful execution and the earlier infrastructure/timeout attempts. This is a reproduction check, not new future-performance evidence.

The prior full release audit, Wave 6 uncertainty calculations and Claude's mechanism checks remain the evidence for this decision. They are linked from the main README rather than rewritten. An unknown-future beta guarantee, absence of overfitting and economic superiority over the simpler T control are not established.

## Release boundary

This change selects the model in the private repository only. No email, evaluator upload, live trading deployment or external submission is authorized or performed by this promotion. Future model changes require their own recorded experiments and checks.
