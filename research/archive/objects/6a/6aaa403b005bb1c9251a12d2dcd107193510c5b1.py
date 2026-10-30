"""Claude's check of GPT's F: reproduce F, then F and T without the sleeve, plus a constant-level control.
python run_check.py VARIANT SLEEVE   (VARIANT in F, T, Flevel, Tlevel)"""
import importlib.util, json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "handoff_f"))
from model_f import factor_risk as FR  # noqa: E402
variant, sleeve = sys.argv[1], float(sys.argv[2])
D = "/home/claude/data/Quant Research Take-Home"
R = np.ascontiguousarray(pd.read_csv(f"{D}/returns.csv", index_col="day").to_numpy(np.float64))
X = np.ascontiguousarray(pd.read_csv(f"{D}/characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(R.shape[0], R.shape[1], 13))
c = pd.read_csv(f"{D}/costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
LEVEL = json.load(open(os.path.join(HERE, "out", "levels.json"))) if variant.endswith("level") else None

class Check(FR.FactorPolicy):
    def forecast(self, returns_history, characteristics_history):
        alpha = FR.P.ScorePolicy.forecast(self, returns_history, characteristics_history)
        T, N = np.shape(returns_history)
        cx, cy, fx, fy = FR.sufficient_statistics(returns_history, characteristics_history, self.cfg)
        common = np.ones(T); factor = np.ones((T, 26))
        if variant == "F":
            factor, _ = FR.fitted_multipliers(fx, fy)
        elif variant == "T":
            common, _ = FR.fitted_multipliers(cx, cy); factor = np.repeat(common[:, None], 26, axis=1)
        elif variant == "Flevel":          # diagnostic: F's full-sample mean multiplier per factor, constant from row 253
            factor[253:] = np.array(LEVEL["F_mean_by_factor"])
        elif variant == "Tlevel":          # diagnostic: T's full-sample mean common multiplier, constant from row 253
            common[253:] = LEVEL["T_mean"]; factor[253:] = LEVEL["T_mean"]
        self.mult_common, self.mult_factor = common, factor
        self.virtual = FR._RescaledBook(self.cfg, N); self.inner = FR._RescaledBook(self.cfg, N)
        self.forecast_output = np.hstack([alpha, common[:, None], factor])
        return self.forecast_output

pol = Check(); pol.sleeve = sleeve
spec = importlib.util.spec_from_file_location("score", "/home/claude/continual-research-takehome/source/Quant Research Take-Home/score.py")
score = importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
shim = type("S", (), {"forecast": staticmethod(pol.forecast), "rebalance": staticmethod(pol.rebalance)})
rows, fsec = score.run(shim, R, X, c)
net = rows[:, 0] - rows[:, 1]; m = rows[:, 3]; b = float(np.cov(net, m)[0, 1] / m.var(ddof=1))
out = {"variant": variant, "sleeve": sleeve, "net_sharpe": float(np.sqrt(252) * net.mean() / net.std()), "beta": b,
       "market_var_share": float(b * b * m.var() / net.var()), "ann_vol": float(np.sqrt(252) * net.std()), "mean_gross": float(rows[:, 2].mean()),
       "ann_fee": float(252 * rows[:, 1].mean()), "mean_common_mult": float(pol.mult_common[253:3779].mean()),
       "mean_factor_mult": float(pol.mult_factor[253:3779].mean()), "certs": sorted({x["status"] for x in pol.certificates})}
if variant in ("F", "T") and sleeve == 0.05:
    lv = json.load(open(os.path.join(HERE, "out", "levels.json"))) if os.path.exists(os.path.join(HERE, "out", "levels.json")) else {}
    if variant == "F": lv["F_mean_by_factor"] = pol.mult_factor[253:3779].mean(0).tolist()
    if variant == "T": lv["T_mean"] = float(pol.mult_common[253:3779].mean())
    json.dump(lv, open(os.path.join(HERE, "out", "levels.json"), "w"))
np.save(os.path.join(HERE, "out", f"{variant}_sl{sleeve:g}_rows.npy"), rows)
json.dump(out, open(os.path.join(HERE, "out", f"{variant}_sl{sleeve:g}.json"), "w"), indent=1)
print(json.dumps(out), flush=True)
