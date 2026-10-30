# Latest-package actual-data replay — prospective amendment

28 October 2026, written before the replay harness or execution. Independent
engineering review established that the committed real-data package checks
predate the subsequent affine-target/beta-shrinkage extension. A current-source
replay is therefore a concrete remaining verification need.

Run only the three already-executed policies V2, B0 and B05 from frozen commit
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`, through the original scorer on original
float64 CSVs. Each policy gets a fresh process and exact unchanged source copies.
No parameter choice or predictive model changes. Default configuration comes
from the literal handoff wrapper; B0 overrides beta_shrinkage=true,target=0 and
B05 overrides beta_shrinkage=true,target=.05.

Record original scorer outputs and actual target diagnostics with observational
wrappers only. Return every original array unchanged. Capture pre-gross allocator
output, post-gross target, current raw beta, current causal corrected beta, net
and gross investment, certificate status and value gap. Observers must not
advance risk or eta state; eta can be read from the already-completed slope list.
Use existing actual forecast/rebalance calls, not another optimization.

Expected outcomes:

- Each completed continuous run has 3,526 earning rows253..3778 and 3,527 decisions.
- Scorer economic arrays match the corresponding committed ledger to absolute
  tolerance1e-8, with exact maximum differences disclosed. V2 must also match
  the previous independent original package ledger to this tolerance.
- Every observed solve is certified and outputs finite capped positions.
- Report maximum gross before/after scaling, scaling count and actual final
  target-beta error. In particular test whether gross scaling explains the B05
  realized-beta shortfall. Distinguish exact estimated-beta feasibility from
  realized regression beta calibration.
- Save all actual differences, certificates and failures. Do not claim a stale
  certificate covers the final scaled portfolio or an unexecuted runtime gate.

Save plan, harness, exact commands, source/input hashes, environment, full daily
ledger, compact per-decision observations and unrounded summary. Runtime is
instrumented and not a replacement for the separate century-length gate.
The engineering reviewer will inspect the observer source before the first run.
