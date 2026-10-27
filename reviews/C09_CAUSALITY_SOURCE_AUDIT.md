# C09 source and protected-evaluation admission review

27 October 2026, Europe/Paris. Independent source review by the local-alpha agent. This review precedes the C09 full-discovery causality run and does not claim that an unexecuted check passed. No candidate or helper source was changed.

## Reviewed policy

C09 is `submission/strategy.py` with `research/configs/C09_additive_long_memory.json`. Its imported project closure is `strategy.py` and `portfolio.py`; it does not import the GLS, factor-risk, interaction, gross-constraint, or local-hinge candidate modules. The recorded C09 configuration differs from C02 only in candidate ID and the previously admitted 1,008-day alpha half-life. Risk estimation remains a 252-day trailing estimator and the other portfolio settings are unchanged.

The checked source/configuration hashes are recorded in `verification/C09_FULL_DISCOVERY_CAUSALITY_PLAN.md` and the accompanying admission manifest. Historical C09 original-source identities are retained as the authority for source equivalence. Source equivalence is distinct from cross-environment numerical output equality.

## Information clock and fitted state

`_basis` consumes one supplied panel. Cross-sectional standardization, fixed clipping, recentering and squares use only that panel; no time-series fit, future row, selected feature list, or full-sample rank is involved. All thirteen linear and thirteen square columns are included.

The forecast loop begins at row 2. At forecast `t`, it reads design panel `t-2`, computes label beta from the return prefix ending at `t-2`, then consumes label return `t-1`. It applies the fitted coefficients to panel `t-1`. With 126 matured pairs, the first active row is 127. The half-life changes the fixed decay scalar, not the information boundary or activation date. Gram, moment, mass, matured count and coefficients are local to this invocation. Total input length controls allocation and iteration termination, not a historical tuning decision or refresh schedule.

`rebalance` recomputes its beta and variance from the history supplied by the original scorer. It uses no forecast-fitted global model. `CONFIG` contains only fixed validated parameters; `configure` rebuilds defaults and clears diagnostics. `_LAST_DIAGNOSTICS` records current-call quantities but is never consulted to choose a later target. Each verifier scenario uses a fresh process, which independently excludes inherited module state from a preceding scenario.

The imported project source has no file reads, network access, subprocess calls, random sampling, wall-clock decision logic, dynamic imports, external learned artifacts, or reads of project validation/audit paths. NumPy and Python internals are dependencies whose implementation internals are outside this source audit.

## Portfolio and accounting scope

The allocator receives the actual drifted held book. It uses a fixed amortized absolute-turnover penalty, positive diagonal risk and an estimated-beta equality with stock bounds. Its scalar dual search has bounded bracketing/bisection loops and raises on unrepresentable arithmetic or unresolved hedge tolerance. It creates new target arrays and does not intentionally mutate caller inputs. The base strategy may proportionally rescale the target to the gross cap; that preserves the estimated-beta hedge but remains the already documented approximation to a jointly gross-constrained optimum.

The supplied scorer, not the optimizer's cost amortization, charges full actual trading costs. Its free initial trade and final closing target are retained. Estimated beta neutrality does not promise realized net-market beta below 0.2 on unseen returns. Historical full-fee, path and feasibility results remain separate empirical evidence; this source review does not substitute for current E2E execution.

## Prospective admission rule review

`research/PROTECTED_EVALUATION_ADMISSION_PLAN.md` keeps the original budget and at-most-three validation policies, nominates exact C06 and C09, conditionally admits C12 under its already frozen paired economic criterion, and freezes simplicity ranks before validation. It preserves continuous replay, correct exclusive endpoint masks, pooled daily net-Sharpe ranking, the original absolute-beta eligibility rule and the one-candidate sealed audit. There is no extra minimum Sharpe or profitable-every-block requirement. Candidate selection on development data remains acknowledged selection exposure.

No substantive nomination-design objection was found. Before holdout access, the rule's historical-prefix reconciliation language needs the root's explicit portability disposition: same-environment causal prefix equality and cross-environment historical reproducibility must not be conflated, and old forecast/target numeric comparisons cannot be declared passed when the original arrays are unavailable. The C09 execution profile prospectively preserves this separation. That disposition plus completed engineering evidence and an immutable concrete nominee manifest are still required; this review grants no protected-data access.

## Outcome

**Source audit: no identified lookahead path in the reviewed two-module C09 closure.** The proposed representative full-discovery intervention profile is appropriate for its stateless ordinary learner and diagonal risk path. It tests first activation, first trade/cost, risk-window eviction, a later midpoint and endpoint, plus truncation/append/repeat. It does not cover every date or conceivable history. Finite causal agreement does not establish absence of research overfit or a tradable edge.

## Prelaunch representation update

The root's canonical-layout C06 standard rerun has now reproduced its historical forecast/target/held-book hashes exactly. The prior unknown-portability discussion was a provisional triage state. The verification fixture had converted canonical Fortran-contiguous returns to C order. The independently reviewed correction preserves original order for copies, prefixes and appends and records actual strides/contiguity. The revised C09 execution profile retains exact original forecast/target and economic-prefix references, with failures still blocking release. It uses corrected verifier SHA-256 `b46df7ed7e3dec9677a7d855ca6b082c872a7c15ce645eaf15f5246f475cdc83` under `verification/INPUT_LAYOUT_CORRECTION_PLAN.md`. The original unexecuted C09 proposal/review/admission remain preserved in `evidence/C09_causality_admission_001`; no C09 model source, configuration, scope, masks or tolerances changed.
