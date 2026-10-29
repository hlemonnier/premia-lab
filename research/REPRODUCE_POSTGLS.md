# Reproduce GC and H20 without touching the selected submission

The baseline is main commit `3d668e1877541742fcb9f9a5c665ff22ba2f7c76`. Each candidate is on its own branch. The downloadable evidence ZIP includes both in one local research workspace for the comparison, not for submission. The frozen main runtime files are included and verified by Git blob identity.

For a Git checkout, start on `research-gls-correlation-combination-20261029` and retrieve the second candidate without merging changes into main:

```bash
git fetch origin research-gls-horizon20-20261029
git restore --source=origin/research-gls-horizon20-20261029 -- research/horizon20
```

Alternatively, the evidence archive's `repo/` already contains both candidate directories. Run commands from that root with the original private task folder, containing unmodified score.py and the three CSVs. Start with a NEW work directory: input caches do not automatically validate provenance when reused.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/new-post-gls-work'
python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate G
for candidate in GC H20 L20; do
  python research/common/e2e_postgls.py --source "$SOURCE" --work "$WORK" --candidate "$candidate" --mode synthetic
done
for candidate in GC H20 L20 F CORR; do
  python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate "$candidate"
done
for candidate in GC H20; do
  python research/common/e2e_postgls.py --source "$SOURCE" --work "$WORK" --candidate "$candidate" --mode market
done
```

The supplementary stock-order checks intentionally retain their strict original thresholds. On the recorded runtime, the default checks below exit nonzero because of aggregate-gross differences of a few 1e-10. Inspect their saved receipts. Do not treat those nonzero exits as an instruction to suppress failures, change tolerances or alter the scored solver.

```bash
python research/common/permutation_check.py --source "$SOURCE" --work "$WORK" --candidate G
python research/common/permutation_check.py --source "$SOURCE" --work "$WORK" --candidate GC
python research/common/permutation_check.py --source "$SOURCE" --work "$WORK" --candidate H20
```

Then run the supplemental, verification-only higher-accuracy workflow and fixed statistical assessment:

```bash
for candidate in G GC H20; do
  python research/common/permutation_check.py --source "$SOURCE" --work "$WORK" --candidate "$candidate" --refine
done
python research/common/assess_postgls.py --source "$SOURCE" --work "$WORK"
```

The assessment records the original failed stock-order receipts separately from the economic/causal shortlist. It does not promote a model. GC met the economic/causal conditions for these four additional replays; H20 did not. Their frozen reproduction commands are:

```bash
for candidate in G GC; do
  python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate "$candidate" --sleeve 0
  python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate "$candidate" --fees 2
done
```

No refined allocator is used by `harness.py`. No third fee level, new blend or horizon is part of this wave. Source arrays remain private. Research code retains large forecast and target files in the work directory for validation; those are not submission inputs.

Recorded environment: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3. One numerical thread per process. The original scorer SHA-256 is `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

Primary plans are authoritative on GitHub at commits `21ca3e98d00ef61188e29477a78fc3187cb7c427` (GC) and `dd1901cb45e9ef9a3676bc3a60a514c6fca11ee8` (H20). Local Git history proves the main E2E workflow preceded candidate implementation; the supplemental permutation workflow was added later to close coverage. The archived main source is an exact verified export, not claimed to be a full network clone. An independent reviewer and actual-century new-candidate execution remain unperformed.
