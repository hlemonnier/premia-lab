# Candidate causality gate: specification before implementation

**Status at creation:** specification only. No candidate has been inspected or tested under this plan; no pass is claimed.

**Purpose:** verify that the submitted code's decisions for an earning day use only information strictly before that day. Use complete evaluator workflows and independent fresh processes. The original scorer and the user-mandated test-order rules remain authoritative.

## Permitted data and frozen inputs

- Before finalist freeze, use only actual discovery rows `[0,2016)` or explicitly generated synthetic histories. Do not load actual validation/audit observations for candidate debugging, causality or runtime checks.
- The candidate retains its documented 1,000-stock, thirteen-feature interface; arbitrary two-stock generality is not required.
- Freeze the candidate source/helper hashes, configuration, seeds, environment and cutoff manifest before executing comparisons. The verification worker must not share a fitted object or module instance with another run.
- Full-file hashes and structural inspection remain distinct from economic analysis. Verification must use a bounded discovery input artifact, not accidentally pass the entire actual CSV into a candidate.

## Failure modes specified before candidate code

1. An unshifted characteristic or return reaches the target for that same day.
2. A scaler, imputer, fit, risk estimate, cluster, selected feature, initialization or position-size calibration uses observations unavailable at the decision time.
3. A training label, including a multi-day return, has not matured at the fitting cutoff.
4. The total input length determines a refit schedule, warm-up rule or historical transformation, changing previous decisions when data are appended or truncated.
5. Forecast outputs appear causal but `forecast` stores a future-trained object that `rebalance` consumes.
6. A module cache, random generator or process state carries information from a previous run.
7. Input arrays are mutated in place, or code reads hidden local files instead of respecting the supplied arguments.
8. A test falsely rejects legitimate post-cutoff differences, or falsely passes after a failed comparison.

## Exact altered-future assertions

For a cutoff `c`, preserve input rows before `c`, change returns, characteristics or both from `c` onward, and leave static trading costs unchanged. Perturbations must remain finite, shape-compatible and inside the admissible input domain. Record the exact transformation and changed-element counts; an identity alteration is not evidence of sensitivity coverage.

With a fixed candidate and isolated state:

- **Forecast:** compare every output channel on rows `0 ... c`, including row `c`. Forecast row `c` must not depend on data at `c`.
- **Positions:** compare targets for earning days `t <= c`. The target for day `c` was selected at the close of day `c-1`.
- **Economic ledger:** compare realized gross return, after-close cost and net return only on scoring days `t < c`. Changed returns at `c` alter that day's realization; changed characteristics at `c` may change its closing trade and cost. These boundary differences are legitimate.
- **State:** inspect state that actually contributes to protected outputs. Do not demand equality of an entire cache containing unused future forecast rows or other future-only elements.

All comparisons use the supplied call sequence: forecast once on the supplied history, then serial rebalance from day 252 with the same empty book. If there is no forecast function, record forecast checks as not applicable and still test actual portfolio decisions.

### Perturbation and boundary coverage

Before each candidate's first run, the manifest selects deterministic admissible return-only, characteristic-only and joint alterations. Suitable interventions include bounded return scaling and time-permutation/replacement of characteristic panels with other values from the allowed discovery/synthetic domain. Explicitly record domain checks and confirm the changed suffix is nonempty. No protected actual outcomes may be used to construct a perturbation.

For a 2016-row discovery replay, the initial candidate-independent cutoff set is `[0,1,251,252,253,1008,2014]`. Select representative first-fit, first-scale/risk-refresh and later-refit/window-eviction boundaries after reading the fixed candidate's schedule, and record them **before execution**. Cover distinct code paths; do not blindly rerun every refresh day. Comparisons that have no protected scored rows or targets are recorded as empty/not applicable, not as coverage of those paths.

A shorter first development replay may use the corresponding valid subset of cutoffs with its actual length recorded. That run cannot claim coverage of later behavior. Finalist coverage must include relevant startup and later-update paths.

## Prefix-length and synthetic-append comparisons

- Compare the full discovery replay against truncated prefixes, initially lengths 504, 1008 and 2015. Compare forecast outputs on their complete common prefix, earning-day targets on the common emitted target days, and daily ledgers on their actual common score days. Respect the scorer's final-row omission in both runs.
- Append a predeclared synthetic continuation to the discovery prefix and verify invariance of all common historical outputs. The synthetic extension is not actual hidden data and cannot establish alpha generalization.
- Training and portfolio state must start from the same fresh-process initialization and evolve continuously. Never warm-start the shorter run with a fitted object from the longer run.

## Numerical and execution expectations

The default expectation is exact deterministic agreement. Also record maximum absolute/relative error and compare with fixed float64 tolerances `atol=1e-14, rtol=1e-12` for forecasts, positions and economic values; row indices, shapes and configuration identities are exact. These are strict numerical-roundoff tolerances, not statistical tolerances. A changed seed or materially changed numerical result is not excused as model uncertainty.

If a particular algorithm requires a different justified roundoff tolerance, document the numerical reason and amend the expectation **before the affected verification run**, preserving prior failures and the reason for the revision. Do not enlarge tolerance merely to make a leakage symptom pass.

Every independent run starts a new Python interpreter with numerical/estimator thread controls fixed before imports. Freeze source/configuration and forbid unintended input mutation. Preserve both normal and altered input hashes, all subprocess exit statuses and logs. Review source/helper code for external file access and future-informed caches; finite numerical interventions alone do not prove universal causality.

A failure later in an altered suffix is a robustness observation, not by itself proof of earlier leakage. If protected outputs were saved completely before that failure, they can support a clearly scoped prefix comparison. If they are unavailable, record that comparison as unverified; never fabricate equality or label a failed execution as passed.

## Required evidence and gate outcome

Each causality E2E packet must contain the frozen plan, worker/runner, candidate/helpers and configuration identities; permitted data source and indices; exact setup and rerun command; original/altered input manifests and perturbation recipe; expected invariants and tolerances; per-cutoff/channel/day actual comparison results; target and economic traces; stdout/stderr; environment/seed/thread metadata; before/after input hashes; and a final status.

Use `executed/pass`, `executed/fail`, `incomplete`, `blocked` or `not applicable` literally. A gate pass requires all nonempty required comparisons to complete within the predeclared tolerance, with source review finding no prohibited access. Any genuine material mismatch in a protected output fails causality regardless of portfolio performance. Passing tested cutoffs establishes the tested evidence, not a mathematical proof covering every future history.

**No E2E has been executed under this plan at creation time.**

## First candidate smoke profile, fixed before its harness implementation

The first execution uses actual discovery rows `[0,600)` only, read from the ready discovery cache. It compares a fresh-process baseline and identical fresh-process repeat; return-only, characteristic-only and joint suffix interventions at cutoffs `[0,125,252,400]`; a 384-row prefix; and a synthetic 64-row append. The 600-row baseline/repeat supplies the longer prefix comparison. This is bounded startup/update coverage, not a claim that later discovery or multi-decade behavior has been verified.

Return interventions multiply the suffix by 0.5, pulling values toward zero without increasing magnitude. Characteristic interventions reverse the suffix's time order, preserving every stock/feature's observed value set; a one-row suffix, if requested later, uses an earlier allowed panel instead. Joint cases apply both. Changed-element counts and exact prefix preservation are recorded. The synthetic append reuses the first 64 allowed panels in reversed time order, with their returns scaled by 0.5, and is explicitly marked synthetic.

Before executing a particular candidate, inspect its fixed initialization schedule. If the first-active forecast or first-earned target boundary reveals an uncovered concrete path, add the corresponding cutoff to the run manifest before execution. This does not change the predeclared information rule or tolerances. No numerical outputs are consulted to choose those boundaries.

The harness must invoke a new Python interpreter for each scenario, freeze the candidate and its sibling Python helpers, and run the unmodified original evaluator. It may record forecast and target outputs through a transparent adapter but must not fit the forecast twice or substitute its own P&L engine. Record only complete comparisons; a failed worker is never relabelled as a successful execution.

## Integration revision before first candidate execution

This revision resolves the independent review's configuration and startup-coverage findings before any C01/C02 numerical run. It changes no information boundary or numerical tolerance and adds no isolated unit tests.

- Require an explicit JSON configuration at the controller. Freeze it with the candidate and protocol, hash it, pass its frozen path and expected hash to every worker, and call `configure(config)` once before forecast/rebalance. A nonempty configuration with no configure interface is a setup failure. Record both the requested configuration and the effective public CONFIG, where available. Compare each worker's requested configuration identity with the baseline. An unchanged default-module run cannot stand in for another configuration.
- Preserve that explicit configuration in exact rerun commands. Check the frozen config, protocol, candidate, scorer and input identities after execution. Every scenario has a fresh module/process even when its configuration is identical.
- Permit several predeclared shorter prefix lengths in one controller run; each is compared with the common original initialization and correct endpoint mask. The smoke profile keeps length 384; the full-discovery profile uses 504, 1008 and 2015.
- Add the first-earned target boundary 253. The first alpha implementation declares 126 matured pairs, so its first active forecast is row 127. Its pure trailing-risk estimate first becomes active at 20 observed rows; the first rolling eviction occurs across rows 253/254. The smoke candidate profile is `[0,20,21,127,252,253,254,400]`; the full-discovery profile is `[0,1,20,21,127,251,252,253,254,1008,2014]`. These boundaries are selected from the fixed implementation schedule, not from performance or numerical comparison results. Confirm them against the completed code before running, and record any schedule correction before execution.
- Require all forecast output values, including the changed suffix, to be finite and record the full shape. A suffix failure remains a failed execution with unavailable comparisons rather than proof of earlier leakage. Full input arrays are made read-only and their hashes are still compared after execution.

The smoke run establishes bounded startup behavior only. The full-discovery run, when executed, establishes the declared discovery cutoffs and prefix/append cases only. Later actual validation/audit observations and century-length behavior remain outside this verification.
