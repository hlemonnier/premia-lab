# Independent review of the selected C09 package

27 October 2026, Europe/Paris. Reviewed by the lead before its first green clean-folder workflow and before audit access. Selection record: `research/VALIDATION_SELECTION.json`, SHA256 `941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa`.

The package contains exactly `strategy.py`, an empty `model/__init__.py`, and the original `model/strategy.py` and `model/portfolio.py`. The two helper hashes equal the historical C09 engine bytes. AST-based inspection of the literal `_FROZEN_CONFIG` found exact dictionary equality with the selected original JSON configuration, SHA256 `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`.

The only executable additions are a static package import, the exact literal configuration, one call to the existing configure function, and direct forecast/rebalance aliases. No learner, optimizer, feature, parameter, information clock, cost convention or signature changes. The required helper files and NumPy dependency are declared in the note.

The approximately one-page note accurately distinguishes discovery/validation observations from claims about the unknown simulator. It reports the actual fixed-rule validation selection, causal clock, 1,008-day learning half-life, full-fee evaluation, estimated-beta hedge and proportional gross-cap approximation. It states the recorded human contributions and AI work without inventing personal implementation or an independent human discovery. Remaining stationarity, adaptation, covariance, beta, cost and tail risks are explicit. The note contains no audit result and must remain unchanged for audit.

Before execution, the reviewer requested one documentation-only clarification: replace “paired discovery criterion” with “fixed parent-comparison criterion.” The C12 exclusion was a predeclared point-estimate comparison, not a significant paired-test rejection. The reviewed resulting entry-point hash is `7f15248160efd09e65d7dcf4d79cb1c5c4897d87641f2c2057f8566c7de7d946`. Executable statements and all helper bytes are unchanged. The earlier note and amendment are preserved in the implementation packet.

The lead authorized the prospective discovery clean-folder workflow only after confirming that exact amended entry-point hash, using the canonical C09 discovery reproduction and discovery cache on CPU 7. A passing workflow and frozen package manifest are still necessary before audit admission. No audit access, alternative policy or external submission is authorized by this review.
