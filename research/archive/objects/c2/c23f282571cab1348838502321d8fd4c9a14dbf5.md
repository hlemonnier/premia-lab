# Literature follow-up: what remains worth testing

**27 October 2026, Europe/Paris.** Independent follow-up to the two existing literature reviews. This review searched SSRN, arXiv, and Alpha Architect, traced useful secondary discussions to primary research, and did not load market arrays or modify strategy code. It creates no new experiment admission and no execution schedule.

## Decision in the recovered project state

The project has progressed beyond the earlier eleven-candidate chat checkpoint: C12 has been evaluated, validation selected C09, and the fixed C09 policy has completed the internal audit and clean handoff workflow. The authoritative local records are [VALIDATION_SELECTION.json](VALIDATION_SELECTION.json), [AUDIT_RELEASE_RECORD.json](AUDIT_RELEASE_RECORD.json), and the independent [audit](../reviews/AUDIT_INDEPENDENT_RESULTS.md) and [handoff](../reviews/HANDOFF_AUDIT_RESULTS.md) reviews. The research coordinator supplied that recovered state to this reviewer; this follow-up does not independently recalculate those results.

**Recommendation: retain the frozen handoff.** The useful literature contribution now is a sharper account of competing explanations and a bounded research backlog. Redesigning on the exposed fifteen years is permitted by the employer, but a redesigned policy would no longer have an untouched internal confirmation period. A future code change can pass causality tests and still be selected using knowledge of later outcomes. Those are different questions.

## 1. Characteristics can describe risk exposures as well as expected returns

Kelly, Pruitt, and Su's *Characteristics Are Covariances: A Unified Model of Risk and Return* introduces Instrumented Principal Component Analysis. Observable characteristics instrument time-varying latent-factor loadings; the model also accommodates a characteristic-associated intercept. This supplies a concrete alternative to interpreting every characteristic-return association as independent stock-specific alpha. Sources: [SSRN 3032013](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3032013) and [NBER 24540](https://www.nber.org/papers/w24540). Their indexed abstracts were available; direct retrieval of the full manuscripts was blocked. The different versions report different empirical factor counts, so no count from their equity application is imported into this project.

**Our inference for the anonymous simulator:** a changing marginal coefficient can reflect a changing realization of common-factor returns or changing loadings, even when the stock-selection mechanism is unchanged. Conversely, a characteristic can predict a genuine common-factor premium that survives the required market hedge. Therefore, neither of these rules is defensible without local evidence:

- Treat every estimated factor exposure as unwanted and project it away.
- Treat every characteristic association as an independent expected-return signal.

The existing covariance-weighted learner and factor-risk allocator already address correlated noise in one way. A full IPCA implementation is a substantial new model family, not a small cleanup. A narrower diagnostic would first decompose existing frozen forecast payoffs into their common-factor and residual components using factor bases estimated only from prior returns. This can explain where the current portfolio earns and loses money without selecting another strategy.

For a **new** residual-target learner, residualizing only the dependent return changes the learning target. It does not generally preserve the coefficient of the original joint model. If the intention is to remove nuisance factors while estimating a partial characteristic effect, the corresponding nuisance projection must be handled consistently for both the regressors and dependent variable, with an explicitly defined weighting convention. GLS and residual-target prediction should not be described as interchangeable.

**Possible falsification:** if a strictly prior-estimated decomposition shows no stable characteristic information beyond the common component, a more elaborate idiosyncratic predictor lacks a rationale. If the common component contains stable predictive payoffs, hedging every latent direction could destroy useful return. This decomposition is descriptive once the whole sample has been inspected; it cannot create a new holdout.

## 2. More variance explained is not the same as more useful factors

Lettau and Pelger's *Estimating Latent Asset-Pricing Factors* makes the distinction explicit: ordinary PCA can miss low-variance factors important for expected returns, while an estimator that also considers pricing errors can identify them. The public [CEPR DP12926 record](https://cepr.org/publications/dp12926) was opened; the related [NBER 24858 record](https://www.nber.org/papers/w24858), *Factors that Fit the Time Series and Cross-Section of Stock Returns*, was available through its indexed primary abstract. This review does not claim to have reproduced their estimator or read a paid full text.

**Our inference:** increasing covariance rank and finding no improvement is evidence about that particular risk-estimation change. It does not establish that all additional predictive factor structure is absent. Equally, this distinction does not justify searching for profitable low-variance directions: expected-return estimates are precisely where estimation error and selection optimism can be severe.

The recent [*Attention Factors for Statistical Arbitrage*, arXiv:2510.11616](https://arxiv.org/abs/2510.11616), gives a modern example of joint characteristic-based factor estimation, residual-signal modeling, and cost-aware trading. Its opened abstract emphasizes weak factors and joint estimation. Its empirical performance and architecture do not transfer to this simulated market. Adopting attention networks now would add architecture, optimization, seed, and regularization decisions while losing a clean comparison with the frozen policy. It is a research lead, not the next authorized implementation.

A bounded alternative, **only if a future research phase is admitted**, would compare one prespecified low-dimensional characteristic-conditioned risk model with the existing estimator while leaving the mean forecast and cost policy fixed. The comparison must measure calibration and realized portfolio outcomes, rather than select a model solely for explaining more contemporaneous variance. With the present information exposure, any improvement would be exploratory.

## 3. Persistence should be measured in the object we intend to trade

Alpha Architect's [*Information Decay: which factors have the longest half-lives?*](https://alphaarchitect.com/information-decay/) led to Flint and Vermaak's [*Factor Information Decay: A Global Study*, SSRN 3986499](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3986499). The primary abstract studies how **factor exposures** evolve after portfolio formation. It says that exposure evolution combined with risk-premium estimates informs the expected-return term structure. This is narrower than saying that feature autocorrelation measures alpha half-life. The full paper was not available for download in the retrieved record.

The distinction matters here:

| Quantity | What its persistence would establish | What it would not establish |
|---|---|---|
| Raw characteristic | The observed input moves slowly | A stable mapping from that input to future returns |
| Frozen model forecast | The fitted score changes slowly | Predictive gains from holding it longer |
| Conditional predictive payoff | The old information still predicts later returns | An optimal cost threshold without risk and holdings |
| Learned coefficient | The estimator forgets slowly | Slow-moving economic truth |

The current cost amortization horizon is an explicit approximation. A future multi-horizon experiment should begin with a prior-defined predictive-decay diagnostic and preserve the distinction between cumulative return and daily expected-return units. For a characteristic row `s` and an `H`-day target covering returns `s+1` through `s+H`, that observation is eligible for a prediction of day `t` only when `s+H <= t-1`. Overlapping labels also require dependence-aware uncertainty. A longer label must not silently make unfinished returns available or multiply daily alpha by `H` while retaining a one-day risk term.

[de Lataillade et al., *Optimal Trading with Linear Costs*, arXiv:1203.5957](https://arxiv.org/abs/1203.5957), supports threshold behavior under proportional costs and links its capped-position problem to a no-trade band under quadratic risk. This confirms the cost-model distinction already recorded in the existing reviews; it does not supply a turnkey multi-asset optimizer or prove that another buffer improves the current allocator.

## 4. What Alpha Architect adds, and what it does not

The opened [Alpha Architect short-term-signals discussion](https://alphaarchitect.com/alpha-from-short-term-signals-may-survive-market-frictions/) led to [SSRN 4115411](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4115411), *Beyond Fama-French Factors: Alpha from Short-Term Signals*. Direct SSRN retrieval was blocked, but the authors' [Robeco research account](https://www.robeco.com/en-int/insights/2022/05/beyond-fama-french-alpha-from-short-term-signals) was readable. It describes combining low-correlated signals and retaining existing holdings under more permissive rules than new entries to reduce turnover. The empirical application uses identifiable equity signals and a liquid-stock universe.

The transferable idea is to compare **incremental net contribution** and actual trading costs, including interaction with existing holdings. The non-transferable elements include their cost assumptions, long/short quantile rules, industry classifications, analyst data, and reported performance. Our assignment already supplies the costs, and our allocator already includes an absolute-turnover penalty. Adding buy/hold thresholds on top would change the portfolio policy and could disturb the hedge; it is not an automatic improvement.

The original [Novy-Marx–Velikov SSRN abstract, 2535173](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2535173), and [publisher record](https://doi.org/10.1093/rfs/hhv063) independently support the usefulness of a buy/hold spread in their anomaly study. They do not support adopting a particular spread here. No new numerical calibration has been taken from a secondary article.

## Ranked backlog and evidence required

These are prospective ideas, **not admitted or executed experiments**.

| Priority | Question | Smallest useful investigation | What would prevent promotion |
|---|---|---|---|
| 1 | Is apparent alpha predominantly common-factor compensation or residual stock selection? | Descriptive, causal factor/residual payoff decomposition of the frozen policy | Unstable attribution; basis estimated with future data; no reproducible incremental information |
| 2 | Does predictive payoff persist long enough to justify the chosen cost horizon? | Fixed-horizon decay comparison with complete labels and unchanged risk/cost arithmetic | Only feature persistence; gross-only gains; benefits concentrated in an inspected window |
| 3 | Do characteristics improve changing risk exposures beyond return PCA? | One prior-specified conditional risk model, with forecast and trading policy fixed | Complexity/runtimes outweigh gains; in-sample fit without improved causal calibration |

The present recommendation is to improve explanation and evidence around the frozen strategy before any expansion of the selectable model set. None of these sources establishes that the simulator contains the named mechanism. No paper, future-perturbation pass, deflated Sharpe statistic, or resampling diagnostic can certify the complete absence of overfit. Preserving the identity of the tested policy and accurately recording information exposure remains the critical control.

## Retrieval and contribution record

This note used public searches with generic methodological terms; employer data and private numeric findings were not sent in search queries. Sources were retrieved on 27 October 2026. Primary abstract records, opened author accounts, and full-text access limitations are identified above. All proposals and interpretations in this note are AI-generated research assistance; no additional human experiment or discovery is attributed to the user.
