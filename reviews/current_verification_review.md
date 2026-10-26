# Verification review of the recovered implementation checkpoint

## Scope and current decision

Independent verification agent, distinct from the recovered accounting, alpha, risk and portfolio authors. Reviewed existing artifacts and source; no actual validation/audit rows or supplied full-sample figures were read. This report distinguishes review of prior evidence from newly executed candidate workflows.

The recovered accounting and corrected allocator can support candidate integration. Their evidence does not establish full-strategy causality, realized beta, profitability or long-history runtime. Configured C01/C02 smoke causality has now completed, as recorded below. Full-discovery and factor-specific numerical gates remain unexecuted by this reviewer.

## Recovered evidence inspected

| Workflow | Recorded execution | Independent readback |
|---|---|---|
| Synthetic CSV → supplied loader → supplied scorer → report (`accounting_001`) | Exit 0; 44 passing checks | Scorer snapshot matches unchanged official source; analytic drift, free opening, reversal fees and omitted final return agree with saved results. |
| Corrected synthetic allocator verification (`portfolio_verify_002`) | Exit 0; 54 passing checks | Live allocator matches tested corrected snapshot; verifier matches the final preimplementation snapshot. |
| Discovery alpha diagnostics (`alpha_diagnostics_001`) | Exit 0; 123 passing checks | All 28 existing artifact-manifest entries match their recorded hashes; source reads bounded discovery cache and matured labels. |
| Discovery risk diagnostics (`risk_diagnostics_001`) | Exit 0; nine passing checks | Recorded input slice is `[0,2016)`; decomposition is explicitly retrospective/descriptive. |

This reviewer did not rerun those completed numerical workflows. Reading their results and checking file identities does not constitute an independent numerical reproduction.

### Accounting details

The scheduled control opens `[0.5,0.5]` for free, drifts to `[0.55,0.45]` after `[0.1,-0.1]`, then pays `0.00015` to reset. Its next gross return is `0.03`; drift becomes `[51/103,52/103]` using the gross-return denominator. Reversal to `[-0.3,0.3]` costs `0.0012048543689320388`. The final synthetic row's large returns are not earned. The buy-and-hold control carries actual drift and pays zero costs. The saved official outputs agree with these independently interpretable expectations.

### Portfolio correction approval

The earlier independent reviewer identified an extreme finite-input overflow that could be clipped into a feasible but suboptimal result. The corrected `at_multiplier` now raises on overflow/invalid division before clipping and converts the error into explicit invalid-arithmetic rejection. This addresses the identified mechanism without claiming arbitrary-precision support. The unchanged verifier's completed second run covers its predeclared normal-scale and invalid-input cases. No postimplementation isolated test was added for this review.

| File identity | SHA-256 |
|---|---|
| Live and corrected tested allocator | `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` |
| Live verifier and final preimplementation verifier | `72e417e521c72ecc5f9d109180c5f2744d97787068403c160b111fea815de60b` |
| Live and accounting-snapshot official scorer | `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96` |

## Causality harness integration

Before first candidate execution, the plan was extended to resolve concrete findings already present in `discovery_interpretation_review.md`, then the E2E harness was updated:

- Explicit candidate JSON is frozen, hashed and passed to every fresh-process worker; `configure` is called exactly once before either strategy entry point. Requested and effective configurations are recorded.
- Exact reruns carry the frozen config. A comparison rejects configuration identity changes.
- Multiple prefix lengths are supported with the original initialization and scorer endpoint convention.
- Candidate schedules determine added startup cutoffs: active alpha row 127, risk warmup row 20, first earned target row 253, and first rolling-window boundaries 253/254. Full coverage includes the predeclared later discovery cutoffs.
- Input arrays are read-only and post-run hashes remain checked; the complete forecast must be finite. Changed-suffix execution failures remain unavailable comparisons, not a fabricated causality pass.

Syntax parsing completed for both `tools/verify_causality.py` and the existing `tools/run_candidate.py`; this is an engineering check, not a numerical causality pass. The discovery runner already freezes config and calls configure once, records full drift-based costs from the supplied scorer and separates engineering completion from observed candidate feasibility. It was not modified during this initial review.

## Gate sequence and current status

1. Read the completed candidate and all imported helpers for lag alignment, fit/update schedule, absence of hidden files or future-trained global state, and purity of its optional risk diagnostic. **C01/C02 source review completed below; C04 source observations also recorded.**
2. Execute explicit C01 and C02 smoke causality profiles and relevant full-discovery profiles, each with frozen identities and complete evidence. **Both smoke profiles completed below; broad finalist verification remains pending.**
3. Let the lead own the bounded economic comparison and experiment budget. Causality workflows do not rank candidates or open validation.
4. Preserve exact gate scope. Tested discovery causality does not establish century-length runtime, all future paths or hidden-continuation profitability.

## Completed C01/C02 source review

The implemented recurrence agrees with the preregistered information clock: at row `t`, the new design is `X[t-2]`, the label is `R[t-1]`, and the label's beta is estimated from `R[:t-1]`. Both EW moments are normalized by the same accumulated mass before the positive ridge is added. The 126th matured pair is incorporated at row 127, the first active prediction. Prediction features are `X[t-1]` and each transform uses only its own published panel.

The sole loop dependence on the total supplied length is where the loop stops and how much output is allocated. All fitted state is local to that forecast call. The imported portfolio helper is state-free; `rebalance` computes risk from its observed history. `_LAST_DIAGNOSTICS` is overwritten after each target, returned only by copy and never read by a decision. `estimate_risk` allocates centered/derived arrays without changing caller arrays or module state. There are no file, network, environment or external data reads in the candidate or imported portfolio helper.

This source review supports causal construction under a fixed valid configuration. Numerical altered-future E2E remains a separate required check. Finite input and tested-path arithmetic are not guarantees for arbitrary extreme values or every possible future history.

The portfolio research agent independently reviewed the changed causality harness and reported no blocking issue: configured fresh workers, cutoff inclusivity, prefix/append masks and final identity checks agree with the original scorer. This was a source review, not an additional numerical execution.

## Executed configured smoke causality

Both frozen candidates completed the corrected E2E controller with exit 0 and `EXECUTED_PASS_SCOPE_ONLY`. Each run has **28 fresh-process scenarios**: one baseline and 27 completed comparisons, comprising an identical repeat, return-only/characteristic-only/joint alterations at each cutoff `[0,20,21,127,252,253,254,400]`, a 384-row prefix and a 64-row synthetic append. Actual base input was only discovery `[0,600)`; the append is synthetic.

| Candidate | Evidence | Comparison records | Maximum protected absolute error | Identity checks |
|---|---|---|---:|---|
| C01 linear | `evidence/causality_C01_smoke_002/summary.json` | 111 PASS, 51 NOT_APPLICABLE | 0.0 | Candidate, config, protocol, scorer and inputs unchanged |
| C02 additive | `evidence/causality_C02_smoke_002/summary.json` | 111 PASS, 51 NOT_APPLICABLE | 0.0 | Candidate, config, protocol, scorer and inputs unchanged |

The not-applicable records are empty protected target or economic ranges before those outputs begin; they are not evidence covering active trading. Active forecast row 127, first target row 253, first rolling-risk eviction, later row 400, prefix length and append invariance are explicitly covered. Each worker also completed the original scorer with finite outputs and no input mutation. Timing was excluded from numerical equality, as specified before execution.

Tested strategy SHA-256: `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7`. Tested allocator SHA-256: `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475`. C01 explicit config SHA-256: `d68f6c02fa119ee9461fbff203c6e1ac6613b524aa84da3174a392bae8673fdf`.

C02 explicit config SHA-256: `5f49f216ed267dec8e91749679bafcd14b9d2acb5f5605f69ab6e6d9fc245bfb`.

The prior `smoke_001` runs are **incomplete orchestration interruptions**, not passes or candidate failures. They preserve their original source/plan/config and seven completed scenarios (baseline plus six comparisons) each. Their original checkpoint summaries and the recorded interruption are retained. The new controller removed normal-path global Python profiling in favor of exception-only scorer traceback inspection. Identical candidate/config identities were used for `smoke_002`. Total concurrent wall times do not establish a controlled speedup or runtime eligibility.

Each completed packet contains frozen source/config/protocol, bounded input identities, expected boundaries, scenario manifests, exact rerun commands, worker logs, daily ledgers, protected arrays and final statuses. An additional same-affinity rerun script records the original single CPU choice (C01 CPU 7, C02 CPU 8). Those supplied rerun scripts have not themselves been executed as another full gate.

## C04 source observations and next verification boundary

A separate source read of `strategy_factor.py` found that only rebalance populates the factor cache, using trailing observations. Refresh epochs depend on observed history count with an anchor at target 253 and period 21; repeated/decreasing history length clears cached factors. Forecast delegates to the causal base learner without filling future risk state, and the optional risk diagnostic remains pure. The alpha-model reviewer separately approved factor solver mathematics and its existing preimplementation numerical evidence in `reviews/factor_independent_review.md`. Neither review establishes a C04 numerical causality pass. Its materially new paths include initialization 253, refresh 274, following nonrefresh 275 and later cache reuse/refresh.

Per the lead's direction, full-discovery causality is reserved for the eventual finalist(s), avoiding repeated broad gates for rejected configurations. The reserved actual validation/audit remains closed in this work. No full-discovery, C04, multi-decade, final-folder or hidden-future claim is supported by these smoke results.

## Discovery telemetry integration

After the initial review, and before the relevant candidate execution, an expectation addendum and then a runner change added read-only portfolio diagnostics. The trace records pre-scale gross, gross scaling, cap saturation and estimated-beta exposure; it reconciles gross before/after scaling and reports scaling frequency. A further C04 addendum preserves all finite scalar factor diagnostics with a fixed field set and prevents overwriting core scorer fields. Summary statistics retain factor fallback/refresh counts, age, rank and solver/covariance diagnostics. These calls occur outside measured candidate-call time and cannot alter the original scorer's arithmetic. Actual C04 behavior must be read from its subsequent root-owned economic run; this reviewer did not execute a scored candidate comparison.
