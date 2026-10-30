# Prospective F3 complete-workflow verification

29 October 2026. Written before `prototype.py`. The expected missing-policy run
must be retained before implementing F3. The harness is `e2e.py`; the original
scorer and copied F2/VTvol references stay unchanged.

## Synthetic fixture and expected outcomes

Use seed20261029, T640, N64 and 13 characteristics with AR coefficient0.95.
The exogenous market alternates volatility0.003/0.020 in80-day blocks and has
independent zero-mean Gaussian innovations. Each stock has true market beta1.
The conditional signal at return date t uses only characteristics at t-1 and
the independently calculated state through t-1. Its 26 coefficients are zero
except linear0:+0.003, linear1:-0.0025 and square0:+0.0015. Add a constant
linear2 premium0.0003 and centered stock noise with standard deviation0.0003.
Costs span0.0001..0.0005. These deliberately strong artificial signals verify
wiring; their profitability is not market evidence.

Run complete original-scorer F2+VTvol and F3+VTvol workflows. A direct weighted
least-squares oracle independently reconstructs the exact53-column F3 forecasts
at rows127,253,319,639. Require maximum forecast discrepancy<=1e-10. The oracle
forms normalized historical weights explicitly, independently of the online
moment recursion. It computes the market state from explicit weighted histories,
not the prototype's state helper. Require the last fitted conditional coefficient
vector's dot product with the fixture's true conditional vector to be positive,
and nonzero forecasts different from F2. Report truth correlation as a diagnostic,
not a market-selection or MSE gate.

For state reconstruction require maximum absolute discrepancy<=1e-12; the first
62 close states must be zero, state bounds[-1,1] hold, and the state varies in
the known-risk fixture. This binds state observations to each design date.

The same fixture with zero exogenous market has state exactly zero after floors
while retaining the nonzero constant characteristic signal. F3 must reduce to
F2 within1e-12 for forecasts and1e-8 for positions and economic columns. This
allows last-bit changes from different-sized LAPACK solves, with actual errors
reported. No changed-memory-layout intervention is combined with temporal tests.

For the conditional fixture, mutate returns and characteristics from row400
using a fixed seed; forecasts through400 must be exactly unchanged, while
decisions and earning rows strictly before400 must match within1e-8. A pure
prefix with401 input rows must likewise match protected outputs. Reuse the
same F3 wrapper on the altered history, prefix and a zero-return history, then
rerun the original history: forecasts and targets must match exactly, economic
columns within1e-12. Zero returns must give exact zero forecasts/positions/fees
and undefined Sharpe and beta.

Every complete workflow requires finite/solvent output, unchanged inputs,
actual stock-level drift/fee reconstruction<=1e-12, gross<=5, actual stock
bound<=0.10, certified base solves, correct scorer counts and opening/endpoint,
and the unchanged VTvol first active clock at63 earned observations. Independently
reconstruct its moments and multiplier from its own virtual targets, tolerance
1e-12. Require virtual targets to be unaffected by outer actual accounting.

## Actual-market mode, unexecuted until root release

The source-bound root release must authorize actual execution. Reproduce
F2+VTvol against the saved original joint daily ledger within1e-8. Score exactly
one F3+VTvol policy, then verify its same-layout future mutation at1500 and pure
prefix1501. Preserve forecasts, targets, virtual targets and original scorer
rows in atomic `.npy` files, reload them and verify their complete identities.
The root independent reviewer reconstructs the actual economics from these.
Selection compares original full net Sharpe, with the fixed beta/solvency/runtime
conditions. Fixed stage masks and paired uncertainty are reported separately.

## Optional long-history runtime mode, unexecuted unless selected

The prospective harness includes a25,200-row mode, using the same1000-stock
actual input history repeated to that length. This mode requires a separate
source-bound root `allow_runtime` release. It is solely a runtime/state-stability
stress, never evidence of new alpha. Run on one CPU with BLAS threads1. Keep
data in read-only memory-mapped arrays when constructing the longer panel.
Require finite/solvent output, mean observed rebalance<100ms and measured
forecast<3600s. Record the complete stress command, source/input identities,
CPU affinity, timings and status accurately. This instrumented prototype stress
does not itself certify Claude's subsequently integrated production package.

## Artifact and source order

Record this specification, executable harness, immutable reference-source
hashes and expected missing-prototype exit3 before implementing F3. Preserve
any failed expectation rather than relaxing it after observing the outcome.
Independent source review and synthetic acceptance precede root's actual release.
All array writes use a temporary file, flush/fsync, atomic rename and immediate
readback. Scorer timing column is excluded from economic-equality comparisons.
