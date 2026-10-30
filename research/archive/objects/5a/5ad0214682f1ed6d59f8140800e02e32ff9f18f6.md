# Literature review: local shape, persistence, and research discipline

**Reviewed 27 October 2026, Europe/Paris.** This note supports one already admitted experiment, C12. It is not a claim that published equity findings identify the supplied simulator. No validation or audit outcomes were inspected for this review. The user's “Xarchive” request is interpreted as arXiv. The review follows SSRN and author/institutional manuscripts, arXiv, and Alpha Architect as a route to original research.

## What changes our next experiment

The most useful remaining controlled contrast is a small local additive expansion. Our existing C02 global square can represent a smooth U-shape or inverted U-shape, but it cannot freely change slope near several fixed characteristic levels. C12 adds that limited flexibility while preserving the learner clock, original columns, and entire portfolio policy. The design is specified in [LOCAL_ADDITIVE_PLAN.md](LOCAL_ADDITIVE_PLAN.md); it is the twelfth original discovery configuration, not the beginning of a knot or penalty sweep.

This choice is deliberately tentative. A more flexible response function can fit noise, increase instability, and produce extra turnover. Published nonlinear success supplies a hypothesis; the exact unchanged scorer supplies the local economic comparison. The opposing literature result below is a reason to preserve a negative outcome rather than rescue the model with extra tuning.

## Sources and their bounded implications

### Additive characteristic functions

Freyberger, Neuhierl, and Weber, *Dissecting Characteristics Nonparametrically*, July 2018, study additive characteristic effects using rank-transformed characteristics, quadratic splines, and adaptive group LASSO. Their framework separates incremental characteristic information from the choice of functional form. That supports testing local responses, while its empirical success does not transfer automatically to this market. Our three fixed hinges and ridge estimator are a simpler adaptation, not their estimator. See the [BFI manuscript](https://bfi.uchicago.edu/wp-content/uploads/we6b7o-WP_2018-50.pdf), Section II and the appendix, and [institutional landing page](https://bfi.uchicago.edu/working-paper/dissecting-characteristics-nonparametrically/).

**Version/access caution:** the institutional page links to [SSRN abstract 2820700](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2820700), whereas the inspected July 2018 PDF cover prints `ssrn.com/abstract=3147101`. The SSRN page did not load in this session. We cite the inspected institutional PDF and retain the discrepancy; we do not assert that these identifiers represent identical bytes or silently substitute one version for another.

Gu, Kelly, and Xiu, *Empirical Asset Pricing via Machine Learning*, September 13, 2019 author manuscript, supplies useful counterevidence. In its monthly empirical comparison, the additive spline GLM did not beat purely linear methods; trees and neural networks benefited from richer interactions. That is evidence against assuming that every univariate nonlinear expansion will help. It also does not establish that a larger model is appropriate for our thirteen-characteristic daily setting. See [author manuscript](https://dachxiu.chicagobooth.edu/download/ML_BKP.pdf), Section 3.2, especially PDF page 27.

### Costs and persistence

De Lataillade, Deremble, Potters, and Bouchaud, *Optimal Trading with Linear Costs*, [arXiv:1203.5957](https://arxiv.org/abs/1203.5957), derives threshold behavior in a capped-position setting and links it to a no-trade band under quadratic risk. This supports reasoning about the interaction of predictive strength, persistence, and proportional fees. It does not provide a drop-in solution for our constrained thousand-stock portfolio. The existing absolute-turnover penalty already embodies a cost-sensitive adjustment mechanism; adding another arbitrary buffer would need a separate, counted hypothesis.

Alpha Architect's [trading-costs review](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/) and [factor transaction-cost discussion](https://alphaarchitect.com/transaction-costs/) were accessed as research indexes. Their links led toward the Frazzini–Israel–Moskowitz transaction-cost work; the linked SSRN and author-paper targets did not load during this retrieval. The indexed [smart-rebalancing discussion](https://alphaarchitect.com/can-smart-rebalancing-improve-factor-portfolios/) was available in search output, while a direct open returned HTTP 403. We do not treat these secondary summaries as a new technical calibration or substitute their cost estimates for the assignment's supplied costs.

### Selection optimism

Bailey and López de Prado, *The Deflated Sharpe Ratio*, July 31, 2014, explicitly addresses selection among multiple trials and non-normal returns. Its calculation needs a defensible account of the attempted search and trial dependence. See [author-hosted manuscript](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf), whose cover identifies [SSRN 2460551](https://ssrn.com/abstract=2460551). Here, eleven related scored configurations are not eleven independent trials, and exploratory diagnostics and design decisions also influenced selection. An unexplained trial count would make a precise-looking adjustment misleading.

Harvey and Liu, *False (and Missed) Discoveries in Financial Economics*, [arXiv:2006.04269](https://arxiv.org/abs/2006.04269), emphasizes the tradeoff between false discoveries and missed discoveries when calibrating multiple tests. The practical lesson for this task is to report uncertainty and negative results without claiming either that a promising development score proves alpha or that a weak contrast proves alpha impossible. We have not implemented their bootstrap procedure and make no paper-derived statistical certification.

## Correcting two tempting interpretations

These are mathematical and research-design observations, not new empirical findings.

**A marginal sign reversal does not by itself identify a changing structural coefficient.** In a centered linear model `Y = sum_k beta_k X_k + epsilon`, with the error uncorrelated with the features, the marginal covariance is

```text
Cov_t(X_j, Y) = sum_k beta_k * Cov_t(X_j, X_k).
```

The marginal association can change sign when predictor covariances change, even if all joint coefficients remain fixed. Conversely, the coefficients may truly change. The initial diagnostics do not distinguish these mechanisms. Joint causal estimation is therefore a more defensible response than hard-coding the dates on which a one-variable relationship reversed.

**Characteristic persistence, signal persistence, and persistence of predictive value are different quantities.** A feature that changes little from day to day can carry an unstable or negligible return premium. A stable nonlinear shape can also fail to survive estimation error or trading costs. Slow feature motion suggests potential turnover advantages; it is not sufficient to choose a longer forecast horizon or a longer coefficient half-life. C12 consequently holds both the one-day label and 252-day coefficient half-life fixed.

## Why the exact C12 scaling is a research-quality improvement

The new hinge columns overlap strongly with the linear and squared columns already present. In a standard-normal reference distribution, the residual hinge component after removing those two directions has standard deviation about 0.106–0.118 at the fixed knots. Penalizing the unscaled hinge coefficient can therefore make the genuinely new direction much more heavily shrunk than its nominal ridge number suggests.

C12 specifies an analytic residualization and scaling convention before reading any C12 output. This makes the intended comparison inspectable without fitting normalization parameters to the whole sample. It does not whiten the observed data, make the three local terms independent, or discover an optimal penalty. The `0.3` local penalty remains a fixed design choice with real bias/variance consequences. All characteristics get the same treatment, including those that looked unpromising in prior exploratory diagnostics.

## Admitted and unadmitted ideas

| Idea | Current status and reason |
|---|---|
| Local additive shape at three fixed knots for all thirteen characteristics | Admitted as C12, paired with C02 and evaluated after full costs. |
| Another arbitrary no-trade buffer | Not admitted; partly duplicates the current absolute-turnover cost objective and changes execution at the same time. |
| Switching directly to neural networks because one paper reports gains | Not admitted; changes model complexity and tuning burden substantially without local evidence or spare budget. |
| Selecting only the few characteristics with favorable standalone nonlinear diagnostics | Not admitted; compounds selection and discards the controlled all-feature comparison. |
| A new grid of memory half-lives, knots, local penalties, or labels | Not admitted; would consume additional selectable configurations and requires a visible prospective protocol change. |
| Computing DSR/PBO and declaring the project free from overfit | Not supported; the selection process and effective trial dependence must first justify such a calculation. |

## Evidence that would change our conclusion

C12 must pass the independently specified synthetic and source gates before its single discovery evaluation. If its net Sharpe does not exceed C02 under the same mask and scorer, the declared local-shape contrast is a negative result. A gross-only improvement would be insufficient. If it improves the paired net result, it remains a development finding shaped by prior research exposure; it can inform nomination only under the existing protocol.

Future-data alteration checks answer whether tested past decisions depend on information from the altered future. They do not measure selection optimism. Untouched chronological validation and the one-candidate sealed audit provide a different kind of evidence, provided the policy is frozen and results do not trigger undisclosed redesign. No finite collection of these checks can promise that the unseen continuation will be profitable.

Progress is governed by these evidence gates. This review creates no calendar execution schedule.
