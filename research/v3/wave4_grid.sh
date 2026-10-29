#!/bin/bash
# Block 2 grid then Block 3 cost stress, sequentially on CPU 0.
cd "$(dirname "$0")/../.."
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
D="/home/claude/data/Quant Research Take-Home"
for frs in 0.3 0.2 0.5; do for ch in 20 10 40 80; do
  taskset -c 0 python3 research/v3/wave4_grid.py --data "$D" --ch $ch --frs $frs
done; done
for cm in 1.5 2; do taskset -c 0 python3 research/v3/wave4_grid.py --data "$D" --ch 20 --frs 0.3 --cost-mult $cm; done
echo "exit $?"
