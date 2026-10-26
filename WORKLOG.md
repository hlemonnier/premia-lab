# Worklog

## Objective

Plan and execute a disciplined, source-grounded quantitative research take-home for Continual Research. Current phase: an eleven-configuration discovery checkpoint is complete. The next work is finalist engineering verification, followed by the protected evaluation gates.

## 2026-10-26 — intake and planning

- Read latest relevant email and earlier scheduling exchange. Folder shared by Arseniy Banayev on 26 October at 14:12 Paris time. Earlier applicant message proposed finishing Wednesday; no explicit final submission hour found. Operational target: Wednesday 28 October, exact deadline unconfirmed.
- Extracted attached ZIP into source/ without changing its files. Read README, strategy interface, scorer, and both examples in full.
- Located authoritative shared Drive folder. Root file names/sizes agree; compare fetched README text. No remote CSV checksum verification available from metadata response.
- Delegated independent requirements, research-methodology, and verification reviews to three agents.
- Confirmed objective is future net Sharpe on an anonymous simulated stock market. It is not an instruction to build a continual-learning architecture.
- Recorded user's testing rules in AGENTS.md and phase0 failure modes/expectations in PREFLIGHT_PLAN.md before writing/running preflight.
- No candidate strategy, alpha experiment, late-period performance inspection, or outgoing email yet.

## Completed preflight and review

- Recorded the input/runner failure modes and expectations before execution.
- Preflight001 failed its original broad inventory assumption before any outcome analysis. Preserved failure, frozen runner, expectations, traceback and manifest. Corrected inventory scope to the exact original ZIP members.
- Preflight002 passed 24 scoped checks with exit 0: archive-member integrity, complete ordered data schema/finiteness, official CSV loader, 504-row equal-weight replay, 250 scored rows and identical economic output on repetition. The equal-weight example's beta is approximately 1 and intentionally violates the assignment condition.
- Independent reviewer verified all 12 original files against decompressed archive members with SHA-256, the saved runner hash, prefix-input hashes and both economic traces. Original source files remain unchanged.
- Two independent cross-reviews resolved exact validation masks, diagnostic/ablation budget loopholes, causal prefix protection, and the difference between input-access scope and evaluation scope.
- Froze RESEARCH_PROTOCOL.json before predictive research: 8-year discovery, two 2-year validation blocks with 1,007 scored observations under official boundaries, and 755 locked-audit observations. Initial cap 12 full discovery configurations, 3 frozen finalists, 6 explanatory ablations (selectable variants count inside 12), one locked audit.
- Defined pooled daily net Sharpe ranking, an explicit numerical tie rule, near-zero beta design aim, and transparent status labels. No arbitrary required Sharpe or per-block profit floor.
- Final independent review clarified that the audit cap is one distinct frozen candidate/configuration. Logged exact reproducibility reruns of unchanged code/configuration remain allowed; retuned or changed candidates are new exposures.
- Data outcome access remains first 504 rows only; full-file reading was input hygiene. No full-sample figures opened. All candidate/alpha/long-horizon claims remain unverified.
- Consolidated master plan and frozen JSON protocol independently approved. The sole final clarification (one distinct audit candidate, exact unchanged reruns allowed) is resolved in both documents. Planning checkpoint complete.

## Execution checkpoint recovered on 26 October

- User authorized a private GitHub repository, commits, parallel research agents, and experiments following the approved plan.
- Recovered the existing project into the current workspace, preserving source files, local history, frozen plans and completed evidence. The old absolute paths in historical evidence describe the original executions; new runs use the current workspace.
- Verified `hlemonnier/continual-research-takehome` exists under the connected user's account and its visibility is private. Remote initially contained only its initial commit; the two local planning/data commits had not been published.
- Recovered accounting001: 44 recorded passing checks through synthetic CSV loading and the unchanged official evaluator. Recovered alpha diagnostics: 123 recorded passing workflow checks over discovery only. Recovered risk diagnostics: nine recorded checks over discovery only. These are recovered executed artifacts, not newly repeated executions.
- Recovered the diagonal-risk allocator and plan/tests-before-code records, two expected red runs, and two subsequent 54-check passing records. Its second review/fix addresses numerical overflow before clipping. These component results do not establish full-strategy performance.
- Discovery findings support joint adaptive coefficients and one small additive-curvature challenger. They also show heterogeneous stock beta, material residual common risk, persistent characteristics and economically relevant costs. No candidate net result exists at this checkpoint.
- Three parallel agents now own alpha implementation, independent E2E verification, and portfolio research/review. Root owns experiment admission, scored comparisons, shared worklog and repository publication.
- Large raw data, numerical caches and bulky reproducible daily diagnostic matrices remain outside Git; their identities and generating commands remain recorded. Committed sources and compact results are the durable research record.

## First executed candidate wave

- C01/C02 specifications preceded implementation. Both configured causality smoke002 runs completed28 fresh-process scenarios with exact protected equality. The earlier smoke001 runs were interrupted during a harness instrumentation revision and remain explicitly incomplete, not passes.
- C04's new factor solver had its failure plan and73-check verifier written before implementation, with expected red evidence. Independent review prompted a zero-cap numerical-edge correction; the unchanged verifier passed73 checks again. Full discovery later completed without solver fallback.
- Four preregistered discovery pipelines completed the unchanged official scorer: net Sharpes C01=0.622345, C02=0.637567, C03=0.106491, C04=0.654213. All realized net market betas were between0.0076 and0.0282. Each run has20 recorded workflow checks and full-fee/target reconciliation. These are development-sample results, not clean future estimates.
- Faster forgetting was worse even before costs. Additive curvature and the factor risk model delivered only tiny pooled net gains. Gross scaling was active on63–97% of calls, a material implementation approximation rather than a rare safety event.
- Admitted bounded second-wave tests C05/C06 for covariance-weighted alpha learning, C07 for exact joint gross constraints, and C08 for a simpler higher-risk-aversion sizing control. All decisions precede their results. Eight total slots reserved, four scored so far, within the fixed twelve.
- Published planning, diagnostics and component evidence to the private GitHub main branch as0fdf79e. Imported its verified Git objects locally and preserved the two original local checkpoint commits and recovery commit on `recovered-checkpoints` before aligning main to the identical published tree.

## Ten-candidate discovery checkpoint

- C05 through C10 all completed the unchanged scorer with 20 recorded workflow checks and exit 0. Their net Sharpes were 0.602469, 0.762944, 0.679825, 0.626206, 0.700155 and 0.739890 respectively. No input, fee convention, scoring window or tolerance was changed to obtain a favorable result.
- GLS alone did not improve the benchmark; the GLS/factor combination C06 is the current leader. Raising covariance ranks to 50 did not beat it. These remain modest development results, not evidence of a strong hidden-future edge.
- The exact gross-constrained C07 optimizer reduced fees and removed postsolve scaling, with byte-identical C02 forecasts. Its average elapsed time met the requirement; a 10.85-second outlier is preserved, with no unusual iteration count and no proven host-cause explanation.
- C08's higher risk aversion also removed scaling, without improving Sharpe materially. C09's longer memory improved the pooled number but weakened the final block. These contrary observations are retained in the current checkpoint report.
- The first-wave comparison completed 99 reporting checks and an independent review. Its paired block bootstrap does not establish the tiny additive/factor gains, while the fast-learning loss has negative ranges under both predeclared block lengths. No resampling result is a probability of hidden-future superiority.
- Admitted C11 before implementation to test the additive assumption using all 78 pairwise interactions under stronger shrinkage. The motivating conditional-Gaussian identity is illustrative; neither Gaussianity nor the simulator's formula is claimed. A known-interaction whole-strategy synthetic workflow is being specified before code. Slot 12 is still unassigned.
- Published the first four models, full run evidence and the second-wave preregistration as GitHub commit `95bfe30`. The local main branch is aligned to its byte-identical tree, with the prior local checkpoint preserved on `recovered-wave1`.

## Eleven-candidate discovery checkpoint

- Published the complete C01–C10 code and evidence as private GitHub commit `e663d9bcb102126ffa943b58cc5c720b7a502613`. The published tree exactly matches the immutable local checkpoint; prior local history is preserved on `recovered-wave2`.
- C11's specification, executable synthetic verifier and expected missing-module stage preceded implementation. Independent source reviewers approved its 26 unchanged additive terms, 78 centered products, fixed penalties, chronology and unchanged C02 portfolio.
- The fixed synthetic workflow completed four fresh-process runs and 40 checks, with all 12 protected comparisons exactly equal and forecast/truth correlation 0.997914. Its strong artificial signal is engineering evidence, not actual-market performance.
- C11 then completed the original scorer on discovery with exit 0 and 20 checks. Net Sharpe 0.603346 was below C02's 0.637567, gross Sharpe was also lower and fees were slightly higher. Candidate mean rebalance time was 10.46 ms; the maximum 721.85 ms is retained. No setting was changed after either result.
- Closed this discovery checkpoint at eleven scored configurations. Slot 12 remains unassigned; the negative interaction result does not justify a pair-selection or penalty search. C06 remains the provisional leader at net Sharpe 0.762944.
- Updated the current report, reproduction guide and contribution ledger. All research and implementation are attributed to the actual AI contributors; no applicant empirical finding or final strategy success is invented.

## Next gate

Independently verify the exact finalist configurations for causality and long-history runtime using permitted or synthetic inputs, then freeze at most three nominees before opening validation. The final nominee identities and simplicity ranks have not been frozen. Protected validation, the single-candidate locked audit and clean final-submission execution remain unexecuted. Validation and audit remain unopened.
