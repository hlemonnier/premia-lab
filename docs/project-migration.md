# Project reorganization record

30 October 2026. The recruitment-oriented working repository has been reorganized as **Premia Lab**, a research workbench. This is a repository/documentation change, not a new numerical model or performance experiment.

## Completed

- Replaced the submission-focused README with a project overview, architecture, quick start, research findings and limitations.
- Added an independently generated public demonstration and black-box verification workflows.
- Retained the nine N0 numerical modules and pinned dependencies unchanged. The compatibility entry point retains the same executable structure.
- Imported 38 recorded branch snapshots into an indexed archive: 42,185 branch/path mappings, 2,920 unique published text/source objects and 1,407 explicit per-snapshot exclusions.
- Preserved distinct versions and negative findings. Original private source commits remain reachable through the private consolidation commit's parents.
- Removed the 37 non-main branch references only after the archive was generated and the original heads were preserved. Only `main` remains.

## Storage verification

The first archive commit omitted some ignored log objects and Git normalized some CSV line endings. A subsequent non-destructive repair restored 604 already-indexed objects from their preserved source blobs. The staged-byte check then verified all 2,920 objects against the archive's recorded identities. See `research/ARCHIVE_STORAGE_REPAIR.json` and `research/ARCHIVE_STORAGE_CHECK.json`.

The runtime itself was not modified. Four public end-to-end test groups pass locally, including the deliberate missing/normalized archive fixture and the actual-policy prefix/future-mutation demonstration. Hosted checks are maintained in `.github/workflows/ci.yml`; their actual run status is authoritative. This reorganization does not claim a new historical backtest, independent reviewer or economic validation.

## Not performed

The existing GitHub repository is still named `continual-research-takehome` and remains private. The connected content/git tools did not expose repository-renaming or visibility administration. No public destination has been created by this task.

The old history contains externally supplied task material, so switching that history to public is not the recommended publication route. `tools/publish_public.py` prepares a **new, clean public `premia-lab` repository** from the reviewed current files, without copying the private Git history. Its default is a no-write preview; actual creation requires `--publish` and the operator's authenticated GitHub CLI. It has not been executed with `--publish` here.

The public archive excludes raw benchmark inputs, the external scorer/specification, private correspondence, detected credentials, binary/generated assets and other explicitly excluded material. Automated filtering is not a blanket copyright or security certification. A software license was not silently granted during the reorganization.
