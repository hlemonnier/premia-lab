# Exact V3 actual-sample evidence preservation

29 October 2026. This is evidence packaging, not an economic experiment.
No strategy or scorer is executed and no live replay output is modified.

## Inputs and release

The only permitted input is the successful, immutable actual-sample replay
packet whose `result.json` SHA256 is
`8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66`.
It contains the recovered original forecast and all three original target
streams, along with the independently replayed package evidence. Root must
review this specification and `archive.py` before authorizing a build.

The build requires a release JSON containing `allow: "build"`,
`archive_script_sha256`, `archive_spec_sha256`, `replay_result_sha256`, and the
absolute `output_directory`. The first two identities must match the reviewed
files; the result identity must match the successful input packet. Output must
be a new directory inside `evidence/v3_archive_20261029/`. No publication or
economic replay is authorized by this specification.

## Exact contents

Preserve both research and package copies of these seven saved arrays:
forecast, final combined target stream, inner target stream, virtual target
stream, decision indices, full scorer rows including timing, and controller
trace. Also preserve each book's exact certificate JSON, array manifest,
summary and daily CSV, plus the parent replay result and invocation record.
Array file hashes must agree with the successful replay's manifest before
packaging. Record its existing raw-array hash, shape and dtype without
regenerating an array or rewriting an NPY header.

Deduplicate only identical complete file SHA256 values. Every original relative
path remains an explicit alias of its exact content object, including when
research and package arrays match. Differences in certificate metadata or
timing rows therefore remain preserved. Runtime's large tiled forecast is
excluded: it is regenerable and is not the actual-sample winner evidence.

## Archive format and readback

Use a single USTAR stream whose regular-file members are sorted by SHA256 and
named `objects/<sha256>`. All tar times, owners and group IDs are zero; modes
are 0644 and owner/group names are empty. Compress with gzip level 9, timestamp
zero and an empty gzip filename. This removes source mtimes, paths and clock
time from archive generation. Identical input files and compressor
implementation produce identical compressed bytes; the recorded final digest
is authoritative across compressor versions.

Split the compressed stream consecutively into binary parts of at most
2,097,152 bytes. Persist each part's size and SHA256, the concatenated archive's
size and SHA256, the object inventory and all original path aliases in a
canonical sorted-key JSON manifest. Record the manifest's own SHA256 separately.
Retain the exact build utility, this specification and root's release alongside
the parts. The temporary unsplit archive is deleted only after successful
readback of all part hashes, the concatenation hash and every decompressed
object's exact bytes. Recheck the original input files after packing. Any
failure leaves partial output and a traceback; there is no automatic retry.

## Restoration

`archive.py verify --packet PACKET` verifies the manifest checksum, every part,
the concatenated compressed bytes and every expected regular tar member.
`archive.py restore --packet PACKET --destination NEW_DIRECTORY` additionally
reconstructs every original relative alias from the verified exact objects.
An optional `--manifest-sha256` provides an independently trusted manifest
identity; checksums provide integrity, not an independent authentication source.

Restore refuses an existing destination and creates files exclusively. It
rejects absolute paths, empty/dot/parent components, backslashes, drive-like
paths, duplicate aliases, unrecognized or duplicate archive members, symlinks,
hardlinks and size/hash mismatches. It never uses `extractall` and never executes
archived content. After restoration, each alias is checked against its original
file SHA256. Partial output is retained on failure for diagnosis.

Verification is archive byte-identity readback only. No strategy, forecast,
economic variant, additional test suite or statistical inference is introduced.
