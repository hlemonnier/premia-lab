# C07 discovery result: solve the gross budget jointly

**Run:** `evidence/discovery_C07_001/`. The lead admitted C07 before scoring, after the new allocator's unchanged preimplementation verifier passed86 checks and another agent approved its source. The official discovery run completed with exit0 and20 passing workflow checks. Input rows were the bounded cache `[0,2016)`;1,762 return observations cover indices253–2014. No validation/audit data was accessed and no code/configuration was changed during this run.

## Result and interpretation

| Metric | C02 proportional gross scaling | C07 exact joint gross constraint |
|---|---:|---:|
| Net Sharpe | 0.637567 | 0.679825 |
| Gross Sharpe | 0.750111 | 0.746039 |
| Annual arithmetic net mean | 4.4038% | 5.1172% |
| Annual net volatility | 6.9072% | 7.5272% |
| Annual full actual fees | 0.7773% | 0.4979% |
| Net market beta | 0.021230 | 0.023539 |
| Maximum drawdown | 8.4883% | 8.6433% |

C07 improved fee efficiency and modestly improved development net Sharpe. Gross Sharpe was essentially unchanged. The saved C07 forecast artifact is byte-identical to C02 (`5984df185016962a3328ebea477690d055bb46072b7933d46637e25f88a84b45`), supporting the intended portfolio-only comparison. This result does not establish a stronger forecast or hidden-continuation improvement, and C06's already-observed net Sharpe remains higher.

The fixed-block C07 net Sharpes were1.2402,0.6161,0.5477 and0.4652. They are descriptive slices of one continuous replay; the first block has251 scored days, then504,504 and503.

## Exact constraint and numerical behavior

There were **zero proportional rescaling calls**. The joint gross budget bound on1,407/1,763 calls (79.81%). The maximum target gross exceeded1 only by4.44e-16 of floating-point error; maximum stock weight was0.01. Maximum absolute estimated-beta exposure was1.41e-13. Mean target gross was0.9742 and mean daily absolute traded weight was0.04163.

The exact-gross solver required at most6 outer iterations and28 scalar prox evaluations on any call. Mean counts across all calls were3.366 and14.938, including zero work on nonbinding-budget branches after the existing diagonal solution. There was no numerical failure or fallback. Original-scorer fees and gross positions reconciled exactly, inputs and frozen sources remained unchanged, and tested gross/net paths remained solvent.

## Runtime and evidence limits

The process was pinned to CPU0 with numerical threads set to one. Candidate rebalance mean was25.75ms, median11.67ms and p95 34.80ms. The retained maximum was10,845.68ms. The official instrumented mean, including the trace adapter, was49.06ms. Forecast took22.76s; the0.0790-hours-per-century figure is a prefix extrapolation only.

Other research tasks ran concurrently on the shared host. The long maximum is reported without assigning an unverified scheduling cause. `postrun_solver_summary.json` identifies the affected calls and their branch/iteration telemetry. The mean requirement passed on this environment; neither this run nor the isolated verifier establishes a hardware-independent latency guarantee or long-history behavior.

## Reproduction and remaining gates

The run retains frozen code/configuration, source and input hashes, complete daily ledger, every target's solver diagnostics, environment, logs, and exact rerun instructions. `launch_command.txt` and `rerun_on_cpu0.txt` preserve the outer CPU affinity. A separate postrun manifest identifies the descriptive trace summary and forecast-identity comparison; no extra strategy execution was needed.

New solver evidence remains in `gross_build_order_001`, `gross_oracles_001`, `gross_red_001`, `gross_verify_001`, and the independent review in `reviews/gross_independent_review.md`. Configured C07 causality and any later finalist/holdout/runtime-release gates remain separate and are not claimed passed by this discovery result.
