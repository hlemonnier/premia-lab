# F — selected main model

Selected by Hugo on 29 October 2026. This is the frozen, audited F implementation from commit `b78de17a13161d65de4031a33dad2d7bde60c70f`; no Python source, model parameter, market sleeve or trading rule has been changed for promotion.

We selected a parsimonious, causally fitted factor-variance adjustment because its historical improvement survives removing the explicit market sleeve and increasing trading costs, while improving the factor-variance forecasting diagnostic. The incremental Sharpe remains statistically uncertain, and a simpler total-risk scaling control performs similarly.

## Run the selected model

Place `strategy.py` and the adjacent `model_f/` directory beside the original `score.py`. Keep the supplied CSV files in the working directory and run:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python score.py strategy
```

Use the permitted libraries listed in `requirements.txt`; the supplied scorer also requires pandas. The release audit tested Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0 and pandas 2.2.3. Dependency pins are an environment record, not learned parameters.

No historical data or fitted models are included. `forecast()` starts or resets a session; `rebalance()` then advances one published day at a time. Risk payload row t uses only input rows before t. The original scorer accepts arbitrary payload width with days first; this package uses `(days, stocks + 27)`.

## Selection is not a statistical pass

The previous release audit passed technical checks but withheld promotion under its stronger statistical gate. That result remains unchanged. The present selection is an explicit user-authorized decision under uncertainty, following the additional no-sleeve and constant-multiplier checks; it does not retroactively pass or weaken the old test.

The supplied fifteen years are exposed development data. Historical net Sharpe is 1.493439947872387 versus 1.4447333005566665 for V3. This is not an expected or guaranteed future gain. A fixed 0.05 equal-weight market sleeve remains explicit, and estimated-beta hedging does not guarantee future beta below 0.2. The repeated-century run establishes operational endurance, not performance on an independent future.

The allocator, engine and base policy are unchanged copies of the verified V3 sources. F's forecasting and factor-risk logic remain identical to the standalone release. The source commit and historical release decision are retained for reproducibility. Promotion does not submit anything to the evaluator.
