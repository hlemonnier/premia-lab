# Conditional composition: E2 execution and a costed market sleeve

29 October 2026, Europe/Paris. The released joint workflow scores
**1.444733300556666**, above the best standalone M1 score
**1.426560898191992** by **0.0181724023646741**. All specified actual-workflow
checks pass. Independent root readback confirmed the score, and the separately
released 25,200-row runtime workflow also passed. The research candidate clears
the frozen economic and computational checks. Production integration remains
separate; actual/runtime evidence and all nine sources are frozen.

The precommitted master plan admits one composition because E2 and M1 separately
improved the original net score. E2 scored 1.3395817822087963 and M1 scored
1.426560898191992, against the F2 + VTvol baseline 1.318334966090838. F3 is excluded
after its negative result. The sole new policy is unchanged F2 forecasting,
unchanged E2 execution, then the unchanged fixed +0.05 stock-replicated market
sleeve. It must beat M1 to replace it; there is no subset search after this run.

The engineering risk is nested holdings. E2 must rebalance against its own
independently drifted holdings and maintain the original F2 virtual return path.
The outer market sleeve then trades the combined stock target and pays actual
net stock costs. Its own drift denominator must not enter the inner optimizer.
The original scorer remains authoritative for the outer economic outcome.
E2's optimization prices trades against its independent inner holdings, while
the original scorer charges the combined outer trades after netting. The
composition is not a single optimizer over the combined portfolio's costs.

The [joint plan](../../evidence/v2_score2_joint_20261029/PLAN.md) and
[prospective workflow specification](../../evidence/v2_score2_joint_20261029/E2E_SPEC.md)
require exact inner-path and M0 equivalence, temporal invariance, cross-history
resets, independent accounting, deterministic cost netting/caps and atomic array
readback. A runtime-only trace-trimming observer must reproduce complete synthetic
economics and every decision hash exactly before a selected composition can use
it for a 25,200-day stress. Tiled data are computational evidence only.

The prospective harness and missing-factory red run preceded the nine-line
composition factory. The red run exited 3 with zero economic executions and is
retained. The factory only constructs E2 through its unchanged wrapper and
passes it to the unchanged MarketSleeve. All five dependencies are byte-identical
copies of the reviewed sources; there was no implementation repair.

## Synthetic verification

The first implemented synthetic workflow exited 0, with empty stderr, and passed
all 14 summary checks plus 383 per-workflow checks across 12 complete scorer runs.
Standalone E2 reproduces its earlier atomic targets, virtual targets, forecast
and economic rows exactly. M0 around E2 recovers that standalone path exactly.
The combined M1 portfolio preserves the inner E2 targets, virtual F2 targets and
returns, EW moments, multiplier and forecast exactly.

Altered-future and pure-prefix checks preserve 361 forecast rows, 108 decisions
and 107 earning rows exactly. Cross-history restart also reproduces the full
420-row synthetic path exactly. Zero returns leave E2 at cash and the outer
market basket at its fixed target, with zero gross return and trading costs.

The deterministic netting case pays 0.00001930605729647984 on its first charged
rebalance, below 0.00002186563611414483 when the component trades are costed
separately. This uses the same actual portfolio denominator for the decomposition.
The deterministic cap case leaves the inner target unchanged while reducing
outer gross. The separate E2 extreme fixture also exercises 133 outer cap
decisions and still preserves every inner E2/F2 decision exactly.

The prospective runtime observer passes its full-recording comparison: rolling
hashes of every actual, inner E2 and virtual F2 target match exactly, along with
forecasts and the four economic scorer columns. It trims diagnostic records
only after a complete outer rebalance; live policy state is unchanged. This
establishes synthetic recording equivalence, not a 25,200-day runtime pass.

The result is preserved in
[synthetic_001/result.json](../../evidence/v2_score2_joint_20261029/synthetic_001/result.json),
SHA256 `f23fa2a55efaf9bbf6c8b120bfdeded7daec33ac961baef17dc68082410fdbe5`.
The nine-file source binding is
[pre_review_source_manifest.json](../../evidence/v2_score2_joint_20261029/pre_review_source_manifest.json).

Independent reviewers accepted composition/state/costs and the E2/runtime
observer interface without required corrections. At that checkpoint actual
scoring and long-history runtime remained unexecuted, each requiring its own
source-bound root release. The released actual result follows below. All history is
exposed development history; this composition is explicitly part of the counted
search. Earlier F3 files and production code remain frozen.

The execution owner accepted the E2 interface and runtime observer with no
corrections, independently rehashing all three full target arrays against both
recording modes and checking final targets, forecasts and economic rows exactly.
The binding review is
[joint_execution_runtime_review.json](../../evidence/v2_score2_execution_20261029/joint_execution_runtime_review.json).

The independent challenge reviewer also accepted the frozen source and complete
synthetic evidence, verifying 171 artifact hashes and 96 atomic arrays. Its
independent accounting reconstruction differs by at most 9.58e-18 across all
fixtures; explicit historical-weight reconstruction of the VT controller differs
by at most 8.88e-16. Exact inner, temporal, M0 and trimmed-path identities were
reconfirmed. See
[joint_synthetic_review.json](../../evidence/v2_score2_review_20261029/joint_synthetic_review.json)
and its bound source-review record.

## Released actual result

Root released the unchanged nine-file implementation in
[JOINT_ACTUAL_RELEASE.json](../../evidence/v2_score2_root_20261029/JOINT_ACTUAL_RELEASE.json),
SHA256 `b3c6afc2f14995b1d5c3c29a5c4c79d84d4721bf4ce341e005aaa59f236ada9b`.
The command ran on CPU 1 with one BLAS/OpenMP thread and original CSV inputs,
exited 0 and produced no stderr. Only the six predeclared actual-data workflows
ran: standalone E2, M0, the one joint candidate, altered future, prefix and restart.

| Original scorer metric | Best standalone M1 | E2 + M1 joint |
|---|---:|---:|
| Full net Sharpe | 1.4265608982 | 1.4447333006 |
| Discovery net Sharpe | 1.1786691069 | 1.1990348669 |
| Validation net Sharpe | 1.8102604044 | 1.8423639698 |
| Audit net Sharpe | 1.6644954621 | 1.6546639685 |
| Annualized net return | 6.509869% | 6.608953% |
| Annualized net volatility | 4.563331% | 4.574514% |
| Annualized trading costs | 0.337040% | 0.253792% |
| Gross Sharpe | 1.5026019869 | 1.5023068898 |
| Realized net market beta | 0.1027110970 | 0.1029775197 |
| Mean gross exposure | 1.8342634126 | 1.8265270274 |

The full comparison uses 3,526 original earning observations, zero-based rows
253..3778. The unchanged diagnostic masks are discovery [253,2015), validation
[2016,3023) and audit [3024,3779). They are exposed development periods, not
fresh confirmation. The audit-period Sharpe declines slightly; the frozen rule
did not require improvement in every historical period.

The annualized net-return gain is 9.908 basis points. Its exact mean-return
decomposition is an 8.325-basis-point reduction in fees plus a 1.584-basis-point
increase in gross return. Fees fall 24.70% relative to M1. Gross Sharpe is almost
unchanged and slightly lower. This supports the execution-cost mechanism:
unchanged F2 forecasting and virtual returns, with a different cost-aware actual
book. It is not evidence of a new forecasting signal. This decomposition concerns
annualized arithmetic return, not an additive decomposition of Sharpe.

The fixed market sleeve remains explicit. Both candidate and standalone carry
about 0.103 realized market beta, below the required 0.2 limit. Their score is
evaluated including this permitted market exposure and all actual trading costs.
The joint is the fifth and final new economic policy admitted by this wave's
precommitted rule. No alternate subset, sleeve amount or parameter was tested.

## Actual operational result and frozen evidence

All nine summary checks and all 192 per-workflow assertions pass. Standalone E2
reproduces the previous atomic targets, virtual targets, forecast and economic
rows exactly. M0 reproduces E2 exactly. The joint preserves every inner E2 target,
virtual F2 target/return, controller moment, multiplier and forecast exactly.

Future alteration and pure prefix each preserve 1,501 forecast rows, 1,248
decisions and 1,247 earning rows exactly. Cross-history restart reproduces all
3,780 forecast rows, 3,527 decisions and 3,526 earning rows exactly. Both inner
and virtual allocator certificates pass on every candidate decision. Drift,
independent state, the free opening, charged final rebalance, physical bounds
and solvency pass; reconstructed scorer accounting error is exactly zero.
No outer gross cap binds in the ordinary actual candidate path. The synthetic
stress covers that branch independently.

Candidate forecasting took 2.897 seconds on the supplied input. Instrumented
mean rebalance time was 7.811 milliseconds and the 99th percentile was 11.446
milliseconds. The subsequently released 25,200-day stress is recorded separately
below; the ordinary-input timing was not treated as its substitute.

The complete actual evidence is frozen under
[actual_001](../../evidence/v2_score2_joint_20261029/actual_001). It includes atomic,
readback-verified targets.npy, inner_targets.npy, virtual_targets.npy, rows.npy,
forecast.npy, decision_indices.npy, virtual_returns.npy and controller_trace.npy,
plus source copies, commands, daily/scalar decision CSVs and all verification runs.
Root can reconstruct economics directly from saved targets and original returns
and costs, without executing another policy.

Key evidence identities:

| Artifact | SHA256 |
|---|---|
| actual_001/result.json | `1e156b5b2c864f5d6b7a7edc2bb190f640b0ad6e4ebc19d536b68e7e7a08b30d` |
| actual_001/economic_comparison.json | `9156228fdaca4dd19cbabd29ab2a5183183c47e59bfc4ee3a8f468dea576bae9` |
| actual_001/E2_M1/array_manifest.json | `b47d435638ee44de4e8acd2c0af14f3a86dac75776118e4264f4d8caa28c8f5f` |

## Independent root readback and fixed-policy uncertainty

Root independently reconstructed every scored stock-level return, drifted holding
and trading cost from the saved targets and original CSV inputs, without running
the policy. It reproduced net Sharpe 1.444733300556666. Maximum absolute gross
return reconstruction error was 5.20e-18; fee error was 2.31e-19. It reconfirmed
3,527 decisions, 3,526 earning rows, the free opening, final charged rebalance
and absence of forced liquidation. Maximum actual weight was 0.016484 and maximum
gross exposure was 3.043265. Its binding record is
[joint_readback_001.json](../../evidence/v2_score2_root_20261029/joint_readback_001.json),
SHA256 `565c895d63e2dc7ee2e511bb47514c09fd08da841b6111c6b6cb5b007bb25e6f`.

Using the predeclared paired moving-block bootstrap, 2,000 draws and seed
20261027, root obtained these 95% intervals for the net-Sharpe difference:

| Block length | Joint minus M1 | Joint minus previous F2 + VTvol leader |
|---|---:|---:|
| 21 days | [0.007456, 0.029299] | [0.046424, 0.202522] |
| 63 days | [0.007364, 0.029751] | [0.045126, 0.194149] |
| 126 days | [0.008205, 0.030607] | [0.041123, 0.191659] |

The corresponding point changes are +0.0181724 and +0.1263983. These are
fixed-policy descriptions of exposed development history. They do not adjust
for the full strategy search or create an untouched validation sample, and were
not added as a promotion requirement after seeing the result.

Root's timing readback also records a maximum individual actual rebalance of
138.104 milliseconds, alongside the 7.811-millisecond mean and 11.446-millisecond
99th percentile. The frozen runtime criterion concerns mean rebalance time.

This research result is bound to the ce3 engine. Production integration must
preserve Claude's subsequent engineering fixes and establish its own equivalence.
No production file was changed by this experiment.

## Completed 25,200-day computational gate

After independent actual-score reconstruction, root separately released the
unchanged runtime harness and selected policy in
[JOINT_RUNTIME_RELEASE.json](../../evidence/v2_score2_root_20261029/JOINT_RUNTIME_RELEASE.json).
The command completed with exit 0 and empty stderr. All three summary checks
and 31 per-workflow checks pass. It used CPU 1 with one BLAS/OpenMP thread and
the prospectively verified observation trimming; all nine source hashes remained
unchanged.

| Runtime measurement | Result |
|---|---:|
| Input observations | 25,200 days × 1,000 stocks |
| Forecast matrix | 25,200 × 1,000 |
| Decisions | 24,947 |
| Economic scorer rows | 24,946 |
| Forecast time | 20.035996 seconds |
| Mean rebalance time | 7.990193 milliseconds |
| 99th-percentile rebalance | 13.269609 milliseconds |
| Maximum rebalance | 150.263600 milliseconds |
| Peak resident memory | 3,835,208 KiB, approximately 3.66 GiB |

The declared limits are forecast time below 3,600 seconds and mean rebalance
below 100 milliseconds on one core. This workflow passes both. Individual
maximum latency is reported separately; the gate was never a per-call 100 ms
guarantee. Finiteness, solvency, both allocator certificates, independent risk
clocks, inner and outer holdings, dynamic caps and actual fee accounting pass
throughout all 24,947 decisions. Reconstructed scorer accounting error is zero.

These 25,200 rows cyclically repeat the supplied data. The run reports an empty
performance-metrics object and provides computational evidence only. It does
not add another economic candidate, estimate future performance or manufacture
an additional validation period.

The frozen runtime packet retains the generated characteristics memmap, full
forecast and scorer rows, decision indices, virtual returns/controller traces,
final actual/inner/virtual targets, per-decision scalar diagnostics and rolling
SHA256 hashes of all three complete target paths. Full target histories are
represented by those rolling hashes in this declared mode; full/trimmed target
equivalence was independently verified on the prospective synthetic workflow.

Runtime result:
[runtime_001/result.json](../../evidence/v2_score2_joint_20261029/runtime_001/result.json),
SHA256 `f4983861a78b53f8a41dcc5b9b49d0a9ddac715a097175861db83ccc5c652bb5`.
Its summary SHA256 is
`dd6c08042ec5c22b73aa0bd4872b233ca648f325f4d7b7c546e6837599832a7d`;
array-manifest SHA256 is
`166213d4aa91ba52c14db857392e04f511ab8845e04b235830e314337d6e1569`.

The selected research policy is ready for review against Claude's current
production implementation. This packet does not claim that an unexecuted
production integration inherits its score, equivalence or runtime result.
