# Independent V2 real-data replay and descriptive diagnostics

28 October 2026 (Europe/Paris). This plan precedes the new replay harness and its
execution. Reviewer scope: reproduce existing policies and explain numerical
behavior; no candidate, coefficient, risk model, parameter, or strategy decision
will be changed or selected here.

## Frozen inputs and policies

- Claude branch `v2-factor-risk`, pinned commit
  `afed8d0cb017acda151c4ea262fc30db7568a4bb` (48 additions over main `fb8c702...`).
  All downloaded file Git blob hashes were checked against GitHub.
- V2: exact four `handoff_v2/` files, including its packaged gamma=200,
  stock cap=.05 and gross cap=5, factor scale=.3. Do not substitute research code.
- Comparator: original four `handoff/` files from main `fb8c702...`, unchanged.
- Original 136,015,226-byte ZIP, SHA256
  `ba49564fb0d8888124fdc0b680f88c843c17359a089129f1fe28e0b94e003dd6`.
  Verify original CSV hashes against `evidence/audit_C09_001/input_manifest.json`.
- Use the original scorer's `load` and `run` functions without editing it.
  Record actual array shape, dtype, strides, C/F layout and hashes. The actual
  CSV loader supplies float64; no unrecorded float32 cache is admitted.
- Separate fresh process and clean package directory for each policy. Preserve
  exact imported paths, copies of all executed source, environment and command.

## Replay expectations and failure reporting

1. Both policies complete the full 3,780-row input with 3,526 scored rows,
   zero-based earning indices 253 through 3778. Every output is finite. Use
   original discovery [253,2015), validation [2016,3023), audit [3024,3779)
   masks, counts 1762/1007/755. Keep the two excluded boundary rows in full output.
2. Published V2 rounded net Sharpes: full 1.243; stages 1.098,1.657,1.148.
   Published C09: .885; stages .700,.659,1.799. Compare at stated three-decimal
   precision; do not replace these historical artifacts with replay values.
3. Preserve complete daily economic rows and targets/held identities. Compare
   C09 economic fields to the existing canonical audit ledger where definitions
   match. Report exact equality and maximum discrepancy; 1e-10 absolute is a
   declared portability tolerance, not a claim of bitwise identity.
4. Instrumentation may observe returned values and the solver's saved multipliers
   but must return original outputs unchanged. It introduces timing overhead:
   instrumented replay is not a formal runtime gate and no century run is claimed.
5. If source timing, imported bytes, hashes, array ordering or scored rows differ,
   preserve failure and investigate before performance interpretation.

## Prespecified allocator observations

Observe each original V2 allocator call before the inherited gross scaling.
Let M=B L, lambda be the first r saved multipliers, nu the normalized-beta
multiplier, and bn=b/max(abs(b)) for movable coordinates. Compute:

- factor consistency q=M' w-lambda/gamma, its infinity norm, and the code's
  own tolerance `1e-13*(1+max(abs(lambda))/gamma)`;
- normalized hedge error and its original `64*eps*(abs(bn)'cap)` tolerance;
- primal objective P and dual upper expression U at the exact scalar maximizer;
- gap U-P, checked independently against
  `gamma/2*||q||^2 - nu*(bn'w)`;
- post-solve gross multiplier, cap feasibility, and model risk on final holdings.

Report exact tolerance violations even if economically tiny. Use absolute
duality gap >1e-10 as a separately declared value-accuracy flag on a hedge-feasible
book; numerical negative gaps at rounding scale are reported, not hidden.
No convergence tolerance, solver iteration count or policy is altered.

## Prespecified beta-feature and risk descriptions

Capture the forecast's existing 27-column solved coefficients and prior betas
without an extra regression or a changed forecast. At each executed target:

- net dollar exposure and gross exposure;
- coefficient and direct forecast contribution of the beta column;
- algebraic decomposition into the net-dollar term, difference between the
  prediction and hedge beta estimates, and centered clipping correction;
- remaining characteristics' contribution to the forecast objective.

This is attribution of a forecast, not a realized alpha-P&L decomposition. Joint
refitting of the other 26 coefficients remains a separate unmeasured effect.

Record predicted specific and unscaled factor second moments on final holdings.
Align each prediction at the previous close with the next actually scored return;
report mean realized squared gross return against the model's predicted second
moment, in the full run and the original stages. The same estimated beta hedge
makes this book approximately market-residual in the model. This is descriptive
risk calibration for the existing chosen positions, not a new strategy or a
selection criterion. No threshold is retrofitted to choose phi.

## Artifacts

Retain this plan, harness, source/input hashes, exact rerun commands, stdout,
stderr, unrounded daily ledgers and diagnostics, and final metric summaries.
Large target/held arrays may stay as reproducible local outputs with hashes
rather than being added to git. Report every executed, failed and unexecuted
check accurately; the now-exposed historical periods remain exploratory for V2.
