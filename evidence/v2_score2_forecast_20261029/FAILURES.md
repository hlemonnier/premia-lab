# Preserved F3 research failures

## Expected missing-policy red

The prospectively written harness exited3 with
`EXPECTED_RED_MISSING_PROTOTYPE`, before prototype.py existed. Economic runs:0.
See preimplementation_record.json and expected_red_001/.

## synthetic_001: serialization, before F3 execution

The first implemented synthetic invocation completed the F2 zero-market
control but failed while writing its summary. The existing endpoint comparison
returned a NumPy boolean, which the JSON encoder rejected. No F3 case was run.
The scorer output, source snapshot, atomic arrays, CSVs and traceback remain
under synthetic_001/ and its adjacent logs.

The only harness correction casts this already-defined endpoint comparison to
Python bool. Its assertion,1e-12 tolerance, fixture and all policy sources are
unchanged. This is an evidence-serialization repair, not a new test, changed
acceptance rule or policy rescue. The original preimplementation harness hash
and expected-red evidence remain preserved. The same complete workflow is
rerun in a fresh synthetic_002 directory.
