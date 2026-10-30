# C06 saved-output historical reconciliation

This read-only reporter consumes the39 already completed discovery/synthetic worker packets, unchanged C06admission, prospectiveplan and PIDnamespace amendment. It fits no model and opens no new market rows. The original expectation includes exact historical forecast/target NPY hashes plus all current-run invariants.

Executed command: `python3 evidence/C06_causality_admission_002/reconcile_groups.py --project . --out evidence/C06_causality_reconciliation_001`.

Actual: exit1 at the first historicalforecast hash check. The saved currentbaseline SHA was d9ce03ba69f9a7a3419a489053c9944bcf3a79c76a5910240e721c5c60859ada; historicalexpected0149e9d11a5d681a5bf96df539468800685b31b09c210bfbedbebc94f8f36cf0. The reporter stopsatthisfailure; laterchecks areunexecuted inthisreport andarenotpassed. See summary.json andstderr.log. Originalcontrollerresults remain separatelyavailable. No tolerance was relaxed.
