# Reproduce the GLS attribution audit

Use branch `research-gls-attribution-review-20261029`. The original F and GLS files remain unchanged. Use a fresh work directory: the inherited loader caches input arrays and must not be reused across different source files.

The original private task folder must contain the unchanged score.py, returns.csv, characteristics.csv and costs.csv. The scorer's SHA-256 is checked automatically. Install the root requirements and pandas (the scorer needs pandas). Recorded environment: Python3.13.5, NumPy2.3.5, pandas2.2.3, SciPy1.17.0, scikit-learn1.8.0. Other versions are not certified here.

Run from the repository root, one numerical thread per process:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/new-gls-review-work'
mkdir -p "$WORK"
# The default and tightened-only dense tests retain two numerical path-equality
# failures. Run them to inspect that documented limitation; do not call them passed.
python research/gls_review/e2e_review.py --source "$SOURCE" --work "$WORK" --mode algebra
python research/gls_review/e2e_review.py --source "$SOURCE" --work "$WORK" --mode algebra --strict-numerics
# Objective-preserving verification-only refinement; NOT used in market scoring.
python research/gls_review/e2e_review.py --source "$SOURCE" --work "$WORK" --mode algebra --polish-numerics
python research/gls_review/e2e_review.py --source "$SOURCE" --work "$WORK" --mode controls
python research/gls_review/run_review.py --source "$SOURCE" --work "$WORK" --variant F
python research/gls_review/run_review.py --source "$SOURCE" --work "$WORK" --variant GLS_original
for variant in G_D O_D G_S O_S D_D O_A G_N; do
  python research/gls_review/run_review.py --source "$SOURCE" --work "$WORK" --variant "$variant"
done
python research/gls_review/e2e_review.py --source "$SOURCE" --work "$WORK" --mode market
for variant in F G_D O_D G_S O_S; do
  python research/gls_review/run_review.py --source "$SOURCE" --work "$WORK" --variant "$variant" --sleeve 0
done
for variant in F GLS_original; do
  for fee in 2 3; do
    python research/gls_review/run_review.py --source "$SOURCE" --work "$WORK" --variant "$variant" --fee "$fee"
  done
done
python research/gls_review/assess_review.py --source "$SOURCE" --work "$WORK"
```

`--prior /path/to/prior_rows.npy` is optional for the F/GLS original reproduction. The evidence ZIP includes the immutable prior rows. G_D must follow GLS_original because it compares every forecast and target against that original run. Market E2E must follow G_D and O_D full runs. Assessment must follow all primary and robustness runs. Do not continue after an unexplained failure; the two default algebra-path failures above are the specific documented numerical exception, not a blanket permission to ignore failing tests.

Inspect `checks/`, `runs/*/summary.json`, `ASSESSMENT.json`, and the daily economic rows. These are development-sample computations, not held-out future scores. Do not deploy the dense verification solver or treat the diagnostic controls as selected models. No changes to main are part of this workflow.

The ZIP preserves failed receipts, logs, original code snapshots, local preimplementation Git history and the separate remote commit identities. Large private input and forecast/position arrays are omitted but hashed. The local bundle is a provenance archive, not a clone of the full remote repository. Model/checker source Git blob identities were independently matched to remote upload responses.
