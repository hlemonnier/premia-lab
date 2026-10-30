# Discovery handoff after C01–C10

**Scope:** independent review of the ten saved discovery summaries only. No new forecast, numerical market scan, strategy execution or reserved-period access was performed for this handoff. Sources are `evidence/discovery_C01_001/summary.json` through `discovery_C10_001/summary.json`. Every run uses the same original-scorer1,762-return discovery window, indices253–2014, and continuous initialization. C11 is pending and is not ranked here.

## Main assessment

We have a reproducible, low-beta research pipeline and several working construction methods. We do **not** yet have strong evidence of a durable high-Sharpe edge. The best development score is C06 at0.763, with several alternatives close behind. Small score differences after adaptive research are not reliable evidence of superiority on the hidden continuation.

The ten runs produced useful discrimination. Rapid adaptation was harmful, the first additive expansion added little, factor risk and covariance-weighted learning interacted, exact gross allocation improved fees, and extra covariance rank did not improve on rank10. These are bounded development findings rather than a recovered description of the simulator.

## Complete comparison

Fees below are annualized actual one-way trading charges, expressed as a percentage of capital; they are not the cost penalty used inside an optimizer.

| ID | Controlled change | Net Sharpe | Gross Sharpe | Net beta | Annual fees | Mean candidate ms |
|---|---|---:|---:|---:|---:|---:|
| C01 | Linear benchmark | 0.6223 | 0.7162 | 0.0172 | 0.652% | 9.68 |
| C02 | Add thirteen squares | 0.6376 | 0.7501 | 0.0212 | 0.777% | 14.69 |
| C03 | C02 half-life63 | 0.1065 | 0.3514 | 0.0282 | 1.727% | 11.17 |
| C04 | C02 plus rank10 factor risk | 0.6542 | 0.8820 | 0.0076 | 0.822% | 24.97 |
| C05 | Covariance-weighted alpha, diagonal portfolio | 0.6025 | 0.7071 | 0.0163 | 0.588% | 11.60 |
| C06 | C05 alpha plus C04 factor portfolio | **0.7629** | 0.9631 | 0.0063 | 0.681% | 27.85 |
| C07 | C02 with exact joint gross budget | 0.6798 | 0.7460 | 0.0235 | 0.498% | 25.75 |
| C08 | C02 risk aversion5000 | 0.6262 | 0.6912 | 0.0063 | 0.124% | 7.81 |
| C09 | C02 half-life1008 | 0.7002 | 0.7860 | 0.0144 | 0.588% | 9.39 |
| C10 | C06 rank50 in learner and portfolio | 0.7399 | 0.9592 | −0.00009 | 0.514% | 27.88 |

All ten completed their scoped scorer workflows, observed finite outputs/solvency, passed the recorded absolute-beta and average-time feasibility flags, and obeyed their declared stock/gross bounds. This is not a blanket causality, long-history or release approval. Shared-host timing outliers remain in the evidence; averages must not be presented as maximum latency guarantees.

## What the controlled contrasts support

**C01/C02: the observed marginal curvature was not a large portfolio breakthrough.** Adding all thirteen squared terms improved development net Sharpe by only0.0152. The diagnostic curves justified the test, but did not establish large incremental tradable alpha. A more faithful response model remains a research question; C11's all-pair interaction test addresses one specific alternative.

**C03/C09: descriptive sign changes did not justify fast forgetting.** The63-day half-life reduced both gross and net Sharpe substantially and increased costs. The1,008-day half-life improved pooled net Sharpe modestly over252 days, but its final fixed block was weaker (0.181 versus0.393). These results are consistent with a variance-versus-adaptation tradeoff; they do not prove permanent coefficients or identify true regimes. Do not hard-code regime dates from this history.

**C04/C05/C06: alpha estimation and risk allocation interact.** The rank10 risk model improved gross Sharpe over C02 but only slightly improved net Sharpe. GLS learning alone did not improve C02. Applying the factor portfolio to the same GLS forecasts did improve the complete net result (C06 versus C05). This supports carrying a coherent learner/portfolio candidate forward; it does not prove the asserted common-shock mechanism or justify saying GLS is universally better. The recorded forecast-identity comparison is stronger evidence for the C05/C06 construction contrast than their names alone.

**C07/C08: proportional scaling had a real fee cost, but fixing it did not transform the alpha.** C07 preserved exactly the C02 forecast artifact, solved the gross budget jointly, and lowered annual fees from0.777% to0.498%; gross Sharpe was essentially unchanged. Raising risk aversion eliminated rescaling too, but produced no useful pooled Sharpe gain. Exact optimization is a valid construction contribution, not sufficient reason to prefer C07 over better-scoring candidates.

**C10: more residual factors did not earn superiority.** Rank50 reduced return, risk and fees, with gross Sharpe essentially unchanged relative to C06 and slightly lower net Sharpe. Its lower absolute volatility/drawdown or nearly zero beta must not displace the frozen objective. The result does not justify another rank grid, nor prove that ranks11–50 contain no useful risk information.

## Provisional shortlist logic

The evidence-ranked pool before C11 is **C06, C10, C09**, with C07 next. This is a transparent starting point for the lead's final nomination, not a claim that these candidates have completed every engineering eligibility gate. C11 may change the pool after its one admitted result and review.

There is a defensible methodological argument for retaining a simpler, distinct construction such as C07 instead of two closely related covariance variants, but that would be an explicit nomination decision made before validation, not a numerical tie: the frozen tie tolerance is1e-6 and these scores are not ties. The lead should record the actual reasoning and final maximum-three candidate identities before opening either validation block. Do not invent a new per-block profit floor, silently promote an unscored combination of components, or change the final pooled-net-Sharpe selection rule.

C06 is the clearest present lead because it has the highest development net score. C10 is a useful unresolved rank comparison, not an improved version by definition. C09 represents the longer-memory alternative but has a visibly weak final discovery block. C07 is a verified cost-policy improvement and useful explanatory evidence; this review does not favor it merely because this reviewer implemented it.

## Remaining decisions and claims

Complete C11's source review and preregistered synthetic workflow, then its authorized economic run. The lead decides whether that result earns any final controlled follow-up; this handoff authorizes none. Before validation, freeze nominees, simplicity ranks, code/configuration identities and relevant causal/runtime/output gates. The validation ranking remains pooled daily net Sharpe under the original beta and engineering eligibility conditions. Only one selected configuration may enter the reserved audit under the frozen protocol.

Keep the final employer note candid: these ten results support a disciplined research process and measured engineering contributions. They do not support a claim of exceptional hidden-future performance, recovery of the simulator, or invented applicant discoveries. Negative findings and AI attribution remain part of the deliverable.
