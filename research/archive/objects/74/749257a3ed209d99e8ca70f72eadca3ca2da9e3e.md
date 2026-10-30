# C12 synthetic E2E result

**27 October 2026, Europe/Paris. Status: `EXECUTED_PASS_SCOPE_ONLY`, exit 0.** All five prospectively specified workflows completed, and all 55 recorded checks passed. The source review and synthetic gate permit the lead to consider the one admitted discovery run; they do not establish a market edge or open validation/audit.

## Evidence and construction order

The exact expectations, controller and expected missing-module run preceded candidate implementation. The original red packet remains at `evidence/C12_synthetic_red_001`, with exit 1 and zero candidate workflows. The complete green packet is `evidence/C12_synthetic_001`; source/config/plan construction records are in `evidence/C12_synthetic_build_order_001`. No candidate bug fix, verifier change, threshold adjustment, seed selection, or additional case was needed between red and green.

The green runner SHA256 is `309d25d824e3fcd8964c50def826787b0f86fe4a4bde0a1c93f0abeb3c29471d`, identical to the preimplementation snapshot. Candidate SHA256 is `c832d4fb444f14ea714a21ce70a873e5c9f3c31e63dbe68f84fccb572d47760f`, identical to the independently reviewed implementation. The requested configuration values match the admitted dictionary in every worker. The source JSON's hash and the controller's normalized JSON hash differ because the controller writes parsed JSON; the exact values and both forms are retained. This is serialization, not a parameter change.

Every worker ran on CPU5 with numerical threads set to one and imported the copied eleven-file candidate closure and original scorer. The worker recorded distinct PIDs within this controller's process namespace. Caller arrays and supplied holdings remained unchanged. Final source/input integrity checks passed. Independent readback of all 80 files recorded in the artifact manifest found no missing file, size mismatch or hash mismatch.

## Protected-decision results

| Workflow | Result | Protected scope |
|---|---|---|
| Baseline | Complete, finite, bounds/accounting checks passed | 600 forecast rows,347 targets,346 economics rows |
| Identical repeat | All four comparisons exactly equal | All forecasts,targets,economics and derived net returns |
| Joint future change at400 | All four comparisons exactly equal | Forecasts through400,targets earning through400,economics before400 |
| Prefix384 | All four comparisons exactly equal | Forecasts through383,targets through383,economics through382 |
| Exact zero returns | Complete, exact cash behavior | Every forecast,target,economic channel and net return is zero |

All twelve protected numerical comparisons had maximum absolute error zero. The joint intervention changed200,000 return values and2,600,000 characteristic values while preserving both earlier input prefixes exactly. Date-index assertions matched the declared scorer endpoints. These outcomes are finite tested paths, not a proof for every possible history.

The first nonzero baseline forecast appeared at row127, after the specified126 matured daily pairs. The pooled scored-forecast/known-truth correlation was **0.988107**, above the prospective0.90 floor. The fixture intentionally embeds a strong stationary local response; this result establishes learning and wiring capability under that construction.

## Economics and cash-path results

On the strong synthetic baseline, the scorer charged total full fees of0.0038288874 across346 scored rows; the separately recorded opening trade waiver was0.0000100096. Saved-target reconciliation differed from the official gross ledger by at most `2.60e-18` and from full fees by `8.47e-21`, within the frozen numerical tolerances; gross exposure matched exactly. Maximum absolute stock weight was0.00114403, maximum gross was1.0000000000000004 within the specified floating-point tolerance, and realized net-market beta was0.00117812.

The synthetic net Sharpe was126.679. Its deliberately unrealistic magnitude reflects the engineered strong, stationary signal and cross-sectional diversification; it must never be presented as project-market performance, a tradable forecast, or an attainable return. The complete baseline metrics and unchanged scorer text remain in `summary.json` and `official_report.txt` for transparency.

On the exact-zero-return fixture, forecasts, targets, gross returns, trading costs, exposure, market returns and net returns were exactly zero. Net-return and market-return variances were exactly zero. Sharpe and beta are stored as null with explicit undefined reasons; no zero ratio is invented. The full original scorer execution completed, while its variance-based reporting function was intentionally not called on this undefined path, as specified before implementation.

Measured baseline forecast time was1.515 seconds and mean official rebalance latency1.997 milliseconds in this600-row instrumented workflow. These are local measurements, not long-history acceptance evidence. Timing is excluded from numerical invariance comparisons.

## Remaining gates

No actual discovery input was used by this synthetic workflow. Actual-data economics, comparison with C02/C06, full-data C12 causal behavior if nominated, protected chronological evaluation, long-history runtime, clean-folder reproduction, and final independent release review remain separate gates. The research budget still allows only the admitted C12 configuration, without retuning the hinge knots, scales, penalties, or portfolio policy after seeing its result.
