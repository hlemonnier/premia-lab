# Independent reconciliation of the selected C09 audit

**27 October 2026, Europe/Paris.** The unchanged prospective audit reviewer completed with `EXECUTED_PASS_SCOPE_ONLY`, exit0, and182 of182 checks passing. It independently reconciles the full canonical C09 audit replay, the entire preceding validation prefix, the original discovery identities, and the selected package/configuration/nomination bindings.

**The selected policy's audit net Sharpe is1.799230712243462 after the supplied full trading costs over755 observations.** The audit beta, runtime, finite-output, position and solvency conditions pass. These are positive findings on the reserved simulated-market audit under the supplied accounting model. They do not establish performance outside that period or trading conditions absent from the simulator.

## Fixed audit outcome

The sole selected configuration is `C09_additive_long_memory`, with original configuration SHA256 `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`. Root published the selection, handoff and audit gate before releasing the canonical audit. The policy replayed continuously from the original empty book and scorer start252 on inputs `[0,3780)`. Only the fixed mask `[3024,3779)` supplied the755 audit observations. No alternative policy was scored for audit selection.

| Metric | Independently reconciled C09 audit |
|---|---:|
| Net Sharpe |1.799231 |
| Gross Sharpe |1.861206 |
| Annual arithmetic net mean |9.676070% |
| Annual net volatility |5.377893% |
| Annual full trading fees |0.333119% |
| Realized net market beta |0.00566555 |
| Maximum audit drawdown |7.019703% |
| Mean gross exposure |0.805479 |
| Full-replay mean candidate rebalance |2.264577ms |
| Full-replay maximum candidate rebalance |6.676364ms |
| Full-replay candidate forecast time |6.294674s |

All original-helper metrics agree exactly with the canonical controller's reported summary. Separate arithmetic also reconstructs the mean, population volatility, Sharpe, centered net-market beta and drawdown within the already fixed numerical tolerances. Runtime refers to the saved canonical execution; this review ran no model.

## Complete replay and prefix evidence

The review verified all canonical artifact hashes/sizes, all source/configuration/scorer/protocol/helper identities, the selected validation record, and the discovery-verified four-file handoff manifest. The package's two engine dependencies equal the selected original source bytes; the configuration and package identities agree with the frozen audit nomination.

The full audit contains3,780 forecast rows,3,527 target/held-book rows, and3,526 economic observations. Every gross return, drifted held book, full paid fee, market return, closing gross exposure and target CSV field reconciles with the saved arrays. Net equals gross minus full fees exactly. The single opening trade remains waived, with no restart or additional free opening at a protected-period boundary. Maximum absolute differences from independently ordered arithmetic are2.78e-17 for gross returns,1.73e-18 for drifted holdings and4.74e-20 for fees, within unchanged `atol=1e-14,rtol=1e-12`.

The stronger extension check uses the full audit arrays directly. Their first3,024 forecasts,2,771 targets and2,771 drifted held books reproduce the **complete original validation NPY identities exactly**:

| Validation prefix reconstructed from full audit arrays | SHA256 |
|---|---|
| Forecasts |`ce5b27d45252947d9482b11c34605fba995f8a8c2fa408f50923b3fe84315df0` |
| Targets |`62e3508941482aa305fef0d103f618bfd5e944df87c4522adb4cf8f7aa91d805` |
| Held books |`10c2eaf971e7dd3ecd9904339b1438fc9da5f26999b977e1c4e075ab23ec2c6f` |

All2,770 preceding validation-replay gross/fee/exposure/market/net rows also match exactly, with maximum error0. The first3,024 input panels equal the validation inputs, and the original discovery inputs, three array-prefix identities and1,762 economic observations likewise match exactly. Timing measurements are outside economic equality targets. These observations support the tested historical-prefix behavior when the supplied input is extended; they do not prove causality for every possible unseen history.

## Preserved evidence failure and exact recovery

The first unchanged readback, `evidence/audit_independent_readback_001`, failed at artifact verification because the canonical artifact manifest listed one temporary partial characteristics copy that had disappeared. The audit summary had already been parsed and the audit access marker was true. This attempt is retained as a failed, exposed evidence review; it is not described as unopened or passed.

Read-only investigation established that the missing214,433,792-byte artifact was exactly recoverable from the first214,433,792 bytes of the retained canonical characteristics file. That byte prefix's SHA256 matched the original recorded digest `35ffdd2b0a27b2c58aa2bb5ad2680b44caa3ad00a4ffc4820ee700771b01a7e5` exactly. After root's explicit approval, an exclusive-create copy restored those exact bytes. The copy source, command, byte count, expected/actual digest, authorization and before/after identities are preserved in `evidence/audit_artifact_manifest_investigation_001`.

All three canonical numeric inputs, the original artifact manifest, original audit summary, original controller, audit nomination and reviewer remained byte-identical before and after recovery. No model was rerun and no source, reference, score mask, tolerance or gate was changed. The specific infrastructure origin of the transient artifact is unresolved. The second review, `evidence/audit_independent_readback_002`, uses the exact same frozen reviewer and passes all182 checks after recovery.

## Uncertainty and interpretation

The separate, prospectively specified audit reporting workflow was also independently read back: all44 reporting artifacts match, the fixed755-row mask and both seeds/block lengths are correct, every1,000-replicate sample contains finite net-mean/Sharpe values, the summary percentiles exactly equal those computed from the retained replicates, and the published tables/fee stresses transcribe correctly. That narrow saved-ledger review is recorded in `reviews/AUDIT_UNCERTAINTY_INDEPENDENT_READBACK.json`; the detailed interpretation is in `reviews/AUDIT_UNCERTAINTY_REVIEW.md`.

Both fixed block lengths produce positive lower endpoints for annual net mean and Sharpe, while the intervals remain broad. At twice the recorded fees, holding the recorded decisions fixed, net Sharpe is1.737247. These are conditional resampling and fee-estimation results for one selected policy; they do not quantify a probability of future profit or establish capacity, fill quality, stationarity or universal freedom from overfit. The earlier validation block ranking varied, and only C09 was admitted to the audit. No audit-period superiority claim over C06 is supported.

## Reproducibility and review scope

The prospective audit readback plan SHA256 is `6384a9f41a2824c3c8c28f7a3ab9acab3efdf1ee4d8c18c9e17b44950d753c40`. The reviewer source was frozen before audit access at `3e254eb87dd8fd1313826ddcdbf8fe91555cb476c85c1524076b7dbb3932c4a8`. Audit nomination SHA256 is `b68c5db46c641f68bdaa7526464c846dd29e1b4ab65c7fd1ab6e8f775762cea4`. The successful independent review summary SHA256 is `9ba63433b9c9b885e89827b04a8444e2df7e520e6bbad3178bb326f5cb0a0146`.

The evidence retains exact commands, fresh-output rerun commands, source/plan snapshots, environment, complete findings, logs, failed attempts and recovery records. This review establishes canonical replay reconciliation and package bindings. The clean handoff's full audit replay equivalence is a separate recorded engineering workflow. Nothing in this review changes the selected policy, parameters, explanatory note, reporting choices or external-submission authorization.
