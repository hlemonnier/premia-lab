# Sole conditional composition: F2 -> E2 -> fixed market sleeve

29 October 2026, Europe/Paris. Prospective plan before joint factory or outcome.

## Authority, admission and exact policy

The root master plan was committed before standalone outcomes at
`d2997e0d98c6407da4b503a77060966904486062`. It permits exactly one composition
of separately qualifying families. E2 scored 1.3395817822087963, above E1 and
the F2 + VTvol baseline 1.318334966090838. M1 scored 1.426560898191992.
F3 scored 1.2943927925112546 and is excluded. Thus the admitted composition is
the unchanged F2 forecast, unchanged E2 execution, and unchanged outer M1.
All historical periods are exposed development data. This adaptive composition
is counted as the fifth and final new economic policy in this wave.

The factory is only composition of existing objects: construct E2 using the
execution owner's unchanged common.wrapper(..., "E2", make_execution), then
wrap it in the independent reviewer's unchanged MarketSleeve with sleeve=.05.
The only control value is sleeve=0. No source or parameter change to either
policy, the F2 learner, VTvol, risk model, allocator or original scorer is allowed.
The five dependencies are copied byte-identically and bound by a manifest.

There are three independent books. The innermost F2 virtual portfolio owns its
own drift, risk state and EW63/EW1008 gross-return moments. E2 owns a separate
actual allocator and its independent drifted holdings. The outer actual book
adds .05/N to each E2 target, then proportionally reduces aggregate gross only
if it exceeds 5. The outer scorer charges trades against its actual holdings;
outer holdings never become the E2 inner holdings. MarketSleeve computes E2's
own drift denominator before calling E2. The actual stock bound is .10+.05/N.
The market sleeve is costed stock exposure, not a separate free index instrument.

The composition retains raw-beta target zero inside E2, actual risk aversion
200/a, stock cap .05*a, cost horizon 20, gross cap 5, original F2 forecast,
H126 risk and chosen factor penalty .3. All state resets on a new forecast
session, and all return/design clocks are those of the already reviewed sources.

## Economic decision

Use the unchanged original scorer on zero-based earning rows 253..3778,
3,526 economic observations and 3,527 decisions. Full net Sharpe is
sqrt(252)*mean(gross return - full actual cost)/std(..., ddof=0).
Only promote the composition if it passes operational checks and beats the
best admitted standalone M1, 1.426560898191992, by more than 1e-8. Otherwise
retain M1. There is no subset search, sleeve-weight search or parameter rescue.
The original stage masks remain diagnostics, and fixed paired moving-block
intervals remain descriptive rather than a new significance gate.

Actual execution requires a root release binding all local source/specification
hashes, the passing synthetic outcome and the qualifying E2/M1 evidence.
Root's independent stock-level readback remains separate from this harness.
No actual joint path has been run at this checkpoint.

## Prospective verification and failure modes

E2E_SPEC.md and executable e2e.py precede joint.py. Preserve a missing-factory
red run with zero economic executions before creating the factory. Then run
the following complete original-scorer synthetic workflows:

1. Reproduce the prior saved E2 synthetic targets, F2 virtual targets, forecast
   and four economic columns exactly on common.fixture's fixed seed/data.
2. M0 around E2 must recover standalone E2 forecasts, targets, virtual targets,
   virtual returns, VT moments and economics exactly.
3. The joint M1 book's inner E2 targets, F2 virtual targets/returns, forecast,
   VT moments and multipliers must be identical to standalone E2. Independent
   reconstruction checks both inner and outer drift, fees and timing.
4. Future alteration from row 360, pure prefix through row 360 and cross-history
   restarts must preserve the specified forecast/target/economic prefixes exactly.
   Zero returns are an intervening history: E2 stays cash while the sleeve holds
   its fixed market basket, with no gross P&L or rebalancing costs in zero returns.
5. Deterministic known-inner reversals verify actual stock-level cost netting,
   the free opening and charged endpoint. A known all-long inner gross 4.99 plus
   .05 sleeve forces outer gross reduction while leaving inner targets unchanged.
   The inherited E2 forecast-times-100 synthetic stress separately exercises a
   capped E2 inner book, and its standalone inner path must remain identical.
6. A prospective observation adapter trims diagnostic records only AFTER each
   complete outer rebalance in runtime mode. On the ordinary synthetic joint
   path, its rolling hashes of every actual, E2 inner and F2 virtual target must
   match full recording exactly, as must forecasts and four economic columns.
   Trimming may never change previous_actual, inner_target, virtual_target,
   risk state, moments or warm starts. It only removes completed trace copies.

Failure modes include feeding outer drift into E2, shared actual/virtual risk
state, updating VT moments with the combined return, charging sum-of-book fees
instead of net stock trades, missing last costs, retaining state on restart,
or changing behavior when trace recording is reduced. The checks directly
target these mechanisms; no retrospective target or threshold changes are allowed.

## Actual and runtime workflows

Actual mode reproduces standalone E2 from original CSV inputs against its saved
NPY arrays; runs M0 and the joint; checks exact independent inner paths; and
runs altered-future, pure-prefix and repeat workflows. It records full stage
metrics, actual costs and realized beta. All arrays are atomic NPY with immediate
readback verification. Standard candidate outputs are targets.npy (3527,1000),
inner_targets.npy, virtual_targets.npy, rows.npy (3526,5), forecast.npy,
decision_indices.npy and virtual-return/controller traces, plus daily CSVs.

Only if the composition is selected and separately root-released, runtime mode
tiles original data to 25,200 rows and 1,000 stocks. It runs the full original
scorer with the prospective observational trimming adapter. Characteristic
history is a read-only memmap; source policies and state transitions are unchanged.
Retain full scorer rows, forecast, final book vectors, rolling SHA256 hashes of
all three decision books, per-decision scalar diagnostics and source/data hashes.
Require one CPU, one BLAS/OpenMP thread, forecasting below 3,600 seconds and mean
rebalance below 100 milliseconds. No alpha score is reported for tiled data.
The synthetic full/trimmed equality is a prerequisite for using this mode.

No production or previous F3 file is changed by this work.
