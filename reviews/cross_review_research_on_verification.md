# Cross-review: research design on verification design

**Reviewed:** `reviews/verification_design.md`.  
**Status:** independent source/design review only; no tests executed and no candidate implemented.  
**Conclusion:** the verification memo correctly captures the main timing, accounting and causality boundaries. No fundamental correction is needed. The following refinements prevent false failures, holdout contamination and excessive test cost.

## Confirmed important points

- Forecast row `c` is protected when data from `c` onward change; `forecast[:c+1]` is the correct comparison (`verification_design.md:143–152`).
- Targets for **earning** day `t <= c` are protected, but daily net returns/costs are protected only for score dates `< c` because the cost after close on `c` may legitimately react to characteristics at `c` (`verification_design.md:154–164`).
- Continuous replay from day 252 followed by score masks is the correct validation construction; restarting at each fold is not (`verification_design.md:84–92`).
- The two-row golden fixture arithmetic and final-row exclusion are correct by manual inspection. This is not a claim of execution (`verification_design.md:124–137`).
- The memo correctly distinguishes gross market parity from exact net-beta parity for the equal-weight control and uses pooled daily returns rather than the average of fold Sharpes (`verification_design.md:33, 92`).

## 1. Bind every test to the research information boundary

G2 and G6 refer to complete/full input histories (`verification_design.md:64–72,104–112`) without explicitly saying which actual data are permitted at each research stage. During discovery, causal debugging and runtime checks should use the discovery prefix and deterministic synthetic continuations, not the locked actual suffix. Otherwise diagnostic output, late model failures, leakage comparisons or aggregate score logs can expose protected information before the method is frozen.

**Recommended addition:** every run configuration declares its maximum real-data row and the metrics/outputs permitted to be inspected. Discovery checks use rows `<2016`; finalist validation uses the permitted validation histories; the final real-data audit runs only after freeze. Synthetic engineering continuations are labelled synthetic and make no profitability claim. Record any unplanned exposure and downgrade the affected interval's holdout status honestly.

## 2. Keep suffix perturbations within an admissible input domain

The alteration recipe in `verification_design.md:141–164` should say more than “deterministic.” Do not create malformed values, forbidden dimensions, invalid costs or returns below the simple-return floor merely to test causality. A legitimate transformation may reject a nonsensical suffix or encounter a later portfolio failure even if all prefix decisions are causal.

Prefer finite perturbations that preserve known data-domain restrictions—for example controlled suffix resampling/reordering or bounded modifications validated against the declared input contract. Include return-only and characteristic-only changes as planned. Store protected-prefix traces incrementally. If an altered history fails only after the protected cutoff, classify that separately as scenario/robustness failure; it is not by itself proof that the earlier decision used future data. A forecast that cannot finish the altered input may leave the causality comparison **unverified**, rather than automatically proving leakage.

## 3. Do not impose equality of whole caches or unused state

`verification_design.md:72,156–164` appropriately asks to inspect state passed from `forecast` to `rebalance`, but the acceptance wording should distinguish causal state from full-history storage. A module may legitimately cache its complete causal forecast array. Its future rows will differ under a suffix mutation even while every protected decision is unchanged.

Require equality of protected outputs and any state actually consumed in forming those outputs. Review the dependence path of other caches. Do not fail a strategy solely because a global array contains changed future elements that are never read early; conversely, do not let a passing forecast-channel comparison excuse future-informed risk state that changes prefix weights.

## 4. Bound causal verification work without weakening its logic

The phrase “each scheduled refit” (`verification_design.md:150`) can imply hundreds of complete forecast reruns per candidate. Combined with a 12-configuration research budget and the permitted forecast runtime, this could consume the entire assignment window.

Use a predeclared deterministic set covering every **distinct code path**: warm-up, first fit, first risk/scaler update, rolling-window eviction, representative later refits, and a late-horizon point. For unchanged code paths across hyperparameter variants, share the structural review and rerun the cutoffs affected by changed windows/schedules. Full finalist verification should include longer histories and additional interventions. Numerical interventions remain evidence plus source review, never a mathematical proof from a large number of random cutoffs.

## 5. Clarify learned state versus hyperparameter selection

`verification_design.md:88` says parameters are chosen using each fold's allowed development prefix. The master plan should keep the agreed protocol unambiguous: freeze up to three candidate specifications before validation A or B is inspected, run both with their declared online update rules, then select the final candidate. Updating fitted coefficients using newly observed labels during a validation interval is allowed; redesigning hyperparameters after seeing that interval changes its research role.

If later work deliberately reuses validation A to design a new candidate and treats B as confirmation, preregister and record that different procedure instead of silently mixing the two interpretations. After selecting a winner on validation, pooled validation Sharpe is a selection statistic, not an untouched out-of-sample estimate.

## 6. Scope synthetic interface checks to the actual promise

The golden two-stock fixture is correctly a test of the evaluator/harness, not a mandatory size-invariance test for the submitted strategy. Preserve that distinction. The task guarantees 1,000 stocks and 13 characteristics; rejecting a strategy for failing on two stocks would add an unstated requirement. Similarly, the first `rebalance` call has the declared warm-up history. Stress genuinely insufficient **model** history within that interface, without inventing a requirement to accept arbitrary malformed or zero-length scorer calls.

The memo already limits checks to promised behavior (`verification_design.md:78`); this clarification prevents the fixture from being misapplied later.

