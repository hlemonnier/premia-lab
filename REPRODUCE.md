# Reproducing the planning preflight

This package contains the master plan, frozen protocol, source reviews, preflight runner, and evidence. It is not the final strategy submission. The supplied `strategy.py` in `source/` is the original scaffold.

## Inputs

Use the user's original archive named `Quant Research Take-Home-20261026T134123Z-1-001(1).zip`. Expected size: 136,015,226 bytes. Expected SHA-256:

```
ba49564fb0d8888124fdc0b680f88c843c17359a089129f1fe28e0b94e003dd6
```

The package omits the large original CSVs/figures and generated 504-day input copies to avoid duplicating the supplied dataset. Original source-file hashes and generated prefix-input hashes are retained. The runner regenerates the prefix inputs from the verified original data. Small source text files are included unchanged for review.

## Setup on a new machine

1. Extract this planning package into a working directory.
2. Place the original ZIP in a known location and verify its SHA-256.
3. Extract the original ZIP into `source/`; it creates `source/Quant Research Take-Home/` with all 12 original members. Existing small source files should match the archive, not be edited.
4. Use Python 3.12 with NumPy and pandas. Recorded versions are NumPy 2.3.5 and pandas 2.2.3. Other package versions are captured in the evidence; no optional solver or boosting package is needed for this smoke run.

From the planning directory, run (replace only the original archive path):

```bash
python -u tools/preflight.py \
  --source 'source/Quant Research Take-Home' \
  --archive '/absolute/path/Quant Research Take-Home-20261026T134123Z-1-001(1).zip' \
  --plan PREFLIGHT_PLAN.md \
  --out evidence/preflight_reproduction
```

Use a fresh output directory on each run. The runner sets numerical-library thread limits before importing NumPy/pandas and requests one-CPU affinity. The original Linux run successfully pinned affinity; unsupported affinity on another OS is reported as a failed benchmarking precondition and requires a documented alternative environment. Do not treat that as candidate-model failure.

The exact original paths/command, frozen runner, frozen expectations, environment, hashes, actual results and economic CSV rows are in `evidence/preflight_002/`. Its `rerun.txt` uses the frozen runner snapshot and frozen expectations; it assumes the original local input paths still exist. The portable command above defines reconstruction when they do not.

Expected successful conclusion: 24 checks pass, 250 scored rows for the first 504 input rows, finite data/results, correct stock/day order, unit gross exposure for the supplied equal-weight example, repeat economic rows exactly equal, and beta approximately 1. Runtime values are machine-dependent. Equal-weight is expected to fail the assignment's beta condition; this run does not validate a candidate.

## Failed preflight history

`evidence/preflight_001/` records a real early failure in the preflight inventory assumption. Its original artifacts remain historical; see `REPRODUCE_FAILURE.md` there for the separate, explicitly unexecuted reproduction setup. That expected failure is not mixed with the successful scope result in preflight 002.

## Unexecuted gates

The golden synthetic accounting workflow, candidate causality interventions, candidate stress/solvency checks, chronological candidate comparisons, protected-period audit, long-horizon timing and clean final-submission execution are all planned and not yet run.
