# Forecast score results: partial fast/slow adaptation improves the development score

28 October 2026, Europe/Paris. Current production source is frozen at `ce3fe4e`.
Both isolated research prototypes were specified before implementation and scores.
The root score-research plan was committed at `251bee83` before actual economics.

## Economic result

**F2 improves official full-development net Sharpe by0.049277, from1.242503 to
1.291780. F1 loses0.104510 and is rejected as a replacement.** Both retain the
current V2 risk/allocator/cost policy. No half-life, mixture coefficient, ridge,
feature subset or risk parameter was changed after seeing their outcomes.

| Policy | Net Sharpe | Annual net return | Annual volatility | Annual full fees | Realized beta | Mean gross |
|---|---:|---:|---:|---:|---:|---:|
| Reproduced V2 |1.242503 |4.7550% |3.8270% |0.17557% |0.04650 |1.58379 |
| F1 daily ridge slopes |1.137993 |4.1332% |3.6320% |0.14512% |0.03158 |1.26332 |
| F2 partial fast/slow |**1.291780** |**5.1265%** |3.9686% |0.20715% |0.04905 |1.58876 |

F2 gives the13 linear coefficients an equal mixture of pooled EW252 and EW1008
fits, while retaining the EW1008 quadratic and beta coefficients. Every fit is
joint over all27 columns. The official scorer replays actual drift, opening,
closing and stock-level costs; this is not a scaled ledger or gross-only score.
Full earning indices are253..3778,3,526 observations, with3,527 decisions.

| Policy | Original discovery mask | Original validation mask | Original audit mask |
|---|---:|---:|---:|
| V2 |1.098002 |1.656859 |1.147558 |
| F1 |0.999519 |1.481003 |1.224562 |
| F2 |1.117706 |1.528936 |1.498744 |

F2 improves the first and last segments but loses in the middle segment. Much
of its aggregate advantage comes from the last segment. All segments were
already exposed before this design; their names do not create fresh validation.
The higher full score nominates F2 under the score-first rule, with operational
causal disposition recorded below. It does not establish a future improvement.

## Paired uncertainty: no extra significance gate

Paired moving-block percentile bootstrap,2,000 draws, seed20261027, legal final
block start included, same fixed date stream for each candidate and V2:

| Difference versus V2 | Point |21-day95% interval |63-day95% interval |126-day95% interval |
|---|---:|---|---|---|
| F1 |−0.104510 |[−0.19594,−0.01157] |[−0.20202,−0.02190] |[−0.20118,−0.02935] |
| F2 |+0.049277 |[−0.06775,+0.16981] |[−0.07251,+0.15736] |[−0.07284,+0.16518] |

The F2 gain is uncertain. These fixed-policy resampling intervals do not correct
the accumulated research search or guarantee stationarity. The prospectively
specified decision does not require the interval to exclude zero, so it would
be inconsistent to add that hurdle after observing this modest positive score.
F1's lower fees and lower beta do not rescue its negative primary-score result.

Readback: `results.json`; source: `analyze_scores.py`; original outputs:
`actual_001/{baseline_V2,F1_base,F2_base}/daily.csv` and `summary.json`.

## Engineering and causality: report the failures accurately

The prototype remains at SHA256
`7854b2f763ae1bcc716282b68791503fe29f83d0aebc64835d8d0d919c722719`.
The controller remains at
`ea097d7d69be37cea7b6edc9c34d697dc3622a3c76172f20812689ccce1939ef`.
The original scorer hash is
`ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`.

Every original actual-data workflow passes its per-run finite, source/input,
drift/fee accounting, cap/hedge and allocator-certificate checks. Each base has
3,527 `ok` certificates and zero gross-scaling events. V2 reproduces the pinned
committed ledger within the existing1e-8 tolerance; its maximum daily economic
field difference is3.45e-10. F1/F2 forecast rows before127 remain zero.

Observed base forecast times were2.86s for V2,2.84s for F1 and2.88s for F2 over
3,780 input rows. Instrumented average rebalance times were4.34,4.21 and4.27ms.
The F2 forecast extrapolates linearly to19.17s/century; this is an extrapolation,
not an executed century-length check. BLAS was limited to one thread.

The preserved synthetic workflow exited1, despite individual checks passing:
F1 constant-Gram forecast equivalence held to9.11e-18, but tiny perturbations
produced target/closing-gross differences just above the initial1e-9 downstream
criterion. A combined future/layout alteration also exceeded1e-12 for F1's
targets. Canonical C-layout future isolation subsequently reproduced the
protected forecasts, targets and economics exactly; original prefix/repeat and
zero-return controls also pass. The fixture's near-zero market variance makes
its displayed static regression beta uninformative; it is not an actual-market
beta eligibility result.

The actual-data workflow also exited1 at its aggregate check: combined future
alteration and Fortran layout preserved forecasts bitwise, but differences in
targets/closing gross exceeded1e-12. Maximum F2 differences were1.673e-12 in
targets and2.311e-11 in the combined economic fields, including gross exposure.
Both candidates' actual prefixes are exact. These are recorded failed strict
combined-layout criteria, not erased or relabeled as passes. Causal isolation
on the canonical layout must be reported separately.

Root authorized one actual F2 same-C-layout future replay, same seed, cut1500,
source and1e-12 rule. It completed all scorer checks, then its comparison failed
when the original F2 baseline NPZ proved truncated. The original F1 baseline
NPZ was also truncated; both are preserved. Disk inspection found about30GB
free, and no intentional rewrite was identified. The cause remains unknown.

Root then authorized one unchanged F2 baseline replay for evidence repair.
The repair exited0 and reproduced the original full forecast and target hashes
exactly, with economic CSV differences at most4.45e-16 from parsing roundoff.
Separate arrays were written through temporary files, flush/fsync and atomic
rename, then reloaded and checked for shape, exact value and hashes. They are
in `baseline_repair_001/verified_arrays/`, with an explicit manifest.

Comparing this verified baseline to the complete canonical-future run yields
**zero differences on all1,501 protected forecast rows,1,248 decisions and1,247
economic rows**. Combined with the exact actual prefix comparison, F2 passes
the canonical temporal-invariance gate. The original combined-layout criteria
remain failed. No additional F1 run was made; its independent saved-target
readback is limited by the corrupt archive, while its CSV score is preserved.

## Research disposition

F2 is the winning forecast prototype, with the canonical actual causal gate
closed; F1 is a retained negative finding. If the independently specified sizing
family also improves, root's precommitted rule admits exactly one joint
forecast/sizing candidate. Do not assume its gains add, and do not create an
F1/F2 mixture or retune the new forecast in reaction to these outcomes.

Claude's production package is unchanged. The deliverable here is reproducible
research evidence and an exact small forecast specification for implementation.
