# Phase 0 preflight: expectations recorded before execution

Scope: validate source identity, input structure, local environment, and the supplied scorer's complete load/replay/report path on the first 504 rows. This is not an alpha experiment and not validation of a new candidate strategy.

## Input expectations and failure modes

| Check | Failure mode | Expected outcome |
|---|---|---|
| Source inventory | Truncation, archive mismatch, changed originals | All 12 ZIP members extracted; SHA-256 and byte sizes recorded; original scorer untouched |
| Remote provenance | Attachment is a different brief/version | Eight root file names/sizes agree with Drive; fetched README text agrees allowing final newline; CSV byte agreement with Drive is NOT claimed |
| Returns | Wrong dimensions, duplicate/reordered days/stocks, invalid numbers | 3,780 rows, 1,000 unique stock columns, CSV day labels 1..3780, all finite numeric returns |
| Characteristics | Reshape silently attaches values to wrong stocks/days | 3,780,000 rows, 13 expected features; exact day-major then stock-major order matches returns and costs; all finite values |
| Costs | Missing, negative, nonfinite, misordered identifiers | 1,000 rows, same stock order as returns, finite nonnegative one-way costs |
| Scorer smoke | Broken loading, import, timing, or output path | Supplied load/run/report completes using first 504 rows; 250 scored rows, finite non-timing outputs, nonnegative trading costs, positive net-return dispersion |
| Equal-weight interpretation | Mistaking a smoke test for an admissible strategy | Gross exposure 1; beta expected near 1 (tolerance 0.02) and thus intentional failure of assignment beta condition |
| Repeatability | Process state affects supplied example | Two in-process repetitions of the supplied example have identical economic rows; timings can differ |
| Runtime provenance | Multithreading creates misleading timings | BLAS/OpenMP thread limits set to one before imports; one CPU affinity requested and recorded if supported; timing is descriptive for this example only |
| Dependency availability | Claiming all promised evaluator packages exist locally | Record actual Python/package versions. Missing optional cvxpy/lightgbm is a limitation, not a pass |

## Data access restriction

Full files may be streamed for hashes, schema, exact keys, and finiteness. Do not compute or expose return moments, correlations, signal associations, or characteristic distributions outside the smoke prefix. Do not open the supplied full-sample figures. Do not train any predictive model.

## Evidence obligations

The runner will preserve this plan, exact command, input/source hashes, environment and CPU/thread details, structural audit results, all supplied-scorer output rows for the smoke prefix, printed report, and a JSON summary with per-check status. Exceptions must be recorded with traceback and nonzero exit status. A second reviewer will inspect the source and artifacts; that review is not claimed until received.

## Boundary conventions

For T=504 and START=252, the supplied scorer first trades after array row252 (CSV day253), then returns score rows253..502 (CSV days254..503): 250 rows. Array row503 is not earned by the scorer. The close502 rebalance cost is included. Preserve these semantics and do not optimize around the endpoint.

## Status

This document precedes the runner and its first execution. Candidate causality, portfolio safety, long-horizon scaling, hidden-future performance, and the complete evaluator environment are unverified.
