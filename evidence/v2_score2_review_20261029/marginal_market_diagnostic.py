"""Read-only marginal spanning diagnostic specified in PLAN.md.

Does not construct or execute a candidate portfolio or report a mixed-series
candidate score. Inputs are the already published joint daily ledger and static
per-stock costs. Gross market addition below omits its incremental actual costs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
import pandas as pd


def identity(path):
    b = path.read_bytes()
    return {"path": str(path.resolve()), "bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--costs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    ledger = pd.read_csv(a.ledger)
    costs = pd.read_csv(a.costs)["cost"].to_numpy(dtype=float)
    idx = ledger["return_index"].to_numpy(dtype=int)
    masks = {"full": np.ones(len(idx), dtype=bool),
             "discovery": (idx >= 253) & (idx < 2015),
             "validation": (idx >= 2016) & (idx < 3023),
             "audit": (idx >= 3024) & (idx < 3779)}
    results = {}
    for name, mask in masks.items():
        p = ledger.loc[mask, "net_return"].to_numpy(dtype=float)
        m = ledger.loc[mask, "market_return"].to_numpy(dtype=float)
        mp, mm = float(p.mean()), float(m.mean())
        vp, vm = float(p.var()), float(m.var())
        cov = float(np.mean((p - mp) * (m - mm)))
        # S(b)=sqrt(252)*(mu_p+b*mu_m)/sqrt(v_p+2*b*c+b*b*v_m).
        # Evaluate only the derivative at b=0. Incremental costs are excluded.
        slope = float(np.sqrt(252) * (mm*vp - mp*cov) / vp**1.5)
        results[name] = {
            "n": len(p),
            "joint_net_sharpe_reconciliation": float(np.sqrt(252)*mp/np.sqrt(vp)),
            "joint_mean_daily": mp, "market_mean_daily": mm,
            "joint_variance_daily": vp, "market_variance_daily": vm,
            "joint_market_covariance_daily": cov,
            "joint_net_beta_reconciliation": cov/vm,
            "joint_market_correlation": cov/np.sqrt(vp*vm),
            "market_mean_annual_pct": mm*25200,
            "market_vol_annual_pct": np.sqrt(vm*252)*100,
            "marginal_market_mean_threshold_annual_pct": mp*cov/vp*25200,
            "sharpe_derivative_at_zero_market_addition_ignoring_incremental_cost": slope,
            "positive_marginal_spanning_direction_before_incremental_cost": slope > 0,
        }
    out = {
        "scope": "Read-only existing-ledger marginal derivative; no new candidate score or execution",
        "command_argv": sys.argv,
        "source": identity(Path(__file__)),
        "plan": identity(Path(__file__).with_name("PLAN.md")),
        "inputs": [identity(a.ledger), identity(a.costs)],
        "results": results,
        "costs": {
            "n": len(costs), "minimum": float(costs.min()),
            "maximum": float(costs.max()), "equal_weight_oneway_cost_per_unit_notional": float(costs.mean()),
            "hypothetical_paid_005_basket_insertion_cost_bps": float(.05*costs.mean()*10000),
            "disposition": "This insertion is free at the actual first trade; subsequent fees need stock-level drift/netting replay. No annual fee estimate is inferred."
        },
        "candidate_disposition": "One fixed +0.05 sleeve proposal; no optimized weight or dynamic premium fit calculated.",
    }
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"results": results, "costs": out["costs"]}, indent=2))


if __name__ == "__main__":
    main()
