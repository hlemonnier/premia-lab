# Synthetic accounting E2E evidence

Status: **EXECUTED_PASS_SCOPE_ONLY**. Exit code: 0. Recorded checks passed: 44/44.

Read expectations.md for predeclared inputs and outcomes, summary.json for all checks, and each control folder for call/position traces, opening-inclusive rows, scored daily rows and the official report. Inputs are fully synthetic and are included. The supplied scorer is copied unchanged under source/.

Rerun the frozen runner/scorer/plan with the exact command in rerun.txt or `bash rerun.sh`. Use a fresh output path if the recorded rerun destination already exists. Dependencies used are Python, NumPy and pandas; exact versions are in environment.json.

These runs validate only the declared synthetic accounting/interface workflows. No actual market CSV is read and no candidate, alpha, causality, beta or runtime claim is established.
