"""25,200-row one-CPU runtime/state check for handoff_v3 with the original scorer.
Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 (and taskset -c 0 if available).
python verification/v3_runtime_check.py --data DIR [--sleeve 0.05]
"""
import argparse, importlib.util, json, os, sys, time
import numpy as np, pandas as pd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
import strategy as S  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--sleeve", type=float, default=0.05); a = ap.parse_args()
S.POLICY.sleeve = a.sleeve
spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
c = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
reps = int(np.ceil(25200 / len(R)))
RT = np.ascontiguousarray(np.tile(R, (reps, 1))[:25200]); XT = np.ascontiguousarray(np.tile(X, (reps, 1, 1))[:25200])
t0 = time.perf_counter(); rows, fsec = score.run(S, RT, XT, c); wall = time.perf_counter() - t0
st = {x["status"] for x in S.POLICY.certificates}
out = {"rows": int(len(rows)), "forecast_s": fsec, "forecast_h_per_century": fsec / 3600, "rebalance_ms_mean": 1e3 * float(rows[:, 4].mean()),
       "rebalance_ms_p99": 1e3 * float(np.percentile(rows[:, 4], 99)), "rebalance_ms_max": 1e3 * float(rows[:, 4].max()),
       "wall_s": wall, "certificate_statuses": sorted(st), "min_one_plus_gross_return": float(1 + rows[:, 0].min()),
       "pass": bool(rows[:, 4].mean() < 0.1 and fsec < 3600)}
print(json.dumps(out, indent=1))
sys.exit(0 if out["pass"] else 1)
