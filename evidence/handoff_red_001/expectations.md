# Handoff engineering and clean-directory equivalence

**Prospective plan, 27 October 2026, Europe/Paris.** Written before the handoff wrapper or its verification controller. No selected wrapper is implemented by this document. Root review precedes implementation; the exact engine is chosen only by the already frozen protected-evaluation rule. This plan creates no new model, parameter choice, market exposure, or calendar schedule.

## Employer contract and intended deliverable

The original `source/Quant Research Take-Home/README.md`, sections “The shape of a strategy,” “Information and lookahead,” “What to hand in,” and “Running things,” requires a top-level `strategy.py` defining `rebalance`, permits `forecast` and helper files, and asks for a short top-of-file note explaining beliefs, construction, AI/human contributions, and long-run risks. The supplied scorer passes declared named arguments, runs the forecast once, and replays the serial book from an empty position at start 252. Preserve the original scorer and its cost/endpoint conventions. Its SHA-256 remains `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

Prepare a small `handoff/` directory containing:

- `strategy.py`: the required deployment entry point, the complete approximately one-page explanatory note, a literal copy of the selected original configuration, and a thin static delegation to the selected engine.
- `model/__init__.py`: empty, making the helper directory a regular Python package.
- The exact imported project source closure for the chosen engine, copied byte-for-byte under `model/`.

For C09, the imported closure is `strategy.py` and `portfolio.py`. For C06, it is `strategy_gls_factor.py`, `strategy_gls.py`, `gls_precision.py`, `strategy_factor.py`, `factor_portfolio.py`, `strategy.py`, and `portfolio.py`. The outer entry-point name does not replace the inner `model/strategy.py`; the package namespace prevents their collision. Existing helpers already select relative imports when loaded as a package. Do not rewrite those branches, flatten files, rename engine symbols, refactor numerics, or include unrelated candidate modules.

The handoff has no research cache, raw dataset, fitted binary, credentials, notebook, test framework, or external service dependency. Preserve its source/configuration manifest in the project evidence, outside the small handoff. A downloadable archive may contain exactly the handoff tree after verification; it must not copy private research/data files accidentally. No external submission or message is authorized.

## Wrapper contract

After root identifies the selected frozen candidate, use a static package import of that exact engine. At import time call the engine's existing `configure` once with a Python literal equal to the frozen original JSON configuration; the configuration is not loaded from an external file or selected by runtime data. Publish `forecast` and `rebalance` as direct aliases of the engine's existing functions so their declared argument names and behavior remain intact. A read-only-purpose configuration copy may be exposed as `CONFIG` for evidence inspection, but it must not affect decisions. No extra learner, state machine, execution policy, filesystem access, environment manipulation, or runtime parameter interface is added.

The reviewer must check that the literal requested configuration equals the selected JSON dictionary and that the actual configured engine state equals the canonical engine's recorded configuration. Extra defaults must not be guessed. The helper-file hashes must equal the concrete nominee manifest and original discovery identities. Every imported project module must resolve under the clean handoff's `model/` directory; accidental import of the research checkout or an unrelated installed `model` package fails the gate.

## Interpretation under the frozen research protocol

This is a deployment representation of one already selected complete policy. It does not count as another selectable candidate only if its engine bytes and configuration remain unchanged and the full E2E equality gates below pass. A different import namespace and a delegation layer are engineering changes with possible behavioral consequences; semantic equivalence is required, not assumed from their small size.

Build and verify the complete wrapper and note on discovery **after validation selection but before audit freeze/access**. Freeze the verified wrapper, package, configuration and evidence identities in the audit nomination record. The canonical selected engine then executes the single permitted audit; the unchanged handoff is replayed afterward as an exact reproducibility check of that same policy. No audit-driven model, configuration, wrapper decision logic, or candidate substitution is permitted. A discrepancy is a retained engineering failure to investigate, not permission to select another policy using audit results.

Write the full explanatory note before audit freeze using facts already supported at that point. The brief does not require audit statistics in the code note; put later audit results in the separate research report. This avoids changing executable-file bytes after the audit. Any necessary later editorial correction must be explicitly recorded as documentation-only and must not silently replace the frozen package or waive equivalence verification.

## Prospective verification: failure modes and construction order

The clean-directory workflow must detect missing helpers, accidental research-path imports, a `strategy` namespace collision, incorrect literal configuration, signature/argument loss, extra state or reset behavior, changed forecast values or dates, changed targets/held books/economics, input mutation, invalid target shape or arithmetic, omitted closing costs, and a final package differing from the one tested. It does not test a new predictive hypothesis.

1. Preserve this plan and root approval before controller implementation. Write one lean complete-workflow verifier, using the existing original-scorer instrumentation and evidence conventions rather than introducing a new framework or isolated unit suite.
2. Preserve an expected missing-wrapper run before implementing the wrapper. It must fail clearly with zero candidate/scorer workflows and retain its command, source/input identities, logs and construction order. No missing-file failure may be reported as a candidate pass.
3. Wait for root's explicit selected candidate/configuration identities. Copy the exact imported engine closure, create the empty package initializer, and write only the planned top-level wrapper and note. Independently review the package against this plan and frozen selection record before executing it.
4. Execute the complete discovery workflow from a fresh clean directory and a fresh interpreter using the unchanged original scorer. Only after it passes, freeze the entire package in the audit nomination. Preserve all failures and exact retries in separate evidence directories.
5. After the selected canonical engine's one permitted audit is complete, run the same frozen handoff in another fresh clean directory on the same full audit replay inputs, compare all outputs, and retain the reproducibility evidence. This is a same-policy rerun, not a second audit selection.

The verification source is written before the wrapper it covers. No postimplementation unit suite, new model scan, or extra holdout access is introduced.

## Clean-directory execution and exact expectations

The isolated directory contains only the handoff package and a byte-identical copy of the supplied scorer. Load input arrays from the explicitly authorized frozen input manifest. Keep project/research directories off the module search path; import only the local handoff and allowed installed numerical/standard-library dependencies. Record actual module paths and dependency versions. No live project module may satisfy a missing helper.

Use one pinned CPU, numerical-library threads set to one before import, fresh process state, and immutable source/config/input snapshots. Preserve canonical memory layout when loading/copying arrays: Fortran-contiguous returns, C-contiguous characteristics, unchanged costs. The scorer's candidate arguments remain the original names and shapes. Inputs are read-only; retained held-book copies detect mutation. The wrapper's aliased functions are invoked through the original scorer's declared-argument adapter and `run`, not through a hand-written replacement simulator.

### Discovery equivalence before audit freeze

Use exactly `[0,2016)` inputs, with the original empty book and start 252. Expected shapes/counts are:

| Output | Exact expectation |
|---|---|
| Forecast | `(2016,1000)`; one forecast invocation |
| Targets and supplied held books | `(1763,1000)`; earning indices 253–2015 |
| Full scorer economic rows | 1,762; indices 253–2014 |
| Original endpoint convention | Row 2015 return is not earned; the closing target's full cost is retained |

Require exact selected-original forecast, target and held-book `.npy` identities, and exact ordinary-Python-float parsed economic rows, excluding wall timing. The standard canonical discovery rerun supplies available array bytes and must itself reproduce the historical identities. Check shape/finiteness, unchanged caller inputs, stock/gross limits, one free opening, full drift-aware fees, and actual configured state. A tiny discrepancy still fails the **exact packaging-equivalence** claim; investigate and preserve it instead of enlarging the criterion or changing the candidate.

Record measured wrapper forecast/rebalance timing. The underlying selected engine's already completed 25,200-row runtime gate remains necessary. Exact function aliases add no separate optimizer or learner; do not substitute a discovery extrapolation for that executed century evidence.

### Complete audit replay equivalence after the canonical audit

Only after the root releases the selected audit and its canonical engine run completes, use the identical `[0,3780)` arrays and unchanged package. Run continuously from start 252. Require `(3780,1000)` forecasts, 3,527 targets/held books for earning indices 253–3779, and 3,526 raw scorer economic rows on `[253,3779)`. Compare **every** forecast, target, held book and economic row to the canonical selected-engine audit execution, not only the final audit score. Only the fixed mask `[3024,3779)` supplies the reported audit statistics: 755 observations.

Require exact `.npy` identities for the full arrays and exact full economic equality excluding timing. Recompute the selected audit metrics on that mask with unchanged population-standard-deviation Sharpe and centered net-market beta. Undefined ratios remain null with reasons. No restart at validation/audit boundaries, retuning, alternative model, or changed feature transformation is allowed. A wrapper replay must not access any additional market input beyond the authorized canonical audit replay.

## Evidence, final bytes and honest note

Each stage preserves setup, exact commands and fresh rerun destination, package/config/scorer/protocol/input hashes, source snapshots, environment/module paths, declared masks, expected versus actual outcomes, complete logs, timing records, full economic ledger and output-array identities. Evidence directories never overwrite earlier attempts. Large reproducible arrays may follow existing Git policy, but the record must not imply unavailable files remain present after a workspace reset.

Rehash the final handoff after clean verification and require equality with the package frozen for audit. If an archive is produced, inspect its exact member list and extracted file hashes against the tested manifest. Packaging cannot add an untested helper, change a newline in an engine file, or ship a different configuration. Keep the full internal evidence in the private project and the handoff itself small.

The top note should be concise, approximately one page, and distinguish:

- What the observed discovery/validation evidence supports, including negative nonlinear contrasts and remaining uncertainty; do not identify the unknown simulator mechanism as fact.
- The selected model, causal information clock, market hedge, full-cost treatment and main engineering choices.
- AI's actual work: research, implementation, experiment execution, reviews, evidence and packaging.
- The user's recorded contributions: reporting that he noticed the same broad early patterns; emphasizing overfit/lookahead control; requesting literature search, independent agents and evidence-driven progress. Do not claim he independently wrote code, reproduced calculations, or discovered a mechanism unless he actually supplies that contribution.
- Long-run risks: changing effects, adaptation lag, risk/beta estimation error, omitted response or covariance structure, cost drag and tail/numerical events beyond tested histories. Finite causal checks and selected development performance do not certify no overfit or future profitability.

The note must say that the `model/` helpers are required. Final delivery consists of the tested `strategy.py` and that helper package, with the private project holding the evidence. Sending the submission remains a separate user-authorized external action.
