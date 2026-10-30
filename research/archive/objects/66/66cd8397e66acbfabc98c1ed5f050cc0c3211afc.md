# Independent review of V3 integration evidence

29 October 2026, Europe/Paris. Reviewer: `v3_evidence_audit`.

**Accept the fixed V3 integration on the evidence in this review.** The unchanged
research policy and shipped package both reproduce net Sharpe
**1.444733300556666**, and the original forecast and all three target arrays
have been recovered exactly by their published hashes. The unchanged temporal
workflow passes all fifteen checks. The unchanged century runtime also passes
with verified one-CPU/thread execution and 49,894 valid certificate records.
No implementation blocker remains within this evidence-review scope.

## Scope and source identities

This review pins `hlemonnier/continual-research-takehome` at production commit
`978824d4b6140c43566ebd61a3ee8157f4080e35`, against the published research winner
`9e56aa755d20c5876485188f4c50ce959f6d63f3`. Research uses the historical engine at
`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`. It covers evidence quality, reference
identity, scorer accounting, temporal checks, runtime provenance and the stated
limits of failure-path coverage. The separate policy and market reviews address
implementation fidelity and the economic interpretation of the sleeve.

All historical source references below refer to the production pin. Line numbers
are provided for audit navigation; claims concern the exact pinned bytes. Root's
source manifest and the independently reviewed bindings identify those bytes.
No production source, model parameter, original input or scorer was changed.

## Static findings

### 1. Historical reference gap: independently closed by exact recovery

`verification/V3_INTEGRATION_SPEC.md:11–13` requires the independent research
rerun's forecast, outer, inner and virtual target hashes to equal the published
manifest **before that rerun is used as the reference**. The results explicitly
disclose that the forecast matched but the target hashes did not, and that the
same-environment rerun was substituted
(`verification/V3_INTEGRATION_RESULTS.md:51–55`).

The original integration harness loads five NPY files from the supplied
`--reference` directory without checking their source, input or file identity
(`verification/v3_integration_checks.py:58–69`). It compares the new package
against those arrays and writes scalar results, without persisting its own
arrays or the supplied reference's provenance (`:72–91`, `:114–116`). Therefore
the fifteen recorded passes establish equality to the supplied replacement
reference. The committed packet alone does not reproduce the full bridge from
the original research winner to that replacement.

This is a disclosed deviation, not evidence that the score was fabricated. The
reported maximum economic difference of approximately `4.5e-13` is strong
economic agreement if independently verified. It does not bound each asset's
position difference. Many position changes can have small aggregate P&L, and a
hash mismatch alone does not establish that hardware caused the difference.

The bounded repair was a source-bound rerun of the same research policy and the
same shipped package, saving forecasts and all three books, comparing their
stock-level targets directly, and independently bridging the daily ledger to
the published original. Before this replay, the original large arrays had not
been Git-persisted and were unavailable in the reset workspace. Both reruns
recovered the original forecast and all three target streams exactly, including
their NPY file and raw-array hashes, shape and dtype. The original per-asset
difference is therefore established as zero. This new evidence closes the
reference gap; it does not change the historical fact that Claude's declared
prerequisite was not met during his own integration.

### 2. Historical runtime provenance gap: closed by unchanged one-CPU replay

The committed runtime script constructs 25,200 rows by tiling the original
history, invokes the supplied scorer and reports timing, unique certificate
statuses and a gross-solvency statistic
(`verification/v3_runtime_check.py:14–24`). Its recorded result is 24,946 scored
rows, forecast time 34.7706 seconds, mean rebalance 11.4451 ms, p99 20.3525 ms,
maximum 317.0753 ms, statuses `ok`, and minimum `1 + gross_return` of 0.982146
(`verification/v3_runtime_check.log:2–13`). Those are useful measurements.

The script's pass Boolean checks only the mean rebalance and forecast limits
(`:24`). Its header recommends thread variables and affinity (`:1–3`), but the
committed log does not record the actual process affinity, thread settings,
library versions, input/source hashes or total certificate count. Consequently
the log alone does not establish the claimed one-CPU execution or complete
state-count accounting. The bounded repair is one run of the unchanged script
with an external observer that captures those facts after its existing timers
finish. Tiled history is runtime/state evidence, not another independent sample
of alpha performance. The mean-time limit is distinct from a per-call maximum;
a 317 ms outlier does not by itself breach a 100 ms mean limit.

### 3. The clean-folder log supports portability and rounded economics

`verification/v3_clean_folder_run.log:1–2` records a successful original-scorer
run with Sharpe `1.44`, beta `0.10`, and mean rebalance `17.8 ms`. That supports
clean-folder execution and rounded agreement. It does not itself preserve
enough precision to prove the full number `1.4447333005564316` a third time.
The precise integration result and rounded clean-folder result should be
described separately.

The isolated-mode failure is correctly retained in
`verification/v3_clean_folder_run_attempt1_isolated_mode.log`. Its import error
is consistent with the documented invocation problem, and is not evidence of a
package defect. The missing-package red run is also retained. The self-matching
runtime cleanup incident described in the conversation has no separate failed
invocation/output in the downloaded 27-file change set; that is an incomplete
execution record, not a failed strategy result.

### 4. A claimed binding-cap failure-path branch was not exercised

The V3 failure-path wrapper deliberately aliases the old engine and allocator
imports to the shipped V3 copies, then executes the existing workflow
(`verification/v3_failure_paths.py:10–19`). That is valid evidence about those
shipped low-level files. The result reports zero failures and several relevant
failure/recovery cases.

One assertion is described as preserving a nonzero beta target under a binding
gross cap, but its own log says `binding days 0` and maximum gross `0.2998` for a
`0.3` cap (`verification/v3_failure_paths.log:4–6`). The fixture verified a
nonbinding case; it did not exercise the claimed binding branch. This is a
coverage qualification. It is not a discovered defect in the selected V3
policy, whose inner beta target is zero. No additional variant or failure-path
rerun is necessary to establish the existing candidate's reported score.

### 5. The market-sensitivity table needs its own arithmetic provenance

The results document says every displayed number comes from a neighboring
committed log (`verification/V3_INTEGRATION_RESULTS.md:8–9`), but the sleeve
comparison script only executes sleeve `0.05` and `0.0`, recording the observed
Sharpe, beta, annual moments, costs and two halves
(`verification/v3_sleeve_comparison.py:20–33`). It does not calculate the
zero/reversed-premium sensitivity table or market thirds shown in the results
(`verification/V3_INTEGRATION_RESULTS.md:67–75`). The separate market-review
packet supplies source-bound arithmetic and distinguishes a sleeve-mean
subtraction from a common market-mean shift. This is a documentation and
interpretation repair, not evidence of a false observed score.

## What the original temporal checks establish

The original altered-future tests use cut points `600`, `2000` and `3500`.
They compare forecasts through the cut and all three target streams before the
cut, then compare truncated histories on their available decision range
(`verification/v3_integration_checks.py:93–107`). The restart workflow scores
one history and then another in the same process and compares the second with
fresh-session output (`:108–113`). These checks match the frozen specification.

Passing them supports absence of the tested future dependence and clean reset
between scoring sessions. It does not prove universal causality for every input
or establish arbitrary resumption from a serialized mid-rebalance state.
Selection overfitting is a separate question: changing future data after a fixed
cut cannot undo the researcher's use of already observed history when choosing
the candidate. The whole provided history remains exposed development data.

## Prospective independent closure packet

The new scope and expected outcomes were frozen in
`evidence/v3_evidence_audit_20261029/REPLAY_PLAN.md`, and the wrapper was
independently reviewed before execution. Root releases each of the three modes
separately, binding the prior successful result where required. No new policy,
parameter or temporal cut is introduced.

| Frozen artifact | SHA256 |
|---|---|
| `audit_replay.py` | `ba5379050c51e20b74aba1e45f787e5e5f643fbaf2bb316179263b0289ce516d` |
| `REPLAY_PLAN.md` | `8d64a56d242aaa516012fd8fa9cc9f1206175eb703591985d7a2e66d0d79acd8` |
| `bindings.json` | `fce32c98e78cef9b008fd6823e98321327474b84e0ae268dfb3822a225f3f2f7` |
| Peer source-review JSON | `a1bb0836ff77441bb529f9bc661249324c73ad33200db5b91749dace09b53811` |

The wrapper records actual process affinity and thread settings, Python/NumPy/
pandas/platform, exact arguments, original source/input hashes and source copies.
Replay saves forecast, three target streams, controller moments/clocks,
decision indices, scorer rows, daily ledgers and full certificate records. It
independently reconstructs actual stock-level drift and costs, including the
free opening and charged endpoint. Every saved array is hashed and immediately
reopened and checked. Subsequent temporal execution verifies the reference
against the successful replay result before consuming it. The runtime observer
retains original timers and validates counts and state only after the existing
script completes.

### Execution outcomes

The independent replay passed with original dimensions, 3,527 decisions and
3,526 scored rows. Both policies produced the same net Sharpe
`1.444733300556666`, beta `0.10297751974238421`, annual net mean `6.6089525784%`,
annual net volatility `4.5745139091%`, and annual fees `0.2537924949%`.

The research and package forecast, all three target streams, decision indices
and controller/state-clock arrays have maximum absolute difference zero. All
four economic scorer columns also have maximum difference zero. Both daily
economic outputs match the original published daily CSV exactly. Timing is
retained but excluded from economic equality.

Crucially, both policies' forecast, outer, inner and virtual NPY file hashes and
raw-array hashes equal the **original published** identities. The historical
large arrays have thus been recovered exactly. The original per-asset
difference is now measured as zero for all three books; it is no longer an
unmeasured bridge or an inference from matching P&L.

Each policy produced 7,054 `ok` certificates. Independent stock-level drift and
fee reconstruction errors were at most `5.2041704279e-18` and
`2.3123999460e-19`, respectively, with exact closing gross and market returns.
The original free opening, charged final decision and absence of forced
liquidation are retained. The two policies each saved their full arrays and
certificate records, not only a summary.

Observed actual-sample package rebalance time averaged `15.8562438925 ms` and
reached `936.4859680004 ms` for its slowest call. The research replay averaged
`16.8395407167 ms` and reached `360.7920159998 ms`. These are the actual measured
figures, with observational capture inside the replay workflow. No cause for
the outliers is inferred. The original brief requires a mean below 100 ms on
one core (`source/Quant Research Take-Home/README.md:59–60`); the unchanged
century-runtime execution is reported separately.

Replay result: `evidence/v3_evidence_audit_20261029/replay_001/result.json`,
SHA256 `8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66`.
Its canonical arrays and complete certificate lists are retained for lossless
preservation.

The existing temporal workflow also passed all fifteen checks, under the same
verified one-CPU/thread settings and unchanged source/input bindings. Its saved
reference was verified against the successful replay result before use.
Altered-future/prefix output and the cross-history restart were exactly equal
on their declared ranges. The base score remained `1.444733300556666`.
No new cut point or policy was introduced. Result:
`evidence/v3_evidence_audit_20261029/temporal_001/result.json`, SHA256
`9d91f352f5bd650f76f58e2d84fc534ce8a111a24ce93a135b5f5c5322125e11`.

The unchanged 25,200-row runtime workflow passed under its separately released
prerequisite chain. Actual process affinity was `[1]`, and all three numerical
thread variables were `1` before and after execution. Its retained measurements
are:

| Runtime observation | Independent result | Required or expected |
|---|---:|---:|
| Forecast rows | 25,200 | 25,200 |
| Rebalance decisions | 24,947 | 24,947 |
| Scored / earned rows | 24,946 / 24,946 | 24,946 / 24,946 |
| Last decision index | 25,198 | 25,198 |
| Certificate count | 49,894, all `ok` | 49,894 accepted |
| Mean rebalance | 12.417116967 ms | <100 ms |
| Rebalance p99 | 33.501725650 ms | descriptive |
| Slowest rebalance | 295.596324000 ms | descriptive |
| Forecast duration | 60.571067487 s | <3,600 s |
| Minimum `1 + gross_return` | 0.982145974188 | >0 |

The existing worker's scoring wall time was `372.394995970 s`; the wrapper's
execution-and-capture interval, including input loading, post-timer capture and
final verification, took `392.977084238 s`. Initial source staging precedes that
interval. Arrays were finite and source/input bindings unchanged.
No Sharpe or alpha inference was made from the repeated history. Runtime result:
`evidence/v3_evidence_audit_20261029/runtime_001/result.json`, SHA256
`241cd9b1f78191f9d2cfb19a7f3c886fb2dcba769988b731a10a68ffa1f30ca1`.

### Evidence preservation

Every completed execution packet is immutable. Complete certificate lists for
both replays and the runtime, source copies, original arguments, releases, array identities and
results are retained. A separate lossless packaging step preserves the runtime
certificate JSON, scored rows and final outer/inner/virtual vectors as five gzip
files, totaling `3,117,406` compressed bytes from `12,036,749` original bytes.
Every compressed file was streamed back and matched its original byte count and
SHA256 exactly. Packaging made no policy execution or numerical change.

Packaging manifest:
`evidence/v3_evidence_audit_20261029/runtime_packaging_001/manifest.json`, SHA256
`414ca37bd2ccbc5f84fc150885e574e87953e04a7556a74ecf0385c7f093c1ae`.
It records both original and compressed identities. The full runtime forecast
remains captured locally and identified in the runtime array manifest; this
small packaging packet does not claim to archive that large forecast. It is
explicitly regenerable from the frozen unchanged workflow and input/source
bindings. The actual-sample canonical forecast and complete target streams are
preserved separately for the original-winner fidelity comparison.

## Remaining limits and disposition

Accept the integration. The fresh packet closes the material reference and
runtime-provenance questions without changing a policy, threshold or scorer.
The original failed reference-hash prerequisite stays explicitly recorded, and
the full-precision clean-folder claim and unexercised binding-cap fixture should
be described accurately. Those reporting qualifications do not invalidate the
now-exact original-winner reproduction.

No further policy execution or test is needed for this review. Preserve the
exact canonical arrays and the result-bound source chain, and carry the
separate market-review corrections into the strategy note. Passing these checks
establishes faithful packaging, original accounting and the tested temporal
properties. It does not establish future alpha or eliminate selection
overfitting; all supplied history remains exposed development data.
