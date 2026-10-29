# Reproduce the characteristic-peer wave

These are rejected research candidates, not submission packages. Main remains the selected GLS ensemble. Original task CSVs and score.py are required; no source data are redistributed.

## Source and settings

Use main base `3d668e1877541742fcb9f9a5c665ff22ba2f7c76`. Full plan: commit `1e4ad458ec8345ba96c2aad4014e8ef2ef0bbc16`, path `research/relations/PLAN_20261029.md`. The exact graph, candidate, scorer harness, E2E and analysis sources are preserved with hashes. The evidence ZIP contains a combined local research workspace; each GitHub candidate branch contains only its own new candidate module, plus shared tools and immutable GC comparison code. GC was not rescored in this wave.

Recorded environment: Python3.13.5, NumPy2.3.5, pandas2.2.3, SciPy1.17.0, scikit-learn1.8.0. Use one numerical thread. Use a fresh WORK directory whenever data, code or versions change; the research input cache does not automatically reject a different source path after population.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/fresh-peer-work'
# From either branch's repository root, or the ZIP's repo/ directory:
python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate G
```

This requires the supplied original scorer identity and checks G's net Sharpe against1.5332155606881952. The recorded full baseline also compared all four economic daily columns to the prior archive, error0.0. The private CSV and original README hashes are in `evidence/inputs/source_identity.json`.

## Alpha branch

On `research-gls-peer-alpha-20261029`:

```bash
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model P --mode synthetic
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model O --mode synthetic
python research/relations/runner.py --source "$SOURCE" --work "$WORK" --model P
python research/relations/runner.py --source "$SOURCE" --work "$WORK" --model O
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model P --mode market
```

O is the own-only explanatory control. PS (relabelled graph) was not admitted because P failed; do not retroactively add it to the registered executed experiments.

## Specific-risk branch

On `research-gls-peer-risk-20261029`, keeping the same input WORK and original source (or using the combined ZIP workspace):

```bash
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model V --mode synthetic
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model VG --mode synthetic
python research/relations/runner.py --source "$SOURCE" --work "$WORK" --model V
python research/relations/runner.py --source "$SOURCE" --work "$WORK" --model VG
python research/relations/e2e.py --source "$SOURCE" --work "$WORK" --model V --mode market
```

VG is the global-pooling explanatory control. Alpha and factor risk stay frozen. The candidate's graph is built inside rebalance using only the supplied prefix.

## Combined comparison

After G/P/O/V/VG have been generated in the same WORK directory:

```bash
python research/relations/assess.py --source "$SOURCE" --work "$WORK"
```

This computes the fixed paired-block bootstrap, summary criteria, forecast diagnostics and explanatory variance/graph diagnostics. It does not fit another candidate. The block seed is20261105,3000 draws for each of21/63/126 days. Primary decisions remain rejection; no stress scenario, post-score tuning or combination was run.

The reported co-movement diagnostic is the daily cross-sectional ratio `v'Wv/(v'v)`, averaged over dates, not a Pearson correlation and not a percentage-explained decomposition. Variance QLIKE uses estimated factor-residual squares, not hidden true variances.

## Contents and limits

The evidence package preserves daily economic rows, fit records, all completed test receipts, logs, inputs/code/output hashes, the expected preimplementation missing-module failure, and local Git history. Forecast/target/large diagnostic arrays and input CSVs are excluded; their hashes and rerun scripts are present. Initial VG synthetic log was interrupted by a tool timeout; the completed rerun and its log are retained. A display-only metric-key lookup failed without affecting experiments. No separate reviewer or century/clean-release audit was performed. No change was made to main or its ten submission files.
