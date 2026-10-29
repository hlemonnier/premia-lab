# Supplemental fixed-book total dependence diagnostic

29 October 2026. Written before the additional ratio calculation below. Parent
requested this small observational extension to distinguish most of the latest
score increment from most of the entire portfolio's return dependence.

The initial PLAN.md already specified and the unchanged mean_sensitivity_001.json
already records descriptive one-factor market R-squared and beta times annual
market mean. Its output SHA256 is
`a40de33bfc14f8c84b5148617973af0332d34d2a62cae9649ec5a6740bb9c8bf`.

For each of the two already observed books only, divide beta times annual market
mean by the book's annual net mean. Report this ratio alongside the previously
computed R-squared, beta and full score. No policy, new parameter, hypothesis
threshold, confidence interval, alternative window or return series is created.

These are full-sample descriptive OLS projections. Neither the intercept nor
the remaining mean is identified stock-selection alpha. The ratio is not a
causal attribution, a result from trading a market-neutralized book, or a
forecast of future factor dependence. A large fraction of an incremental score
gain need not imply that most of the entire portfolio is the market factor.
