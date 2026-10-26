# C11: complete second-degree characteristic model, before implementation

**Admission:** the lead admitted C11 in `EXPERIMENT_LEDGER.md` before this implementation or its economic results. At this specification checkpoint, `submission/strategy_interactions.py` is absent. An independent agent will finish the known-interaction synthetic full-strategy E2E specification and executable verifier, and preserve an expected missing-module run, before this candidate source is written. No C12 is authorized here.

## Hypothesis and controlled question

All previous characteristic learners assume that expected return is additive across the supplied attributes. We have varied memory, observation precision and portfolio covariance more than the conditional-mean structure. Existing marginal curvature and moderate feature correlations motivate one test of that additive assumption.

For illustration, standardized jointly Gaussian variables X and Z satisfy `E[XZ | X] = rho * X^2`. A joint interaction can therefore appear as one-dimensional curvature. This identity does not establish Gaussianity of these characteristics or identify the simulator. It explains why the existing decile curves do not uniquely justify an additive squared-term mechanism.

C11 extends C02 with every pairwise interaction, preserving the original additive model and the entire portfolio policy. It is a bounded experiment, not a presumption that interactions are present or that a larger model will generalize. No pair is selected by name or by an additional predictive scan.

## Exact feature basis and regularization

For each available characteristic panel, call the unchanged C02 additive transformation. Its first13 columns are per-panel standardized, clipped and recentered linear values; its next13 columns are centered squares scaled by `sqrt(2)`. Keep these26 columns byte-identical.

Let `z` denote those first13 linear columns. Enumerate all pairs `(i,j)` with `0 <= i < j < 13`, in NumPy's strict upper-triangle order:78 pairs. For each pair form `z[:,i] * z[:,j]`, then subtract that product's cross-sectional mean **on this same published panel**. Apply no additional variance estimate, rank transform, clipping, pair selection or interaction normalization: the scale is fixed at1. Append the78 columns after the original26, giving104 columns in all. Original clipping already bounds these products.

The ridge matrix is diagonal with0.1 for the first26 coefficients and1.0 for the78 interaction coefficients. The original `ridge` configuration remains0.1; the sole new numerical setting is `interaction_ridge=1.0`. Stronger shrinkage is a fixed engineering choice to limit the larger basis, not a fitted optimum. There is no penalty grid.

The strategy supports only the specified additive base plus interactions; a contradictory `basis` setting is rejected rather than silently producing a different feature set.

## Exact information clock and fitting

Use the unchanged ordinary pooled EW fit, not the GLS learner. For forecast row t, the newest matured pair is the design from `X[t-2]` with label `R[t-1]`. Residualize the label using the base beta estimate on `R[:t-1]`, strictly before that label return. Predict from the104-column design of `X[t-1]`.

Update `G <- decay*G + Phi.T@Phi/n`, `b <- decay*b + Phi.T@y/n`, and `mass <- decay*mass+1`. Solve `(G/mass + ridge_diagonal) theta = b/mass` after126 matured daily pairs. Keep half-life252, so `decay=2**(-1/252)`. The first potentially nonzero forecast remains row127, and all earlier outputs are zero. Both moments use the same mass. Every learned matrix/coefficient is local to the forecast invocation.

No extra intercept is added. Every basis column is centered on the available panel. There are no pairwise cross-terms involving returns, costs, future observations or fitted full-history objects. The104 parameters and their cross-sectional observations are dependent; they must not be described as104 independent bets or millions of independent training examples.

## Portfolio and configuration equality

`rebalance`, `estimate_risk` and `get_last_diagnostics` delegate to the unchanged C02 base implementation. C11 retains raw trailing252-day beta, the original risk fallback/variance floor/shrinkage, diagonal cost-aware allocator, risk aversion1000, cost horizon20, stock bound0.01 and proportional gross cap1.0. Full actual costs remain in the unchanged scorer. Known gross-rescaling limitations remain visible rather than being fixed inside this alpha contrast.

The configuration differs from C02 only in the candidate identifier and new `interaction_ridge` field. All base controls are checked mechanically before economic execution. Configure rejects unknown controls through the base validator and resets from defaults; it does not fit data or create a market cache.

## Failure modes and required observable outcomes

1. **Duplicate/missing/misordered interaction columns:** source review verifies the strict upper triangle has78 distinct pairs and excludes the13 squares already present. The original26 columns are reused unchanged. No result-driven pair edits are permitted.
2. **A basis that cannot learn the intended joint effect:** the independently specified synthetic workflow generates a known lagged pair-product signal and runs this complete strategy through the original scorer. Forecast/truth agreement, positive net outcome under its deliberately strong fixture, finite targets, costs and declared controls must satisfy that verifier's thresholds fixed before code. Synthetic success validates capability and execution, not actual-market alpha.
3. **Timing/centering leakage:** each product is formed and centered only on its own available panel; beta and training labels retain the original maturity clock. Fresh-process repeated, future-altered and prefix synthetic scorer workflows compare protected forecasts, targets and economic ledgers. The actual configured discovery causality profile remains a separate finalist gate.
4. **Different base model or portfolio hidden in the extension:** preserve unchanged original files and equal base configuration. The wrapper delegates the same risk, trading and diagnostics functions. No covariance/GLS/risk-rank upgrade is bundled here.
5. **Incorrect penalty placement or warm-up:**104 columns receive a104-dimensional ridge with26 original and78 stronger penalties;126 matured pairs and first active row127 remain unchanged. Positive penalties regularize duplicated/correlated columns without a new numerical solver.
6. **State/input mutation:** local-only moments and coefficients, read-only supplied arrays, exact repeat evidence and input/source hashes. Forecast cannot leave a future-trained object for rebalance.
7. **Unrepresentable features or model outputs:** nonfinite consumed data and invalid settings fail explicitly. Expanded products are bounded by the existing transform, but resulting moments/predictions still require finite checks. A numerical exception is a failed run, not a silent cash fallback.
8. **Excessive runtime:** the larger Gram matrix increases fitting work. Record complete forecast timing and required extrapolation transparently; no unexecuted century pass. Existing average rebalance budget still applies to the unchanged portfolio call. Required output storage grows linearly with history, while learned moment/state dimensions stay fixed.

The independent synthetic workflow specification and executable verifier are completed before implementation; their exact fixtures and thresholds are authoritative for that workflow. No custom helper, optimizer or postimplementation isolated test is introduced. Subsequent market verification uses the existing original-scorer E2E runner and source review.

## Economic execution and interpretation

After the predeclared synthetic workflow and independent source review pass, the lead has authorized one exact discovery run on CPU1:

```sh
taskset -c 1 python -u tools/run_candidate.py --project . --strategy submission/strategy_interactions.py --config research/configs/C11_interactions.json --out evidence/discovery_C11_001
```

Use only input rows `[0,2016)`, score indices253–2014 inclusive and continuous holdings. Retain gross/net Sharpe, annual return/volatility/fees, beta, drawdown, all four fixed blocks, exposure/concentration, gross-rescaling frequency and timing. The primary controlled comparison is C11 versus C02. No extra scan, candidate or holdout access is authorized by this plan.

A favorable development result would support considering this specification in protected validation, not formally prove nonadditivity or identify the generator. A weak result should be preserved and argues against consuming the final slot on interaction tuning. No per-block profitability requirement or new Sharpe threshold is added. Any C12 follow-up needs its own explicit prospective admission and hypothesis.

## Attribution

The interaction hypothesis, implementation and empirical comparison are AI research work under the user's instructions. The mathematical aliasing argument is a reason for an experiment, not an applicant discovery in these data or a claim that the desired edge has already been found.
