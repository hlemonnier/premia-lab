# Continual Research — F submission

`main` is the submission branch. The entry point is **`strategy.py` at the repository root**; its opening note explains the market hypothesis, construction, AI/human contributions and long-run limitations. The adjacent `model_f/` directory contains every required helper. No research checkout, trained-model file, prediction cache or network access is required by the strategy.

## Why we selected F

We selected a parsimonious, causally fitted factor-variance adjustment because its historical improvement survives removing the explicit market sleeve and increasing trading costs, while improving the factor-variance forecasting diagnostic. The incremental Sharpe remains statistically uncertain, and a simpler total-risk scaling control performs similarly.

F keeps the causal pooled expected-return forecast and uses a shared Gamma regression with three multihorizon predictors and an intercept to adjust 26 factor variances. Fits use only matured labels. The adjustments are bounded; existing correlations, specific variances, transaction-cost-aware allocation and the explicit 0.05 equal-weight market sleeve are retained. This is a portfolio-construction choice, not a claim of newly established stock-selection alpha.

The supplied-history net Sharpe is 1.49344 (V3: 1.44473); the simpler total-risk control scores 1.49091. The history has been exposed during research. Statistical intervals for incremental performance include zero, causal software tests do not rule out selection overfit, and neither historical beta nor repeated-history endurance tests guarantee future compliance. F was explicitly selected under uncertainty, not because the previous statistical promotion gate passed.

## Run with the original assignment

Place `strategy.py`, `model_f/`, and `requirements.txt` in the supplied task folder alongside the original, unchanged `score.py`, `returns.csv`, `characteristics.csv` and `costs.csv`. With the dependencies installed, run:

```bash
python score.py strategy
```

The strategy requires NumPy, SciPy and scikit-learn; `requirements.txt` records the audited versions. The original scorer additionally needs pandas. The tested environment is Python 3.13.5 and pandas 2.2.3. No dependency installation occurs inside the strategy.

## Files to submit

Submit this folder's `strategy.py` and the entire `model_f/` directory; include this README and `requirements.txt`. Source data and the employer's scorer are deliberately not redistributed. There are no alternate candidate directories or experiments in the submission.

For maintainers, the **Submission package** workflow checks the exported archive in isolation and produces `Continual_Research_Submission.zip`. The same check runs locally:

```bash
python .github/scripts/check_submission.py
```

The check preserves the audited F helper identities, validates the entry point and note, and exercises complete constructed forecast/rebalance paths, prefixes, altered futures and session resets. It is a regression check, not a fresh statistical evaluation. Git export attributes exclude maintenance files from the submission ZIP.

Research and historical evidence are preserved separately on `research-archive-pre-submission-20261029` and the existing research/audit branches. New experiments belong on research branches; `main` is reserved for verified, submission-ready releases. Nothing is sent to the evaluator by this repository or its workflow.
