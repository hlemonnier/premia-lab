# Independent review of frozen-position attribution

27 October 2026, Europe/Paris. Reviewer: independent causality/source agent. This document records staged review; a completed specification review is not an executed tool or market-analysis pass.

## Preimplementation specification review

**Status: the bounded descriptive design is acceptable, subject to the prospective verifier, implementation and execution gates below.** The selected C09 policy, its configuration and its four-file handoff must remain unchanged. All historical periods are already exposed; no result from this extension is clean confirmation for a new policy.

Read `research/FROZEN_ATTRIBUTION_PLAN_20261027.md`, the two follow-up literature/notes documents, original scorer, and the existing `submission/strategy.py` and `submission/strategy_factor.py` risk functions. No market arrays, new attribution outputs or model executions were used for this specification judgment.

### Indexing and prior-information state

The saved target at index zero is chosen after close 252 and first earns return 253. The opening book for scored return row `t` is therefore `targets[t-253]`. Using `targets[t-252]` would use a target chosen after seeing that return. Using the saved drifted book would explain after-return holdings rather than the opening book. Reconciliation of opening target times realized returns against the original gross ledger must precede interpretation.

For that earning day `t`, C09's original risk call receives exactly `R[:t]`, ending at `t-1`. Its trailing risk window and marginal-variance shrinkage must be unchanged. C04's cache epoch is `max(0,(history_length-253)//21)`, so when the explanatory estimator first visits earning row 253 it refreshes on 253, 274, 295, and so forth. Between refreshes, reuse the stored correlation loadings and rescale with the current prior-estimated marginal variances. Recomputing factors on every day, fitting them on the full packet, or silently shifting the refresh epoch would change the explanatory lens.

The requested preimplementation clarifications have been adopted in the root plan: factor rank 10, shrinkage 0.5, refresh every 21 days, window 252, and thin-SVD rank tolerance `float64_epsilon * max(number_of_stocks, number_of_loading_columns) * largest_singular_value`, retaining only singular values strictly above the threshold. Empty or numerically zero spans need an explicitly empty basis. These values must not be chosen from attribution outcomes.

### Mathematical decomposition and interpretation

Let `e = r - beta * m` and let the columns of Q be an orthonormal basis for the fixed explanatory loading span. The algebra

`w'r = (w'beta)m + w'QQ'e + w'(e-QQ'e)`

is correct. The factor scores use realized row `t` solely for descriptive attribution. They are not an admissible same-day forecast. The loading basis and opening book must be determined before row `t`.

This is a Euclidean projection onto C04's current rescaled factor-loading span. It is not IPCA estimation, a fitted price-of-risk model, or an identification of the simulator's economic factors. A small remainder can coexist with no independent tradable alpha; a large remainder can contain omitted common risks, nonlinear exposures and estimation error. The prior beta is the same beta used to construct the frozen hedge, so a near-zero estimated-market component is substantially constructional and does not independently establish realized future beta neutrality.

For each original stage mask, `Cov(component,gross)/Var(gross)` is an additive covariance contribution when all terms use the same sample and denominator convention. Contributions sum to one if gross variance is nonzero. They can be negative or greater than one. They are not nonnegative independent-risk percentages, PCA variance-explained percentages, or portfolio weights. Component volatilities do not add, and neither component Sharpe ratios nor selected mean percentages should be introduced after seeing outcomes.

### Prospective verification requirements

The independent verifier should use the complete CLI workflow and written expectations before the tool exists. Known-component fixtures need nonzero market, factor and remainder contributions, changing predetermined opening positions, an independently established factor span/rank, and enough assets that rank ten does not automatically capture every residual direction. A correct sum-to-gross identity alone would not detect an implementation that sends the whole residual to the factor bucket or always uses a zero span.

The fixture must make the target-index shift economically detectable. A known periodic factor construction with more than ten independent residual directions is one possible design, not a required change to the admitted specification. Zero returns must retain zero components and null undefined covariance ratios. Malformed identity data must fail before numeric interpretation. A modified future and a truncated packet must preserve all earlier descriptive rows whose own realized returns have not changed, with fixed tolerances set before execution. Since attribution uses return `t`, a suffix mutation beginning at `c` protects attributed economic rows strictly before `c`; it does not protect row `c` itself.

Only an independent implementation review and a completed prospective synthetic workflow can release the one declared canonical attribution. No source-review approval substitutes for that execution evidence.

## Cross-review of the user-note reconciliation

The mathematical corrections in `research/USER_NOTES_REVIEW_20261027.md` are sound within their stated assumptions: an equal-weight overlay can hedge estimated beta when correctly sized; centered sample covariance has rank at most 251 with 252 observations; constraint multipliers couple static no-trade conditions; the annualized daily Sharpe standard-error illustration needs the daily/annual frequency conversion; residualization and GLS are different operations; and scaling portfolio targets need not preserve exact scorer Sharpe because the drift denominator and subsequent trades change.

The document correctly treats diagonal residual risk as a regularization trade-off rather than claiming that residual correlations vanish. It also correctly distinguishes a 1,008-day learning half-life, characteristic persistence and the 20-day cost-control horizon. Its no-trade expression is valid at an unchanged feasible interior book, with its explicit warning to evaluate the risk gradient at the solved portfolio when other coordinates move. The caveat about gross rescaling disturbing that local no-trade result is necessary and accurate.

One wording correction was requested and applied in the notes: the original assignment README itself describes its particular naive cvxpy example as taking about one second per call. That is an employer-provided estimate for that example, not a local benchmark and not a universal statement about cvxpy or 1,000-variable programs. It should not be described as having the same unsupported provenance as an invented two-to-five-millisecond claim. No strategy change follows from this clarification.

## Cross-review of the literature follow-up

`research/LITERATURE_FOLLOWUP_20261027.md` appropriately separates primary-source claims, limitations of abstract-only access, and project-specific inferences. This reviewer independently retrieved the primary arXiv abstracts for [linear-cost trading](https://arxiv.org/abs/1203.5957) and [attention factors](https://arxiv.org/abs/2510.11616), and the [CEPR latent-factor record](https://cepr.org/publications/dp12926). Their narrow methodological descriptions match the note: proportional costs support threshold/inaction behavior in the cited single-market setting; covariance-dominant PCA can miss expected-return-relevant weak factors; attention factors are a much larger proposed architecture rather than a small improvement established for this simulator.

Direct NBER retrieval returned HTTP 403. A subsequent search retrieved the indexed primary [NBER 24540 abstract](https://www.nber.org/papers/w24540) and the [SSRN 3032013 record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3032013); these support the distinction between characteristic-instrumented dynamic loadings and characteristic-associated intercepts. The versions report different empirical factor counts, as the note already acknowledges. This does not support importing either count into the simulated market.

The indexed primary [Flint–Vermaak SSRN abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3986499) concerns the persistence of factor exposures and says that expected-return implications also require risk-premium estimates. The note correctly refuses to identify this with predictive-alpha decay. Its label-maturation rule `s+H <= t-1` is correct for the stated forward target. No full manuscripts, real-market Sharpe estimates, or independent reproductions are claimed by this cross-review.

The proposed decomposition is a narrower explanatory exercise than IPCA, weak-factor optimization or a new residual learner. It can clarify where the frozen policy's realized P&L is recorded under one prespecified, causally updated factor-span construction. Its correlation loadings refresh every 21 observations, but daily marginal-variance rescaling can change the final span between refreshes. It cannot by itself determine whether those earnings are risk compensation, stock-specific mispricing or durable alpha.

## Implementation and execution review

The separate prospective `verification/FROZEN_ATTRIBUTION_E2E_PLAN.md` has now been read before the implementation exists. It specifies 420 synthetic days, sixteen Hadamard stock directions, eleven complete-period residual frequencies with distinct amplitudes, the top-ten known factor span, changing target weights, and all three nonzero known P&L components. This resolves the concern that a purely additive identity could pass a meaningless projection. The altered-future case begins at row 337, a refresh boundary, and explicitly checks that row's prior-estimated span against its changed realized return. Repetition, truncation, degenerate risk, wrong manifest digest, tampered bytes, malformed indices and falsified gross accounting are also declared prospectively. These are useful independent whole-workflow expectations rather than component tests that mirror the implementation.

The 404-line `tools/verify_frozen_attribution.py` was then reviewed while the implementation was being prepared. Its oracle is the independently specified Hadamard projection and never imports the implementation or helper risk estimator. It explicitly checks all three nonzero components, rank, opening-target indexing, current-day prior-estimation boundary, exact protected prefixes, original fee preservation, fixed stage summaries, null degenerate ratios, output hashes and unchanged handoff. Each scenario runs in a fresh subprocess. The malformed inputs are new synthetic packets with deliberate corruption; actual research evidence is not rewritten. No blocking mathematical or control-flow defect was identified in this verifier review, and no extra test was introduced by this reviewer.

The preserved `evidence/frozen_attribution_red_001` records the missing-implementation stage with six checks and one subprocess. Its status is `EXPECTED_RED_MISSING_IMPLEMENTATION`; the controller succeeds because the missing tool is expected, not because an attribution ran successfully. The original rerun path later contains the implemented tool, so reproducing that absence requires the original preimplementation checkout or an explicit fresh nonexistent `--implementation` path. That portability distinction should be documented separately; the original evidence must not be rewritten to make its past environment appear current.

## Completed implementation source review

**Source review: passed within the declared descriptive scope.** The complete 385-line `tools/attribute_frozen_policy.py` was read independently. No change to its source or the verifier was requested after reading the synthetic outcomes.

| Reviewed object | SHA256 |
|---|---|
| Attribution tool, equal to the synthetic frozen copy | `ffb438980341e8729ff25cdbd56644fb32f1aabc81f17f87fd1aef2a16d81463` |
| Preimplementation verifier, unchanged | `acfc1cc613b21bd6094c25da194f56a943a410ab4f0a10bcad6372c41294edb0` |
| Preimplementation E2E expectations | `c437e64355e7fa01ff3a1c7084b92d518f607e98c416472e6cab24349a74ceba` |
| C09 base-risk helper | `104a16789d2a9d78a9fa77e6e27b3e7f87952eff041a599634e96267de045bd7` |
| C04 factor helper | `9e63257c14859430b5190763c5f1fd35320c582019c941ae28b43243587a4959` |

The tool authenticates the explicitly passed packet manifest and every consumed source/data identity before loading numeric arrays. Real mode additionally pins the original canonical inventory and metadata hashes and requires the separate `--allow-canonical` flag. That flag is an execution guard, not a substitute for the root's reviewed release. Synthetic mode requires its synthetic metadata kind and rejects the real-mode flag. Paths are confined to the declared packet, and output creation refuses to overwrite an existing directory or write inside the immutable packet.

Only authenticated helper copies are imported through a private process package. `factor.configure` receives the exact original C09 configuration and fixed C04 settings. Its base learner and factor wrapper forecast/rebalance functions are replaced locally with exception-raising sentinels; the attribution loop never calls them. It calls only the prior-risk estimator and correlation-factor function. Import-time configuration does not fit any data. There is no read of characteristics, forecasts, original CSVs or an alternative strategy's outcomes.

For each `t` the code selects `targets[t-253]`, reconciles its realized gross P&L and the ledger's net/market arithmetic, then estimates risk from `R[:t]`. It refreshes correlation loadings at the prescribed epoch, retains them between refreshes, and rescales with current marginal variances. Thin SVD uses the frozen tolerance rule, with an empty matrix for no factors and no retained singular vectors if all singular values are zero. The projection, remainder and full-cost subtraction follow the admitted equations. Each output records both the correlation-fit cutoff and current variance cutoff, so factor-age reporting cannot conceal daily rescaling.

The stage summarizer preserves the three original masks, uses population covariance/variance consistently, leaves zero-variance covariance contributions null, and reports signed contributions without clipping them to zero or one. Output contains no component Sharpe or selected interval. Each day must reconstruct the original gross and net at the prospectively fixed tolerances; completed rows and an error remain available on failure. Consumed input and private helper hashes are checked again before success. The tool writes only its fresh evidence directory; it has no operation that edits the selected handoff or historical packet.

## Completed synthetic evidence review

The unchanged prewritten controller completed `evidence/frozen_attribution_synthetic_001` with **258 passing checks and nine fresh CLI subprocesses**, controller exit code 0. This reviewer then read the saved result files directly, rather than accepting that pass flag alone. No model or canonical market attribution was executed by this reviewer, and no additional test suite was written.

The independent readback observed:

| Item | Observed result |
|---|---|
| Current versus frozen tool/verifier source hashes | Exact identities listed above |
| Complete saved synthetic artifact inventory | 278 entries; zero missing, size-mismatched or hash-mismatched entries |
| Known market-component maximum absolute error | `6.098637220230962e-20` |
| Known residual-factor-component maximum absolute error | `5.149960319306146e-19` |
| Known remainder-component maximum absolute error | `5.497243827680409e-19` |
| Repeat | All 166 daily rows and all CSV fields exactly equal |
| Altered future beginning at 337 | All 84 earlier rows and all CSV fields exactly equal |
| Truncated 338-day packet | All 84 available attributed rows and all CSV fields exactly equal |
| Wrong manifest digest | Rejected at `packet_manifest_identity`, before numeric loading |
| Tampered return file | Rejected at `identity:inputs/returns.npy`, before numeric loading |
| Duplicate ledger index | Rejected at expected row 260, with no completed attribution rows |
| Consistently falsified gross and net | Rejected at opening-gross reconciliation at row 260, discrepancy `-0.001`; seven prior rows preserved |

The zero fixture completed with zero rank/economics and the prescribed null covariance ratios. The unchanged controller also checked the changed return at refresh row 337 against the independently known prior span and beta. Both are synthetic engineering evidence, not observations about market alpha.

Exact read-only command used for the independent saved-evidence inspection, from the repository root:

```sh
python - <<'PY'
from pathlib import Path
import json,hashlib,csv,numpy as np
p=Path('evidence/frozen_attribution_synthetic_001')
s=json.loads((p/'summary.json').read_text())
print('controller',{k:s[k] for k in ['status','exit_code','model_executions','market_data_read']})
print('checks',len(s['checks']),'passed',sum(x['status']=='PASS' for x in s['checks']))
for f in ['tools/attribute_frozen_policy.py','tools/verify_frozen_attribution.py','verification/FROZEN_ATTRIBUTION_E2E_PLAN.md']:
 print('current_source_sha256',f,hashlib.sha256(Path(f).read_bytes()).hexdigest())
print('frozen_implementation_sha256',hashlib.sha256((p/'implementation_used.py').read_bytes()).hexdigest())
print('frozen_verifier_sha256',hashlib.sha256((p/'verifier_used.py').read_bytes()).hexdigest())
for r in s['processes']:
 q=Path(r['output']);d=json.loads((q/'summary.json').read_text()); print(r['name'],r['exit_code'],d['status'],'numeric',d['numeric_content_read_started'],'rows',d['completed_rows'],'error',d.get('error','').splitlines()[-1:])
def read(path):
 with path.open(newline='') as f: return list(csv.DictReader(f))
actual=read(p/'runs/baseline/daily_attribution.csv'); expected=read(p/'known_components.csv')
keys=['market_component','residual_factor_component','remainder_component']
a=np.array([[float(r[k]) for k in keys] for r in actual]);e=np.array([[float(r[k]) for k in keys] for r in expected]);print('known_component_max_abs_errors',np.max(np.abs(a-e),axis=0).tolist())
for label in ['repeat','future_suffix','truncated']:
 rows=read(p/f'runs/{label}/daily_attribution.csv')
 if label=='future_suffix': rows=[r for r in rows if int(r['return_index'])<337]
 print(label,'protected_rows',len(rows),'all_common_fields_equal',rows==actual[:len(rows)])
manifest=json.loads((p/'artifact_manifest.json').read_text())
bad=[]
for rel,item in manifest.items():
 f=p/rel
 if not f.is_file() or f.stat().st_size!=item['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=item['sha256']:bad.append(rel)
print('saved_manifest_entries',len(manifest),'mismatches',bad)
PY
```

The command exited 0. Its numerical outcomes and rejection causes are reproduced in the table above. The original synthetic packet retains all nine commands, outputs, expectation files, input/source snapshots, stdout/stderr, and the controller's separate rerun command. A future checkout must restore those recorded locations or explicitly reconstruct the same identified synthetic inputs before replaying path-specific commands.

## Release disposition

The source review and synthetic engineering gate support release of **only the single originally declared descriptive attribution**, with unchanged source/configuration/rank/window/refresh/threshold and original period masks. The root must record that release and its exact real-packet command separately. At this review checkpoint, no canonical numeric attribution is approved as completed or interpreted. Any actual failure remains a failure; it does not authorize changing the explanatory lens to improve the result or reopening model selection.
