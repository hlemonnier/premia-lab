#!/usr/bin/env bash
set -euo pipefail
exec taskset -c 4 bash /workspace/scratch/a72f2bd378f1/continual-research-takehome/evidence/C06_causality_C_001/rerun.sh
