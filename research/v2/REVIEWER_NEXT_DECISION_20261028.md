# Reviewer handoff after explicit-beta experiments

28 October 2026, Europe/Paris. Baseline under review:
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`. This specifies unexecuted next
diagnostics and engineering work. It does not override any completed experiment's
retention rule. There is no calendar schedule.

## Decision now

Keep V2 as the current candidate. R27, B0 and B05 did not clear their recorded
retention rules. Preserve their implementations and all results. B05 is a useful
exposure-control instrument, not a demonstrated Sharpe improvement over V2.

Read [the independent follow-up review](../../reviews/V2_FOLLOWUP_INDEPENDENT_REVIEW_20261028.md).
Its most discriminating new observation is that the B05-minus-B0 net-return
increment has market R-squared .999261 and beta .050239: the target knob adds
almost pure market exposure. The shared absolute beta error around -.014 remains
and is not caused by final gross scaling, solver feasibility or fee covariance
in the independently replayed actual paths.

## 1. Correct interpretation and complete the engineering contract

Replace the following claims in the handoff/research notes:

| Current claim | Supported wording |
|---|---|
| Centering makes beta-error risk invisible | Most of the centered beta direction lies outside D26; centering itself preserves eta*(1-bhat). Specific risk and its projection capture some variation, but may miss common covariance. |
| Betas truly drift 17% toward one | Shrinkage improves forecasts of noisy next-year beta estimates in this sample; measurement error and genuine beta dynamics have not been separately identified. |
| The market regression settles that no premium exists | A large market loading is detected; the constant intercept is unresolved. A zero-alpha simulation demonstrates a possible channel rather than the true generator. |
| Pure tradable selection Sharpe is 1.1 | A full-sample market-residual Sharpe of approximately 1.08–1.10 is observed; no corresponding costed causal neutral strategy has been demonstrated at that level. |
| Explicit beta is controlled precisely | The target increment is reproduced almost one-for-one, while both corrected policies retain an approximately -.014 absolute level error and pass the stated .02 tolerance. |
| B05 is statistically equivalent to V2 | The difference is unresolved and B05 fails the point-estimate replacement rule; equivalence needs a previously specified meaningful margin. |

Keep the allocator. Enforce the final certificate after its recovery attempt;
define the failure behavior before implementation. An uncertified vector must
not silently become the traded target. A failed solve may raise a clear error
or use a separately specified, certified feasible fallback; a zero-book fallback
is not feasible for a nonzero beta target.

Certify final post-processing too. Scaling a solution by a<1 changes a nonzero
target beta to a*target. If supporting such a binding-cap case, preserve the
affine hedge while satisfying the gross cap through an explicitly defined
feasible solve; do not claim the pre-scaling certificate covers it. Neither B0
nor B05 hit the gross cap in the actual reviewed sample, so this is not an
explanation for their negative realized-beta offset.

Use a prospective E2E failure/expected-outcome plan before these fixes and retain
red/green commands, source identities and outcomes. Reuse established workflows;
do not add unit tests after writing the fixes. Default V2 economic agreement,
corrected-path causality and final-target feasibility are the relevant gates.
The tiny original-scorer return-layout rounding difference is distinct from a
strategy lookahead failure. Century runtime remains a separate requirement.

## 2. Primary next diagnostic: next-day hedge error on frozen V2 positions

### Hypothesis

The causal annual-horizon beta shrinkage improves the hedge-error forecast for
the actual direction the strategy trades at the next-day horizon. The competing
possibility is that its equal-stock annual MSE improvement fails to transfer to
portfolio-weighted daily exposure, or improves it only partially while leaving
a directional calibration bias.

### Frozen objects and sample

Primary book: exact V2 targets from the reviewed package. Secondary books: exact
B0 and B05 targets, with their already-fixed configurations. These are controls,
not alternative primary samples from which to choose a favorable result.

Decisions after close t=252..3777 earn rows 253..3778. Use all 3,526 common earning
observations and the original discovery/validation/audit masks. Preserve one
continuous scorer path, all costs, drift and closing conventions. Diagnostic
returns are gross when evaluating position exposure; report net counterparts
separately. Do not change any position, forecast, target, half-life or eta rule.

At each decision obtain raw b_t from the last 252 published returns through t.
Compute the existing causal eta_t using only pairs whose forward 252-day beta
windows have fully matured by that information set: after close t the prefix
length is t+1, so pair maturity is s+252 <= t+1 and the existing tracker is
evaluated at that length. This applies
even for the V2 book whose
trading configuration does not use the correction. Let

`b_corrected=(1-eta_t)*b_raw+eta_t*mean(b_raw)`.

The two portfolio beta predictions on the same weights are
`p_raw=w_t'b_raw` and `p_corrected=w_t'b_corrected`.

### Shared mean convention and primary score

Use the arithmetic stock-return mean over the same last 252 available rows:
`rbar_t=mean(R[max(0,t-251):t+1], axis=0)`, and `mbar_t=mean(rbar_t)`.
Both beta forecasts use this identical past-only mean convention. No alternative
mean estimator will be chosen after inspecting scores.

For next-day portfolio return `g=w_t'R[t+1]` and market `m=mean(R[t+1])`, define

`H_j,t = (g - w_t'rbar_t - p_j,t*(m-mbar_t))**2`.

Primary statistic: mean `H_corrected-H_raw` on the V2 book. Negative is the
prespecified sign supporting usefulness at the traded horizon. Report its
21/63/126-day paired moving-block 95% ranges, 2,000 draws, seed 20261027, using all
legal starts. Report every stage and both secondary books whatever the sign.
These are exploratory fixed-book diagnostics on exposed history, not new
validation. The noisy common mean estimate and serial dependence remain limits.

This loss evaluates next-return hedge error under a stated common-mean model;
it does not pretend to observe a latent instantaneous true beta. An improved
score does not by itself establish unbiased exposure or higher net Sharpe.
Conditional-mean/timing effects can also contribute to a static regression-beta
offset; do not identify the offset exclusively with latent beta estimation error.

### Complementary calibration outputs

Save the date, gross return, market return, both beta predictions, eta, net and
gross investment and both means. Report constant-plus-market regressions of
`g-p_j*m`, with HAC10 intervals and fixed 21/63/126 sensitivity; show gross/net
versions separately. Report the B05-minus-B0 response and the shared level error.
Show the relation to the existing annual equal-stock MSE without treating the
overlapping dates as independent Bernoulli trials.

Require future-mutation and prefix invariance of all available-at-decision
diagnostic inputs and beta predictions. Future scoring outcomes naturally change
when future returns are changed; the protected predictions must not.

## 3. Secondary shadow diagnostic: raw-return risk for an explicit-beta book

The current risk state models residual returns. For target p=b'w, actual raw
second moment also contains the market square term and a market/residual cross
term. The latter is weight-dependent even when p is fixed.

Use B05 as the primary explicit-exposure book for this diagnostic. B0 and V2 are
invariance controls with their own matching corrected/raw hedge definitions.
Keep all original holdings frozen. This is not an allocator modification.

### Joint factor-market construction

On each matured return row s, use exactly the policy's causal residualization,
published loading basis and existing factor fit to obtain f_s and residual u_s.
Augment the factor-return vector with that day's observed market return:
`x_s=(m_s,f_s)`. Accumulate its normalized outer-product moment matrix Omega
with the existing factor half-life 126. Absorb exactly the existing risk state's
rows s=1..t, with the identical initialization, decay and normalization; require
Omega's factor block to reproduce the existing physical-scale F numerically.
This is a **second-moment** state, consistent with the current accumulation of
factor outer products.

At decision t, let D_t be the policy's published 26-column risk basis and b_t
its current matching raw/corrected beta. Define

`Sigma_raw = diag(d_t) + [b_t,D_t] @ Omega_t @ [b_t,D_t].T`.

Use physical factor scale 1 for this risk diagnostic. Specific risk, its
shrinkage/floor and all time conventions stay inherited. The residual-only
comparator is `diag(d_t)+D_t F_t D_t'`, where F is the corresponding block of
the same Omega. Joint outer-product estimation preserves positive semidefiniteness;
do not combine unrelated estimates and hide a negative risk prediction by a floor.

For z=D_t'w_t and p=b_t'w_t, record the forecast difference explicitly as

`market_square = p*p*Omega[0,0]`

`factor_market_cross = 2*p*(Omega[0,1:] @ z)`.

V2 under its matching raw-beta hedge and B0 under its matching corrected hedge
should show effectively zero change. B05 need not. Adding only the raw-beta market
direction to raw-beta-neutral V2 cannot repair its hidden-beta issue; that is
why it is an invariance control.

The proposed low-rank model does not automatically represent residual-market
covariance outside the factor span. Track the same weighted moment of u_s*m_s
and report its current-book projection `2*p*w_t'E_t[u*m]`, signed and absolute,
relative to predicted risk by stage. Do not silently assume this remainder is
zero or add it to a diagonal residual model without checking joint coherence.
The construction also inherits the original omission of factor/idiosyncratic
cross moments E[f*u']; tracking u*m addresses the additional market remainder,
not every possible misspecification of the raw-risk model.
If it is material, a full-risk-model claim remains unresolved and a subsequent
model needs its own specification.

### Risk score and disposition

Compare `log(q)+g**2/q` on the same 3,526 earning rows, with q floored at 1e-16 for
nonzero books and loss 0 for exactly zero books, as in the prior R27 rule.
Primary shadow-risk statistic is mean loss(raw reconstruction)-loss(residual only)
on B05. Report 21/63/126-day paired block ranges and all stages. Other books and
aggregate calibration ratios are controls/secondary diagnostics.

A lower score supports the specified added market/factor risk terms; it does
not establish a profitable policy or a fully correct covariance. A materially
missing u-market term must be reported even if the low-rank score improves.
No new strategy is run as part of this diagnostic stage.

## 4. What happens after these measurements

- If the annual correction helps next-day portfolio loss but leaves a level
  error, distinguish useful risk reduction from calibrated exposure. A new
  estimator must learn on prior matured portfolio outcomes, with a separately
  frozen rule; do not fit an offset to the full-sample -.014.
- If it fails the primary daily score, do not call the hedge solved because it
  wins on annual stock MSE. Revisit the estimation horizon/objective.
- If market/factor cross terms improve raw-risk forecasting and matter for
  allocation, the next single policy intervention can isolate that risk change
  with mean forecasts frozen. Specify it before executing it.
- If the quantities are small or do not predict risk, close this beta-control
  branch of research for now and return to mean-forecast or covariance research.
  Repeated target grids around a .012 Sharpe gap would add selection noise.

The objective remains future net Sharpe subject to the assignment's constraints.
Beta zero is not intrinsically required, and explicit exposure is not intrinsically
an alpha improvement. Keep V2 until a justified, recorded replacement decision
is supported. Preserve the user's own authorship in the final note; the derivations,
diagnostics and instructions here are AI-generated research assistance.
