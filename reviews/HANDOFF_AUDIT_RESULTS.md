# Frozen C09 handoff: complete audit replay equivalence

**27 October 2026, Europe/Paris.** The single authorized unchanged-package audit replay completed successfully. Every forecast, target, held book, and scored economic row matched the completed canonical C09 audit exactly. No strategy, configuration, verifier, or explanatory-note bytes changed after audit access.

## Authorization and prospective source lineage

Root explicitly released this replay after `evidence/audit_C09_001` completed, under the pre-access audit gate committed as `5522f41eb6b6b72b69b9a5f01268031ecea3869a`. This was the planned same-policy packaging reproducibility check, with no additional model selection or audit-driven change.

The prospective plan remains `verification/HANDOFF_ENGINEERING_PLAN.md`, SHA-256 `f9b052fbd78b732397a1f9d0154e7fe342b7b2095ca4cda15ebf6922c68bc10f`. The unchanged verifier is `tools/verify_handoff.py`, SHA-256 `2b3c12d17b599940d37b19ac0609442d9b963a465ce7db139b45f9107dd5b739`; it was written before the wrapper, independently reviewed by root, and exercised through the preserved expected missing-wrapper run before implementation.

Independent source review is recorded in:

- `reviews/HANDOFF_VERIFIER_SOURCE_REVIEW.md`, SHA-256 `239fa75ad2667b8040afa6faa93a73a4aebc0dce8b8b3569e68be3a3ad1e43da`.
- `reviews/HANDOFF_PACKAGE_SOURCE_REVIEW.md`, SHA-256 `fe413a15d545fbd26a1f381d9f8e2640981d5488c563a9635afa2f130dc89ea5`.

The selection record remains `941c07313d3d3f1914a93a57d85f032e8e0e609f7dd0495ff7f4f618bc5a42fa`; the original C09 configuration remains `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`. Before audit access, discovery equivalence froze `evidence/handoff_discovery_001/package_manifest.json` at `97ec4469c51311730d906a68bd594ecd48b75d87bb29f0beccb6f7e3e5d8d813`. The canonical audit nomination, SHA-256 `b68c5db46c641f68bdaa7526464c846dd29e1b4ab65c7fd1ab6e8f775762cea4`, binds that exact package in `handoff_package_manifest_sha256`.

## Executed complete workflow

The replay evidence is `evidence/handoff_audit_001`. Its summary preserves the exact executed command; `rerun.txt` gives the frozen-source command with a fresh destination. The packet retains the original scorer, prospective expectations, protocol, selected configuration, selection record, discovery package manifest, clean package, canonical reference records, isolated environment, logs, full output arrays, timing array, economic ledger, and artifact manifest.

The completed canonical reference was `evidence/audit_C09_001`, with its identical read-only inputs under `evidence/audit_C09_001/inputs`. The replay ran continuously on `[0,3780)` from the original empty-book start 252 in a fresh isolated interpreter, CPU 7, numerical-library threads fixed at one. It imported project modules only from the clean local `model/` directory. Canonical Fortran returns and C characteristics layouts were preserved.

The controller exited **0**, status `EXECUTED_PASS_SCOPE_ONLY`, with **20 controller checks and 26 worker checks passed**, one forecast invocation and one original-scorer workflow.

| Quantity | Exact completed comparison |
|---|---|
| Forecast | `(3780,1000)`, every value covered by exact canonical `.npy` identity |
| Targets | `(3527,1000)`, earning indices 253–3779, exact canonical identity |
| Supplied held books | `(3527,1000)`, exact canonical identity |
| Scored economic history | 3,526 rows on `[253,3779)`; gross returns, full fees, net returns, closing exposures and market returns exact |
| Accounting | Empty opening book, recorded free opening trade, all subsequent full fees, exact complete drift/gross reconciliation and retained closing cost |
| Reported audit mask | `[3024,3779)`, exactly 755 observations; no restart or retuning at period boundaries |
| Integrity | Frozen package, scorer, configuration, controller controls and input files unchanged |

The full-array SHA-256 identities match both the canonical audit's recorded hashes and its actual saved binaries:

- Forecasts: `252ff4099a66cb164358fe87a286329b24df714c726659fedd468daa658cfbde`.
- Targets: `948c0fb8aa9462586c6972ac409c25d0c768e20ab7817cf4fe434908ee4de617`.
- Held books: `127612d14a0f043e2000093a8594637c92a929fd45bba528fe1aa6e6c09bb7ba`.

## Fixed audit metrics and measured runtime

The wrapper reproduced the canonical selected-policy metrics exactly:

| Metric on the fixed 755-row audit mask | Value |
|---|---:|
| Annualized net Sharpe | 1.799230712243462 |
| Realized net equal-weight-market beta | 0.005665548854062871 |
| Annual arithmetic net return | 9.6760703596526% |
| Annual net volatility | 5.377893059410654% |
| Annual full trading costs | 0.3331189682351051% |

Candidate forecast time for the complete 3,780-row replay was `6.22620633599945` seconds. Mean candidate rebalance time was `2.1916697088159798` milliseconds; maximum `14.649230000941316` milliseconds. These measurements are recorded separately from exact economic comparisons. The previously executed 25,200-row workflow remains the long-history runtime evidence.

These are the same audit observations already produced by the selected canonical policy, not a second independent performance sample. Packaging equality establishes that the deliverable reproduces that policy on the executed histories. The audit measures performance in the supplied simulated market; it does not establish the unknown future score, universal causal correctness, or absence of overfitting. Uncertainty and selection interpretation belong to the separate research evaluation.

## Saved-evidence readback and final bytes

`evidence/handoff_audit_readback_001/readback.json` records the implementation owner's saved-evidence reconciliation, including exact source-review lineage. It rehashed all **36** replay artifacts, confirmed complete counts and masks, matched all three actual canonical output binaries, checked clean import/runtime controls, and rehashed the current four-file package. It executed no further strategy workflow. This author readback does not substitute for an independent final evidence review.

The unchanged deliverable still contains only:

| Member | SHA-256 |
|---|---|
| `strategy.py` | `7f15248160efd09e65d7dcf4d79cb1c5c4897d87641f2c2057f8566c7de7d946` |
| `model/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `model/strategy.py` | `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7` |
| `model/portfolio.py` | `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` |

The replay summary SHA-256 is `4e55d8e26eb135aa1460026275df4d8e9164cb1648c8732758a42e99cb3d9069`; its artifact-manifest SHA-256 is `58178a3f288a900c12f942fdff1e7dcc6dddb94aefbbdf40563aa39b145a955b`. The canonical audit summary and artifact-manifest hashes are respectively `da5df90330f0542a5c1c416090eae4eca44332a5717a1199c4a72b2ce1fb152b` and `2e1aff5ae8e1257a6abef712b821e4859778dd20f0bb60f2a9903cf0c350d95b`.

No post-audit source or note edit, new candidate, parameter adjustment, relaxed equality criterion, or external submission occurred in this work.
