# Frozen C09 return attribution — prospective descriptive protocol

27 October 2026, Europe/Paris. Written after the completed C09 audit, before
implementing or inspecting this attribution. This is a descriptive extension of
the evidence package, with no selectable candidate, forecast, position, cost,
configuration, or submission change. All supplied periods are already exposed.

## Question and admission

The user's notes distinguish risk exposures from predictive characteristics.
Kelly–Pruitt–Su's *Characteristics Are Covariances* supplies a related primary
research motivation: characteristics can describe changing common-factor
exposures as well as expected returns. The current C09 policy hedges the estimated
equal-weight market but uses diagonal residual risk. Its positive net result does
not establish that the remaining earnings are stock-specific.

Measure the realized P&L of the **existing, frozen C09 positions** in three
components: estimated market exposure, a prespecified residual-factor span, and
the remainder. The residual-factor span uses the already investigated C04
estimator: trailing 252 days, rank 10, factor shrinkage 0.5, refresh every 21 days, residual-correlation
factors rescaled by the current prior-estimated marginal variance. This is a
fixed explanatory lens, not an estimate of the simulator's true factor count.

No rank, window, refresh, subset, policy or output-driven alternative is admitted.
The analysis cannot promote a strategy, alter validation selection, or create
another clean internal confirmation sample. It is recorded as an additional
descriptive research exposure, outside the twelve selectable configurations.

## Inputs and identity

Use the canonical saved `evidence/audit_C09_001` packet. Before reading numeric
content, verify its input-return, target, daily-ledger, configuration and source
identities against its original manifests. The frozen C09 configuration remains
SHA256 `aac98ea250f067d79ef731737bfaec3f19112a4093d820bab0e6f170fbd420ba`.
The packet may be read from the original retained workspace; no historical file
may be rewritten or recovered speculatively. The current writable repository is
the destination for new artifacts only.

Read the original `returns.npy`, `targets.npy`, and `daily.csv`. Characteristics,
forecasts, raw CSVs and new strategy executions are unnecessary. Record hashes
for all consumed files and for the unchanged helper functions used to estimate
risk/factor loadings. Use a private copied helper package in the evidence folder
and a fresh process; no analysis state may affect the handoff.

The original scorer takes target zero after close 252. It earns return row 253.
Thus for scored return row `t`, the opening weights are
`targets[t - 253]`, not the drifted after-return holdings and not the target
chosen after observing return `t`. Reconcile `w_t @ R[t]` with every saved gross
return before interpreting any component.

## Fixed decomposition

At day `t`, estimate beta and residual variance using only `R[:t]`, with the C09
risk parameters. Follow C04's exact refresh epoch
`max(0, (t - 253) // 21)` for the correlation loadings. On a refresh, fit them only
on the trailing available history and current beta. Between refreshes retain
the correlation loadings, rescaling with the current causal marginal variances
as C04 does. Obtain an orthonormal basis `Q_t` for the resulting factor-loading
span using a thin SVD, retaining singular values strictly above
`float64_eps * max(number_of_stocks, number_of_loading_columns) * largest_singular_value`.
An all-zero loading matrix has an empty retained span. This threshold is fixed
before implementation or numeric attribution. Rank
deficiency and an empty factor span must be handled explicitly and reported.

Let `m_t = mean(R[t])` and `e_t = R[t] - beta_t * m_t`. Then compute:

- market component `w_t @ beta_t * m_t`;
- residual-factor component `w_t @ Q_t @ (Q_t.T @ e_t)`;
- remainder `w_t @ (e_t - Q_t @ (Q_t.T @ e_t))`;
- the original full cost, preserved as its own subtraction.

The components sum to the saved gross return, and gross less full cost equals
the saved net return. Realized factor scores use the day's realized returns for
after-the-fact attribution; they are not forecasts or available trading inputs.
Only the loadings and opening holdings must precede the day being explained.
The remainder may contain omitted common factors, nonlinear exposures and
estimation error. Neither that remainder nor the factor component is identified
as economic alpha or a risk premium by this algebra.

The estimated-market contribution is expected to be tiny largely by construction:
the same prior beta estimator defines C09's hedge. That component is not an
independent test of future market neutrality. The separately measured realized
net-return beta in the original economic record remains the relevant empirical
constraint check.

## Reports fixed before results

Write one complete daily table over the canonical 3,526 economic rows, plus
summaries for exactly the original discovery `[253,2015)`, pooled validation
`[2016,3023)`, and audit `[3024,3779)` masks. Boundary rows excluded by the frozen
stage masks remain in the daily reconciliation. Do not choose subperiods from
their results.

For each stage report sample count, annual arithmetic mean of each of the three
gross components, full costs, total gross and total net, and annual volatility
of each component. Also report `Cov(component, gross)/Var(gross)` for the three
gross components. These covariance contributions add to one but can be negative;
they are not independent risk shares or PCA explained-variance ratios.
Report mean/maximum absolute estimated market exposure, realized span ranks,
maximum input-history cutoff and factor-age information, plus maximum accounting
reconciliation errors. Undefined ratios remain null. Do not calculate component
Sharpe ratios, significance, or mean-contribution percentages that would suggest
independent tradable sub-strategies.

## Verification and release order

1. An independent agent writes the failure modes, fixtures, expected outcomes and
   executable **complete-workflow** verifier before implementation. Preserve an
   expected missing-implementation run.
2. Implement only the prescribed descriptive tool. Do not add tests afterward
   that merely mirror its implementation.
3. Run the prewritten workflow on synthetic known-component returns and fixed
   saved positions. Cover exact time indexing and accounting, zero/degenerate
   risk, suffix alteration and truncation, and malformed manifest rejection.
   Every run preserves command, fixture/code hashes, expectations, results and
   logs, including failure records.
4. An independent reviewer checks information timing, source reuse, rank handling,
   additive arithmetic, interpretation and prospective records before the actual
   canonical packet is processed.
5. Run the single declared descriptive attribution and independently reconcile
   saved results. Unexpected results remain visible. A failed identity or
   accounting gate blocks interpretation; it never licenses rewriting a manifest,
   changing a tolerance or altering the frozen policy.

Completed source/accounting checks are separate from empirical findings. No
calendar execution schedule is imposed. The selected four-file C09 handoff must
remain byte-identical throughout.
