# C04 discovery result: residual-factor risk

**Run:** `evidence/discovery_C04_001/`, executed with the lead's authorization and frozen C04 configuration. **Outcome:** exit0, `EXECUTED_PASS_SCOPE_ONLY`,20 workflow checks passed. No code/configuration changes were made during the run. Actual numeric inputs were restricted to the verified discovery cache `[0,2016)`; validation and audit remain unopened by this agent.

## Economic result

The unchanged official scorer emitted1,762 daily observations, return indices253–2014 inclusive, from1,763 continuous rebalance calls. The final emitted target earns input index2015 and is not realized by the scorer's endpoint convention. No restart was introduced at a reporting boundary.

| Metric | Observed discovery value |
|---|---:|
| Daily-net annualized Sharpe | 0.654213 |
| Gross-return Sharpe | 0.881974 |
| Arithmetic annual net mean | 2.3581% |
| Annual net volatility | 3.6045% |
| Annualized full actual fees | 0.8218% |
| Realized net market beta | 0.007565 |
| Mean gross exposure | 0.945421 |
| Maximum drawdown | 4.8558% |
| Worst daily net return | −1.2115% |

Fixed discovery-block net Sharpes were0.3157,0.9730,0.7523 and0.5425. Block1 contains251 scored observations; blocks2–4 contain504,504 and503. These are descriptive slices of the same continuous development replay, not independently selected models or holdout evidence.

The score is positive but modest. Whether this factor model improves the parent C02, or merits a finalist slot, requires the lead's complete four-candidate comparison. This result alone does not establish an incremental contribution or hidden-continuation quality.

## Controls, solver behavior and accounting

- Zero factor fallback across all1,763 calls;84 factor refreshes, with age0–20 days and rank10 throughout.
- Factor dual used3–6 Newton iterations, mean4.2768;4–7 inner diagonal solves, mean5.2768. Maximum recorded dual-gradient residual was6.97e-12.
- Maximum covariance marginal-variance identity error was2.17e-19. The largest per-call factor diagonal fraction ranged from0.3162 to0.4565, below the predeclared0.5 bound.
- Maximum absolute estimated-beta exposure was1.42e-13. The official realized net beta remained distinct from this numerical equality and was0.007565.
- Full-cost accounting and closing gross exposure reconciled exactly with the original scorer. All outputs were finite and tested gross/net paths remained solvent. Configured stock/gross bounds held to the declared tolerance.

The gross rescale is economically material: it bound on1,114/1,763 calls (**63.19%**), with minimum scale0.4978, mean pre-scale gross1.0630 and maximum2.0089. Mean daily absolute traded weight was0.06661. The policy therefore cannot be described as preserving the optimizer's exact no-trade bands on every close. This caveat was predicted before the experiment and is now observed.

## Measured runtime

The process was pinned to CPU3, with all numerical thread controls set to one. Other candidates ran concurrently on other assigned CPUs; measurements are wall times on a shared machine.

| Scope | Calls | Mean | p95 | Maximum |
|---|---:|---:|---:|---:|
| Complete candidate rebalance | 1,763 | 24.97ms | 39.78ms | 674.84ms |
| Factor refresh closes | 84 | 37.93ms | 60.31ms | 100.63ms |
| Other closes | 1,679 | 24.33ms | 36.60ms | 674.84ms |

The original scorer's instrumented mean, including the transparent trace adapter, was30.91ms. Candidate forecast took12.94s over2,016 rows. Its0.0449 hours-per-century figure is a linear extrapolation, not a completed century run. The average rebalance requirement passed on this run; the maximum call duration is reported rather than hidden. The slowest calls were not factor-refresh events and showed ordinary4–5 dual iterations; their exact scheduling cause was not established.

## Evidence and reproduction

`summary.json`, `daily.csv`, `target_diagnostics.csv`, frozen sources/configuration, input/source identities, logs, environment and artifact manifest are in the run directory. `launch_command.txt` preserves the requested outer `taskset -c 3` invocation; `rerun_on_cpu3.txt` preserves a fresh frozen rerun with the same affinity. The timing split is a postrun calculation from the saved trace, with its own `postrun_analysis_manifest.json`; it did not rerun or retune the strategy.

Remaining gates include configured C04 causality, later chronological evaluation if nominated, long-history/runtime and final clean-folder execution. No new experiment is proposed or executed by this report before the lead's comparison.
