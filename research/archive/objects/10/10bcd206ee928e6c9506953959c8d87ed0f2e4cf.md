# Claude handoff: integrate the 1.444733 research policy

29 October 2026, Europe/Paris. Implementation/review instructions, without an
execution calendar. This supersedes the prior 1.318335 candidate nomination.

## Decision and reference

Integrate **unchanged F2 forecast + E2 execution + fixed M1 market sleeve**.
The selected original-scorer net Sharpe is **1.444733300556666**, annual
arithmetic net return **6.6089525784%**, annual net volatility **4.5745139091%**,
annual actual fees **0.2537924949%**, and realized net beta **0.1029775197**.
Historical stage Sharpes are **1.1990348669 / 1.8423639698 / 1.6546639685**.

Preserve prior F2 + VTvol (1.3183349661), E2 alone (1.3395817822), M1 alone
(1.4265608982) and original V2 (1.2425030733) as reproducible comparators.
F3 (1.2943927925) is rejected. E1 improves the score but is superseded by E2.
There is no need to repeat a search or change selection thresholds to integrate
this winner. Full evidence and interpretation:
[SCORE2_RESEARCH_RESULTS_20261029.md](SCORE2_RESEARCH_RESULTS_20261029.md).

The executable reference is the thin
[joint factory](../../evidence/v2_score2_joint_20261029/joint.py), which composes
unchanged, source-bound dependencies. Its SHA256 is
`2beeb7beb6d2107818d7570047c02d24f0654912fcc2cd5217bd01580b10c48f`.
The nine-file
[manifest](../../evidence/v2_score2_joint_20261029/pre_review_source_manifest.json)
is the authoritative policy/source identity, not this prose alone.

## 1. Preserve F2 exactly

Use the original 27-column design: 13 standardized linear characteristics,
13 centered squares and standardized raw trailing beta, in that order. Fit
every column jointly in both pooled EW regressions, half-lives 1008 and 252,
ridge 0.1, with 126 matured-pair warm-up. Maintain separate Gram, score-vector
and mass states; share the already computed daily sufficient-statistic updates.

```python
coef = coef_slow.copy()
coef[:13] = 0.5 * coef_slow[:13] + 0.5 * coef_fast[:13]
prediction = design_today @ coef
```

Squares and beta stay slow. A learned whole-forecast combination, averaging
all coefficients, refitting feature blocks separately or using an expanding
slow window would be a different policy. Keep the existing production learned
adaptive mode disabled for this candidate.

Forecast row t uses X[t-1] and beta[t]; its newest matured pair is X[t-2]
against residual return t-1. Each beta estimate uses only already published
returns for that role. Preserve the raw-beta label and hedge convention. No
beta correction, R27 risk basis or F3 interaction is part of this integration.
Reset forecasting moments and the complete policy session at every forecast
invocation. Normalize panel memory layout as required by current production.

F2 reference SHA256:
`7854b2f763ae1bcc716282b68791503fe29f83d0aebc64835d8d0d919c722719`.

## 2. Three independent books, with explicit clocks

### Virtual F2 reference

The first book is the unchanged F2 reference allocator: factor penalty 0.3,
factor/specific half-lives 126, specific shrinkage 0.2, variance floor 1e-6,
raw beta window 252, gamma 200, cost horizon 20, stock cap 0.05, gross cap 5,
estimated-beta target zero. The factor penalty is a chosen control, not a
calibrated forecast. Beta correction and the beta risk column remain off.

Drift the previous virtual target with its own earned gross return and
denominator 1+g_virtual. Update normalized EW63 and EW1008 second moments with
that earned gross return, excluding the empty opening observation. Then compute:

```python
a = 1.0 if earned_count < 63 else clip(
    sqrt(max(q1008, 1e-12) / max(q63, 1e-12)), 0.5, 2.0
)
```

At the original start, decision 252 is free and does not increment earned
count; the first active controller decision is close 315 for earning row 316.
Use the actual session lifecycle rather than hardcoded dates in production.
The virtual book owns its own risk state and solver warm start.

### E2 inner execution book

The second book uses its own previous E2 target, own earned gross return and
own drifted holdings. Maintain a separate engine, risk state and optimizer warm
start. Supply the same F2 forecast and published risk inputs. At each decision,
set gamma=200/a and stock cap=0.05*a, with cost horizon 20, gross cap 5 and
raw-beta target zero. Solve against the **E2 inner held book**, not virtual
holdings and not the outer market-combined holdings.

Configure/reset engines once at session start. Daily gamma/cap updates must
not reset or double-advance the risk model. Do not share engine globals or
warm-start state between the books. The engine's risk absorption clock and
certificates must agree with the reference workflow at every close.

E2 reference source SHA256:
`64dbb239848661fee97004e363d79a1568f02656e6b5e8ce5d76933faf338d1f`.
The research implementation uses namespaced engine copies to guarantee this
separation. Production may use explicit state objects, provided reproduction
demonstrates equivalent behavior.

### Actual combined book

After E2 produces target w_inner, add **0.05/N** to each stock. If combined
gross exceeds 5, reduce the whole combined target proportionally to gross 5.
Return that final target to the original scorer. Begin the fixed sleeve with
the free opening trade; do not add a new warm-up or a fitted market-premium
predictor. There is no separate index asset.

The outer scorer drifts and costs the actual combined book. The wrapper must
separately drift the E2 inner book before calling E2, using the inner gross
denominator. It must never pass the outer held positions into E2 as its own
holdings. The outer cap must not alter stored inner or virtual targets.

M1 reference source SHA256:
`91f6c27a11d18e23ac937dd7f4962210ee081bd011e963431e2a495b16a8648b`.
The fixed +0.05 is additional market notional; the observed total beta becomes
about 0.103. It is a different policy from the earlier corrected-beta forecast,
risk-residual and hedge experiment targeting total beta 0.05, whose rejection
stands. Do not silently substitute that earlier beta-correction path.
The declared pre-cap outer stock bound is **0.10 + 0.05/N**, or 0.10005 at
N=1000; dynamic inner bound is 0.05*a and virtual bound is 0.05. These bounds
apply to different books. Actual maximum observed outer weight is 0.016484.

All three books, controller moments/counts, risk models and warm starts reset
on a new forecast session. Preserve the monotone one-close-at-a-time rebalance
contract. Extra research trace histories are not policy state and need not be
kept by the deployable package.

## 3. Preserve current engineering safeguards

Research used pinned ce3 engine sources. Root observed production head
`c51d31fe63c68255f2220935a8bc615c62bd1d0c` during this wave. Integrate on the
current branch and retain Claude's resumed solve, cold restart, certified
matched-diagonal fallback-or-raise and final constraint checks. Do not replace
these with the older copied research engine.

Apply final checks to each book's correct bound, including the outer market
term. Keep restart and contiguous-panel fixes. A certified solve covers the
actual solved optimization problem; the inherited proportional gross reduction
does not make it a globally optimal explicit-gross-constrained QP. E2 prices
inner-book trades; final combined netted costs are measured by the scorer.

## 4. Prospective integration verification

Write the integration E2E specification and harness before production changes.
Do not add retrospective unit tests that mirror the implementation. Reuse the
original scorer and exact input hashes, keeping every failing and passing run.
First integration is fidelity work: parameter changes are new experiments.

Reproduce the reference forecast, three target streams and economic rows.
Before production edits, freeze these integration comparisons explicitly:
F2 forecast values and decision indices must match exactly; maximum absolute
weight difference must be at most 1e-8 in each of the virtual, inner and outer
target streams; maximum absolute difference in each of the four economic
columns (gross return, actual fee, closing gross, market return) must be at most
1e-8; and absolute full net-Sharpe difference must be at most 1e-8. Record all
observed differences, even within tolerance, and inspect their cause. Timing
columns are excluded from economic equality. Same-layout future/prefix/restart
identities inside the integrated package remain exact. Main candidate arrays live under
`evidence/v2_score2_joint_20261029/actual_001/E2_M1/`.

| Artifact | SHA256 |
|---|---|
| forecast.npy | `eaf4efefe539a476fdacbe05989e5e7c08feeb93b0d229b4f6269e18d3f69350` |
| targets.npy | `3813aafe0f6fa65fa3849af85108e90a902c5ab640571ad131288693fe252c32` |
| inner_targets.npy | `1529fdd4249d362e7da4de583d7c2a3b847ab0c89e2fdfeee7a60fe1e9c71c24` |
| virtual_targets.npy | `4da574ed4313cf793af1a29d9236bf3652f1e1f922edf49dd00272f3327ea3aa` |

Require the full score, beta, costs and fixed stage results above; original
free-opening, drift, reversals, netting, charged endpoint and no-liquidation
behavior; independent controller/inner/outer states; future-alteration, prefix
and cross-history reset identities; and failure/recovery/final-book branches
appropriate to the current engine. The existing research known-inner and
extreme-cap fixtures are available in the prospective joint specification.

Reproduce actual costs from final stock targets, rather than scaling or adding
independently costed P&Ls. Do not remove realized market beta from returns and
present that as the score of a separately traded hedge.

The selected research prototype's long-history gate is recorded in the results
report. The integrated production package needs its own full-history and
25,200-row one-core runtime/state check. Required mean rebalance time is below
100 ms and forecasting below one hour per century. Repeated data are only a
computational stress input, not another confirmation of alpha.

Remove hardcoded workspace paths, research monkeypatching, dependency on saved
arrays and full target-history logs from the deployable package. Keep only the
decision state needed from published data and a portable strategy/helpers
interface. For research-array restoration from the branch, use
[EVIDENCE_RESTORATION.md](../../evidence/v2_score2_root_20261029/EVIDENCE_RESTORATION.md).

## 5. Note and decision language

Report the actually executed integrated score once reproduction passes. The
research gain is a combination of adaptive forecasting already selected in
wave 1, causal risk sizing, cheaper actual-book execution and a small deliberate
market allocation. The new F3 forecast did not improve the score and was dropped.

Call the market component what it is: compensation from exposure to this
sample's market return, not a new stock-selection premium. The total future
book remains subject to the beta limit. All historical periods have influenced
development; the paired intervals are fixed-policy descriptions, not
selection-adjusted proof of future superiority. The final historical segment
is slightly weaker than M1 alone, despite the better full score.

Credit GPT research/audit and Claude's actual implementation work accurately.
The human contribution section must contain the user's own contribution, not
invented work. Keep the note concise and include the relevant failure modes:
forecast instability, market-premium reversal, beta-estimation error, cost
sensitivity and integration/runtime failures. No external message or submission
is authorized by this handoff.
