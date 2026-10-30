"""Prespecified descriptive paired comparison of two existing replay ledgers."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parent
paths = [root / 'run_c09_003/daily.csv', root / 'run_v2_001/daily.csv']
dfs = [pd.read_csv(p) for p in paths]
assert np.array_equal(dfs[0].return_index, dfs[1].return_index)
assert np.array_equal(dfs[0].return_index, np.arange(253, 3779))
b, x = [d.net_return.to_numpy() for d in dfs]
n = len(b)


def sr(a, axis=None):
    return np.sqrt(252) * a.mean(axis=axis) / a.std(axis=axis)


out = {'inputs': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
       'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'plan_sha256': hashlib.sha256((root / 'PAIRED_READBACK_PLAN.md').read_bytes()).hexdigest(),
       'argv': sys.argv, 'n': n, 'net_correlation': float(np.corrcoef(b, x)[0, 1]),
       'observed_sharpe_difference': float(sr(x) - sr(b)), 'intervals': []}
for L, corrected in [(63, False), (63, True), (21, True), (126, True)]:
    rng = np.random.default_rng(20261027)
    nb = int(np.ceil(n / L))
    starts = rng.integers(0, n - L + int(corrected), size=(2000, nb))
    idx = (starts[:, :, None] + np.arange(L)).reshape(2000, -1)[:, :n]
    diff = sr(x[idx], axis=1) - sr(b[idx], axis=1)
    assert np.isfinite(diff).all()
    out['intervals'].append(dict(block_length=L, corrected_endpoint=corrected,
        draws=2000, seed=20261027, percentile_95=np.percentile(diff, [2.5, 97.5]).tolist(),
        resampled_positive_fraction=float((diff > 0).mean())))
out['stage_sharpe_differences'] = {}
day = dfs[0].return_index.to_numpy()
for name, lo, hi in [('discovery',253,2015),('validation',2016,3023),('audit',3024,3779)]:
    mask = (day >= lo) & (day < hi)
    out['stage_sharpe_differences'][name] = float(sr(x[mask]) - sr(b[mask]))
(root / 'paired_readback.json').write_text(json.dumps(out, indent=2, allow_nan=False) + '\n')
print(json.dumps(out, indent=2, allow_nan=False))
