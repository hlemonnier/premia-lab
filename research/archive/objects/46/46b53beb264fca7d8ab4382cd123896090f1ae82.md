# Reproduce the fixed parallel batch

The coordinator branch contains all five modules. Each model-family branch contains its own module and the same common runner/checker. Root strategy.py remains the selected GLS reference, NOT a newly promoted experiment. Use the original private take-home folder and a NEW work directory. Do not reuse caches across datasets, source changes or library versions; the convenience cache loader does not automatically certify provenance.

Recorded environment: Python3.13.5; numpy2.3.5, scipy1.17.0, scikit-learn1.8.0, pandas2.2.3. Numerical threads are capped at1. Memory quota was4GiB; at most two simultaneous market jobs. The complete original scorer is used, unchanged.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export SOURCE='/absolute/path/Quant Research Take-Home'
export WORK='/absolute/path/fresh-parallel10-work'
python research/parallel10/run.py --source "$SOURCE" --work "$WORK" --prepare
# Coordinator: all ten jobs. Family branch: use ONLY its two mode names.
printf '%s\n' N N0 V V0 R R0 M M0 C C0 | xargs -P2 -n1 sh -c '
  m="$1"
  mkdir -p "$WORK/logs"
  python research/parallel10/e2e.py --source "$SOURCE" --work "$WORK" --model "$m" --mode synthetic > "$WORK/logs/${m}_synthetic.log" 2>&1 &&
  python research/parallel10/run.py --source "$SOURCE" --work "$WORK" --model "$m" > "$WORK/logs/${m}_market.log" 2>&1
' sh
# Stop and inspect failures. Do not silently omit missing/failed modes.
python research/parallel10/assess.py --work "$WORK"
printf '%s\n' N V R M C N0 | xargs -P2 -n1 sh -c '
  python research/parallel10/e2e.py --source "$SOURCE" --work "$WORK" --model "$1" --mode market > "$WORK/logs/${1}_actual_E2E.log" 2>&1
' sh
python research/parallel10/injection_e2e.py --source "$SOURCE" --work "$WORK"
```

`--prepare` always enforces the selected GLS Sharpe baseline. Its optional comparison to an archived rows.npy uses the original session path; it is skipped, not claimed passed, when that path is absent. Compare the supplied baseline rows manually when reproducing on another host. The evidence package includes them. Main/input Git/SHA identities must be checked separately from a mere score match.

The full batch assessment requires all ten result folders. On an individual family branch, run its primary and control only; use the archived complete assessment for the other families. The factory lazily imports each family, so absent families do not affect the selected pair. Every candidate forecast can also reconstruct its inputs independently using `--uncached`; no production strategy reads shared research caches.

Output: complete original-scorer daily cashflows, forecast and target arrays, parameter/graph/mode records, fit/runtime summaries and E2E receipts. All results, including failed controls, are retained. Large arrays and original CSVs are not redistributed; hashes and commands let them be regenerated. Recorded queue scripts in the evidence archive preserve the exact session launch commands; the shell above is a portable equivalent, not a claim it was the exact launcher used.

The original constructed tests predate model implementation. Supplemental activation/timing/direction checks and the pre-score eligible-link fix are documented in PRE_SCORE_NOTES.md and the report. The initial missing-module failure and earlier N/N0 receipts are retained. A new pass never rewrites an old failure.

No primary qualifies for the registered extra no-sleeve/double-fee replays. No combined model, century test, separate reviewer sign-off or main promotion is part of this batch. N0 is an interesting control, not an automatically selected release.
