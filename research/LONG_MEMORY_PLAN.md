# C09: one longer-memory alpha contrast, before execution

**State:** prospective specification and configuration only. The lead reserved C09 after inspecting the recorded C01–C06 outcomes, and will update the experiment ledger before the economic execution. No new model code or feature scan is needed. Existing sources remain unchanged. The lead's execution acknowledgment is still required.

## Question and evidence motivating the change

The first discovery diagnostics showed changing univariate characteristic-return associations. Those changes can reflect varying true expected returns, correlated return noise, sampling variation, or several of these together. They were not proof of genuine rapid regimes.

The admitted faster-memory candidate C03 underperformed C02 before costs as well as after them. The specified covariance-weighted learner C05 did not improve C02's gross or net Sharpe either. C06's combination of that learner with the factor portfolio improved the observed score modestly, but did not establish the mechanism behind estimation error. These already-viewed development results motivate one simpler discriminating question: **would a slower learner reduce harmful estimation noise enough to outweigh adaptation lag?**

## Exact complete configuration

C09 copies C02's additive candidate and changes one numerical setting:

- `alpha_half_life`: **1008 days**, four times C02's 252-day half-life.
- Candidate identifier: `C09_additive_long_memory`.

The value 1008 is selected as one predetermined four-year contrast, not a scan or a claim of optimality. All other JSON controls remain equal to C02: ridge 0.1, 126 matured-pair warm-up, all thirteen linear and thirteen centered-square terms, feature clipping, risk window/fallback/shrinkage/floor, diagonal allocator, cost horizon, risk aversion, stock bound and proportional gross policy. Use the existing unchanged `submission/strategy.py`; there is no expanding-mode patch, refit-schedule change or new estimator implementation.

The learner remains causal and has fixed-size sufficient statistics. A 1008-day half-life does **not** require reading 1008 future startup observations: at forecast row t it still normalizes the moments accumulated only from completed pairs, emits zero before row127 and uses no observation at or after t. The original startup and risk schedules are unchanged.

## Failure modes and verification

The existing original-scorer E2E runner is the appropriate verification. No new isolated or postimplementation unit test is introduced. Before running, compare the JSON against C02 and record that only the identifier and half-life differ. Freeze the source/configuration snapshots in a fresh evidence directory.

The actual run must reconcile the same `[0,2016)` input scope, score indices253–2014, 1,763 targets, full actual trading costs, shapes/finiteness, actual beta and stock/gross bounds. Record complete daily output, fixed discovery blocks, gross/net performance, turnover, gross-rescaling frequency and runtime. Undefined statistics or numerical exceptions remain failures/unverified outcomes; no tolerance or window change is allowed to obtain a favorable comparison.

Causality is governed by the existing plan. A configuration-specific causality run remains necessary before C09 can be promoted to a finalist. Prior C02 causality evidence does not constitute an executed C09 pass merely because the implementation is the same.

## Interpretation and stopping

Compare C09 with C02 under the same complete portfolio. A better development score is compatible with reduced estimation variance, but does not prove true coefficients are stable or establish hidden-future performance. Poor results weaken this particular slower-learning hypothesis. Any improvement in turnover, sizing or concentration must be reported because it can also explain a net difference.

This proposal authorizes no intermediate half-life grid and no automatic combination with another winner. A later combination needs its own prospective ledger entry, clear controlled question and remaining configuration budget. The validation/audit periods remain closed until their original gates.

The hypothesis and configuration are AI research decisions made in response to recorded evidence. They are not retrospectively attributed to the applicant, and the result is unknown at this specification checkpoint.
