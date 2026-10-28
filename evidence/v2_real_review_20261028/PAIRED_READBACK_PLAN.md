# Paired saved-ledger comparison: plan before calculation

28 October 2026. The V2 selected-candidate bootstrap output is absent from its
committed comparison file. After the two already specified unchanged-package
replays, compare their saved full-run daily net returns. This is a descriptive
comparison of the packaged V2 and C09, not an exact reconstruction of the
uncommitted interval for the unlevered research variant and not a fresh test.

- Inputs: the two `run_*_001/daily.csv` files from this review, exactly matching
  return indices 253 through 3778. Record SHA256 identities.
- Primary calculation: reproduce `research/v2/exploration/compare.py` conventions:
  63-observation moving blocks, 2,000 draws, seed 20261027, identical index draws
  for both strategies, mean/std(ddof=0)*sqrt(252), percentile interval [2.5,97.5].
  Its original upper-exclusive start `n-L` omits the final legal block. Preserve
  that version for fidelity; additionally report the corrected bound `n-L+1`.
- Fixed dependence sensitivity: also report corrected-bound results for block
  lengths 21 and 126, with seed reset to 20261027 for each. Never choose one
  interval as definitive because it gives a preferred conclusion.
- Calculate unrounded stage differences and net-return correlation directly.
  Label the fraction of bootstrap differences above zero as a resampling
  fraction, not a posterior probability or selection-corrected p-value.
- No model re-estimation, no adaptive draw count, no policy replay, no inference
  that resampling undoes full-sample model selection or nonstationarity.
- Expected: identical input indices and finite statistics; no numerical range
  is predeclared as a pass criterion. Preserve all four interval calculations,
  commands, source and output. Check the missing selected-V2 comparison record
  separately from whether the independently calculated interval is similar.
