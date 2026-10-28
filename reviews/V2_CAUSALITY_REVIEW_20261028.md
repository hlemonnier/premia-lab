# V2 independent causality, state and reproducibility review

**28 October 2026, Europe/Paris.** Reviewed commit: `afed8d0cb017acda151c4ea262fc30db7568a4bb`, branch `v2-factor-risk`. The inspected source was fetched by the coordinator and Git-blob verified. This review owns the information-boundary and public-workflow analysis; allocator optimality and actual-market replay are separate reviews. No strategy source or configuration was changed.

## Verdict

**The packaged strategy is causal in the fresh, monotonically advancing scorer workflow examined here.** Its beta feature, fitted-label timing and incremental risk update have the correct information boundaries. An independent synthetic end-to-end replay preserved the protected forecast, target and economic prefixes exactly under ordinary future replacement and truncation. This is positive implementation evidence, not a claim that the V2 selection is free of overfit.

Two engineering issues need correction:

1. **Risk-state identity is inferred solely from history length.** A new history starting at the same or later length can inherit another run's factor and specific-risk state. An end-to-end scorer restart reproduces a material discrepancy. The ordinary repeated full replay from the default starting day resets correctly and is a passing control; the published fresh-process backtest is not invalidated by this particular finding.
2. **Characteristic memory layout is not canonicalized.** The committed layout check changes only returns. Passing characteristics in Fortran layout changes protected forecasts at rounding scale and can amplify into larger, still economically tiny, target discrepancies. The claim that all arrays are made C-contiguous is false for this implementation. This is numerical reproducibility, not economic lookahead.

The committed verification trail also falls short of the brief's breadth: the visible causality script exercises the research forecast factory, not the packaged implementation, and reports `FAIL` without returning a failure exit code. Several reported runs have no committed invocation, raw ledger or input/source identity packet. These gaps do not prove the reported runs were not performed; they prevent independent confirmation of the exact claims from that branch alone.

## 1. Information timing is correct in the ordinary workflow

Source references below use the pinned commit. Line numbers refer to the inspected snapshot.

### Forecast beta feature and labels

In [engine.py](https://github.com/hlemonnier/continual-research-takehome/blob/afed8d0cb017acda151c4ea262fc30db7568a4bb/handoff_v2/model_v2/engine.py), `causal_betas`, lines 56–70, constructs `beta[t]` exclusively from returns with indices less than `t`. The cumulative sums are indexed at `t` and the lower historical boundary; later rows are not subtracted into an earlier estimate.

For training pair `s`, `design(s)` uses `X[s]` and `beta[s+1]` (lines 98–99). That beta uses returns through row `s`, which are available when `X[s]` is published. The response is the return of day `s+1`, residualized by its pre-day beta. At forecast row `t`, the newest incorporated pair is `s=t-2`, so its label is `R[t-1]`, already published. Prediction uses `X[t-1]` and `beta[t]`, also known then (lines 106–114). There is no off-by-one lookahead in this beta column.

The implementation precomputes beta and residual arrays for the whole supplied history, but the loop consumes only eligible entries. Merely allocating or computing an array of future values does not make the earlier forecast future-dependent. The relevant criterion is whether an unavailable value reaches the forecast, and the inspected indexing does not do that.

### Risk state and portfolio

The supplied scorer passes the close-of-day history `R[:today+1]`, `X[:today+1]` and forecast row `today+1` into rebalance. With history length `T`, `_RiskState.absorb` consumes return row `s` against characteristic row `s-1`, and estimates label beta from `R[:s]` (engine lines 127–137). The loop stops after consuming `s=T-1`, today's published return. The next-day loading matrix uses `X[T-1]`, and the hedge beta includes returns through today (lines 160–168). These are legitimate next-day decision inputs.

The persistent state holds risk estimates and solver warm-start values, not future-trained forecast coefficients. A fresh process starts with no risk state because the packaged wrapper invokes `configure`. The state then advances one published day at a time. The same basis for mean and risk does not itself create information leakage; its statistical suitability is a separate question.

The scorer, position drift and fee conventions were preserved byte-for-byte. The audit compares targets at close-of-day indices and ledger observations at earning-day indices separately. In particular, changing data from row 300 protects forecast row 300, decisions through close 299, and ledger economics through day 299. A decision made after observing changed row 300 is allowed to change.

## 2. Confirmed state-identity defect

**Location:** `handoff_v2/model_v2/engine.py`, lines 149–163; `forecast`, lines 84–115; wrapper configuration at lines 72–74.

The only automatic reset condition is:

```python
if _STATE is None or _STATE.upto > T:
    _STATE = _RiskState(n, 26, cfg)
```

There is no run identity, input-history identity or stock-dimension check. `forecast` does not reset the risk state. The handoff wrapper calls `_engine.configure(_CONFIG)` only at import, then assigns direct aliases `forecast = _engine.forecast` and `rebalance = _engine.rebalance`; these functions share the module's global `_STATE`. Reusing the imported strategy does not rerun the wrapper's configuration step or construct a new session. Therefore, after a session has processed 300 rows, a different session whose first rebalance also receives 300 rows skips initialization and all historical absorption. It combines the previous session's historical `F` and `d` with the new session's current characteristics, hedge beta and forecast. Appending more rows does not remove the stale history immediately; it only exponentially decays it.

### Complete-workflow reproduction

The independent E2E first scores synthetic history A through risk-state history length 300. In the same process it then calls the unmodified scorer on independent synthetic history B with `start=299`, so the first rebalance also receives 300 rows. It compares the entire B run against a fresh-process B run with identical arguments.

| Comparison | Maximum absolute discrepancy |
|---|---:|
| Full B forecast array | 0, bitwise equal |
| Target stock weight | 0.0283145382, about 2.83 percentage points |
| Daily gross portfolio return | 0.0009873237, about 9.87 bp |
| Daily fee fraction | 0.0000402337, about 0.402 bp |
| Gross exposure | 0.1664145286 |

The contaminated run begins with `_STATE.upto=300`; the fresh run begins with no state. The changed outputs are not explained by different forecasts, inputs or scorer arithmetic.

A control runs complete A and B histories consecutively at the standard `start=252`. There the old state length 339 exceeds the new first-call length 253, triggering the existing reset. Forecasts, targets and economic ledgers match the independent fresh B run **bitwise**. Thus this is a reproducible restart/reentrancy bug, not proof of future contamination in Claude's ordinary full-history performance run.

### Repair to ask Claude for

Introduce an explicit run-lifecycle reset. For this assignment's declared workflow, resetting the risk and warm-start state at the beginning of `forecast` is a small direct repair: the scorer calls forecast once before each run. An explicit strategy/session object is cleaner if multiple books or interleaved histories are intended. Also validate stock dimensions before cache reuse; silently accepting a different stock ordering cannot be solved by a dimension check alone.

Do not hash the complete growing history every day merely to support caching; that would add needless quadratic work over long histories. Decide and document the supported append-only/session contract. Validate the repair through the already defined full-workflow restart cases, including default-start behavior and the existing runtime requirement. This reviewer does not implement the repair.

## 3. Confirmed characteristic-layout gap

**Locations:** engine lines 84–99 and 152–165; [causality_check.py](https://github.com/hlemonnier/continual-research-takehome/blob/afed8d0cb017acda151c4ea262fc30db7568a4bb/research/v2/exploration/causality_check.py), lines 20–28.

Both forecast and rebalance make `R` C-contiguous. They retain `X` as supplied. `basis` uses `np.asarray(..., dtype=float64)`, which does not force C order when the dtype already matches. Consequently the cross-sectional reductions can follow different floating-point accumulation paths. The existing research check calls `np.asfortranarray(R2)` but leaves `X2` unchanged, so it cannot detect this issue.

The independent E2E changes the future from row 300 while separately putting the characteristics into Fortran layout. On the protected prefix:

| Object | Maximum absolute discrepancy |
|---|---:|
| Forecast | 1.72e-18 |
| Target weight | 4.68e-10 |
| Daily gross portfolio return | 3.00e-12 |
| Daily fee fraction | 5.76e-13 |
| Gross exposure | 6.41e-10 |

These differences are economically negligible. The forecast's protected differences start at row 127, the first row after the 126-pair training minimum. They show layout sensitivity, not access to future data. However, they fail the blanket bitwise-layout claim and the preset target comparison tolerance of `atol=1e-12, rtol=1e-10`.

Canonicalize each two-dimensional characteristic panel before cross-sectional reductions, rather than copying the entire 3D history on every rebalance call. This can make the result independent of the caller's memory layout at modest cost. Test both return and characteristic layouts on the actual packaged entry point. Preserve a sensible distinction between exact decision-prefix checks and scorer output roundoff: putting raw returns into Fortran layout alone left targets exactly equal, while the unmodified scorer's own dot products changed the gross-return ledger by at most 2.60e-18.

## 4. What the committed verification actually establishes

The branch contains 48 added files. Its visible engineering evidence includes the allocator specification/test source and a one-line century runtime summary. The following limitations are material to reproducing the brief:

- **Research versus packaged entry point.** `causality_check.py` gets its forecast from `V.VARIANTS[name]()` at line 15. The packaged engine is a separate implementation. Its direct-label calculation differs from the research cumulative-sum label calculation. Passing the factory check does not automatically verify that separate file or the whole rebalance pipeline.
- **Failure signaling.** The causality script prints `PASS` or `FAIL` at line 32, but has no failure exit. An automated gate based on exit status can accept a failed run.
- **Coverage is forecast-only.** The script does not capture positions, risk state, fees, turnover or scorer return prefixes. Its row-`cut` inclusion is correct for nontruncated inputs; truncation necessarily ends before that output row.
- **Research inputs have an undocumented precision dependency.** `common.py` caches characteristics as float32 and trusts an existing cache without identity validation. `variants.py` promotes to C-contiguous float64 only if the `X64` environment variable is set; promotion cannot undo prior float32 rounding. Raw scorer loading uses Pandas' ordinary float parsing. Therefore an exact clean-folder-versus-research claim needs input/cache hashes and actual dtype metadata, not just an explanation about cumulative sums.
- **Paths are not portable.** Exploration files refer to `/home/claude/explore`, `/home/claude/explore/out` and `/home/claude/continual-research-takehome`. Some data paths have environment overrides, while repository/output paths do not. A reviewer cannot run the advertised commands in an arbitrary checkout without adaptation.
- **Several artifacts are absent from the committed V2 tree.** `net_*.npy` ledgers needed by `compare.py`, `F26.npy` consumed by `drift_test.py`, the full clean-folder replay packet, original causality logs and a runnable century-workload construction/command are not in `research/v2/results`. The single century text line does not bind the result to inputs, source, configuration, BLAS thread count or environment. Root's new actual replay can establish fresh evidence but cannot retroactively verify the original missing run packet.
- **Reported timing is not independent evidence here.** This audit's small synthetic workload is deliberately not used to validate the thousand-stock/century runtime claims. The separate root replay owns any newly executed actual-data timing.

A small portable replay controller is a better next engineering deliverable than another pile of isolated assertions. It should select the packaged module, load hash-bound canonical inputs, invoke the unchanged scorer, save forecast/target/economic outputs, exercise future and restart variants, and exit nonzero on failed requirements. Preserve the research controller separately from the small handoff.

## 5. Independent E2E evidence retained

The [prospective audit plan](../evidence/v2_causality_review_20261028/PLAN.md) preceded the [audit harness](../evidence/v2_causality_review_20261028/run_e2e.py). No production implementation followed; this is a source review with independent complete-workflow diagnostics of the existing candidate, not postimplementation unit tests.

The first execution ran **10 fresh processes**, including 12 complete scorer executions because two restart cases execute two sessions. Every process completed with exit code zero. The controller records comparison failures in its results; a zero process exit is not presented as a blanket audit pass. The independent fixture is deterministic, with 340 days, 96 stocks and 13 persistent characteristics. It produces nonzero forecasts and positions. Its market-plus-characteristic construction is only an engineering stimulus; it is not an empirical result about the supplied simulator.

Meaningful outcomes:

| Workflow | Result |
|---|---|
| Fresh repeat | Exact forecasts, targets and economic ledger |
| Ordinary future alteration from row 300 | Exact protected prefixes; later forecasts and targets change |
| Truncation to 301 rows | Exact available forecast/target/ledger prefixes |
| Return-array Fortran layout | Exact protected forecast and targets; scorer gross-return roundoff at 2.60e-18 |
| Characteristic-array Fortran layout | Rounding-sensitive forecast and amplified, economically tiny target differences |
| Different history with equal-length restart | Material stale-state failure reproduced |
| Different history with normal default-start full restart | Exact fresh-run equivalence |

The complete [results](../evidence/v2_causality_review_20261028/run_001/results.json), [commands](../evidence/v2_causality_review_20261028/run_001/commands.json), [input/source identities](../evidence/v2_causality_review_20261028/run_001/input_source_manifest.json), [environment](../evidence/v2_causality_review_20261028/run_001/environment.json), individual logs, source snapshots, input fixture and output arrays are retained. A generated allocator bytecode cache was present in the copied source directory and recorded in the manifest; the authoritative implementation identities are the pinned `.py` files below. The bytecode cache is not a handoff dependency.

| File | SHA256 |
|---|---|
| Packaged strategy.py | `49269965f5f204a52ddb37d5723edbdf711da742db9cc6b75ffd7ced30549f73` |
| engine.py | `e06cb49f2cf6c396697687ae6607859541ff2054fd8b66320ef357a2ec696cd1` |
| allocator.py | `8b50e5c4fa8ec2efb2baa9de8635ad8988f36387c780de271971245d50f3fe8f` |
| Original score.py | `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96` |

Rerun from the repository root, supplying the verified snapshot path and a new output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python evidence/v2_causality_review_20261028/run_e2e.py --snapshot /workspace/scratch/a83c191d516f/v2-review-snapshot --out evidence/v2_causality_review_20261028/run_002
```

`run_002` has not been executed. The controller refuses to overwrite an existing output directory. The committed snapshot can instead be reconstructed from the pinned branch and pointed to with `--snapshot`.

## 6. Recommended disposition

Keep the V2 model as a viable research candidate. The ordinary information flow passes this review; withdrawing it on a generic lookahead accusation would be unsupported. Ask Claude to correct state lifecycle and panel-layout handling, make the packaged end-to-end gate portable and binding, and retain the actual ledger provenance before treating the package as fully verified. Continue alpha and risk-model research independently of these engineering fixes. The statistical question of whether V2 improves expected future Sharpe remains separate from this causality result.

The draft contribution note should also distinguish a candidate under review from a final selection: `handoff_v2/strategy.py` lines 54–57 currently states that the applicant chose to replace C09. This review has no evidence of that final user decision and does not make it on the user's behalf.
