# Independent readback of the two released validation workflows

27 October 2026, Europe/Paris. Written before this reviewer opens either validation outcome. Root explicitly released the exact C06/C09 commands after durable commit `6b9ea857b2329f31451cabe0a482c36d45441fd1`, under nomination SHA256 `fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5`. The root is executing the models. This review reads only their completed saved E2E packets and does not import/execute a candidate, change a configuration, or access audit observations.

## Inputs and prerequisite

Read `evidence/validation_C06_001` and `evidence/validation_C09_001` only after root confirms both completed with exit0. Require exact completed-controller status, validation mode, frozen nomination/controller/helper/scorer/protocol/source/configuration identities, and true validation/false audit flags. Freeze this plan and the readback source before reviewing outcomes. Preserve input identities, exact command, environment, all findings/failures, source hash and final result in this separate packet. Do not edit the input packets or referenced summaries.

## Full workflow expectations

Both numeric input prefixes have exactly3,024 rows,1,000 stocks and13 characteristics, with float64 finite arrays, nonnegative costs, canonical F-contiguous returns and C-contiguous characteristics. All artifact hashes/sizes and source/input manifest entries must match. The two candidates must have identical canonical numeric inputs. No raw source CSV or array beyond the already released validation prefix is needed.

Each packet must contain full forecasts shaped(3024,1000),2,771 targets and held books,2,771 candidate latencies and target-day records, and2,770 daily economic observations for return indices253 through3022. All arrays/latencies/economic fields must be finite; latency and fees must be nonnegative. Target earning indices are253 through3023. The first held book is empty. All targets obey the frozen stock/gross bounds within1e-12; gross/net returns remain above−1.

Reconstruct every gross return from the previous target and actual same-day return. Reconstruct the drifted holdings using the original gross-return denominator, and all paid fees from the next target minus those drifted holdings. Reconstruct raw market return and closing gross exposure. Use the already frozen `atol=1e-14,rtol=1e-12` for independently ordered arithmetic. Net must equal gross minus full fees exactly. The opening target's full trade cost is recorded as waived, with no reset or second waived opening at validation boundaries. Target CSV values must reconcile to full saved arrays and latencies.

The first2,016 input panels must match the byte-identified discovery cache values. Re-serialize the actual first2,016 forecast rows and first1,763 target/held rows and require their original discovery NPY hashes exactly. Do not rely solely on separately saved prefix files. Require the original1,762 economic and net observations to match exactly; timing columns are outside that identity target.

## Metrics, eligibility and selection

Use only the frozen masks A `[2016,2520)` (504), B `[2520,3023)` (503), and pooled `[2016,3023)` (1,007). Recompute metrics directly from the saved daily rows, and reconcile all original-helper summaries exactly with the copied hash-identified helper. Independently calculate the key annual mean, population volatility, net Sharpe, realized market beta and drawdown from those same net/market observations. Undefined ratios stay null. Reconcile actual candidate latency to its complete saved latency vector, separately from scorer instrumentation.

Eligibility follows the unchanged protocol: completed causal/output/path/long-history gates, current finite/path controls, defined pooled score/beta, absolute pooled net beta below0.2, and measured mean candidate rebalance below100ms. There is no minimum Sharpe, requirement that each block be positive, new cost adjustment, or post-result redesign.

Rank eligible candidates by pooled daily net Sharpe. Apply the already frozen absolute tie tolerance1e-6 to the best score, then the nomination's simplicity rank (C09=1,C06=3), then measured mean candidate latency. If no candidate is eligible, report no selection. Preserve every candidate's metrics and eligibility reasons. This review reports the mechanical ranking for the root-owned selection record; it neither opens audit nor chooses a new policy.

A pass means the saved released workflows and fixed selection arithmetic reconcile. It cannot prove absence of overfit, causal correctness on all possible future data, or a tradable future edge. The independent audit remains unopened by this reviewer.
