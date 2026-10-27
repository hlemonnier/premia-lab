# Independent review of the long-history fixture layout correction

**27 October 2026, Europe/Paris.** Reviewed before replacement execution. Controller SHA256: `9c7d5d520da50c8a118b6c3d00744886e548e71d9dbdacbad68b2b4dfc707a4e`. Compared the complete diff against the frozen controller in `evidence/C06_long_history_001/runner_used.py` and read the prospective `verification/INPUT_LAYOUT_CORRECTION_PLAN.md`.

The only code changes derive each source array's C/F memory order and record its shape/strides, identify the new cache recipe as preserving layout, and pass that source-derived `fortran_order` flag to NumPy's existing memory-mapped array creator. A vector that is both C and F contiguous remains in the ordinary representation. Costs are copied unchanged. The deterministic numeric tiling, source hashes, dimensions, dtype, child controls, scorer, candidate/configuration, original reference, tolerances and acceptance checks are unchanged.

The cache recipe now includes source layout, so an existing cache from the old default-C construction cannot silently pass the new recipe check. The prescribed new cache and evidence directories also preserve the original failed attempt. This is an input-fixture representation correction prompted by a concrete failed exact-reproduction assertion; it changes no model choice and introduces no isolated postimplementation test.

**Review decision:** approve the same complete C06 century E2E on CPU6 with `cache/long_history_25200_layout`, output `evidence/C06_long_history_002`, and the original historical C06 reference. Its forecast, target and held-book hashes and prefix economics remain binding. A source review cannot claim that those identities or the full runtime/path checks pass; the replacement execution must establish them.

This review covers the century controller diff only. The separate canonical-layout causality worker/profile correction requires its own source review and recorded execution. No protected validation or audit access is authorized by this review.
