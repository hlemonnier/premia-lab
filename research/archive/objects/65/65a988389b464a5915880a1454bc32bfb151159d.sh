#!/usr/bin/env bash
set -euo pipefail
exec taskset -c 2 bash /workspace/scratch/a72f2bd378f1/continual-research-takehome/evidence/C06_causality_A_001/rerun.sh
