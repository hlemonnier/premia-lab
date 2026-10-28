# Independent saved-output verification of the score pilots

28 October 2026, Europe/Paris. Reviewer: score_opportunity_audit. Parent requested
this readback after reviewing the source of the two pilot workflows. This plan
precedes the independent calculation code and its execution. Owner messages have
already disclosed that F1 scores about1.138 and VTvol about1.277 versus V2 about
1.243; the verification is explicitly not blinded and changes no policy choice.
F2 and VTvar results were not known when this specification was written.

## Inputs and immutable scope

Expected forecast directory:
`evidence/v2_score_forecast_20261028/actual_001/`, especially `baseline_V2`,
`F1_base`, `F2_base`, their arrays, CSVs, summaries, source/inputs and final
verification/status. Expected overlay directory:
`evidence/v2_score_overlay_20261028/actual_001/`, especially `fixed_one`,
`VTvol`, `VTvar`, daily/decision CSVs, array hashes, summaries and final results.
The original returns.csv and costs.csv supply stock-level independent accounting.
Source and input identities must match the pinned current V2 source and its
previously verified original inputs. All files read are hashed in the readback
manifest. The readback runs after the required final files are complete.

If root's prospective conditional joint is admitted, its exact saved artifact
paths and schema will be recorded in an addendum before reading/recomputing that
joint result. No additional candidate, parameter or score-window search occurs.

### Conditional-joint addendum, before joint implementation/result

Both standalone families have a positive point improvement: owners disclosed
F2 about1.291780 and VTvol about1.277109, with VTvar about1.274191. Root's fixed
conditional rule therefore nominates only F2+VTvol, subject to the causal
disposition. Its directory will be `evidence/v2_score_joint_20261028/`.
Its virtual targets must match the standalone **F2** target array, not V2's.
Reconstruct its second moments and multiplier from its own F2 gross returns.
The same independent moment reconstruction will be applied to both overlays.
This is additional accounting/source verification, not a new economic hypothesis.
The owner will supply the final subdirectory/schema before saved-output reading.

## Independent calculations fixed before execution

1. Require earning rows253..3778 (3526) and decision rows252..3778 (3527), all
   finite, monotonic and exactly matched to the original scorer endpoint.
2. Recompute net=gross-paidfees; mean/std(ddof=0)*sqrt252; annual arithmetic mean,
   volatility and paid fees; centered regression beta on the original equal-
   weight market; full and existing stage masks [253,2015), [2016,3023),
   [3024,3779). The boundary observations remain full-sample only.
3. For forecast base/F1/F2, use saved target arrays and the original stock return
   and cost arrays to reconstruct every gross return, drifted holding and actual
   fee. Start with zero positions, waive only opening fee, and retain the final
   scored close's fee on its never-earned target. Compare every economic field
   with original-scorer rows and the saved CSV, absolute tolerance1e-12.
4. For overlays, first require the saved baseline_V2 target array's raw contiguous
   SHA256 to match each overlay's recorded virtual-target hash exactly. Then
   reconstruct actual targets as saved multiplier times saved aggregate-gross
   scale times the frozen base targets. Require the reconstructed actual-target
   SHA256 to match each overlay's recorded target hash exactly. Independently
   reconstruct stock-level accounting as in3; do not accept a sum of virtual
   fees or a scaled net return as actual trading cost.
5. Cross-check each summary metric to1e-10 and verify both baseline paths reproduce
   the same economics within1e-8. Record measured numeric differences. Check
   finite/solvent actual returns, gross<=5+1e-12, actual caps appropriate to the
   candidate (.05 forecast, .10 overlays), certificate statuses/counts and
   recorded mean runtime. Source identities and executed input hashes bind the
   results to their code/data.
6. Recompute candidate-minus-V2 paired moving-block Sharpe intervals with block
   lengths21,63,126,2000 draws and seed20261027. Independent implementation uses
   one generator per length, starts from0 through n-L inclusive, concatenated
   blocks truncated to n. Every candidate is reported, not only winners. These
   are conditional descriptive intervals on already explored history, not a
   new statistical promotion gate.
7. A development score improvement requires difference>1e-8; numerical ties do
   not trigger the joint. Absolute full-sample beta<.2, solvency and recorded
   runtime/source/causality disposition remain operational constraints. The
   readback recomputes the numerical ranking, not future-performance certainty.

## Causal and numerical disposition

The original F1 synthetic constant-Gram and mixed-layout allocation expectations
failed and remain failed. The original protected forecast comparisons passed;
the later same-C future isolation passed exactly under the original tolerance.
The readback will report these separately from actual-market future/prefix
checks and never describe the entire original test history as all passed.
An actual failure remains a failure and must be considered by root before
admission. No failed result, source or threshold is overwritten.

The saved-output script is an E2E evidence reconciliation, not a new unit test of
the strategy implementation. No strategy runs in this workflow. Preserve its
own command, source hash, complete findings, failures and output manifest.

## Reported artifact issue before this readback executed

While this readback source was being written, the forecast owner reported that
the saved F1 and F2 NPZ archives lack valid ZIP central directories. The readback
has not opened or changed those archives and has no earlier copies. Preserve
the original files and the owner's failed read. A separate verified recovery or
unchanged-source replay may be supplied via explicit array-path arguments.
Every replacement must reproduce the original summary's target and forecast
raw-array SHA256 exactly, as well as the original economic CSV. No replacement
is accepted merely because its rounded performance is similar. The integrity
failure remains separate from strategy causality and economic performance.

Root authorized an unchanged-source F2 replay with independently verified atomic
NPY outputs. Readback may therefore use that directory after exact original
array-hash reproduction. Root does not authorize a redundant rejected-F1 replay.
For F1, an explicit ledger-only mode will recompute its CSV score, stage metrics,
fees as reported, market consistency and scalar decision/certificate records;
independent stock-level target/fee reconstruction remains **blocked**. It must
not be counted as passed. This limitation cannot affect the winner's accounting
admission, which still requires complete verified arrays.
