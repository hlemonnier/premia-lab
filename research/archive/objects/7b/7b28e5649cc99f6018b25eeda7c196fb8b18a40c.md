# Independent review of C11 and its predeclared workflow

**Reviewer:** portfolio-research agent, independent of the interaction implementation and synthetic-verifier authors.

**Decision at source-review checkpoint:** approve the exact C11 source and configuration below for the already-authorized, predeclared synthetic whole-strategy workflow. No blocking source defect was found. At that checkpoint, approval for the subsequent admitted discovery run remained conditional on the synthetic workflow completing successfully. The subsequent evidence sections below record the later synthetic and discovery outcomes. No actual-data causality, long-history runtime, or release approval is claimed.

## Scope and identities

Read the C11 admission in `research/EXPERIMENT_LEDGER.md`, `research/INTERACTION_ALPHA_PLAN.md`, `verification/INTERACTION_WORKFLOW_PLAN.md`, the complete new strategy/configuration, the complete synthetic controller, relevant reused causality-worker paths, the unchanged C02 implementation, and the construction-order records. Review actions read source/configuration/evidence and compared hashes and JSON settings. They did not import or execute the candidate, create isolated tests, rerun any market strategy, inspect new market statistics, or access validation/audit arrays.

| Reviewed artifact | SHA256 |
|---|---|
| `submission/strategy_interactions.py` | `6a66bf842ea4fbdfde53e9d3423ffeed60088c2db3c27699cdbab2e3c89c7ae2` |
| `research/configs/C11_interactions.json` | `6e8f446417d3d8c51c6fd081ecc775e6f5a0982deebdec01712436655c344dfc` |
| Unchanged `submission/strategy.py` | `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7` |
| Unchanged `submission/portfolio.py` | `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` |
| `tools/verify_interaction_workflow.py` | `f60bf69431b33943cc4199cf99dc5131181e10c08b78de0c3e294509712e898b` |
| `verification/INTERACTION_WORKFLOW_PLAN.md` | `2f91a5b2d2676244d0255ec5f53b1ff6ba77cd48339eebfa9ff6f6726bc56ecb` |

The two unchanged base files match their frozen copies in `evidence/discovery_C02_001/source/candidate/`. The C11 source and configuration match the implementation snapshots in `evidence/interaction_workflow_build_order_001/`. Every C02 configuration value other than `candidate_id` is identical; the only added key is `interaction_ridge`, equal to 1.0. No existing candidate was modified to create this contrast.

## Basis and estimation algebra

`_interaction_design` calls `base._basis(panel, config)` with the admitted additive setting. The original array is retained unchanged as the first 26 output columns. The product construction reads its first 13 columns, and NumPy strict-upper-triangle indices with `k=1` enumerate exactly 13×12/2 = 78 distinct pairs without duplicating the existing square terms. Advanced indexing and multiplication create new product storage; centering that storage cannot alter the original columns. Each product is centered using only its own available cross-section. There is no fitted normalization, selected pair list, future panel, return-derived feature, or additional scale parameter.

The 104-dimensional system places ridge 0.1 on the original 26 terms and 1.0 on the 78 products. Both Gram and response moments receive the same EW decay and daily cross-sectional normalization, and both are divided by the same accumulated EW mass before solving. The positive diagonal penalty regularizes correlated or duplicated columns using the existing NumPy linear solver. The model remains an ordinary EW ridge learner; GLS or factor covariance is not silently added.

The mathematical motivation is correctly limited. For standardized jointly Gaussian variables, the conditional product expectation can be quadratic in one variable. That identity is an illustrative reason to test additive separability, not proof of Gaussian characteristics, a simulator mechanism, or a tradable interaction in these data. Fixed unit product scale and the stronger interaction penalty are modeling choices, not empirically optimized quantities. The 104 coefficients are not 104 independent sources of evidence.

## Chronology, state, and validation

For forecast row t, the new code uses design `X[t-2]`, observed label return `R[t-1]`, and beta estimated from `R[:t-1]`, which excludes that label. The prediction uses the already-published panel `X[t-1]`. The loop starts at t = 2 and counts one matured pair per iteration, so the 126th pair is available at t = 127. All preceding predictions remain zero, matching C02's declared startup.

Gram matrices, response moments, mass, coefficients, and predictions are local to each forecast call. The module-level pair indices are fixed structural constants, and its configuration contains controls rather than fitted market state. Forecast cannot populate a future-trained model or risk cache for rebalance. Feature construction does not modify caller arrays; risk estimation uses the unchanged pure base helper. Consumed panels and returns are checked by the existing base paths, and nonfinite emitted predictions fail explicitly.

`configure` validates the new positive finite interaction penalty, rejects a contradictory non-additive basis, and forwards all remaining controls to the unchanged base validator. Unknown keys therefore remain errors. It resets from defaults through `base.configure` and records the new penalty in the wrapper configuration. The approved runner invokes one exact candidate/configuration in each fresh process. Arbitrary interleaving of several differently configured wrappers sharing the same base module is outside that execution contract.

## Portfolio identity and remaining model risk

`rebalance`, `estimate_risk`, and `get_last_diagnostics` delegate directly to C02. Raw trailing beta, residual-variance shrinkage/floor, diagonal risk, risk aversion, turnover penalty horizon, stock bounds, and gross cap are unchanged. The original scorer continues to charge full actual trading costs around the actual drifted holdings.

The inherited proportional gross scaling remains an approximation to the joint constrained cost optimum. This is a known limitation preserved for the controlled alpha comparison, not a newly corrected component. The larger basis can increase estimation noise and forecast runtime. Correct source and synthetic representational ability cannot establish actual-market benefit, reliable hidden-future performance, or the required long-history runtime.

## Verification construction order and controller review

The recorded order is consistent with the user's requirement:

1. At 21:07:17 UTC, the workflow plan was snapshotted while both verifier and candidate were absent.
2. At 21:09:31 UTC, the executable verifier was snapshotted while the candidate remained absent.
3. At 21:09:33–35 UTC, `evidence/interaction_workflow_red_001` completed with `EXPECTED_RED_MISSING_MODULE`, exit 1, and zero candidate/scorer workflows. Its two setup checks do not constitute candidate verification.
4. At 21:10:23 UTC, the C11 implementation/configuration snapshots were recorded with the hashes above.

The current verifier hash equals both its preimplementation snapshot and the red-stage frozen runner. No cases or numerical thresholds were added during this review.

The synthetic controller generates its conditional-mean fixture without importing candidate code and does not pass truth to the strategy. It executes the frozen complete candidate with the unchanged original scorer in fresh processes for baseline, repeat, future alteration, and shorter prefix. Configuration equality, source/input identities, finite shapes, declared stock/gross bounds, startup, and strong-fixture capability/economic thresholds are explicit. The original score indices and protected comparisons are coherent: alteration from row 400 preserves forecasts through 400, targets earning through 400, and economic rows strictly before 400. The prefix uses only its available forecast/target/ledger ranges.

The baseline accounting reconciliation uses consecutive saved targets, same-day observed returns, gross-return drift, and full one-way costs. It reports the original opening waiver separately. Incomplete workers cannot pass protected comparisons, and a later suffix failure alone is not diagnosed as leakage. The controller records timing without asserting a century-runtime pass.

## Remaining gate

At this source checkpoint, the synthetic candidate workflows and C11 market run have not been observed by this reviewer. The verification agent may now execute the unchanged, already-authorized synthetic workflow. Its saved outcome must be reviewed before the admitted economic comparison proceeds. Full configured causality, finalist nomination, protected validation, the single-candidate audit, and final packaging remain separate gates under the frozen protocol. This review authorizes no C12, interaction scan, or penalty search.

## Subsequent executed synthetic evidence review

Independently read `evidence/interaction_workflow_001/summary.json`, source identities, configuration, and input manifests after its completion at 21:13:32 UTC. All four fresh-process original-scorer workflows completed with exit 0, and all 40 predeclared checks passed. The twelve protected numerical comparisons across repeat, future alteration, and shorter prefix recorded maximum absolute error exactly zero. The declared first active forecast was row 127. Original gross-return, drift-based full-fee, and posttrade-exposure accounting reconciled within the frozen tolerance.

The deliberately strong synthetic fixture produced forecast/truth correlation 0.997914, net-market beta −0.000901, maximum gross 1.0000000000000004, and maximum absolute stock weight 0.00130929. Its net Sharpe of 126.601 is an artificial-fixture outcome and has no interpretation as actual-market expected performance. The fixture's purpose is to demonstrate representation, chronology and complete-interface execution under a known lagged interaction mechanism.

The executed candidate and unchanged verifier match the reviewed hashes above. Frozen serialized configuration hash `04a49c278a243676224f6151685da9479932d9c56077c4198ab42c336bfd047f` differs from the original JSON file hash because of serialization; independently parsed objects are identical. Red-stage and successful-stage input manifests are identical. Final source and generated-input integrity flags are true. No rerun or additional candidate test was performed for this readback.

**Updated gate decision:** the predeclared synthetic workflow has passed its stated scope, so the already-admitted C11 discovery run may proceed. Actual-market C11 economics and configured finalist causality remain separate, unreviewed outcomes at this checkpoint. The synthetic 600-row timing does not establish century runtime, and this review still authorizes no additional candidate or protected-period access.

## Subsequent executed discovery evidence review

Read the completed `evidence/discovery_C11_001` summary and source manifest, verified the frozen candidate/configuration/scorer hashes, and compared its saved daily ledger and summary with C02 and C06. All three ledgers have the same 1,762 return indices, 253–2014 inclusive. Recalculated pooled net/gross Sharpe, annual arithmetic mean, annual volatility and annual full fees directly from those saved ledgers; these reproduce their summaries, and each saved net-return series equals gross return minus full cost exactly. This is evidence readback, not a new candidate execution or feature scan.

C11 completed at 21:15:05 UTC with exit 0 and all 20 discovery-run checks passed. Its frozen entry point, configuration and original scorer match the reviewed identities. Inputs and frozen sources were unchanged. The recorded observed-beta, average-time, finite/solvency and stock/gross-bound flags all passed. The source and synthetic gates did not turn its economic result into an improvement.

| Saved discovery metric | C02: additive parent | C11: all pair products | C06: current development leader |
|---|---:|---:|---:|
| Net Sharpe | 0.637567 | 0.603346 | 0.762944 |
| Gross Sharpe | 0.750111 | 0.722123 | 0.963122 |
| Annual arithmetic net mean | 4.4038% | 4.1666% | 2.5907% |
| Annual net volatility | 6.9072% | 6.9058% | 3.3956% |
| Annual full fees | 0.7773% | 0.8199% | 0.6810% |
| Realized net-market beta | 0.02123 | 0.02222 | 0.00633 |
| Mean daily absolute turnover | 0.062116 | 0.065493 | 0.055630 |
| Calls requiring proportional gross scale | 79.75% | 80.49% | 51.84% |
| Maximum drawdown | 8.4883% | 8.3679% | 5.2777% |

The controlled C11–C02 difference is −0.034221 net Sharpe and −0.027989 gross Sharpe, with effectively unchanged annual volatility. Annual net mean falls by 0.2372 percentage points while full fees rise by 0.0427 percentage points. The deterioration therefore is not explained solely by extra costs. Fixed-block net Sharpes are 1.110764 / 0.536817 / 0.544525 / 0.362120 for C11, versus 1.141547 / 0.610645 / 0.531851 / 0.393269 for C02. Only the third block is slightly higher; no new block-profitability gate is inferred from this comparison.

C06 is a different complete learner/portfolio policy, so its comparison with C11 is a candidate-ranking observation rather than isolation of the interaction feature effect. C11 has a higher absolute arithmetic mean than C06 but substantially higher volatility and lower net Sharpe. That does not justify switching away from the frozen objective. C11's slightly lower drawdown than C02 likewise does not compensate for the weaker primary score under the existing protocol.

Observed C11 full-discovery forecast time was 26.805 seconds. Candidate rebalance mean was 10.459 ms, 95th percentile 16.419 ms and maximum 721.851 ms on CPU 1 with one numerical-library thread. These are shared-environment measurements; differences in wall timing between separate candidate runs are not controlled speed comparisons. The recorded 0.0931-hour century forecast estimate is an extrapolation, explicitly not an executed long-history gate. Maximum estimated-beta target exposure was 1.416e−13, maximum stock weight 0.007133, and maximum gross 1.0000000000000004 within numerical tolerance.

**Research conclusion:** this one fixed interaction specification has not earned promotion over its additive parent. Successful known-signal learning establishes that the implementation can represent and trade a strong interaction fixture; it does not imply that the supplied discovery data reward the same extension. The negative result does not prove that all possible interactions are absent or that no other regularization would work. It supplies no positive reason for an unplanned interaction search. The lead's decision to stop this checkpoint at eleven scored configurations, leave slot 12 unassigned, and preserve protected periods is consistent with the evidence. C06/C10/C09 remains the provisional score-ranked pool; finalist eligibility and formal nomination still require their separate gates.

Provenance of the saved economic artifacts read for this comparison:

| Candidate | Summary SHA256 | Daily ledger SHA256 |
|---|---|---|
| C02 | `55be398f57a598a29fb320007beab9b3131ceda6f37078e15a3478ebebf0b75e` | `5e5c6b55419c417377a5eac170e4838242ed19a44b97150320bf0c8d7d9ce736` |
| C06 | `7c457816f90e2dd8a4e7cdbd49cc1d4f44e6254d43486fe1b645798a89f913dc` | `4d87353339cd0fd2dc81fb75b303e05f5b1e3d3b530ba1abc8090810fc881cab` |
| C11 | `0fb61fe3851d2bbcd222743d027d859e22552bd9b8333014e36ce30fab11c87d` | `260ffb8c31392192387bc8e071903372bc59987ece4297e7907754597f0fc04a` |

No new numerical model, synthetic rerun, C12 configuration, validation input, or audit input was used in this evidence review.
