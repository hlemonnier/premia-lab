# C11 known-interaction whole-strategy verification, before implementation

## Purpose and required order

This is a synthetic full workflow of the complete new C11 strategy through the unchanged supplied `score.py`. It is not an isolated test of the existing basis, risk estimator or allocator, and is not evidence of actual-market superiority. The lead admitted C11 before this plan. At this checkpoint `submission/strategy_interactions.py` and `tools/verify_interaction_workflow.py` do not exist.

Required order: write and snapshot this plan; write and snapshot the executable workflow verifier; execute the expected missing-module red stage; only then release the implementation author to create C11. Preserve all failures. Do not add cases or change numerical thresholds after the candidate implementation. A concrete implementation failure may be fixed and rerun against the unchanged verifier, with both runs retained.

The verifier reuses a frozen copy of the existing causality worker for fresh-process official-scorer execution and its comparison primitive. It does not create another scorer or a competing accounting simulator. A small controller generates the fixture, freezes sources/configuration, checks the known-signal outcome and compares complete saved workflow outputs. No actual market arrays, validation or audit data are opened.

## Deterministic fixture, fixed before code/results

Use NumPy `default_rng(20261026)` and exactly600 days,1000 stocks and13 characteristics, all float64. Draw arrays in this order from the same generator:

1. Characteristics `X` are independent standard normal draws of shape `(600,1000,13)`.
2. Market innovations are600 standard normal draws, clipped to `[-4,4]`, then multiplied by0.008.
3. Idiosyncratic innovations are standard normal draws of shape `(600,1000)`, clipped to `[-4,4]`, multiplied by0.006, then centered across stocks each day.

True stock market loadings are deterministic `linspace(0.6,1.4,1000)` and have mean one. Costs are deterministic `linspace(0.000005,0.000015,1000)`, nonnegative and nonzero; the original scorer charges these full one-way costs with only its original free opening trade.

Construct the known conditional mean independently from the model implementation. For each panel `X[s]`, subtract each column's cross-sectional mean, divide by its cross-sectional population standard deviation (floor1e-12), clip to `[-4,4]`, and recenter those linear columns. Form the three products `(0,1)`, `(2,3)` and `(4,5)`, each centered on that same panel. Their fixed coefficients are respectively `+0.0015`, `−0.0010`, `+0.00075`. For t>=1, `truth[t]` is that weighted product sum from `X[t−1]`; `truth[0]=0`. Set `R[t,i]=beta[i]*market[t]+truth[t,i]+idio[t,i]`.

The signal is intentionally strong and stationary. It tests representational ability, lag alignment, learning and portfolio execution under known conditions. It is not calibrated to real-market predictability and must never be presented as an attainable market return. No truth value is passed to the candidate. Save all generated arrays, including truth and true beta for review, with array/file hashes and the generator's frozen source identity. Require correct dimensions, finite values, nonnegative costs and stock returns above−1 as fixture preconditions.

## Exact candidate and scoring contract

Use the complete C11 configuration from the admitted specification: candidate ID `C11_interactions`, additive base, alpha half-life252, ridge0.1, interaction ridge1.0,126 training pairs, feature clip4, risk window252, risk minimum20, variance shrinkage0.2, variance floor1e-6, risk aversion1000, cost horizon20, stock bound0.01 and gross cap1. No synthetic-specific model knobs are allowed. The configuration is explicit, copied, hashed and passed to `configure` in each fresh child.

The official scorer hash is `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`. Use its original start252. A600-row workflow produces346 scored rows with return indices253–598 and347 targets for earning days253–599. A384-row prefix produces130 scored rows253–382 and131 targets253–383. Preserve the original continuous drift, same-day closing fee timing and opening waiver.

The full forecast must be finite and have shape `(days,1000)`. Rows0–126 must be exactly zero; row127 must contain a nonzero prediction. This checks the declared first active row at the complete-interface level. Source review separately establishes that the first26 additive terms are reused unchanged and all78 distinct strict-upper-triangle products receive the specified ridge.

## Four fresh-process workflows and protected ranges

Run sequentially on CPU2, with numerical-library threads set to one. Every case gets a new interpreter, frozen candidate/config and original scorer; no fitted state is shared. Save full forecasts, target arrays and daily ledgers for each case. Timing is recorded but excluded from equality.

| Case | Input | Compare to baseline |
|---|---|---|
| Baseline | All600 synthetic rows | Reference, known-signal/economic/control checks |
| Identical repeat | Same600 rows | All600 forecast rows,347 targets and346 economic rows |
| Joint future alteration | From row400 inclusive, multiply returns by0.5 and reverse the order of characteristic panels within that suffix | Forecast rows0–400 inclusive; targets earning through400; economic rows strictly before400 |
| Prefix384 | Only input rows0–383 | Forecast rows0–383; targets earning through383; economic rows through382 |

The joint altered prefix must be exactly unchanged before400 and both suffix inputs must actually differ. The altered suffix remains finite/admissible. Completion failures yield an incomplete/unverified comparison; a later suffix exception alone is not proof of leakage. Inputs are read-only during candidate calls and are hashed before/after; holdings passed by the scorer must not be mutated.

All protected numerical comparisons use absolute tolerance1e-14 plus relative tolerance1e-12. Compare target and score-day index arrays exactly. For economic equality compare gross return, full cost, gross exposure, market return and derived net return. Exclude wall timings. The worker's optional/module configuration record must match the explicit frozen requested configuration in every process.

## Concrete acceptance expectations

These expectations are fixed before the new candidate code or any candidate result:

- All four official workflows complete with finite outputs, valid shapes, untouched inputs and identical source/config/scorer identities.
- Every saved target obeys stock absolute weight<=0.01+1e-12 and gross<=1.0+1e-12. All scored gross and net returns exceed−1. Record known-true-beta exposure as a diagnostic; the required economic beta check is the baseline's realized net-market absolute beta<0.2, using the official market column and centered OLS.
- On baseline scored forecast rows253–598, the pooled Pearson correlation of the flattened forecasts with the withheld known conditional means is at least0.90. Both variances must be positive. This is the capability check; no claim that exact coefficients or unshrunk forecast scale must be recovered.
- Baseline daily net mean is positive and annualized daily net Sharpe exceeds1.0, with population standard deviation. This generous strong-fixture expectation is not a discovery-market acceptance floor.
- Independently reconcile the baseline official gross returns, full fees and posttrade gross exposures against the saved consecutive targets and the same day's observed returns. Use the declared numerical comparison tolerance. Retain the waived opening trade as a separate diagnostic; do not charge it into the retained ledger or grant another free trade.
- All three repeated/altered/prefix protected comparisons pass the exact boundaries above. No unavailable range is called passed.

Record baseline net/gross Sharpe, annual mean/volatility/fees, realized beta, forecast/truth correlation, exposure extrema, paid total fees, opening full cost waived, true-beta exposure, forecast seconds, and mean/max official rebalance latency. This600-row test does not establish long-history runtime, all possible future paths or a real-market causality pass. The actual configured discovery economics remain a subsequent lead-controlled run after independent source review and this workflow.

## Evidence and execution

Every run refuses to overwrite its directory. Preserve setup, generator recipe and seed, complete input identities, explicit config, source snapshots/hashes, frozen worker/verifier, original scorer, protocol, this plan, expected case boundaries, exact commands, environment, worker stdout/stderr/status, forecast/target/daily outputs, per-check actual values and final status. Provide a frozen rerun command that retains CPU2 and writes a fresh directory. A time limit of300 seconds per child is fixed here; timeout is incomplete evidence and cannot pass a comparison.

The first invocation must stop with exit1 and `EXPECTED_RED_MISSING_MODULE` after freezing the verifier/plan/config/generated-input evidence while the candidate entry point is absent. It executes zero candidate/scorer workflows. This is the required construction-order evidence, not a failed implemented strategy.

```sh
taskset -c 2 python -u tools/verify_interaction_workflow.py --project . --strategy submission/strategy_interactions.py --out evidence/interaction_workflow_red_001
```

After implementation and source review, execute the identical verifier with the actual admitted config:

```sh
taskset -c 2 python -u tools/verify_interaction_workflow.py --project . --strategy submission/strategy_interactions.py --config research/configs/C11_interactions.json --out evidence/interaction_workflow_001
```

No isolated unit test, actual-data discovery comparison, hyperparameter search or protected-period access is part of this workflow.
