# Frozen GLS candidate

This folder is a standalone candidate package, not a promotion of GLS to main.
Place its files alongside the original unchanged scorer and supplied CSVs, then
run `python score.py strategy`. The opening strategy note describes the model,
contributions, mechanism and limitations. The original task allows all required
libraries; requirements.txt preserves the audited pins. The tested interpreter
is Python 3.13.5. The scorer additionally requires pandas (tested 2.2.3).

## Frozen identity

`gls_alpha.py` is a byte-for-byte copy of the original research GLS module
(blob `f26b3c5b8c8578525af7db19f01898140b9b7fc7`). The six model_f helpers and
requirements.txt are unchanged. Only the public adapter and documentation are
new. There is no research-directory import or data-dependent initialization file.

## Evidence and decision boundary

Historical net Sharpe: GLS 1.5332155606881952, F 1.493439947872387.
The matched-control evidence supports covariance-aware coefficient-wise
regularization, not a general penalty-independent GLS advantage. Incremental
confidence intervals include zero; all supplied history is exposed development
data. No new performance claim follows from packaging or repeated-history
endurance. F remains the selected main release. Separate reviewer sign-off and
any promotion require distinct recorded decisions.

The release verification branch is research-gls-release-20261029. Its
verification/gls_release directory holds the plan, checks, exact commands and
results; those files are not required at runtime or included in this handoff.
