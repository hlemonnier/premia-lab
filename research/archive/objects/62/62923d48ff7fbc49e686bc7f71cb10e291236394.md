# V2 independent causality / state E2E audit plan

Recorded before writing the audit harness or executing these cases. Reviewed source is pinned afed8d0cb017acda151c4ea262fc30db7568a4bb. No candidate source will be edited. This is an independent integration audit of the supplied forecast -> immutable scorer -> incremental risk -> target -> drift/cost workflow, not a new model experiment or postimplementation unit-test suite.

## Setup and inputs

Use the unmodified handoff_v2 four files and supplied score.py. Use Python/NumPy/Pandas from the installed runtime, BLAS threads fixed to one. Generate one deterministic synthetic fixture, seed 20261028, 340 days, 96 stocks, 13 persistent characteristics, market plus characteristic-dependent returns, static 2–8 bp costs. This fixture is intended only to exercise nonzero forecasts and holdings. It is not evidence about alpha, actual-market performance or deadline runtime. Preserve the exact generation code, fixture arrays, source SHA256 identities, process commands, logs and outputs.

## Prospective expectations / failure modes

1. Two fresh baseline processes must produce identical forecasts, targets and five economic/scoring columns (exclude measured runtime).
2. Replace both returns and characteristics from zero-based row 300 onward. A fresh run must leave forecast rows <=300, close-of-day targets <300, and ledger rows <300 identical. Later forecasts/decisions must respond, preventing vacuous comparisons.
3. Truncate to length 301. Compare all available forecasts and close-of-day decisions with the baseline prefix, and compare overlapping ledger economics. The supplied scorer excludes its terminal row; respect its actual index mapping.
4. Repeat altered-future execution with return-array Fortran layout and characteristic-array Fortran layout separately. Numerical equality should hold to 1e-12 absolute / 1e-10 relative. Bitwise equality is also recorded because the brief claims canonical layouts and exact protected prefixes. Any rounding-only discrepancy is explicitly classified as layout sensitivity, not economic future information.
5. Restart integration: in one process run a baseline stream ending at risk-state history length 300, then launch an alternative history at scorer start 299, whose initial risk-state history length is also 300. The second run's complete ledger and first target should agree with a fresh-process alternate run with the same arguments. This deliberately tests the public scorer's start option plus engine global-state identity, beyond the usual default-start full replay. Record the standard default-start repeated-run control separately; do not claim default scorer leakage from a failing custom restart.
6. Standard repeated full score.run calls on two different histories from start 252 must match a fresh alternate run (shorter starting history should reset the old cache).
7. Future mutation cases inspect the packaged handoff, not the research forecast factory. Existing research causality scripts are reviewed separately for coverage and failure signaling.

## Scope and decisions

No reoptimization, hyperparameter changes or new strategy variant. Record pass/fail per expectation, exact maximum differences and first differing row. The fixture and any failure remain preserved. A failure prompts a source-linked repair recommendation for Claude; this auditor does not implement it. A passing check establishes only the exercised workflow. No synthetic score will be used to rank research candidates.

## Intended command

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python evidence/v2_causality_review_20261028/run_e2e.py --snapshot /workspace/scratch/a83c191d516f/v2-review-snapshot --out evidence/v2_causality_review_20261028/run_001

The harness is to be written after this plan, and will refuse an existing output directory. Exact expanded subprocess commands are saved with actual results.
