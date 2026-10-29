# Continual Research — GLS ensemble submission

`main` is the submission-ready branch. **The selected model is the frozen 50/50 GLS ensemble**, not the standalone GLS estimator. The entry point is `strategy.py` at the repository root, with the short explanatory note required by the assignment. `gls_alpha.py` and the adjacent `model_f/` directory contain every required helper. There is no research-directory, fitted-model, cache or network dependency.

## Why we selected this combination

We selected a fixed 50/50 combination of two causal estimates of the same return premia: the original F2 forecast and a covariance-weighted, coefficient-wise-regularized forecast. The historical gain survives removing the explicit market sleeve and increasing trading costs, but its added value is not statistically established.

The 50/50 blend, coefficient-wise ridge, half-lives, features and portfolio rules are unchanged from the audited release. Pure GLS scored about 1.4818 versus F's 1.4934; the combination scored 1.53322. The benefit therefore supports this combination, not a claim that the second estimator is superior on its own. Matched controls show weighting and shrinkage working jointly. Reviewer tests at half/double ridge strength are sensitivity checks, not configurations selected for deployment.

GLS retains the F risk and execution model. Its underlying rationale remains:

> We selected a parsimonious, causally fitted factor-variance adjustment because its historical improvement survives removing the explicit market sleeve and increasing trading costs, while improving the factor-variance forecasting diagnostic. The incremental Sharpe remains statistically uncertain, and a simpler total-risk scaling control performs similarly.

The F2 and GLS return estimates use the same 27-column design. GLS uses lagged covariance to weight matured observations and profiles a daily nuisance intercept. Both forecasts use only previously published rows. Allocation retains F's bounded factor-variance corrections, correlations, specific variances, transaction-cost-aware optimizer and explicit 0.05 market sleeve.

## Evidence and limits

| Historical comparison | F | Frozen GLS ensemble |
|---|---:|---:|
| Original-fee net Sharpe | 1.49344 | 1.53322 |
| Without explicit market sleeve | 1.38560 | 1.41900 |
| Double trading fees | 1.47227 | 1.51331 |
| Triple trading fees | 1.45623 | 1.48272 |

All figures concern the same exposed development history, not fresh holdouts or expected future returns. Incremental-performance intervals include zero, and repeated model selection can inflate the apparent advantage. The pure-estimator result does not bound future downside. Future beta below 0.2, avoidance of ruin and outperformance are not guaranteed by historical tests.

The frozen package has passed standalone reproduction, executed causality checks and an actual 25,200-day repeated-history endurance run. That long path tests software and resources, not unseen economics. One strict stock-order gross-exposure assertion failed by about 2.9e-10 against a 1e-10 threshold. The separately reviewing AI accepted the documented finite-precision exception; the failed receipt remains failed and no tolerance or production solver was changed.

Claude reproduced and reviewed the package as a different AI model, not an independent human. The user authorized selection following that assessment. Prior inconclusive statistical results remain inconclusive; this is a reasoned selection under uncertainty, not a retroactive significance-test pass.

## Run with the original assignment

Place `strategy.py`, `gls_alpha.py`, the entire `model_f/` directory and `requirements.txt` alongside the supplied, unchanged `score.py`, `returns.csv`, `characteristics.csv` and `costs.csv`. With dependencies installed, run:

```bash
python score.py strategy
```

The strategy needs NumPy, SciPy and scikit-learn. `requirements.txt` records the audited versions; the original scorer additionally uses pandas. The tested environment is Python 3.13.5 with pandas 2.2.3. No installation occurs inside the strategy.

## Submission and maintenance

Submit `strategy.py`, `gls_alpha.py`, all six files in `model_f/`, this README and `requirements.txt`: **ten files** in total. Source CSVs and the employer's scorer are deliberately not redistributed. Maintenance metadata is excluded from the export.

The **Submission package** workflow validates the actual exported archive in isolation. Frozen source identities, entrypoint structure, package allowlist and causal E2E workflows are mandatory checks. Optional hosted artifact upload can fail when storage quota is full without changing those gates. Build and check the same ZIP locally with:

```bash
python .github/scripts/check_submission.py
```

Export an already verified commit with:

```bash
git archive --format=zip --output=Continual_Research_Submission.zip HEAD
```

F's exact former submission is preserved on `submission-f-archive-20261029` at `ebf1ff1636e263d5fa98ce724cf65dc912d3d0c3`. GLS release evidence is on `research-gls-release-20261029` at `7acba976f4515a50d6fcf4ebf72def1bbba14818`; Claude's review is `research/v3/gls_check/REVIEW_20261029.md` on `v2-factor-risk`. Promotion evidence is separate on `verification-gls-promotion-20261029`. Historical research branches are preserved. New experiments belong on their own branches; `main` remains a verified submission package. No repository workflow sends anything to the evaluator.
