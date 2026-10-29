"""Paired moving-block bootstrap of net Sharpe differences vs V3 (2,000 draws, 63-day blocks,
seed 20261029), as pre-registered in WAVE3_PLAN. python research/v3/wave3_bootstrap.py"""
import json, os
import numpy as np
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
net = lambda r: r[:, 0] - r[:, 1]
sh = lambda x: np.sqrt(252) * x.mean(-1) / x.std(-1)
base = net(np.load(f"{D}/V3_rows.npy")); n = len(base); L = 63
rng = np.random.default_rng(20261029)
idx = np.concatenate([(s[:, None] + np.arange(L)).reshape(-1) for s in [rng.integers(0, n - L + 1, size=-(-n // L)) for _ in range(2000)]]).reshape(2000, -1)[:, :n]
out = {}
for v in ("M2", "H1"):
    x = net(np.load(f"{D}/{v}_rows.npy")); dif = sh(x[idx]) - sh(base[idx])
    out[v] = {"observed_diff": float(sh(x) - sh(base)), "ci95": [float(np.percentile(dif, 2.5)), float(np.percentile(dif, 97.5))],
              "share_draws_positive": float((dif > 0).mean())}
print(json.dumps(out, indent=1)); json.dump(out, open(f"{D}/wave3_bootstrap.json", "w"), indent=1)
