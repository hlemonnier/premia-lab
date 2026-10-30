"""Run packaged V2 with configuration overrides through the unmodified scorer.

python research/v2/run_candidate.py --data DIR --name NAME --set key=value [...]
Writes results/candidates/NAME.json and results/ledgers/net_NAME.npy (day, net, gross, cost, market).
"""
import argparse, importlib.util, json, os, sys, time
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
import strategy as V2  # noqa: E402
from model_v2 import engine  # noqa: E402
STAGES = {"full": (253, 3779), "discovery": (253, 2015), "validation": (2016, 3023), "audit": (3024, 3779)}
ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--name", required=True)
ap.add_argument("--set", nargs="*", default=[]); a = ap.parse_args()
over = {}
for kv in a.set:
    k, v = kv.split("="); over[k] = json.loads(v)
engine.configure({**V2._CONFIG, **over})
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
c = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy()
spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
netdollars = []
def reb(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
    w = engine.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
    netdollars.append(float(np.sum(w))); return w
shim = type("S", (), {"forecast": staticmethod(engine.forecast), "rebalance": staticmethod(reb)})
t0 = time.time(); rows, fsec = score.run(shim, R, X, c)
pr, cost, gross, mkt, sec = rows.T; net = pr - cost; day = 253 + np.arange(len(rows))
out = {"name": a.name, "overrides": over, "forecast_s": fsec, "rebalance_ms": 1e3 * sec.mean(), "wall_s": time.time() - t0,
       "certificates": {s: sum(1 for x in engine.CERTIFICATES if x.get("status") == s) for s in ("ok", "ok_after_recovery", "not_certified")},
       "mean_net_dollars": float(np.mean(netdollars))}
for s, (lo, hi) in STAGES.items():
    k = (day >= lo) & (day < hi); mc = mkt[k] - mkt[k].mean()
    out[s] = {"sharpe": float(np.sqrt(252) * net[k].mean() / net[k].std()), "ret_pct": 100 * 252 * net[k].mean(),
              "vol_pct": 100 * np.sqrt(252) * net[k].std(), "cost_pct": 100 * 252 * cost[k].mean(),
              "beta": float(mc @ (net[k] - net[k].mean()) / (mc @ mc)), "gross": float(gross[k].mean())}
os.makedirs(os.path.join(ROOT, "research/v2/results/candidates"), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, f"research/v2/results/candidates/{a.name}.json"), "w"), indent=1)
np.save(os.path.join(ROOT, f"research/v2/results/ledgers/net_{a.name}.npy"), np.vstack([day, net, pr, cost, mkt]))
print(json.dumps(out, indent=1))
