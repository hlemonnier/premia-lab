# Independent V3 integration review

29 October 2026, Europe/Paris. Reviewer: GPT, with separate source, evidence and
market-interpretation reviewers. Production commit:
`978824d4b6140c43566ebd61a3ee8157f4080e35` on `v2-factor-risk`.
Research reference: `9e56aa755d20c5876485188f4c50ce959f6d63f3`.

## Decision

**Accept the V3 integration. Retain the fixed +0.05 market sleeve as the selected
score-first policy.** Source review, exact original-reference fidelity, all
fifteen unchanged temporal checks and the one-core century-runtime workflow
pass. No demonstrated production defect requires a code change. Correct the
reporting and scenario interpretation described below.

The recommendation follows the user's objective and the original brief: future
net Sharpe, with a future market-beta condition. It is not a forecast that 1.445
will persist, an assertion that the sleeve is stock-selection alpha, or a claim
that a finite audit can rule out research overfitting. No executable production
file, scorer, input, parameter or selection threshold was changed in this review.

## 1. The original numerical reference has been recovered exactly

Claude disclosed a genuine deviation from his integration specification. His
independent research rerun did not reproduce the original target-array hashes;
he used that same-environment rerun as the comparison reference. Agreement in
daily returns alone could not bound differences in individual stock positions.
Nor did the committed integration report retain a complete source/input/array
binding for that replacement reference. A different numerical environment was
a plausible explanation, not a demonstrated cause.

We closed that question without changing the policy or relaxing its tolerances.
After independent source review of the prospective verification wrapper, root
released one rerun of the pinned research and one rerun of the pinned package.
The original data and scorer, consumed source files, environment, thread settings,
reference identities, actual targets, controller state and complete economic rows
were captured together. Both replays produced:

| Quantity | Independent research | Shipped V3 |
|---|---:|---:|
| Net Sharpe | 1.444733300556666 | 1.444733300556666 |
| Net beta to equal-weight market | 0.10297751974238421 | 0.10297751974238421 |
| Annual arithmetic net mean | 6.6089525784% | 6.6089525784% |
| Annual net volatility | 4.5745139091% | 4.5745139091% |
| Annual mean full trading costs | 0.2537924949% | 0.2537924949% |
| Certified optimizer calls | 7,054, all `ok` | 7,054, all `ok` |

Forecasts and all three target streams match both each other and the original
published **file and raw-array hashes exactly**, with the original shapes and
dtypes. Original identity is therefore recovered; this is stronger than a small
economic discrepancy. Decision indices and controller traces also match each
other exactly. All four economic columns match both each other and the original
published daily ledger exactly. Timing columns naturally differ and are excluded
from economic identity claims.

Independent stock-by-stock accounting reconstructs the economic rows with maximum
gross-return error `5.204170427930421e-18` and fee error
`2.31239994600424e-19`. The opening trade is free, the endpoint trade is charged,
and no forced liquidation is added. Both books use 3,527 decisions and 3,526
earning rows under the original scorer convention.

This result resolves the present fidelity question. It does not rewrite Claude's
historical failed hash prerequisite as a pass or identify the cause of his earlier
cross-environment discrepancy. His reported 1.4447333005564316 remains consistent
to approximately `2.34e-13` in Sharpe.

Evidence: [replay result](../evidence/v3_evidence_audit_20261029/replay_001/result.json),
[frozen plan](../evidence/v3_evidence_audit_20261029/REPLAY_PLAN.md),
[peer review](../evidence/v3_policy_audit_20261029/replay_wrapper_peer_review.json),
[root release](../evidence/v3_root_review_20261029/REPLAY_RELEASE.json).
Replay-result SHA256:
`8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66`.

## 2. Source review supports the intended policy

The deployed F2 forecast, E2 sizing and M1 sleeve match the frozen research
formulas. Forecast labels mature before use; row t uses characteristics known
before t. The virtual book and inner traded book own separate risk states,
targets, optimizer state and drift denominators. Only the virtual book's earned
gross returns update the volatility controller. The inner book's own gross
return determines the drift of its held positions. `forecast()` recreates
session state. The scorer charges the
actual combined stock trades, including netting between sleeve and inner book.
The copied engine and allocator are byte-identical to the hardened c51 versions.

No selected-policy implementation, causal-clock, cost-accounting or state-isolation
defect was demonstrated. No production correction is required by this source
review. The factor-risk scale of 0.3 remains a chosen penalty, not a calibrated
variance forecast. Optimizer certificates apply to the solved subproblems; they
do not establish global optimality of a different explicit-gross-constrained
problem after a proportional gross reduction.

See [independent source review](V3_POLICY_REVIEW_20261029.md) and its
[research-to-production mapping](../evidence/v3_policy_audit_20261029/reference_source_mapping.json).

## 3. Keep the sleeve; describe its market dependence correctly

The original brief explicitly maximizes future net Sharpe and specifies a
whole-future-period regression beta below 0.2. It also asks for a market-hedged
book and says a strategy mostly long the market is unwanted. It does not state a
second numerical beta-equals-zero requirement. Our interpretation is to respect
the stated beta condition and explain the market component honestly. The observed
0.103 is compliant on the supplied sample, not proof of future compliance.

| Policy | Historical net Sharpe | Observed net market beta |
|---|---:|---:|
| E2 stock book, sleeve 0 | 1.3395817822 | 0.052981 |
| Selected V3, sleeve +0.05 | 1.4447333006 | 0.102978 |

The added sleeve improves historical Sharpe by 0.105152. It accounts for roughly
83.2% of the latest 0.126398 improvement over the prior F2-plus-volatility leader.
This percentage describes that sequential comparison; it is not a unique
decomposition of Sharpe. That increment is substantially market exposure. The whole strategy is a
different question: in the observed net-return regression, market R-squared is
10.16%, and beta times the market mean is 1.49 annual percentage points, or
22.56% of the portfolio's annual net mean. These are descriptive projections,
not identified causal alpha or a traded market-neutral result.

Claude's 1.286 calculation is a valid narrow sensitivity if the *added sleeve
alone* loses its mean contribution while the inner book, costs and final-book
volatility are held fixed:

    (mu_joint - 0.05 * mu_market) / sigma_joint = 1.2864659455.

It is not a full replay of a market with zero expected return. In particular,
leaving the no-sleeve comparator at 1.340 ignores its existing 0.053 market beta.
A consistent, explicitly limited common-market-mean adjustment is:

    S_j(nu) = [mu_j + beta_j * (nu - mu_market)] / sigma_j.

These are annual arithmetic means and annualized volatilities. This holds
observed beta, centered fluctuations, nonmarket means, covariance, positions and
costs fixed and changes only the common market mean. It yields:

| Assumed common annual market mean | With +0.05 sleeve | Without sleeve |
|---|---:|---:|
| Observed +14.4799% | 1.444733 | 1.339582 |
| 0% | 1.118774 | 1.165241 |
| -14.4799% | 0.792814 | 0.990900 |

Under those fixed assumptions the expressions cross at **4.4377%** annual market
mean. That is an algebraic sensitivity, with no uncertainty interval here; it is
not a market forecast, an optimal sleeve weight or a timing trigger to add to
the code. A different return-generating process could change the forecasts,
residuals, risk estimates, targets, drift and trading costs too.

The corrected comparison still favors removing the sleeve under zero market
mean. There is no need to hide that. Conversely, assuming a zero future market
mean is not new evidence that it will be zero. The fixed +0.05 remains the selected
policy under the user's score-first objective. Neither historical superiority
nor a frozen selection rule proves future dominance. Do not enlarge or tune the
sleeve to approach the beta limit as part of this integration.

Full derivation, source bindings and saved calculations:
[market review](V3_MARKET_REVIEW_20261029.md),
[mean-sensitivity output](../evidence/v3_market_challenge_20261029/mean_sensitivity_001.json),
[whole-book dependence output](../evidence/v3_market_challenge_20261029/total_dependence_001.json).

## 4. Completed verification and reporting disposition

The unchanged fifteen-check temporal workflow passed against the newly bound
original reference. Replacing future inputs and truncating the history at rows
600, 2000 and 3500 leave the declared prior forecasts and all three target
streams exactly equal. The cross-history restart also matches a fresh run
exactly. The current source and data bindings remain unchanged, actual CPU
affinity is `[1]`, and the three numerical thread settings are all `1` before
and after execution. Temporal-result SHA256:
`9d91f352f5bd650f76f58e2d84fc534ce8a111a24ce93a135b5f5c5322125e11`.
See [temporal result](../evidence/v3_evidence_audit_20261029/temporal_001/result.json).

The unchanged 25,200-row runtime workflow also passed. It used actual CPU
affinity `[1]` and `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1`,
recorded before and after execution. Source and input identities were unchanged.

| Century workload measure | Independent V3 result | Requirement |
|---|---:|---:|
| Forecast | 60.571067 s | Under approximately 3,600 s |
| Mean rebalance | 12.417117 ms | Under 100 ms |
| 99th-percentile rebalance | 33.501726 ms | Reported diagnostic |
| Maximum rebalance | 295.596324 ms | Reported diagnostic |
| Decisions / earning rows | 24,947 / 24,946 | Exact declared counts |
| Optimizer certificates | 49,894, all `ok` | Every solve accepted |
| Minimum one plus gross daily return | 0.9821459742 | Positive throughout |

The workload tiles the original input to 25,200 rows. It is engineering/runtime
evidence, not a century of new market observations. We did not compute or select
on its Sharpe. Full scalar certificates and the small runtime arrays are
preserved losslessly; the large tiled forecast is saved locally with its hash
and explicitly designated regenerable. Runtime-result SHA256:
`241cd9b1f78191f9d2cfb19a7f3c886fb2dcba769988b731a10a68ffa1f30ca1`.
See [runtime result](../evidence/v3_evidence_audit_20261029/runtime_001/result.json)
and [compressed evidence manifest](../evidence/v3_evidence_audit_20261029/runtime_packaging_001/manifest.json).

The actual-sample package replay averaged **15.856 ms** per rebalance, with a
maximum of **936.486 ms**. The requirement is an average below 100 ms, not a
per-call bound; a cause for the isolated maximum is not established. Keep that
actual-sample observation distinct from the measured century maximum above.

Other nonblocking reporting qualifications:

- The committed clean-folder CLI log displays Sharpe 1.44 and beta 0.10. It
  confirms clean-folder execution and the rounded score, not every decimal of a
  third full-precision comparison. The two full-precision comparisons and this
  independent exact-reference replay provide the numerical evidence.
- The inherited forced-failure harness exercises the shipped allocator and
  engine entry point. It does not force every fallback through the newly written
  `Book` and `ScorePolicy` wrapper. Static wiring is correct and normal-path
  certificates pass; this coverage limit is not a demonstrated wrapper defect.
- The failed missing-package and isolated-mode attempts are retained. Claude
  disclosed a self-killed first runtime launch, but its separate attempt log was
  not present among the 27 changed files inspected at the pinned commit. Do not
  invent that missing log or a passing result for the attempt.

## 5. Overfitting, causality and the next research decision

The entire supplied sample is now exposed development history. Pre-recorded
variant waves and the fixed sleeve weight help constrain researcher discretion,
but do not recreate an untouched holdout or account for every earlier experiment.
Paired fixed-policy bootstrap intervals do not correct the entire selection
history. Source inspection and altered-future checks address implementation
lookahead; they do not certify that a selected historical Sharpe will generalize.

The correct conclusion is a faithfully integrated, causally supported candidate
with a reproducible historical score and a declared market component. Future
Sharpe and future beta remain unknown. Keep this candidate as the baseline for
subsequent research; genuine improvement should be evaluated on total net
portfolio performance after actual combined trading costs, while separately
reporting market contribution. A new family of forecasts needs its own prospective
research specification; this integration review introduces none.

The applicant's contributions paragraph must remain in the applicant's own
words. Research/selection and integration/audit attribution must match actual
work. No external submission is part of this review.

## 6. Evidence retention and concrete handoff

The initial scope correctly recorded that the old large arrays were unavailable.
The new exact-hash recovery resolved that limitation. To avoid repeating it,
both actual-sample replay packets' numerical evidence is preserved as exact
file-byte aliases in a deterministic, lossless archive. It retains forecasts,
all three target streams, indices, controller traces, full scorer rows including
timing, certificates, daily CSVs and the associated result records. Identical
research/package files are deduplicated without regenerating array headers.

The archive has 24 original aliases, 18 distinct objects and 53 parts. Its
manifest SHA256 is
`3e487e00a671834c6a7cd80d638e5326da8adcb7b8f5723e9cc62e9d54028a12`.
Every part, the concatenated compressed archive and every decompressed object
passed byte-identity readback before publication; the original evidence remained
unchanged. [Restoration instructions](../evidence/v3_archive_20261029/README.md)
restore to a new destination without running a policy. The final deployment
folder remains small; the research archive is not a required strategy file.

The [Claude handoff](V3_CLAUDE_HANDOFF_20261029.md) contains precise documentation
corrections and the selected-policy decision. Private publication is on
`review/v3-integration-audit-20261029`, based on the pinned Claude commit. The
production branch and executable files are not edited by this review.
