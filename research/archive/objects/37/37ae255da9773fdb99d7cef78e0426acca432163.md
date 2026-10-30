# Reproduce Wave 5

Use a fresh work directory. Nothing in this workflow selects or submits a strategy.
The archive supplies the exact upstream V3 files, the needed Wave4 helper code,
Wave5 code, and two prior economic-row arrays used by the reference gate.
The original market CSVs are not redistributed.

## Layout

Run commands from `Wave5/repo`. Keep `Wave5/wave4_evidence/results/B0_rows.npy`
and `R1_rows.npy` alongside that repository directory. The replay runner uses
this explicit relative layout for its historical reference check. For a fresh
GitHub checkout, extract the previous Wave4 ZIP to the sibling directory
`wave4_evidence`, or copy these two supplied reference arrays there.

Recorded environment: Python3.13.5, NumPy2.3.5, pandas2.2.3, SciPy1.17.0,
scikit-learn1.8.0. No GPU, PyTorch, or external data required.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/fresh-wave5-work'
mkdir -p "$WORK"
python research/wave4/reproduce_baseline.py --source "$SOURCE" --work "$WORK"
python research/wave5/run_wave5.py --source "$SOURCE" --work "$WORK" --mode R1
python research/wave5/e2e_wave5.py --source "$SOURCE" --work "$WORK" --mode synthetic
for MODE in H P E A_pool A_cross; do
  python research/wave5/run_wave5.py --source "$SOURCE" --work "$WORK" --mode "$MODE"
done
for MODE in H P E; do
  python research/wave5/e2e_wave5.py --source "$SOURCE" --work "$WORK" --mode market --candidate "$MODE"
done
python research/wave5/assess_wave5.py --source "$SOURCE" --work "$WORK"
```

Do not reuse a work directory after changing inputs, dependencies or code. The
inherited raw-array loader has no automatic cache invalidation. Large forecast
and target arrays are saved by replays, but are omitted from this evidence ZIP;
the manifest records their identities for re-creation checks. Daily economic
rows, metrics, fitted coefficients, bootstrap draws and E2E receipts are included.
Timing columns are naturally not bit-reproducible. Trading-economic columns and
causal forecast/position prefixes are the controlled quantities.

Expected headline scores: V3 1.4447333005566665; R1 1.4576547036224103;
H 1.4590786996561371; P 1.3624617433444741; E 1.4460721441758073;
A_pool 1.4572048979345196; A_cross 1.4453045200524623.
All 96 E2E assertions pass in the recorded environment. No primary candidate
passes the preregistered development gate against R1. Both conditional-combination
flags are false. Do NOT run extra combinations or change thresholds to produce
a winner and call that the registered Wave5 experiment.

The original preregistration is commit09cbdc7614c8148869acc6d98e18598e3208a376,
`research/wave5/PLAN_20261029.md` on `gpt-wave5-causal-research-20261029`.
The ZIP contains its receipt and a local Git bundle proving the E2E-before-model
file ordering. That local history is not a full clone of the remote repository.
The five required upstream source files and four new Python files were verified
against the remote Git blob hashes, as recorded in VERIFICATION_SUMMARY.json.

No deployable strategy was promoted. ResearchPolicy requires an explicit mode;
it does not read scores, select a mode, or load pretrained coefficients. The
synthetic and altered-future tests evaluate software behavior, not new evidence
of financial outperformance. The 15-year sample remains exposed development data.
