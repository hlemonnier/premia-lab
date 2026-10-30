# Workflow setup

/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 /workspace/scratch/a72f2bd378f1/continual-research-takehome/tools/report_protected_uncertainty.py --project . --mode audit --run C09=evidence/audit_C09_001 --nomination-sha256 b68c5db46c641f68bdaa7526464c846dd29e1b4ab65c7fd1ab6e8f775762cea4 --out evidence/audit_uncertainty_001

Source review and the zero-ledger E2E precede actual protected reporting. Real protected reporting requires the root's existing stage release and unchanged nomination identity. This workflow reads completed saved ledgers and never invokes a model.
