# Portfolio allocator correction and integration handoff

## Decision and scope

The requested overflow correction is implemented and the unchanged preimplementation numerical verifier has passed again. The allocator is ready for complete-strategy integration within its declared numerical contract. Root should read back the small correction before treating this fix as independently approved: this follow-up agent both implemented and assessed the correction, while the earlier independent report identified the defect.

No market observations were read. No new isolated tests, fixtures, or tolerances were written. No Git operations were performed. Complete-strategy causality, scorer behavior, realized market beta and economic performance remain separate E2E obligations.

## Correction

The previous scalar solve used `np.errstate(over="ignore", ...)`; it could produce infinity before a transaction-cost subtraction, then clip infinity into a finite feasible but wrong solution. The independent report derived a finite-input example whose optimum is `[1,1]` but whose overflowed solve could return `[1.5,1.5]`.

The updated `at_multiplier` encloses the shifted alpha, held-gradient comparison, cost-adjusted divisions and clipping in `np.errstate(over="raise", invalid="raise", divide="raise")`. A resulting `FloatingPointError` becomes an explicit `ValueError` describing unrepresentable allocation arithmetic. An overflow can therefore no longer reach clipping and be silently accepted as the optimum. Existing explicit checks continue to cover scaled risk, scaled costs, risk gradients and attainable normalized exposure.

This is a conservative input rejection strategy, not arbitrary-precision optimization. It may reject extreme inputs even when algebraic rearrangement could produce a representable answer. That behavior fits the predeclared contract and keeps ordinary-scale mathematical behavior unchanged.

The extreme counterexample has not been executed as a new isolated test. The correction is justified by source reasoning and the existing verifier supplies regression evidence over its predeclared fixtures.

## Executed verification

From the project root:

```bash
python tools/verify_portfolio.py --module submission/portfolio.py --plan verification/PORTFOLIO_PLAN.md --out evidence/portfolio_verify_002
```

Actual outcome: exit 0, `PASS_SCOPE_ONLY`, **54 checks passed and zero failed**. The directory preserves setup, exact frozen code, inputs, expected outcomes, actual outputs, source identities, command, logs and timings. Its `rerun.txt` recreates the run using frozen files in a fresh output directory.

| Identity | SHA-256 |
|---|---|
| Corrected allocator and run-002 frozen allocator | `fed482fde5aafb17fe423fcf9bbeefc66bc8f8323b85e72531def52ebae87475` |
| Unchanged verifier and final preimplementation snapshot | `72e417e521c72ecc5f9d109180c5f2744d97787068403c160b111fea815de60b` |
| Unchanged verification plan | `c507dd7f10fd93c06eb5a3321c6bf921ba74f409a9ec27b71c17137732711d3e` |

The 32 synthetic 1,000-asset allocation calls averaged 7.851 ms on the recorded single CPU; p95 was 20.164 ms and maximum was 21.698 ms. This does not establish the complete rebalance or century-length forecast requirement. Existing numerical-reference errors remain unchanged from run 001.

## API and integration boundary

```python
allocate(expected_returns, held_positions, variances, betas, trading_costs,
         risk_aversion, cost_horizon, weight_cap) -> numpy.ndarray
```

The output minimizes the declared diagonal quadratic risk and absolute trading-cost objective under a box and exact estimated-beta equality. `held_positions` must be the scorer's drifted holdings. Supply positive floored variances. Full actual trading costs remain in the official scorer; amortizing them inside the allocation objective is only a control approximation. A downstream gross rescale preserves the estimated-beta equality but generally changes optimality for the exact objective.

The module is pure NumPy, deterministic, and state-free. It neither estimates beta nor reads files. Input arrays are unchanged in all existing fixtures. Arbitrary extreme arithmetic rejection, process interruption handling, complete-strategy execution and unseen market compliance are not blanket guarantees supplied by this handoff.
