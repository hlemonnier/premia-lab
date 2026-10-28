# Joint result: F2 plus VTvol

28 October 2026, Europe/Paris. Research prototype using unchanged production
V2 helpers and the original scorer. The conditionally admitted combination
improves official development net Sharpe to **1.3183349661**, versus
**1.2425030733** for V2: an increase of **.0758318928**, approximately 6.1%.

## Results from complete scorer replays

| Policy | Net Sharpe | Discovery / validation / audit | Net return/year | Net vol/year | Fees/year | Net beta |
|---|---:|---|---:|---:|---:|---:|
| Current V2 | 1.242503 | 1.098002 / 1.656859 / 1.147558 | 4.7550% | 3.8270% | .1756% | .04650 |
| F2 forecast alone | 1.291780 | 1.117706 / 1.528936 / 1.498744 | 5.1265% | 3.9686% | .2071% | .04905 |
| VTvol overlay alone | 1.277109 | 1.087012 / 1.757166 / 1.298085 | 5.4953% | 4.3029% | .3080% | .05209 |
| **F2 plus VTvol** | **1.318335** | **1.103512 / 1.633970 / 1.593029** | **5.7865%** | **4.3893%** | **.3364%** | **.05272** |

The joint gains .02655490 against F2 alone and .04122547 against VTvol alone. It
passes the recorded rule requiring a gain greater than 1e-8 over both selected
components, beta within .2, finite solvent accounting and observed mean runtime
below 100 ms. These are development selection results; the supplied history has
already influenced model design.

Fees increase by about .1608 percentage point/year versus V2. Average realized
risk also rises: this is not an unconditional risk-reduction claim. The middle
original stage is slightly below V2, while the final original stage improves
materially. No every-period-win criterion was imposed retroactively.

## Exact implementation

F2 fits the existing pooled ridge learner at half-lives 1008 and 252, mixes the
first 13 linear coefficients equally, and retains the slow quadratic and beta
coefficients. Label and feature timing are unchanged.

The unchanged VTvol wrapper maintains F2 as an independent virtual book,
including its own gross-return drift and cost-aware allocator. It scales the
new F2 target by the square root of slow EW1008 divided by fast EW63 gross
second moments, clipped to [.5,2]. Both moments use only virtual returns already
earned by the current close. Multiplier 1 applies for fewer than 63 earned
observations. The final actual target keeps gross limit 5, and the original
scorer charges the full actual net trade.

The base virtual book in this joint is F2. Its moments are not borrowed from
the previous V2 overlay experiment. The factory joint.py only composes the
two unchanged, previously tested implementations. No new parameter was searched.

## Reproduction and causal evidence

The synthetic joint complete-scorer workflow passes 22/22 checks. Direct F2 and
the fixed-one wrapper give exactly identical forecasts/targets; the active
overlay preserves its virtual F2 targets. Future alteration from row 360,
prefix 361 and cross-history restart preserve the protected path exactly.
Independent actual drift/fee reconstruction has maximum error 0.

The actual fixed-one F2 control reproduces the separate F2 score exactly.
Its forecast SHA256 is
`10e86d588bbba22a3ed0f61673cc80a0d100df2b62d983711bc2365087747927`;
its virtual-target SHA256 is
`5d8bb12d46e76b1b5dd95a7c33f764496417c5f3bec136d6a2ffbc7147fc8850`.
Both match the joint's unscaled F2 book. All 3,527 joint optimizer certificates
are ok; all 3,526 economic rows reconcile with the scorer.

F2's original mixed-layout strict workflow retains its numerical failures.
Before joint actual release, its unchanged-source baseline was repaired after
a truncated saved-array artifact. The repaired replay matches original
forecast/target hashes exactly and passes the canonical-layout actual future
test at cut 1500 with zero differences in protected forecasts, targets and
economics. That evidence correction changed no parameter, tolerance or score.
The verification record and hash are in this packet's execution_record.json.

Joint multipliers range .656624–1.645094, with mean 1.155961. Neither multiplier
bound nor final gross cap activates. Observed instrumented mean rebalance time
is 3.40 ms, and forecast time is 2.45s. The century gate was not executed in this
pilot; extrapolation is not a completed long-history check.

## Uncertainty

Paired moving-block 95% intervals, 2000 draws, seed 20261027, length 63:

| Comparison | Net-Sharpe difference | 95% interval |
|---|---:|---:|
| Joint minus V2 | +.075832 | [−.081966,+.217923] |
| Joint minus F2 | +.026555 | [−.061413,+.113594] |
| Joint minus VTvol | +.041225 | [−.081823,+.148638] |

Lengths 21 and 126 are also retained in actual_001/results.json. The intervals
include zero and do not adjust for the entire earlier selection history. They
describe unresolved uncertainty. The result nominates the joint as the leading
candidate from this bounded wave; it does not establish future superiority.

## Reproduction files

- PLAN.md: conditional admission and exact specification before implementation.
- build_order.json: harness-first chronology and expected missing-module failure.
- SOURCE_REVIEW.md: independent review of exact files before execution.
- commands.json: exact E2E and actual rerun commands.
- `e2e_001/`: all synthetic workflows, arrays, ledgers and source copies.
- actual_001/results.json: complete actual results and paired intervals.
- actual_001/fixed_F2/ and actual_001/joint_F2_VTvol/: full daily economics,
  scalar decisions and array identities.
- actual_001/references_manifest.json: exact V2, F2 and VTvol ledger hashes.
- execution_record.json: release evidence, source bindings and successful exits.

This is AI-generated research and research-prototype code under the user's
direction. The original V2 implementation remains attributed to Claude. No
applicant contribution, final submission or production integration is invented.
