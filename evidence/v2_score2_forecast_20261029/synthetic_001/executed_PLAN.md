# F3: characteristic premia conditional on a causal market-risk state

29 October 2026, Europe/Paris. Prospective specification: no F3 implementation,
new actual-market forecast or new actual-market score exists at this checkpoint.
Root owns admission and execution. This file proposes exactly one forecast policy.

## Objective and existing evidence

Improve original-scorer net Sharpe against the research leader F2 + VTvol,
1.318334966090838. All supplied historical periods are exposed development data.
Their old discovery/validation/audit labels do not provide fresh confirmation.
No forecast-MSE, pure-alpha or statistical-significance threshold replaces the
net-score objective. Causality, solvency, beta and runtime requirements remain.

Existing C11 interaction and C12 local-hinge experiments lost against their
declared older parents. They do not falsify every shape extension under V2,
but weaken the case for another immediate polynomial/spline expansion. F2 has
already improved the score by changing linear-coefficient memory. F3 instead
asks whether observable market conditions predict the relative payoffs of
the existing characteristic directions.

The ordinary VTvol controller changes the size of a whole virtual book. F3
allows each characteristic premium to respond differently to one market-risk
state. At any one date its new characteristic predictions remain in the
existing 26-column characteristic span, already represented by V2's risk model.
The existing beta column remains; F3 does not add a beta-by-state interaction.

## Exact observable market state

Let m_s = mean_i R[s,i], using the same equal-weight market series as the base
model. At close s, after return row s is published, update, separately for
h in {63,1008}:

    S_h <- 2^(-1/h) S_h + m_s^2
    M_h <- 2^(-1/h) M_h + 1
    q_h,s = S_h / M_h

Both sums and masses start at zero at the start of each forecast invocation.
The first observation is return row 0; count=s+1 for the ordinary full input.
Before 63 observed market returns, c_s=0. Otherwise set

    c_s = clip(log(max(q_1008,s,1e-12) / max(q_63,s,1e-12))
               / (2 * log(2)), -1, 1).

These are normalized gross-return second moments, not demeaned variances.
No full-sample moments or fitted centering/scaling are used. State +1 corresponds
to recent volatility at most half the long reference, and -1 to at least twice
the long reference, subject to the numerical floor. Equal moments give zero.
All-zero market returns therefore yield zero state exactly after flooring.

Market risk is chosen because it is an independently observable systematic
condition and because the cited multifactor literature conditions relative
factor weights on market volatility. Using virtual-book risk would introduce
strategy-dependent state and a more complicated counterfactual. This is a
local design choice, not a claim that market risk predicts this simulator.

## Exact 53-column design and estimation

For published characteristic panel X[s], retain the unchanged 27-column design
D_s: 13 standardized linear characteristics, 13 centered squares, then raw
trailing beta standardized across stocks. The beta is beta[s+1], calculated
from returns through s. Append

    H_s = c_s * D_s[:, :26]
    A_s = [D_s, H_s].

Column order is the existing 27 followed by 13 conditional linear and 13
conditional square columns. No characteristic selection or additional shape
expansion is allowed. The original columns remain byte-identical to F2's design.

Fit two complete pooled EW ridge systems on all 53 columns, with half-lives
1008 and 252. Use diagonal penalties 0.1 on the original 27 coordinates and
1.0 on the 26 state interactions. The moments and masses have the same updates
as F2, and the original 126 matured-pair warm-up is retained.

The bounded state has magnitude no greater than one, so each interaction's
absolute loading is no greater than its parent feature's. On this explicit
scale its ridge is ten times larger; with small state variation its effective
shrinkage is stronger still. This is deliberately conservative and is not a
penalty optimized from these new scores. It does not imply orthogonality,
unit variance or a universal tenfold ratio of coefficient shrinkage.

After solving both complete systems, use

    coef = coef_slow.copy()
    coef[:13] = 0.5 * coef_slow[:13] + 0.5 * coef_fast[:13]
    prediction[t] = A_(t-1) @ coef.

The 13 squares, beta and all 26 interactions retain their slow coefficients.
The original coefficients are jointly refitted; beta is not numerically held
at its previous estimate. It simply retains slow memory and no direct state
interaction. Arbitrary row-specific forgetting in one Gram matrix is forbidden.

## Information clock

For forecast row t, the newest matured training pair is

    [X[t-2], beta[t-1], c_(t-2)] -> residual return R[t-1].

The state c_(t-2) uses market returns only through t-2, never its label return
t-1. The current forecast uses X[t-1], beta[t] and c_(t-1), which may use return
row t-1 because it is already published. The first potentially active forecast
remains row 127. All fitted moments and controller/risk state reset each session.

Future perturbations beginning at return row k must preserve forecast rows
through k. Their protection for rebalances must stop before close k because
the close-k rebalance legitimately observes R[k]. Prefix checks use identical
canonical input layout to distinguish temporal leakage from accumulation order.

## Complete policy and comparison

The sole actual-market alternative is F3 with the unchanged VTvol controller,
using F3 as its underlying virtual book. Keep the base factor risk model,
penalty scale 0.3, H126 factor/specific risk, gamma 200, cost horizon 20, virtual
stock cap 0.05, gross 5, raw betas and estimated-beta target 0 unchanged. Actual
scorer costs and drift remain unchanged. Do not use old F2 virtual returns to
size F3. No unscaled F3, alternate state, penalty, window or coefficient grid
is authorized by this file.

Primary comparator: a reproduced F2 + VTvol on identical earning rows 253..3778.
Differences <=1e-8 are numerical ties; higher net Sharpe may nominate the new
policy only after operational admission. Report all stage masks, gross/net
returns, fees, realized beta, constraints, runtime and the established paired
block intervals without adding a requirement that all subperiods improve.
Any joint composition with a new execution policy needs root's separately
predeclared combination rule before either constituent's results.

## Prospective E2E verification and source ordering

Write and preserve the complete-workflow harness before implementing F3.
An independent reviewer checks the harness and then the implementation before
actual-market scoring. Reuse the unchanged original scorer and record exact
commands, data/source hashes, outputs and failures. Synthetic workflows check:

1. A deliberately strong known conditional-characteristic signal, generated
   from a known lagged market state. The fixture must bind the state date to
   the design date and publish exact outcomes/tolerances before implementation.
2. A zero-state nonzero-signal control: the enlarged ridge system reduces
   mathematically to F2. Verify forecasts, actual positions, drift and fees
   against F2 with declared numerical tolerances, not a forced exact claim
   after differently sized LAPACK solves.
3. Future alteration, prefix and fresh-session repetition of the complete
   F3 + VTvol strategy. Verify protected forecasts, positions and economics.
4. Exactly zero returns/cash economics; undefined Sharpe/beta must remain
   undefined rather than be manufactured as a passing numeric score.
5. Independent market-state reconstruction including first 63 observations,
   the warm-up boundary, floors, bounds and protection against using each
   training pair's own label in its state. This is observed inside complete
   workflows, not a postimplementation isolated-test suite.
6. Actual scorer accounting, free opening, charged final rebalance, virtual
   book independence, finite/solvent paths and constraint/certificate records.

The expanded two-system work is O(T*N*53^2 + T*53^3), with fixed-dimensional
learned state; this is a complexity statement, not a runtime pass. Measure
forecast and rebalance costs. Source/data selection and array checkpoint
publication must preserve the earlier archive-failure lessons: atomic files,
readback and identities, with no silent evidence repair.

## Falsifiers and interpretation

The market state might change variance without changing conditional means.
In that case the existing covariance allocator and VTvol may already capture
the useful effect, while F3 adds estimation noise. State/feature collinearity
can shift the original coefficients despite ridge. A stable state can leave
the new columns weakly identified. F3 may increase implicit market exposure
or turnover; actual net score and beta determine its disposition. None of
these mechanisms is assumed beneficial merely because an external paper found
conditional effects in US factor data.

## Primary literature inspected

- DeMiguel, Martin-Utrera and Uppal (2024), *A Multifactor Perspective on
  Volatility-Managed Portfolios*: https://doi.org/10.1111/jofi.13395 . Publisher
  full HTML inspected. Their distinction between factor-specific conditional
  weights and a common multiplier motivates F3; their factor set, fitted
  portfolios, state scale and empirical gains are not imported here. SSRN
  primary record: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3982504 .
- Freyberger, Neuhierl and Weber, *Dissecting Characteristics Nonparametrically*:
  https://www.nber.org/papers/w23227 . Primary abstract inspected. It motivates
  flexible characteristic responses with shrinkage, but it does not rescue
  the local C12 negative. No new spline policy is nominated.
- Gu, Kelly and Xiu, *Empirical Asset Pricing via Machine Learning*:
  https://www.nber.org/papers/w25398 . Primary record and publisher discussion
  inspected. Their additive spline method's limited improvement is relevant
  counterevidence against assuming more univariate terms must add value.
- Feng and He, *Factor Investing: A Bayesian Hierarchical Approach*:
  https://arxiv.org/abs/1902.01015 . Primary record revisited as context for
  heterogeneous conditional coefficients and estimation risk; F3 does not
  implement its Bayesian model or claim its empirical results.

No new market outcome analysis was used to choose this proposal. The design
is AI research assistance; no applicant contribution or result is invented.
