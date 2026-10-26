# Risk diagnostics 001 — preregistered descriptive study

Scope: discovery cache only, actual rows [0,2016). No strategy, forecasts, selected positions, costs-adjusted portfolio results or later-period access. This is diagnostic exposure, not one of the12 scored candidate configurations.

Questions: how heterogeneous/stable are stock market betas; how much covariance survives removal of the equal-weight market; does a low-dimensional residual risk structure exist; how heterogeneous are known costs relative to stock volatility? No answer is assumed.

Fixed calculations: OLS market betas with intercept using all discovery data descriptively and each of four504-day blocks; stock/market/residual volatility; cross-block beta changes; cost quantiles and Pearson/Spearman correlation with total/idiosyncratic volatility and absolute beta. Residual covariance/correlation spectrum on the pooled discovery data, with variance shares at k=1,3,5,10,20,50,100. Report average off-diagonal correlation and absolute correlation. This is an in-sample descriptive risk decomposition, not a deployable historical risk model or evidence of alpha. Any actual strategy must estimate risk using information available at each decision.

Expected workflow: cache shape and declared scope must match2016days; reject a longer cache; all values finite; cost nonnegative; market variance positive. Numerical checks on the completed decomposition: covariance symmetry, finite/nonnegative eigenvalues up to numerical tolerance, residual time-series means and covariance with the market near floating-point zero. None of these checks asserts that useful structure must exist.

Evidence: frozen plan/runner, input/code/protocol hashes, exact command, environment, running/final status, output tables and report, recorded checks/errors. All exploratory quantities are listed above; no outcome-driven new scans are allowed inside this run. No isolated tests or post-implementation unit tests are needed for this complete descriptive workflow.
