# M1 complete-workflow specification — before implementation

29 October 2026. Owner: score2_challenge. Root has approved implementation under
the wave-2 master plan, SHA256
84e6d400dccc71c6a5b88ce189bd370c357d6bda0346246ce57ebf3c75a74fd2.
Actual-market policy scoring still requires independent source review, passing
synthetic E2E and explicit root release. No new score has been observed.

## Fixed policy

Wrap the unchanged ce3-based F2 + VTvol reference as an independent inner
portfolio. M0 has b=0; M1 has b=0.05. On each observed close, drift the previous
inner target by its own gross return, give those inner held positions to the
inner policy, and receive its new target u. Return u+b/N, reduced proportionally
only if combined gross exceeds 5. Keep u for the inner next-day state. The
original scorer owns outer actual drift and stock-level netted fees.

The sleeve starts with the free opening; no new warm-up. It is added after the
inner volatility multiplier. Preserve the original ending charged rebalance,
without forced liquidation. The true pre-cap weight bound is 0.10+0.05/N.
The actual gross cap never modifies the inner portfolio's state or moments.
Forecast entry resets both layers; calls must advance one published row.

## Expected failures and edge cases

The harness must first fail because sleeve.py does not exist. Thereafter it
will independently detect an implementation that uses outer held positions
inside the inner book, multiplies b by the VT multiplier, sums standalone fees,
counts a free opening as an earned return, omits the closing rebalance fee,
applies a stock cap of 0.10 to the combined book, or lets an outer gross cap
change the inner state. Nonfinite/ruined states or repeated/skipped decisions
must raise rather than invent a continuation. Constructor values other than
the M0/M1 alternatives are rejected.

## Prospective synthetic workflow and tolerances

Reuse the deterministic prior joint fixture (seed 20261028, T=420, N=64) with the
unchanged original scorer. Compare direct joint, M0 and M1. Require:

- M0 forecasts/targets exact, economics within 1e-12 of the direct joint.
- M1 inner targets exact to the direct joint; when outer cap is inactive,
  target-inner equals 0.05/N within 1e-12 and earned gross decomposition within 1e-12.
- Independent target-based drift/fee reconstruction within 1e-12; full accounting
  includes every decision, free opening and the final charged target.
- Future mutation from row 360, prefix through row 360 and a restart after those
  histories preserve protected forecasts and targets exactly. Economic rows
  agree within 1e-12. Canonical contiguous arrays are used, with no layout switch.
- Bounds within 1e-12, finite and solvent paths, and all base allocator certificates
  accepted. The virtual stock cap remains 0.05; actual M1 bound is 0.10+0.05/N.

Also run the original scorer from start 0 on deterministic small markets and a
known sequential inner policy. Cover constant inner targets with nonzero stock
returns, a long/short reversal, zero inner target, zero returns, strict trade
netting savings relative to separately summed trades, and forced aggregate cap.
The known inner policy independently verifies the held positions it receives.
Cap tests deliberately use large toy positions and check gross scaling rather
than asserting the production inner weight bound for the toy.

The harness independently reconstructs both actual and inner drift. It validates
every saved .npy by reading it back, then records dtype, shape, whole-file SHA256
and raw-array SHA256. Writes use a temporary file, fsync and atomic replacement.

## Actual replay interface, not yet authorized

The same preimplementation harness can enter --mode actual only with a JSON
root release containing approved=true and matching sleeve_sha256 and
harness_sha256, and with --e2e-result referencing passing results for identical
sources. It runs M0 and M1 with the original scorer from row 252. M0 must match
the existing joint ledger within 1e-8. M1 must retain exact M0 inner target and
forecast identities. It then runs the same M1 at one real future cut 1500 and
prefix 1501 to check canonical temporal invariance. These are verification
reruns of the identical policy, not additional candidates.

Every actual baseline/candidate output contains atomic targets.npy
(3527,1000), rows.npy(3526,5), inner_targets.npy and forecast.npy, plus an array
manifest. CSV daily economics and scalar decisions, source/input identities,
exact command, environment and outcomes are also recorded. All arrays retain
the original scorer's gross,cost,gross-exposure,market,time column order.

Report the original net score, original stage masks, costs, beta, exposure,
runtime and certificates. The master's admission rule and conditional joint
policy remain unchanged. A failure is preserved, never relabeled by a looser
tolerance after the result. No parameter/weight search follows a disappointing
score. Production source and original scorer remain immutable.
