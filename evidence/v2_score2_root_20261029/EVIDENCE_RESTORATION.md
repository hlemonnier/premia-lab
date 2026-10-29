# Wave 2 evidence: preservation and reproduction

29 October 2026. This is storage/reproduction documentation, not a new research
policy or an additional performance evaluation.

## What is preserved

Every source file, written specification, release, review, result, log and
failure record is retained. Seven main actual daily ledgers remain directly
readable CSV files. Other CSV ledgers and all NPY outputs of at most 1 MiB are
preserved byte for byte in deterministic ZIP archives under `publication/`.
The archive manifest records every original repository-relative path, byte
count, SHA256 and storage destination. ZIP CRC checks and exact decompression
comparisons are performed before publication. Packaging does not alter policy
code, recorded positions, economic values, decisions or thresholds.

The selection covers declared research sources and outputs. Interpreter caches
and incidental environment temporary entries are excluded. An original broad
run artifact manifest may also mention such incidental entries; that original
manifest is retained unchanged. The input/source and array manifests identify
the declared reproducible workflow, and `publication/manifest.json` identifies
the material actually preserved or designated for regeneration.

NPY files larger than 1 MiB are reproducible research intermediates. Their
contents are **not in Git**. Their exact original identities, array shapes and
execution commands are retained. This includes full forecasts, large position
histories and the tiled runtime characteristic panel. Running a saved-target
audit requires restoring the relevant omitted arrays first. The original
input CSVs are not duplicated into the research publication.

## Restore archived outputs

From the repository root, use the archives matching:

```text
evidence/v2_score2_root_20261029/publication/*.zip
```

Member names already include their original repository-relative directories.
Check each member against `publication/manifest.json`. If a destination exists,
require its SHA256 to agree before replacing it; retain differing local work.
Extract into the repository root. Verify the extracted hashes against the
manifest. No downloaded or newly executed policy is involved in this step.

## Original inputs and executable snapshot

The original data directory supplied to `--data` must contain these unchanged
files:

| File | SHA256 |
|---|---|
| returns.csv | `6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d` |
| characteristics.csv | `46b9df20aebb324bd0026090d54f04bd6835283881dd73e728e90f16a5279a08` |
| costs.csv | `ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186` |
| score.py | `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96` |

The root saved-target readback uses `score.py` from this data directory for its
identity check. The unchanged scorer itself is also preserved in the executable
snapshot. Pass this portable snapshot path explicitly:

```text
--snapshot evidence/v2_score2_execution_20261029/actual_001/source
```

It contains the pinned ce3 `handoff_v2/strategy.py`, the three files in
`handoff_v2/model_v2/`, and `source/Quant Research Take-Home/score.py`. No external
`v2-followup-snapshot` checkout is needed. These historical research copies are
not replacements for Claude's current production safeguards.

M1 additionally imports the prior-wave
`evidence/v2_score_joint_20261028/{e2e,joint,overlay,prototype}.py` and reads its
`actual_001/joint_F2_VTvol/daily.csv`. These files are inherited through commit
`37b323e00f2e79d0a5d799a3fdab6946ad04c2e8`. F3 reads
`evidence/v2_followup_review_20261028/replay_V2_002/input_hashes.json`; root
verified this file remotely at the wave-2 plan commit, blob SHA
`9e2a8cc6905b3aee1f1465aba90ead74ae0c64d3`. It records the three input CSV hashes
listed above.

## Regenerate omitted arrays without replacing original evidence

Follow each owner's `EXECUTION.md` and recorded `invocation.json`, preserving
source/release identities, policy settings and original input hashes. Use a
**new, empty `--out` directory**: the historical output directories already
exist and the harnesses deliberately refuse to overwrite them. Set the three
thread variables to one and select one available CPU as in the original commands.

Restore the E2 actual reference first. The joint harness compares against
`evidence/v2_score2_execution_20261029/actual_001/E2`; regenerate the execution
workflow into a new output directory, verify the omitted forecast and target
array hashes against the original `verification.json`, then copy only matching
omitted arrays into that original reference directory. The joint replay can then
run into its own new output directory using the unchanged root release.

Do not replace the original `rows.npy`, CSV, JSON, manifests or logs with rerun
versions. Execution times naturally change on a rerun, so full timing-containing
rows will not reproduce byte for byte. The preserved original economic columns
and deterministic target/forecast arrays are the relevant comparisons, at the
original declared tolerances. A difference must be investigated and retained;
do not update the original expected hash to make it pass.

Root's independent readback command is recorded in
`READBACK_EXECUTION.md`. It does not execute or refit a policy. After the relevant
arrays have been restored, use a new output path for its reconstruction too.

The selected joint runtime workflow reads original CSVs and constructs its own
25,200-row repeated panel. It does not need the optional NumPy cache used by the
unused standalone execution `runtime.py`. Repeated data test computation and
state stability, not future investment performance.
