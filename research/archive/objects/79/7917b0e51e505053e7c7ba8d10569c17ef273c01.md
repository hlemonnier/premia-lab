# Score-directed research: a bounded predictive experiment set

28 October 2026, Europe/Paris. Root owner. Recorded before the new predictive
outputs. Reviewed production source is `ce3fe4e76271709422165d6f24e2fbecd9d0fe07`;
the previous independent review is `87660c1a42824def84951d2355a76d690cd38108`.

## Objective and authority

The user now explicitly prioritizes improving the official evaluation score.
The supplied brief defines that score as future net daily-return Sharpe and
permits parameter development on all fifteen supplied years. All historical
segments are now development data. Their old names do not create new validation.
No pure-alpha, zero-realized-beta, risk-forecast-loss or presentation-quality
criterion may replace net Sharpe as the performance objective. Causality,
solvency, the market-beta condition and the stated runtime limits remain binding.

This plan supersedes the *priority ordering* in REVIEWER_NEXT_DECISION_20261028.md:
the one-day beta diagnostic and raw-risk shadow are secondary research, not
blocking gates for unrelated score improvements. Earlier findings and negative
experiments remain in the record. The rejection rules for R27/B0/B05 remain
honored; this is a new explicitly counted experiment family, not a rescue of them.

Our role remains independent researcher/reviewer and implementation planner for
Claude. Any code here is an isolated research prototype with preserved inputs,
source and outputs. The production handoff and original scorer are unchanged.

## Information available before these experiments

V2 official full-development net Sharpe is approximately 1.242503. Original
score start is row 252; earning rows are 253..3778. Prior 29 ledgers have been
reconciled. In the separately planned opportunity readback:

- Eliminating all current fees on the unchanged V2 gross stream gives Sharpe
  1.289755. This is not a bound on all possible trading-policy changes.
- The fixed same-forecast diagonal/full-factor equal-risk retrospective mixture
  scores 1.22186; the decorrelated-forecast/full-factor mixture scores 1.25617.
  Both use hindsight normalization, are nonexecuted descriptive series, and do
  not establish a new strategy score. They reduce the priority of a blend run.
- Lagged EW63 V2 gross-risk buckets have broadly similar means and rising risk;
  the highest bucket has lower mean. Bucket boundaries are retrospective and
  cannot be used as a trading rule. This motivates an independently specified
  continuous causal sizing rule, not bucket optimization.
- A single coefficient half-life applies to all current forecast terms. Previous
  broad half-life and decorrelation changes do not isolate the two estimators
  below under the selected V2 portfolio policy.

## Four permitted standalone alternatives

All retain V2 features, labels, beta handling, allocator configuration and source
unless the single listed transformation necessarily changes its decisions.

1. **F1: average daily ridge slopes.** For each newly matured cross-section,
   form G=D'D/N and h=D'e/N, solve a=(G+0.1I)^(-1)h, then average a with the
   existing 1008-day exponential half-life. Forecast with the current published
   27-column design. This replaces pooled-Gram ridge with daily-slope averaging;
   no new hyperparameter is selected. Constant-Gram equivalence is a synthetic
   verification condition, not evidence that the actual market has constant G.
2. **F2: partial fast/slow forecast combination.** Fit causal pooled ridge with
   half-lives 252 and 1008, same ridge 0.1 and warm-up 126. Average the fast and slow
   coefficients 50/50 for the first 13 linear characteristics; retain the slow 13
   squared terms and slow beta coefficient. No feature selection by realized
   result, interaction expansion or fitted mixing weight is allowed.
3. **V1: causal inverse-volatility sizing.** Run an unchanged V2 virtual book,
   including its own drift denominator and risk/allocator state. Its earned
   gross returns update normalized EW63 and EW1008 second moments through the
   current close. After 63 earned observations, use
   a=clip(sqrt(max(q1008,1e-12)/max(q63,1e-12)),0.5,2). Before then a=1.
   The actual target is a times the virtual target, subject to V2's gross 5 cap.
   The empty opening at row 252 does not count as an earned observation. The
   first eligible multiplier is computed after close 315 for earning row 316.
   The base book retains its 0.05 stock cap; scaling can raise the actual stock
   weight to 0.10. The brief allows this, and no actual 0.05 cap is asserted.
4. **V2var: causal inverse-variance sizing.** Same as V1, except
   a=clip(max(q1008,1e-12)/max(q63,1e-12),0.5,2). Same clocks, bounds and daily
   updates; no weekly-refresh or alternative-half-life search.

The virtual book is an internal causal signal generator. The unmodified scorer
drifts the actual book and charges actual netted position changes. Multiplying
a stored return ledger does not constitute an executed candidate. Virtual fees
are not inserted into a drift denominator; the original scorer does not do so.
Full details, failure modes and prospective E2E checks are owned in the two
evidence directories for forecast and overlay research.

## One conditional joint alternative, specified before results

If at least one forecast candidate and at least one sizing candidate each beat
the V2 official full-development Sharpe while satisfying the operational checks,
run exactly one joint candidate: the highest-scoring admitted forecast and the
highest-scoring admitted sizing rule. Scores within 1e-8 are numerical ties;
break such a tie in favor of F1 and V1. Score the actual combined strategy;
effects are not assumed additive.
This adaptive choice is part of the recorded development search, not a new
independent confirmation. If either family has no improvement, omit the joint
candidate and report it as unexecuted under this rule.

## Metrics and decisions

Primary: net mean/std(ddof=0)*sqrt(252) from the original scorer, all earning rows
253..3778. Compare against the reproduced V2 benchmark. A score difference no
larger than 1e-8 is numerical equivalence and cannot trigger the joint candidate.
Operational admission requires finite and
solvent actual paths, absolute full-sample regression beta < 0.2, causal protected
forecasts/decisions, and stated runtime feasibility. Report beta and performance
on the old stage masks as diagnostics, not independent confirmations or new
subperiod thresholds. Preserve gross/net returns, fees, exposure, multiplier
activity, source/data identities and failed runs.

Rank admitted candidates by their primary score. A higher score is a development
improvement, not a proved improvement on the employer's unseen decades. Paired
time-block uncertainty informs confidence; no requirement that a 95% interval
exclude zero is imposed as an additional selection criterion. Retain all four
outcomes and the conditional joint outcome if run, including disappointing ones.
Do not optimize another exponent, window, threshold or mixing coefficient in
response to this experiment set. Any subsequent family needs its own concrete
hypothesis and specification rather than a calendar schedule.

## Verification and source ordering

Each owner records a plan, then the E2E verification harness/specification, then
the candidate implementation. Root or another independent reviewer inspects
source and timing before economic execution. No postimplementation unit tests.
The actual scorer is immutable. Existing package bits, input hashes, exact
commands, environment, timing and evidence are preserved. No submission or
outgoing message to an evaluator is authorized by this research plan.
