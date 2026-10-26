# Independent review of discovery interpretation and causality harness

**Reviewer:** alpha-review agent, distinct from the diagnostic authors.  
**Scope:** existing alpha/risk evidence, recorded plans, diagnostic source, and the preimplementation causality E2E harness. No new data scan, candidate portfolio evaluation, validation/audit inspection or postimplementation unit test was performed.

## Decision

The recorded diagnostics justify the proposed first comparison of an adaptive joint linear model and a small additive nonlinear challenger. They do not yet establish a tradable edge, beta compliance or net profitability. The recorded findings maintain that distinction and preserve contrary evidence.

The alpha run reports 123 passing workflow checks, exit 0 and 135,122 daily diagnostic records. The risk run reports nine passing workflow checks and exit 0. Review of the code agrees with the stated discovery-only scope and date alignment. These are reviews of completed evidence and source, not independent numerical reruns.

## Alpha interpretation

The most consequential facts in [ALPHA_FINDINGS.md](../research/ALPHA_FINDINGS.md) are supported by the stored summaries:

- Woe and Dread have positive controlled mean ICs in the first two fixed blocks and negative ICs in the final two. Permanent favorable signs would be an unsupported simplification.
- Next-day Snap, Crackle and Pop curvature contrasts are negative in all four fixed blocks. The diagnostic selected the contrast before outcomes, retained all thirteen characteristics and reported small/contrary cases. This earns a restrained additive challenger, rather than proof of a universal quadratic response.
- Feature rank persistence near 0.999 at one day and near 0.98 at twenty days supports investigating low-churn holdings. Changing coefficients, prices, risks and hedges can still create substantial portfolio turnover.
- Correlated characteristics and correlated residual returns mean that thirteen individual ICs are not thirteen independent sources of alpha. The longer-horizon labels also overlap. No stock-day iid significance claim is warranted.

The code's `X[s]` label begins at `R[s+1]`; its trailing beta includes rows `s-251 ... s`, and the forward horizon ends within its assigned block. The one-day descriptive count of 1,763 is consistent with including discovery return row 2015. The later official portfolio count remains 1,762 because that scorer does not earn the final input return. This difference is intentional and documented, not an off-by-one correction to make later results look better.

The standardized linear slope is correlation multiplied by cross-sectional label standard deviation, and the fixed curvature is `(Q1+Q10-Q5-Q6)/2`. Neither is a portfolio net return. Quantile tie handling uses average ranks; actual evidence reports no empty buckets or undefined ICs.

## First candidates: details to freeze before scoring

Keep all thirteen characteristics in the joint model. For C02, add the same predefined squared basis for every characteristic and regularize jointly; do not hand-select Snap/Crackle/Pop because their curves look attractive. Retain linear terms because observed curves need not be symmetric. Per-date centering/scaling and bounded basis construction are causal if they use only the panel available for the forecast date.

At forecast row `t`, the latest matured training pair is `X[t-2] -> R[t-1]`; prediction uses `X[t-1]`. A residual training target must use the stock-beta estimate available before its label return. A historical pooled diagnostic beta cannot be reused inside the deployed learner.

A fixed 252-day exponential half-life is a defensible starting hypothesis, not a learned optimum. Normalize the exponentially weighted Gram matrix and target moment consistently so that the intended ridge strength is stable as the warm-up mass accumulates. If a faster adaptation alternative is later selected, declare and count it before viewing its portfolio result. Keep forecasting and portfolio configuration identical across C01/C02 except the specified basis, so the first contrast has a clear interpretation.

The proposed exact estimated-beta equality and stock-specific no-trade cost penalty fit the stated objective. Report residual-covariance limitations, and keep full actual costs in the official evaluator. A diagonal-risk baseline can be useful without being described as a complete hedge of all common risk. Additional details are in [RISK_FINDINGS.md](../research/RISK_FINDINGS.md).

## Causality harness review

The inspected `tools/verify_causality.py` correctly invokes the original scorer, starts a new Python interpreter per scenario, freezes sibling Python helpers, hashes input arrays before/after, and checks protected forecast, target and economic outputs. Its boundary rules agree with the preregistered plan:

| Alteration starts at row `c` | Protected comparison |
|---|---|
| Forecasts | All channels through row `c`, inclusive |
| Targets | Earning days at or before `c` |
| Gross/cost/exposure/market and net ledger | Scored days strictly before `c` |

The prefix and synthetic-append cases account for the scorer's terminal omission. Timing is excluded from numerical equality. Empty target/ledger ranges are recorded as not applicable. Nonzero worker exits, incomplete workers and input mutations cannot become a successful comparison merely because a status file exists. A failed suffix is explicitly not diagnosed as earlier leakage without a completed comparison.

### Integration items to resolve before execution

1. **Candidate configuration:** at review time the harness reads `CONFIG` for recording but has no `--config` argument and does not call `configure()`. It therefore tests only the imported module default. Either freeze a candidate-specific default module or add explicit frozen configuration handling before the first C01/C02 runs. A C01 default pass cannot be labelled a C02 pass.
2. **Startup boundaries:** the default cutoff 252 has no protected target because the first target earns row 253. Add cutoff 253 and the first-active forecast boundary determined by the fixed warm-up policy. With 252 completed pairs, that first forecast is row 253; with 126 pairs it is row 127. Record these choices before numerical execution.
3. **Scope:** the 600-row smoke profile is deliberately limited. A pass must not claim later discovery dates, multi-decade runtime, unseen histories or universal causality. Independent candidate/helper source review remains necessary, including external data access and hidden cross-call state.

These are E2E integration requirements, not newly written isolated tests. No causality execution has been performed by this reviewer.

## Acceptance boundary

Proceed to the first preregistered, fully charged discovery portfolio comparisons once code/configuration identity and the above integration items are fixed. Preserve failures and negative results. The reserved validation/audit data remain closed; promising descriptive contrasts do not open those gates.
