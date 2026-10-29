# V3 integration (F2 → E2 → M1) — specification and frozen comparisons (written before the package)

29 October 2026. Implements `research/v2/SCORE2_IMPLEMENTATION_HANDOFF_20261029.md` (GPT wave 2)
as a new deployable package `handoff_v3/`, built on the current production engine
(`c51d31f`: session reset, contiguous panels, certified solve → recovery → cold restart →
certified diagonal fallback or raise, final-book checks). `handoff_v2/` stays unchanged
as the V2 reference. No research parameter is changed; this is fidelity work.

## Reference

An independent rerun of GPT's exact research code (pinned `ce3fe4e` engine, original scorer,
verified inputs), whose array hashes must equal GPT's published `array_manifest.json`
(forecast, targets, inner_targets, virtual_targets) before it is used as the reference.

## Package design

- `model_v3/engine.py`, `model_v3/allocator.py`: current production files, unchanged.
- `model_v3/policy.py`: the F2 forecast and three books as explicit state objects:
  virtual F2 book (γ 200, cap 0.05), inner E2 book (γ 200/a, cap 0.05·a, solved against its
  own drifted holdings), outer book = inner + 0.05/N, proportional reduction only if gross > 5.
  Each book owns its risk state and warm start; no module globals are shared between books.
  `forecast()` resets every book, controller moments and counts.
- Volatility controller: EW63 and EW1008 second moments of the virtual book's earned gross
  return (opening excluded); a = 1 until 63 earned observations, then
  clip(sqrt(max(q1008, 1e-12)/max(q63, 1e-12)), 0.5, 2).
- Final-book checks on every book with its own bound: virtual |w| ≤ 0.05, inner ≤ 0.05·a and
  raw-beta exposure 0, outer ≤ 0.10 + 0.05/N and gross ≤ 5; certified solves only.
- No saved arrays, no hard-coded paths, no research monkeypatching; NumPy and stdlib only.

## Frozen comparisons (`verification/v3_integration_checks.py`, nonzero exit on failure)

1. Forecast: identical decision indices; forecast values **exactly** equal to the reference.
2. Targets: max |difference| ≤ 1e-8 for the virtual, inner and outer streams.
3. Economics: max |difference| ≤ 1e-8 in each of gross return, fee, closing gross and market
   return (timing column excluded); |net Sharpe difference| ≤ 1e-8. All observed differences
   are recorded even when within tolerance.
4. Causality on the packaged entry point (exact identity, same input layout): inputs replaced
   from row c ∈ {600, 2000, 3500}: forecast rows ≤ c and all three target streams for decisions
   ≤ c − 1 identical; truncated history of length c identical on its range; cross-history restart
   (history A scored, then history B in the same process) identical to a fresh run of B.
5. Every solve certified (status in ok / ok_after_recovery / ok_after_cold_restart /
   fallback_diagonal), every final-book bound respected.
6. The allocator failure-path checks (`verification/v2_failure_paths.py`) still pass.

Separately: a 25,200-row, one-CPU runtime check (mean rebalance < 100 ms, forecast < 1 hour
per century) and a clean-folder run of `handoff_v3` with the unmodified `score.py`.
