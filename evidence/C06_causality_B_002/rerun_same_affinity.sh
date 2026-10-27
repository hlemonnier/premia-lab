#!/usr/bin/env bash
set -euo pipefail
exec taskset -c 3 bash /workspace/scratch/a72f2bd378f1/continual-research-takehome/evidence/C06_causality_B_002/rerun.sh
