# Independent review of the consolidated master plan

**Decision:** APPROVE — the one requested lockbox-budget clarification has been implemented and verified by readback. No material unresolved issue remains.  
**Scope:** `Continual_Research_Master_Plan.md`, `RESEARCH_PROTOCOL.json`, completed preflight summary and independent preflight review.  
**Method:** document/artifact review only; no new tests, strategy implementation, model fits or outcome experiments.

## Resolved finding: lockbox reproduction budget

The initial review found that `locked_audit_candidate_runs: 1` could conflict with the required clean-folder reproduction and final official full-sample report. The root agent corrected both documents.

Readback confirms that master-plan section 5 now permits **one distinct frozen candidate/configuration exposed to the lockbox**, explicitly allows and logs exact unchanged reproduction runs, and treats a changed model or configuration as a new exposure that cannot preserve the original untouched-audit claim. The JSON now uses `locked_audit_distinct_candidate_configurations: 1` plus an explicit `locked_audit_reproducibility_reruns` policy with the same meaning.

The clarification is sufficient. It permits reproducibility verification without permitting hidden retuning or additional candidate selection on the lockbox.

## Verified consistency

- **Assignment contract:** future net Sharpe, signed stated beta threshold, past-only information, allowed dependencies, average one-core rebalance budget and compact submission are represented correctly. Absolute-beta screening and the 0.1 design target are explicitly internal choices, not fabricated employer requirements.
- **Index windows:** discovery has 1,762 scored observations; combined validation A/B have 504 and 503; pooled validation has 1,007; lockbox has 755; full official replay has 3,526. Inclusive prose ranges agree with exclusive JSON slices. First-call history length and the scorer's omitted final return/cost boundary are correct.
- **Research access:** actual outcome analysis remains in discovery until finalist freeze, and the lockbox remains structurally inspected only until its declared release. Online learning on matured observations is distinct from changing the frozen rule. No future-informed initializer or hidden prefix leak is prescribed.
- **Budgets and selection:** complete configurations, diagnostics and ablations are accounted for. At most three finalists are frozen before validation. Pooled net Sharpe is the primary ranking, with a predeclared numerical-tie rule; stability/uncertainty diagnostics cannot silently become a different ranking criterion. No unsupported Sharpe floor is introduced.
- **Verification policy:** the user's test-order rules are explicit; E2E is preferred; evidence is required for failed/interrupted runs as well as successes. Forecast cutoff inclusivity, earned-day target comparisons and strictly earlier net/cost comparisons are correct. Future cache elements are not incorrectly required to be equal.
- **Current status:** the plan accurately limits the successful preflight to 24 recorded structural/smoke checks and the first 504 input rows. It correctly identifies equal-weight beta failure by design, missing local optional packages, unchanged ZIP provenance, unknown remote CSV byte identity and all unexecuted candidate gates. Independent preflight review supports these scope-limited statements.
- **Reproducibility:** the failed first preflight remains visible; its reconstruction instructions are not claimed rerun-verified. Source identity, exact commands/configurations, run status and final clean-folder evidence are required.

No other material issue was found. The plan is suitable to freeze and deliver as the completed planning checkpoint. This approval concerns the plan's consistency and the scope of its evidence claims; it does not validate an unimplemented strategy or establish future performance.
