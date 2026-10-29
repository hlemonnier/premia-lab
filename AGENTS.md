# Submission branch contract

`main` is the ready-to-submit frozen GLS ensemble, not a research workspace. Its root must retain `strategy.py` with the short note, `gls_alpha.py`, `model_f/`, README.md and requirements.txt. The exported archive has exactly ten files: those four root files and six model_f helpers. CI/maintenance files are export-ignored. Use separate research branches for each proposed model, data, caches and evidence.

The chosen policy is the existing 50/50 blend of F2 and covariance-weighted, coefficient-wise-regularized forecasts. Do not substitute pure GLS, change ridge based on reviewer sensitivity runs, retune the blend or combine another model during packaging/documentation work. All model/helper sources and dependency pins must match the frozen audited GLS package. The prior F submission is preserved on submission-f-archive-20261029 at ebf1ff1636e263d5fa98ce724cf65dc912d3d0c3.

Keep selection uncertainty and human/AI contributions honest. A different AI reviewed the package; it was not an independent human review or new market sample. The original inconclusive statistical tests and failed tiny stock-permutation assertion remain historical records; reviewer acceptance of the numerical exception does not turn the assertion into a pass. No future downside floor is established. No model selection without explicit authorization and appropriate validation.

Document failure modes and expected outcomes before implementation, then write complete E2E checks. Never add unit tests after the implementation they cover. Preserve original scorers and inputs; retain failures and report unexecuted checks accurately.

Before updating main, run `python .github/scripts/check_submission.py`. Any executable change also requires original-scorer reproduction and applicable causality/runtime checks on its research branch. Commit only allowlisted submission/maintenance files; do not merge research folders into main. Passing CI does not imply statistical superiority or enforced branch protection.

Never submit externally or message the evaluator without explicit authorization.
