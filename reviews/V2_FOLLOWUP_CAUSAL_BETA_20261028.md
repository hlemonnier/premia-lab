# V2 follow-up: causal beta correction and experiment fidelity

28 October 2026, Europe/Paris. Reviewed source:
[`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`](https://github.com/hlemonnier/continual-research-takehome/commit/ce3fe4e76271709422165d6f24e2fbecd9d0fe07).
This is an independent audit of Claude's follow-up, not a new candidate run or a
change to the strategy. Parent review covers statistical return readback; a
separate engineering reviewer covers allocator and default-package fixes.

## Verdict

**The implemented shrinkage uses matured historical information, and the
independent complete-scorer experiment supports causality with the correction
active. The submitted future-beta MSE numbers reproduce exactly. R27's shadow
comparison and the matched-diagonal construction implement their stated
contrasts correctly.** These results support the code and the particular risk
measurement. They do not establish that latent betas literally mean-revert by
17%, that centering makes beta-error risk mathematically invisible, or that a
market-regression intercept identifies pure tradable stock-selection alpha.

The engineering and research claims should be kept at their actual scope. In
particular, lower individual-stock error against noisy next-year beta estimates
is useful evidence, but it is not a guarantee of next-day portfolio beta control.

## 1. Information timing in the new path

Source references in this section are to `handoff_v2/model_v2/engine.py` at the
pinned commit.

| Operation | Exact information used | Judgment |
|---|---|---|
| Raw beta at array row `t` (`causal_betas`, lines 75–89) | Return rows `[max(0,t-252),t)` | Historical only. |
| Eta pair (`_EtaTracker`, lines 102–117) | Pre-window `[s-252,s)` and post-window `[s,s+252)`, admitted only when `s+252 <= t` | The nominal future label is fully matured when admitted. |
| Forecast label on return row `s` (lines 137–144) | Corrected beta and eta available from rows `<s`, multiplied by realized return/market on row `s` | Label becomes available at the close of `s`; no premature update. |
| Forecast row `t` (lines 158–166) | Newest training pair `X[t-2] -> E[t-1]`; prediction uses `X[t-1]` and raw beta computed from rows `<t` | Causal under the scorer's contract. |
| Risk update for realized row `s` (lines 180–192) | Loadings from `X[s-1]`, raw beta from `R[:s]`, eta from fully matured pairs through prefix length `s`; response is `R[s]` | Update occurs only once row `s` is available. |
| Hedge after close `d` (lines 223–226) | Prefix length `T=d+1`, so beta and eta may use all rows through `d` | Causal for positions earning row `d+1`. |

Passing the full array into `_EtaTracker` does not itself create leakage: the
slice bounds and maturity condition restrict every selected pair. The expanding
list of slopes is reset in each new forecast or risk state; in a normal scorer
run its calls have monotonically increasing history lengths.

The plan's phrase “after close t” should be made consistent with the code's
prefix-length convention. The code first activates the hedge correction after
close row 503, when rows `[252,504)` have become available, for return row 504.
It first uses a corrected label on return row 504. This is legitimate information
timing, not a future-data access. Explicitly distinguishing close row `d` from
prediction row/history length `t=d+1` removes the one-day ambiguity in the prose.

The forecast beta characteristic remains the raw standardized column. For an
affine shrinkage `b_corrected=a*b_raw+c`, its centered standardized column is
the same when `a>0` and neither standard deviation is affected by the numerical
floor, including the existing fixed clipping convention. The
observed correction satisfies that condition. This is not an unconditional
identity for arbitrary estimated eta: the code neither constrains eta nor
guards a zero cross-sectional denominator in `_EtaTracker` line 115. A future
implementation specification should state what happens when the slope is
nonfinite or nonpositive. No such failure occurred in this audit's data.

## 2. Independent actual-data beta diagnostic readback

The plan was written before execution and peer-reviewed. The new diagnostic
workflow recomputes beta by centered matrix products directly; it does not call
the implementation's `_EtaTracker`, `_window_beta`, or `_correct` to generate
the actual-data comparison. It preserves the exact submitted decision grid and
records the newest matured training endpoint at every decision.

| Submitted-sample quantity | Independent result |
|---|---:|
| Evaluation dates | 144 |
| First eta | 0.09480528749040684 |
| Last eta in this evaluation sample | 0.17727840712348708 |
| Mean raw-beta MSE | 0.04313413259015087 |
| Mean corrected-beta MSE | 0.03929552541627599 |
| Dates with smaller corrected MSE | 139 / 144 = 96.5278% |
| Largest absolute discrepancy from committed aggregate | 0.0 |
| Any unmatured label admitted to eta? | No |

Evidence: [beta_mse_readback.json](../evidence/v2_followup_causal_beta_20261028/beta_mse_readback.json)
and [beta_mse_by_date.csv](../evidence/v2_followup_causal_beta_20261028/beta_mse_by_date.csv).

### What “97% of dates” means

Successive evaluation windows begin 21 days apart and last 252 days, sharing
**231 return days**. The result is not 144 independent successful predictions,
nor a 97% probability that the correction will be better on new data. It is a
descriptive success frequency on overlapping evaluation windows.

Before execution, this audit also specified all twelve phase cohorts of that
21-day grid. Within each cohort, evaluation starts are 252 days apart. Every
cohort has a negative mean paired MSE difference; the range is approximately
`[-0.004991,-0.003179]`. Cohorts contain twelve dates each, with corrected-beta
win frequencies of either 11/12 or 12/12. This is useful descriptive stability,
not twelve independent replications: cohorts overlap one another, parameters
share expanding training histories, and no independence theorem is asserted.

### Small endpoint omission

The submitted loop uses `range(504,T-252,21)`. With `T=3780`, the last legal grid
date `t=3528` is excluded although `[3528,3780)` is a complete future window.
The audit prespecified and retained this boundary sensitivity separately.
Including that one point gives 145 dates, raw MSE `0.0431366591`, corrected MSE
`0.0393158680`, and win frequency 96.5517%. The substantive MSE conclusion is
unchanged. This is a small sample-boundary omission, not lookahead.

### The estimand matters

The observed future beta is itself a noisy regression estimate over the next
year. If `b_pre=b_true+u` and `b_post=b_true+v` with constant latent beta and
independent zero-mean errors, the cross-sectional regression slope is

\[
\frac{\operatorname{Var}(b_{true})}
     {\operatorname{Var}(b_{true})+\operatorname{Var}(u)}<1.
\]

Thus a slope around 0.82 can arise without any true-beta dynamics. The submitted
constant-true-beta synthetic example is itself consistent with this distinction.
Use “shrinkage predicts future-window beta estimates more accurately in this
sample,” rather than claiming that the true betas drift 17% toward one.

The horizon and weighting are also different from the trading objective. The
diagnostic minimizes an equally weighted stock-level MSE against a 252-day
outcome. The strategy earns next-day returns on endogenous, signed, unequal
weights. Good stock-level average calibration need not eliminate a systematic
portfolio exposure error. The observed roughly −0.014 error relative to both
explicit targets is therefore informative; it should not be rounded away as
“precise control,” although it passes the specified ±0.02 empirical tolerance.

## 3. Independent corrected-path complete-scorer experiment

The provided complete-scorer fixture and capture functions were reused with
820 rows, 96 stocks, thirteen characteristics, seed 20261028, and nonzero costs.
The unchanged strategy and scorer were copied to an isolated evidence source
directory. All five runs used packaged settings with `beta_shrinkage=True` and
`beta_target=.05`; no forecast or allocator code was changed.

The maturity-sensitive cutoff was row 650. Eta at this cutoff was
`0.13997371796016989`, so the experiment exercised the correction rather than
its initial zero-eta fallback. The altered future changed both later forecasts
and later targets, demonstrating a nontrivial stimulus.

| Compared case | Protected forecasts | Protected targets | Economic scorer columns |
|---|---|---|---|
| Replaced returns and characteristics from row 650 onward | Exact | Exact | Exact |
| Same future with Fortran-layout X only | Exact | Exact | Exact |
| Same future with both R and X Fortran-layout | Exact | Exact | Max difference `3.47e-18` |
| Truncated prefix of length 650 | Exact | Exact | Exact |

For full histories, forecast rows through 650, allocation decisions through
close 649, and economic scorer rows 253–649 were protected. For the truncated
case, comparison respects the scorer's last scored row 648. The wall-clock
timing column is excluded.

The one small difference is produced by the unchanged scorer's dot product on
a different return-array view. Before this audit executed, the engineering
reviewer had observed the same mechanism in its separate fixture. The plan was
amended prospectively to preserve exact forecast criteria, add the strict
X-only case, and allow a `1e-12` target/economic tolerance only when returns are
also Fortran-layout. This audit did **not** change an acceptance criterion after
seeing its own result. All prespecified comparisons passed; blanket bitwise
identity across every scorer input layout would still be inaccurate.

All 2,665 observed synthetic allocation calls received `ok` certificates, with
no recovery. This is a report of the executed workflow, not independent proof
of every numerical certificate condition. Reviewed source hashes and the
isolated copies remained unchanged after all runs.

Evidence: [corrected_path_e2e.json](../evidence/v2_followup_causal_beta_20261028/corrected_path_e2e.json),
[prospective plan](../evidence/v2_followup_causal_beta_20261028/PLAN.md),
[peer source review](../evidence/v2_followup_causal_beta_20261028/pre_execution_peer_review.json),
[exact command](../evidence/v2_followup_causal_beta_20261028/command.txt),
and [workflow source](../evidence/v2_followup_causal_beta_20261028/readback_and_e2e.py).
The workflow exited zero; stderr is empty. No full actual-data candidate
strategy was rerun by this sub-review.

## 4. R27 and matched-diagonal fidelity

Source review of `research/v2/r27_shadow.py` confirms the inherited primary
risk score is implemented as specified:

- Capture the original V2 targets through the unchanged scorer.
- Predict with each risk state after absorbing only returns through decision
  close `t`, using loadings published at that close.
- Compare exactly the 3,526 earning rows 253–3778 using `g=w_t'R[t+1]`.
- Use physical factor scale 1 in both shadow matrices, the `1e-16` floor, and
  zero loss for an exactly zero book.
- Report the fixed 21/63/126-day paired block intervals and all stage masks.
- Preserve cross-sectional residual demeaning and the beta information dates.

The candidate switch adds the centered/clipped beta column to risk while the
mean forecast remains unchanged. Specific risk changes mechanically because
the additional factor explains part of the daily response; that was explicitly
allowed. The observed risk-gate pass and subsequent Sharpe-rule rejection are
therefore not inconsistent. The gate requires a negative sample mean loss
difference, not a confidence interval entirely below zero.

The matched-diagonal switch in `engine.py` lines 228–230 also implements the
correct algebra at fixed risk state: it adds `row_sum((D@L)**2)` to `d`, then
sets `L=0`. Its pre-solve marginal variances match the original matrix exactly
up to floating arithmetic. The larger resulting book and active gross cap are
downstream responses to removing correlations. They matter when interpreting
performance and feasibility; they do not mean the intended matrix intervention
was implemented incorrectly. This control supports a conditional statement
about the current allocation policy, not an unrestricted claim that all V2's
advantage over C09 has been attributed to correlations.

## 5. Correct the centering argument

The added risk beta column is itself centered. R27 could not repair an exposure
that centering alone made unrepresentable. More precisely, in the illustrative
shrinkage relation with cross-sectional mean beta one,

\[
b_{true}-\widehat b=\eta(\mathbf1-\widehat b),
\qquad
\mathbf1^\top(b_{true}-\widehat b)=0.
\]

The omitted beta-error loading is a **centered** vector. The 26-column space can
represent its projection; the reported approximately 93% residual span means
the remainder is largely missing from that factor representation. It does not
mean the model assigns literally zero risk: daily unexplained variation also
enters its diagonal specific-risk estimates, albeit without the common
covariances that a diversified portfolio can be sensitive to.

Centering removes a uniform loading from the factor span, but a beta-neutral
net-long book is not generally a uniform portfolio. The scalar risk quantity
is `w'Sigma w`, not just the fact that `1'w` is nonzero. The useful mechanism is
an inadequately represented common beta-error direction, not a universal
blindness caused by centering.

Likewise, shrinkage in forecast labels, risk residuals, and the hedge changes
three parts of the policy together. This can be a coherent alternative design;
it is not a controlled attribution of how much of V2's gain came from each
part. The raw beta feature remains a potential predictive direction even after
the label correction. Any subsequent mechanism claim needs a smaller frozen
contrast rather than inferring the whole story from B0/B05's total Sharpe.

## 6. Versioned plans and outcome decisions

The Git history and exact early-plan blobs were independently retrieved:

| Plan | Present in commit | Subsequent result commit | Plan unchanged at reviewed head? |
|---|---|---|---|
| R27 | `5bd1c169` | Risk result `2108ecaf`; policy result `ec312ec3` | Yes |
| Explicit beta | `c9fcbd8e` | Candidate results `ce3fe4e7` | Yes |

R27 additionally inherits the earlier reviewer's already versioned primary
metric and retention rule. The Git sequence supports plan-before-final-result
publication. It cannot reconstruct the exact within-session ordering of every
local code edit or diagnostic: the explicit-beta plan, implementation, test
logs and diagnostic results were committed together. That limit is distinct
from claiming the rule was changed; the plan blobs did not change.

The implementation retained V2 because R27, B0 and B05 failed their specified
Sharpe thresholds. That is faithful reporting. Those thresholds are exploratory
selection conventions on exposed data, not statistical equivalence tests or
proof that a marginally lower score implies worse future performance. In
particular, an interval including zero does not establish a “statistical tie.”
Report “no resolved performance difference under this comparison” unless an
equivalence margin and suitable procedure were specified.

Evidence: [plan_commit_readback.json](../evidence/v2_followup_causal_beta_20261028/plan_commit_readback.json).

## Recommendations from this sub-review

1. Accept the causal timing and the reproduced stock-beta MSE improvement within
   their measured scope. Preserve the negative strategy outcomes.
2. Correct the prose claiming literal beta mean reversion, complete invisibility
   due to centering, precise realized exposure control, and identified pure alpha.
3. If beta correction remains a candidate, evaluate its portfolio-relevant
   calibration on fixed holdings and the relevant return horizon before changing
   its parameters. A constant correction that improves one-year stock MSE can
   still bias next-day portfolio exposure.
4. Clarify the eta estimator's finite/degenerate-sample behavior and the sign
   condition behind the standardized-feature identity. Engineering separately
   identifies nonzero-target feasibility after gross scaling.
5. Keep covariance intervention, forecast-label intervention and hedge
   intervention separately interpretable in the next research specification.

This audit and its observational analysis are AI-generated research assistance.
No applicant contribution or unexecuted empirical test is implied.
