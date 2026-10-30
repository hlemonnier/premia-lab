# Reproduce Wave 6

Run from the repository root on branch `gpt-wave6-risk-state-20261029`, or from
`Wave6/repo` in the evidence archive. Use the ORIGINAL supplied source folder
containing `returns.csv`, `characteristics.csv`, `costs.csv` and `score.py`.
Do not use the research cache as a deployed forecasting model.

## Environment

Recorded: Python3.13.5, NumPy2.3.5, pandas2.2.3, SciPy1.17.0, scikit-learn1.8.0.
The source scorer is unmodified. Models require only NumPy, scikit-learn and the
standard library; the supplied scorer additionally uses pandas. Cross-version
bit identity is not asserted. Every numerical worker used one BLAS/OpenMP thread.
The two concurrent research workers used separate policies and state.

## Exact workflow

Use a NEW work directory for different sources, code, or library versions.
Input-array caches must not be reused across different datasets. Source CSV
hashes and reference-source identities are recorded by the references run.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/fresh-wave6-work'
PRIOR='/absolute/path/Wave6/previous_results'

# From the repo root:
python research/wave6/e2e_wave6.py --source "$SOURCE" --work "$WORK" --mode synthetic
python research/wave6/run_wave6.py --source "$SOURCE" --work "$WORK" --prior "$PRIOR" --mode refs
for MODE in C F I T; do
  python research/wave6/run_wave6.py --source "$SOURCE" --work "$WORK" --mode "$MODE"
done
for MODE in C F; do
  python research/wave6/e2e_wave6.py --source "$SOURCE" --work "$WORK" --mode market --candidate "$MODE"
done
python research/wave6/assess_wave6.py --work "$WORK" --prior "$PRIOR"
```

References require `B0_rows.npy` and `H_rows.npy` from the previous evidence;
assessment also requires `R1_rows.npy`. The package supplies these unchanged in
`previous_results`. The runner verifies reference economic rows and Sharpe;
the original V3 reference source manifest, previously ZIP-only, is preserved
on this isolated branch at `research/wave5/UPSTREAM_IDENTITY.json`.

The complete models return an `(days, stocks+27)` forecast payload: all stock
alpha forecasts, one common specific-variance multiplier, then 26 factor-variance
multipliers. Both alpha and risk information must be covered by altered-future
checks. None of the policy code loads a trained model or historical scores.

`C` and `F` are primary candidates. `I` and `T` are explanatory controls. `CF`
is blocked by the CLI unless the registered combined-entry gate has passed;
it did not pass in this wave. Do not modify model parameters or run extra
combinations to reproduce the reported result.

## Read the exceptions, not just the green result

The initial E2E implementation preceded the models and intentionally failed on
a missing-module import. The original constructed-data run then had four
stock-permutation position failures at1e-10, with differences below6.20e-10.
Unchanged B0 also exhibited this numerical issue. Before any new market score,
only the permutation-position budget was amended to1e-8 (with aggregate-exposure
and cashflow checks). Causality/prefix/reset tolerances remain1e-10; their final
maximum errors are0.0. Read `NUMERICAL_AMENDMENT.md` and the retained failures.

The reports and JSON distinguish a development-shortlist pass from a strong
statistical-promotion pass. F passes the former and fails the latter. No
production handoff has been overwritten. This folder is research evidence,
not a submission-ready replacement for V3 and not an independent-agent audit.

The session-only `execute_registered.py` and `execute_market_checks.py` are
included in the ZIP/local Git history as command provenance. They expect the
session directory layout; the portable commands above are preferred.
