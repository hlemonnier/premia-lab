"""EXPLICIT_BETA_PLAN.md pre-execution diagnostic: do causally corrected betas predict
realized next-252-day betas better than raw trailing betas? Past-only eta at each date."""
import json, os, sys
import numpy as np, pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "handoff_v2"))
from model_v2.engine import _EtaTracker, _window_beta, _correct  # noqa: E402
R = np.ascontiguousarray(pd.read_csv(f"{sys.argv[1]}/returns.csv", index_col="day").to_numpy(np.float64))
T = len(R); tr = _EtaTracker(); rows = []
for t in range(504, T - 252, 21):                  # dates where a corrected beta exists and the future window completes
    eta = tr.eta(R, t)
    raw = _window_beta(R[:t]); cor = _correct(raw, eta); post = _window_beta(R[t:t + 252])
    rows.append((t, eta, np.mean((raw - post) ** 2), np.mean((cor - post) ** 2)))
a = np.array(rows)
out = {"dates": len(a), "eta_first": a[0, 1], "eta_last": a[-1, 1], "mse_raw": a[:, 2].mean(), "mse_corrected": a[:, 3].mean(),
       "share_of_dates_corrected_better": float(np.mean(a[:, 3] < a[:, 2]))}
json.dump(out, open(os.path.join(ROOT, "research/v2/results/beta_correction_diagnostic.json"), "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
