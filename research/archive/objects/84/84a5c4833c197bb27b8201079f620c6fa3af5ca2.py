"""Paired comparison of each scored variant against C09 on the same days.

Sharpe difference over the full scored run with a moving-block bootstrap
(63-day blocks, 2,000 draws, same resampled days for both series), plus
the per-period Sharpe. Descriptive: every period has now been looked at.
"""
import glob
import json
import os

import numpy as np

from common import STAGES, sharpe

OUT = "/home/claude/explore/out"
base = np.load(f"{OUT}/net_C09_engine.npy")
day, b = base[0], base[1]
rng = np.random.default_rng(20261027)
n = len(b); L = 63; nb = int(np.ceil(n / L))
starts = rng.integers(0, n - L, size=(2000, nb))
idx = (starts[:, :, None] + np.arange(L)).reshape(2000, -1)[:, :n]


def sr_rows(x):  # Sharpe of each bootstrap row
    return np.sqrt(252) * x.mean(axis=1) / x.std(axis=1)


rows = []
for p in sorted(glob.glob(f"{OUT}/net_*.npy")):
    name = os.path.basename(p)[4:-4]
    v = np.load(p)
    assert np.array_equal(v[0], day)
    x = v[1]
    d = sr_rows(x[idx]) - sr_rows(b[idx])
    meta = json.load(open(f"{OUT}/variant_{name}.json"))
    rows.append((name, sharpe(x), sharpe(x) - sharpe(b), np.percentile(d, 2.5), np.percentile(d, 97.5),
                 float(np.mean(d > 0)),
                 *[sharpe(x[(day >= a) & (day < c)]) for a, c in STAGES.values()],
                 meta["all"]["cost_pct"], meta["all"]["beta"], meta["rebalance_ms"]))
rows.sort(key=lambda r: -r[1])
hdr = f"{'variant':16s} {'Sharpe':>6} {'diff':>6} {'95% boot range':>17} {'P(>0)':>6} {'disc':>6} {'val':>6} {'audit':>6} {'cost%':>6} {'beta':>6} {'ms':>5}"
print(hdr)
for r in rows:
    print(f"{r[0]:16s} {r[1]:6.3f} {r[2]:+6.3f} [{r[3]:+6.3f},{r[4]:+6.3f}] {r[5]:6.2f} {r[6]:6.3f} {r[7]:6.3f} {r[8]:6.3f} {r[9]:6.2f} {r[10]:6.3f} {r[11]:5.1f}")
json.dump([dict(zip(["variant", "sharpe", "diff", "lo", "hi", "p_pos", "disc", "val", "audit", "cost_pct", "beta", "ms"], r)) for r in rows],
          open(f"{OUT}/comparison.json", "w"), indent=1)
