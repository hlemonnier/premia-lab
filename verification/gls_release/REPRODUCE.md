# Reproduce the frozen GLS release checks

Use branch `research-gls-release-20261029` and the original take-home folder.
This branch preserves the original research source alongside handoff_gls;
main remains the F submission. Run from the repository root with a NEW work
directory. Never reuse the input cache after changing source files or code.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/new-gls-release-work'
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode package
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode synthetic
```

The frozen synthetic suite intentionally retains an observed failed strict
stock-permutation gross-exposure equality at1e-10; its receipt has34/35 passes.
Do not hide this exit code in an all-green summary or loosen its tolerance.
Run the prespecified supplemental investigation, which reproduces the failure
and compares the same objective at higher numerical solution accuracy:

```bash
python verification/gls_release/permutation_diagnostic.py --repo . --source "$SOURCE" --work "$WORK"
```

Continue the remaining independent verification scopes explicitly (not by
claiming the previous suite passed):

```bash
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode full
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode reference
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode century
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode late
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode market
python verification/gls_release/release_checks.py --repo . --source "$SOURCE" --work "$WORK" --mode cli
```

`full` optionally accepts `--prior /path/GLS_original.npy` from the attribution
evidence archive to compare all archived economic columns. The reference run
compares all current forecasts, positions and economics against the packaged
run. The publication uses that optional prior comparison. Without it one check
is absent, not implicitly passed.

All economic scoring uses the original scorer and original allocator. Only the
small constructed permutation diagnostic uses the verification-only KKT wrapper.
The century and late modes allocate disk-backed repeated inputs of about2.8GB
plus forecast/output arrays. Use sufficient free disk and memory. This is not
a new market simulation; century Sharpe is not used for model selection.

`cli` extracts/stages only the candidate files and original scorer, hard-links
user-owned CSVs into a fresh directory, empties PYTHONPATH and invokes
`python score.py strategy`. For a literal manual run, extract GLS_Candidate.zip
into the supplied task folder, without replacing its scorer or CSVs.

## Environment and receipts

Tested: Python3.13.5; NumPy2.3.5; SciPy1.17.0; scikit-learn1.8.0;
pandas2.2.3 for the scorer. Each numerical process uses one BLAS/OpenMP thread.
Timings are shared-host measurements, not guarantees on the evaluator's hardware.
Other package versions have not been certified in this release.

Checks and logs preserve failures. The initial prepackage launch is expected
to fail before strategy.py exists; the container's unsupported streaming launch
failed before strategy execution. Input/source hashes and the tested package
are recorded separately. New evidence does not rewrite previous inconclusive
statistical results. See REVIEW_REQUEST.md: independent review remains pending.
