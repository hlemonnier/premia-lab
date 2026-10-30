# Research ledger

The maintained policy is N0. This folder preserves the route to it: mechanisms, fixed plans, controls, negative findings and verification records—not only successful models.

**[Browse every archived branch snapshot →](ARCHIVE.md)**  
**[Machine-readable provenance and omissions →](archive/index.json)**

## Read by question

| Research question | Main evidence | Takeaway |
|---|---|---|
| Can more flexible alpha models improve the characteristic signal? | Earlier factor research and Waves 4–5 | Added complexity and richer transformations did not consistently help. |
| Does conditional factor risk matter? | Wave 6 and F verification | Factor-variance timing improved the historical portfolio; simpler total-risk scaling was a close control. |
| How should common premia be estimated? | GLS experiment and attribution review | Covariance weighting and coefficient-wise shrinkage mattered jointly; the fixed forecast combination, not pure GLS, was selected. |
| Can correlation estimation improve allocation? | Standardized-correlation and GC experiments | A modest construction improvement survived the GLS combination; not promoted as the current model. |
| Do peer or directed stock links add information? | Peer-link and ten-job research waves | Cross-stock extensions increased turnover and failed their matched comparisons. |
| Does own-stock history add anything? | N0 frozen review | A small residual correction survived source/sleeve diagnostics, with uncertain incremental performance. |
| Can the code be used outside the research workspace? | Release, promotion and single-package checks | Raw-history execution, package isolation, accounting, causality and long-path resource use were checked separately from economics. |

## Selected recorded comparisons

All values below are net Sharpe on the **same exposed simulated development history**, not independent evidence. Controls are not automatically eligible release candidates.

| Specification | Net Sharpe | Status in the research record |
|---|---:|---|
| Characteristic-factor reference (V3) | 1.44473 | Historical reference |
| ML specific-risk adjustment (R1) | 1.45765 | Small uncertain development gain |
| Multihorizon specific risk (H) | 1.45908 | Increment versus R1 below its fixed rule |
| Factor-variance adjustment (F) | 1.49344 | Earlier selected release |
| Fixed premium-estimator combination (G) | 1.53322 | Earlier selected release |
| G plus standardized allocation correlations (GC) | 1.54739 | Research candidate; not the current policy |
| Twenty-day target (H20) | 1.53896 | Rejected for period inconsistency |
| Characteristic-peer return dynamics | 1.34111 | Rejected |
| Characteristic-peer specific-risk pooling | 1.52963 | Rejected |
| Directed residual cross-stock links | 0.71804 | Rejected; high turnover |
| Own-history control (N0) | 1.55078 | Current implementation; exploratory selection |
| Cross-factor dynamics | 1.44420 | Rejected |
| Individual-response clipping | 1.53566 | Small, inconsistent gain; rejected |
| Adaptive forecast mixture | 1.49349 | Rejected versus fixed combination |
| Added residual low-rank covariance | 1.46927 | Rejected |

The full reports include controls and counterevidence omitted from this compact table. In particular, N0's gain over G is approximately 0.0176 with a confidence interval including zero. Fee stresses are separate hypothetical scenarios; the original supplied fee schedule remains the economic objective.

## Archive organization

`experiments/` contains reading guides grouped by source branch. `archive/objects/` stores unique published file contents, and `archive/index.json` maps every original branch/path to the stored object. Different versions are preserved instead of silently overwriting one another. Confidential inputs, third-party benchmark files and unreviewed binaries are excluded explicitly.

```bash
python tools/restore_research.py --list
python tools/restore_research.py --branch research-parallel10-plan-20261029 --output /tmp/premia-batch
```

Historical snapshots are reference workspaces, not additional maintained production models. See [reproducibility](../docs/reproducibility.md) and [research method](../docs/research-method.md).
