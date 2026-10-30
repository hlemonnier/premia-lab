#!/usr/bin/env bash
set -euo pipefail
cd /workspace/scratch/a72f2bd378f1/continual-research-takehome
exec taskset -c 4 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 /workspace/scratch/a72f2bd378f1/continual-research-takehome/tools/verify_causality.py --project /workspace/scratch/a72f2bd378f1/continual-research-takehome --strategy /workspace/scratch/a72f2bd378f1/continual-research-takehome/submission/strategy_gls_factor.py --config /workspace/scratch/a72f2bd378f1/continual-research-takehome/research/configs/C06_gls_factor.json --out /workspace/scratch/a72f2bd378f1/continual-research-takehome/evidence/C06_causality_C_002 --days 2016 --cuts 275 1008 2015 --prefix-days 2015 --append-days 64 --timeout-seconds 600
