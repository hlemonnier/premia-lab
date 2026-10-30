# F standalone candidate — not yet promoted

Place strategy.py and model_f/ beside the original score.py. Keep the supplied
CSV files in the working directory and run `python score.py strategy`.
Only installed permitted libraries are needed. Use one BLAS/OpenMP thread for
timing: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1.

No historical data or fitted models are included. forecast() starts/reset a
session; rebalance() then advances one published day at a time. Risk payload
row t uses only input rows <t. The original scorer accepts arbitrary payload
width with days first; this package uses (days, stocks+27).

This package preserves Wave6 F mathematics. Research-only imports and large
position diagnostic logs are removed. The allocator, engine and base policy
are unchanged copies of the verified V3 sources. See the release evidence for
exact equivalence, causal checks, runtime and promotion status.
