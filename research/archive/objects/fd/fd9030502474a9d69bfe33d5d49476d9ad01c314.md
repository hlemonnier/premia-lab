# C06 current-layout saved-output disposition

Source-reviewed reporter executed once under CURRENT_SCOPE_DISPOSITION_PLAN.md and HISTORICAL_ARRAY_RECOVERY.md, preserving the original combined historical byte-check failure. No candidate was run by this report.

Executed command: `python3 evidence/C06_causality_admission_002/reconcile_current_groups.py --project . --out evidence/C06_causality_current_disposition_001`.

Actual: exit0;39completeworkers,36comparison scenarios,120directnumericcomparisonsPASS and24emptycomponentsNOT_APPLICABLE; every nonempty current-run numeric comparison is exact. All1131 identity,scope,mask,process andcomparison checks passed within this scoped report. Originalcombined C-vs-Fbyte gate remainsFAIL. StandarddiscoveryhistoricalreproductionPASS. Hash-identical originalforecast/target arrays nowpermit numericcomparison: all values lie within the previously frozen tolerances. See summary.json for separate statuses and exactmaxima.

The reporter verifies live admitted source identities as well as frozen evidence. A rerun requires the admitted version of those source files (recorded in admission.json); a later fixture correction must not be silently substituted. Candidate workflows themselves have their original frozen runner/source reruncommands.
