# Independent reconciliation of the released validation results

**27 October 2026, Europe/Paris.** The saved-output review completed with `EXECUTED_PASS_SCOPE_ONLY`, exit0, and288 of288 checks passing. It independently confirms that both candidates meet the frozen eligibility conditions and that **C09_additive_long_memory is selected by pooled net Sharpe**. No model was rerun, no configuration changed, and no audit observation was read by this review.

## Result under the frozen rule

All figures below are recomputed from the original full-cost daily ledgers. The score masks are A `[2016,2520)` with504 observations, B `[2520,3023)` with503, and pooled `[2016,3023)` with1,007. Pooled metrics come from the pooled daily series.

| Policy and period | Net Sharpe | Annual arithmetic net mean | Annual net volatility | Annual full fees | Realized net market beta |
|---|---:|---:|---:|---:|---:|
| C06, validation A |0.517307 |1.6646% |3.2179% |0.5474% |−0.004032 |
| C06, validation B |0.312408 |1.3002% |4.1618% |0.7408% |0.009641 |
| **C06, pooled** |**0.398603** |**1.4826%** |**3.7195%** |**0.6440%** |**0.004670** |
| C09, validation A |0.366159 |1.4386% |3.9290% |0.1953% |0.001116 |
| C09, validation B |0.935789 |3.9157% |4.1844% |0.2222% |0.008362 |
| **C09, pooled** |**0.659210** |**2.6759%** |**4.0593%** |**0.2088%** |**0.005858** |

Exact pooled scores are0.39860308981402176 for C06 and0.6592096865251688 for C09. Their difference exceeds the frozen1e-6 tie tolerance; simplicity and latency do not determine this selection. Both absolute pooled betas are below0.2, and actual mean candidate rebalance latencies are8.453814ms for C06 and2.130234ms for C09, both below100ms. The complete engineering, finite-output, position and solvency gates also reconcile.

The policy ranking changes between blocks: C06 has higher net Sharpe in A, while C09 has higher net Sharpe in B. C09's pooled maximum drawdown is6.3592%, compared with5.9350% for C06. Its lower recorded full fees accompany the higher pooled net score, but these are different complete learning/portfolio policies; this comparison does not isolate a causal effect of memory, learning precision, or optimizer design. No block-specific rule or new minimum performance threshold was added.

## What the independent review verified

The two packets contain identical canonical3,024-row input arrays, with Fortran-contiguous returns and C-contiguous characteristics. All input/output/source artifact hashes and sizes match, as do the nomination, scorer, helper, configuration and original-reference identities. The review read the entire saved forecasts, targets, drifted held books, timing vectors and ledgers. It confirmed2,771 target decisions and2,770 economic observations in each continuous replay, with no boundary restart or additional free opening trade.

Every gross return, drifted holding, full fee, market return, closing gross exposure and target CSV field reconciles against the saved arrays. Net equals gross minus full fees exactly. Independently ordered arithmetic remains within the original `atol=1e-14,rtol=1e-12`: across both candidates the largest absolute differences are2.78e-17 for gross returns,1.73e-18 for drifted holdings, and1.36e-19 for fees. Market returns and gross exposure reconstruct exactly. All targets satisfy the frozen stock/gross caps and the full gross/net paths remain solvent.

The actual first2,016 forecast rows and first1,763 target/held rows were re-serialized from the full validation arrays. All six original discovery NPY hashes match exactly. The original1,762 gross, fee, exposure, market and net observations also match exactly. This check used the full arrays directly rather than trusting the controller's separately saved prefix artifacts.

The original metric helper reproduces every reported A/B/pooled summary exactly. Separate arithmetic reconstructs the key mean, population volatility, Sharpe, market beta and drawdown within the unchanged tolerance. Saved timing vectors reproduce the reported candidate mean/max latency exactly. The review then applies the original eligibility and ranking rules and agrees with the root-owned selection record.

## Provenance and interpretation

The separate packet is `evidence/validation_independent_readback_001`. Its prospective expectations SHA256 is `adcf3443118be8ca809a5a82b6d9a8427396e5d72e4c8dd8755fa3ec8087fd87`; executed readback source SHA256 is `7cbfaeed4988ae9d2e2f1770eccfa190167a797da11f9929aa62003eca91280b`; completed summary SHA256 is `c082d7e4b94ba05497e55a2af991c53943330820e5f8dc7df982b3038b0b428c`. The packet records the exact command, source, environment, manifests,288 per-check findings, logs and a fresh-output rerun command.

The chronology is explicit: expectations were frozen before this reviewer received the parent result notification, but that notification disclosed the scores and selected policy before readback source implementation finished. The review is independent arithmetic and identity reconciliation, not a blinded review of the ranking. No model, acceptance threshold, score mask or selector was modified after that disclosure.

Validation has selected one of two exposed policies. These findings verify the accounting, identities and mechanical selection; they do not remove selection uncertainty, prove stationarity, or establish a tradable future edge. The separately specified uncertainty report and single fixed-policy audit provide distinct evidence. This reviewer has not accessed the audit.
