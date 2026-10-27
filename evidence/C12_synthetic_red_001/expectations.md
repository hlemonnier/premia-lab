# C12 local-additive synthetic workflow: prospective expectations

**27 October 2026, Europe/Paris.** This independent E2E plan restores the approved, unexecuted C12 verification after the workspace reset. Lost intermediate runs are unavailable evidence, never passes. This file is written before the new controller and candidate implementation. The controller must be frozen and an expected missing-module run preserved before the implementation author is released. No isolated unit tests are introduced.

## Purpose and failure modes

Exercise the complete C12 forecast and portfolio through the unchanged supplied scorer, in a fresh process for every case. The workflow must detect incorrect lag alignment, absent or incorrectly scaled local response terms, missed training warmup, future-dependent forecasts or positions, input mutation, invalid target bounds, missing cost charges, wrong drift accounting, nonrepeatable state, and invented metrics on a cash-only path. It does not establish predictive power on the supplied market, comprehensive causality, or freedom from adaptive selection overfit.

The admitted model is defined in `research/LOCAL_ADDITIVE_PLAN.md`: preserve C02's original 26 columns and add 39 fixed-reference local hinges, with original ridge 0.1 and local ridge 0.3. No candidate parameter, fixture parameter, case, mask, or threshold may be chosen after viewing a C12 result. Fix a concrete implementation bug against this unchanged gate and preserve both attempts if necessary. A failure is not permission to tune the candidate or increase the discovery budget.

## Deterministic independent fixture

Use NumPy `default_rng(20261027)`, exactly 600 days, 1,000 stocks and 13 characteristics, float64. Draw in this order:

1. Characteristics are standard-normal draws of shape `(600,1000,13)`.
2. Market innovations are 600 standard-normal draws, clipped to `[-4,4]` and multiplied by 0.008.
3. Stock innovations are standard-normal draws of shape `(600,1000)`, clipped to `[-4,4]`, multiplied by 0.006, and centered across stocks for each day.

The deterministic true stock betas are `linspace(0.6,1.4,1000)`. Full one-way costs are `linspace(0.000005,0.000015,1000)`. Construct the known response independently, without importing any candidate module. For each prior-day panel, standardize each characteristic by its current cross-sectional mean and population standard deviation (floor `1e-12`), clip to `[-4,4]`, and recenter to obtain `z`. Let `q=(z**2-panel_mean(z**2))/sqrt(2)`. For each tuple below form a centered hinge, subtract its fixed standard-normal projections and divide by its reference standard deviation:

| Characteristic | Knot | Truth coefficient |
|---|---:|---:|
| 0 | -1 | +0.0015 |
| 2 | 0 | -0.0010 |
| 4 | +1 | +0.00075 |

For each knot `a`, define `Q=erfc(a/sqrt(2))/2`, `phi=exp(-a*a/2)/sqrt(2*pi)`, `m1=phi-a*Q`, `m2=(1+a*a)*Q-a*phi`, `s2=m2-m1*m1-Q*Q-phi*phi/2`. The local term is `(maximum(z-a,0)-panel_mean(maximum(z-a,0))-Q*z-phi*q/sqrt(2))/sqrt(s2)`. For day `t>=1`, truth is the weighted sum from panel `X[t-1]`; truth at day 0 is zero. Returns are true beta times market innovation, plus truth, plus stock innovation. Truth and true beta are retained for controller evaluation and are never passed to the candidate.

This signal is deliberately strong and stationary, with no effort to imitate achievable market returns. The generated arrays must be finite, all returns above -1 and all costs nonnegative. Preserve arrays, file and array hashes, seed, exact generator source, and NumPy version. The separate cash-control fixture reuses the exact same characteristic and cost arrays, but replaces every return by exactly zero; its input identities are separately recorded. No actual project return or characteristic array is accessed.

## Exact configuration and scorer contract

Use candidate ID `C12_local_additive`, additive basis, alpha half-life 252, ridge 0.1, local ridge 0.3, minimum training pairs 126, clip 4, risk window 252, minimum risk days 20, variance shrinkage 0.2, variance floor `1e-6`, risk aversion 1000, cost horizon 20, stock cap 0.01 and gross cap 1. The explicit requested dictionary and candidate-reported configuration must match exactly in each process. Synthetic-specific model parameters are prohibited.

The original scorer SHA256 is `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`. Invoke its unchanged `run` with start 252. A 600-row input produces 347 targets for earning rows 253–599 and 346 economic rows 253–598. A 384-row prefix produces 131 targets for earning rows 253–383 and 130 economic rows 253–382. The initial target is free under the supplied scorer; all subsequent drift-adjusted changes pay full costs, including the closing target at the endpoint. The portfolio's cost amortization does not change this charge.

## Five fresh-process workflows

Run sequentially on CPU5 with numerical-library thread variables set to one. Reuse a byte-identical frozen copy of `tools/verify_causality.py`; each case starts a fresh interpreter, imports the complete frozen candidate and scorer, calls `configure`, forecasts, and executes the original scorer. The cash control uses the worker's ordinary baseline kind with a different input directory; no special candidate or worker logic is needed.

| Case | Inputs | Protected comparisons |
|---|---|---|
| baseline | All 600 synthetic rows | Known-signal capability, economics, accounting and controls |
| repeat | Identical 600 rows | All forecasts, targets and economic rows |
| joint_from_400 | Returns at rows 400 onward multiplied by 0.5; characteristic panels in that suffix reversed | Forecast rows 0–400 inclusive; targets earning through 400; economic rows strictly before 400 |
| prefix_384 | Only rows 0–383 | Forecast rows 0–383; targets earning through 383; economics through 382 |
| zero_returns | 600-row cash-control fixture | Exact zero forecasts, targets and all four economic channels; valid interface, input integrity and accounting |

The joint intervention must leave the earlier inputs byte-identical and actually alter both suffix arrays. Confirm intervention metadata, masks, target-day and economic-day indices. A later suffix error alone does not imply prefix leakage: retain failed logs and classify unavailable comparisons as unverified. Timing is retained but excluded from output equality. Numerical protected comparisons use the unchanged worker tolerance `atol=1e-14`, `rtol=1e-12`; exact date-index and cash-zero assertions use exact equality. Report actual maximum error, including exact equality when observed, rather than implying tolerance implies exactness.

## Fixed acceptance criteria

- All five complete workflows return the expected forecast, target and ledger shapes; outputs are finite; caller inputs and holdings are unchanged; observed source/config/scorer identities match the frozen expected closure.
- Target absolute stock weight is at most `0.01+1e-12`, gross at most `1+1e-12`; each gross and net scored return exceeds -1.
- Baseline forecast rows 0–126 are exactly zero and row 127 contains a nonzero prediction. The cash-control forecast remains zero throughout.
- On baseline scored rows 253–598, pooled Pearson correlation between all forecast values and withheld truth is at least 0.90, with positive variances.
- Baseline daily net mean is positive, annualized population-standard-deviation Sharpe exceeds 1.0, and centered realized net-market absolute beta is below 0.2. These strong-fixture engineering checks are not market acceptance thresholds.
- Reconcile baseline and cash-control gross returns, full drift-based costs and posttrade gross exposures from saved consecutive targets and same-day returns. For targets `w_t,w_(t+1)`, expected gross is `w_t dot R_t`; drift is `w_t*(1+R_t)/(1+gross)`; full cost is `abs(w_(t+1)-drift) dot costs`; scorer exposure is `sum(abs(w_(t+1)))`. Use the unchanged numerical comparison primitive.
- Every repeat, altered-future and prefix comparison passes the exact protected ranges above. No empty or unavailable range is a pass.
- Cash-control forecasts, targets, gross returns, fees, exposure, market returns and derived net returns are exactly zero. Net and market variance are exactly zero. Report Sharpe and beta as JSON null with explicit undefined reasons; never substitute zero. Avoid the official reporting function on this path because variance-based ratios are undefined, while the complete original `run` must still complete.

Report baseline gross/net Sharpe, annualized net mean/volatility and fees, paid fees, opening fee waived, realized beta, known-true-beta exposure, target extrema, forecast/truth correlation, forecast seconds, and mean/max scorer rebalance latency. The original scorer's baseline textual report is retained. No runtime acceptance beyond child completion is inferred; the 600-row workflow does not establish long-horizon limits.

## Construction order, snapshots, and outcomes

1. Preserve this plan and its hash in `evidence/C12_synthetic_build_order_001/01_plan_*`.
2. Write `tools/verify_c12_local_workflow.py`, freeze it and its hash as `02_verifier_*` before candidate source exists.
3. Run the command below while the candidate is absent. Require exit 1 and `EXPECTED_RED_MISSING_MODULE`, after freezing plans, controller, worker, config, scorer, existing source closure, generated inputs, environment and exact rerun. It executes zero candidate/scorer workflows. This is construction-order evidence, not a failure of implemented C12.
4. After the red run is preserved and the root confirms all C06 source snapshots are frozen, release the implementation author. Record the implementation source/config identities before executing green. Independent source review precedes the green run.
5. Run the same frozen controller with the admitted configuration. Never overwrite a prior evidence directory. Preserve setup, expectations, exact source/config/input hashes, scenario manifests, commands, environment, all child logs/status/outputs, actual checks and final integrity checks. Use 300 seconds per child; timeout yields incomplete/unverified evidence.

```sh
taskset -c 5 python -u tools/verify_c12_local_workflow.py --project . --strategy submission/strategy_local_additive.py --out evidence/C12_synthetic_red_001
taskset -c 5 python -u tools/verify_c12_local_workflow.py --project . --strategy submission/strategy_local_additive.py --config research/configs/C12_local_additive.json --out evidence/C12_synthetic_001
```

The actual-data discovery run, market comparison, full-data causal gate, validation, audit, long-history runtime and release are separate, unexecuted gates. This plan opens none of them and authorizes no new configuration.
