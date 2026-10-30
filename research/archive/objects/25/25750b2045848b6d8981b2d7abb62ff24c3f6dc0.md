# Independent result verification: score improves to1.318335

28 October 2026, Europe/Paris. Reviewer: score_opportunity_audit.

**The independently reconstructed leading prototype is F2+VTvol, net Sharpe
1.318334966090838 versus V2's1.242503073307361: a gain of0.075831892783477.**
The scorer, actual stock-level drift, all paid fees and final endpoint reconcile.
This is a development-score improvement; the supplied history is already exposed.

## Recomputed results

| Policy | Official net Sharpe | Difference vs V2 | Annual net mean | Annual net vol | Annual fees | Net market beta |
|---|---:|---:|---:|---:|---:|---:|
| V2 |1.242503 |— |4.755036% |3.826982% |0.175566% |0.046496 |
| F1: daily-slope average |1.137993 |−0.104510 |4.133165% |3.631977% |0.145117% |0.031584 |
| F2: partial fast/slow forecast |1.291780 |+0.049277 |5.126510% |3.968562% |0.207145% |0.049046 |
| VTvol |1.277109 |+0.034606 |5.495275% |4.302900% |0.307982% |0.052090 |
| VTvar |1.274191 |+0.031688 |6.283879% |4.931663% |0.436717% |0.057363 |
| **F2+VTvol** |**1.318335** |**+0.075832** |**5.786507%** |**4.389254%** |**0.336406%** |**0.052720** |

All reported scalar performance metrics reconcile to at most6.94e-18 in their
reported units. V2 and the fixed-one overlay control reproduce identical daily
economics. The joint beats F2 alone by0.026554901757001 and VTvol alone by
0.041225468417561, exceeding the prospective1e-8 numerical tie guard.

| Policy | Discovery | Validation | Audit |
|---|---:|---:|---:|
| V2 |1.098002 |1.656859 |1.147558 |
| F1 |0.999519 |1.481003 |1.224562 |
| F2 |1.117706 |1.528936 |1.498744 |
| VTvol |1.087012 |1.757166 |1.298085 |
| VTvar |1.064625 |1.806735 |1.346022 |
| F2+VTvol |1.103512 |1.633970 |1.593029 |

The larger final-period gain accompanies roughly flat first-period and slightly
lower middle-period performance. These old stage labels are diagnostics; they
are not fresh independent confirmation. No new every-stage-win condition was
imposed after these outcomes.

## Independent full-cost accounting

The readback loads the original stock returns and per-stock costs, with hashes
matching the previously verified originals. It reconstructs every return,
drifted holding, paid trade and closing gross exposure from actual targets,
including the single free opening at row252 and the fee on the final target at
row3778 whose next return is never scored.

The maximum difference from the saved scorer economics is2.26e-17. Forecast
baseline/F2 target arrays are matched to their original raw-array hashes. For
each overlay, the virtual targets match the standalone V2 target hash exactly;
the joint instead matches standalone **F2**. Multipliers and final gross scaling
reconstruct the actual target arrays, whose raw hashes also match the recorded
original actual-target hashes exactly. This establishes the stock-level cost
reconstruction; no separately charged virtual-leg fee is substituted for actual
fees. The independently reconstructed moments and multipliers have error0.

All relevant source copies match the pinned production identities, and joint
forecast/overlay dependencies match their reviewed standalone source copies.
The winning book's maximum gross exposure is3.159930, maximum individual weight
0.016441, and worst gross daily return approximately−1.7498%. Its measured
instrumented rebalance mean is3.402ms. Each reported base run has3,527 `ok`
certificates; the complete stock-level readback applies to V2, F2, the fixed-one
control, both overlays and the joint, with the F1 limitation below.

Fees and full-sample volatility increase in the winner. The gain is a higher
net return-to-risk ratio from different forecasts and time-varying exposure,
not a claim of lower unconditional risk or lower costs. The new net score also
exceeds V2's unchanged-holdings gross Sharpe of1.289755, so fee deletion alone
could not reproduce this gain on V2's original holdings path.

## Paired uncertainty independently recomputed

The readback independently generates2,000 paired moving-block samples per fixed
length21,63,126, seed20261027, including the final legal block start. It verifies
the overlay owners' reported intervals. All five candidates are included.

| Candidate minus V2 | Difference | 63-day block95% interval |
|---|---:|---:|
| F1 |−0.104510 |[−0.202024,−0.021901] |
| F2 |+0.049277 |[−0.072513,+0.157362] |
| VTvol |+0.034606 |[−0.059673,+0.128229] |
| VTvar |+0.031688 |[−0.134782,+0.185188] |
| F2+VTvol |+0.075832 |[−0.081966,+0.217923] |

Lengths21 and126 are retained in the complete result JSON. These intervals do
not adjust for the entire model-development history or establish hidden-future
superiority. They do not replace the score-based selection rule with an extra
significance requirement.

## Failures and evidence boundaries retained

The forecast workflow's original strict mixed-layout allocation comparisons
failed, despite identical protected forecasts. The original F1 constant-Gram
downstream allocation comparison also failed its very tight expectation. Those
records remain failed; there is no blanket `all passed` claim. The canonical
same-C F2 actual future alteration at cut1500 later reproduces protected
forecasts, targets and economics with maximum difference0. Its original-source
repair verification is included in this readback JSON.

The first F2 canonical comparison encountered a truncated original baseline NPZ.
Root authorized one unchanged-source replay and separate atomic NPY evidence.
The repaired forecast and target raw hashes equal the original recorded hashes
exactly, and its economics equal the original CSV within4.44e-16. Independent
accounting here uses those verified repaired arrays. No parameter, tolerance,
economic result or original damaged file was replaced.

F1's original target NPZ is also truncated. Its CSV score, stage performance,
reported fees, market series, scalar decision constraints and certificate
records reconcile independently. **Its independent stock-level target/fee
reconstruction remains blocked**, and is not reported as passed. The rejected
policy was not rerun merely to fill that evidence gap. This limitation does not
apply to the nominated joint or either of its selected components.

A full-century run is not supplied by this readback. Actual measured runtime
and source review are separate from a completed long-history admission gate.
No production integration, employer submission or new experiment occurs here.

## Reproducibility and source review

Root reviewed the pre-execution accounting, moment-clock, CSV-round-trip and
bootstrap method. The forecast owner then independently reviewed the narrow
NPY repair loader and explicit F1 ledger-only limitation. The accepted reader
SHA256 is`df4ac78a168fc4116d28871be35b61c624d09fdba4e768464e35a473287dfff7`.

Exact command, executed from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python evidence/v2_score_opportunity_20261028/actual_readback.py --out evidence/v2_score_opportunity_20261028/actual_readback_001.json --f1-ledger-only --f2-arrays evidence/v2_score_forecast_20261028/baseline_repair_001/verified_arrays --joint-folder evidence/v2_score_joint_20261028/actual_001/joint_F2_VTvol > evidence/v2_score_opportunity_20261028/actual_readback_001.stdout.log 2> evidence/v2_score_opportunity_20261028/actual_readback_001.stderr.log
```

Exit code0. The output JSON records62 input identities, the original forecast
failure status, F2 repair/canonical verification, source identities, complete
metric differences and all intervals. Standard output/error and the prospective
plan remain alongside it. This reader ran no strategy.
