# Independent source review: overlay pilot

28 October 2026, Europe/Paris. Reviewer: score_opportunity_audit.

Reviewed `PLAN.md`, `overlay.py`, `e2e.py`, and `run_pilot.py` before a working
overlay scoring run. This is a static scientific/accounting review; no numerical
outcome is certified by it.

## Mathematical and temporal disposition

The overlay implementation matches the two specified policies. The virtual
target earns the current published return and drifts using its own gross return;
the actual book drifts independently in the unchanged scorer. Current-close
virtual gross returns update normalized second moments before the next target.
The empty opening call does not update the moments or earned count. The first
eligible multiplier is at close315 for earning row316, after63 actual earning
observations. Floors, bounds, powers and gross cap match the prospective plan.

Actual fees use the change from actual drifted holdings to the scaled target,
including the single free opening and final scored close. Virtual fees remain
diagnostic. Zero estimated beta survives scalar scaling. The actual stock bound
can reach0.10; the original assignment permits that. Fixed multiplier1 reproduces
the unchanged V2 book by construction, with an executed equality check required.

Future-mutation and prefix comparison boundaries agree with the scorer's
endpoint. The power0 control and both dynamic policies must retain identical
virtual targets and forecasts. Session reset clears wrapper and engine state.
The paired bootstrap uses `integers(0,n-length+1)`, correctly admitting the last
legal block start. Stage masks and full score are the established ones.

## Requested corrections before actual pilot execution

1. Align `replacement_contender` with root's prospective numerical-equivalence
   rule: improvement must exceed1e-8, rather than any positive floating-point
   difference.
2. Bind the passed synthetic E2E result to the exact executed overlay and E2E
   source hashes, then compare those with current files before the actual run.
   Reading an arbitrary `all_passed` flag is insufficient source admission.
3. Preserve the existing mutated, prefix and repeated E2E cases with the same
   `save_run` mechanism, preferably also compressed forecast/target arrays.
   These cases currently produce comparison booleans but no independent saved
   outcome readback. This adds evidence persistence without changing a test,
   threshold, fixture or candidate. Preserve the original preimplementation
   harness/build-order identity alongside any evidence-only revised harness.

No economic or causal defect was found in the strategy transformation. The
source is accepted for the specified workflow conditional on those small
admission/evidence corrections. The original synthetic expectations must remain
unchanged, and failed runs must remain visible. No full-century or future-score
claim is supported by static review.

## Follow-up disposition

**ACCEPTED FOR THE SPECIFIED SYNTHETIC E2E AND CONDITIONAL ACTUAL PILOT.**

The reviewer inspected exact old/new diffs before any working scorer execution.
All three requested changes are present. `overlay.py` is byte-identical to the
first reviewed implementation. Existing E2E assertions and tolerances are
unchanged; the E2E revision only preserves additional outputs and identities.
The original files remain as `.pre_review` copies and the original missing-import
failure/build-order record remains available. All three Python files parse.

Reviewed current SHA256 identities:

- Overlay: `f603bc4e2e9ae8df6d407c8ba1d64b13753fcec19fde8c295e815fe2f09ca1f8`.
- E2E: `20886671b882437fe2afe34543d529fc38018422dcae2ddd4ef843b568f1ea79`.
- Actual pilot: `4b009b55a9e2406c5b5bdcca1ece7ec09df6b6834b9e0a8691ff756828e2368e`.

This accepts source admission only. Actual execution must follow a passing E2E
of those exact sources and retain any failure. No runtime or score outcome has
been inferred from this source review.
