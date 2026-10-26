# Reproducing the research and its planning preflight

The repository contains the frozen plan, development strategies, independent reviews, complete-run evidence and reproduction scripts. It is not the final strategy submission. The supplied `strategy.py` in `source/` remains the unchanged original scaffold. Candidate implementations are in `submission/` and require their named JSON configurations for research comparisons.

## Reproduce an executed discovery candidate

Restore the original archive below into `source/`. Use Python 3.12 and the recorded versions in `requirements-research.txt`; each run also records its exact environment. From the repository root, prepare only the permitted discovery cache:

```bash
python tools/prepare_discovery.py \
  --project . \
  --cache cache/discovery \
  --out evidence/data_preparation_reproduction
```

This preparation validates source identities and reads numeric rows `[0,2016)` only. It does not open validation or audit outcomes. Then reproduce, for example, C06:

```bash
python tools/run_candidate.py \
  --project . \
  --strategy submission/strategy_gls_factor.py \
  --config research/configs/C06_gls_factor.json \
  --out evidence/discovery_C06_reproduction
```

Use a new output directory for every run. The runner freezes the candidate, all Python helpers, configuration, original scorer and expectations before importing them. It requests one available CPU and fixes numerical-library threads before imports. The recorded original runs used explicit `taskset` CPU assignments to avoid direct affinity contention; their environment records identify them. Timing differs with hardware and shared load.

For an exact historical code reproduction, use the source/configuration snapshots under that run's `source/candidate/` and `config.json`, plus its frozen runner, scorer, protocol and expectations as shown by `rerun.txt`. Historical commands contain the original absolute workspace paths; replace the project and output locations when reproducing on another machine, retaining the frozen source/configuration files. On a clean clone, the large `.npy` outputs are regenerated; their hashes, original ledgers and inspectable summaries are already versioned.

The source code chooses no candidate based on the final row count, and the scorer begins with an empty book at 252. Discovery produces 1,762 score rows, indices 253 through 2014, under the official endpoint convention. This is not a holdout score. Do not pass all 15 years into a candidate before the relevant protocol gate.

## Reproduce the first-wave comparison

`evidence/comparison_wave1_001/rerun.txt` points to its frozen reporting script and expected inputs. It reads completed C01–C04 daily ledgers, fits no strategy, and performs the predeclared paired moving-block bootstrap. The frozen copies of its inputs, actual bootstrap draws, summaries and report are retained. A reporting pass is separate from candidate causality and from out-of-sample validation.

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

## Executed and remaining gates

The synthetic accounting workflow has executed with 44 passing checks. C01 and C02 each completed their configured 600-row causal smoke workflow with 28 fresh-process scenarios and exact protected equality; earlier interrupted smoke runs remain explicitly incomplete. New diagonal, factor, precision and exact-gross numerical components have preimplementation check records and subsequent executed evidence. Ten actual discovery configurations have completed the unmodified scorer with 20 workflow checks each at this checkpoint.

Full finalist-specific causality, long-history runtime, protected validation, the locked audit, and clean final-submission execution remain unexecuted. No earlier component or smoke result substitutes for those gates. Consult the current worklog rather than the frozen planning protocol's historical status fields.
