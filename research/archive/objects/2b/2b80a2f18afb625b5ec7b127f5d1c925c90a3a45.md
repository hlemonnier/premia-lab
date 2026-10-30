# Robust GLS responses versus coherent date attenuation

This branch owns R and R0 only. After run.py --prepare, invoke run.py/e2e.py with --model R or --model R0. Other model families are intentionally absent; the lazy factory imports only the selected pair. The complete ten-job assessment is reproduced on research-parallel10-plan-20261029. The network injection check is not applicable on this branch.

R scores 1.535659977 versus G 1.533215561 and R0 1.533020223. Its gain is below the preregistered threshold and it loses in two stages and the first half. The primary is rejected without retuning clipping, ridge or blend. Main remains unchanged.
