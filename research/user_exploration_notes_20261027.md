# Quant Research Take-Home: exploration notes

Working notes, not a solution. Sources: my read of the folder (README, `score.py`, `strategy.py` stub, the two examples, a slice of `costs.csv`) and three outside reviews, referred to as **D1** (long structured review with the table), **D2** (generic ZIP review) and **D3** (latest review).

Tags: **[me]** is my own point, **[D1]** / **[D3]** is an idea taken from that review.

**What is not verified.** I never opened `returns.csv`, `characteristics.csv` or the figures. Anything about what the data *does* is a hypothesis to test, not a finding.

---

## 1. Fixed facts (README and score.py)

- 1000 stocks, 3780 days, 13 anonymous characteristics: Woe, Malice, Dread, Frolic, Up, Down, Charm, Strange, Top, Bottom, Snap, Crackle, Pop.
- Costs are static, one-way and per stock (about 2 to 8 bps in the visible slice), charged on |Δweight|. The first trade is free.
- Score is the annualized Sharpe of (portfolio return minus cost) over a future run of decades. `score.py` starts at day 252 with an empty book.
- Beta is the slope of daily net return on the equal-weight market's daily return, over the whole run, and must stay under 0.2.
- `rebalance` is serial and must average under 100 ms on one core. `forecast` runs once, about an hour per century of days. Allowed libraries: numpy, pandas, scipy, cvxpy, scikit-learn, lightgbm.
- Timing: forecast row t positions you for day t, so it may use data through day t-1 only. Characteristics for day d are published after d's close, alongside d's return.
- Lookahead is checked by reading the code and by rerunning `forecast` on altered futures. Tuning on the 15 given years is explicitly allowed.
- They run Claude on the same folder as a baseline. The note must say where the AI did the work and where you did.

---

## 2. Verdict on the three reviews

**D1: best.**
- Good: the 4+6+3 naming pattern, the rank-deficiency trap (an uncentered second-moment matrix over 252 days has rank at most 252, so at least 748 null directions), the Woodbury and low-rank factor-risk idea, the unit test that alters the future, and the point that dollar-neutral is not beta-neutral.
- Overstated:
  - It quotes Gârleanu–Pedersen, but costs here are linear, so the optimal structure is a no-trade band, not partial adjustment.
  - The "2–5 ms" figure has no benchmark.
  - "Vastly higher Sharpe" from steering fast signals to cheap stocks is unsupported.
  - Vol-targeting is argued from the market's vol, but your book should be hedged, so what matters is the book's own vol.
  - Frozen full-sample weights pass the mechanical check but make the in-sample Sharpe unreliable.
  - "Almost certainly a factor model" is a guess.

**D3: second.**
- Good: start simple, heavy work in `forecast`, factor risk models, cost heterogeneity, cheap turnover control, strict causality.
- Wrong:
  - It says to residualize against the characteristics. That destroys the signal.
  - It hedges beta by subtracting a multiple of the equal-weight portfolio, which ignores per-stock betas and trades all names.
  - It says to ignore off-diagonals, which loads clusters blindly.
  - It never addresses the label-timing trap or the refit compute budget.
- It quotes figure numbers (about +500–600% for the equal-weight market, trailing vol about 8% to 23%) that I cannot confirm.

**D2: ignore.** It could not open the files and guessed an order-book problem (FIFO queues, Fenwick trees, latency). This is a daily cross-section of stocks. Only the generic bullets (lookahead, multiple testing, costs) are valid.

---

## 3. Structure to probe (as tests)

1. **The 4/6/3 grouping [D1].** Do Woe/Malice/Dread/Frolic, the six quarks and Snap/Crackle/Pop differ in autocorrelation half-life, mutual correlation or relation to returns? It could just be three familiar lists, so test it.
2. **Characteristic anatomy [me].** Raw or ranked or z-scored? Discrete? Missing values? Per-stock persistence (AC1, AC20)? Are any of them lagged copies, transforms or combinations of the others? Do the pairs (Up/Down, Charm/Strange, Top/Bottom) behave as differences or interactions [D1]?
3. **Timing alignment [me].** Compare corr(char_t, r_t) against corr(char_t, r_{t+k}) for k = 1..20. A strong same-day link means the characteristic is built partly from returns. The decay curve gives the trading horizon.
4. **Fast and slow signals [D1].** Separate signals by decay horizon so the cost-aware step knows how long an alpha lasts. `forecast` can return a `(days, n, k)` array for this.
5. **Covariance structure [D1, me].** Eigenvalue spectrum against the Marchenko–Pastur bulk. Are the clusters stable across sub-periods? Do characteristics map to cluster membership or factor loadings?
6. **Raw against residual returns [D1, me].** Test IC on raw returns and on factor-residual returns, and keep whichever the data supports. Residualizing returns hides any characteristic that predicts the factor returns themselves.
7. **Costs [D1, D3].** Correlation of cost with vol, cluster and per-stock IC. If the best signals live in costly names, net alpha shrinks.
8. **Stationarity [me].** IC by year and by vol regime. A signal that fades across the 15 years is a warning for the decades that follow.
9. **Data hygiene [me].** NaNs, extreme returns, stocks that start or stop. Check that the figure claims (equal-weight total return, trailing vol) match `returns.csv`.

---

## 4. Biases and traps

| Trap | Why it matters here | Defence |
|---|---|---|
| Rank-deficient covariance [D1, D3] | 252 days for 1000 names leaves at least 748 null directions, and the naive optimizer piles risk into them | Low-rank factor model plus diagonal, or shrinkage; never invert the raw sample covariance |
| Slow solver [D1, D3] | cvxpy on 1000 variables is about 1 s per call against a 100 ms budget | Woodbury on a factor covariance, plus a proximal or warm-started solver with per-stock no-trade bands |
| Lookahead in `forecast` [D1, D3] | Full-sample normalization, PCA or a model fit on all rows fails the altered-future test | Strictly causal operations along axis 0, plus a unit test that changes day t and asserts rows before t are unchanged |
| Label timing [me] | A model for row t can only train on pairs (char_s, r_{s+1}) with s+1 ≤ t-1; using s = t-1 puts r_t in the training set | Embargo the last label; refit on a schedule, not daily, to stay in budget |
| Stock-days are not independent [me] | Cross-sectional correlation inflates t-stats | Daily cross-sectional IC or Fama–MacBeth slopes, autocorrelation-robust errors |
| Multiple testing [D3, me] | 13 characteristics × horizons × transforms × models | Few pre-stated hypotheses; deflate the best result; a hold-out (say last 5 years) untouched until the end |
| Sharpe noise [me] | Standard error is about sqrt((1 + SR²/2)/years) | About 0.3 at SR 1 over roughly 14 scored years, so gaps below that between variants are mostly noise |
| Beta is not scale-free [me] | Beta = ρ·σ_book/σ_mkt, so it grows with book size, and it is measured over the whole run, not per day | Control book vol and residual correlation together |
| Dollar-neutral is not beta-neutral [D1] | Stocks have different betas | Project weights orthogonal to ones and rolling per-stock betas |
| Positions drift [me] | Weights move with returns each day, so neutrality decays between rebalances | Re-impose neutrality as a constraint inside the cost-aware step, not as a post-hoc overlay (untested) |
| Parameter sharing [D1] | Stock-specific parameters decay | Same mapping from characteristics to returns across stocks, or within clusters |
| Ruin [D1, D3] | A book that loses everything in a day is finished | Size modestly; Sharpe is scale-free anyway |
| Non-stationary volatility [D1, D3] | The trailing-vol figure suggests regimes | Let the risk model adapt; check whether it already handles it before adding explicit targeting |
| Priors from real markets [me] | The market is synthetic | Trust evidence over momentum or value folklore |

---

## 5. Construction notes (for later)

- Start with a simple, fast baseline, then add complexity only if it earns its keep [D3].
- Heavy work (feature building, model fits, risk factors) goes in `forecast`; keep `rebalance` to a few NumPy operations [D3].
- With linear costs, the optimizer should produce a no-trade band for each stock proportional to its cost, not a blend toward holdings [me, D1].
- Rolling decompositions per call can eat the 100 ms budget; update the risk model every few days, computed causally [me].
- Use a tight equality or allclose check in the altered-future unit test; start exact and relax only if BLAS effects require it [me].

---

## 6. Claims to distrust

- Any specific number about the data that came from a review that never opened the files.
- Exact solver speeds ("2–5 ms") without a benchmark.
- "Characteristic-neutral expected returns" [D3]: residualizing against what you want to predict removes it.
- "Ignore off-diagonals" [D3] and "subtract a multiple of the equal-weight portfolio" [D3].
- "Almost certainly a latent factor model" [D1]: plausible, but test it.

---

## 7. Suggested exploration order

1. Load and sanity-check. Check NaNs, extremes, per-day characteristic distributions and persistence.
2. Recompute the equal-weight cumulative return and rolling 252-day vol, and compare with the figures.
3. Alignment and IC decay for every characteristic, with by-year breakdown and robust t-stats.
4. Test the 4/6/3 grouping.
5. Risk structure: spectrum, clusters, and characteristics against loadings.
6. Costs against vol, characteristics and IC.
7. Stationarity by year and regime.
8. Only then build a baseline. Hold out the last 5 years and don't touch them until the end.

---

## 8. Log for the one-page note

The note needs: what you came to believe about the market, what you built and why, where AI did the work and where you did, and what you expect to break over decades. Keep a running log as you go:

| Date | Hypothesis | Test that could have failed | Result | Decision | AI or me |
|---|---|---|---|---|---|
| | | | | | |

The strongest line you can write is one hypothesis the data refused, and what you changed because of it.
