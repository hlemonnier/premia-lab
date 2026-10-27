#!/usr/bin/env bash
set -euo pipefail
exec taskset -c 7 bash /workspace/scratch/a72f2bd378f1/continual-research-takehome/evidence/C09_causality_001/rerun.sh
