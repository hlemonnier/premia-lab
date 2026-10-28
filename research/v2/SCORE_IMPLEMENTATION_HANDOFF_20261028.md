# Claude handoff: integrate the 1.318335 research leader faithfully

28 October 2026, Europe/Paris. This is an implementation/review decision, not a
calendar. The completed evidence is in [SCORE_RESEARCH_RESULTS_20261028.md](SCORE_RESEARCH_RESULTS_20261028.md).

## Decision and exact target

Integrate **F2 + VTvol**, preserving current V2 as a reproducible benchmark.
Research net Sharpe is **1.318334966090838**, versus **1.242503073307361** for
V2. Actual beta is **0.05272035468** and annual fees **0.3364064134%**. The
combination is the winner of the precommitted four-standalone-plus-one-joint
experiment set, not a new post-result mixture-weight optimization.

The original scorer and source inputs must stay unchanged. Keep the tested
parameters and arithmetic order while first integrating the candidate. The
score-first instruction does not call for restoring zero realized beta, adding
R27, changing the factor penalty, fitting an offset to beta, or retuning the
new half-lives. Those would be separate experiments.

## 1. Forecast: two complete pooled fits, one partial coefficient combination

Use the exact original 27-column design, in this order: 13 standardized linear
characteristics, 13 centered squares, standardized raw trailing beta. Both
learners fit every column jointly, with ridge 0.1 and 126 matured-pair warm-up.

Maintain separate EW Gram, score-vector and mass states at half-lives 252 and
1008. Share each day's already computed design, Gram and score contribution.
Combine the fitted coefficients as follows:

    coef = coef_slow.copy()
    coef[:13] = 0.5 * coef_slow[:13] + 0.5 * coef_fast[:13]
    prediction = design_today @ coef

Squares and beta stay slow. Do not average the whole prediction vectors, refit
the two feature blocks separately, or apply different decays to arbitrary rows
of a single Gram matrix. Those are different models.

Keep the original label clock: forecast row t sees X[t-1], its newest matured
pair is X[t-2] against residual return t-1, and each beta estimate uses only
returns already published for that role. Reset forecast moments and the base
risk/solver session at every forecast invocation.

Reference implementation:
[prototype.py](../../evidence/v2_score_forecast_20261028/prototype.py),
SHA256 `7854b2f763ae1bcc716282b68791503fe29f83d0aebc64835d8d0d919c722719`.

## 2. Base allocator: retain V2 settings

Keep factor-risk scale 0.3; factor/specific half-lives 126; specific shrinkage
0.2; variance floor 1e-6; raw beta window 252; risk aversion 200; cost horizon
20; virtual stock cap 0.05 and virtual gross cap 5. Beta correction and the beta
risk column remain off. The estimated-beta target remains zero. No change to
the allocation objective is part of this integration.

## 3. Execution: independent virtual F2 book and actual scaled book

At each close t, drift the previous virtual F2 target using its own gross
return g_t and denominator 1+g_t. Supply that virtual drifted book to the base
allocator with the F2 forecast. Update normalized EW63 and EW1008 gross-return
second moments with the just-earned virtual return. Do not insert fees into
the virtual denominator; the original scorer does not insert them there.

Use multiplier 1 before 63 earned observations. Thereafter use

    a = clip(sqrt(max(q1008, 1e-12) / max(q63, 1e-12)), 0.5, 2.0)

and return a times the new virtual target. Apply only the tested proportional
gross-5 reduction if needed. The actual scorer then drifts actual positions
and charges the true trade from actual held positions to this returned target.
Never substitute the virtual book's fees or scale a previously stored P&L.

The virtual book is F2 in the combined candidate. Using the old V2 virtual
returns to set its multiplier would not reproduce the tested strategy. The
first scored earning day is row 253; empty opening row 252 does not increment
the earned count. The first active multiplier is after close 315, positioning
for row 316. These indices illustrate the default start; implement the count
from the actual session lifecycle rather than special-casing historical dates.

Forecast starts a new session and resets virtual positions, EW sums/masses,
earned count and the base risk/optimizer state. The research wrapper expects
monotone one-day calls; make the production contract explicit.

Reference composition and controller:
[joint.py](../../evidence/v2_score_joint_20261028/joint.py) and
[overlay.py](../../evidence/v2_score_joint_20261028/overlay.py).
The wrapper's actual stock weights can exceed the virtual 0.05 cap; the declared
multiplier bound implies at most 0.10 before gross scaling. This is allowed by
the assignment. Do not introduce an extra 0.05 actual cap and call it equivalent.
Observed maximum actual stock weight is only 0.01644 on the current replay.

## 4. Packaging and release checks

Write the prospective end-to-end integration checks before changing production
code. Reuse the original scorer and research evidence, preserving exact source,
input and configuration identities. Acceptance for faithful integration is
economic reproduction, not a second round of optimizing settings.

Require the full daily economics to agree with the joint reference within the
declared 1e-8 reproduction tolerance, then inspect the actual differences.
Reproduce the full score, beta, costs and three historical segment summaries.
Check source/input hashes, final positions, actual fees, drift, startup,
endpoint and virtual-book independence. Preserve the existing future-boundary,
prefix and cross-history restart tests on the composed path.

Protected forecasts and same-layout temporal checks should reproduce the exact
identities established in research. The earlier combined future/layout tests
had tiny downstream numerical failures, retained in the evidence. Do not claim
those tests passed or silently change tolerances to erase their history.

Remove research-only logging of entire target histories, hardcoded workspace
paths and dependency on saved research arrays. Retain only state needed to
generate decisions from supplied past data. Avoid monkeypatching as the final
package architecture; the research factory is an executable reference.

Run the current integrated package's long-history/runtime gate. The observed
joint mean is 3.40 ms per call on the current one-core replay, with forecast
about 2.45 seconds for 3780 rows, but a century check of this new package has
not been executed. Report that gate accurately rather than inheriting the old
V2 package's result. A tiled history can test runtime/state stability, not
establish future alpha.

During publication, `v2-factor-risk` advanced to
`c51d31fe63c68255f2220935a8bc615c62bd1d0c`. An independent static readback found
that the previously reviewed allocator failure paths and final-book checks
have now been implemented. Integrate on that current head and preserve its
resumed solve, cold restart, certified matched-diagonal fallback or raise, and
final constraint checks. Do not replace production with the ce3 research source
copies. The base final check concerns the virtual 0.05 stock cap; any outer
VTvol check must use the declared actual 0.10 bound.

The same head adds a learned expanding/H252 whole-forecast adaptive mode. That
is a different policy from fixed H1008/H252, linear-only F2. Keep the existing
adaptive mode disabled and implement F2 as its own explicit mode. Static
inspection found no change to the forecast/label or risk-absorption clocks; it
does not establish economic equivalence on the new head. The reproduction and
runtime checks above remain required. Exact hashes and production diffs are in
[concurrent_head_readback.json](../../evidence/v2_score_forecast_20261028/concurrent_head_readback.json).

## 5. What to say in the research note

State that the objective is the official net score and that the new candidate
combines partially faster linear-premium learning with causal risk sizing.
Report the executed score and actual costs, and attribute the prototype and
audit to GPT assistance and the production integration to whoever performs it.

All historical periods are development data. The joint's gain is concentrated
in the final period; its paired 63-day interval against V2 includes zero
([-0.08197,+0.21792]). This uncertainty is not a new selection veto, but it must
not be turned into a claim of established future superiority. No hidden future
market was accessed. No pure-alpha Sharpe or applicant contribution is invented.

## 6. Next research decision after integration

The next mechanism worth specifying is the cost of changing the risk multiplier,
because more aggressive sizing improved gross performance but lost its advantage
after fees. A cost-aware scalar adjustment or conditional factor allocation
would be new policies and must each have a separate exact hypothesis and
original-scorer comparison. Do not extend this wave with an exponent/window
grid or chase the rejected F1 coefficient estimator. Maintain F2 alone as a
useful lower-cost comparator and V2 as the historical baseline.
