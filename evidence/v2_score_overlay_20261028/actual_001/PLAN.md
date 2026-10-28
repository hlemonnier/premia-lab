# Score pilot: causal volatility management of an unchanged V2 virtual book

28 October 2026, Europe/Paris. Owner: score_allocation_research. Parent authorized
this bounded research prototype after the saved-ledger opportunity readback.
Claude remains responsible for any later production integration. Source baseline
is `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`; all historical stages are exposed
development data. The supplied README permits full-sample parameter choice.

## Hypothesis and exactly two alternatives

Past V2 risk varies more than its conditional average return in the fixed EW63
bucket diagnostic. A bounded, past-only size controller may improve official
future net Sharpe by reducing exposure in high-risk states. That diagnostic used
hindsight bucket thresholds; no threshold from it enters this policy.

Maintain one unchanged V2 virtual book at its packaged configuration (gamma200,
factor scale.3, cost horizon20, raw beta hedge, stock cap.05, gross cap5). Its
forecast, risk estimates, optimizer and drift evolve independently of the actual
overlay positions. The base forecast and code are copied unchanged.

At close t, the previous virtual target v earns g_t=v'R[t] and drifts to
v*(1+R[t])/(1+g_t). Fees are not subtracted from this denominator: that is exactly
the supplied scorer's convention. Call the base rebalance once to obtain v_t.
The current gross return updates two normalized EW second moments, half-lives
63 and1008. Use only actual virtual earning rows after its opening call:
for the original start252, the first earned observation is row253. If n<63,
set a_t=1. At n=63 (close315), and thereafter, use:

* VTvol: a_t=clip(sqrt(max(q1008,1e-12)/max(q63,1e-12)),.5,2).
* VTvar: a_t=clip(max(q1008,1e-12)/max(q63,1e-12),.5,2).

Both update every day. The only difference is exponent1/2 versus1. Second
moments use sums S_h <- decay_h*S_h+g_t^2 and masses M_h <- decay_h*M_h+1,
q_h=S_h/M_h. No centered variance, fitted return mean, risk quantile, dynamic
beta target, altered forecast, alternate half-life, clip, or refresh grid is
admitted. The positive floor and caps are fixed before the pilot.

The actual target is a_t*v_t, reduced proportionally only if its gross exceeds5.
The unchanged scorer drifts the actual portfolio with its own actual return and
charges the full net trade to this actual target. Virtual standalone costs are
diagnostic; never charge them instead of actual costs. Record all scaling and
cap activity. The virtual stock cap.05 implies an actual per-stock bound.10;
the assignment has no separate stock cap. Estimated zero beta survives scalar
scaling. Realized net beta must still be measured, not inferred from the hedge.

## Controls and tests written before implementation

`e2e.py` is written before `overlay.py`. Its initial execution should fail with
the missing overlay import; preserve that failure. Then implement the wrapper
and `run_pilot.py`, and obtain independent source review before any scorer run
with a working overlay. Synthetic E2E first, actual-data pilot second.

The synthetic fixture is deterministic (seed20261028,420days,64stocks,13features)
and has persistent characteristics, market exposure, factor returns and a
volatility change. It is an engineering fixture, not alpha evidence.

Expected E2E outcomes:

1. A fixed multiplier1 wrapper reproduces a directly scored unchanged V2.
   Forecasts and decisions are exact; daily economics tolerance1e-12. Runtime
   columns are excluded. Both virtual decisions under VTvol/VTvar are identical
   to the multiplier1 virtual decisions. They share one immutable base policy.
2. Both dynamic policies activate exactly at earned count63, stay within [.5,2],
   enforce final gross<=5+1e-12 and have finite output. Capture every certificate.
3. Alter R and X from zero-based row360 onward; forecast rows<=360 and decisions
   at closes<360 remain unchanged. For a prefix of361 input rows, all its
   forecasts and all its decisions/economics reproduce the matching full run.
4. Reusing the same wrapper object on another history and then the first history
   reproduces the original run. forecast() resets both wrapper and base state.
5. Independently reconstruct actual drift and full fees from emitted targets,
   including free opening trade and the final charged, never-earned target.
   Check every scorer economic field to1e-12 and preserve source/input hashes.
6. A century/runtime gate is not claimed from this short E2E. Actual pilot
   runtime is instrumented and must be reported as such.

## Actual scorer experiment and decision rule

Use original returns.csv, characteristics.csv and costs.csv, parsed to contiguous
float64 with the exact current V2 source and unchanged scorer. Run multiplier1,
VTvol and VTvar continuously from252 to the scorer's original endpoint. All
three reset at forecast(). The full score uses earning rows253..3778. Stage
masks remain [253,2015),[2016,3023),[3024,3779); no stage reset or extra free
opening trade. Compare multiplier1 with the prior independently replayed V2
ledger, requiring daily economics agreement within1e-8.

Record full/stage net Sharpe, gross/net returns, costs, realized beta, gross/net
exposure, worst daily gross return, multiplier moments and clipping, gross-cap
activity, certificates, timing, and exact commands/environment/input/source IDs.
Keep every negative outcome. Forecast unchanged and virtual targets equal across
policies are separate explicit controls. Preserve daily and decision CSVs.

An alternative is a replacement contender only if official full net Sharpe
exceeds the current baseline by more than1e-8 (numerical tie guard, as clarified
in the parent's master plan), abs(realized net beta)<.2, no ruin/nonfinite state,
causality checks pass, and observed mean rebalance time is below100ms on one core.
Report original stages and paired block uncertainty rather than imposing a new
95% significance hurdle. A tiny positive selected difference is not evidence of
future superiority. No production promotion or additional tuning is automatic.

Runtime/long-horizon admission of a contender would still require an explicit
current-package long-history check. This pilot is research; no claim of future
performance or unobserved evaluation is made.
