# C12 independent source review

**27 October 2026, Europe/Paris.** Reviewer: independent verification agent, distinct from the C12 implementation author. This source review was written before the green synthetic workflow. It authorizes that frozen workflow within its scope; no market-performance, validation, audit, or universal causality pass is inferred.

## Reviewed identity and construction order

The prospective model specification has SHA256 `6734f57b354abd8b1e5e2102d196e10fe07b9e9bb5297f5f573d62848d39ab12`. The independent workflow expectations have SHA256 `4fb69198d908491a52a5d0077140fd370def4dcf4a2da453742e3a1bfb43bea7`; the controller is `309d25d824e3fcd8964c50def826787b0f86fe4a4bde0a1c93f0abeb3c29471d`. Those sources and the absent candidate/config were recorded before implementation. The expected red run is preserved at `evidence/C12_synthetic_red_001`: exit 1, `EXPECTED_RED_MISSING_MODULE`, zero candidate workflows, frozen-source and generated-input integrity true.

After all three C06 candidate snapshots were confirmed frozen, the implementation author was released. Reviewed C12 source SHA256 is `c832d4fb444f14ea714a21ce70a873e5c9f3c31e63dbe68f84fccb572d47760f`; explicit configuration SHA256 is `7d37ef0d34bbb95fc33dd12e64a88688d9f995cba23e8223813b8e3e01edcd12`. All ten existing candidate sibling source files are byte-identical to the red snapshot. The independent plan and controller remain byte-identical; no test or threshold was added after implementation. Exact chronology and hashes are in `evidence/C12_synthetic_build_order_001`.

## Basis and penalty review

The new module calls the unchanged additive `base._basis`, preserves its original 26 columns in the concatenation, and derives the local block from those exact centered linear and square arrays. It forms all thirteen characteristics' hinges at -1, 0, and +1, centers each within the current panel, subtracts fixed analytic reference projections and divides by the fixed reference standard deviations. Its `(stocks,13,3)` array is reshaped in feature-major order, matching column `26+3*j+k`. There is no selected subset, empirical reference fit, ranking across time, or input-dependent knot.

An independent analytic calculation before candidate implementation confirms reference scales `0.11811820495718785`, `0.10614888300004365`, `0.11811820495718879`. The normalized three-term reference Gram eigenvalues are approximately `0.138404`, `1.069956`, `1.791640`, so the terms are correlated; a single `1/1.3` shrinkage multiplier is not the joint model's shrinkage. This calculation is design algebra, not a postimplementation isolated candidate test. Its full numbers and formula are retained in `02_analytic_reference_calculation.json`.

The forecast moment arrays are 65-dimensional. Its ridge diagonal assigns 0.1 to the original 26 directions and 0.3 to the 39 added directions, using the admitted explicit config. Both design and target moments use the same 252-day exponential decay and accumulated mass. No parameter search or alternative penalty is present.

## Information clock and state review

At forecast index `t`, the newest training design is characteristic panel `t-2`; its return label is `t-1`. The label beta uses returns strictly before `t-1`. The emitted forecast uses characteristic panel `t-1`. Starting at `t=2` makes the 126th matured pair available at `t=127`, matching the first potentially nonzero forecast. All moment arrays, mass, coefficients and learned state are local to `forecast`; the global arrays contain only the deterministic analytic reference constants and configuration.

The candidate delegates rebalance, risk estimation and diagnostics unchanged to the base implementation. Forecast does not populate a fitted object that rebalance later consumes. Each independent workflow imports the copied closure in a fresh interpreter and applies its frozen configuration. The worker checks read-only input preservation and verifies held positions are not mutated. These source observations support the intended clock, while the prospective altered-future and prefix workflows will supply finite-path evidence.

## Scorer and cash control

The workflow retains the supplied scorer byte-for-byte, including start 252, the waived opening trade, drift based on gross return, full subsequent costs, the closing target, and the unused final input return. It reconciles economics from saved consecutive targets for the baseline and exact-zero-return cases. The new basis does not change accounting or the allocator's existing gross-rescaling approximation.

With exactly zero returns, labels and moment vectors remain zero; positive ridge makes the linear system nonsingular, forecasts remain zero, and the unchanged allocator's empty initial holdings stay zero. The complete scorer can therefore run without invoking its variance-based report on that case. The frozen controller requires zero numerical economics and explicitly records undefined Sharpe/beta as null with reasons. The green execution must establish this behavior; this source argument alone is not a pass.

## Review decision and limits

No discrepancy between source and admitted specification was found. Proceed with the unchanged five-case synthetic E2E controller on CPU5. Any failure must remain visible and be resolved without changing the prospectively fixed expectations or silently selecting a more favorable candidate. After that gate, the lead may separately authorize the one admitted discovery run.

A successful synthetic run will establish only the stated fixture, accounting and protected-prefix properties. It will not demonstrate tradable alpha, rule out every possible information leak, establish long-horizon runtime, or remove selection optimism from the eleven earlier discovery results and subsequent design reasoning.
