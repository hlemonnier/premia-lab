"""Descriptive attribution of the two actually executed frozen portfolios."""
from pathlib import Path
import hashlib
import json
import numpy as np


HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run():
    result_path = HERE / "actual_001/result.json"
    result = json.loads(result_path.read_text())
    assert result["all_passed"] and result["source_unchanged"]
    a, b = (result["results"][n] for n in ("M0", "M1"))
    assert a["outer_cap_count"] == b["outer_cap_count"] == 0
    data = {}
    manifest = {}
    for name, summary in (("M0", a), ("M1", b)):
        data[name] = {}
        manifest[name] = {}
        for key in ("rows", "targets"):
            spec = summary["array_manifest"][key]
            path = Path(spec["path"])
            array = np.load(path, allow_pickle=False)
            assert digest(path) == spec["sha256"]
            assert hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest() == spec["array_sha256"]
            assert list(array.shape) == spec["shape"] and str(array.dtype) == spec["dtype"]
            data[name][key] = array
            manifest[name][key] = spec
    row0, row1 = data["M0"]["rows"], data["M1"]["rows"]
    assert np.array_equal(row0[:, 3], row1[:, 3])
    market = row0[:, 3]
    target_delta = data["M1"]["targets"]-data["M0"]["targets"]
    gross_delta = row1[:, 0]-row0[:, 0]
    cost_delta = row1[:, 1]-row0[:, 1]
    net_delta = (row1[:, 0]-row1[:, 1])-(row0[:, 0]-row0[:, 1])
    errors = {
        "target_increment_max_error": float(np.max(np.abs(target_delta-.05/target_delta.shape[1]))),
        "gross_increment_max_error": float(np.max(np.abs(gross_delta-.05*market))),
        "net_increment_max_error": float(np.max(np.abs(net_delta-(.05*market-cost_delta)))),
    }
    assert max(errors.values()) < 1e-12
    days = np.arange(253, 253+len(market))
    segments = {"full": (253, 3779), "discovery": (253, 2015),
                "validation": (2016, 3023), "audit": (3024, 3779)}
    attribution = {}
    for name, (lo, hi) in segments.items():
        ix = (days >= lo) & (days < hi)
        m = market[ix]-market[ix].mean()
        fee_beta = float(m@(cost_delta[ix]-cost_delta[ix].mean())/(m@m))
        measured_net_beta_delta = b["performance"][name]["net_beta"]-a["performance"][name]["net_beta"]
        attribution[name] = {
            "n": int(ix.sum()),
            "gross_increment_ann_percentage_points": float(25200*gross_delta[ix].mean()),
            "market_005_ann_percentage_points": float(25200*.05*market[ix].mean()),
            "incremental_actual_cost_ann_percentage_points": float(25200*cost_delta[ix].mean()),
            "incremental_actual_cost_ann_bps": float(2520000*cost_delta[ix].mean()),
            "net_increment_ann_percentage_points": float(25200*net_delta[ix].mean()),
            "incremental_cost_market_slope": fee_beta,
            "net_beta_increment": measured_net_beta_delta,
            "net_beta_identity_error": abs(measured_net_beta_delta-(.05-fee_beta)),
        }
        assert attribution[name]["net_beta_identity_error"] < 1e-12
    report = {
        "type": "descriptive_actual_book_difference_no_new_candidate",
        "scope_sha256": digest(HERE / "ATTRIBUTION_SCOPE.md"),
        "script_sha256": digest(__file__), "result_sha256": digest(result_path),
        "source_arrays": manifest, "no_gross_cap_binding": True,
        "daily_identity_errors": errors, "segments": attribution,
        "interpretation": "M1's added gross return is the executed fixed market basket. Its incremental net return subtracts the actual combined-book fee difference. Unchanged inner targets/forecasts imply no new stock-selection or market-timing alpha is claimed. Incremental fees are not a standalone sleeve-cost estimate."
    }
    destination = HERE / "actual_book_attribution.json"
    destination.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"daily_identity_errors": errors, "segments": attribution}, indent=2))


if __name__ == "__main__":
    run()
