#!/usr/bin/env bash
set -euo pipefail
diagnostic_rerun_dir="${1:-$(mktemp -d /tmp/continual-alpha-rerun-XXXXXX)}"
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python /workspace/scratch/305f831f543f/continual_takehome/evidence/alpha_diagnostics_001/runner_used.py --project-root /workspace/scratch/305f831f543f/continual_takehome --output "$diagnostic_rerun_dir"
