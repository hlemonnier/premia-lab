# Persistence, trading costs, and the next admissible experiment

**Independent literature review, 27 October 2026, Europe/Paris.** Scope: primary papers and publisher records reached through SSRN, arXiv, and Alpha Architect; comparison with this project's existing cost-aware allocator. No market experiment, holdout access, or additional configuration is admitted by this review.

## Findings that affect the research direction

There is a useful distinction between a characteristic that changes slowly and an expected return that persists. If the response coefficient changes or the response function changes shape, a persistent characteristic can have a less persistent forecast. A long forecast-estimation half-life is a third concept: it controls how slowly the fitted mapping forgets observations. These three quantities should not be substituted for one another. The supplied market's discovery diagnostics motivate a hypothesis, but they do not measure an optimal holding horizon.

Similarly, a change in a marginal characteristic-return association does not by itself establish a change in the underlying multivariate coefficients. Under a fixed linear response, `Cov(X_j,Y)_t = sum_k Cov(X_j,X_k)_t * beta_k`; changing predictor covariances can reverse a marginal relationship. A joint adaptive fit and a local nonlinear contrast can address different explanations without choosing individual features from their best-looking univariate results. These are mathematical observations about identification, not findings that the anonymous simulator has a particular mechanism.

### Dynamic trading: useful principle, different cost model

[Gârleanu and Pedersen, *Dynamic Trading with Predictable Returns and Transaction Costs*, March 2012 author manuscript](https://nbgarleanu.github.io/DynTrad.pdf), particularly Sections 2–3, connects optimal dynamic trades to the evolution of expected returns. More persistent return predictors receive greater weight in the dynamic target. The framework explicitly uses quadratic trading costs; the paper distinguishes its partial-adjustment policy from the no-trade regions associated with proportional costs. Its closed-form policy therefore cannot be copied into our proportional-cost scorer without changing the problem. The useful transferable question is whether anticipated signal persistence is represented sensibly in decisions, not whether a published quadratic-cost formula improves this market.

**Project inference:** the current twenty-day cost amortization is an approximation whose adequacy remains empirical. A learned decay model, different horizon, or dynamic execution policy would constitute an additional predictive/portfolio choice and would need prospective admission. This review does not tune that horizon or grant another trial.

### Linear costs: retain the no-trade logic already present

[de Lataillade, Deremble, Potters, and Bouchaud, *Optimal Trading with Linear Costs*, arXiv:1203.5957](https://arxiv.org/abs/1203.5957) studies linear costs with a strict position cap. In its single-market formulation, optimal switching depends on a predictor threshold; it also relates that threshold to a no-trade band in a quadratic-risk formulation. This supports the economic importance of withholding weak trades under proportional costs. It is not a solution to our thousand-stock problem with coupled beta constraints and estimated residual risk.

**Project inference:** the existing allocator already optimizes expected return against risk and an absolute trading-cost penalty around actual drifted holdings. Adding an arbitrary buffer on top may duplicate that mechanism, alter the beta hedge, or create another tuning dimension. A new buffer is lower priority than establishing whether the conditional-mean representation contains useful information after the unchanged full cost charge.

### Alpha Architect route: prioritize useful trades, verify the primary source

The [Alpha Architect smart-rebalancing article](https://alphaarchitect.com/can-smart-rebalancing-improve-factor-portfolios/) was directly readable in this review. It led to the publisher's [Arnott, Li, and Linnainmaa, *Smart Rebalancing*, Financial Analysts Journal 80(2), 2024](https://rpc.cfainstitute.org/research/financial-analysts-journal/2024/smart-rebalancing), DOI `10.1080/0015198X.2024.2317323`. The public publisher abstract describes concentrating turnover in stronger signals and reducing implementation costs relative to fully rebalanced long-only paper portfolios. The complete article is marked premium/member content and was not read here. No detailed threshold, performance figure, or priority-policy ranking is treated as independently verified from the full paper.

**Project inference:** this route reinforces evaluation of net outcomes and economically useful turnover. It does not establish that a second discretionary trade-ranking layer improves the existing joint optimizer. Our full cost ledger, exposure limits, and actual drift are therefore held fixed for C12, so its comparison with C02 isolates the new forecast representation.

### SSRN cost taxonomy: provenance and access limits

Search resolved [Novy-Marx and Velikov, *A Taxonomy of Anomalies and their Trading Costs*, SSRN 2535173](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2535173), and the associated [NBER working paper 20721](https://www.nber.org/system/files/working_papers/w20721/w20721.pdf). The indexed primary abstract concerns after-cost anomaly performance and cost mitigation. Direct NBER retrieval returned HTTP 403; the author's Rochester PDF timed out. This review records that useful research lead but does not present a blocked full paper as read or base an implementation on unverified numerical results.

## Decision for this project

C12 is a fixed local-additive response experiment, not another risk, cost, or leverage change. It keeps every C02 portfolio parameter, all thirteen characteristics, the information clock, the source scorer, and the exact discovery mask. Its purpose is to test whether local slope changes add information beyond the original global quadratic basis. The local penalty and reference scaling were fixed before implementation; there is no knot or penalty search.

The independent synthetic workflow checks whether the complete implementation can learn a deliberately strong known local response and remain unchanged on protected decisions when future inputs are altered. A separate exact-zero-return path checks that the system remains in cash and reports variance-based metrics as undefined. Those are engineering checks. They cannot turn a discovery performance difference into evidence of tradable alpha.

All twelve admitted configurations and all earlier exploratory decisions belong to the selection history. C12's specification is prospective relative to C12, but the discovery sample has already influenced research direction. The continued protection is an unchanged nominated policy on chronological validation and the sealed audit, after accounting, causality, runtime, and independent review gates. No probability-of-overfit or deflated-Sharpe number is manufactured from the fiction that the observed configurations were independent, exhaustive trials.

No further candidate is admitted here. In particular, a fixed ordinary/GLS blend, multi-day labels, residual-return predictors, learned signal decay, and extra no-trade filters remain proposals requiring separate visible decisions. Negative C12 results must be retained without changing its fixture, penalty, knots, or acceptance rule. The next action is determined by evidence; there is no fixed calendar execution schedule.

## Retrieval record

| Source | Route and observed access | Use in this review |
|---|---|---|
| Gârleanu–Pedersen author PDF | Opened full 69-page manuscript; quadratic-cost discussion located | Dynamic-persistence principle and cost-model mismatch |
| arXiv:1203.5957 | Opened author/title/version/abstract record | Linear-cost threshold and no-trade-band connection, within stated scope |
| Alpha Architect smart rebalancing | Opened full article and followed publisher link | Discovery route, not sole technical authority |
| CFA Institute publisher record | Opened public abstract; full article member-gated | Limited claim about prioritizing stronger trades and implementation costs |
| SSRN2535173/NBER20721 | Search metadata/abstract resolved; full NBER blocked, author PDF timed out | Research lead and access limitation only |

This is AI-produced research and verification work. The user's report of having observed similar broad discovery patterns is acknowledged in the central contributor ledger; no additional human analysis or code is invented here.
