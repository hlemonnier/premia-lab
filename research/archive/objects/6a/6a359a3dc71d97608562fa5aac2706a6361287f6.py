"""Claude's GLS review runner: python run_gls.py NAME SLEEVE RIDGE BLEND (imports handoff_gls unchanged)."""
import importlib.util, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "handoff_gls"))
import gls_alpha as G  # noqa: E402
name, sleeve, ridge, blend = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
D = "/home/claude/data/Quant Research Take-Home"
R = np.ascontiguousarray(pd.read_csv(f"{D}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{D}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
c = pd.read_csv(f"{D}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)

class P(G.CandidatePolicy):
    def forecast(self, returns_history, characteristics_history):
        base = G.FactorPolicy.forecast(self, returns_history, characteristics_history)
        out, self.learner_records = G.gls_forecast(returns_history, characteristics_history, base, {**self.cfg, "ridge": ridge})
        n = np.shape(returns_history)[1]
        if blend != 0.5:                                   # out = .5 F2 + .5 GLS on rows >= 253; recover GLS and reblend
            gls = 2 * out - base[:, :n]
            out = np.where(np.arange(len(out))[:, None] >= 253, blend * gls + (1 - blend) * base[:, :n], base[:, :n])
        self.forecast_output = np.hstack([out, base[:, n:]])
        return self.forecast_output

pol = P(); pol.sleeve = sleeve
spec = importlib.util.spec_from_file_location("score", "/home/claude/continual-research-takehome/source/Quant Research Take-Home/score.py")
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
shim = type("S", (), {"forecast": staticmethod(pol.forecast), "rebalance": staticmethod(pol.rebalance)})
rows, fsec = score.run(shim, R, X, c)
net = rows[:, 0] - rows[:, 1]; m = rows[:, 3]; b = float(np.cov(net, m)[0, 1] / m.var(ddof=1)); t = 253 + np.arange(len(net))
sh = lambda x: float(np.sqrt(252) * x.mean() / x.std())
out = {"name": name, "sleeve": sleeve, "ridge": ridge, "blend": blend, "net_sharpe": sh(net), "beta": b,
       "market_var_share": float(b * b * m.var() / net.var()), "ann_vol": float(np.sqrt(252) * net.std()), "mean_gross": float(rows[:, 2].mean()),
       "ann_fee": float(252 * rows[:, 1].mean()), "stages": [sh(net[(t >= a) & (t < z)]) for a, z in ((253, 2016), (2016, 3024), (3024, 3779))],
       "forecast_s": fsec, "rebalance_ms": float(1e3 * rows[:, 4].mean()), "certs": sorted({x["status"] for x in pol.certificates})}
np.save(os.path.join(HERE, "out", f"{name}_rows.npy"), rows); json.dump(out, open(os.path.join(HERE, "out", f"{name}.json"), "w"), indent=1)
print(json.dumps(out), flush=True)
