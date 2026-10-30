# Post-GLS results — correlation combination improves historical Sharpe

29 October 2026. Frozen main: 3d668e1877541742fcb9f9a5c665ff22ba2f7c76. No promotion or external submission.

## Decision

GC combines the exact selected GLS/F2 forecast with the previously fixed standardized-correlation allocator. Net Sharpe is **1.5473865516722796**, versus main G **1.5332155606881952**, a gain of **0.0141709909840844**. It improves all three stages and both halves, without increasing measured beta, and remains ahead without the market sleeve and with doubled fees. It meets the economic/causal research-shortlist criteria, not a full release sign-off or proof of future superiority.

H20, a fully matured 20-day residual-return target replacing only the GLS half of the fixed ensemble, scores **1.5389641354186303**. It fails the fixed shortlist because both later stages and the second half worsen. Its matched-delay one-day control L20 scores **1.5170758957520005**. H20 was not tuned, combined, or sent to additional fee/sleeve scenarios.

GC plan: research-gls-correlation-combination-20261029, commit 21ca3e98d00ef61188e29477a78fc3187cb7c427. H20 plan: research-gls-horizon20-20261029, commit dd1901cb45e9ef9a3676bc3a60a514c6fca11ee8. Both precede implementation/scoring. Two primary candidates only; no horizon/blend/ridge/seed grid. Full history is exposed development data.

## All original-fee replays

Unmodified score.py; 3526 scored daily rows, zero-based253..3778. Each portfolio pays its own drift/trades. Fees are annualized percentages of capital.

| Policy | Net Sharpe | Beta | Fees/year | Mean gross |
|---|---:|---:|---:|---:|
| F reference |1.493439948|0.101233256|0.255160595%|1.759036|
| CORR on F reference |1.506230508|0.101147543|0.246801345%|1.716951|
| G selected GLS |1.533215561|0.094122448|0.231191958%|1.587392|
| GC |1.547386552|0.093984592|0.221355205%|1.542390|
| H20 |1.538964135|0.094557166|0.203042052%|1.621903|
| L20 diagnostic |1.517075896|0.093407728|0.207892928%|1.585405|

| Period | G | GC | H20 |
|---|---:|---:|---:|
|[253,2016)|1.262598869|1.270065483|1.299913123|
|[2016,3024)|1.929593992|1.935154273|1.890309178|
|[3024,3779)|1.743700852|1.772031297|1.730539556|
|Second half|1.850586280|1.865508366|1.822607852|

The first half equals the first period; none is a fresh holdout.

## Mechanisms and counterevidence

GC changes allocation correlations only. Standardize estimated factor returns by the marginal variance forecast known before each return; every21 days fit LedoitWolf(assume_centered=True) over at most252 available dates; normalize correlations, blend50/50 with F's existing correlation, and restore F's marginal variances. Both virtual and inner allocation books use this change. GLS training covariance is NOT changed. All GC alpha and marginal-risk forecast channels equal main G exactly. Maximum relative factor marginal-variance error is below1e-14.

GC's annual net mean falls from6.32401% to6.21300%; volatility falls from4.12467% to4.01516%. Fees, gross and beta decline. Worst observed daily net return is -1.51019% versus G -1.52381%; no future tail guarantee follows. This is construction, not a new expected-return signal.

The correlation increment is+0.012790560 on F and+0.014170991 on G. The difference-of-differences is+0.001380431, with63-day95% interval[-0.008024417,+0.010841465]. The components retain their historical benefits when combined; super-additive synergy is not established.

H20 uses feature row s=t-21 and the mean of residual returns s+1..s+20=t-1, each residual formed using its own prior beta. Covariance weights use only rows through s and F's multiplier for s+1. All training labels have matured before prediction. This is not an optimal dynamic-control policy or an exact covariance model for overlapping horizons. The H1 reproduction control matches original GLS. L20 uses only the first return of each window but releases it at the same time as H20.

On3508 common diagnostic dates, H20 slightly worsens next-day MSE (0.0003586008823 versus G0.0003585973144) and20-day-average MSE (0.00001824798478 versus0.00001824708354). Mean IC also falls at both horizons. H20 beats the deliberately stale L20 but does not support replacing G. Overlapping labels do not multiply independent information; future diagnostic labels never enter policy training before maturity.

## Prespecified robustness for GC

| Scenario | G | GC |
|---|---:|---:|
|Original fees/sleeve|1.533215561|1.547386552|
|No sleeve|1.419004977|1.432220777|
|Double fees|1.513311164|1.521597463|

No-sleeve beta: G0.044125807, GC0.043987717. Double-fee beta: G0.088240124, GC0.087777409. Residual beta is nonzero. All are full reoptimized scorer runs, not subtractions from fixed return series. No3x-fee or actual-century run for the new candidates.

## Uncertainty

Paired circular date-block bootstrap:3000 draws,seed20261104,blocks21/63/126. At63 days, GC-G95% interval is[-0.025244184,+0.054757969]; centered one-sided p0.232922, Holm p0.465845 across the two primaries. H20-G interval is[-0.029271794,+0.039734787]. GC intervals also include zero at21/126days. This adjustment does not account for all prior adaptive research; consistency/stress scenarios reuse the same history. No expected+0.014 future gain or success probability is inferred.

## Checks, timing and honest limits

Main runtime/docs/dependencies match ten frozen Git blob identities; five source identities match. G/F/CORR fresh daily economic columns match archived replays exactly. Original scorer SHA256:ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96.

Preimplementation E2E workflow and intentional missing-module failure are retained in local history. Constructed assertions: GC37,H2043,L2043 all pass. Supplied-data assertions:27 per primary all pass. Every causal/prefix/reset/layout earlier-output comparison has error0.0. Ten complete market/reference/stress runs each have7054 allocator certificates, all ok, with separately reconstructed cashflows.

The predeclared permutation workflow was initially omitted from the script and added later as supplemental E2E, not claimed preimplementation code. Strict gross-exposure permutation checks FAIL on G3.5773e-10, GC4.4151e-10,H203.9447e-10 versus1e-10. Forecasts, weights, returns and fees pass their respective tolerances. A prior verification-only active-set refinement reduces aggregate errors below1.6e-15; no objective/tolerance or scored solver changed. Original failures remain failed. Workflow receipts total201 named assertions:198 pass,3 fail; source/reproduction checks are separate. This is not an all-green release certificate or independent-agent review.

Primary full forecast times G23.28s,GC27.87s,H2025.84s; mean rebalances10.92/10.29/11.53ms. One numerical thread per process; concurrent shared-host runs, not isolated benchmarks. New candidate century times are only linear extrapolations. No independent reviewer or standalone new release audit was performed.

A streaming-container launch failed before execution; ordinary subprocesses completed the runs. No economic failure was discarded. Both candidate source files and uploaded verification code are checked against their executed Git blob identities. Main remains unchanged. See REPRODUCE_POSTGLS.md; the conversation evidence ZIP contains daily outputs, fit records, all receipts/logs, input/source hashes and local preimplementation history. Private CSVs and large caches/forecasts/targets are excluded but reproducible.

Methodological motivation, not dataset evidence: Garleanu/Pedersen NBER w15205 on signal persistence and costly dynamic trading; Ledoit/Wolf on covariance shrinkage; Engle/Sheppard NBER w8554 on variance/correlation separation. No DCC-GARCH or published numerical replication is claimed. GC awaits separate review/packaging/endurance before any selection; H20 is rejected under the fixed rule.
