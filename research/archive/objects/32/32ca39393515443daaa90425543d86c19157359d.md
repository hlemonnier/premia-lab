# Independent replay of the existing allocator suite

Written before this reviewer executes the existing suite. No new unit tests or strategy code are being written. Source is the pinned GitHub snapshot at `afed8d0cb017acda151c4ea262fc30db7568a4bb`; `source_manifest.json` binds the supplied suite, allocator and baseline.

## Expected outcome and failures

Run the unchanged `research/v2/test_allocator.py` once, with NumPy numerical libraries restricted to one thread and cvxpy/Clarabel installed in an isolated `/tmp` dependency directory. Expect each supplied check to pass and process exit 0. A failed check or exception remains a failure and will not be removed or retuned. In particular inspect convex-oracle objective/weight agreement, equality, caps, zero-factor reduction, no-trade behavior, input rejection and deterministic behavior. A timing failure is hardware-specific and distinct from numerical correctness. This suite alone does not verify the full trading workflow, risk-state lifecycle or default convergence on the real market; the coordinator is separately executing the unchanged scorer with solver diagnostics.

## Exact command

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=/tmp/v2-allocator-review-deps python /workspace/scratch/a83c191d516f/v2-review-snapshot/research/v2/test_allocator.py
```

`run_existing_suite.py` only captures the exact existing command, stdout, stderr, environment versions, elapsed wall time and exit code. It does not add assertions, modify the suite or mutate production sources.

## Dependency setup

The first ordinary sandbox pip attempt failed because network access was denied. The authorized isolated dependency installation was then retried through the execution approval mechanism. Actual versions and outcome are recorded at execution time.
