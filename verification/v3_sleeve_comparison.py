"""Score handoff_v3 with the unmodified scorer at sleeve 0.05 (packaged) and sleeve 0.0 (no market position).

python verification/v3_sleeve_comparison.py --data DIR [--report FILE]
Sleeve 0.0 should reproduce GPT's E2-alone result (net Sharpe 1.339582 in SCORE2_RESEARCH_RESULTS_20261029.md).
"""
import argparse, importlib.util, json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "handoff_v3"))
import strategy as S  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--report"); a = ap.parse_args()
spec = importlib.util.spec_from_file_location("score", os.path.join(ROOT, "source", "Quant Research Take-Home", "score.py"))
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
R = np.ascontiguousarray(pd.read_csv(f"{a.data}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{a.data}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
c = pd.read_csv(f"{a.data}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
out = {}
for sleeve in (0.05, 0.0):
    S.POLICY.sleeve = sleeve
    rows, fsec = score.run(S, R, X, c)
    net = rows[:, 0] - rows[:, 1]; m = rows[:, 3]
    beta = float(np.cov(net, m)[0, 1] / m.var(ddof=1))
    half = len(net) // 2
    sh = lambda x: float(np.sqrt(252) * x.mean() / x.std())
    out[str(sleeve)] = {"net_sharpe": sh(net), "beta": beta, "ann_return": float(252 * net.mean()), "ann_vol": float(np.sqrt(252) * net.std()),
                        "ann_cost": float(252 * rows[:, 1].mean()), "mean_gross": float(rows[:, 2].mean()),
                        "sharpe_first_half": sh(net[:half]), "sharpe_second_half": sh(net[half:]),
                        "rebalance_ms": float(1e3 * rows[:, 4].mean()), "forecast_s": fsec}
    print(sleeve, json.dumps(out[str(sleeve)]), flush=True)
if a.report:
    json.dump(out, open(a.report, "w"), indent=1)
