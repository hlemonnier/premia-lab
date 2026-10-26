# Discovery data preparation — before execution

Purpose: provide a fast, explicitly limited input for the first research phase. Read only rows [0,2016) for outcomes and characteristics, plus the static known cost vector. Source-file hashing may stream whole files as input identity checking; no later numeric outcome is used.

Expected source: the unchanged supplied archive identified in RESEARCH_PROTOCOL.json. The original source manifest from preflight002 is authoritative. Expected outputs: returns float64 (2016,1000); characteristics float64 (2016,1000,13); costs float64 (1000,); metadata with ordered names/day labels and hashes.

Failure modes/expected behavior: modified or missing source -> stop; wrong stock/feature/day order -> stop; unexpected prefix row count -> stop; nonfinite values or negative costs -> stop; malformed/wrong-sized cache -> never mark ready. Do not sort/reindex silently. No return statistics, correlations, scores, predictive models, or full-sample figures are part of this workflow.

Record source/code/output hashes, frozen runner, exact command, environment, setup, expectations, per-check outcomes and final status in evidence/data_preparation_001. Write a running status before numeric processing and preserve errors. Cache data is derived and excluded from Git; the evidence and complete regeneration script are committed. Agents must wait for a ready metadata file before using the cache.
