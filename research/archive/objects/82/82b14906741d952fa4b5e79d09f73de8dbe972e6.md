# Residual co-movement versus matched extra marginal risk

This branch owns C and C0 only. After run.py --prepare, invoke run.py/e2e.py with --model C or --model C0. Other families are absent and lazily imported only when requested. The full batch assessment belongs to research-parallel10-plan-20261029; the injected network check is not applicable on this branch.

C scores 1.469265806 versus matched-diagonal C0 at 1.533057030 and selected G at 1.533215561. The bounded PSD low-rank addition fails the fixed criterion despite estimated residual modes. No rank, threshold, strength or covariance subtraction was tuned after outcomes. No new model is promoted and main stays untouched.
