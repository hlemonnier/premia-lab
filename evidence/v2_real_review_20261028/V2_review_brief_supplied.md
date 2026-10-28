# V2 strategy: review brief

**Purpose.** A self-contained account of the V2 work on the Continual Research quant take-home, for independent critical review. It covers what was done, why, the results, how they were checked, and where the work is weakest.
**Repository:** `hlemonnier/continual-research-takehome`, branch `v2-factor-risk` (commits `6f62916`, `afed8d0`). The new code is in `handoff_v2/` and the research trail in `research/v2/`. `main` and the original C09 handoff are unchanged.
**Authorship.** The applicant directed the work. An AI assistant (Claude) wrote the code, ran the experiments and wrote this brief.

---

## 1. The task, in brief

- **Data.** A simulated market: 1,000 stocks over 3,780 daily rows. There are 13 anonymous characteristics per stock per day (Woe, Malice, Dread, Frolic, Up, Down, Charm, Strange, Top, Bottom, Snap, Crackle, Pop) and a static one-way cost per stock (2–8 bp).
- **Objective.** Maximize out-of-sample net Sharpe over an unseen continuation lasting decades. Score each day as `x = portfolio return − trading cost`, then `Sharpe = mean(x)/std(x)·√252`.
- **Constraints:**
  - Beta to the equal-weight market below 0.2 out of sample (slope of daily net return on market return).
  - `rebalance` averages under 100 ms per call.
  - `forecast` runs once on the full history and takes about an hour per century of days.
  - Row t of the forecast may use only rows before t; this is checked by rerunning on altered futures.
- **Mechanics.**
  - Positions drift each day by `w·(1+r)/(1+r_p)`.
  - Cost is the per-stock cost times `|Δw|`.
  - Scoring starts at row 252 with an empty book.
- **Tuning.** Fitting on all 15 years is explicitly allowed.
- **Deliverable.** `strategy.py` with a one-page note. Graders assess alpha research and portfolio construction separately, and want to know what the applicant added beyond a Claude baseline.

## 2. Starting point: C09, the frozen handoff on `main`

- **Forecast.**
  - An exponentially weighted ridge regression (half-life 1,008 days, ridge 0.1) on the 13 cross-sectionally standardized characteristics plus their 13 centered squares.
  - Each training label is the next day's market-residual return, with beta estimated before the label day.
  - Row t predicts using X[t−1]; the newest training pair is X[t−2] against R[t−1].
- **Portfolio.**
  - Diagonal residual-variance risk (252-day window, shrunk 0.2 toward the median).
  - A scalar-dual allocator handles linear costs amortized over 20 days around the drifted book, an exact estimated-beta hedge, and 1% per-stock caps.
  - A gross cap of 1.0 then scales the book down proportionally.
- **Earlier research process.** The project split the history into discovery rows [0,2016), validation [2016,3024) and a sealed audit [3024,3780). It ran 12 discovery configurations, selected C09 on validation, and ran the audit once.
- **C09 scores (net Sharpe, unmodified scorer):**

| Full run | Discovery | Validation | Audit |
|---|---|---|---|
| 0.885 | 0.700 | 0.659 | 1.799 |

- **Attribution.** The repo's own analysis attributes most of the audit's gross return to common-factor exposure (rank-10 PCA span): +7.75 pp from the factor span against +2.26 pp from the remainder.

## 3. What the data says (tests run on the full sample)

All residual returns below are market-residual: `e[t] = r[t] − β[t]·m[t]`, with β estimated from rows before t.

| Question | Test | Result |
|---|---|---|
| Do the characteristics act as factor loadings? | Each day, regress e[t] on the standardized X[t−1]; compare with PCA of residual covariance | Mean daily R² is 0.26 with 13 linear terms and 0.33 with the squares added. The top 13 PCs explain 0.20 of residual variance. Spearman correlation between stocks' characteristic similarity and their residual correlation is 0.51 |
| Is C09's edge factor exposure? | Project the top-k trailing return factors out of the forecast | Audit Sharpe falls from 1.80 to 0.67 (k=10); the full run falls to 0.651 (k=10) and 0.867 (k=20) |
| Do premia drift, or is it noise? | Between-segment variance of the 26 factor-return means (6 segments), against a null built by shuffling 63-day blocks of the whole 26-vector | Overall p = 0.29. The 13 linear terms alone give p = 0.05, driven by Frolic and Dread. The 13 squares give p = 0.89. Power is low: a 1 bp/day change is about one segment's standard error |
| Do the 4/6/3 name groups (Severance tempers, quarks, Rice Krispies elves) matter? | Within- vs between-group correlation of characteristics; permutation test; forecast on group composites | The blocks are real: mean \|r\| 0.28 within groups vs 0.09 between, permutation p < 5e-5, stable across all four quarters of the sample. Group composites forecast worse, though (net Sharpe 0.587), because members of one group carry different premia |
| Is there information beyond characteristic levels? | Rank IC with the residual return, after removing the 26-column characteristic basis | Residual reversal over 1–21 days is real (lag-1 IC t ≈ 3.7) but decays within about 10 days. Low-beta stocks earn more. Characteristic changes show weak, unstable effects |
| How fast does the characteristic signal decay? | IC of the full-sample premium-weighted signal with returns L days ahead | Flat out to 60 days (t ≈ 5.5 at every lag) |

## 4. One change at a time on C09

All variants were scored with the unmodified `score.py` over the full run. The 95% range is a paired moving-block bootstrap (63-day blocks, 2,000 draws) of the Sharpe difference from C09.

| Variant | Net Sharpe | Δ vs C09 [95%] | Discovery / Validation / Audit |
|---|---|---|---|
| C09 reimplementation (exact match) | 0.885 | — | 0.700 / 0.659 / 1.799 |
| + trailing-beta feature | 0.923 | +0.038 [+0.012, +0.070] | 0.714 / 0.781 / 1.825 |
| Decorrelated prediction | 0.970 | +0.085 [−0.13, +0.27] | 0.763 / 0.694 / 1.865 |
| Decorrelated + beta | 1.000 | +0.115 [−0.10, +0.30] | 0.770 / 0.810 / 1.858 |
| Factor risk, scale 1.0, + beta | 1.199 | +0.315 [−0.17, +0.90] | 1.027 / 1.761 / 0.675 |
| **Factor risk, scale 0.3, + beta (V2)** | **1.244** | **+0.359 [0.00, +0.82]** | **1.100 / 1.657 / 1.149** |
| Factor risk, scale 0.1, + beta | 1.155 | +0.270 [−0.03, +0.64] | 1.045 / 1.375 / 1.360 |
| V2 at 5× book size (packaged) | 1.243 | — | 1.098 / 1.657 / 1.148 |

The "decorrelated" variant predicts with `D (D'D/N)⁻¹ coef` instead of `D coef`. A diagonal-risk book holding the plain forecast effectively bets (characteristic correlation × premium) rather than the premium itself; decorrelation undoes that.

**Negative results (all kept):**

| Variant | Net Sharpe |
|---|---|
| Residual reversal as a learned feature | 0.746 |
| Reversal scaled to its own decay (20- and 60-day cost horizons) | 0.861 / 0.871 |
| 5-day / 20-day labels | 0.858 / 0.831 |
| 252-day / infinite memory | 0.867 / 0.777 |
| Projecting out 10 / 20 return factors | 0.651 / 0.867 |
| Group composites / composites + members | 0.587 / 0.854 |
| Cost horizons of 5, 60, 120, 250 days | 0.870 / 0.880 / 0.874 / 0.869 |
| Factor risk with the decorrelated forecast | 1.107 |

**Factor level, before costs.** The 26 factor-return series were combined three ways: premium-weighted, premium × characteristic covariance (what a diagonal-risk book delivers), and mean-variance in factor space. No combination dominates in every period. Results are in `research/v2/results/factor_level.json`.

## 5. The V2 strategy (`handoff_v2/`, NumPy only)

**Forecast.** C09's learner with one extra column: each stock's trailing 252-day market beta, standardized, so 27 columns in total.
- The beta for pair s is estimated from rows before s+1. At prediction time, row t uses `beta[t]`, estimated from rows before t.
- Training pair s is X[s] against e[s+1]. The newest pair used for row t is s = t−2.

**Risk model, rebuilt incrementally inside `rebalance` from history through today:**
- `D_t` is the 26-column basis (13 standardized characteristics plus centered squares) of today's published characteristics.
- **Daily factor returns:** `f_s = (D'D)⁻¹ D' e_s`, using `D` from X[s−1] and the market-residual e_s (beta from rows before s, cross-sectionally demeaned).
- **Factor covariance:** `F` is an exponentially weighted second moment of `f` (half-life 126 days).
- **Specific variance:** `d` is an EW variance (half-life 126 days) of `u_s = e_s − D f_s`, shrunk 0.2 toward the median and floored at 1e-6.
- **Combined:** `Σ = diag(d) + φ·D F D'` with **φ = 0.3**.
- **Hedge betas:** estimated from the last 252 rows through today.

**Allocator.** An exact solution of

```
max_w  μ'w − γ/2 (w' diag(d) w + φ (D'w)' F (D'w)) − Σ_i (c_i/20)|w_i − h_i|
s.t.   b'w = 0,  |w_i| ≤ cap
```

- **Method:** write `F = LL'` (eigendecomposition, eigenvalues floored at 0). Dualize `z = L'D'w` and `b'w = 0`. Given the multipliers, each stock solves a scalar soft-threshold/clip problem.
- **Solver:** damped Newton on the convex dual, Hessian `A' W A + blockdiag(I/γ, 0)` over stocks in their interior region, with Armijo backtracking. The beta multiplier is then polished by bisection, so the hedge holds to floating-point tolerance. Multipliers are warm-started day to day.
- **Final scaling:** a gross cap is applied afterwards by proportional scaling, as in C09.

**Packaged configuration:** γ = 200, cap = 5%, gross cap = 5, cost horizon 20 days. This is a 5× rescale of the tested γ = 1000 / cap 1% / gross 1, which changes Sharpe by 0.001.

**Why φ = 0.3.** The diagonal book (C09-like) keeps its factor bets; the full factor-risk book (φ = 1) hedges them away.
- The two earn in different periods: validation 0.81 vs 1.76, audit 1.86 vs 0.68.
- Their daily net returns correlate only 0.53.
- An equal-risk blend of their return streams scored 1.244, with 0.92 / 1.56 / 1.59 by period.
- Scaling the factor covariance gives a single book between the two, with costs netted.
- φ was picked from {0.1, 0.3, 1.0} (1.155 / 1.244 / 1.199). The curve is smooth.

## 6. V2 performance (packaged, clean folder, unmodified scorer)

| | Full run | Discovery | Validation | Audit | Return / vol per yr | Cost per yr | Beta | Gross |
|---|---|---|---|---|---|---|---|---|
| C09 | 0.885 | 0.700 | 0.659 | 1.799 | 5.2% / 5.9% | 0.42% | 0.009 | 0.86 |
| V2 | 1.243 | 1.098 | 1.657 | 1.148 | 4.8% / 3.8% | 0.18% | 0.047 | 1.58 |

Rebalance takes 10.5 ms per call on the real data. The forecast takes 2.5 s.

## 7. Verification

1. **Allocator.** The spec and tests were written before the implementation, and the first run failed on the missing module as expected. 38 checks then passed:
   - Agreement with cvxpy/Clarabel on random problems: weights within ~5e-7, objective within ~1e-10 relative.
   - Exact beta equality and exact caps.
   - With F = 0 it reduces to the original C09 allocator (2.6e-16).
   - No trade when holdings are already optimal; cap 0 forces weight 0.
   - Invalid inputs are rejected; outputs are deterministic and inputs are not mutated.
   - Median solve 1.4 ms at n = 1000, k = 26.

   A separate regime with many no-trade bands and no active caps agreed with cvxpy to 2e-9.
2. **Forecast causality on the real data.** Inputs were replaced from row c on, for c ∈ {400, 1500, 3024, 3700}. Rows ≤ c are bitwise identical; row c is included because it uses only rows before c. This also holds for an altered copy passed in Fortran memory layout and for truncated histories, and later rows do respond to the change. All arrays are made C-contiguous inside `forecast`; the repo previously found that memory layout can change floating-point reductions.
3. **Packaging.** The clean-folder run with the unmodified `score.py` reproduced the research run to 3.4e-11 per day. It is not bitwise identical because the research version computed labels as cumulative-sum differences.
4. **Century runtime.** 25,200 tiled rows through the unmodified scorer:
   - Forecast 27.9 s (0.008 h per century).
   - Rebalance mean 4.8 ms, p99 7.8 ms, max 246 ms (the one-off risk-state build).
   - Worst daily return −1.75%.
5. **Reproduction.** The C09 reimplementation reproduced the original engine's scored ledger to three decimals in every metric.

## 8. Known weaknesses: please challenge these

- **Selection on fully exposed data.** About 25 scored variants, with φ chosen from three values. The bootstrap range for V2's gain over C09 touches zero ([0.00, +0.82]) and does not correct for selection. Expect shrinkage.
- **No clean out-of-sample estimate for V2.** C09's sealed audit is the only untouched number in the project, and V2 underperforms C09 in that period (1.15 vs 1.80). The argument is that the audit rewarded factor exposure during a favorable stretch, but that is an interpretation, not a test.
- **The φ rationale is partly empirical.** In theory φ = 1 is the correct mean-variance answer if F and the premium estimates are right. φ = 0.3 implicitly says "don't fully trust the factor covariance relative to noisy premium forecasts" or "keep some factor timing." A Bayesian or robust-optimization justification would be better than a three-point grid.
- **Realized beta grows with book size.** It is 0.009 at the base size and 0.047 at the packaged 5× size. Likely mechanism: the low-beta tilt combined with estimation error (low estimated betas regress upward). Shrinking hedge betas toward 1 (Blume/Vasicek) is untested.
- **Premium dynamics are unidentified.** Neither drift nor constancy can be established, so the 1,008-day half-life is inherited from C09, not justified. A state-space or Kalman model of the premia is the obvious next step and has not been done.
- **The risk model uses the same 26 columns as the forecast.** F is estimated from factor returns defined by the forecast's own basis, so the optimizer is effectively mean-variance in that 26-factor space. Is there circularity or overfitting risk in using the same basis for alpha and risk?
- **Gross-cap scaling after the solve** is a disclosed approximation, inherited from C09. It may disturb the no-trade decisions.
- **Volatility management is untested.** Market volatility ranges from about 7.5% to 23% across the sample, and no explicit volatility targeting was tried.
- **The equal-risk blend was computed from return streams** with trailing volatility. It was used only to motivate φ, not as a strategy.

## 9. Questions for the reviewer

1. Is the conclusion that "characteristics act as factor loadings and the edge is factor premia" justified by the R²/PCA comparison and the projection test, or is there an alternative explanation?
2. Is the drift test well designed (statistic, block length, null), and is the low-power caveat stated correctly?
3. Is φ = 0.3 defensible, or should factor-risk scaling come from a principled model, such as premium-estimation uncertainty in a Black-Litterman / Bayesian setup or a factor-timing shrinkage argument?
4. Any flaw in the allocator's dual formulation, convergence or edge cases (bands, caps, infeasible hedge, singular Hessian)?
5. Any lookahead path missed? In particular: the forecast's beta column, the incremental risk state in `rebalance`, and the prediction-time beta.
6. Given the evaluation is "decades" of continuation, which single change would most improve expected out-of-sample Sharpe: a premium state-space model, beta shrinkage for the hedge, volatility targeting, or something else?
7. Is the bootstrap comparison (paired, 63-day moving blocks, full run) appropriate for a difference between two strategies sharing one forecast core?

## 10. Where to find things

| Item | Path |
|---|---|
| Submission candidate and draft note | `handoff_v2/strategy.py` |
| Forecast, risk state, rebalance | `handoff_v2/model_v2/engine.py` |
| Allocator | `handoff_v2/model_v2/allocator.py` |
| Allocator spec / tests | `research/v2/ALLOCATOR_SPEC.md`, `research/v2/test_allocator.py` |
| Exploration scripts | `research/v2/exploration/` (`structure.py`, `drift_test.py`, `alpha_sources.py`, `factor_level.py`, `variants.py`, `compare.py`, `causality_check.py`) |
| All scored results | `research/v2/results/` (`comparison.json`, `variant_*.json`, `structure.json`, `century_v2.txt`) |
| V2 summary | `research/v2/README.md` |
| Original C09 handoff and its research trail | `handoff/`, `research/`, `reviews/`, `evidence/` |
