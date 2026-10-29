# V3 policy and hardened-engine review

29 October 2026, Europe/Paris. Independent reviewer: `v3_policy_audit`.
Reviewed production head: `978824d4b6140c43566ebd61a3ee8157f4080e35`.
Prior hardened engine: `c51d31fe63c68255f2220935a8bc615c62bd1d0c`.

## Verdict and scope

**No demonstrated causal, state-isolation or selected-policy implementation defect
was found. No production code correction is required by this source review.**
The fixed F2 -> E2 -> M1 policy is implemented coherently, and the hardened
allocator and engine are exact copies of the prior production versions.

This conclusion comes from static reading of the pinned source and interpretation
of the existing verification workflows. I did not execute a policy, add a model,
write retrospective unit tests, change a parameter or alter production files.
It is not an independent numerical reproduction or an unconditional approval of
every integration-evidence claim. The separate numerical-reference/provenance
review remains relevant to overall admission.

Exact fetched source bytes and their Git/SHA256 identities are preserved in
[source_manifest.json](../evidence/v3_policy_audit_20261029/source_manifest.json).
The review scope is retained in
[SCOPE.md](../evidence/v3_policy_audit_20261029/SCOPE.md).

## Findings requiring precise reporting

### V3-P01 — Failure-path evidence covers the copied solver and engine, with narrower coverage of the new policy wrapper

**Priority: evidence qualification; not a demonstrated selected-policy bug.**

`verification/v3_failure_paths.py:13` aliases the V2 engine/allocator imports to
the shipped V3 modules and `:19` executes the existing V2 failure harness.
That inherited harness calls `allocate_factor` directly for forced fallback
and edge cases (`verification/v2_failure_paths.py:41`), and calls
`engine.rebalance` for its synthetic whole-scorer path (`:57`).

The actual V3 strategy uses `Book.rebalance` at `handoff_v3/model_v3/policy.py:70`
and the outer `ScorePolicy.rebalance` at `:114`. The existing failure-path log
therefore does not itself demonstrate a forced fallback traversing this new
entire wrapper path. It correctly demonstrates behavior of the shipped,
byte-identical allocator and engine files. The normal actual integration
workflow does traverse the new wrapper, and its recorded 7,054 solves all have
status `ok`.

Static inspection confirms that `Book.rebalance` calls the hardened allocator
at `policy.py:81`, preserves its per-book warm state and information record,
then calls the current final-book check at `:87`. The outer final-book check
is present at `:147`. No missing call or changed selected-path failure behavior
was found. The report should keep this distinction rather than describing the
inherited harness as exhaustive failure coverage of every new wrapper branch.

### V3-P02 — The runtime script's pass field is narrower than a complete operational provenance certificate

**Priority: evidence qualification; numerical/runtime reviewer to close.**

`verification/v3_runtime_check.py` reports mean/p99/max timings, forecast time,
observed certificate-status set and minimum one-plus-gross-return. Its final
`pass` expression checks only mean rebalance below 100 ms and forecast below
3,600 seconds. The script's source does not record or assert CPU affinity,
thread environment, exact certificate count, or expected row count.

The committed log reports the expected 24,946 scored rows and only `ok` statuses.
The original scorer rejects a ruined path, and the package checks final books
at every decision. Thus the log is useful evidence. The one-CPU/thread setting
must come from the actual invocation/environment evidence, not from this pass
boolean alone. This review does not independently verify Claude's measured
runtime configuration or turn the source omission into a claim of a timing
failure. Root's separate evidence review determines whether the existing record
or a bounded, prospectively specified replay closes that point.

## Source conclusions

### Forecast information clock and fixed F2 definition

`policy.py:30` obtains trailing betas from `engine.causal_betas`, whose contract
and implementation at `engine.py:77` use returns strictly before each beta row.
Cross-sectional standardization at `engine.py:55` canonicalizes the supplied
panel before reductions; it does not standardize against future panels.

At forecast row t, `policy.py:44` sets the newest matured design index to t-2.
Its target at `:47` is the residual return at t-1. Prediction at `:58` uses the
published X[t-1] design and beta[t]. All statistical moments involved in that
row therefore depend only on data before t. Computing the residual array for
the entire input is not itself lookahead: only the matured element is consumed.

The two complete 27-column fits use half-lives 1008 and 252. Ridge and the
126-pair warm-up come from the frozen configuration. Only the first 13 linear
coefficients are averaged at `policy.py:57`; the squared-characteristic and
beta coefficients remain slow. This is the selected F2 policy, rather than
the unused learned whole-forecast adaptive mode still present in the copied
engine module.

The stored `forecast_output` is returned to the scorer. Rebalance checks its
existence but does not inspect future rows of that array. The scorer supplies
the appropriate already-causal row as `expected_returns`.

### State isolation, timing and resets

At `policy.py:103`, each forecast invocation constructs distinct virtual and
inner `Book` instances. Each owns a copied configuration, target, `_RiskState`
and optimizer warm dictionary. The controller sums, masses, earned count,
outer target, previous-day marker, certificates and multiplier are reset in
the same session initializer.

The risk state advances only while its next unpublished-to-the-state index
is below the currently supplied history length (`policy.py:75`). Its absorbed
return and design use the inherited `engine.py:224` clock. Dynamic gamma and
stock caps are local allocation settings; changing them does not recreate or
double-advance the risk state.

The virtual and inner gross returns are separately computed at `policy.py:125`
and `:126`. Each book drifts with its own denominator at `:129` and `:130`.
No outer combined positions are substituted into either internal book.

The first opening decision has no preceding earned observation. The controller
updates only once `last_day` is set (`policy.py:131`). After 63 earned returns,
the normalized EW63/EW1008 second moments determine the clipped multiplier.
Thus the opening observation is excluded and the original first-active-clock
convention is preserved. Subsequent calls must advance exactly one history row
at a time; a new `forecast()` is the supported session reset.

### Allocation, netting and outer target

At `policy.py:141`, the virtual book retains gamma 200 and cap 0.05. At `:142`,
E2 uses gamma 200/a and cap 0.05*a around its independently drifted inner book.
Both use the raw-beta zero target, 26-column risk basis and the fixed cost
horizon. The constructor rejects the incompatible beta-shrinkage, beta-risk-
column, matched-diagonal and nonzero-target variants.

The market sleeve is added at `policy.py:144`, after the inner target is chosen,
and only the combined target is proportionally reduced when gross exceeds 5.
The resulting stock bound is 0.10 + 0.05/N for the shipped fixed sleeve. The
outer reduction does not overwrite the inner or virtual targets.

The `held_positions` argument from the scorer is intentionally not used by this
fixed outer composition: the inner optimization needs its own drifted holdings,
and the final outer target is completely determined by that inner target plus
the fixed sleeve. The original scorer prices actual combined trades against
its own actual held positions. The package does not add virtual fees to actual
fees or fabricate a free index return. This remains separate-book execution,
not a joint optimizer of final netted transaction costs.

### Hardened safeguards are preserved

The copied engine and allocator are byte-identical to c51:

| Source | SHA256 |
|---|---|
| `handoff_v3/model_v3/engine.py` | `c134317d82effbf557481e7007e110a3209658d246a75a2257e856dd7047eb26` |
| `handoff_v3/model_v3/allocator.py` | `b9d855b319beb76b4b6f7009e92181c5fef854be93b34cea7cbafa2c7c459f3b` |
| `handoff_v3/model_v3/policy.py` | `58cec7e9a2665a1149766ce89e5a7c97ccfb03cf9d21c2f9f980240fd5d218e6` |
| `handoff_v3/strategy.py` | `715f8fb607fbbad6d078c3debfeb8dc3f7de12c674df14e4f4a05ed179649d59` |

The allocator retains resumed solve, cold restart, certified matched-diagonal
fallback and an exception if even that cannot be certified. The new Book
entrypoint calls the inherited final check with its dynamic stock cap and zero
raw-beta target. `ScorePolicy` checks the actual combined bound as well.

As already disclosed in the research packet, the solver certificate applies
to its solved stock-cap/beta optimization problem. The later proportional
gross reduction is a feasibility operation; it does not establish global
optimality of a different explicit-gross-constrained objective. Fallback
certification likewise concerns the stated matched-diagonal fallback problem.

## Existing verification interpreted at its actual scope

The integration harness checks exact forecasts; bounded differences in all
three target streams and four economic columns; score difference; counts and
normal-path statuses; future replacement at zero-based cut points 600, 2000
and 3500; pure prefix histories; and cross-history restart. Its protected
indices are consistent with the scorer: forecast rows through the cut are
protected, and decisions strictly before the cut are protected. Runtime
timing columns are excluded from economic identity as intended.

The supplied JSON records exact same-environment agreement and normal-path
certification. This source review does not resolve the deviation between the
published original target hashes and Claude's regenerated reference, nor
independently authenticate the missing original array values. That bridge is
the separate numerical/provenance review's task.

No path to future outcomes or retrospective parameter adaptation was found
in the deployed source. This supports causal implementation under its declared
session contract. It does not prove absence of selection overfitting across
the already exposed research history.
