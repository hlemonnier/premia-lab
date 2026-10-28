# V2_R27_beta_risk — plan and frozen decision rule (written before execution)

Source specification: `research/v2/REVIEWER_NEXT_EXPERIMENTS_20261028.md`, section 3. Adopted unchanged.

**Hypothesis.** The beta-derived direction carries common residual risk that the
26-column characteristic risk model cannot represent. Supporting diagnostic
(`results/beta_diagnostics.json`, computed before this plan): the daily return of the
standardized-beta factor, jointly with the 26 columns, has market slope −0.048
(Newey–West t = −19.7) and an insignificant intercept; 93% of the beta column lies
outside the 26-column span. The 26 risk columns are cross-sectionally centered and
residual returns are demeaned, so a beta-hedged net-long book's exposure to
beta-estimation error is invisible to the R26 model.

**Change.** Forecast: exactly V2's 27-column forecast. Risk loadings: append the
same centered/clipped standardized beta column. On absorbed row s: `basis(X[s-1])`
plus beta from `R[:s]`; response `e = R[s] - beta_s*R[s].mean(); e -= e.mean()`
(unchanged). For the allocation after close t: `basis(X[t])` plus beta from `R[:t+1]`.
Everything else inherited from packaged V2 (half-lives 126, specific shrinkage 0.2,
floor 1e-6, phi 0.3, cost horizon 20, gamma 200, caps 5%, gross cap 5).

**Stage 1 — risk gate on frozen V2 holdings.** Decisions at closes t = 252..3777,
weights w_t = V2 targets, g_t = w_t · R[t+1] (earning rows 253..3778, 3,526 days).
q_t = w'(diag(d_t) + D_t F_t D_t')w at physical factor scale 1, floored at 1e-16
for nonzero books; zero book → loss 0 for both models. loss = log q + g²/q.
**Pass iff mean(loss_R27 − loss_R26) < 0.** Report 21/63/126-day paired block
bootstrap ranges, per-stage means and calibration ratios (secondary).

**Stage 2 — only if stage 1 passes.** One continuous full-fee run of the packaged
R27 candidate. **Retain R27 only if** stage 1 passed **and** full-run net Sharpe
exceeds packaged V2 (1.242503) **and** realized beta < 0.2 and runtime within budget.
Report all stages and paired uncertainty regardless. A failure rejects this version;
no rescue by tuning phi, gamma, hedge or forecast.
