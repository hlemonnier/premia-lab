# Portfolio allocator handoff

## Implementation and API

`submission/portfolio.py` defines:

```python
allocate(expected_returns, held_positions, variances, betas, trading_costs,
         risk_aversion, cost_horizon, weight_cap)
```

It returns a new float64 vector. Arrays must be finite one-dimensional vectors of the same nonzero length; variances and risk aversion must be positive, costs nonnegative, and horizon positive. A scalar or vector of nonnegative caps is accepted. Invalid inputs raise `ValueError`; unresolved numerical convergence raises `RuntimeError`. The caller supplies a positive variance floor. The function is pure, deterministic and depends only on numpy.

The constrained optimum is obtained from independent bounded scalar minima at each value of a beta multiplier, then a bracketed one-dimensional bisection. Signed and zero betas, zero caps, held weights outside the box, and no-trade plateaus are handled explicitly. The objective and proof obligations are in `PORTFOLIO_PLAN.md`.

The implementation uses `trading_costs / cost_horizon` only inside the portfolio objective. Actual trading costs remain those of the supplied scorer. There is no gross cap in this optimizer. Subsequent uniform scaling preserves beta neutrality but generally changes optimality under the declared objective; that additional control belongs in strategy documentation.

## Verification executed

`evidence/portfolio_verify_001/summary.json` reports **`PASS_SCOPE_ONLY`, exit code 0, 54 checks passed**:

- 34 valid-input cases: hand calculations, an independent quadratic KKT linear-system solution, twelve independent SciPy primal epigraph solves, and a 1,000-asset problem with a constructed known KKT optimum.
- Nineteen invalid-input cases requiring `ValueError`.
- One allocator-only runtime gate, with 32 calls on one CPU and numerical library thread counts set to one.

The largest normalized objective discrepancy against the independent primal reference was `2.0702126684759206e-13`, below the predeclared `2e-8` threshold. Maximum weight error on the 1,000-asset known optimum was `5.661703744719304e-16`, below `1e-9`. All checks of output shape/finiteness, position bounds, beta, deterministic repetitions and argument immutability passed.

Measured 1,000-asset allocation times: mean **5.417 ms**, p95 **10.583 ms**, maximum **19.739 ms**. These are synthetic allocator timings on the recorded environment, not full-strategy or long-horizon runtime verification.

## Verification order and reproducibility

Chronological records and immutable snapshots are in `evidence/portfolio_build_order_001`:

1. Plan recorded at `2026-10-26T14:45:40.906410+00:00`, before the verifier and allocator existed.
2. Initial verifier recorded at `2026-10-26T14:47:48.678423+00:00`, while the allocator was absent.
3. A verifier-only evidence correction was recorded at `2026-10-26T14:49:18.786233+00:00`, still before implementation: make red-stage rerun use a deliberately absent module path and record the working directory. Numerical cases were unchanged.
4. Expected missing-module red run 002 finished at `2026-10-26T14:49:44.483301+00:00`. Numerical cases were explicitly **NOT RUN** in that stage.
5. Implementation was recorded at `2026-10-26T14:51:27.688826+00:00`; the final verifier remained unchanged. The first implementation verification then passed without altering tests or tolerances.

Final preimplementation verifier SHA-256:

`72e417e521c72ecc5f9d109180c5f2744d97787068403c160b111fea815de60b`

Verified allocator SHA-256:

`176e4a4f42124dd76a0f4fa26db2c0427b1a4ea46c9805aa820155283aff918c`

Each evidence directory retains its own runner, frozen expectations, concrete synthetic fixtures, environment, hashes, exact command, rerun command, logs, summary and actual outputs where execution reached them. Use `evidence/portfolio_verify_001/rerun.txt` to rerun the exact frozen successful verifier against its exact frozen allocator. The original invocation, from the project root, was:

```bash
python tools/verify_portfolio.py --module submission/portfolio.py --plan verification/PORTFOLIO_PLAN.md --out evidence/portfolio_verify_001
```

The output path must be new for any future execution; existing evidence is not overwritten.

## Limits and next gate

No market data, validation data or reserved audit outcomes were read for this work. These results establish the specified numerical optimizer contract on its predeclared fixtures. They do not establish profitable alpha, complete-strategy causality, scorer accounting, future beta compliance, portfolio solvency, complete-strategy timing, or a century-scale runtime bound. Those remain full-workflow gates.

## Independent review and correction

`reviews/portfolio_independent_review.md` approved the optimization mathematics and verification chronology but requested one numerical correction: overflow inside a scalar solve could be clipped into a feasible yet nonoptimal portfolio. The initial run-001 pass remains limited to its recorded fixtures and does not erase that source-review finding.

The implementation now raises `ValueError` when intermediate scalar allocation arithmetic overflows, becomes invalid, or divides by zero. This conservative rejection follows the predeclared representability contract; it does not claim stable optimization for every extreme finite input. See `reviews/portfolio_fix_review.md` for the reason and source assessment.

The **unchanged preimplementation verifier** was then executed in `evidence/portfolio_verify_002/`: **54/54 checks passed**, exit code 0, status `PASS_SCOPE_ONLY`. No fixture or tolerance was added or altered after implementation. The verifier hash still equals the final preimplementation snapshot. The live allocator equals the frozen run-002 allocator byte for byte.

Corrected allocator SHA-256: `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475`.

Run-002 synthetic 1,000-asset allocator timing over 32 calls on one CPU: mean **7.851 ms**, p95 **20.164 ms**, maximum **21.698 ms**. Numerical errors against the existing references are unchanged. These timings are still component-only; complete-strategy and long-horizon performance remain unverified by this artifact.

The overflow counterexample was assessed by source reasoning; it was not added as a postimplementation unit test or represented as an executed check. The original expected-red evidence remains preserved, and `evidence/portfolio_red_001/RERUN_NOTE.md` explains how to reconstruct that historical missing-module stage without pretending its old live path is still absent.
