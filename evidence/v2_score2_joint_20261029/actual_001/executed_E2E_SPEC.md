# Prospective joint workflow specification

This file and e2e.py are written before joint.py. Exact equality means equal
float64 values (and identical rolling bytes where hashes are compared), excluding
measured execution seconds. All row indices are zero based.

## Constants and declared numerical tolerances

- Original scorer and ce3 engine source identities: common.SOURCE_HASHES.
- Synthetic seed/data: unchanged common.fixture(), T=420, N=64, 13 features,
  seed 20261028, nonnegative unequal costs .0001..0005.
- Altered future: from row 360 on synthetic and 1500 on actual;
  R becomes -.6*R+.0007 and X is reversed across stocks then shifted by .2.
- Protected forecasts: through boundary row, inclusive. Protected decisions:
  strictly before boundary. Protected earning rows: strictly before boundary.
- Temporal, M0 and inner-path forecast/target/economic equivalence: exact.
- Accounting, held-book identity, target formula, return decomposition,
  independently reconstructed virtual returns/moments/multipliers: 1e-12.
- Gross cap: 5+1e-10. Per-stock bound: .10+sleeve/N+1e-10.
- Inner raw-beta exposure: <=1e-9. Candidate realized whole-period beta: <.2
  in absolute value. Both inner and virtual solve certificates must be ok or
  ok_after_recovery, and risk-state absorption must end at decision_index+1.
- F2 warm-up forecasts rows 0..126 are zero. VT multiplier is exactly 1 for
  fewer than 63 earned virtual returns. Gamma=200/a and inner cap=.05*a.
- Actual source/array identities and prior standalone outputs: exact hashes
  and array values. Old CSV economics can be checked within 1e-8 only if used;
  the main reference is the prior atomic NPY and therefore requires exact values.

## Synthetic complete workflows

Run standalone E2, M0, joint, altered future, prefix, zero returns, restart,
and the joint with runtime observation trimming. Compare F2 virtual targets,
returns, EW moments, multipliers and forecasts as well as inner E2 targets.
Reconstruct original scorer gross P&L, actual drift, stock costs and target gross.
First decision 252 is free; final decision T-2 is charged and never earns T-1.
Scorer rows count T-254 and decisions count T-253.

The trimmed run must produce identical full-path decision-book hashes and
forecast/economic rows to full recording. Keep only last trace records after
hashing each completed decision, stripping trace-array fields. Never touch
the actual policy state arrays or learned state. On restart reset observer
hashes, independent prior targets, moments and counters too.

Known-inner fixture: T=8, N=3, start=0, costs [.001,.002,.003]. Returns are
[[0,0,0],[-.01,.03,.005],[.02,-.01,.01],[-.03,.01,.02],[.01,.01,.01],
[-.02,0,.01],[.005,-.007,.012],[0,0,0]]. Target sequence is
[[.3,-.2,.1],[.3,-.2,.1],[-.3,.2,-.1],[0,0,0],[.1,.1,-.1]], cyclically.
Require actual reversals and strict reduction of first charged fee relative
to separately summed component turnover, using a common actual denominator.
For forced outer cap use constant inner target [4.99/3]*3; require every outer
scale<1, gross<=5, and unchanged known inner targets. These fixture targets are
not an E2 forecast and are exempt only from E2 stock/beta/certificate checks.

Additional inherited E2 stress: common.fixture(n=128), forecast multiplied by
100 by the same predeclared harness injection as the execution owner's stress.
Compare standalone E2 and wrapped M1 inner/virtual paths exactly. Require inner
gross to reach 5 within 1e-8. Report outer binding count without requiring this
random-sign stress to exercise a branch already forced by the known fixture.

## Actual workflow and admission

Run standalone E2, M0, joint, joint altered future, joint prefix and joint restart.
Match saved standalone E2 atomic forecasts, targets, virtual targets and four
economic columns exactly. No additional forecast, sleeve or allocation variant.
The unchanged root selection rule compares joint net Sharpe with 1.426560898191992
plus 1e-8 after operational checks. All stage labels are development diagnostics.
Root's paired block intervals and stock-level independent readback use saved
arrays and do not execute an alternative policy.

## Runtime workflow

Separate allow_runtime release is mandatory. Tile original returns and features
cyclically to (25200,1000) and (25200,1000,13), retaining supplied stock costs.
Run only the selected joint under the original scorer, with trace trimming.
Record no Sharpe or claimed new economic evidence. Forecast <3600s and mean
rebalance <100ms on one CPU and one BLAS/OpenMP thread; other physical/certificate
checks continue over the entire path. Persist rolling target hashes, full rows
and forecasts, final targets and scalar decision records. Do not extrapolate a
small-input timing pass into this gate.
