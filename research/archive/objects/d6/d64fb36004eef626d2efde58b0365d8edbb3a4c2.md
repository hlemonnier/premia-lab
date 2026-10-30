# C03: faster adaptation, specified before its first score

Hypothesis: the changing conditional relationships in the existing discovery diagnostics make the 252-day forgetting half-life slow to react. Compare one fixed 63-day half-life with C02's 252-day value; do not search a grid or adjust other settings.

Implementation is the existing additive model; only `candidate_id` and `alpha_half_life` change in the explicit configuration. The input boundary, basis, normalized ridge0.1, minimum126 matured pairs, historical residual-label beta, all risk/cost controls, and holdings remain identical.

Run the original scorer over the discovery cache [0,2016), scoring [253,2015). Use the same full fees and continuous empty-book initialization. Save the exact configuration/source identities, targets, daily and block outcomes, timings and rerun command. Compare pooled net Sharpe, all fixed block results, actual cost, realized beta and scaling frequency. There is no predeclared profitability floor and no guaranteed expected winner. A result-driven follow-up needs another pipeline slot. A causality smoke for a changed half-life cannot automatically be claimed from C02's pass; finalist verification must use its exact configuration.
