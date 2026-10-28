# Preserved audit harness failure and correction

28 October 2026. V2 replay `run_v2_001` completed successfully with its original
saved harness. C09 replay `run_c09_001` failed before the forecast or trading
loop: the observer passed only two arguments to C09's forecast, whose original
signature also requires `trading_costs`. This is an audit-wrapper defect, not a
C09 strategy failure. Its clean source, environment, input identities, original
harness and traceback are retained. It produced no scored ledger.

The subsequent first invocation of `paired_readback.py` therefore also failed
because the C09 daily ledger did not exist. Its stderr is retained as
`paired_stderr_failed_001.log`. No bootstrap result was produced.

Before the C09 rerun, extend only the observer signature to receive the scorer's
declared `trading_costs`, and forward it to the unchanged C09 forecast. The V2
branch of the observer is unchanged. No policy, numerical method, or performance
criterion is modified. Use fresh output `run_c09_002` and new logs; preserve
`run_c09_001` and its original logs. The successful V2 replay is not repeated.

Amend the paired readback inputs to `run_c09_002/daily.csv` and
`run_v2_001/daily.csv`; all four planned resampling calculations and conventions
remain unchanged. This correction precedes the first successful calculation.

## Second comparator attempt

`run_c09_002` completed its forecast, then failed at the first rebalance: C09's
rebalance declares four arguments and does not take characteristics, unlike
V2's five-argument signature. The audit observer again forwarded a fixed
positional signature. No scored ledger was produced. The second paired
readback invocation consequently also failed on the missing ledger; its
stderr/stdout remain under their `_002` names.

The complete fix uses the original scorer's own `with_declared_arguments`
adapter for both delegated functions, forwarding named inputs just as the
scorer normally does. This handles each package's actual interface without
altering its numerical code. Third comparator attempt uses fresh directory
`run_c09_003`; the first two failures are retained. The paired readback now
consumes that successful directory if available, with no change in methodology.
