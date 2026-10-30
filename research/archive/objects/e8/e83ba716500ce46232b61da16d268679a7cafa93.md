# Independent review of Claude's V3 integration

29 October 2026, Europe/Paris. Root scope before any independent policy replay.

## Pinned work and authority

The user requests the senior quant review of Claude's pushed implementation.
Review `v2-factor-risk` at `978824d4b6140c43566ebd61a3ee8157f4080e35`, compared
with the prior hardened production head
`c51d31fe63c68255f2220935a8bc615c62bd1d0c`. The selected research policy is the
published F2 -> E2 -> M1 at research commit
`9e56aa755d20c5876485188f4c50ce959f6d63f3`, score 1.444733300556666.

This is fidelity and interpretation work. No new forecast, risk parameter,
market weight, alternative strategy, cost schedule or scoring convention is
introduced. All historical data are already exposed development data. The user
prioritizes the official future net Sharpe subject to the original brief.
No production file, external message or submission is changed by this review.

## Questions and bounded evidence

1. Inspect the actual V3 source for F2 clocks, three independent portfolios,
   costs, state resets, current hardened allocator wiring and final constraints.
2. Reconcile Claude's assertions with his committed specification, source and
   logs. Distinguish an unchanged-package reproduction from exact agreement with
   original research arrays, full-precision economics from rounded CLI output,
   and a reported runtime pass from recorded one-core/source/input provenance.
3. Where that chain is incomplete, replay the unchanged reference and package
   under a prospective whole-workflow verification wrapper, reviewed by another
   researcher before execution. Reuse existing temporal cutpoints and runtime
   code; do not expand the policy search. Record source/input/environment hashes,
   exact invocations, outputs, failures and declared numerical comparisons.
4. Audit the sleeve interpretation against the original brief. Derive explicitly
   labeled fixed-policy market-mean sensitivities using saved ledgers; do not
   describe mean subtraction as a rerun of an altered simulated market.
5. Produce a concrete integration decision and precise documentation corrections.
   Preserve any exception to original comparison requirements rather than
   silently reclassifying it as a pass.

## Reference availability limitation

The original wave-2 large target arrays were designated reproducible intermediates
and omitted from Git, while their hashes, policy sources and daily ledgers were
published. Those original large arrays are no longer present in this executor.
Consequently a fresh source-bound rerun can establish same-environment reference
fidelity and agreement with published economics, but cannot directly measure
maximum per-stock differences from the unavailable original arrays. Tiny return
differences do not imply small per-stock differences. This boundary must remain
explicit even if all fresh comparisons pass. Fresh canonical winning arrays
will be preserved more durably for subsequent integration reviews.

## Ownership

- `v3_policy_audit`: source review and peer review of the new verification wrapper.
- `v3_evidence_audit`: existing-evidence review, prospective rerun wrapper and runs.
- `v3_market_challenge`: original-brief interpretation and saved-ledger arithmetic.
- Root: immutable snapshots, release, integrated judgment and publication.

The supported environment status tool and network-policy snapshot are unavailable
in this executor. GitHub connector reads/writes are used; no CLI credential or
TCP-access readiness is assumed. Source download copies are verified against Git
blob hashes before use. The first broad concurrent connector batch had a fetch
error; a smaller exact-ref batch completed and all 27 changed files were verified.
