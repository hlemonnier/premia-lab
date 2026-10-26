# C11 interaction experiment: negative discovery result

## Finding and decision

The fixed full second-degree extension did not improve C02. C11 achieved discovery net Sharpe **0.603346**, versus **0.637567** for C02. Gross Sharpe also declined, while full fees increased. Three of the four fixed chronological blocks were weaker. This result does not support using the remaining pipeline slot to tune interaction penalties or select favorable pairs. It does not prove that the simulator is additive or that every interaction model would fail.

The lead closed this discovery checkpoint at eleven scored configurations. Slot 12 remains unassigned. No further experiment, validation or audit is authorized by this note.

## Controlled comparison and scope

C11 preserves C02's 26 linear/squared terms, EW half-life 252, ridge 0.1 on those terms, prior-label market residualization, 126-pair warm-up, and complete diagonal portfolio policy. It adds all 78 centered strict-upper-triangle products of the existing bounded linear columns, with fixed unit scale and ridge 1.0. There was no pair selection or penalty grid. The prospective specification is [INTERACTION_ALPHA_PLAN.md](INTERACTION_ALPHA_PLAN.md).

Both results use input rows **[0,2016)** and original-scorer return indices **253–2014 inclusive**: 1,762 scored days and 1,763 rebalance calls. The last target earns index 2015 and is not scored. Indices are zero-based. Sources are the preserved [C02 summary](../evidence/discovery_C02_001/summary.json) and [C11 summary](../evidence/discovery_C11_001/summary.json); no new predictive scan or resampling was performed for this note.

| Metric | C02 additive | C11 full second-degree |
|---|---:|---:|
| Net Sharpe | 0.637567 | 0.603346 |
| Gross Sharpe | 0.750111 | 0.722123 |
| Annual arithmetic net return | 4.4038% | 4.1666% |
| Annual net volatility | 6.9072% | 6.9058% |
| Annual full fees | 0.7773% | 0.8199% |
| Realized net market beta | 0.021230 | 0.022222 |
| Maximum drawdown | 8.4883% | 8.3679% |
| Mean daily absolute turnover | 0.062116 | 0.065493 |
| Gross-rescaled rebalances | 1,406 / 1,763 (79.75%) | 1,419 / 1,763 (80.49%) |
| Mean gross before scaling | 1.212326 | 1.242062 |

| Fixed return indices | Scored days | C02 net Sharpe | C11 net Sharpe |
|---|---:|---:|---:|
| 253–503 | 251 | 1.141547 | 1.110764 |
| 504–1007 | 504 | 0.610645 | 0.536817 |
| 1008–1511 | 504 | 0.531851 | 0.544525 |
| 1512–2014 | 503 | 0.393269 | 0.362120 |

The similar volatility and lower gross Sharpe show that the weaker net result is not solely a fee effect. The small third-block gain does not rescue the pooled result. The inherited proportional gross-rescaling approximation remains frequent, exactly as in the intended C02 portfolio contrast. No statistical significance or generalization claim is made from these descriptive differences.

## Executed verification and remaining limits

Before source implementation, the independent verification agent froze a known-interaction full-strategy synthetic workflow and preserved the expected missing-module run. After implementation and independent source review, the unchanged verifier completed four fresh-process original-scorer workflows with **40 passes and zero failures**. Forecast/truth correlation was 0.997914 on its deliberately strong synthetic fixture; first active row was 127; repeat, future-altered and prefix protected values matched exactly. This establishes execution and learning capability on that fixture, not actual-market alpha. See [synthetic summary](../evidence/interaction_workflow_001/summary.json) and [independent review](../reviews/interactions_independent_review.md).

The exact authorized C11 discovery command completed with exit 0 and **20 passes, zero failures**:

```sh
taskset -c 1 python -u tools/run_candidate.py --project . --strategy submission/strategy_interactions.py --config research/configs/C11_interactions.json --out evidence/discovery_C11_001
```

Forecast computation took 26.805 seconds. Candidate rebalance mean was 10.459 ms, p95 16.419 ms and maximum 721.851 ms; the scorer's instrumented mean was 17.559 ms. The measured average was below 100 ms. The runner's 0.093-hour century forecast figure is an extrapolation, not an executed century run. These timings were measured in separate discovery runs and are not a controlled speed benchmark against C02.

Discovery targets respected stock/gross caps, finite arithmetic, net solvency and the realized absolute-beta threshold. These are observed-scope results. Actual-data configured causality, century runtime, later validation and audit are not established by this discovery run. Validation and audit remain unopened.

## Integrity and attribution

Post-run readback confirmed that the live source, config and prospective model plan still match their pre-run implementation record. The source and unchanged base dependencies match the discovery packet's frozen copies; the frozen config has exactly the requested values. The only C02/C11 config differences are candidate identifier and the added `interaction_ridge=1.0` setting. The runner's input-unchanged and source-unchanged checks both passed.

| File | SHA-256 |
|---|---|
| `submission/strategy_interactions.py` | `6a66bf842ea4fbdfde53e9d3423ffeed60088c2db3c27699cdbab2e3c89c7ae2` |
| `research/configs/C11_interactions.json` | `6e8f446417d3d8c51c6fd081ecc775e6f5a0982deebdec01712436655c344dfc` |
| `research/INTERACTION_ALPHA_PLAN.md` | `c1698414bf16862d94e7b500fc5850d6afdd2dd46dae5711a333bd3c2f21d1a4` |
| Frozen synthetic verifier | `f60bf69431b33943cc4199cf99dc5131181e10c08b78de0c3e294509712e898b` |

The hypothesis, candidate implementation, verification and interpretation are AI research under the user's instructions. No applicant empirical discovery is invented. The complete setup, source and input identities, commands, logs, daily ledgers and result summaries remain in the evidence directories.
