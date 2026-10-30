# Bounded volatility-overlay research pilot

See PLAN.md for the prospective policy and verification specification, SOURCE_REVIEW.md for independent source admission, commands.json for exact commands, and execution_record.json for successful run status.

The preimplementation harness failed as expected on the missing overlay module. All 38 synthetic E2E checks then passed. The unchanged-scorer actual replay scores are V2 1.242503, VTvol 1.277109 and VTvar 1.274191; all costs are included. The complete results and paired uncertainty are in actual_001/results.json. There is no additional window, clip, beta-target or refresh search.

The conditionally admitted F2 plus VTvol experiment lives separately in ../v2_score_joint_20261028/. Its PUBLICATION_README.md lists every synthetic output archive that must be included explicitly, even if an ordinary Git inventory ignores npz files.

Policy sources are frozen. Preserve original plans, pre-review files, failures and all observed outcomes. Actual runtime is instrumented; no century gate is claimed from this pilot.
