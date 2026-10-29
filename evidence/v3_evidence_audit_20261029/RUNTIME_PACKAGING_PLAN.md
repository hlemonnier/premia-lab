# Runtime evidence packaging

29 October 2026, Europe/Paris. Root requested this packaging before completion of
the released runtime run. It preserves evidence only; it does not execute or
change a policy, recalculate any performance number, or add a numerical test.

After `runtime_001/result.json` exists and reports the authorized runtime mode
passed, preserve the full certificate JSON and four small NPY files: scored
rows and the final outer, inner and virtual vectors. Write deterministic gzip
copies into a new sibling directory, leaving the completed runtime packet
unchanged. Retain original and compressed byte sizes/SHA256 values and stream
each decompressed file back through SHA256 to verify exact byte restoration.
For the arrays, require original file identity to match the completed runtime
result before compression. Record the result JSON identity and the packaging
script/plan identities in a separate manifest.

The full 25,200-row runtime forecast remains captured locally with its file and
raw-array identities in the original runtime packet. This packaging does not
claim to archive that large forecast. It is explicitly regenerable from the
frozen unchanged runtime workflow, source/input bindings and release. The
actual-sample canonical forecast and three complete target streams are being
archived separately by root; this choice concerns repeated-input runtime
evidence only.

No input, original result, completed array, source file or frozen gate is
modified. A failed gzip/readback check leaves its partial output and propagates
the failure; no automatic deletion or retry occurs. This is lossless artifact
verification, not another strategy run.
