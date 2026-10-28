# Next-day hedge error and raw-risk reconstruction — execution note (before running)

Executes `REVIEWER_NEXT_DECISION_20261028.md` §2 and §3 as written; script
`hedge_risk_diagnostics.py`. Frozen books: V2 (primary for §2), B0, B05 (primary for §3).
No position, forecast or parameter changes; decisions t = 252..3777, earning rows 253..3778.

§2 primary statistic: mean(H_corrected − H_raw) on V2; negative supports usefulness of the
annual beta correction at the traded horizon. Block ranges 21/63/126 days, 2,000 draws,
seed 20261027, all legal starts. Every stage and both secondary books reported.

§3 primary statistic: mean(loss_raw − loss_resid) on B05 with loss = log q + g²/q (q floored
at 1e-16 for nonzero books, 0 loss for zero books). V2 and B0 must show zero change
(their policy beta exposure is zero). The factor block of the joint moment must reproduce
the engine's F. The residual-market remainder 2p·w'E[u m] is reported, not added.

Disposition (from the reviewer's §4): if both effects are small or not predictive, close the
beta-control branch and return to mean-forecast and covariance research. No new strategy runs
in this stage. No target offset is fitted to the observed −0.014.

Prefix invariance: decision inputs at t < cut − 1 must be bitwise identical when rows ≥ cut
(cut = 2500) are replaced.
