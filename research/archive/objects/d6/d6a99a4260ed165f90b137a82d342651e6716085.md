# Discovery risk findings — run 001

**Scope:** observed discovery rows `[0,2016)` only. The pooled and four-block estimates are descriptive and retrospective. They are not historical risk forecasts or evidence of a profitable portfolio. No validation/audit outcomes or supplied full-sample figures were read for this review.

**Executed evidence:** [risk_diagnostics_001/summary.json](../evidence/risk_diagnostics_001/summary.json), [blocks.csv](../evidence/risk_diagnostics_001/blocks.csv), [stocks.csv](../evidence/risk_diagnostics_001/stocks.csv), and [spectrum.csv](../evidence/risk_diagnostics_001/spectrum.csv). The run exited 0 and recorded nine passing workflow checks, including input identity, allowed scope, decomposition reconciliation, covariance properties, and unchanged inputs. These checks validate that recorded workflow, not a future strategy.

## 1. Hedge heterogeneous market exposure

The equal-weight market has 12.52% annualized daily volatility in this discovery interval. Median individual-stock volatility is 30.05%; median residual volatility after a centered market regression is 26.99%.

Pooled stock market betas differ materially:

| Quantile | Market beta |
|---|---:|
| Minimum | 0.200 |
| 10th percentile | 0.624 |
| Median | 0.950 |
| 90th percentile | 1.421 |
| 99th percentile | 1.929 |
| Maximum | 2.858 |

A dollar-neutral book therefore need not have zero market exposure. The first trading policy should constrain the position-weighted **causally estimated stock betas**, with realized net beta assessed by the unmodified scorer. Estimated neutrality is a design control; it cannot guarantee future realized neutrality.

The cross-sectional correlations of stock betas between adjacent 504-day blocks are 0.872, 0.883 and 0.903. Median absolute changes are 0.114, 0.107 and 0.099. This is consistent with useful persistence alongside estimation error and changing exposures. It supports investigating a rolling estimate, without establishing that any particular lookback or shrinkage constant is optimal. A fixed 252-day lookback is a reasonable first engineering choice; its quality must be judged in the subsequent portfolio workflow.

## 2. Market removal leaves material covariance

The leading eigenvalues of the pooled discovery residual covariance account for:

| Number of components | Share of residual variance |
|---:|---:|
| 1 | 4.60% |
| 3 | 10.05% |
| 5 | 14.04% |
| 10 | 21.33% |
| 20 | 30.20% |
| 50 | 44.67% |
| 100 | 57.65% |

The corresponding residual-correlation shares are similar: 20.68% for ten components and 29.58% for twenty. Mean pairwise residual correlation is −0.00091, while mean absolute pairwise correlation is 0.06263.

The small **signed average** correlation must not be presented as evidence that residual risks are independent. Positive and negative relationships cancel, and a market constructed from the same universe imposes an aggregate residual restriction. The spectrum and absolute correlations show why a diagonal variance approximation can miss material portfolio risk.

A diagonal residual-risk allocator remains a transparent first benchmark. If a candidate's risk or instability warrants a more elaborate hedge, a small causal factor-risk model is the next hypothesis to preregister. The present pooled spectrum does not select a valid live factor rank, establish factor stability, or authorize using full-discovery eigenvectors for earlier decisions. A trailing estimate and a fresh complete pipeline slot would be required for a selectable alternative.

## 3. Costs are economically relevant and heterogeneous

Known one-way cost rates span 2.01–7.99 basis points per unit traded, with median 5.01 basis points; the 10th and 90th percentiles are 2.76 and 7.42 basis points. A complete entry and exit therefore incurs two legs of these costs, absent the scorer's explicitly free initialization trade.

The measured cost associations with stock risk are weak in this census:

| Quantity | Pearson correlation with cost | Spearman correlation with cost |
|---|---:|---:|
| Total stock volatility | 0.022 | 0.026 |
| Residual stock volatility | 0.040 | 0.032 |
| Absolute market beta | −0.032 | −0.025 |

These summaries do not establish independence or make a blanket preference for the cheapest stocks optimal. The allocator should use each stock's own known cost and current drifted holding. Any amortization horizon in its objective is a control approximation; the official scorer must continue charging full actual transaction costs on every charged rebalance.

## 4. First implementation boundary

The evidence supports a deliberately interpretable first comparison: identical causal risk/cost machinery, an adaptive joint linear alpha forecast, and one adaptive additive-curvature challenger. Suggested shared controls are a trailing stock-beta estimate, positive residual-variance floor, a direct estimated-beta equality, stock position bounds and an explicit gross-exposure policy. These are our engineering decisions, not additional assignment constraints.

If beta shrinkage toward one is used, record both the shrinkage rule and the unshrunk estimated exposure as a diagnostic. Hedging a shrunk beta vector does not mathematically imply hedging the unshrunk vector when the net dollar position is nonzero. Likewise, proportional gross scaling preserves the selected beta equality but generally changes the optimum of an allocator that did not include the gross constraint.

Portfolio net Sharpe, drawdowns, charged turnover, realized beta and runtime remain unanswered by this descriptive study. Those require actual full-workflow evidence before either alpha family is considered successful.

## Reproduction

The frozen code, expectations, exact rerun command and environment are in `evidence/risk_diagnostics_001/`. The underlying discovery cache can be rebuilt by the recorded data-preparation workflow from the unchanged supplied archive. This review inspected existing outputs and code; it did not run an additional predictive scan, candidate backtest, or isolated test.
