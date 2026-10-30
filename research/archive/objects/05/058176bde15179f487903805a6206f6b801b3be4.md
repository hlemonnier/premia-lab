# Cross-review: verification of the research and requirements plans

**Status:** planning/source review only. No models, tests or data-outcome analysis were executed. Reviewed `research_design.md` and `requirements_audit.md` without modifying either.

## Overall judgment

The two plans are consistent on the core contract: tomorrow-only information, net Sharpe as the objective, separate alpha/portfolio evaluation, drifted holdings for costs, exact official accounting, continuous warm-up and truthful AI attribution. The provisional 8-year discovery / 4-year validation / 3-year lockbox, first-wave cap of 12 complete discovery configurations and at most 3 finalists is defensible **as a declared internal discipline**, not an employer requirement or a statistical guarantee. I found no reason to replace it.

Before implementation, resolve the following operational ambiguities in the root plan. None requires another architecture or a large test framework.

## 1. High priority: define score masks as well as input partitions

`research_design.md:32–42` correctly states input slices and continuous replay, but input rows are not identical to scored rows. `requirements_audit.md:59–65` correctly identifies the official final-row omission.

A simple consistent policy is:

| Stage | Maximum input prefix | Score mask in Python indices | Number of scored rows |
|---|---:|---:|---:|
| Discovery | `0:2016` | `253:2015` | 1,762 |
| Validation A, from one combined validation replay | `0:3024` | `2016:2520` | 504 |
| Validation B, same replay | `0:3024` | `2520:3023` | 503 |
| Combined validation | `0:3024` | `2016:3023` | 1,007 |
| Final lockbox | `0:3780` | `3024:3779` | 755 |

These counts follow the original scorer, whose final returned row is `T−2`. They are a proposed explicit policy, not new project requirements. Freeze the actual masks in the experiment manifest. Run both validation blocks together after freezing finalists; slice the same daily trace. Avoid running A on a shorter prefix and later silently comparing its changed row count to A from a longer replay. Do not read the next protected input row merely to make a block exactly 504 scored days long.

The first rebalance is at close of Python day 252 and receives **253 history rows**; its target first earns a return on day 253. Keep that distinction visible when calling `0:252` the initial history.

## 2. High priority: close the ablation and diagnostic selection loopholes

`research_design.md:102–108` limits scored pipeline configurations but also allows six ablations and many signal diagnostics. The intention is good; the accounting needs one clarification:

- Treat feature scans, predictive diagnostics, choices among transformations, horizon comparisons, fit-window changes and hand-tuned adjustments as **research exposures** in a lightweight ledger even when they do not count as a complete scored pipeline. Twelve scored portfolios can still follow hundreds of implicitly selected modeling choices.
- Conduct candidate-changing ablations in discovery and count any newly considered complete pipeline inside the 12-configuration budget.
- Freeze any validation-stage explanatory ablations before opening validation results. If an ablation becomes a selectable alternative, it must be one of the at-most-three frozen finalists; otherwise label it explanatory and do not use it to introduce a new winner.
- A validation result may choose among frozen finalists. It must not generate a revised fourth finalist while the same blocks retain their clean-validation description.
- Cost stress, parameter neighbors, subperiod checks and bootstrap results are also exposures if they change the model. They are not a free separate optimizer.

The first-wave budget may be revised **before further results are inspected**, with a recorded reason. If an expansion is motivated by results already seen, say so; it is adaptive research, not retroactive preregistration. It does not automatically invalidate an untouched lockbox.

## 3. Medium priority: make the finalist decision rule executable, without invented significance hurdles

`research_design.md:110,118` proposes aggregate validation Sharpe, two-block stability and paired uncertainty, with simpler candidates preferred when differences are unstable. This is sensible but leaves room for post-result discretion.

Before validation, record the primary ranking statistic, exact eligibility conditions and tie/fragility procedure. The primary statistic should remain the pooled daily **net Sharpe**, not the average of block Sharpes or a t-test on mean return differences. If using paired block uncertainty, recalculate both candidates' Sharpes on the same resampled blocks and assess the difference in the objective being selected. Freeze the block rule using discovery information.

Do not require every two-year block to have a positive score, impose an unsupported minimum Sharpe, or use a universal significance cutoff as a hidden acceptance condition. Short blocks can be noisy. A candidate supported mainly by one period should trigger a fragility finding and a defensible judgment, not an automatically invented success/failure threshold. Record the decision and evidence even if the choice remains uncertain.

## 4. Medium priority: clarify what “final refit” means

`research_design.md:44–48` and `requirements_audit.md:49–53,92` agree that updating on matured observations is allowed and that backfilling history with a later-trained model is not.

Make the final operation explicit: after selection, the **already-frozen causal update rule** continues through all available observations. Its fitted state at the end naturally uses the permitted past. Do not add an ad hoc whole-sample initializer that seeds early forecasts or rebalance state with parameters trained on later rows. Changing model design or hyperparameters after inspecting the lockbox is a new research exposure and forfeits the untouched-lockbox claim; deterministic causal fitting under the frozen rule does not.

## 5. Medium priority: preserve the complete timing and reproducibility gate

`requirements_audit.md:79` correctly notes that the printed rebalance average excludes the first call. Carry that fact into the root acceptance criteria: report official timing **and** startup/periodic-refresh timing separately. Single-core measurement must cover estimator/solver thread settings as well as environment variables.

The plans otherwise contain the necessary reproducibility elements. Add the run lifecycle from the verification memo: write a running record before execution, then preserve pass/fail/incomplete status with actual logs. Predeclare tolerances and expected failure behavior; an exception must not disappear from the experiment ledger.

A century-sized synthetic replay is an engineering diagnostic, not alpha evidence. Do not make an expensive full-century run the first step. Use staged history lengths, measured memory/state growth and explicit limits; a projected result must remain labeled projected until executed.

## 6. Scope discipline: do not turn sensible safeguards into a second objective

`research_design.md:94–96` correctly distinguishes safeguards from hidden portfolio constraints. Preserve that distinction when choosing actual limits: no arbitrary gross/concentration cap should be presented as an employer rule. Choose sizing and numerical safeguards from observed/stressed failure modes, and disclose their performance tradeoff.

Likewise, a custom optimizer is not yet required. First establish the actual control problem and profile a credible implementation. Use isolated numerical checks only if a custom component is necessary, with failure modes and tests written before its implementation. The minimal hand-in remains the strategy and declared helpers; the research/evidence workbench should not become a platform project.

## Acceptance recommendation

Approve the plans for the next phase after the root manifest fixes (1) score masks and day-label mapping, (2) exposure/budget accounting including ablations, and (3) the pre-validation decision rule. Keep the remaining points as implementation acceptance gates. No evidence yet supports a particular signal, optimizer, achieved Sharpe, beta margin or runtime claim.
