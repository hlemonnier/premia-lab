# Reproduce Wave 4

Use the private repository branch `gpt-wave4-ml-control-20261029`, its unchanged
`handoff_v3` directory, and the original take-home source folder. Do not use the
cached experiment policies as a submission: only `r1_candidate.py` recomputes
its forecasts and risk models causally from arbitrary input histories.

## Environment and fresh work directory

The recorded environment was Python 3.13.5, NumPy 2.3.5, pandas 2.2.3,
SciPy 1.17.0 and scikit-learn 1.8.0. Numerical tolerances, rather than exact
cross-platform bit equality, are the contract. The original run used one
BLAS/OpenMP thread per process. No GPU or deep-learning framework is required.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/fresh-wave4-work'
mkdir -p "$WORK"
# Run these from the repository root, in this order.
python research/wave4/reproduce_baseline.py --source "$SOURCE" --work "$WORK"
python research/wave4/run_wave4.py --source "$SOURCE" --work "$WORK" --mode cache
python research/wave4/run_wave4.py --source "$SOURCE" --work "$WORK" --mode controls
python research/wave4/run_wave4.py --source "$SOURCE" --work "$WORK" --mode innovation
python research/wave4/run_wave4.py --source "$SOURCE" --work "$WORK" --mode risk
python research/wave4/control_mix.py --source "$SOURCE" --work "$WORK"
python research/wave4/verify_r1.py --source "$SOURCE" --work "$WORK" --mode full
python research/wave4/verify_r1.py --source "$SOURCE" --work "$WORK" --mode prefix
python research/wave4/verify_r1.py --source "$SOURCE" --work "$WORK" --mode mutations
```

Use a NEW work directory when changing input files, code, or library versions.
The research cache is an experiment-speed convenience and does not validate
its provenance automatically. It must not silently be reused across different
sources. Research caches can take several GB; they are not part of a submission.
`controls` requires the original baseline rows produced by the first command.
`full` requires the research R1 rows, targets and risk multipliers; prefix and
mutation checks require the full integrated run. The source `score.py` is never
patched. Failed experiments are intentionally retained.

## Uncertainty and the negative variance diagnostic

After the runs, the following calculation reproduces the recorded diagnostic:

```python
import json
from pathlib import Path
import numpy as np
w = Path('/absolute/path/fresh-wave4-work')
a = np.load(w/'results/B0_cached_rows.npy')
b = np.load(w/'results/R1_rows.npy')
x, y = a[:, 0]-a[:, 1], b[:, 0]-b[:, 1]
n = len(x)
rng = np.random.default_rng(20261029)
deltas = []
for _ in range(3000):
    starts = rng.integers(0, n, size=int(np.ceil(n/63)))
    idx = ((starts[:, None] + np.arange(63)) % n).ravel()[:n]
    aa, bb = x[idx], y[idx]
    deltas.append(np.sqrt(252)*(bb.mean()/bb.std()-aa.mean()/aa.std()))
print('Paired interval:', np.quantile(deltas, [.025, .975]))
print('Fraction positive:', np.mean(np.asarray(deltas) > 0))
d = np.load(w/'cache/d.npy', mmap_mode='r')[252:3778]
u2 = np.load(w/'cache/u2.npy', mmap_mode='r')[253:3779]
ratio = np.load(w/'cache/R1_ratios.npy', mmap_mode='r')[252:3778]
mult = .5 + .5*ratio
# QLIKE difference; the label-only constant cancels.
qlike_delta = np.mean(np.log(mult) + u2/d*(1/mult - 1))
print('QLIKE change (lower better):', qlike_delta)
```

The bootstrap interval is development-data uncertainty, not a probability of
future superiority, and it is not corrected for the whole historical research
search. Mutation-case Sharpes test software causality, not economic robustness.

## Stage the candidate without replacing V3

```bash
mkdir -p "$WORK/staged_r1"
cp -R handoff_v3/model_v3 "$WORK/staged_r1/model_v3"
cp research/wave4/r1_candidate.py "$WORK/staged_r1/strategy.py"
cp "$SOURCE/score.py" "$WORK/staged_r1/score.py"
(cd "$SOURCE" && python "$WORK/staged_r1/score.py" strategy)
```

The copied scorer is byte-for-byte unmodified; running from the source directory
loads the original CSVs while importing the staged strategy. The copied scorer
is for local validation only, not an additional submission requirement. Do not add data files, fitted models,
research caches or sampled future paths to the candidate package. Both forecast
channels (alpha and risk multiplier) must be covered by the grader's altered-
future check. A two-channel array is explicitly allowed by the assignment.

## Provenance

The connector returned source text, not a local Git clone. For this session,
only the executable V3 paths required by the policy were transcribed locally,
with comments and unused paths abbreviated. Those local files are NOT claimed
to be byte-identical to the upstream files. Original V3 and the cached replay
matched to <3e-13 Sharpe error and to zero difference in daily economic rows.
The candidate's streamed integration matched its research run in every economic
row and target weight. The ZIP preserves the exact local reference separately,
plus its hashes, so the executed environment is inspectable. Repository commands
above use the authoritative upstream `handoff_v3`, which was never overwritten.
An independent replay using a fresh full Git clone remains a separate review
step; do not call this session an independent multi-agent audit.
