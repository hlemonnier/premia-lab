# Workflow setup

/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 /workspace/scratch/a72f2bd378f1/continual-research-takehome/tools/report_protected_uncertainty.py --project . --mode validation --run C06=evidence/validation_C06_001 --run C09=evidence/validation_C09_001 --nomination-sha256 fc41b27dccc8fc24b7952e66562f399b54b5c7a3109612dcfcfbae38e21e83a5 --out evidence/validation_uncertainty_001

Source review and the zero-ledger E2E precede actual protected reporting. Real protected reporting requires the root's existing stage release and unchanged nomination identity. This workflow reads completed saved ledgers and never invokes a model.
