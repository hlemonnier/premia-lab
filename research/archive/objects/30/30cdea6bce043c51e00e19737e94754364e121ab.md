# Independent research design review

**Status:** planning only. No strategy has been implemented, no model has been fitted, and no return outcomes or supplied full-sample figures were inspected for this review. Sources were the five small text/code files in the supplied ZIP. The plan below is a proposal, not a claim that any hypothesis works.

## 1. Define the actual scientific problem

The target is the annualized Sharpe of **daily portfolio returns after the scorer's trading costs on the unseen continuation of one synthetic market**, subject to its market-beta condition. The continuation can last decades. This is an anonymous-market forecasting and portfolio-construction problem; the sender's name does not turn it into a continual-learning, neural-network, or reinforcement-learning assignment. The brief separately evaluates alpha research and portfolio construction. Source: `README.md:25–43, 147–161`.

The supplied sample is 3,780 days, 1,000 stocks and 13 anonymous characteristics. Characteristic names carry no justified economic interpretation. We should learn their predictive relationships and stability from permitted data instead of naming them value, momentum, quality, or another familiar factor. Source: `README.md:3–5, 20–23`.

**The useful ambition is finding and defending a durable edge, then converting it into net returns efficiently.** A model family, a large feature library, or a sophisticated optimizer is not evidence of an edge. The assignment explicitly says the naive example is not a hint and that an unassisted language-model solution is a baseline. Source: `README.md:131–138, 163–171`.

## 2. Exact timing and estimand to preserve

For a day indexed `t`, the supplied scorer earns the return on the previously selected weights, drifts those weights using that **gross** portfolio return, then calls `rebalance` using histories through `t` and forecast row `t+1`. It subtracts the trading cost of the resulting after-close trade from day `t`'s return. The next day earns returns on the new weights. The first trade is free and the first empty-book row is discarded. Source: `score.py:49–71`.

Consequences:

1. The supervised pair for a one-day forecast is `X[s-1] -> returns[s]`, never `X[s] -> returns[s]`.
2. A call constructing row `t` may fit models on completed supervised pairs with label dates strictly less than `t` only. Every scaler, missing-value rule learned from data, factor loading, risk estimate, feature selection rule and regime detector has the same information boundary.
3. Trading must use the **drifted** positions passed into `rebalance`, not a cached copy of yesterday's target weights.
4. The primary experiment metrics must reproduce `net = gross_return - after_close_cost`, `std(ddof=0)`, and the market-regression slope in the supplied scorer. Supplementary diagnostics must not quietly replace this objective.
5. The provided loop stops at `days-2`; the final return row is not realized by the stock scorer. All reported evaluation windows must use actual row dates emitted by this loop rather than assume that the last input date was scored.
6. A zero portfolio has zero variance and therefore undefined Sharpe. It is a useful correctness fixture, not a ranked baseline.

The source of truth is `score.py:51–79`. We should not repair its accounting and then claim the repaired score is official.

## 3. Research partitions and contamination discipline

Freeze these positional boundaries before inspecting returns for research:

| Role | Input rows | Use |
|---|---:|---|
| Initial history | `0:252` | Warm-up available before the evaluator begins trading |
| Discovery | `0:2016` | Feature diagnostics, initial hypotheses, fit/portfolio design and bounded development search; scored rows begin only after the first trade |
| Validation A | `2016:2520` | First two-year chronological comparison of frozen finalists |
| Validation B | `2520:3024` | Second two-year chronological comparison of the same finalists |
| Locked internal audit | `3024:3780` | Final three-year audit after method and parameter freeze |

These are zero-based positional slices, not claims about the CSV's day labels. First verify the mapping from row positions to labels.

**Replay all experiments continuously from the scorer's day 252 and slice the resulting daily ledger for metrics. Do not restart the book or learned state at validation boundaries.** The hidden evaluator warms through the available fifteen years and only then measures the future continuation. A validation run starting with an empty book at its own boundary changes the problem. Source: `README.md:112–114`; `score.py:33–71`.

The algorithm is allowed to update its fitted state on all data that has become available during a validation or audit period; the frozen object is the update rule and its hyperparameters. This is how a live adaptive strategy is evaluated. Previously seen labels cannot be used to revise the rule while retaining the original holdout claim.

Mechanical checks over every row—schema, stock ordering, counts, finiteness, duplicate keys—are permissible without comparing future returns or strategy scores. Record the exact scope of such checks. Avoid the supplied full-sample performance/correlation figures before the locked audit; if someone has inspected them, disclose that coarse exposure rather than calling the audit fully untouched.

The brief expressly permits hyperparameter tuning on all fifteen available years (`README.md:88–95`). Our internal holdout is a discipline we choose, not an extra task requirement. Once its results influence a redesign, it becomes development data and must be labelled accordingly. The genuine unseen test is the employer's continuation. A final deterministic refit on all available **past** data may be sensible for continuation, but it must not alter earlier forecast rows using future information.

## 4. A bounded hypothesis ladder

### Stage A — Understand what is measurable

Within discovery only, characterize each characteristic's scale, tails, cross-sectional variation, persistence and redundancy. Establish whether the values are time-varying stock signals, mostly persistent stock attributes, common time signals, or mixtures. These are observations to make, not assumed meanings.

For lagged characteristics, examine both signed predictive association and stable nonlinear shape. Use daily cross-sectional diagnostics and chronological subperiods. Distinguish a predictive conditional mean from a characteristic that merely identifies high-beta or high-volatility stocks. Check signal persistence and alpha decay at a small preregistered set of horizons, e.g. 1, 5 and 20 trading days, because tradable value depends on costs and persistence.

Forward-horizon labels must be complete at a training cutoff; overlapping multi-day labels require an appropriate boundary exclusion. A one-day causal label does not justify blindly imposing a generic large embargo, and a 20-day label does not justify ignoring the unfinished final 19 labels. Cross-sectional observations and overlapping horizons are dependent; millions of stock-day pairs do not imply millions of independent observations.

### Stage B — Establish a defensible alpha benchmark

The first candidate family should be a regularized pooled model using lagged characteristics, with a clearly defined cross-sectional transform and a fixed causal update schedule. A simple ridge model is a natural **candidate** because it makes shrinkage and coefficient stability inspectable; it is not preselected as the winner. Compare raw robustly scaled versus rank-transformed information only if discovery diagnostics justify that choice.

Track coefficient/response-shape stability over time and residual predictive structure. Diagnose whether expected returns are broad-market forecasts, relative-stock forecasts, common group effects, or a combination. A dollar-neutral book is not automatically beta-neutral.

### Stage C — Allow one nonlinear challenger

Only if the discovery evidence indicates stable residual nonlinearity, compare one modest nonlinear specification against the linear family. An additive transform model **or** a shallow, tightly budgeted boosted model is sufficient initially; do not run a catalogue of neural nets and tree libraries. Fit frequency, history window, complexity and regularization all count against the search budget.

The challenger must improve the same cost-aware, beta-controlled portfolio, not just in-sample prediction loss or gross IC. We should be able to state the empirical question it answers. If a nonlinear response is visible but unstable, stronger shrinkage or the simpler model may be better.

### Stage D — Examine omitted structure only when earned

A return-history signal, risk-group conditional signal, or an interaction may replace a failed hypothesis route if a specific residual diagnostic supports it. Do not add these by familiarity with real-market factor recipes. Any clustering or factor estimation used by a live forecast must be fitted causally; the provided full-sample clustered pictures do not supply a deployable group definition.

Use a small number of complementary signals only when their incremental **net portfolio contribution** is established. An ensemble of correlated variants mostly enlarges the implicit parameter search.

## 5. Portfolio construction as a separate research question

Start with a transparent risk approximation and an explicit market hedge. Upgrade to a shrunk low-rank-plus-diagonal risk model if residual correlations make it materially useful. Estimate all risk components from past information, update on a fixed schedule, and keep market-beta shrinkage and stability visible.

A sensible optimization target to investigate is expected return minus a variance penalty minus the actual linear transaction-cost term around the drifted current holdings. This produces a real reason not to trade small expected improvements. It is a candidate control policy rather than a claim that one-step mean–variance maximization is the exact long-run Sharpe solution.

Important comparisons:

- Does the cost-aware policy improve net Sharpe versus the same signal/risk model with mechanical target rebalancing?
- Does the risk model add value versus diagonal risk with an explicit market hedge?
- Is a forecast's persistence sufficient to amortize entry and exit costs? A one-day forecast smaller than a one-way cost can still have multi-day value; the chosen horizon/cost treatment needs an explicit rationale.
- How much net performance comes from unintended market exposure, risk-group exposure, concentration or a small date subset?
- Does the policy remain numerically stable and fast under a longer history and warm state?

Set an internal beta target near zero and use an explicit margin below 0.2. The brief's word “under” is formally ambiguous for a large negative beta; do not exploit that wording. Plan to check the magnitude of realized net-return beta, with the official signed slope reported as well. Scaling a market book down merely to satisfy the numerical beta threshold would evade the intended task, which asks for the market to be hedged out. Source: `README.md:33–37`.

Use conservative size, concentration and gross-exposure controls to prevent pathological drift and numerical failures. These are implementation safeguards, not invented hidden scoring criteria. Do not claim an unconditional bankruptcy guarantee for a short or levered book with an unbounded synthetic return process; disclose the stress envelope actually checked. The score's failure condition is gross daily portfolio return no greater than -1 (`score.py:53–55`), and conservative operation should also examine large costs/net losses.

Avoid a dense 1,000-variable general solver in every daily call unless measured evidence proves it meets the budget. A low-dimensional risk representation and a warm-started specialized solver are plausible routes. Correctness of a custom solver must be specified before implementing it, then verified against an appropriate small reference problem or known analytic cases. This respects the user's tests-before-covered-code rule.

## 6. Concrete search and complexity budget

Proposed initial ceiling, to be frozen in the project ledger:

- **12 complete scored discovery pipeline configurations maximum.** Count the entire signal, updating, risk, cost, and sizing parameter combination. Hand-changed parameters count as a new configuration. This is not permission for a separate 12-point search in every subsystem.
- **Two main alpha families maximum.** A third route requires abandoning or replacing an unsupported route and recording why; it does not expand the cap automatically.
- **Three finalists maximum** promoted to the two validation blocks, with their specifications frozen before either block is scored.
- **Six explanatory ablations maximum**, selected to test distinct claims; never turn an ablation result into an unlogged new finalist.
- **One locked-audit evaluation of the frozen candidate.** Correcting a mechanical bug must be recorded as another exposure; changing a model after seeing the audit forfeits the clean holdout claim.

This is an initial discipline, not a magical optimum. Expand it only for an explicit unresolved hypothesis or defect, with the reason and increased selection risk recorded before doing so. Stress scenarios are robustness diagnostics, not additional model-selection candidates, unless their results change the model.

Prefer an agreed selection rule over “keep improving the number.” First require causal correctness, finite valid weights, survival on executed paths, beta compliance and runtime feasibility. Among eligible finalists, compare aggregate chronological validation net Sharpe, the two separate blocks, and uncertainty of paired daily performance. If differences are unstable or not distinguishable at the available sample size, prefer the simpler, more stable candidate. Do not promise a minimum Sharpe or a victory over the undisclosed employer/Claude benchmark.

## 7. Evaluation evidence required for scientific claims

Each scored experiment should record source/input hashes, exact configuration, code identity, process/environment details, random seeds where relevant, and a daily ledger containing date/row, gross return, trading cost, net return, market return, gross/net exposure, turnover and timing. Save aggregate and block-level metrics together. The official scorer lacks many diagnostics, so a surrounding research runner may record them without modifying the official calculation.

Report official net Sharpe and net beta first. Supporting diagnostics include gross Sharpe, annualized costs, turnover, exposure/concentration, rolling beta, drawdowns, net-return tails, signal strength/persistence and runtime distribution. Risk and turnover matter through future performance and feasibility; they are not hidden additional objectives.

Use time blocks for uncertainty estimates and paired strategy comparisons. If a bootstrap or related diagnostic is used, freeze its block rule and report it as uncertainty conditional on the research process, not a cure for having tried many models. Cost sensitivity, a fixed signal delay, a small neighboring-parameter perturbation and a fixed history/subperiod sensitivity are more informative than repeatedly optimizing until every plot looks attractive.

Show a causal evolution of forecasts and decisions, not just a score. Particularly informative negative evidence is a high-IC signal whose turnover destroys its net edge, a nonlinear improvement that fails the next time block, or an apparently neutral book with persistent realized beta. Record rejected ideas as findings, not failures to hide.

## 8. Horizon and causality robustness

Forecast outputs must be invariant on a prefix when future returns or characteristics are altered, appended or removed, with comparisons at floating-point precision. This includes warm-up behavior, scheduled retraining and all learned preprocessing. A fit schedule keyed to a fraction of the total input length can violate this even if no explicit forward shift appears. Source: `README.md:63–95`.

Predeclare failure modes and expected outcomes before implementing any required isolated checks. Use E2E replay plus future-mutation/prefix comparisons as the default. Verify module/state reset across repeat runs, and compare results under the same inputs in fresh processes. Do not rely on one module instance silently carrying state from a prior experiment.

Long-horizon complexity matters independently of a 15-year runtime. The brief allows about an hour of forecast time per century and an average under 100 ms per daily rebalance on one core (`README.md:59–70, 189–195`). Avoid repeated full-history refits that make runtime grow quadratically, daily dense decompositions, and tensors containing a full covariance matrix for every date. The input characteristics alone are approximately 2.62 GB as a century of float64 values at 25,200×1,000×13; this is a derived scale estimate, not a measured memory budget. Each extra full output channel costs about another 202 MB at that horizon. Keep caches and output channels purposeful.

## 9. Stop/go decisions and honest attribution

Reject a candidate for leakage, invalid shape, nonfinite output, unsafe realized drift, inconsistent repeatability, or failure to fit the measured runtime envelope. Reject its **research claim** when the edge disappears after correct alignment, market control or costs, or depends on one unstable period. A failed research hypothesis can still yield a useful explanation in the final note.

The final deliverable is a working `strategy.py` with a short note at its top and any explicitly named necessary helper files, not a production trading platform or a large research framework (`README.md:140–145`). Keep the richer experiment log and reproducible evidence as supporting material.

The note must distinguish actual AI work from actual human decisions. We cannot attribute an agent-discovered signal or agent-chosen modeling decision to Hugo unless he really made or independently defended that contribution. Maintain a provenance/decision ledger now, and have him examine the final empirical argument so that the submission is understandable and defensible. The brief explicitly welcomes AI, but expressly asks what the candidate added (`README.md:131–145, 160–161`).

## 10. Matters still requiring evidence or clarification

- Data integrity and exact label ordering have not been established by this review.
- No predictive relationship, profitable signal, cost level distribution, achievable Sharpe or feasible model runtime has been established.
- The exact meaning of the beta inequality is not formalized beyond the signed reported slope; targeting near-zero beta avoids dependence on the ambiguity.
- The task does not specify a memory ceiling or precise host/BLAS implementation. Measure one-core performance and report the environment instead of promising portability from an unmeasured run.
- The source brief does not state a submission deadline. The parent agent is checking the email thread; do not infer a deadline from the assignment itself.
- The future generator, regime persistence, hidden-score length and benchmark are intentionally unknown. Design for causal adaptation and stress plausible changes; do not claim the unseen regime will match the sample.

