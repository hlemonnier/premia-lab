# Harness failure record

The expected missing-policy failure preceded sleeve.py, with the exact
preimplementation harness SHA256 in build_order.json.

The first implemented synthetic workflow, synthetic_001, ran through the checks
but could not serialize its final result because some check values were NumPy
booleans. It exited1 with TypeError, so its outcome is a failed workflow, not a
passing result. All its executed source copies, logs and atomic arrays remain.

The correction converts NumPy scalars with item() in JSON serialization and
prints the saved result rather than attempting another unsupported serialization.
No policy, fixture, assertion, tolerance or decision rule changed. The unchanged
sleeve will be rerun with the corrected harness into a new synthetic_002 folder.
The original preimplementation test ordering and the failed harness version are
preserved. No actual-market policy was scored during this correction.
