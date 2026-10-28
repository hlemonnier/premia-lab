# One conditionally admitted joint candidate: F2 plus VTvol

28 October 2026, Europe/Paris. Owner: score_allocation_research. The parent's
master score plan was committed as251bee83d182e8796b7e2a35354fd1475b7dc242 before
economic runs. It admits one joint candidate only if the independently specified
forecast and allocation families both improve the official net-Sharpe score.
F2 scored1.2917800643 and VTvol1.2771094977, against V2=1.2425030733. This selects
the combination by the recorded conditional rule, not a new post-result grid.
F2's final causal disposition is required before joint actual-data execution.

## Exact composition

Copy unchanged V2 source/scorer atce3fe4e and unchanged research source files:
`v2_score_forecast_20261028/prototype.py` and
`v2_score_overlay_20261028/overlay.py`. Set
`engine.forecast=prototype.make_forecast(engine,'F2')`, then use the existing
`VolatilityOverlay(engine,config,power=.5)`. Every base configuration remains
the exact current V2 setting. The base virtual book is now F2, not V2: its own
actual virtual gross returns drive EW63 and EW1008 second moments. The63-earned
observation startup, floor1e-12, multiplier clip[.5,2], daily refresh, raw-beta
hedge and final gross5 limit are unchanged. No alternative forecast mix, power,
window, cost horizon, beta target or clip is admitted.

## Prospective E2E workflow before composition implementation

Write a joint E2E harness by reusing the existing overlay complete-scorer
harness and its assertions/tolerances. Before joint.py exists, the harness must
fail on the missing joint import and retain that red result. Then implement the
minimal composition factory. Independent review precedes successful execution.

The only harness adaptations, made before implementation, are: load the copied
F2 forecast into the engine for the direct reference; construct wrappers through
the new composition factory; run one dynamic joint power.5 instead of both
original powers; preserve the additional source copies and their identities.
Use the same deterministic420-day,64-stock fixture and scorer start252.

Require fixed-one control forecasts/targets to match directly scored F2 exactly,
economics within1e-12; joint virtual targets and forecasts exactly equal fixed
F2; independent actual drift/full-fee reconstruction within1e-12; startup at
earned63/close315; finite targets, gross cap and certificates; future alteration
from row360 leaves forecasts<=360 and decisions<360 unchanged; prefix361
matches the full run; reuse after different histories exactly reproduces the
first result. All original assertions and numeric tolerances are retained.
Save every case's ledgers, decisions, forecast/target arrays and source hashes.
This uses a C-contiguous perturbation to isolate future dependence. It does not
erase or relabel the forecast pilot's recorded mixed-layout strict failures.

## Actual execution and selection

After joint synthetic success and root's F2 actual-causality disposition, run
fixed-one F2 control and exactly one F2+VTvol joint policy with the original
CSV inputs and scorer. Compare fixed F2 against the independently scored F2
ledger, to absolute1e-8 on day/net/gross/fee/market. Preserve same forecasts and
virtual targets across fixed and joint policies. No full-sample risk scaling
or saved-future target lookup enters live decisions.

Use earning rows253..3778 and original stage masks [253,2015),[2016,3023),
[3024,3779). Report full/stage economics, fee increment, gross, realized beta,
multiplier/clipping, source identity and observed runtime. Compute paired
21/63/126-day moving-block intervals with2000 draws and seed20261027 against
original V2, F2 alone and VTvol alone, with the final legal block start included.

The joint is a leading replacement contender only if it beats both selected
individual candidates by more than1e-8, abs(realized net beta)<.2, no ruin or
nonfinite state, causal checks and source bindings hold, and observed mean
rebalance time<100ms on one core. Full net Sharpe is the economic selection
criterion; block intervals and stages describe uncertainty rather than imposing
an unannounced95% significance gate. All historical periods remain development.
If the joint does not win, retain the best eligible individual candidate. No
further combination, parameter rescue or production integration is admitted.

The observer retains traces for audit and is research code. Long-history runtime
and final small production packaging remain separate admission tasks; no claim
about them follows from a short synthetic workflow or an extrapolation.
