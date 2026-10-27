# Frozen C09 descriptive attribution — E2E expectations before implementation

27 October 2026. This specification and its executable controller precede
`tools/attribute_frozen_policy.py`. The root admission is
`research/FROZEN_ATTRIBUTION_PLAN_20261027.md`. No policy is executed or changed;
all inputs in this workflow are explicitly synthetic saved packets.

## Fixed tool contract

```
python tools/attribute_frozen_policy.py --project ROOT --packet PACKET \
  --mode synthetic --packet-manifest-sha256 SHA256 --out NEW_DIRECTORY
```

Real processing additionally requires `--mode real --allow-canonical` and the
root's separate release. The synthetic verifier never invokes real mode.
Synthetic mode rejects `--allow-canonical`. There are no numerical tuning knobs.

Each packet has canonical-format `inputs/returns.npy`, `targets.npy`, `daily.csv`,
byte-identical C09 `config.json`, `input_manifest.json`, `source_manifest.json`,
and `artifact_manifest.json`. The four original helper files are at
`source/candidate/{strategy.py,portfolio.py,strategy_factor.py,factor_portfolio.py}`.
The passed manifest hash authenticates the immutable inventory; hashes and sizes
of every consumed input/source must be checked before loading numeric content.
Synthetic input kind is `synthetic_frozen_attribution`. No characteristics,
forecasts, raw market CSV or market returns array is read by this verifier.

The implementation must copy and import the original helpers privately, configure
the original C09 risk controls and C04 factor settings, and never call a candidate
forecast or rebalance. It must record code/input/source identities, commands,
expectations, environment, logs, checks and failures in a fresh output directory.

### Output schema

`daily_attribution.csv` includes `return_index`, `target_index`,
`risk_history_stop_exclusive`, `factor_history_stop_exclusive`, `factor_age_days`,
`factor_rank`, `estimated_market_exposure`, `market_component`,
`residual_factor_component`, `remainder_component`, `full_cost`, `gross_return`,
`net_return`, `gross_reconciliation_error`, `net_reconciliation_error`, and
`opening_gross_reconciliation_error`. Extra explicitly descriptive columns are
allowed; no component Sharpe is reported.

`summary.json` uses status `EXECUTED_PASS_SCOPE_ONLY` or
`EXECUTED_FAIL_OR_INCOMPLETE`, `exit_code`, `numeric_content_read_started`,
`model_executions: 0` and `stages`. Stages are `discovery`, `validation`, `audit`,
with fixed `index_slice` masks `[253,2015)`, `[2016,3023)`, `[3024,3779)` and
`rows`. Each has `annual_arithmetic_mean` and `annual_volatility` dictionaries for
the three component names, `full_cost`, `gross_return`, `net_return`;
`gross_covariance_contribution` for the three components;
`estimated_market_exposure: {mean_abs,max_abs}`; `factor_rank: {min,max}`;
`max_risk_history_stop_exclusive`, `max_factor_history_stop_exclusive`,
`max_factor_age_days`, `max_abs_gross_reconciliation_error`, and
`max_abs_net_reconciliation_error`. Empty stage metrics are null, with rows zero
and masks preserved. Undefined zero-variance covariance contributions are null.

## Known-component fixture

Use 420 days and 16 stocks. Spatial directions are the columns of a deterministic
16-order Hadamard matrix: column zero is the market, columns 1–11 are residual
directions. Returns have one market cosine and eleven different residual cosine
frequencies, all with period 252. Residual amplitudes strictly decrease, with
the eleventh smaller than the first ten. Every trailing 252-day window contains
complete periods: temporal means vanish, distinct frequencies are orthogonal,
and every stock has the same residual variance. Thus the C04 correlation
estimator's rank-ten span is independently known to equal columns 1–10, even
after current-variance rescaling and factor shrinkage 0.5.

Saved opening targets vary deterministically by day and contain nonzero market,
leading-factor and eleventh-direction exposures. Their exact gross P&L is
calculated from these known components without importing the implementation or
risk helper. The targets array has `days−253` rows; scored return row t uses
`targets[t−253]`. Its next target after close t is `targets[t−252]`. Synthetic
full fees use that next target, actual return drift and fixed 2–8bp stock costs.
The saved ledger uses the original scorer's complete schema and endpoint.

The component expectations use the known Hadamard span, not the implementation's
SVD. The market beta is one for each stock. All three contributions must be
economically nonzero, the span rank must be ten, and wrong opening-target indexing
must produce a detectable discrepancy. Fixed numeric reconciliation tolerance:
`atol=1e-12, rtol=1e-10`. Protected repeated/prefix numerical rows must be exactly
equal; a failed comparison is preserved and never relaxed after seeing results.

## Complete workflows and failure modes

1. **Expected red:** invoke the not-yet-existing implementation in a fresh process
   against the generated baseline packet. Preserve its missing-file error. This
   is an expected implementation absence, not a passing attribution.
2. **Baseline:** execute the complete CLI and reconcile every component, original
   gross/net/fee row, row count, target index and exact refresh schedule. Day t
   uses history stop t; factor refreshes are at 253, 274, 295, … and age is 0–20.
   Recompute stage summaries independently from the output series. No component
   may be called alpha or an independently tradable strategy.
3. **Repeat:** rerun the identical saved packet in a fresh process and require
   exact equality of all daily numeric output fields.
4. **Altered future:** change returns from row 337, a refresh boundary, with a
   fixed random generator; keep the fixed target schedule. Rebuild only this new
   synthetic packet's own ledger/manifests. All attribution rows before 337 must
   equal baseline exactly. At row 337 also check components against the original
   known prior span and beta using the changed day's realized return. This tests
   the current-day information boundary, not just an unchanged prefix.
5. **Truncation:** truncate to 338 input days. The scored indices end at 336,
   and all their attribution rows must equal the full baseline exactly.
6. **Zero/degenerate risk:** all returns, targets and fees are exactly zero.
   Components and arithmetic summaries remain zero, factor rank is zero, and
   zero-variance covariance contributions remain null. Empty stage metrics are
   also null. No epsilon substitution creates a spurious defined ratio.
7. **Wrong manifest digest:** a mismatched supplied manifest hash must fail
   before numeric content is loaded, with inspectable failure artifacts.
8. **Tampered input:** modify a return-file byte without updating its original
   packet inventory. The hash check must reject it before numeric loading.
9. **Malformed indices:** duplicate a saved ledger index in a separately declared
   synthetic packet with a matching inventory. Structural validation must fail.
10. **Wrong gross accounting:** alter one gross return and its net consistently
    in a separately declared synthetic packet with a matching inventory. Opening
    target × realized-return reconciliation must still fail.

The last four workflows deliberately corrupt new synthetic packets; they never
rewrite an actual research manifest. Expected rejection is distinct from an
unrelated failure: the two identity cases require
`numeric_content_read_started: false`. Later structural/accounting rejection
must have a recorded error and no successful status.

## Controller evidence

The controller `tools/verify_frozen_attribution.py --project ROOT --out NEW_DIR`
creates the fixtures, launches fresh subprocesses, verifies outputs and writes
all fixtures, commands, input identities, stdout/stderr, expectations, source
snapshots, checks, status and a rerun command. `--expect-missing` is used once for
the preserved preimplementation red record. The root separately releases any
actual packet only after the synthetic workflow and source review pass.

The selected four-file handoff is hashed before and after the workflow and must
remain byte-identical. No synthetic result is actual-market alpha evidence.
