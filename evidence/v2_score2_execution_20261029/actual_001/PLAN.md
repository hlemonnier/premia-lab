# E1/E2: price actual trading when managing the risk of F2

29 October 2026, Europe/Paris. Owner: score2_execution. This follows the
root-approved SCORE2_RESEARCH_PLAN_20261029.md. No actual-market alternative
has been scored when this plan is written. Baseline source is ce3fe4e; reference
F2 + VTvol net Sharpe is 1.318334966090838. Every historical segment is exposed
development data. Original scorer and production sources remain unchanged.

## Exact alternatives

Keep the original F2 virtual portfolio, including its own gross-return drift,
factor-risk state, optimizer warm state, raw-beta hedge and forecast clock.
The desired multiplier a_star is exactly the prior VTvol rule: normalized
EW63/EW1008 gross-return second moments, floor1e-12, square-root ratio clipped
to [.5,2], enabled after63 earned observations. Opening row252 earns nothing
and is excluded. First active close315 positions for row316.

E1 chooses the actual scalar a after the warm-up by minimizing

    .5*200*max(q63,1e-12)*(a-a_star)**2 + costs @ abs(a*v-held_actual)/20

over [.5,min(2,5/sum(abs(v)))]. Virtual gross<=5 guarantees a feasible interval;
zero v returns a zero target. Before63 observations use a=1. The objective is
a chosen convex tracking penalty, not a calibrated utility or an expected-score
theorem. No strength/window grid is admitted. The solve includes stock-trade
netting and the supplied actual drifted book. The scalar's left/right derivative
and box KKT residual certify global optimality. A local fee inequality against
the desired target at the same held book does not guarantee lower total fees.

E2 preserves the same virtual book/multiplier, then uses a separate instance of
the ce3 engine to solve around actual held positions with risk_aversion=200/a,
weight_cap=.05*a, gross_cap5, cost_horizon20 and raw-beta target0. Engines have
distinct risk and warm states. Both reset once per forecast; changing the two
actual allocation coefficients daily must not call configure or reset risk.
The actual book uses the same F2 expected returns; its previous actual holdings
affect transaction costs. The virtual state never consumes actual positions.

With no costs, w=a*x gives the scaled quadratic objective. Scaling equivalence
is required only where the virtual gross cap does not bind; a fixed actual
gross5 cap is not the homothetic image of a binding virtual cap for a<1.
Extreme-cap tests check actual feasibility separately. E1 and E2 are distinct
policies and are never combined with each other.

## Prospective failure modes and complete-scorer checks

Write common.py and e2e.py before execution.py. Run e2e.py while execution.py
does not exist and preserve the missing-import result. Then implement policies
and request independent source review before any actual-market scoring.

Use the prior deterministic420-day/64-stock/13-feature fixture, seed20261028,
and original scorer. Engine/forecast/scorer copies are SHA256-bound to the first
wave. Use independent namespaced imports to prevent Python's module cache from
sharing engine globals. Tests are complete scorer runs, not post-code units.

Required checks, fixed before implementation:

1. Direct reference and baseline wrapper: forecasts/virtual and actual targets
   exact, non-runtime economic columns tolerance1e-12. E1 and E2 retain exactly
   the reference forecast and virtual-target hashes on each identical input.
2. Reconstruct actual gross returns, actual drift and all stock fees from saved
   targets, including free opening, reversals and final charged rebalance;
   maximum non-runtime economic discrepancy<=1e-12. No forced liquidation.
3. Same C-layout future alterations from row360: forecasts through360 exact,
   decisions before360 exact, economic columns before360 exact. Prefix361
   reproduces all its forecasts and decisions/economics exactly. Reusing each
   wrapper after a different history reproduces its original path exactly.
4. Zero returns produce finite zero targets/economics. Zero-cost E1/E2 paths
   match the zero-cost reference within1e-8 per position and economic field;
   the64-stock virtual gross is bounded above by3.2, so virtual gross5 cannot
   bind. Numerical tolerance accommodates the independently solved E2 system.
5. All E1 active scalar solves have feasible bounds (1e-12), box KKT residual
   <=1e-10, and objective no greater than its feasible desired-scalar comparator
   by more than1e-12. Check using an independent subgradient reconstruction from
   recorded targets and the actual held book. Warm-up is identified separately.
6. Every base/actual allocator call has an accepted certificate; all actual
   targets are finite with gross<=5+1e-10, stock cap<=.10+1e-10 and current raw
   estimated-beta exposure<=1e-9. E2 risk states must advance to the published
   row exactly and must not share warm-state objects.
7. A synthetic128-stock fixture with100x F2 forecast amplitude forces gross-cap
   activity; require finite solvent paths and declared constraints for both
   alternatives, not scaling equivalence under binding reference gross caps.
   The amplitude is a fixed engineering stress, never an economic candidate.

Use1e-8 for historical-reference economics reproduction and report actual
differences. Never relax a failed tolerance after seeing a result. Separate
canonical-layout temporal causality from previous mixed-layout failures.

## Evidence and release

Actual runner may execute only after root's source/E2E release, using one-core
BLAS. Run baseline, E1 and E2 once, retain every result, source identity, exact
commands and stdout/stderr. Scored earning rows253..3778; stage masks are
[253,2015),[2016,3023),[3024,3779). Net Sharpe uses ddof0 and all actual fees.
Admission: beat1.318334966090838 by more than1e-8; absolute net beta<.2; finite
solvent paths, declared constraints and certificates; causal checks; mean
rebalance<100ms. Paired21/63/126-day intervals (2000 draws, seed20261027,
last legal block start included) describe uncertainty, not an additional gate.

Write actual targets.npy, virtual_targets.npy, rows.npy and forecast.npy
atomically: temporary file, flush/fsync, rename, then reopen and verify shape,
dtype and full array hash. verification.json names every array and binds file
hashes. Save complete daily/decision CSVs. This avoids the prior truncated NPZ
checkpoint failure; target histories are research evidence, not policy inputs.

A prospective optional runtime path tiles supplied history to25200 rows into
memory-mapped arrays, uses one-core BLAS, and runs only the selected policy
after explicit root release. It checks actual forecast/runtime, finite/solvent
path and constraints without storing all target histories. Repetition tests
computational/state behavior, never future alpha. It is not run by default.

## Primary sources and scope

- Garleanu and Pedersen, Dynamic Trading with Predictable Returns and Transaction
  Costs, NBERw15205/JF2013, https://www.nber.org/papers/w15205 and
  https://doi.org/10.1111/jofi.12080. Partial adjustment and signal persistence
  motivate cost-sensitive execution. Their quadratic-cost solution does not
  derive E1's proportional-cost scalar penalty or guarantee our performance.
- Boyd et al., Multi-Period Trading via Convex Optimization,
  https://web.stanford.edu/~boyd/papers/cvx_portfolio.html and
  https://arxiv.org/abs/1705.00109. Jointly optimizing forecasts, risk and actual
  transaction costs motivates E2; our implementation is single-period.
- Lobo, Fazel and Boyd, Portfolio Optimization with Linear and Fixed Transaction
  Costs, https://stanford.edu/~boyd/papers/portfolio.html. Proportional trading
  costs and convex risk terms support the tractability of E1/E2. No fixed-fee
  nonconvex model or result about expected future Sharpe is imported.
