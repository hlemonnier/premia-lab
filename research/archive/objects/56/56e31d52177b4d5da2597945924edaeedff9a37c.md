# Strict stock-permutation exception: investigation before its supplemental run

The synthetic release suite has 34/35 passing explicit assertions. Its strict
1e-10 economic-row stock-permutation comparison fails at 2.8919333594501495e-10.
Alpha differs by less than5e-18, risk channels by2.22e-16, weights by3.33e-10
(within the previously fixed1e-8 permutation-weight tolerance). Prefix, future
mutation, reset and memory-layout comparisons are exactly zero.

Do not change the original receipt, model, solver settings or test tolerances.
Recreate the identical synthetic data and permutation, identify errors separately
for return, fee, gross and market columns, and record maxima. Then repeat the
same two complete workflows with the already preserved verification-only dense
active-set KKT refinement, symmetrically applied to both orders. Require errors
below the ORIGINAL1e-10 tolerance and valid cap/trade-region/KKT checks. This
will distinguish finite solver stopping sensitivity from an estimator defect.
The refined solver must never generate a reported market or century score.

The remaining frozen full-data/century checks may proceed as an investigation,
not as a claim that the failed synthetic assertion passed. The default failure
remains a disclosed numerical exception even if the supplemental check passes.
