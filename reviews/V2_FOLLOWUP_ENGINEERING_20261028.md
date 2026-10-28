# V2 follow-up engineering review

28 October 2026, Europe/Paris. Independently reviewed source:
[`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`](https://github.com/hlemonnier/continual-research-takehome/commit/ce3fe4e76271709422165d6f24e2fbecd9d0fe07).
Baseline source: `afed8d0cb017acda151c4ea262fc30db7568a4bb`.

## Verdict

The restart and characteristic-layout corrections address the previously
demonstrated defects. The original independent complete-scorer workflow now
reproduces the custom-start restart control and the characteristic-layout
control bit for bit. The affine beta-target extension has the correct dual,
gradient and primal–dual gap. The existing allocator architecture remains sound.

The new certificate is useful observability, but it is not yet an enforced
postcondition: after two unsuccessful passes, the allocator returns the
uncertified vector and the engine trades it. It also certifies the vector before
the engine's gross-cap scaling. Scaling preserves a zero beta equality, but it
does not preserve a nonzero beta target. These limitations should be fixed or
made explicit before claiming guaranteed exposure control over arbitrary future
runs. They do not, by themselves, invalidate the reported sample paths.

**Actual-path closure:** the coordinator subsequently replayed the latest V2,
B0 and B05 in fresh processes. This reviewer independently read every decision
and economic CSV row. All three runs have 3,527 certified decisions, no gross
scaling and final estimated-beta target errors below `6.69e-13`. The failure-path
limitations above did not occur and do not explain the corrected books' realized
beta offset. Section 9 records these results and the direct old/new V2 comparison.

No production strategy or scorer source was modified by this review. No new
unit tests were written. The newly executed workflow is the original independent
E2E workflow, reused unchanged after a prospective expectation plan.

## 1. Independent regression execution

The [prospective plan](../evidence/v2_followup_engineering_20261028/PLAN.md) fixes
the inputs, controls and outcomes before this execution. The runner is byte for
byte the same as `evidence/v2_causality_review_20261028/run_e2e.py` from the earlier
review. Ten fresh workers perform twelve complete original-scorer executions
on deterministic 340-row, 96-stock synthetic histories.

The [readback](../evidence/v2_followup_engineering_20261028/independent_readback.json)
checks all results rather than relying on the controller's exit code. All ten
workers exited zero, all saved forecast/position/economic-ledger arrays were
finite, all runs traded, all six future-change stimuli changed later forecasts
or positions, and the copied strategy/scorer sources remained unchanged.

**Twenty of twenty-one strict bitwise comparisons passed.** The restart fixes,
the Fortran-characteristic fix, ordinary future mutation, truncated prefix and
fresh repeat all passed. The one failed expectation is important to describe
accurately: with Fortran-layout **returns**, protected gross daily P&L differs
by at most `2.6020852139652106e-18` on 31 observations. Protected forecasts,
targets, fees, reported gross exposure and market-return fields remain bitwise
identical. The original scorer computes `positions @ all_returns[today]` on
the caller's array layout; this last-bit P&L discrepancy is outside the strategy
canonicalization. It is not evidence of future information changing decisions.

The expectation of bitwise economic ledgers across return layouts was therefore
too strong for the unchanged scorer. It is retained as a failed prospective
expectation, not silently converted into a pass. Do not alter the supplied scorer
to hide it. Separate exact decision invariance from economic agreement at a
declared floating-point tolerance when the scoring reduction itself changes
layout.

The unchanged old runner has a stale literal commit identifier in its generated
`environment.json`. The actual commit, all executed source hashes, runner hash,
plan hash and metadata qualification are in
[review_identity.json](../evidence/v2_followup_engineering_20261028/review_identity.json).
The literal runner was deliberately left unchanged. Exact command/environment,
stdout, stderr, process exits and raw comparison results are retained in the
evidence directory.

This run does not activate beta shrinkage: 340 rows are insufficient to complete
its first 252-plus-252-row calibration pair. The separate causal-beta reviewer
owns that flags-on complete-scorer exercise. The coordinator owns the actual
candidate ledger readback. Those results must not be attributed to this execution.

## 2. The two original fixes are appropriate for the declared interface

### Session lifecycle

[`engine.forecast`](https://github.com/hlemonnier/continual-research-takehome/blob/ce3fe4e76271709422165d6f24e2fbecd9d0fe07/handoff_v2/model_v2/engine.py#L125)
sets `_STATE = None` and clears the certificate list before computing the new
forecast. The supplied scorer calls forecast once at the beginning of each run,
so the old different-history/same-initial-length cache error is fixed for that
interface. The source explicitly declares an append-only history within a
session. A shortening history also rebuilds the risk state.

This is a defined lifecycle, not detection of arbitrary mutation of old rows in
the middle of a session. A direct `rebalance` caller that swaps histories without
a new forecast is outside that contract. That qualification is now explicit and
reasonable for the supplied scoring interface.

### Feature layout

[`basis`](https://github.com/hlemonnier/continual-research-takehome/blob/ce3fe4e76271709422165d6f24e2fbecd9d0fe07/handoff_v2/model_v2/engine.py#L53)
canonicalizes each two-dimensional feature panel to C-contiguous float64 before
centering, scaling, clipping and squaring. Forecast and risk construction share
this helper. It fixes the actual X-layout reduction discrepancy without forcing
a full century-sized characteristic tensor copy.

The independent old workflow verifies both forecast and position consequences,
not only a helper-array equality. The remaining R-layout last-bit scorer result
has the separate scope explained above.

## 3. The nonzero beta-target mathematics is correct

Let `M = B L`, `s_b = max(abs(b_i))` over movable stocks, `bn = b/s_b`, and
`c = beta_target/s_b`. The problem now imposes `bn'w = c`. The convex dual is

\[
g(\lambda,\nu)=\frac{\|\lambda\|^2}{2\gamma}+\nu c+
\sum_i\max_{|w_i|\leq cap_i}
\left[(\mu_i-M_i\lambda-\nu b_{n,i})w_i
-\frac{\gamma d_i}{2}w_i^2-\kappa_i|w_i-h_i|\right].
\]

Its beta gradient is `c - bn'w`. The beta-polishing root is `bn'w-c = 0`.
For the scalar-optimal vector returned at the final multipliers,

\[
g-P=\frac{\gamma}{2}\left\|M^\top w-\lambda/\gamma\right\|^2
-\nu\left(b_n^\top w-c\right).
\]

The new dual at allocator line 92, gradient at line 98, polishing exposure at
line 139 and certificate at lines 181–184 agree with this derivation. This is
the reviewer's algebra; it is not a claim that reported realized beta equals the
chosen estimated-beta target.

The allocator's opening docstring still writes the zero-target equality and
zero-target gap without the `c` term. The implementation contains the correct
generalization; update the explanation to match it.

## 4. Certificate enforcement remains incomplete

[`allocate_factor`](https://github.com/hlemonnier/continual-research-takehome/blob/ce3fe4e76271709422165d6f24e2fbecd9d0fe07/handoff_v2/model_v2/allocator.py#L180)
checks finiteness, exact box feasibility, normalized beta residual and a
scale-dependent gap threshold. If the first pass fails, it resumes the joint
solve from the beta-polished point. This is the intended recovery rather than a
beta-only repair that ignores factor stationarity.

However, if recovery also fails, lines 198–203 label the result `not_certified`
and still return it. The engine appends the certificate at line 235 and uses the
vector without inspecting its status. A saved report can detect this afterwards;
the deployed strategy does not enforce it before trading. The current claim
that every recorded real-data solve passed is compatible with this source gap.

**Required next engineering correction:** after the one permitted recovery,
enforce a documented final outcome. An unacceptable feasibility/value residual
must trigger a deterministic, validated recovery or an explicit failure, not
an unchecked trade. Keep the tolerance related to meaningful value error;
do not introduce crashes solely because a harmless gradient misses an excessively
tight threshold. A warm-start reset is one possible recovery input, not a proof
that a fallback vector is feasible for a nonzero target.

The old source suite does not independently prove the historical test-first
sequence. The new before/after artifacts improve that evidence, but their
content and commit ancestry must be distinguished from a later rerun's results.

## 5. The certificate is before the final portfolio transformation

The engine computes the certificate on the box/beta solution, then applies

\[
w_{final}=a w,\qquad
a=\min(1,\mathrm{gross\_cap}/\|w\|_1).
\]

If `b'w = beta_target`, the final exposure is `a * beta_target`. Thus any active
gross reduction changes a nonzero target. The saved certificate refers to the
pre-scaling vector; it cannot certify the final requested beta target or the
objective with a gross constraint.

With target zero, scaling preserves that equality but still does not solve the
original cost-aware objective with the gross cap included. Costs are around the
drifted book, so scaling can introduce trades on stocks that optimally stayed in
their no-trade bands. This is an existing limitation with new relevance for an
affine beta constraint.

**Practical action:** record gross-cap activation and final estimated-beta
residuals alongside the certificate. If gross never binds on B0/B05, disclose
that limitation without pretending it explains their realized-beta error. If
binding occurs, either solve the gross constraint jointly or specify a repair
that jointly enforces the affine target and caps. A blanket statement that
market exposure is controlled precisely is too strong when the final book can
violate even the chosen estimated-beta target.

The published matched-diagonal experiment reports an active gross cap. Its
certificate can still be valid for the pre-scaling solver, but not for the final
portfolio's optimality under all implemented constraints. This distinction is
relevant to interpreting that experiment's size and cost effects.

## 6. Source-derived edge cases introduced by the target option

These are analytically identifiable API defects, not newly executed isolated
tests and not failures demonstrated on the supplied actual-data trading path.

| Case | Source behavior | Correct mathematical interpretation |
|---|---|---|
| Every beta is zero, target zero, at least one movable stock | The unconditional feasibility check uses `abs(c) >= abs(bn) @ cap`, i.e. `0 >= 0`, and raises | The beta equality is redundant; the risk/cost/box problem remains valid |
| Every cap is zero, nonzero target | Early return at lines 59–60 happens before target validation | The requested equality is infeasible and must not silently return zero |
| Every cap is zero, target zero, `info` supplied | Early return emits no certificate | The unique zero portfolio is valid; a successful status should be emitted if every solve promises one |
| Target exactly at the maximum box-achievable exposure | The `>=` check rejects it as unattainable | The boundary is feasible; either support it or explicitly document a strict-interior domain rather than call it infeasible |

These checks require small targeted pre-implementation verification when Claude
repairs them. They do not justify replacing the accurate main solver.

## 7. Commit chronology and what the supplied logs establish

The seven commits after the independent review were retrieved directly by
pinned first-parent revision. Their identities, dates, messages and changed
paths are preserved in
[commit_history_readback.json](../evidence/v2_followup_engineering_20261028/commit_history_readback.json).

| Commit | Recorded stage |
|---|---|
| `5bd1c16` | Engineering plan, checks, before/after artifacts and fixes; beta diagnostics; R27 plan and shadow code |
| `2108eca` | R27 frozen-holdings shadow result; candidate runner; matched-diagonal option |
| `b4aefa1` | In-progress R27 and matched-diagonal logs |
| `ec312ec` | Completed R27 and matched-diagonal results and ledgers |
| `c9fcbd8` | Explicit-beta plan, diagnostic, affine-target implementation and supplied before/after target-test logs |
| `52a3a21` | In-progress B0/B05 logs |
| `ce3fe4e` | Completed explicit-beta results and ledgers |

Thus the R27 policy plan precedes its shadow/result commits and the explicit-beta
policy plan precedes the policy-result commit. The engineering plan, tests, red
and green artifacts, and production correction share one commit; the analogous
target-extension material also shares one commit. Git does not establish their
within-commit creation/execution order. The provided red logs support Claude's
reported sequence, but this reviewer does not certify a historical ordering
that the version history does not independently encode. This does not obstruct
the independent present-state replay or invalidate the visible experiment plans.

The supplied beta-target test log has 32 passing assertions, including ten
positive/negative target comparisons to a convex oracle, and a saved initial
`TypeError` for the missing `beta_target` argument. Source and logs were inspected;
this particular cvxpy suite was **not rerun** in this follow-up. The earlier
allocator suite's independent 38/38 result applies to the earlier source, not
automatically to every later revision.

Two evidence-scope qualifications matter:

- The target-zero check compares the **current** function's default call with
  the current function's explicitly supplied zero target. It verifies that API
  equivalence; it is not a comparison with the old source.
- `verification/v2_package_checks_after_fix.json` and its log were first added
  in `5bd1c16` and are unchanged in the later target/correction commit. Their
  exact real-ledger equality and 3,527 certified-call report document the first
  engineering fix, before the affine-target extension. A current-source replay
  or independent current ledger readback must establish any stronger latest-head
  claim. The coordinator owns that evidence.

That current-source replay has now been completed and independently read back;
section 9 closes the actual-path evidence gap without retroactively attributing
the new result to the old verification logs.

## 8. Conclusions for the coordinator

1. Accept the restart and characteristic-layout fixes for the declared scorer
   lifecycle; independent complete-scorer evidence supports them.
2. Accept the affine-target mathematics. Estimated-beta feasibility and realized
   future market exposure remain different quantities.
3. Retain the dual allocator. Close the failure-enforcement and final-book
   certificate gaps before presenting it as guaranteed under all conditions.
4. Keep the failed R-layout bitwise-ledger expectation visible. It is a numerical
   scorer-layout qualification, not a causal strategy failure.
5. Do not attribute the real-candidate certificate counts, runtime or ledger
   identity to this synthetic execution. Those claims belong to their actual
   artifacts and the coordinator's independent replay/readback.

This document is independent AI-generated research/engineering review. It does
not rewrite the applicant's authorship or Claude's implementation history.

## 9. Independent readback of the latest actual V2/B0/B05 replays

The coordinator's prospective `LATEST_PACKAGE_REPLAY_PLAN.md` and observational
`replay_latest.py` were reviewed before execution. The observer copies exact
current source, calls the original scorer, returns original strategy arrays
unchanged, and reads the eta tracker only after the real hedge update. It does
not advance the tracker or call an extra optimizer. CSV arrays are explicitly
C-contiguous float64, as in the committed candidate runner; the loader is not
literally the scorer's `load` helper.

The first two launches failed at Python parsing because of an extra closing
brace, before producing any economics. The pre-execution reviewer inspected
the mathematical and observational logic but missed this syntax defect. The
saved pre-reviewed hash matches the failed source; an independent diff confirms
that the executed observer removes only that brace. The correction, failed
source and logs are retained. This is an audit-harness defect, not a failure of
Claude's strategy. See
[observer_parse_failure_readback.json](../evidence/v2_followup_engineering_20261028/observer_parse_failure_readback.json).

Successful attempt `002` ran each fixed policy in a fresh process. This reviewer
used Python's CSV reader and independent numeric aggregation on all three
`decisions.csv` and `daily.csv` files, rather than relying only on the coordinator's
summaries. The full
[independent readback](../evidence/v2_followup_engineering_20261028/latest_actual_replay_independent_readback.json)
records their hashes, index alignment, source identities, finiteness, cap checks,
certificate counts, scalar hedge identities and performance agreement.

| Observed quantity | V2 | B0 | B05 |
|---|---:|---:|---:|
| Decisions / economic rows | 3,527 / 3,526 | 3,527 / 3,526 | 3,527 / 3,526 |
| `ok` certificates | 3,527 | 3,527 | 3,527 |
| Recoveries / uncertified outcomes | 0 / 0 | 0 / 0 | 0 / 0 |
| Maximum pre/post gross | 2.622571 | 2.396221 | 2.394017 |
| Gross-scaled decisions | 0 | 0 | 0 |
| Maximum final estimated-beta target error | `2.18e-13` | `6.38e-13` | `6.69e-13` |
| Maximum absolute certificate gap | `4.45e-18` | `5.42e-18` | `1.02e-17` |
| Net Sharpe | 1.242503 | 1.044469 | 1.230593 |
| Realized net market beta | .046496 | -.013855 | .036383 |

All stock caps pass; maximum absolute weights are approximately 1.48%, below
the 5% cap. Every copied production/scorer hash is unchanged. The independent
performance and summary aggregations agree exactly when parsed from the same
CSV decimal strings. Shrinkage intensity eta ranges from zero to .207316 on
the B0/B05 paths, so the affine beta correction
does not reverse cross-sectional ordering on these paths.

The direct old/new V2 comparison was also recomputed independently, after
asserting identical earning indices. Maximum net-return difference is
`6.351381009669921e-12`; gross-return difference is `6.578568852860789e-12`;
fee difference is `4.627307075651035e-13`; daily closing gross difference is
`2.490592176940254e-10`. These satisfy the declared `1e-8` portability tolerance.
Differences from the coordinator's readback are at most `2.23e-16`, attributable
to CSV float-parser rounding. This is numerical reproduction rather than a
cross-environment bitwise-identity claim. See
[latest_v2_vs_original_independent_readback.json](../evidence/v2_followup_engineering_20261028/latest_v2_vs_original_independent_readback.json).

**Implication:** solver feasibility and final gross scaling are ruled out as
explanations for B0/B05's approximately −.014 realized-beta level error
on these particular replayed paths. The estimated-beta equality is accurately
enforced; realized market exposure is an estimation/calibration question. The
generic failure-path and binding-gross defects remain relevant to future robustness,
but must not be used to discount these correctly reproduced actual results.
