"""Wave 4 Block 2 grid: cost_horizon x factor_risk_scale on V3 (both books). Also runs the
Block 3 cost stress (--cost-mult). python research/v3/wave4_grid.py --data DIR --ch 20 --frs 0.3 [--cost-mult 1]"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wave3 as W  # noqa: E402
ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--ch", type=float, required=True)
ap.add_argument("--frs", type=float, required=True); ap.add_argument("--cost-mult", type=float, default=1.0); ap.add_argument("--sleeve", type=float, default=0.05)
a = ap.parse_args()
R, X, c = W.load(a.data)
import strategy  # noqa: E402,F401
cfg = {**dict(W.E.CONFIG), "cost_horizon": a.ch, "factor_risk_scale": a.frs}
pol = W.ScorePolicy(cfg, sleeve=a.sleeve, outer_gross_cap=5.0)
rows, fsec = W.score_policy(pol, R, X, c * a.cost_mult)
s = W.summary(rows); s.update({"cost_horizon": a.ch, "factor_risk_scale": a.frs, "cost_mult": a.cost_mult, "sleeve": a.sleeve,
                               "cert_statuses": sorted({x["status"] for x in pol.certificates})})
name = f"grid_ch{a.ch:g}_frs{a.frs:g}_cm{a.cost_mult:g}_sl{a.sleeve:g}"
out = os.path.join(HERE, "results", "wave4"); os.makedirs(out, exist_ok=True)
np.save(os.path.join(out, name + "_rows.npy"), rows); json.dump(s, open(os.path.join(out, name + ".json"), "w"), indent=1)
print(name, round(s["net_sharpe"], 6), round(s["beta"], 4), round(s["ann_fee"] * 100, 4), flush=True)
