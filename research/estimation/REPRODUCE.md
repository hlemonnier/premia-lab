# Reproduce the robust/Kalman research round

Use the original private take-home folder and a fresh work directory. Runtime: Python 3.13.5, NumPy2.3.5, SciPy1.17.0, pandas2.2.3, scikit-learn1.8.0. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1. The scorer must have SHA-256 ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96.

The two branches each own one model. Use separate checkouts/worktrees of `research-gc-robust-premia-20261029` and `research-gc-kalman-premia-20261029`. Both inherit the frozen GC reference. They may share a fresh WORK directory because the supplied input files and reference implementation are identical; never reuse it after changing source inputs or code. The evidence ZIP additionally contains a combined executed local snapshot for convenience, not a deployable submission.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SOURCE='/absolute/path/Quant Research Take-Home'
WORK='/absolute/path/fresh-estimation-work'
# From either branch's repository root:
python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate G
python research/common/harness.py --source "$SOURCE" --work "$WORK" --candidate GC
# From the robust branch:
python research/estimation/e2e.py --source "$SOURCE" --work "$WORK" --candidate R --mode synthetic
python research/estimation/harness.py --source "$SOURCE" --work "$WORK" --candidate R
python research/estimation/e2e.py --source "$SOURCE" --work "$WORK" --candidate R --mode market
# From the Kalman branch:
python research/estimation/e2e.py --source "$SOURCE" --work "$WORK" --candidate K --mode synthetic
python research/estimation/harness.py --source "$SOURCE" --work "$WORK" --candidate K
python research/estimation/e2e.py --source "$SOURCE" --work "$WORK" --candidate K --mode market
# Either branch; requires both candidate result sets, not the other model's code:
python research/estimation/assess.py --source "$SOURCE" --work "$WORK"
```

The model source files import the frozen correlation reference and common likelihood helper. No edits to root strategy.py/model_f/gls_alpha.py are needed. The runner recomputes all predictions causally; saved forecast/target arrays are verification evidence, not deployed model parameters. The original scorer is never patched.

The fixed hypotheses and failure modes are recorded in each branch's PLAN_20261029.md, committed before model implementation. The local Git bundle preserves the workflow-before-model ordering and expected initial missing-module failure. Code listings in the evidence snapshot are the exact executed files; source/input/output identities are in the manifest. Full-history arrays and private source CSVs are deliberately excluded from the evidence ZIP, but rerun commands regenerate them.

Neither candidate passes the economic gate, so no-sleeve, double-fee, standalone release packaging, actual-century execution and separate reviewer assessment were not performed in this round. Main remains the selected GLS submission; none of this research code is a submitted replacement.
