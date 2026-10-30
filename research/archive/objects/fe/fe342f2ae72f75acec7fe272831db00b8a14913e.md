# Continual Research take-home

Private research workspace for the supplied anonymous simulated stock market. The objective is future net Sharpe under the assignment's causal, market-beta and runtime requirements.

## Selected main model: F

**F is the selected model on `main`, approved by Hugo on 29 October 2026.** The canonical runnable package is [handoff/](handoff/README.md), with entry point [handoff/strategy.py](handoff/strategy.py). [handoff_f/](handoff_f/README.md) is an identical named copy of that package. All Python files and dependency pins are unchanged from the audited standalone F release at commit `b78de17a13161d65de4031a33dad2d7bde60c70f`; only selection documentation has changed.

We selected a parsimonious, causally fitted factor-variance adjustment because its historical improvement survives removing the explicit market sleeve and increasing trading costs, while improving the factor-variance forecasting diagnostic. The incremental Sharpe remains statistically uncertain, and a simpler total-risk scaling control performs similarly.

F keeps the existing causal expected-return forecast and predicts bounded adjustments to the variances of 26 characteristic factors. One shared Gamma regression uses three multihorizon predictors and an intercept, refitted every 126 days using matured labels. Factor correlations, specific variances, the certified allocator and the explicit 0.05 equal-weight market sleeve are unchanged. This is a portfolio-construction choice, not a claim of newly established stock-selection alpha.

### Evidence and limits

The original-scorer development net Sharpe is **1.493439947872387** for F, versus **1.4447333005566665** for V3. The simpler total-risk scaling control T scores **1.490907502081972**. These are historical observations on exposed development data, not expected or guaranteed future gains.

The release audit passed technical checks, including causality, exact reproduction, standalone execution and a repeated-history century-scale endurance run. A fresh promotion replay again matches the audited daily economic rows exactly; see [the promotion verification receipt](verification/f_promotion/VERIFICATION_20261029.json). The endurance path is not an independent future sample.

**The previous statistical promotion gate did not pass and has not been rewritten.** Selection is an explicit user-authorized decision under uncertainty, taking account of the additional no-sleeve and constant-multiplier checks. See [the selection decision](MODEL_SELECTION.md) and [machine-readable selection](MODEL_SELECTION.json). Historical no-promotion reports remain historical records; they are not assertions that F now passes significance tests.

The full fifteen supplied years have already been examined. Causality checks do not certify the absence of overfitting. Future factor premia, risk dynamics and market carry may change, and estimated-beta hedging does not guarantee future beta below 0.2.

## Run F

Use the selected [handoff package instructions](handoff/README.md). Keep the original source files and CSVs unchanged. From the repository root, stage a clean run as follows:

```bash
ROOT="$PWD"
SOURCE='/absolute/path/to/Quant Research Take-Home'
STAGE="$(mktemp -d)"
cp -R "$ROOT/handoff/." "$STAGE/"
cp "$SOURCE/score.py" "$STAGE/score.py"
(cd "$SOURCE" && OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python "$STAGE/score.py" strategy)
```

The tested dependency pins are in `handoff/requirements.txt`; the original scorer also uses pandas. The package contains no historical arrays, fitted-model files or prediction caches and requires no research-directory imports or network access. The evaluator-facing files are `strategy.py` and the adjacent `model_f/` helpers. Promotion to `main` is not an external submission.

## Preserved references and research trail

- [handoff_v3/](handoff_v3/strategy.py): unchanged V3 reference.
- [handoff_c09/](handoff_c09/strategy.py): the previous `main` handoff, preserved byte for byte. The [C09 archive](artifacts/continual_research_C09.zip) is historical, not the selected F package.
- `submission/`: historical development candidates; its old default is not the selected model. Use `handoff/` for F.
- [Frozen F release audit](https://github.com/hlemonnier/continual-research-takehome/blob/b78de17a13161d65de4031a33dad2d7bde60c70f/verification/f_release/DECISION_20261029.md) and [release reproduction instructions](https://github.com/hlemonnier/continual-research-takehome/blob/b78de17a13161d65de4031a33dad2d7bde60c70f/verification/f_release/REPRODUCE.md).
- [Wave 6 results and controls](https://github.com/hlemonnier/continual-research-takehome/blob/5cb7e47e94659617ee4a55bda25c7f1930abbe0b/research/wave6/RESULTS_20261029.md).
- [Claude's no-sleeve and fixed-multiplier checks](https://github.com/hlemonnier/continual-research-takehome/blob/v2-factor-risk/research/v3/f_check/F_CHECK_20261029.md).

[The original master plan](Continual_Research_Master_Plan.md), [frozen protocol](RESEARCH_PROTOCOL.json), [worklog](WORKLOG.md), [C09 reproduction guide](REPRODUCE.md), [historical experiment ledger](research/EXPERIMENT_LEDGER.md) and [source register](SOURCE_REGISTER.md) preserve earlier research decisions. Their historical selection/status fields do not override the current `MODEL_SELECTION.json`. Earlier figures and protected-period claims concern the original C09 workflow, not a fresh holdout for F. The employer's continuation remains unseen.

## Data and verification discipline

Restore the large CSVs and supplied figures from the original archive; they are excluded from Git. The supplied [brief](source/Quant%20Research%20Take-Home/README.md), scorer and examples remain unchanged. Small inspectable results, source identities and rerun instructions are versioned.

Follow [AGENTS.md](AGENTS.md): prefer E2E workflows and retain evidence, including failures. If isolated testing is needed, specify failure modes and expected outcomes before tests and implementation. Never describe an unexecuted check as passed. Preserve negative research findings and the distinction between software correctness, historical performance and future evidence.
