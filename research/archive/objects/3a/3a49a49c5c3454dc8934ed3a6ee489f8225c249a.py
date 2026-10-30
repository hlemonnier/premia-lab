"""Altered-future check on the real data, the way the brief describes it:
rerun forecast with every row from `cut` onward replaced, and require rows
< cut to be bitwise identical. Also tries a truncated history and an
altered copy in Fortran memory layout. Usage: python causality_check.py VARIANT"""
import sys

import numpy as np

import variants as V
from common import load

name = sys.argv[1]
R, X, c = load()
X = np.asarray(X, dtype=np.float64)
fc = V.VARIANTS[name]().forecast
base = fc(returns_history=R, characteristics_history=X)
rng = np.random.default_rng(7)
ok = True
for cut in (400, 1500, 3024, 3700):
    R2 = R.copy(); X2 = X.copy()
    R2[cut:] = rng.normal(0, 0.03, R2[cut:].shape); X2[cut:] = rng.normal(0, 1, X2[cut:].shape)
    for label, args in (("altered", (R2, X2)), ("altered_F_layout", (np.asfortranarray(R2), X2)),
                        ("truncated", (R[:cut], X[:cut]))):
        out = fc(returns_history=args[0], characteristics_history=args[1])
        # Row `cut` uses information through cut-1, so it must be unchanged too
        # when inputs change from row `cut` on (truncated output stops before it).
        upto = cut if label == "truncated" else cut + 1
        same = np.array_equal(base[:upto], out[:upto])
        moved = label == "truncated" or not np.array_equal(base[cut + 1:cut + 50], out[cut + 1:cut + 50])
        ok &= same and moved
        print(f"cut {cut:4d} {label:17s} rows<=cut identical: {same}   later rows respond: {moved}", flush=True)
print("PASS" if ok else "FAIL")
