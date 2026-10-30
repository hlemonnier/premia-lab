# N0 publication completed

30 October 2026. The user renewed the request to put the verified N0 model on GitHub main. The earlier blocked publication remains a historical failed attempt; this task used the normal GitHub connector to create a new commit successfully, then updated main without force and with an expected-head check.

## Published identity and scope

- Previous main: `3d668e1877541742fcb9f9a5c665ff22ba2f7c76` (GLS).
- New main: `2164030581870f7f794d613b5848636bf2b581ca` (N0).
- Published tree: `a620d2fba22d002bd414239e8084ba55af34fe60`.
- Staging branch: `submission-ready-n0-20261030`.
- Previous GLS is preserved on `submission-gls-archive-20261030`; its head was verified before publication.
- Final main readback confirms the new commit.

The working tree was restored from the previously verified release archive and checked to match the prepared remote tree `99833d32610e927dc99b6b6178730fd739d01702`. The latest research-update ZIP changes only README.md and the strategy.py docstring. The executable strategy AST, N0 core/network, GLS/F helpers, dependency versions, parameters, original fees and trading rules remain unchanged. The updated local and remote trees match exactly. This workspace was assembled from verified archives, not a network clone.

Main contains only the thirteen exported submission files and allowlisted maintenance metadata. Entry point: root strategy.py selecting NetworkPolicy('N0') without shared snapshots. The additional files are gls_alpha.py, README.md, requirements.txt, six model_f files and three model_n0 files. No data, scorer, research folders, fitted models or prediction caches are in the submission export. First-person research documentation and uncertainties are preserved. The archive/checker and branch contract now describe N0 rather than GLS.

## Fresh checks in this publication task

The existing N0 release and archive workflows were reused; no model, tolerance, threshold or test objective was tuned.

The extracted thirteen-file archive passes eleven frozen helper/dependency blob checks, the frozen N0 entry-point AST check, six constructed replay workflows and fourteen equality comparisons. Earlier outputs have maximum difference 0.0 in activation, risk-channel, prefix, future-mutation and reset comparisons.

A fresh original-scorer replay on 3,780 days and 1,000 stocks produced 3,526 scored rows:

- Net Sharpe: 1.550777576322453.
- Full-period market beta: 0.09328720770138473.
- Annual trading costs: 0.34384511858473253%.
- Maximum daily economic-column difference from the archived frozen N0 release: 0.0.
- Separate cashflow reconstruction error: 5.204170427930421e-18.
- Allocation certificates: 7,054, all status ok.
- Complete forecast: 27.87798632 seconds.
- Average original-scorer rebalance: 5.46275223 ms.

Timings use one numerical thread per process on a shared host, not dedicated-machine guarantees. The prior century run was not repeated because the executable strategy is unchanged; it remains prior endurance evidence, not a new market sample. No separate N0 reviewer assessment is claimed.

Source scorer SHA-256 remains `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`. Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3.

## Hosted CI and delivery

The exact promoted commit ran on staging in GitHub Actions run `41060927281`, job `124080162791`. The final job conclusion is success. Installation and mandatory exported-package/causal E2E verification passed. The optional artifact-upload warning step ran, so hosted artifact availability is not claimed. No check was made optional during this task, and no account storage or artifacts were changed.

Local logs, receipts, input hashes and fresh daily economic rows are retained under `n0_main_publish_20261030` in the conversation workspace. The local Git commit metadata differs from GitHub's; matching tree and blob identities establish the published file identity.

Selection remains a user-authorized decision under uncertainty, not a claim of statistically established future improvement or a separate N0 review. Nothing was submitted or emailed to the evaluator. Research branches and previous releases are preserved.
