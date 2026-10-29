# Reproduce the F release audit

Extract the evidence ZIP. It contains repo/, work/prior/ and recorded receipts,
not the private CSV inputs or multi-GB generated arrays. Use a fresh work/cache.
The supplied source folder must contain the original README, score.py and CSVs.

```bash
cd F_validation/repo
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/F_validation/work'
V='verification/f_release'
python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind B0 --name B0
python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind F --name F
python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind T --name T
python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind release --name release
python "$V/release_e2e.py" --source "$SOURCE" --work "$WORK" --mode equivalence
python "$V/release_e2e.py" --source "$SOURCE" --work "$WORK" --mode synthetic
python "$V/release_e2e.py" --source "$SOURCE" --work "$WORK" --mode market
python "$V/package_audit.py" --source "$SOURCE" --work "$WORK"
python "$V/transition_e2e.py" --source "$SOURCE" --work "$WORK"
for scale in 2 3; do
  python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind release --name F_fee$scale --cost-scale $scale
  python "$V/runner.py" --source "$SOURCE" --work "$WORK" --kind B0 --name B0_fee$scale --cost-scale $scale
done
python "$V/century.py" --source "$SOURCE" --work "$WORK"
python "$V/assess.py" --work "$WORK"
```

The century script constructs a repeated-history operational path and writes
several GB of disk-backed arrays. Its performance is not independent future
validation. Daily score rows and original evidence are retained. Supplied input
cache reuse is only valid for the same source dataset; use a new work/cache for
changed inputs or library versions. Prior evidence is available in work/prior.

For an isolated submission-shape replay, copy handoff_f/ into an otherwise
empty directory, add the original score.py and the user's original CSVs, and
run `python score.py strategy` there with PYTHONPATH unset. The separately
provided candidate ZIP contains exactly handoff_f/ contents, not tests or data.

Tests are deterministic within the tested numerical environment. Tiny numerical
differences across library/BLAS versions are not evidence of leakage; the stated
causal tolerance is 1e-10 and the preexisting permutation-weight tolerance is
1e-8. No threshold or model should be tuned to the new outputs. Full Git history
of the local audit is included as a bundle. Remote main was not changed.
