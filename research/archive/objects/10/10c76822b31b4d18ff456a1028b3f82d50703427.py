"""Read-only audit of frozen synthetic evidence, without policy execution."""
from pathlib import Path
import hashlib
import json
import numpy as np


HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent / "v2_score2_execution_20261029"
RUN = EVIDENCE / "e2e_001"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def raw_digest(array):
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def declared_fixture(n=64):
    """Recreate the saved prospective input specification, not any policy."""
    rng = np.random.default_rng(20261028)
    x = np.empty((420, n, 13), dtype=np.float64)
    x[0] = rng.normal(size=(n, 13))
    for t in range(1, 420):
        x[t] = .92 * x[t-1] + np.sqrt(1-.92**2) * rng.normal(size=(n, 13))
    beta = rng.uniform(.7, 1.3, n)
    market = .0003 + .006 * rng.normal(size=420)
    returns = np.empty((420, n))
    for t in range(420):
        z = x[max(0, t-1)]
        scale = .6 if t < 330 else 2.
        returns[t] = (beta*market[t] + .00008*z[:, 0] + .00006*(z[:, 1]**2-1)
                      + scale*(.0015*z[:, 2]*rng.normal() + .008*rng.normal(size=n)))
    return returns, x, np.linspace(.0001, .0005, n)


def run():
    scope = json.loads((HERE / "execution_readback_scope.json").read_text())
    assert digest(RUN / "result.json") == scope["result_sha256"]
    result = json.loads((RUN / "result.json").read_text())
    prior = json.loads((HERE / "execution_source_review.json").read_text())
    assert result["all_passed"] and all(result["checks"].values())
    for name, expected in result["source_files"].items():
        assert digest(EVIDENCE / name) == digest(RUN / name) == expected
        assert prior["source_sha256"][name] == expected
    for name, expected in result["source_hashes"].items():
        assert digest(RUN / "source" / name) == expected
    artifacts = json.loads((RUN / "artifact_manifest.json").read_text())
    for name, expected in artifacts.items():
        assert digest(RUN / name) == expected, name

    returns, x, costs = declared_fixture()
    inputs = json.loads((RUN / "input_manifest.json").read_text())
    assert [list(returns.shape), list(x.shape)] == inputs["shapes"]
    for name, a in (("R", returns), ("X", x), ("costs", costs)):
        assert raw_digest(a) == inputs[name]
    future = returns.copy()
    future[360:] = np.random.default_rng(20261029).normal(0, .015, size=future[360:].shape)
    extreme, _, extreme_costs = declared_fixture(128)
    arrays = {}
    observed = {}
    verified = 0
    for verification_path in sorted(RUN.glob("*/verification.json")):
        folder = verification_path.parent
        name = folder.name
        verification = json.loads(verification_path.read_text())
        saved = {}
        for filename, spec in verification["arrays"].items():
            path = folder / filename
            a = np.load(path, allow_pickle=False)
            assert digest(path) == spec["file_sha256"]
            assert raw_digest(a) == spec["array_sha256"]
            assert list(a.shape) == spec["shape"] and str(a.dtype) == spec["dtype"]
            assert spec["verified"]
            saved[filename] = a
            verified += 1
        arrays[name] = saved
        r, c = returns, costs
        if name.endswith("_future"):
            r = future
        elif name.endswith("_prefix"):
            r = returns[:361]
        elif name.endswith("_zero_returns"):
            r = np.zeros_like(returns)
        elif name.endswith("_extreme"):
            r, c = extreme, extreme_costs
        if name.endswith("_zero_cost") or name == "zero_cost_reference":
            c = np.zeros_like(c)
        targets, rows = saved["targets.npy"], saved["rows.npy"]
        assert targets.shape == (len(r)-253, r.shape[1])
        assert rows.shape == (len(r)-254, 5)
        previous = targets[:-1]
        earning_returns = r[253:-1]
        # Independent vectorized reconstruction; the policy/harness reconstruct
        # incrementally. Accumulation-order discrepancies remain reported.
        gross_return = np.sum(previous*earning_returns, axis=1)
        assert np.min(gross_return) > -1
        held = previous*(1+earning_returns)/(1+gross_return[:, None])
        full_cost = np.sum(np.abs(targets[1:]-held)*c, axis=1)
        reconstruction = np.column_stack((gross_return, full_cost,
                                         np.sum(np.abs(targets[1:]), axis=1),
                                         earning_returns.mean(axis=1)))
        errors = np.max(np.abs(reconstruction-rows[:, :4]), axis=0)
        assert np.max(errors) <= 1e-12
        observed[name] = {"n_decisions": len(targets), "n_earning_rows": len(rows),
                          "max_column_errors_g_cost_gross_market": errors.tolist(),
                          "max_gross": float(np.abs(targets).sum(axis=1).max()),
                          "final_decision_index": len(r)-2}

    differences = {}
    for mode in ("E1", "E2"):
        base = arrays[mode]
        assert np.array_equal(base["forecast.npy"], arrays["baseline"]["forecast.npy"])
        assert np.array_equal(base["virtual_targets.npy"], arrays["baseline"]["virtual_targets.npy"])
        assert np.array_equal(base["forecast.npy"][:361], arrays[mode+"_future"]["forecast.npy"][:361])
        assert np.array_equal(base["targets.npy"][:108], arrays[mode+"_future"]["targets.npy"][:108])
        assert np.array_equal(base["rows.npy"][:107, :4], arrays[mode+"_future"]["rows.npy"][:107, :4])
        prefix = arrays[mode+"_prefix"]
        for filename in ("forecast.npy", "targets.npy", "virtual_targets.npy"):
            assert np.array_equal(base[filename][:len(prefix[filename])], prefix[filename])
            assert np.array_equal(base[filename], arrays[mode+"_repeat"][filename])
        assert np.array_equal(base["rows.npy"][:len(prefix["rows.npy"]), :4], prefix["rows.npy"][:, :4])
        assert np.array_equal(base["rows.npy"][:, :4], arrays[mode+"_repeat"]["rows.npy"][:, :4])
        zero = arrays[mode+"_zero_cost"]
        reference = arrays["zero_cost_reference"]
        dt = float(np.max(np.abs(zero["targets.npy"]-reference["targets.npy"])))
        de = float(np.max(np.abs(zero["rows.npy"][:, :4]-reference["rows.npy"][:, :4])))
        assert dt <= 1e-8 and de <= 1e-8
        differences[mode] = {"zero_cost_target_error": dt, "zero_cost_economic_error": de,
                             "future_prefix_restart_exact": True,
                             "reference_virtual_and_forecast_exact": True}
        assert observed[mode+"_extreme"]["max_gross"] >= 5-1e-8
    math_review_path = HERE.parent / "v2_score2_forecast_20261029/execution_math_review.json"
    math_review = json.loads(math_review_path.read_text())
    assert math_review["source_sha256"]["execution.py"] == result["source_files"]["execution.py"]
    assert math_review["required_changes"] == []
    report = {"reviewer": "score2_challenge", "decision": "accepted_for_root_actual_release",
              "required_changes": [], "scope_sha256": digest(HERE / "execution_readback_scope.json"),
              "audit_script_sha256": digest(__file__), "source_review_sha256": digest(HERE / "execution_source_review.json"),
              "synthetic_result_sha256": digest(RUN / "result.json"),
              "source_files": result["source_files"], "prospective_checks_passed": len(result["checks"]),
              "artifact_files_verified": len(artifacts), "atomic_arrays_verified": verified,
              "workflows_reconstructed": observed, "independently_verified_differences": differences,
              "math_review_sha256": digest(math_review_path),
              "limitations": ["No new policy run or actual-market scoring occurred in this audit.",
                              "E2 retains ce3 post-solve proportional gross scaling; a solver certificate is not a certificate of a globally optimal gross-constrained QP.",
                              "Actual market and long-history runtime admission remain outstanding."]}
    destination = HERE / "execution_synthetic_review.json"
    destination.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: report[k] for k in ("decision", "prospective_checks_passed", "artifact_files_verified", "atomic_arrays_verified", "independently_verified_differences")}, indent=2))
    print("Maximum independent accounting discrepancy:", max(max(v["max_column_errors_g_cost_gross_market"]) for v in observed.values()))


if __name__ == "__main__":
    run()
