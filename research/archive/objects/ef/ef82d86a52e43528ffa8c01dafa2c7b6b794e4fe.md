# Bounded candidate causality E2E

Status: **EXECUTED_PASS_SCOPE_ONLY**. Exit code: 0. Actual input prefix: [0,2016).

The frozen worker starts a new Python interpreter for every scenario and calls the unchanged official evaluator. The project/ directory contains the exact bounded input files, candidate/helpers, scorer and plan. No actual validation/audit data is included. Read expectations.md and scenarios.json for expected boundaries; summary.json records actual comparisons and limitations. Each worker has its manifest, command, input hashes, status, protected forecast/target/ledger arrays, daily ledger and stdout/stderr logs.

Use rerun.txt or `bash rerun.sh` for an exact frozen rerun into a new directory. Select a fresh output path if it exists. A completed comparison does not establish untested dates, hidden-future performance or runtime. Empty protected ranges are marked not applicable; failed workers are not claimed passed. Source review for prohibited access and future-informed state remains a separate required gate.
