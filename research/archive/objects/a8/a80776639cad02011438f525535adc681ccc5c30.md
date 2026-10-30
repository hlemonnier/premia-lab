# Post-F research — two separate candidates, main unchanged

29 October 2026. Frozen main base: ebf1ff1636e263d5fa98ce724cf65dc912d3d0c3.

## Decision

The selected F reference reproduces 1.493439947872387 exactly. The new GLS-alpha candidate scores **1.5332155606881952**, +0.0397756128158082. The standardized-correlation candidate scores **1.5062305082757375**, +0.0127905604033505. Both improve all three chronological stages and both halves, satisfy the preregistered development-shortlist rules, and pass the executed E2E checks. Neither establishes statistically reliable future superiority. Main remains the audited F submission; no promotion, combination or external submission was performed.

GLS branch: research-f-gls-alpha-20261029; plan commit a7f258bff3c93798f4b5105ec39ebce293215772. Correlation branch: research-f-standardized-correlation-20261029; plan commit 4343359df4b194f02dbaaa2d0a73ea4b30739be7. Plans were committed before candidate implementation/scoring. The complete E2E code was written/committed locally first, and its missing-module failures retained. Each branch owns only its own candidate; common verification tools and this comparison report are shared.

## Full original-scorer results

Same supplied scorer and fees; 3526 daily observations, zero-based rows253..3778. Fees are annualized percentage of capital. Every policy incurs its own actual drift and transaction costs. The initial trade remains free as in the original scorer.

| Policy | Net Sharpe | Beta | Annual fees | Mean gross |
|---|---:|---:|---:|---:|
| F | 1.493439948 | 0.101233256 | 0.255160595% | 1.759036 |
| GLS | 1.533215561 | 0.094122448 | 0.231191958% | 1.587392 |
| CORR | 1.506230508 | 0.101147543 | 0.246801345% | 1.716951 |

| Period | F | GLS | CORR |
|---|---:|---:|---:|
| [253,2016) | 1.216402295 | 1.262598869 | 1.218399890 |
| [2016,3024) | 1.898307393 | 1.929593992 | 1.915673260 |
| [3024,3779) | 1.684744107 | 1.743700852 | 1.705275656 |
| Second half | 1.806894634 | 1.850586280 | 1.825005549 |

The first half equals the first period. These are exposed development slices, not fresh holdouts.

## Mechanisms and diagnostics

GLS changes the pooled return learner, not its feature set. Each matured cross-section is weighted by the inverse of a covariance forecast known before that outcome, with an unpenalized intercept profiled out. Woodbury avoids a 1000x1000 inverse. EW1008/252 learners use ridge0.1 times the weighted Gram diagonal; predictions blend 50/50 with F2 after the fixed warmup. The portfolio risk model, factor multipliers, sizing, sleeve and allocation rules remain those of F. Statistical precision undoes the allocator's deliberate factor-risk discount of0.3. This differs from the previous diagonal WLS cross-sectional ceiling diagnostic and Wave5's conditional-mean scaling.

GLS mean daily cross-sectional IC improves from0.014878908 to0.015391435; IC mean/std annualized improves from1.26650 to1.35141. Forecast MSE decreases slightly, from0.000357932342 to0.000357913287. Portfolio annual net mean falls from6.39403% to6.32401%, while volatility falls from4.28141% to4.12467%; fees and gross decrease. Worst net day is -1.52381% versus F -1.69190%. These are historical observations, not a tail guarantee or proof of new information. The whole GLS specification was tested; separate contributions from weighting, intercept profiling, relative ridge and warmup have not been isolated.

CORR keeps F's alpha exactly and preserves its marginal factor variances. Factor returns are standardized using variances forecast before each return. Every21 days, Ledoit-Wolf is fitted to at most252 past standardized observations; its normalized correlation is blended50/50 with F's original correlation. F's marginal variances restore covariance units. This is a rolling shrinkage estimator, not fitted DCC-GARCH.

CORR's Gaussian factor-covariance proxy loss changes by -0.266690003 overall (lower is better), with stages -0.220718351 / -0.596242468 / +0.065946902. The final stage worsens on this diagnostic despite its higher portfolio score. Estimated factor returns are imperfect proxies, not the simulator's hidden true covariance. Maximum diagnostic relative marginal-variance change is2.22e-16. Alpha matches F exactly; GLS's risk forecast channels also match F exactly.

## Prespecified no-sleeve controls

Both candidates passed the development metrics and software checks, triggering only the already permitted no-sleeve controls. All policies were fully replayed, not adjusted by subtracting an estimated market return.

| Sleeve removed | Net Sharpe | Gain vs F without sleeve | Beta |
|---|---:|---:|---:|
| F | 1.385598087 | 0 | 0.051236731 |
| GLS | 1.419004977 | +0.033406889 | 0.044125807 |
| CORR | 1.397745550 | +0.012147463 | 0.051150759 |

The gain survives removing the explicit market holding without increasing measured beta. Residual beta is not zero: this is not proof of market-independent alpha.

## Uncertainty

Paired circular date-block bootstrap,3000 draws, seed20261102; identical resampled dates for both candidates. At63-day blocks:

| Comparison | Observed gain | 95% interval | Centered one-sided p | Holm p, two candidates |
|---|---:|---|---:|---:|
| GLS-F | +0.039775613 | [-0.066666301,+0.145430358] | 0.236921 | 0.473842 |
| CORR-F | +0.012790560 | [-0.025869168,+0.055908555] | 0.262246 | 0.473842 |

The21- and126-day intervals also include zero. This does not account for every adaptive choice across the project. Period consistency and no-sleeve tests use the same exposed data, not independent replication. Both pass development shortlist thresholds, not a proof of future gains. No parameters, seeds, windows or combinations were searched after observing the results. GLS is the leading new research candidate; F remains selected on main.

## Verification and reproducibility

Fresh F economic rows match the Wave6 archive exactly. Source/scorer identities are preserved; original score.py SHA256 is ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96. New executable blobs were checked against the executed local files before committing.

136 recorded E2E checks pass:40 constructed-data and28 supplied-data checks per candidate. They exercise the original scorer, separate cashflow reconstruction, prefixes, future-return/characteristic mutations, reused-session reset, memory layouts, zero data and stock permutation. Earlier forecast/position comparisons have zero difference. Existing permutation-weight tolerance1e-8 was not changed. All full primary and no-sleeve runs have7054 optimizer certificates, all status ok. No lookahead was detected in the executed cases; no absence-of-overfit guarantee follows.

Full primary forecast time:12.69s GLS,8.22s CORR,6.41s F. Serial rebalance:9.52/9.64/9.85ms, respectively. One numerical thread per process, shared host. Only linear century projections were made for these candidates; no actual-century test or fee-doubling/tripling run was performed for the new variants. No independent-person/subagent audit is claimed.

A NumPy Boolean initially prevented the assessment JSON from being serialized. Only that export conversion was fixed, then the assessment rerun; no model, threshold or economic result changed. Original failure logs and intentional preimplementation failures are retained. No economic trial was discarded.

See REPRODUCE_GLS_CORR.md. The downloadable evidence archive retains exact code, fit records, daily cashflows, source/output hashes, commands, logs and local preimplementation history. Private CSVs and large forecast/position arrays are excluded but reproducible. Use a fresh work directory when source inputs/code change; the research cache is not a deployable model component.

Methodological motivation only: Engle/Sheppard NBER w8554 (2001), Ledoit/Wolf (2004), official scikit-learn LedoitWolf documentation, and Beck/De Nard/Wolf, Improved Inference in Financial Factor Models (2023). Accessible abstracts/documentation informed the designs; no published empirical result was assumed to transfer to this market.
