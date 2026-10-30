# Restorable V3 actual-sample evidence

The packet preserves **24 original evidence files as exact byte aliases of 18
unique content objects**. Both research and deployed-package records include
the forecast, all three target streams, decision indices, complete scorer rows,
controller trace, certificates, manifests, summaries and daily CSVs. The replay
result and invocation are included. Equal files share one stored object;
restoration recreates every original relative filename and exact file bytes.

The source replay passed with result SHA256
`8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66`.
Its research and package forecast and all three target streams recovered the
original historical file and raw-array hashes exactly.

On the published branch, the large raw replay arrays are intentionally
represented by this split archive and its alias manifest. The 25,200-row runtime
forecast is excluded; it is regenerable from the separately preserved runtime
source and input identities.

## Restore

Run from the repository root. Choose a **new destination that does not exist**;
the utility refuses an existing destination and verifies every restored alias.

```sh
python evidence/v3_archive_20261029/packet/archive.py restore \
  --packet evidence/v3_archive_20261029/packet \
  --destination ../NEW_v3_replay_restored \
  --manifest-sha256 3e487e00a671834c6a7cd80d638e5326da8adcb7b8f5723e9cc62e9d54028a12
```

The trusted manifest SHA256 above binds the object inventory, original file
identities, aliases, archive digest and all part digests. The utility verifies
the parts and decompressed content before completing restoration. It never
executes the archived files.

## Completed build

The one authorized build ran on CPU 2. Its complete part, archive and object
readback passed, and all original replay-file hashes remained unchanged.

| Item | Value |
|---|---:|
| Original file bytes, including aliases | 234,303,620 |
| Unique exact object bytes | 119,217,340 |
| Compressed archive bytes | 110,586,119 |
| Git-safe parts | 53 |
| Largest part | 2,097,152 bytes |
| Final part | 1,534,215 bytes |

Concatenated archive SHA256:
`0c5f1165f1d3e011816e27b72270c9cff8289030f59f839d62565f8e99e1e882`.
Build-result SHA256:
`ce37a8b9b2df4e27e33632af85931a0ae74819e7d09878d4f08c155ea29c87b2`.

`packet/build_result.json` retains the readback outcome. The packet also retains
the reviewed utility, specification and root release. No strategy or scorer
was executed during packaging.
