# Alpha discovery findings — diagnostic run 001

**Executed scope:** actual rows `[0,2016)` only; no validation/audit outcomes or supplied figures inspected.  
**Run:** `evidence/alpha_diagnostics_001/`; status `PASS_SCOPE_ONLY`, exit 0, 123 workflow checks passed.  
**Output:** 135,122 daily diagnostic records; no undefined ICs or empty quantile buckets; no candidate positions or portfolio backtest.  
**Research budget:** zero complete pipeline slots used. The feature, horizon, shape, persistence and redundancy exposures are recorded in `diagnostic_exposures.json`.

## Decision-relevant conclusion

The discovery data support a **small joint model with causal adaptation**, and justify a **restrained additive nonlinear challenger**. They do not support locking in a simple list of permanently positive and negative characteristic slopes.

Three observations drive that recommendation:

1. Characteristics move very slowly and are already close to cross-sectionally standardized. Their information can persist for weeks, which makes low-churn trading worth investigating.
2. Several apparent linear relationships change sign across the discovery history. In particular, the attractive early positive associations of Woe and Dread turn negative later. A pooled coefficient can conceal this instability.
3. The fixed nonlinear curvature contrast is consistently negative for Snap, Crackle and Pop at the one-day horizon across all four discovery blocks. This warrants a compact nonlinear response test. It is not proof of three independent nonlinear alphas: these characteristics are correlated, and quarter-level results remain noisy.

These are descriptive relationships in the development sample. No result here establishes net Sharpe, required beta compliance, realistic turnover or hidden-future generalization. Source: `predictive_summary.csv`, `quantile_shapes.csv`, `persistence.csv`, `redundancy.csv` in the run directory.

## 1. Alignment, controls and uncertainty

For feature date `s`, the first target return is `s+1`. Horizons 1, 5 and 20 use the arithmetic average of the next `h` returns, in **daily-return units**. They are not compounded holding returns. All labels finish inside their assigned two-year discovery block. Predictive origins begin at feature index 252.

The retained target counts are 1,763 / 1,747 / 1,687 for horizons 1 / 5 / 20, respectively. The one-day diagnostic count includes the last already-observed discovery return; it is deliberately different from the official portfolio scorer's 1,762 discovery observations. No scorer boundary has been changed.

Market-controlled targets subtract a stock's beta, estimated on the 252 observed days through the feature date, times the forward equal-weight-market average return. This removes estimated heterogeneous market exposure; it does not establish neutrality to every latent risk factor. All planned beta estimates were available.

Statistics are first calculated daily across stocks and then summarized by time. We do not use stock-day iid standard errors. Fixed 63-day block summaries and four two-year blocks expose instability, but are not corrections for the many inspected hypotheses. Source: the frozen `expectations.md`, `config.json`, `beta_control_coverage.json`, `checks.json` and `daily_diagnostics.csv`.

## 2. The characteristics are slow-moving standardized states

Across the thirteen characteristics, median daily cross-sectional standard deviations range from approximately **0.99999965 to 1.00000065**. Their pooled mean daily cross-sectional levels are between roughly −3.5×10⁻⁷ and 7.5×10⁻⁸, while the standard deviations of those daily means are approximately 9×10⁻⁶. The supplied values are therefore consistent with already standardized cross-sections, with small rounding effects.

Daily rank persistence is approximately **0.9989–0.9990** for every feature. At twenty days, it remains near **0.98**. For example:

| Characteristic | Rank persistence, 1 day | Rank persistence, 5 days | Rank persistence, 20 days | Top-decile retention, 20 days |
|---|---:|---:|---:|---:|
| Woe | 0.9990 | 0.9951 | 0.9807 | 86.5% |
| Up | 0.9990 | 0.9950 | 0.9804 | 86.3% |
| Snap | 0.9989 | 0.9949 | 0.9802 | 86.6% |
| Pop | 0.9990 | 0.9950 | 0.9805 | 86.3% |

Persistent stock means account for approximately 58%–62% of pooled characteristic variance over the eight-year prefix. This is consistent with slow-moving relative-stock attributes rather than rapidly changing daily observations. It does **not** imply expected returns have equally stable signs.

Known trading costs have weak contemporaneous cross-sectional correlations with these characteristics; the largest absolute pooled correlation is about 0.046. This does not establish independence, but there is no large simple linear cost association in this diagnostic.

**Implication:** start with the provided scale, avoid gratuitous full-history standardization, and investigate persistent signal targets with explicit no-trade behavior. Feature persistence alone does not measure portfolio turnover: return-driven position drift and changing fitted coefficients can still create trading. Source: `characteristic_summary.csv`, `persistence.csv`.

## 3. Linear associations are small, and several are unstable

The following table reports daily cross-sectional mean IC and predefined quantile contrasts for **market-controlled, next-day** labels. “Spread” is mean top-decile label minus mean bottom-decile label. It has no transaction costs, leverage policy, portfolio drift or candidate score attached to it.

| Characteristic | Mean Pearson IC | Mean rank IC | Top-minus-bottom, bp/day | Curvature contrast, bp/day |
|---|---:|---:|---:|---:|
| Woe | 0.00428 | 0.00483 | 2.73 | −1.88 |
| Malice | −0.00486 | −0.00410 | −2.32 | −0.48 |
| Dread | 0.00448 | 0.00496 | 4.36 | −0.17 |
| Frolic | −0.00335 | −0.00351 | −1.66 | −0.02 |
| Up | −0.00645 | −0.00667 | −4.70 | −0.26 |
| Down | −0.00143 | −0.00160 | −1.41 | −0.41 |
| Charm | 0.00007 | −0.00046 | −0.07 | 0.51 |
| Strange | 0.00200 | 0.00152 | −0.23 | −0.06 |
| Top | −0.00210 | −0.00235 | −2.37 | −0.79 |
| Bottom | −0.00052 | −0.00109 | −1.17 | −0.70 |
| Snap | −0.00691 | −0.00639 | −5.73 | −2.87 |
| Crackle | −0.00015 | 0.00012 | −1.81 | −1.38 |
| Pop | 0.00236 | 0.00229 | −0.09 | −1.23 |

The striking caution is Woe/Dread, not the ordering of pooled scores:

| Characteristic | Block 1 IC | Block 2 IC | Block 3 IC | Block 4 IC |
|---|---:|---:|---:|---:|
| Woe | 0.02085 | 0.01276 | −0.00241 | −0.00575 |
| Dread | 0.02315 | 0.01369 | −0.00213 | −0.00742 |
| Malice | 0.00565 | 0.00135 | −0.00421 | −0.01695 |
| Charm | 0.00885 | −0.01171 | −0.00326 | 0.01083 |
| Frolic | −0.00286 | −0.00236 | −0.00345 | −0.00449 |
| Snap | −0.00621 | −0.00063 | −0.01626 | −0.00421 |

The first block has fewer predictive origins because of initial history. Woe's controlled top-minus-bottom contrast falls from +18.34 bp/day in block 1 to −5.85 in block 4; Dread falls from +23.55 to −3.60. A permanent positive slope inferred early would have been exposed to the wrong later sign. Frolic and Snap have negative mean IC in all four blocks, but this still does not establish stable incremental alpha once correlated features and residual risk are considered.

**Implication:** estimate characteristics jointly with shrinkage and an explicitly causal adaptation rule. Compare a small, predetermined amount of adaptation instead of reading these realized sign changes and hard-coding dates/regimes. Source: `horizon_1_summary.csv` / `predictive_summary.csv`, target `market_controlled`.

## 4. A restrained nonlinear hypothesis has earned investigation

The predeclared curvature contrast is `(Q1 + Q10 − Q5 − Q6)/2`: the average of the outer quantile labels minus the average of the central two. It is fixed before results and does not select the best buckets retrospectively.

| Characteristic | Block 1 curvature | Block 2 | Block 3 | Block 4 | Pooled |
|---|---:|---:|---:|---:|---:|
| Snap | −9.80 | −2.32 | −0.16 | −2.69 | −2.87 |
| Crackle | −1.66 | −2.23 | −0.28 | −1.48 | −1.38 |
| Pop | −1.96 | −0.43 | −1.65 | −1.24 | −1.23 |

Units are bp/day, next-day market-controlled labels. All twelve listed block contrasts are negative. The full quantile curves show that this need not be a symmetric quadratic: Snap is particularly weak in its highest decile, while Pop's two extremes are both weak. Combining a linear term with a restrained curvature term is a more faithful initial hypothesis than assuming a pure square response.

The weakness must remain visible: Snap's curvature is near zero in block 3 and becomes +0.03 bp/day at the twenty-day horizon in that block. Quarter-level curvature summaries change sign; Snap's one-day quarter means span roughly −17.50 to +17.10 bp/day. Thus “negative in every two-year block” is not evidence of uniformly positive performance at shorter horizons.

**Implication:** an additive nonlinear challenger, with coefficients estimated jointly and regularized, is supported as a next experiment. These results do not justify a large tree search, an interaction catalogue or treating the three features as independent bets. Source: `quantile_shapes.csv`, `predictive_summary.csv`.

## 5. The associations can persist over weeks

Labels at longer horizons are averaged back into daily-return units. Several conditional differences remain comparable in magnitude:

| Characteristic / contrast | 1-day horizon | 5-day horizon | 20-day horizon |
|---|---:|---:|---:|
| Snap, top-minus-bottom | −5.73 | −5.69 | −5.30 |
| Up, top-minus-bottom | −4.70 | −4.60 | −4.76 |
| Dread, top-minus-bottom | 4.36 | 4.13 | 4.89 |
| Snap, curvature | −2.87 | −3.30 | −3.60 |
| Crackle, curvature | −1.38 | −1.59 | −1.93 |
| Pop, curvature | −1.23 | −1.14 | −1.21 |

This is consistent with persistent conditional expected-return differences. It strengthens the reason to test cost-aware holding/no-trade policies rather than treating every daily signal change as an immediate full rebalance. Overlapping multi-day labels and persistent characteristics are highly dependent: horizon agreement is not three independent confirmations. Counts also differ because labels are required to finish within each block.

## 6. Joint estimation matters

The features are moderately correlated, with stable pairwise structure. Selected pooled mean daily Pearson correlations are:

| Pair | Correlation |
|---|---:|
| Woe–Malice | 0.438 |
| Charm–Bottom | 0.410 |
| Charm–Down | 0.402 |
| Snap–Crackle | 0.375 |
| Down–Bottom | 0.371 |
| Strange–Top | 0.368 |
| Woe–Dread | 0.351 |
| Crackle–Pop | 0.321 |

For example, Snap–Crackle remains approximately 0.368–0.383 across the four blocks. This is material redundancy, without near-perfect duplication. An individual feature's apparent effect can include correlated information from others. Squared terms can also be correlated even when linear correlations are only moderate.

**Implication:** fit and assess joint incremental contributions. Do not simply sum independently selected quantile signals or regard the thirteen mean ICs as independent discoveries. Source: `redundancy.csv`.

## 7. Next experiments recommended to the lead

1. **Joint causal regularized linear benchmark.** Use the observed characteristic scale, learn only matured pairs, and compare a small predefined update/forgetting choice within the pipeline budget. Test whether joint estimation and risk control resolve unstable univariate associations.
2. **One compact additive nonlinear challenger.** Add a restrained curvature basis under joint shrinkage; record its precise basis and candidate status before fitting. Test incremental net portfolio contribution rather than retaining nonlinear terms because this descriptive table looks encouraging.
3. **Separate persistence from trading policy.** Carry the same forecast through a credible market-controlled risk/cost policy, then use a predeclared ablation to measure the value of no-trade behavior. Do not infer cost-adjusted performance from the decile tables.

Questions still unanswered include exact predictive coefficients, useful forgetting timescale, latent-risk contamination, incremental nonlinear value, realized costs, beta compliance and achievable net Sharpe. The data do not yet answer them. Any further interaction/subgroup/horizon scan needs a prior written extension; no holdout access is implied by these findings.

## Reproduction and provenance

The code, plan and protocol used are frozen in `evidence/alpha_diagnostics_001/`. `inputs.json` contains the discovery-cache, code, plan and protocol hashes. `command.txt` records the executed command; `rerun.sh` runs the frozen script into a new output directory. `summary.json`, `checks.json`, logs and `artifact_manifest.json` document the workflow. The input arrays remained unchanged.

The 123 checks establish this diagnostic workflow's declared scope and internal reconciliations. They do not establish candidate causality or correctness of a trading implementation that has not yet been built. Independent review of the diagnostic code and findings is still required before treating these as final research conclusions.
