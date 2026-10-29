# ML incremental-signal test — results: both models fail the gate; ML on these features is closed

Plan (committed before running, `6bee53f`): [ML_PLAN_20261029.md](ML_PLAN_20261029.md).
Output: `ml_incremental.json` and `ml_incremental.log`. Out-of-sample days 1008..3778, with a
causal yearly refit. Neither model was tuned.

| Signal | IC mean | IC Sharpe | 1st / 2nd OOS half | Incremental IC Sharpe over F2 (1st / 2nd half) | Corr. with F2 | Gate (incremental ≥ 1.0, both halves > 0) |
|---|---:|---:|---|---|---:|---|
| F2 (current forecast) | 0.0154 | **1.36** | 0.63 / 2.00 | — | — | reference |
| Gradient boosting | 0.0013 | 0.22 | −0.41 / 0.78 | **−0.28** (−0.59 / 0.01) | 0.15 | fail |
| Neural net (64-32) | 0.0025 | 0.45 | −0.46 / 1.25 | **−0.13** (−0.53 / 0.27) | 0.10 | fail |

- Both models see more information than F2: the same characteristics and beta, plus three
  price features. Yet on their own they forecast residual returns far worse than F2, and what
  they add beyond F2 is negative overall.
- *Interpretation:* consistent with the ceiling diagnostics (`ceiling_shapes.json`): in this
  market, the predictable part of returns is captured by the linear-plus-square
  characteristic structure, with pooled, slowly adapting premia. Flexible models spend their
  capacity fitting noise. The neural net's better second half alone (1.25) mostly overlaps
  with F2, since its incremental value is only 0.27.
- Not tested (the plan pre-specified no tuning): other architectures, other targets, ensembles.
  A tuned search on exposed data would be selection, not evidence.

Decision: no ML forecast column goes to a full-scorer test. V3 stays.
