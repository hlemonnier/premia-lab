# Architecture

## One active policy

`model_n0.N0Policy` is the public class. `strategy.py` delegates `forecast` and `rebalance` to one instance. There is no model selector, saved fitted model, research-cache dependency or required network access.

| Module | Responsibility |
|---|---|
| `policy.py` | Public N0 policy and bounded own-residual correction |
| `premia.py` | Covariance-weighted premium estimate and fixed forecast combination |
| `risk.py` | Causal factor-variance adjustment and risk-aware stock books |
| `execution.py` | Pooled forecast, virtual-book sizing, sequential allocation and sleeve |
| `engine.py` | Characteristic transforms, causal betas and recursive risk state |
| `residuals.py` | Causal residual histories and correction projection/cap |
| `allocator.py` | Constrained cost-aware allocator and numerical certificates |
| `config.py` | Frozen configuration |

## Information time

Forecast row **t** uses source rows **strictly before t**. The newest one-day training response is return `t-1`, paired with characteristics at `t-2`. The next prediction uses characteristics at `t-1`. Covariance weights used to train a response precede that response. Cross-sectional normalization does not borrow future dates.

N0 begins fitting its additional stock-specific effects at forecast row 505. Each fit uses 504 matured labels and is refreshed every 126 rows. A correction is shrunk, projected away from the existing intercept/characteristic/beta design and limited relative to the baseline forecast. These are frozen research choices, not universally optimal constants.

## From forecasts to trades

The slow forecast is a fixed equal combination of two estimates of the same premia. The risk model estimates shared factor risk and specific risk, with bounded factor-variance adjustments. N0 adds a small residual forecast; it does not replace the common-premium model.

The allocator penalizes absolute changes from drifted stock holdings. It solves for a cost-aware portfolio with stock limits and an estimated-beta constraint. A reference stock portfolio controls sizing. The final market sleeve is added after the stock allocation; actual costs are charged on the combined trades. The internally tracked stock book is not identical to the total portfolio.

The market sleeve is an intentional exposure, not an alpha discovery. No historical beta check guarantees a future beta below a fixed level.

## Why inherited components remain inside N0

N0 was developed on top of factor-risk and GLS-estimation work. The required calculations now live inside one package. Historical labels such as F or GLS in research reports describe the experimental path, not additional active models in the current project.

This repository reorganization does not change the numerical modules. Their SHA-256 identities are recorded in `runtime_manifest.json` and checked in CI.
