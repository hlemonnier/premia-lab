# V3 market interpretation review: fixed-policy sensitivity only

29 October 2026, Europe/Paris. Reviewer: v3_market_challenge.

## Scope before calculations

Inspect the immutable supplied README, Claude's deployed V3 comparison script,
its committed results, and the published actual ledgers for the already selected
E2 and E2+M1 policies. Pin Claude head
`978824d4b6140c43566ebd61a3ee8157f4080e35` and research evidence head
`9e56aa755d20c5876485188f4c50ce959f6d63f3`.

No policy is executed or modified. No sleeve weight, parameter, feature subset,
date window or other new economic candidate is selected. This is an observational
interpretation and arithmetic readback of existing results. All supplied periods
are exposed development history under the user's continued score-first mandate.

## Questions and fixed calculations

1. What exact operation produced Claude's claim that a zero market premium gives
   sleeve Sharpe 1.286 versus no-sleeve Sharpe 1.340? Distinguish a change only
   to the sleeve's mean contribution from a common market-mean change affecting
   both strategies' observed beta exposures.
2. Reproduce existing full-score moments using the fixed earning rows
   253..3778 and ddof=0. Verify the committed daily ledger hashes against the
   published identities and record source/input SHA256 values.
3. For existing net return series p_j and equal-weight market m, compute their
   full-sample descriptive OLS betas. Let mu_j, sigma_j and mu_m denote annual
   arithmetic means and annual volatility. A **frozen-return sensitivity** to
   assumed annual market mean nu is

       S_j(nu) = [mu_j + beta_j*(nu - mu_m)] / sigma_j.

   This holds each book's beta, centered-return fluctuations, nonmarket mean,
   positions and costs fixed. Evaluate only nu=mu_m, nu=0 and nu=-mu_m.
   Report both books under each common scenario. This is neither a rerun of
   the strategy in altered market data nor an estimate of future performance.
   Also report the one-factor OLS explained-variance fraction and beta times
   market mean, solely to describe whether the current return stream is mostly
   the market factor. These descriptive projections do not identify economic
   stock-selection alpha or prove what a counterfactual hedge would earn.
4. Solve the algebraic equality of those two linear-in-nu Sharpe expressions,
   if the slope difference is nonzero. Label its market-mean breakeven as
   conditional on the frozen quantities, not an optimal sleeve calibration.
5. Separately reproduce Claude's sleeve-only mean subtraction, p_joint minus
   0.05*mean(m), and compare it with the unchanged E2 series only under that
   precisely stated conditional assumption. Do not call that a common-market
   zero-premium counterfactual.
6. Assess the brief from its complete wording: future net Sharpe is the stated
   objective, numerical market-beta limit is below 0.2, and the surrounding prose
   asks for market hedging and says a mostly market-long strategy is unwanted.
   Keep explicit requirements, interpretation and uncertainty about unseen
   future beta separate. No inference that a positive historical market premium
   must persist, or that every beta below 0.2 is an unconditional permission to
   maximize market allocation.

## Evidence and reporting

The output will preserve exact consumed-file hashes, formulas, observed moments,
the three fixed mean scenarios, the algebraic crossing and relevant source line
references. Required corrections are limited to inaccurate interpretation or
unsupported claims; any request for a changed deployment policy must be justified
separately. No universal no-overfit or no-lookahead guarantee is inferred from
these arithmetic calculations. Any missing data or failed readback is reported.
