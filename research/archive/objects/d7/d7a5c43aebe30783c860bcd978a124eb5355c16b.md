# Causal adaptive forecast mixing and equal-weight-loss control

This branch owns M and M0 only. After run.py --prepare, invoke run.py/e2e.py with --model M or --model M0. Other families are deliberately absent; the factory imports them only if explicitly requested. Reproduce the complete ten-job assessment on research-parallel10-plan-20261029; the injected network check is not applicable here.

M scores 1.493494747 and M0 1.493150511, both below the fixed 50/50 G ensemble at 1.533215561. These are supervised loss-trained mixtures, not RL agents. The frozen shrinkage, fit schedule and weight bounds were not retuned. Neither specification is promoted; main is unchanged.
