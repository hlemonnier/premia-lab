"""Wave 4 Block 3: distribution of realized beta (and net Sharpe) over 20-year future paths by
stationary block bootstrap (mean block 63, 2,000 paths, seed 20261029), from scored daily rows.
python research/v3/wave4_beta_bootstrap.py ROWS.npy [ROWS2.npy ...]"""
import json, sys
import numpy as np
def paths(n, length=5040, mean_block=63, draws=2000, seed=20261029):
    rng = np.random.default_rng(seed); out = np.empty((draws, length), dtype=np.int64)
    for d in range(draws):
        i = 0
        while i < length:
            s = rng.integers(0, n); L = min(rng.geometric(1 / mean_block), length - i)
            out[d, i:i + L] = (s + np.arange(L)) % n; i += L
    return out
res = {}
for f in sys.argv[1:]:
    r = np.load(f); net = r[:, 0] - r[:, 1]; m = r[:, 3]
    idx = paths(len(net)); N, M = net[idx], m[idx]
    Mc = M - M.mean(1, keepdims=True)
    b = ((N - N.mean(1, keepdims=True)) * Mc).sum(1) / (Mc ** 2).sum(1)
    sh = np.sqrt(252) * N.mean(1) / N.std(1)
    res[f.split("/")[-1]] = {"beta_in_sample": float(np.cov(net, m)[0, 1] / m.var(ddof=1)), "beta_p50": float(np.median(b)),
                             "beta_p95": float(np.percentile(b, 95)), "beta_p99": float(np.percentile(b, 99)), "P_beta_gt_0.2": float((b > 0.2).mean()),
                             "sharpe_p5": float(np.percentile(sh, 5)), "sharpe_p50": float(np.median(sh)), "sharpe_p95": float(np.percentile(sh, 95))}
print(json.dumps(res, indent=1))
