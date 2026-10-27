# Independent source review: saved-ledger uncertainty reporter

**27 October 2026, Europe/Paris.** Reviewed before the reporter's first execution by the protected-controller verifier, independently of the reporter's author. The review covered the complete source, both prospective plans, and the final narrow amendment diff. No protected result was opened for this review.

## Reviewed identities and decision

| Artifact | SHA256 |
|---|---|
| Final reporter, `tools/report_protected_uncertainty.py` | `859829789c827670529b6065c914e9c60bf158b2d3badbdda3403222dc3a213c` |
| Root reporting plan | `ff7526bf7b869400274aed83e8c7f2d9a4e1f10a561da0591423e0cbafeef132` |
| Prospective workflow expectations | `197bb5fc1e6394f772f6e71788ccb8d66ad401f47d43068aaf565a632508d594` |
| Original metric helper | `6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69` |

**No remaining source blocker for the single prescribed zero-check.** Release only this command from the project root:

```sh
python tools/report_protected_uncertainty.py --project . --mode zero-check --run ZERO=evidence/protected_replay_zero_001 --out evidence/protected_uncertainty_zero_001
```

This review does not authorize validation/audit execution or claim that the zero-check has already passed. Actual protected execution remains the lead's separate decision after durable publication of the frozen nomination and reporting evidence. The reporter executes no candidate and changes no selection rule.

## Statistical and ledger review

The moving-block implementation matches both plans. For each fixed length21 or63 it constructs a new `default_rng(20261027 + L)`, draws1,000 rows of `ceil(N/L)` independent uniform starts from0 through `N-L` inclusive, adds consecutive offsets within each block, concatenates in draw order, and truncates atN. There is no wraparound, overlap exclusion, future-dependent block choice, or fitted block-length rule. N is fixed at1,007 for pooled validation and755 for audit. Audit creates its generator anew under the same seed rule.

The validation arm order is deterministically C06 then C09. Each replicate's single index vector is applied to both candidates; the difference is C06 Sharpe minus C09 Sharpe for that same replicate. The synthetic ZERO_A/ZERO_B pair explicitly aliases one zero ledger and is labeled as one source fixture with no C09 model execution. Audit has one arm and no paired-candidate result.

Replicate economics use the original net definition, gross minus full fees. Annual arithmetic mean is252 times daily mean, and Sharpe uses the original population standard deviation and square-root252 scaling. A zero standard deviation produces null. A paired ratio difference is null whenever either component ratio is undefined. Percentile bounds use the prescribed linear-interpolation2.5%/97.5% quantiles of finite replicates, with explicit finite/undefined/total counts. No finite replicates yields null bounds with a reason. Complete start matrices and replicate values are retained.

The parser requires the unchanged daily-column order and every full-replay return index, with exact CSV day-label alignment, finite values, nonnegative fees/exposure/latency, and exact net=gross−fee. Each score mask is checked against the original protocol and its exact day sequence. The copied, hash-identified original metric helper recomputes each interval's metrics and requires exact dictionary equality with the controller summary, including the original population-variance convention. Full-replay candidate latency and period-specific instrumented latency remain separately identified.

Cost stress changes only the saved fee column at the fixed multipliers1.0,1.5,2.0. Gross returns, market observations and recorded decisions are held fixed. The1.0 output must equal the original metrics exactly. These are reporting stresses; the source contains no allocator rerun, candidate selection, retuning, or additional strategy configuration.

## Access, provenance and amendment review

Actual modes require the exact supplied nomination hash, its approved stage, matching configuration, the exact C06/C09 validation pair or the single audit-selected policy, and the copied selection record where applicable. Input metadata and fixture kind are checked before the outcome summary is parsed. Zero-check accepts only the prescribed synthetic metadata and requires absent nomination and false protected-access flags. Real outcome access is recorded before parsing an outcome summary or the audit selection record.

Completed-controller status, counts, masks, configuration, source identities, input-integrity records, and all controller-check statuses are required. Every consumed source/metadata/ledger file is checked against its artifact entry; the saved copy is checked again against that same identity. The artifact manifest itself is loaded once as bytes and its copy is checked against those captured bytes' hash and size. Final copied-file integrity is checked again after reporting. The reporter clearly states that large model/input NPY arrays are not consumed or independently rehashed by this saved-ledger workflow.

The first reviewed source, SHA256 `505b2719288e5181337383faf65e24d55f59141fafeaa4a633757c8ad5c812ab`, is preserved in the build-order packet. Before any execution, the author corrected the audit access marker's placement and closed the verify/copy identity gap identified in review. The final amendment also gives the frozen rerun command explicit paths to its copied plans, while retaining the original hardcoded plan hashes. A complete diff confirms that these amendments do not change masks, formulas, seeds, draws, fee multipliers, metric helper, candidate requirements, or selection rules. Syntax-only compilation of the final source passed.

The zero-check must still demonstrate zero means/fees/volatility/drawdown; null Sharpe/beta;1,000 finite zero annual-mean replicates and1,000 undefined ratio replicates per arm and block length;1,000 undefined paired differences per length; null ratio bounds and `[0,0]` mean bounds; and unchanged zero economics under all three fee stresses. Preserve any failed or incomplete outcome. A passing synthetic result will establish only this reporting path, not actual-market uncertainty, stationarity, selection quality, or absence of overfit.
