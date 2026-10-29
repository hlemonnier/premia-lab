"""Observational ratios under TOTAL_DEPENDENCE_SCOPE.md; no strategy execution."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "a40de33bfc14f8c84b5148617973af0332d34d2a62cae9649ec5a6740bb9c8bf"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = HERE / "mean_sensitivity_001.json"
assert sha(source) == SOURCE_SHA
out = HERE / "total_dependence_001.json"
if out.exists():
    raise RuntimeError("Preserve original output")
raw = json.loads(source.read_text())
answer = {}
for name, s in raw["published_fixed_policy_moments"].items():
    answer[name] = {
        "net_sharpe": s["net_sharpe"],
        "net_beta": s["descriptive_net_beta"],
        "market_ols_r_squared": s["market_ols_explained_variance_fraction"],
        "annual_net_mean": s["ann_arithmetic_mean"],
        "annual_beta_times_market_mean": s["beta_times_market_mean_ann"],
        "beta_times_market_mean_share_of_net_mean": s["beta_times_market_mean_ann"] / s["ann_arithmetic_mean"],
    }
result = {"source_sha256": SOURCE_SHA,
          "script_sha256": sha(Path(__file__)),
          "scope_sha256": sha(HERE / "TOTAL_DEPENDENCE_SCOPE.md"),
          "books": answer,
          "interpretation": "Ex-post OLS descriptions, not causal alpha attribution, tradable hedge results or future forecasts.",
          "no_policy_execution": True, "no_new_selection_threshold": True}
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"out": str(out), "sha256": sha(out), "books": answer}, indent=2))
