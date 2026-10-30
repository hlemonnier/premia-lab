# Research direction review before C11 admission

**Reviewer:** alpha-model agent. **Scope:** existing diagnostic and completed experiment artifacts only; no new numerical scan, fit, return-history analysis or implementation in this review.

## Recommendation

Admit one fixed full second-degree characteristic model as C11 to test additive separability. Keep the final slot unspent until an observed result justifies a specific follow-up. Do not continue a risk-rank or memory grid merely because the numerical machinery is available.

The current evidence is modest. The baseline's net Sharpe is about0.62, additive terms raise it only to0.64, GLS plus factor construction reaches about0.76, and raising both factor ranks to50 does not improve that score. These are development outcomes selected amid several experiments, not demonstrated durable alpha. The robust numerical infrastructure is useful, but it has not itself created a strong trading edge.

## What the results do and do not establish

C02's improvement over C01 is small relative to the first-wave paired-bootstrap ranges. Faster adaptation C03 worsened gross as well as net performance. C09's longer memory modestly improved pooled performance while worsening the final discovery block. Neither result turns the original changing univariate signs into proof of real coefficient regimes or stable coefficients. Covariance-weighted learning C05 did not improve C02 alone; its interaction with factor construction in C06 helped, but that is not identification of a contamination mechanism. C10 changes learner and portfolio rank together and therefore cannot separately attribute its small deterioration to either component.

The repeated risk and estimation variations leave an obvious restrictive assumption largely untested: the conditional mean is a sum of one-variable functions. All current characteristic learners have that additive structure, apart from shared estimation/risk treatment. A controlled interaction extension asks a meaningfully different question.

## Why interactions have a defensible rationale

The original diagnostics report curvature for some characteristics and moderate correlations between characteristics. Marginal curvature does not uniquely identify an additive squared term. For an illustrative pair of jointly Gaussian, standardized variables X and Z with correlation rho,

`E[X Z | X] = rho * X^2`.

Thus a joint product effect can appear as a quadratic curve when one variable is examined alone. This identity is a mathematical illustration, **not** a finding that these supplied characteristics are jointly Gaussian or that the simulator uses products. It explains why correlated predictors weaken the inference from one-dimensional decile curves to an additive response model.

A complete fixed interaction basis is preferable to selecting Snap/Crackle/Pop pairs after reading their favorable curves. It tests the class uniformly, keeps all original terms and avoids a catalogue of cherry-picked pair hypotheses.

## Proposed bounded comparison

Use C02 as the parent. Retain its26 existing columns exactly and append all78 strict upper-triangle products of its13 bounded centered linear columns. Center each product using only the published cross-section; use a fixed unit scale for these products so there is no new normalization search. Apply a diagonal ridge penalty0.1 to the original26 terms and1.0 to the78 interactions. Keep the same causal matured pairs, EW half-life252,126-day warm-up, risk estimates, diagonal allocation, costs and sizing.

This is104 coefficients, not78 independent discoveries. Correlated columns, persistent states and common return shocks create estimation risk even with millions of stock-day rows. Stronger interaction shrinkage is a fixed design choice that limits flexibility; it is not a learned optimum or a guarantee against selection bias.

The existing ridge linear algebra and complete E2E framework are sufficient. A new custom optimizer would add no value to this question. The expanded normal-equation cost needs actual timing, and the new source needs configuration-specific causality and independent review. No portfolio policy change should be bundled into the first contrast.

## Why not pivot to return history yet?

The reviewed artifacts contain no measured momentum, reversal or residual-return serial-dependence evidence. Slow characteristic persistence does not establish return autocorrelation. Choosing a particular return lag, horizon, sign or interaction now would introduce a less-grounded new family and additional choices. Return-history research could become justified by its own prospectively specified diagnostics, but it is not currently a better-supported use of this single slot.

## Interpretation boundary

A C11 development gain would justify considering the fuller conditional-mean specification for the protected validation comparison. It would not formally prove nonadditivity, identify the generator or establish future performance. A weak result would argue against spending the final slot on interaction tuning. The last slot need not be used at all. Continue to preserve the untouched-period gates and report that the current empirical edge remains uncertain.
