# Numerical-only amendment, before all Wave6 market scores

Unchanged B0 also fails the original 1e-10 stock-permutation weight test: maximum errors 1.47e-10 and 2.04e-10 under two fixed permutations. The original candidate constructed-data run has 76/80 passes; four permutation-position failures have errors 1.75e-10 to 6.20e-10. These are preserved, not relabeled passed.

The allocator certifies an objective/duality gap, not 1e-10 component-wise weight equality under changes to floating-point accumulation order. No model, solver, hyperparameter or statistical criterion changes. Only the stock-permutation TARGET tolerance becomes1e-8 absolute weight. The separate exposure comparison uses N*1e-8, the natural sum-of-weights bound. Actual return, fee and market-return columns retain1e-10. This clarifies that gross exposure is not a cashflow; it must not be bundled under the tighter cashflow tolerance specified in the review plan. All forecast-prefix, mutated-future, reset and forecast-permutation checks remain at1e-10.

This is a numerical testing amendment informed by constructed inputs and the unchanged baseline, not by a new candidate's market score. The failed original contract remains part of the report. Repeat the full constructed-data E2E workflow before any new candidate market replay. Same-session checks are not an independent audit.
