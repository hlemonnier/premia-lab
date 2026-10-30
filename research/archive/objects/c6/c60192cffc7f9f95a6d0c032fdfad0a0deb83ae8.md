# C11 preimplementation synthetic workflow and verification review

## Disposition

The fixed C11 source is approved for its already-admitted discovery run after independent source review and the completed predeclared synthetic whole-strategy workflow. The workflow exited0 with **40 passing checks**, four completed fresh-process executions of the original scorer, and no failed or unavailable comparison. This is a scoped capability and execution result on deliberately strong synthetic data. It is not evidence of actual-market alpha, a full-discovery causality pass or a long-history runtime pass.

The implementation author did not write the verifier. This reviewer wrote the plan and executable workflow before C11 existed, inspected the completed source, and ran the fixed workflow. The separate portfolio reviewer independently approved both the controller and candidate source before execution, then read back the completed evidence without rerunning it; see `reviews/interactions_independent_review.md`.

## Construction order and identities

`evidence/interaction_workflow_build_order_001` preserves the plan checkpoint with both verifier and candidate absent, the executable-verifier checkpoint with candidate absent, and the later implementation snapshots. The first run, `evidence/interaction_workflow_red_001`, exited1 with `EXPECTED_RED_MISSING_MODULE`, zero candidate/scorer workflows and intact frozen-source/generated-input identities. Its expected missing-module outcome is retained as construction-order evidence, not described as a strategy pass.

The subsequent completed run is `evidence/interaction_workflow_001`. The plan, verifier and worker were unchanged. Its generated input manifest is identical to the red stage's manifest, so the fixture was not changed in response to candidate output.

| Identity | SHA-256 |
|---|---|
| Synthetic plan, before implementation and executed unchanged | `2f91a5b2d2676244d0255ec5f53b1ff6ba77cd48339eebfa9ff6f6726bc56ecb` |
| Synthetic verifier, before implementation and executed unchanged | `f60bf69431b33943cc4199cf99dc5131181e10c08b78de0c3e294509712e898b` |
| Reused fresh-process causality worker | `1123bad6b74ad6a8ef639ae313a25fcfc5fa4a793121e553a33415d6fc4964b1` |
| Implemented and executed C11 entry point | `6a66bf842ea4fbdfde53e9d3423ffeed60088c2db3c27699cdbab2e3c89c7ae2` |
| Admitted C11 JSON file | `6e8f446417d3d8c51c6fd081ecc775e6f5a0982deebdec01712436655c344dfc` |
| Frozen synthetic-run JSON serialization | `04a49c278a243676224f6151685da9479932d9c56077c4198ab42c336bfd047f` |
| Completed synthetic summary | `6746db1d790a57239b602f5f23e81515a8d7c9b4807ceedc16b29214e1680b7f` |
| Completed artifact manifest | `0638e653bf0310e95efa814cb9e698d326615d3a58f14cd48e3f2b6aebb507fa` |

The synthetic controller validates the explicit requested configuration and serializes it into its frozen JSON. This changes formatting (including1e-6 notation), so its byte hash differs from the admitted JSON. Readback confirms exact equality of all parsed values. Each worker receives the same frozen serialization, records its hash and passes exact requested/effective configuration equality. No parameter changes are hidden by that formatting difference.

Readback verified all **68 recorded artifact files** against their saved sizes and SHA-256 values, with no mismatches. That readback is a saved-evidence audit, not a second numerical replay.

## Source and configuration review

C11 calls the unchanged base additive transform, retaining its26 values and appending78 products from `np.triu_indices(13,k=1)`. The product array is newly allocated and centered only on that published panel. It does not mutate the base26 columns. The ridge matrix places0.1 on the first26 coefficients and1.0 on the78 products; moments retain the same EW mass normalization and252-day half-life.

For output row t, training design is the panel at t−2, the newest label return is t−1, and its beta is estimated from returns strictly before that label. The prediction design is the panel at t−1. Learned moments and coefficients are local to each forecast call. The static pair indices and validated configuration contain no learned future state. First active row is127 after126 matured pairs.

Portfolio, risk and diagnostics delegate unchanged to the base implementation. Mechanical configuration comparison with C02 changes only the candidate ID and adds `interaction_ridge=1.0`; all other values are identical. Base strategy SHA `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7` and allocator SHA `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` match C02's frozen evidence. The original scorer remains `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

## Synthetic outcomes and accounting

The fixed seed20261026 generates600 days,1000 stocks and13 characteristics, with known lagged centered pair-product means, heterogeneous market loadings, bounded idiosyncratic noise and small nonnegative full costs. Truth is withheld from candidate arguments. The strong stationary signal is an intentional capability fixture, not an estimate of realistic market predictability.

| Predeclared check | Actual |
|---|---:|
| First active forecast row127 | Exactly127; all earlier forecasts zero |
| Forecast–truth pooled correlation>=0.90 | **0.9979141889595857** |
| Positive net mean and net Sharpe>1 | Daily mean0.001711690900483265; synthetic net Sharpe126.60122490160612 |
| Absolute realized net-market beta<0.2 | 0.000901393470621035 |
| Maximum stock weight<=0.01+roundoff | 0.0013092889308923912 |
| Maximum gross<=1+roundoff | 1.0000000000000004 |
| Known true-beta exposure, diagnostic only | Maximum absolute0.005406236744666356 |
| Gross-return reconstruction | Maximum absolute error2.17e−18 |
| Full drift-based fee reconstruction | Maximum absolute error1.52e−20 |
| Posttrade gross reconstruction | Exact |

All600-row cases returned346 scored rows253–598 and347 targets253–599; the384-row prefix returned130 scored rows253–382 and131 targets253–383. The baseline retained full paid fees totaling0.00415788565735104, while its original free opening trade had full unwaived cost0.000010026287918336767. No fee was reduced or extra opening waiver introduced.

The extremely high synthetic Sharpe follows from the deliberately strong known signal and cross-sectional diversification in the fixture. It must never be combined with actual-market comparison tables or interpreted as a tradable result. The corresponding forecast time13.6174s and mean official rebalance time11.4941ms (maximum108.7986ms) are observations on this short synthetic workflow, not the actual-market runtime gate or a century replay.

## Fresh-process invariance evidence

The baseline, identical repeat, joint suffix alteration and prefix each used a distinct fresh interpreter and frozen source/configuration. All completed with finite full outputs, unchanged inputs/holdings, valid caps and gross/net solvency. The altered suffix really changed both inputs from row400 onward while preserving their earlier prefix.

Every protected numerical comparison was exact, despite the permitted tolerance1e-14 absolute plus1e-12 relative: **all12 maximum absolute errors were zero**.

| Case | Forecasts compared | Targets compared | Economic rows compared |
|---|---|---|---|
| Identical repeat | Rows0–599 | Earning253–599 | Returns253–598 |
| Joint alteration from400 | Rows0–400 inclusive | Earning253–400 inclusive | Returns253–399 only |
| Prefix384 | Rows0–383 | Earning253–383 | Returns253–382 |

Economic comparisons include gross return, full fee, gross exposure, market return and derived net return. Wall timings are excluded. Fresh workers cannot share fitted candidate state. Candidate-specific full-discovery perturbations, untested startup boundaries and long-history behavior remain outside this four-case synthetic result.

## Completed discovery evidence audit

After the source and synthetic gate cleared, the implementation author executed the one admitted C11 discovery configuration. This reviewer then audited the saved artifacts without importing the candidate, refitting it or replaying the scorer. The audit is recorded in `reviews/C11_discovery_evidence_audit.json` with14 passing readback checks.

All29 artifact files match their recorded sizes/hashes, and all15 source-manifest entries match. The three imported files (`strategy_interactions.py`, `strategy.py`, `portfolio.py`) are identical across the reviewed synthetic snapshot, discovery snapshot and live source. The discovery runner copied the admitted JSON byte-for-byte with SHA `6e8f446417d3d8c51c6fd081ecc775e6f5a0982deebdec01712436655c344dfc`; its parsed values match the synthetic configuration. The scorer identity is unchanged, and the input-cache identities exactly match C02's permitted discovery inputs. Postexecution input hashes are unchanged.

The official run completed exit0 with20 passing workflow checks. Saved indices are exactly253–2014 for1762 scored days and253–2015 for1763 targets. Every daily net value equals gross minus the full fee exactly; the recorded original-scorer fee equals the captured same-close expected fee exactly. Recomputing net/gross Sharpe and annual fees from the saved daily ledger reproduces the reported figures.

| Actual discovery metric | C11 |
|---|---:|
| Net Sharpe | **0.6033462154364932** |
| Gross Sharpe | 0.7221228565881533 |
| Annual arithmetic net mean | 4.1666% |
| Annual net volatility | 6.9058% |
| Annual full costs | 0.819949% |
| Realized net market beta | +0.0222217 |
| Maximum drawdown | 8.3679% |
| Mean gross | 0.978179 |
| Gross-rescaling calls | 1419/1763 (80.4878%) |

The fixed-block net Sharpes are1.110764,0.536817,0.544525,0.362120. They are descriptive and do not replace pooled Sharpe. C11's pooled net result is lower than C02's0.637567; gross Sharpe is also lower than C02's0.750111, while full annual fees rise from about0.7773% to0.8199%. This fixed all-pair extension did not improve the measured discovery objective. Its synthetic capability success must not be substituted for that negative actual-data comparison. This result does not prove all interactions absent or establish the additive model as optimal.

All recorded candidate feasibility flags are true. Mean candidate rebalance time is10.4589ms, official instrumented mean17.5591ms and maximum candidate call721.8509ms. Forecast time26.8054s produces a straight-line century estimate0.0931h; no actual century execution occurred. These observations do not establish quiet-machine or all-future-path runtime.

The independently audited discovery summary hash is `0fb61fe3851d2bbcd222743d027d859e22552bd9b8333014e36ce30fab11c87d`; its artifact-manifest hash is `397ebbacc4edc34d6e21182a48f5fa1af6de877f0c5ecccced159c2f6f01b557`.

## Closing disposition

Approve the recorded C11 discovery result and its negative comparison with C02; no identity, accounting or evidence blocker was found. This approval is not a release decision. Configured full-discovery causality, long-history runtime, protected validation/audit and final clean-folder gates remain unexecuted. The lead closes this checkpoint at eleven scored configurations with slot12 unassigned. No holdout, C12, altered threshold, postimplementation unit test or duplicate candidate replay is authorized or performed by this review.

## Final reproduction/worklog claim review

This reviewer read the lead's updated `REPRODUCE.md` and `WORKLOG.md` after the C11 artifact audit. **Approve their verification-status claims for the eleven-configuration research checkpoint; no correction is required.** This was a documentation/evidence read, with no new numerical execution.

The reproduction guide and latest worklog section correctly distinguish C11's40-check, four-process synthetic workflow from its20-check actual discovery execution. Their12 exact protected comparisons and0.997914 forecast/truth correlation agree with the saved synthetic summary. The strong fixture is explicitly identified as engineering evidence, while C11's actual net Sharpe0.603346 is correctly reported as below C02.

Neither document claims an actual-data C11 causality pass. Both preserve the unfinished full-finalist causality and long-history runtime gates, and neither treats a forecast extrapolation as a century execution. The final nominee identities/simplicity ranks are not frozen; protected validation/audit and clean final-submission execution are explicitly unexecuted, with both outcome periods unopened. The earlier planning and ten-candidate paragraphs are clearly historical checkpoints, rather than replacement current statuses.

The documents support publishing this source/evidence research checkpoint. They do not constitute final strategy selection, release approval or authorization for another experiment. Reviewer-owned files are stable for the lead's commit.
