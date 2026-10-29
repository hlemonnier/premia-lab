#!/bin/bash
# Wave 4 addendum runs, split across two CPUs.
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
D="/home/claude/data/Quant Research Take-Home"
run() { taskset -c $1 python3 research/v3/wave4_grid.py --data "$D" --ch $2 --frs $3 --sleeve $4; }
( run 0 5 0.5 0.05; run 0 5 0.7 0.05; run 0 10 0.7 0.05; run 0 5 1.0 0.05; run 0 10 1.0 0.05; run 0 10 0.3 0 ) &
( run 1 5 0.5 0; run 1 10 0.5 0; run 1 20 0.5 0; run 1 5 0.7 0; run 1 10 0.7 0; run 1 5 1.0 0; run 1 10 1.0 0 ) &
wait; echo "exit 0"
