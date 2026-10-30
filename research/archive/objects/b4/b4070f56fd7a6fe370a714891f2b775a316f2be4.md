# Independent pre-execution source review: F2 plus VTvol

28 October 2026, Europe/Paris. Reviewer: score_opportunity_audit.

**Accepted for the specified joint synthetic workflow. Actual execution remains
conditional on synthetic success and root's F2 causal/evidence disposition.**
This is source admission, not a numerical or runtime pass.

## Findings

The composition factory installs exactly the existing F2 forecast and wraps the
same engine in the unchanged volatility overlay at power0.5. Power0 is solely
the fixed-F2 control. The engine's own forecast and risk state reset at each
wrapper forecast. Reinstalling the F2 closure does not recursively call the old
forecast: the prototype calculates predictions directly from the engine's basis,
beta and configuration helpers.

The base virtual targets and gross returns are those of F2. Its own observed
returns update the overlay moments. Actual drift and costs remain the original
scorer's responsibility. The standalone F2 target hash must match the joint
virtual targets in independent readback; there is no old V2 risk stream inside
the new strategy.

The overlay and forecast dependency copies are byte-identical to the independently
reviewed originals. The E2E diff changes only the direct-reference forecast,
composition factory, copied source evidence, and single dynamic policy to test.
Existing full-scorer assertions and tolerances remain unchanged. The same
nontrivial fixture exercises startup, prefix/future invariance, session reset,
virtual invariance and independent actual fee/drift reconstruction.

The actual runner binds all four implementation/E2E dependencies to the passed
synthetic source copies, uses the unchanged scorer endpoint and old stage masks,
reproduces the standalone F2 control ledger, and compares the joint with all
three specified reference series. Its block bootstrap admits the last legal
start. The numerical improvement guard is1e-8 and there is no new significance
hurdle. Reference CSV parsing can introduce tiny roundoff, but the fixed1e-8
reproduction tolerance accommodates it and independent readback will use
round-trip parsing.

No extra candidate, parameter, target beta or future-dependent risk normalization
was introduced. All Python sources parse. The original F2 mixed-layout numerical
failures must remain distinct from canonical-path causality. The reported
truncated baseline-array artifact is an unresolved evidence issue at this review
checkpoint, not a reason to relabel its failed read as passed.

## Exact reviewed SHA256 identities

- `PLAN.md`: `91235882e00185e912a0a383dd2f32e1ca3b5af0f49a26cc7a83f162eb955b2e`.
- `joint.py`: `fcf6dd9a917299516bb3b5bee92f9488b0546f7bf3914f7a2289bfeb4c104b33`.
- `e2e.py`: `2a0ebbcdbcf14bc95975729b7699474b25f2a21f754ed5d7fb2b0ac3748cc9ba`.
- `overlay.py`: `f603bc4e2e9ae8df6d407c8ba1d64b13753fcec19fde8c295e815fe2f09ca1f8`.
- `prototype.py`: `7854b2f763ae1bcc716282b68791503fe29f83d0aebc64835d8d0d919c722719`.
- `run_joint.py`: `aef56c13068327c46c432c2f485c471fc333863f5ce3576eccafdd86b867ece4`.
