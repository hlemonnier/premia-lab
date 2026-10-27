# Protected replay controller: pre-access engineering results

**27 October 2026, Europe/Paris.** Both prescribed complete workflows finished on CPU5 with status `EXECUTED_PASS_SCOPE_ONLY` and exit0. They used the exact existing C06 configuration. No validation or audit market observations were parsed, no candidate was selected, and no additional alpha configuration was introduced.

## Prospective order and identities

The expectations in `verification/PROTECTED_REPLAY_PLAN.md` were recorded before the controller existed. The build-order record is `evidence/protected_replay_build_order_001/01_plan_record.json`. After implementation and syntax-only compilation, the lead independently reviewed the admission checks, bounded loading, full scorer accounting, masks, original-prefix gates, failure/access records and frozen rerun paths. The lead released exactly the two engineering workflows. The execution source and release are preserved in `02_controller_snapshot.py` and `02_implementation_record.json` in that folder.

| Artifact | SHA256 |
|---|---|
| Prospective replay plan | `32dc6a11c84ce4009490cccd057f0b0836f22581ef42e05ede77c51ebb0dd436` |
| Executed controller | `d3c3cfd4a1fde10398fc5546f3dc48d395f68a4c06fbe73311c8b5c2cdc37dfe` |
| Unchanged metric/helper source | `6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69` |
| Original scorer | `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96` |
| Exact C06 configuration | `f424033fae2e2ca4a8f0a532a2da41dc4841235f1c8c67394e26e9081c9a49fb` |

The original candidates, scorer, metric helper and protocol were not edited. Initial source review corrected a scorer-hash transcription and a JSON-serialization detail before execution was frozen. Neither issue generated a model execution or protected-data exposure. No executed failure was discarded.

## Executed outcomes

| Complete workflow | Inputs | Targets / economic rows | Checks | Result |
|---|---|---:|---:|---|
| `evidence/protected_replay_discovery_001` | Existing canonical discovery rows `[0,2016)` | 1,763 / 1,762 | 38/38 pass | Exact historical decision/economic parity |
| `evidence/protected_replay_zero_001` | Fully synthetic zero returns and characteristics, 3,024 rows, positive costs | 2,771 / 2,770 | 34/34 pass | Exact cash path and defined handling of undefined ratios |

Both replays invoked the original scorer once from start252. The saved full daily ledgers cover return indices253–2014 and253–3022 respectively. Both preserve Fortran-contiguous returns and C-contiguous characteristics. All candidate, scorer, helper, plan, protocol, reference and input identities remained unchanged through completion.

### Discovery parity

The complete original forecast, target and drifted-held-book NPY identities reproduced exactly:

- Forecasts: `0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0`.
- Targets: `b4f2365512f31aa0dbf77e1e1bcfa9c32b187aa47ab516c5c0d878c42127d886`.
- Held books: `8cbfc1e2c61a58a2651ff9bb425a217ca18dceabcb6bd406f4883e4d0318c853`.

All1,762 gross-return, full-cost, gross-exposure, market-return and net-return observations also match the original economic columns exactly. Timing columns are measured anew and are outside the equality target. Net Sharpe is exactly the existing development result, `0.762944047825874`; this is a reproduction, not a new alpha discovery.

Captured scorer fees and target gross exposures match exactly. Separate vectorized arithmetic agrees at the unchanged `atol=1e-14,rtol=1e-12`: maximum absolute errors are8.67e-18 for gross returns,1.73e-18 for drifted holdings and6.78e-20 for fees. The opening full cost of0.000500452666648163 is recorded as waived, with all later costs charged. The path passes finiteness, stock/gross limits, and gross/net solvency checks.

Measured candidate forecast time is5.301s; mean candidate rebalance time is8.377ms. These measurements describe this discovery workflow. The separately approved long-history workflow supplies the full-century runtime evidence.

### Zero-return workflow

Forecasts, targets, drifted held books, gross returns, full fees, closing gross exposures and market returns are all exactly zero. Positive input trading costs do not create a fee without a trade. Independent accounting differences are exactly zero.

The fixed validation masks contain504 rows for A `[2016,2520)`,503 rows for B `[2520,3023)`, and1,007 rows for pooled validation `[2016,3023)`. Every interval has zero arithmetic net mean, zero volatility and zero full fees. Net Sharpe, gross Sharpe and realized beta are JSON null with explicit zero-variance reasons. The textual scorer ratio report is skipped with a reason. The synthetic beta eligibility flag has no economic interpretation; its scope is explicitly `NOT_APPLICABLE_SYNTHETIC`.

Historical market-prefix comparison is explicitly `NOT_APPLICABLE_SYNTHETIC_VALUES`. This workflow exercises the validation-length endpoint and undefined-metric paths. No audit-length synthetic workflow was executed; the audit-mask arithmetic was source-reviewed.

## Evidence integrity and remaining release boundary

Each evidence packet preserves exact commands and frozen rerun commands, environment and CPU/thread settings, source/configuration/reference/input manifests, expected outcomes, per-check actual outcomes, full arrays, daily/target ledgers, metrics and logs. The saved-output readback in `evidence/protected_replay_build_order_001/03_result_readback.json` verified all81 recorded artifacts across both packets without a mismatch. All72 recorded checks passed. Both summaries record `protected_numeric_access_started:false`, `validation_opened:false`, and `audit_opened:false`.

The discovery summary SHA256 is `c93783920644352300a939af287fbaed53afbd0b6675fa2a3a08b0487be31bb1`; the zero-workflow summary SHA256 is `68da4f379866e7b10b1a4fe394ea2b41e232d17bbbed552193fd204368d216ad`. These executed summaries can serve as the controller-verification evidence in the lead-owned nomination manifest.

Actual validation still requires that separately frozen root-approved nomination manifest, its exact hash, the completed candidate engineering evidence, and the lead's explicit execution release. Audit additionally requires the frozen selected-policy record. The two engineering passes establish the tested replay behavior; they do not establish future profitability, absence of research overfit, or universality beyond the reviewed and executed paths.
