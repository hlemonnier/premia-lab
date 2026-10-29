# Next forecast hypothesis: conditional characteristic premia

29 October 2026, Europe/Paris. F3 completed the released original-scorer workflow
and did not improve the score: net Sharpe **1.2943927925112546**, against
**1.318334966090838** for F2 + VTvol. All specified operational checks passed.
F3 is rejected under the frozen economic rule and is ineligible for the
conditional composition. No state, ridge or feature tuning follows this result.
The prospective specification remains unchanged in
[PLAN.md](../../evidence/v2_score2_forecast_20261029/PLAN.md).

## Prospective hypothesis

Reserve one F3 experiment: let the existing characteristic premia vary with a
single bounded causal market-volatility state. Compare its complete F3 + VTvol
policy with F2 + VTvol, whose established research net Sharpe is 1.3183349661.
Do not add another polynomial/spline grid. Existing C11/C12 negatives provide
weak grounds for spending the next forecast experiment on larger static shapes.

F2 gives linear coefficients partly faster memory. VTvol changes the size of
the whole book. F3 asks a different question: can a market-risk condition change
the relative expected payoffs of the 26 characteristic directions? Its new
date-specific predictions stay in the existing characteristic risk span.

## Exact policy

Using market return m_s=mean_i R[s,i], compute normalized EW63/EW1008 second
moments through each published close s. After 63 observations define

    c_s = clip(log(max(q1008_s,1e-12)/max(q63_s,1e-12))/(2*log(2)), -1, 1),

and use zero before that. There is no fitted state normalization. State +1/-1
corresponds to recent volatility half/double its long reference, before floors
and clipping.

Append c_s times each of the 26 existing characteristic columns to the original
27-column design, producing 53 columns. Both H1008/H252 fits use ridge 0.1 for
the original 27 and 1.0 for the new 26. Combine only the first 13 linear coefficients
50/50; retain all other slow coefficients. This refits all columns jointly.

For the label at s+1, the state may see returns only through s. Prediction row
t uses X[t-1], beta[t] and c_(t-1); its newest training pair is X[t-2] with
c_(t-2) against residual R[t-1]. The conditional beta interaction is excluded.

The risk model and allocator remain unchanged, and the existing VTvol controller
must use the new F3 virtual book. Stronger state shrinkage, bounded state,
fixed windows and one candidate reduce discretion; they cannot certify absence
of selection overfit. The original net scorer decides the economic contrast.

## Research grounding and counterarguments

[DeMiguel, Martin-Utrera and Uppal (2024)](https://doi.org/10.1111/jofi.13395)
distinguish conditional multifactor weights from timing one fixed combination,
and incorporate transaction costs. That distinction motivates this experiment;
the exact state, ridge and forecast design are local choices, not a replication.
The [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3982504)
and full publisher HTML were inspected.

[Freyberger, Neuhierl and Weber](https://www.nber.org/papers/w23227) motivates
flexible characteristic functions with regularization, while
[Gu, Kelly and Xiu](https://www.nber.org/papers/w25398) supplies counterevidence
that additive spline expansions need not beat simpler methods. The existing
local negative results make this an unattractive immediate repeat. The
[Feng-He arXiv paper](https://arxiv.org/abs/1902.01015) supplies broader context
on heterogeneous conditional coefficients and estimation risk; no Bayesian
rewrite is justified by the present local evidence.

F3 can fail because the market state only predicts risk, already handled by
the allocator; because the weak conditional-mean relationship cannot support
26 additional coefficients; or because changed exposures and costs absorb a
gross gain. All supplied periods are development history. The predeclared
complete-workflow verification and independent source review precede any actual
score; lower MSE or a favorable explanatory story cannot promote F3.

## Implementation and synthetic verification checkpoint

Root admitted the exact F3 policy before implementation. The prospective
[E2E specification](../../evidence/v2_score2_forecast_20261029/E2E_SPEC.md) and
executable harness preceded prototype.py; the expected missing-policy run
exited 3 with zero economic runs. The first implemented workflow then exposed
a NumPy-boolean JSON serialization issue after its F2 zero-market control,
before any F3 execution. A single explicit bool cast repaired that existing
check without changing its assertion, tolerance, fixture or model. The failure
and original source remain recorded in
[FAILURES.md](../../evidence/v2_score2_forecast_20261029/FAILURES.md).

The unchanged policy subsequently passed all 10 summary checks and 120
per-workflow checks across 8 complete synthetic scorer runs. Future, prefix
and cross-history restart outputs match exactly. The direct weighted-regression
oracle matches forecasts to 1.03e-18; independent state reconstruction differs
by at most 1.67e-15. When the market state is zero, forecast differences from F2
are 2.17e-19, target differences 1.0010648351932439e-9 and economic differences
7.40e-10, within the prospectively fixed 1e-8 downstream tolerance.

The known conditional coefficient direction is recovered. Its overall
forecast/truth correlation is 0.441, reported as a synthetic diagnostic rather
than a profitability or admission threshold. The oracle verifies the specified
strongly shrunk estimator, not an ideal unregularized conditional forecast.
See [synthetic_002/result.json](../../evidence/v2_score2_forecast_20261029/synthetic_002/result.json).

The independent reviewer accepted the frozen source and passing workflow with
no required changes, independently checking all 64 atomic arrays and 120
per-workflow assertions. The review is recorded in
[forecast_source_review.json](../../evidence/v2_score2_review_20261029/forecast_source_review.json).
At that checkpoint, actual-market F3 scoring and the optional long-history
runtime mode remained unexecuted and required a source-bound root release.
The subsequent authorized actual run is recorded below. Production code and
the original scorer are unchanged.

## Released actual-market result

Root committed the master plan at
`d2997e0d98c6407da4b503a77060966904486062` before any new policy outcome,
then released the exact six source/specification files, independent review,
synthetic result and ce3 baseline identities in
[F3_ACTUAL_RELEASE.json](../../evidence/v2_score2_root_20261029/F3_ACTUAL_RELEASE.json).
The run used CPU 1 and one BLAS/OpenMP thread, exited 0 and produced no stderr.
Only the prospectively specified baseline, F3, altered-future and prefix paths
were executed. These are four workflow runs and one new economic candidate.

| Original scorer metric | F2 + VTvol | F3 + VTvol |
|---|---:|---:|
| Full net Sharpe | 1.3183349661 | 1.2943927925 |
| Discovery net Sharpe | 1.1035119417 | 1.0898200725 |
| Validation net Sharpe | 1.6339700633 | 1.5708339738 |
| Audit net Sharpe | 1.5930290673 | 1.5769908430 |
| Annualized net return | 5.786507% | 5.698352% |
| Annualized net volatility | 4.389254% | 4.402336% |
| Annualized trading costs | 0.336406% | 0.344646% |
| Gross Sharpe | 1.3971448452 | 1.3748770274 |
| Realized net market beta | 0.0527203547 | 0.0532341489 |
| Mean gross exposure | 1.8236404524 | 1.8199405946 |

All stage labels describe exposed development history. The fixed masks are
unchanged: full earning rows 253..3778; discovery [253,2015), validation
[2016,3023), audit [3024,3779), with zero-based indices and exclusive upper
bounds. The full metric has 3,526 observations; the historical stage masks
omit their two original transition rows and were not adjusted for this run.

The full net Sharpe change is **-0.02394217357958328**. Net annualized return
falls by 8.815 basis points, of which 0.824 basis points is the increase in
annualized costs. Gross annualized return also falls by 7.992 basis points, and
gross Sharpe is lower. The shortfall is therefore already present before fees;
costs add a smaller deterioration. Mean exposure and market beta barely change.
This rejects this exact conditional forecast under the chosen score objective.
It does not establish that every conditional-premia model fails, or statistically
prove that the market state contains no predictive information.

The baseline net score reproduces exactly. The maximum difference in the four
saved daily economic columns versus the preceding CSV is 4.44e-16, well inside
the prospectively fixed 1e-8 tolerance. F3 uses its own virtual holdings and
its own causal VTvol history throughout.

## Actual verification and evidence

All six summary checks and all 60 per-workflow checks across the four actual-data
runs pass. At the predeclared future-alteration boundary, all 1,501 protected
forecast rows, 1,248 decisions and 1,247 earning rows match exactly. The pure
prefix produces the same exact equality. Independent market-state reconstruction
differs by at most 6.15e-15. Stock-level accounting error is exactly zero; opening
is free, the final rebalance is charged, drift and controller timing agree,
inputs are unchanged, and every one of the 3,527 candidate solves is certified.
The path is finite and solvent, stock/gross bounds pass, and absolute net beta
is below 0.2.

On CPU 1 with one thread, candidate forecasting took 3.740 seconds; instrumented
mean rebalance time was 3.489 milliseconds and the 99th percentile was 5.555
milliseconds. These are measurements on the supplied 3,780-row input. The
optional 25,200-day runtime stress remains unexecuted because the candidate
does not qualify economically; the ordinary run is not relabeled as that gate.

The original scorer, production files and six release-bound sources remained
unchanged. The complete result and readback identities are in:

- [actual_001/result.json](../../evidence/v2_score2_forecast_20261029/actual_001/result.json).
- [actual_001/economic_comparison.json](../../evidence/v2_score2_forecast_20261029/actual_001/economic_comparison.json).
- [F3_VTvol/array_manifest.json](../../evidence/v2_score2_forecast_20261029/actual_001/F3_VTvol/array_manifest.json).

The candidate retains targets.npy (3,527 by 1,000), rows.npy (3,526 by 5),
forecast.npy (3,780 by 1,000), virtual targets, decision indices and learner
traces. Every NPY was written atomically and reopened for complete hash readback.
Root's separately predeclared independent accounting and paired block-interval
analysis can use these saved outputs without rerunning the policy. Its outcome
is separate from this harness verification. No new forecast alternative is
selected or executed from the F3 negative result.
