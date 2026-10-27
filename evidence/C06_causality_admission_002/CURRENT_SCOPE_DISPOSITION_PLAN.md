# Separate disposition of current-run causality and historical byte identity

27 October 2026, Europe/Paris. This reporting contract is written before the new saved-output reporter executes. Root approved this separate disposition after the original combined reporter failed; it does not replace that failed result.

## Observed issue and preserved failure

All39 original causality workers completed and their unchanged controllers reported the protected-output comparisons passed. The combined reconciliation reporter then failed the historical forecast NPY SHA check before it reached the remaining scenario checks. That failure and original reporter remain in `evidence/C06_causality_reconciliation_001`. The historical exact forecast/target hash expectation is not retroactively labeled passed.

Read-only diagnosis found the current2016-row forecast identical to the first2016 rows of the new25200-row workload forecast, while both differ in SHA from the historical discovery output. Historical daily economic values differ by floating-point amounts within the already frozen `atol=1e-14, rtol=1e-12`; those magnitudes are not a new tolerance. A source/layout difference exists: original discovery returns are Fortran contiguous and the historical discovery runner preserves that map, whereas the causality worker explicitly copies returns to C order. This is a plausible numerical mechanism, not an established causal explanation or permission to blame BLAS without evidence.

## New report scope and expectations

Run a separate read-only reporter over the exact same completed39 worker packets. Preserve the original admission, source/config/input/scorer identities, actual scenario input hashes, exact masks/shapes, complete child-process records and direct protected-output comparisons. Every required current-run comparison must satisfy the original frozen tolerances; exact equality and maximum absolute errors are reported separately. No candidate is run or tuned, no new market interval is opened, and no numeric tolerance changes.

Historical forecast and target serialized SHA identities are reported as distinct PASS/FAIL observations and the original failed report is linked. Historical raw output arrays are not assumed present solely from a hash: until hash-identical originals are recovered or reproduced, elementwise historical forecast/target error is unavailable. Daily historical economic columns and net are directly compared with the same frozen tolerance and reported separately from bitwise identity. Current-run baseline identities across A/B/C must agree exactly.

If current-run invariants pass, the status is `EXECUTED_PASS_CURRENT_ENVIRONMENT_ONLY` with `original_combined_gate: FAILED_HISTORICAL_BYTE_IDENTITY`. That scoped result must not be summarized as an unqualified pass of the original combined gate. A current-run failure or unavailable comparison fails/incompletes this new scope. Finite causal tests still do not prove universal causality, absence of research overfitting, or alpha generalization.

The new reporter is derived from the preserved original reporter solely to keep the historical byte-identity observations separate and complete the previously unexecuted current-run checks. The prior report is never overwritten. Record exact commands, source hashes, logs and all outcomes.
