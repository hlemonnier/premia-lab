"""Do the characteristic premia drift, or is the apparent change noise?

Null: each of the 26 joint factor-return series (F26: daily slopes of residual
returns on the standardized day t-1 basis) has a constant mean. Statistic:
for each factor, the between-segment variance of means over 6 equal ~2.3-year
segments, scaled by the within-segment sampling variance (approx chi2 with 5 df
under an iid null). Total = sum over factors. Null distribution: shuffle
63-day blocks of the *whole 26-vector* across time (keeps cross-factor
correlation and short-range dependence, destroys slow mean drift).
"""
import numpy as np
from common import NAMES
F = np.load("out/F26.npy")[253:3779]
names = NAMES + [n + "^2" for n in NAMES]
T, K = F.shape; S = 6

def stat(F):
    seg = np.array_split(F, S); n = np.array([len(s) for s in seg])
    means = np.stack([s.mean(axis=0) for s in seg]); var = np.stack([s.var(axis=0, ddof=1) for s in seg])
    grand = (means * n[:, None]).sum(axis=0) / n.sum()
    return (((means - grand) ** 2) / (var / n[:, None])).sum(axis=0)  # per factor

obs = stat(F)
L = 63; blocks = [F[i:i + L] for i in range(0, T - T % L, L)]
rng = np.random.default_rng(0); null = []
for _ in range(5000):
    null.append(stat(np.concatenate([blocks[j] for j in rng.permutation(len(blocks))])))
null = np.array(null)
p_each = (null >= obs).mean(axis=0)
print(f"total statistic {obs.sum():.1f}; block-shuffle null mean {null.sum(1).mean():.1f}; p = {(null.sum(1) >= obs.sum()).mean():.4f}")
print(f"linear only: {obs[:13].sum():.1f} vs null {null[:,:13].sum(1).mean():.1f}, p = {(null[:,:13].sum(1) >= obs[:13].sum()).mean():.4f}")
print(f"squares only: {obs[13:].sum():.1f} vs null {null[:,13:].sum(1).mean():.1f}, p = {(null[:,13:].sum(1) >= obs[13:].sum()).mean():.4f}")
print("factors with p < 0.05:", [(names[k], round(p_each[k], 3)) for k in np.argsort(p_each) if p_each[k] < 0.05])
# Is the overall premium vector stable even if individual ones wander? share of
# full-sample mean explained by each segment's mean vector (cosine similarity)
seg = np.array_split(F, S); g = F.mean(axis=0)
print("cosine(segment mean, full-sample mean):", [round(float(s.mean(0) @ g / np.linalg.norm(s.mean(0)) / np.linalg.norm(g)), 2) for s in seg])
