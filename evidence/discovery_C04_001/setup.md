# Setup

Restore the source archive named in REPRODUCE.md and prepare the verified discovery cache with tools/prepare_discovery.py. This run reads only cache/discovery numeric arrays. Use the package versions in environment.json. The rerun command uses frozen strategy and helper sources; it writes a new directory and refuses to overwrite evidence.

The large output arrays are reproducible from this command and identified in artifact_manifest.json. Candidate timings exclude logging and the optional risk diagnostic; official timings include the transparent adapter.
