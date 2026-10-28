# Allocator review evidence

Status: the unchanged supplied suite completed, exit 0, all 38 supplied checks PASS. No new unit tests or strategy implementation were written. See `PLAN.md` for the pre-run scope and `source_manifest.json` for exact source identity. `result.json` records the command, versions, one-thread environment, elapsed time and check counts. `stdout.txt` and `stderr.txt` preserve the complete captured output. All source hashes remained unchanged (`source_unchanged_after.json`).

Dependencies were installed into `/tmp/v2-allocator-review-deps`; the ordinary sandbox attempt was blocked by network permissions, then the execution approval mechanism allowed the isolated installation. The selected versions were cvxpy 1.9.3, Clarabel 0.11.1, NumPy 2.5.4 and SciPy 1.18.1. To reproduce those principal numerical dependencies:

```sh
python -m pip install --target /tmp/v2-allocator-review-deps cvxpy==1.9.3 clarabel==0.11.1 numpy==2.5.4 scipy==1.18.1
python evidence/v2_allocator_review_20261028/run_existing_suite.py
```

The supplied suite's own process path is absolute and is recorded in `result.json`; update that path in a copied capture wrapper only when reproducing in a different workspace. Preserve the original test bytes. The tests use six deterministic random n=200 problems, one full-size reference problem, and their other existing assertions. This is evidence for those cases, not a proof of convergence on all admissible inputs. Runtime here is an environment-specific observation.
