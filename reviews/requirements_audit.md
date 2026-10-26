# Independent requirements and evaluator audit

Status: planning review only. The supplied brief and Python files were inspected directly from the attachment. No strategy was implemented, no model was fitted, no data outcomes were inspected, and no execution or performance result is claimed.

## 1. The actual task

The project is a synthetic equity-market strategy exercise. It is **not a request to build a continual-learning framework**, and the company name must not become a methodological requirement. The dataset is described as 1,000 stocks, 3,780 daily observations and thirteen named characteristics. The characteristics' names are explicitly not interpretable economic labels. Everything to be learned about the simulated market is to come from the supplied files. [README.md:1–5, 20–23]

The primary objective is **annualized out-of-sample Sharpe of daily net returns over a long continuation of the synthetic market**, potentially decades. The sole stated portfolio constraint is beta to the equal-weight market under 0.2 over that future period. Long, short, leveraged and concentrated positions are allowed; there is no separate turnover, leverage, diversification or aesthetic objective. Solvency still matters because the arithmetic fails at a gross portfolio return of −100%. [README.md:25–43]

The evaluators also read the code and submission note and assess alpha research and portfolio construction separately. Numerical performance alone does not replace a defensible research process, cost treatment, risk model and computational implementation. [README.md:147–161]

## 2. Source hierarchy

1. The assignment README is the behavioral contract and objective.
2. The supplied `score.py` is the concrete local evaluator; preserve an unchanged copy and reproduce its accounting exactly when comparing candidates.
3. `strategy.py` is the required interface scaffold, not a recommended method.
4. The two example strategies are illustrative weak baselines. The README explicitly says their deficiencies are things to fix, not hints. [README.md:163–171]

Any email-specific deadline, delivery channel or amendment must be recorded separately. This reviewer did not inspect email, so none is asserted here.

## 3. Formal contract and acceptance evidence

| ID | Requirement | Source | Required eventual evidence |
|---|---|---|---|
| R01 | Submission module defines `rebalance`; `forecast` is optional. | README.md:45–47 | Fresh-process import and official scorer execution. |
| R02 | `rebalance` returns one weight per stock as a fraction of current capital. | README.md:49–57; strategy.py:24–35 | Complete replay records shapes, finiteness and state evolution. |
| R03 | Only declared named arguments are passed; optional arguments are `held_positions`, `expected_returns`, `returns_history`, `characteristics_history`, `trading_costs`. | README.md:51–57; score.py:26–30, 58–64 | Use exact documented names and run through the supplied adapter. |
| R04 | Position for day t may use only returns and characteristics dated strictly before t. | README.md:74–95 | Causal replay plus future-alteration and truncation checks at multiple cutoffs. |
| R05 | Forecast first axis is days; row t is used to establish positions for day t. Richer payload shapes are allowed. | README.md:63–70; score.py:41–46, 60 | Full history, prefix and altered-future output alignment. |
| R06 | Rebalance is serial and averages below 100 ms per call on one core. State is allowed. | README.md:59–61 | Single-core, thread-limited full replay with per-call timing and hardware/environment recorded. |
| R07 | Forecast may take approximately one hour per century (25,200 trading days). | README.md:63–67; score.py:82 | Measured forecast runtime, century scaling, and a long-history check that does not rely solely on linear extrapolation. |
| R08 | Costs are stock-specific, time-invariant one-way fractions of absolute traded notional. Costs apply to buys and sells. | README.md:20–23, 99–110 | Gross-return, drift, turnover, costs and net-return reconciliation. |
| R09 | Empty initial book; first trade free; local replay starts at day index 252. | README.md:112–114; score.py:14, 49–71 | Boundary trace and known-outcome accounting workflow. |
| R10 | Headline score is mean(net)/std(net) × sqrt(252), with numpy's population standard deviation in the supplied scorer. | README.md:116–129; score.py:74–83 | Independent metric reconciliation on the exact scored observations. |
| R11 | Future beta is slope of daily **net** returns on the equal-weight market's daily return over the scored interval, with centering/intercept. | README.md:33–35; score.py:78–79 | Same-beta calculation on validation periods; report uncertainty and no guaranteed future compliance. |
| R12 | Avoid a gross daily portfolio return ≤−1, which terminates the provided replay. | README.md:39–43; score.py:53–55 | Historical and explicit synthetic stress workflow; finite weights and denominator checks. |
| R13 | Use only numpy, pandas, scipy, cvxpy, scikit-learn, lightgbm and the Python standard library. | README.md:193–195 | Clean allowed-environment run; dependency inventory. |
| R14 | Deliver `strategy.py` with an approximately one-page top note covering market beliefs, design, reasoning, truthful AI/human contributions and long-run failure risks. Declare necessary helper files. | README.md:131–145 | Submission review, runnable folder and explicit provenance note. |

These are future acceptance checks, not results already achieved.

## 4. Exact information clock

At the close of day d, the evaluator first earns that day's gross return on positions selected at close d−1. It drifts those positions, then calls `rebalance` with both histories including day d and `forecasts[d+1]`. The returned vector is held for day d+1. [score.py:51–70]

For a model using the latest characteristic vector, the supervised pairing is therefore characteristics at d to returns at d+1. When forecasting day t, the latest permissible completed training pair is characteristics at t−2 to returns at t−1. Day t−1 characteristics are permissible as the prediction input but their day t label is unavailable. Multi-day labels require their own additional maturity boundary.

Every data-dependent transformation is covered by the same rule: standardization across time, missing-value fills, clustering, feature selection, covariance estimates, hyperparameter refits, volatility scaling, PCA and startup calibration. Full-history `forecast` availability is computational convenience, never information permission. Code review must also inspect side effects: a causal-looking forecast array does not excuse a future-trained global object consumed by `rebalance`.

Cross-sectional transforms of the most recent available day's characteristics are permissible because the entire stock panel for that past day is available. Static costs are explicitly passed and can be used directly. The thirteen names must not be decoded into real-market feature assumptions. [README.md:20–23, 79–95]

The README explicitly permits choosing fixed design parameters on all fifteen supplied years. That permission does **not** make an online fit on the entire unknown scoring history causal. An unambiguous implementation trains/refits using only matured past observations and uses fixed, disclosed development choices. A final unused development period is a research discipline, not a restriction imposed by the brief. Do not present use of the whole supplied sample for tuning as prohibited. [README.md:88–95]

## 5. Scorer details and discrepancies that matter

### 5.1 Boundary convention

For T observations and `start=252`, the loop runs `today = 252, …, T−2`. The first row (day 252) is removed. Therefore the recorded scoring rows are **253, …, T−2**, yielding T−254 rows. For the stated T=3,780, that is 3,526 daily scoring rows. [score.py:51, 71]

The first position is selected after the close of day 252, using histories through day 252; its first earned return is day 253. The return for the final CSV day T−1 is not earned by the scorer. Conversely, transaction costs on the rebalance after day T−2 are charged although the resulting positions' next-day return is outside the scored output. The first trade is free. This is a specific evaluator boundary, not a reason to modify the official file or optimize a terminal-day exploit.

### 5.2 Net-return accounting is additive

Daily net return is gross portfolio return minus the cost of the rebalance at that same day's close. Drift uses `1 + gross_portfolio_return`, not `1 + net_return`. Costs do not rescale next-day target weights inside this evaluator. Gross exposure reported in each row is exposure **after** the day's rebalance, while that row's gross return was earned by the previous position. [score.py:53–69, 75–83]

Do not silently replace this with a more realistic self-financing NAV model; reconcile against the supplied arithmetic and discuss limitations if relevant.

### 5.3 Stated requirements are not all enforced by assertions

The scorer does not itself check no-lookahead, the beta limit, the runtime limits, exact output shape, finite forecast/position elements or solver status. It asserts forecast row count and gross daily solvency. Returning bad shapes or NaNs can lead to unintended broadcasting, arithmetic failures or misleading metrics. Passing one invocation of `score.py` is not evidence of full compliance. [score.py:41–71]

### 5.4 File-order assumptions

`load()` converts returns to an array in CSV column order, costs to an array in CSV row order, and characteristics to a flat array reshaped into `(days, stocks, k)` without sorting or checking labels. Data integrity checks must verify the original CSV ordering and exact day/stock alignment before relying on these arrays. Avoid “fixing” only a research loader while the grader will use a different order. [score.py:17–23]

### 5.5 Runtime measurement caveats

`report` averages timing in rows returned by `run`; because the initial row is discarded, its first rebalance is omitted from that average. Preserve official measurements, but separately include startup and long-run behavior so heavy first-call work is visible. The full run requires a thread-limited environment; multithreaded BLAS can otherwise make “one core” timing untrue. Forecast runtime divided by observed day count and scaled to 25,200 is only an extrapolation; it does not prove bounded century behavior. [score.py:42–45, 57–65, 71, 82–83]

### 5.6 Example mean-variance implementation

The naive example's quadratic term is the uncentered second moment of trailing returns, despite the README describing covariance. With 252 observations and 1,000 assets, its risk matrix cannot be full rank. It has no explicit shrinkage, beta control, solver-status handling or solvency guard and solves a cvxpy problem every day. These explain why merely refining that example is an insufficient research plan; they are not evidence about the best strategy for the actual data. [example_naive_mv.py:20–27; README.md:163–171]

## 6. Material ambiguities and conservative operating assumptions

| Question | What is known | Planning assumption that allows progress |
|---|---|---|
| Is beta threshold signed or absolute? | Wording is “under 0.2”; intent is to hedge the market out. | Target beta close to zero and evaluate absolute beta with a margin, without claiming the brief explicitly requires absolute beta. Do not exploit a large negative beta. |
| How exactly is hidden warm-up/state constructed? | README says run starts like `score.py` at day 252; all supplied fifteen years are warm-up and scoring is after them. | Causally replay the supplied years and carry state into continuation. Do not reset the book or fitted state at the hidden scoring boundary unless clarified. |
| What is the deadline and submission route? | Not stated in archive. | Root must resolve from email or ask one focused question after doing the useful planning work. |
| Is a serialized model fitted on all supplied data permissible during warm-up? | Fixed tuning on the supplied years is allowed; strict historical forecast causality is also required. | Prefer an unambiguous causal training path. Do not backfill historical forecasts with a model trained on later labels. If external model artifacts are essential, explicitly record training cutoff and activation time. |
| What hardware and precise century runtime cutoff are used? | One core, average under 100 ms for rebalance; forecast “about an hour” per century. | Benchmark with one thread, leave substantial runtime headroom, report hardware and scaling honestly. |
| Are cross-sectional identities and feature definitions stable in the continuation? | Same market is described; no changing-universe protocol is supplied. | Use the documented fixed stock/feature dimensions while ensuring history length can grow substantially. Do not invent universe expansion requirements. |

Beta is scale-sensitive whereas Sharpe is approximately scale-invariant with linear costs. This mathematical observation does not justify using market exposure as the main alpha or hiding beta through a tiny book. Portfolio sizing also changes drift and, therefore, subsequent costs, so exact scale invariance must not be assumed from the linear one-period equations. Zero-dollar exposure is not the same thing as zero market beta. [README.md:33–43; score.py:53–69, 79]

## 7. Verification plan consistent with the user's testing policy

The user has prohibited writing unit tests after the implementation they cover. Record this as a project rule before any new implementation. Prefer a small number of meaningful workflow checks with independently specified expected behavior:

1. **Data-to-score baseline workflow:** verify schemas and index alignment, run supplied equal weight, capture official output and account for its expected beta-condition failure. Equal weight is a deliberate negative control, not a feasible candidate.
2. **Known-outcome accounting workflow:** before implementing a custom replay or optimizer, document tiny synthetic histories whose position drift, cost and scored rows can be calculated explicitly; execute the full import/forecast/rebalance/score path. This is an E2E contract check, not a later mirror of implementation details.
3. **Causality workflow:** from fresh process/module state, compare original history with multiple future-altered histories and truncated prefixes; ensure all affected forecasts and actual position paths before each information boundary remain invariant to stated floating-point tolerance. Include `forecast` state consumed by rebalance, not only array rows.
4. **Chronological research workflow:** freeze candidate definitions and development choices, train/retrain causally, evaluate contiguous later periods through official accounting, and write all candidate outcomes to an append-only experiment ledger. No random row-wise splits.
5. **Long-run, state and stress workflow:** run documented long synthetic/stress inputs for shape, finite arithmetic, solvency controls, deterministic restarts and computational scaling. Label these as engineering checks; repeated/resampled histories do not prove hidden-market alpha.
6. **Clean submission workflow:** build the exact hand-in folder, run it from a fresh process with only allowed dependencies and declared assets, and produce a final manifest and rerun instructions.

Before any isolated test is necessary, first commit its failure modes, edge cases and expected outcomes; then write its tests; only then implement the covered code. Never retrofit implementation-mirroring tests or label an unrun check passed.

Each E2E artifact should include the purpose, source/input hashes, exact code/config revision, environment and single-thread settings, setup and inputs, complete command, expected results, actual results, exit status, timings, stderr/stdout and relevant output paths. A reviewer must be able to reproduce it without private memory or unstated steps.

## 8. High-priority planning cautions

- A sophisticated model is not a requirement. A deep model, reinforcement learning, a continual-learning architecture or a software platform is justified only if controlled evidence shows incremental value for net future Sharpe.
- Keep alpha estimation and portfolio construction assessable separately: a forecast-quality result does not establish profitable, low-beta trading after costs; a sophisticated optimizer does not rescue nonexistent predictive information.
- Do not optimize the example's in-sample number as the project goal. The objective is performance over a long future generated by mechanisms not disclosed to us.
- Do not use characteristic names, the user's prior interests or assumptions about actual US equities to assign meanings to synthetic signals.
- Hidden-future performance is not verifiable now. Report evidence and uncertainty, not guarantees or claims of optimality.
- The hand-in is compact: the useful complexity belongs in research evidence and necessary algorithmic choices, not an unnecessarily large submission package.
- The AI contribution statement must remain truthful. Multi-agent reviews do not become human judgments; the user must genuinely understand and be able to defend the final reasoning.

