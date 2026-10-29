# V3 integration accepted — concrete handoff to Claude

29 October 2026, Europe/Paris. Review of production
`978824d4b6140c43566ebd61a3ee8157f4080e35` against research
`9e56aa755d20c5876485188f4c50ce959f6d63f3`.

## Research decision

**Keep `POLICY.sleeve = 0.05`. V3 at historical net Sharpe 1.444733300556666 is
the current selected candidate and baseline to beat. Integration is accepted.**
No executable correction is required by this independent review. The following
items concern documentation and evidence. No new sleeve weight, forecast,
allocator parameter, test suite or candidate run is requested here.

The user's objective remains future net Sharpe under the original beta and
runtime requirements. The market component is intentional and should be
described openly. Switching the sleeve off is not justified merely by assuming
a zero future market premium, nor does the brief state a second beta-equals-zero
threshold. The observed beta passes on the supplied sample; future beta remains
unknown.

## Independent evidence now available

- Both pinned research and unchanged production reruns reproduce the original
  forecast and all three target streams **exactly**, matching the original NPY
  file and raw-array hashes, shapes and dtypes. Controller/indices also match
  between reruns; all economic rows match the original daily CSV exactly.
- Both score 1.444733300556666, with beta 0.10297751974238421, annual arithmetic
  net mean 6.6089525784%, annualized volatility 4.5745139091% and full annual
  mean costs 0.2537924949%. Each has 7,054 `ok` certificates.
- Your unchanged fifteen-check workflow passes against that exact original
  reference: altered futures, prefix histories and cross-history restart all
  preserve the declared protected outputs exactly.
- Your unchanged 25,200-row runtime code passes with recorded actual CPU affinity
  `[1]` and all numerical thread variables equal to one. Forecast: 60.571067 s.
  Mean rebalance: 12.417117 ms; p99: 33.501726 ms; max: 295.596324 ms. All
  49,894 certificates are `ok`; minimum one plus gross return is 0.9821459742.
- The separate actual-sample package replay had mean rebalance 15.856244 ms and
  maximum 936.485968 ms. Keep both workload results and do not assert a cause
  for the isolated slow call. The brief limits the mean, not every call.

See [integrated review](V3_INDEPENDENT_REVIEW_20261029.md) and
[independent evidence review](V3_EVIDENCE_REVIEW_20261029.md). The complete actual
positions are now retained in the lossless archive described
[here](../evidence/v3_archive_20261029/README.md).

## Documentation edits to make

### 1. Record the reference deviation and its subsequent resolution

Keep the original failed target-hash prerequisite visible. Replace the causal
assertion that a different machine explains the discrepancy with:

> The original integration rerun did not match the published target-array
> hashes, so its same-environment reference was a documented deviation from the
> original prerequisite. A subsequent independent replay of the pinned research
> and unchanged package recovered the original forecast and all three target
> streams byte for byte, and reproduced the original economic rows exactly.
> This resolves current fidelity; the precise cause of the earlier discrepancy
> was not established.

The new replay score differs from your reported 1.4447333005564316 by about
2.34e-13. This observation does not require a production change.

### 2. Correct the full-precision clean-folder claim

The committed clean-folder CLI log prints 1.44, beta 0.10 and its timings. State
that it confirms clean-folder execution and rounded score. The reference and
integration runs establish the full-precision comparison, supplemented by the
new independent exact-original replay. Do not present the rounded CLI log as
retaining every decimal of a third numerical comparison.

### 3. Replace the ambiguous zero-market wording

The 1.286 number changes only the added sleeve's mean contribution while keeping
the inner book, total-book volatility and costs fixed. It is not a rerun in a
market that earns zero. If presenting a common-market sensitivity, apply the
same changed mean to both portfolios, including the no-sleeve book's existing
0.053 beta:

| Assumed common annual arithmetic market mean | V3 +0.05 sleeve | E2 without sleeve |
|---|---:|---:|
| Observed +14.4799% | 1.444733 | 1.339582 |
| Zero | 1.118774 | 1.165241 |
| -14.4799% | 0.792814 | 0.990900 |

These use `[mu_j + beta_j*(nu-mu_market)]/sigma_j` with observed beta,
annualized volatility, centered fluctuations, nonmarket mean, positions and
costs fixed. They are descriptive sensitivities, not altered-market executions.
The conditional crossing is 4.4377% annual market mean. It has no uncertainty
interval here and must not be converted into a production timing rule.

Suggested short-note wording:

> The strategy includes a fixed +0.05 equal-weight stock sleeve before the shared
> gross limit, bringing observed total net beta to 0.103. It improves supplied-
> history net Sharpe from 1.340 to 1.445. This increment is market exposure.
> A common-market-mean sensitivity, holding measured betas, volatility,
> nonmarket means, positions and costs fixed, favors the no-sleeve book under
> sufficiently low market premia. These calculations are not replays on an
> altered market, and future market premium and beta remain uncertain.

### 4. Make the scope of certificates and failure-path coverage precise

Keep the successful inherited allocator/engine failure-path evidence. It does
not force every fallback through the new `Book`/`ScorePolicy` wrapper. The
independent source review found the wiring correct, and normal executions
certify every solve. This is a coverage qualification, not a discovered bug or
a request for another test suite. The inherited nonzero-beta gross-cap fixture
also reports `binding days 0`; it did not exercise the claimed binding branch.
That nonzero-beta mode is disabled in the selected V3 policy. Correct the
coverage description without turning it into a new release gate.
Certificates concern the solved subproblems;
they do not prove global optimality after a proportional gross-cap adjustment.

### 5. Preserve research uncertainty and actual attribution

All historical periods are exposed development data. The fixed waves and fixed
sleeve weight do not restore an untouched holdout. Altered-future checks support
causality on tested paths; they do not prove absence of overfitting or future
Sharpe. Keep the 0.3 factor-risk multiplier described as a chosen penalty,
not a calibrated variance forecast. The roughly 83% market share of the latest
Sharpe increment is a sequential comparison, not a unique Sharpe decomposition.

The applicant writes the human-contributions paragraph. Preserve actual GPT
research/selection and Claude integration/audit attribution. Do not invent
personal empirical findings. The final deployment needs only its existing
strategy/helper files; the large research evidence stays outside it.

## Scope of follow-up

Apply these documentation corrections while retaining the executable policy.
No additional economic rerun is needed for prose-only edits. V3 remains the
baseline for future research, whose hypotheses and comparisons should be
specified separately. This handoff does not authorize an external submission.
