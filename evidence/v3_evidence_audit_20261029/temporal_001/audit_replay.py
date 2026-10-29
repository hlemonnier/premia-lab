"""Whole-workflow evidence capture under REPLAY_PLAN.md; unchanged policy bytes."""
from pathlib import Path
import argparse
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
import platform
import shutil
import sys
import time
import traceback

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
THREADS = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
ACCEPTED = {"ok", "ok_after_recovery", "ok_after_cold_restart", "fallback_diagonal"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def raw_sha(a):
    return hashlib.sha256(memoryview(np.ascontiguousarray(a)).cast("B")).hexdigest()


def normalize(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, Path):
        return str(x)
    raise TypeError(type(x).__name__)


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False, default=normalize) + "\n")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def save_array(path, a):
    a = np.asarray(a)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as f:
        np.save(f, a, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)
    restored = np.load(path, mmap_mode="r", allow_pickle=False)
    assert restored.shape == a.shape and restored.dtype == a.dtype
    assert raw_sha(restored) == raw_sha(a)
    return {"path": path.name, "shape": list(a.shape), "dtype": str(a.dtype),
            "file_sha256": sha(path), "array_sha256": raw_sha(a)}


def save_arrays(folder, arrays):
    folder.mkdir(exist_ok=True)
    identities = {name: save_array(folder / (name + ".npy"), a) for name, a in arrays.items()}
    dump(folder / "array_manifest.json", identities)
    return identities


def env():
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
    return {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
            "platform": platform.platform(), "pid": os.getpid(),
            "cpu_affinity": sorted(os.sched_getaffinity(0)),
            "thread_variables": {k: os.environ.get(k) for k in THREADS},
            "numpy_build_configuration": stream.getvalue()}


def verify_sources(bindings):
    for group in ("production", "research", "ce3", "inputs"):
        d = bindings[group]
        for name, expected in d["sha256"].items():
            assert sha(Path(d["root"]) / name) == expected, (group, name)
    assert sha(bindings["published_daily"]["path"]) == bindings["published_daily"]["sha256"]
    assert sha(bindings["published_array_manifest"]["path"]) == bindings["published_array_manifest"]["sha256"]


def stage(bindings, out):
    roots = {}
    for group in ("production", "research", "ce3"):
        dst = out / "source" / group
        roots[group] = dst
        for name, expected in bindings[group]["sha256"].items():
            source = Path(bindings[group]["root"]) / name
            target = dst / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            assert sha(target) == expected
    scorer = roots["ce3"] / "source/Quant Research Take-Home/score.py"
    target = roots["production"] / "source/Quant Research Take-Home/score.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(scorer, target)
    assert sha(target) == bindings["inputs"]["sha256"]["score.py"]
    return roots


def load_inputs(bindings):
    p = Path(bindings["inputs"]["root"])
    R = np.ascontiguousarray(pd.read_csv(p / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(p / "characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
    c = pd.read_csv(p / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    assert R.shape == (3780, 1000) and X.shape == (3780, 1000, 13) and c.shape == (1000,)
    assert all(np.isfinite(a).all() for a in (R, X, c))
    return R, X, c


def metrics(rows):
    g, cost, gross, market, seconds = rows.T
    net = g - cost
    mc = market - market.mean()
    return {"net_sharpe": float(np.sqrt(252) * net.mean() / net.std(ddof=0)),
            "net_beta": float(mc @ (net - net.mean()) / (mc @ mc)),
            "annual_mean_net_return": float(252 * net.mean()),
            "annual_net_volatility": float(np.sqrt(252) * net.std()),
            "annual_mean_cost": float(252 * cost.mean()),
            "mean_rebalance_ms": float(1000 * seconds.mean()),
            "max_rebalance_ms": float(1000 * seconds.max())}


def maxdiff(a, b):
    assert np.shape(a) == np.shape(b), (np.shape(a), np.shape(b))
    return float(np.max(np.abs(a - b), initial=0))


def accounting(targets, indices, rows, R, costs):
    previous = np.zeros(R.shape[1]); reconstructed = []
    for j, (t, target) in enumerate(zip(indices, targets)):
        g = float(np.sum(previous * R[t]))
        assert np.isfinite(g) and g > -1
        held = previous * (1 + R[t]) / (1 + g)
        fee = 0.0 if j == 0 else float(np.sum(costs * np.abs(target - held)))
        reconstructed.append([g, fee, float(np.abs(target).sum()), float(R[t].mean())])
        previous = target
    errors = np.max(np.abs(np.asarray(reconstructed)[1:] - rows[:, :4]), axis=0)
    assert np.all(errors <= 1e-12), errors
    return errors.tolist()


def run_book(label, policy, score, R, X, c, folder):
    targets = []; inner = []; virtual = []; indices = []; control = []; output = {}

    def forecast(returns_history, characteristics_history):
        output["forecast"] = policy.forecast(returns_history, characteristics_history)
        return output["forecast"]

    def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
        w = policy.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
        t = len(returns_history) - 1
        if label == "research":
            p = policy.inner
            wi, wv = policy.inner_target, p.virtual_target
            upto = (p.engine._STATE.upto, p.actual_engine._STATE.upto)
            a = p.records[-1]["multiplier"]
        else:
            p = policy.POLICY
            wi, wv = p.inner.target, p.virtual.target
            upto = (p.virtual.state.upto, p.inner.state.upto)
            a = p.multiplier
        q = [p.sums[h] / p.masses[h] if p.masses[h] else 0.0 for h in (63, 1008)]
        assert upto == (t + 1, t + 1), upto
        assert .5 <= a <= 2
        assert np.max(np.abs(wi)) <= .05 * a + 1e-10
        targets.append(np.array(w, copy=True)); inner.append(wi.copy()); virtual.append(wv.copy())
        indices.append(t); control.append([p.earned, *q, a, *upto])
        return w

    shim = type("Observer", (), {"forecast": staticmethod(forecast), "rebalance": staticmethod(rebalance)})
    rows, fsec = score.run(shim, R, X, c)
    arrays = {"forecast": output["forecast"], "targets": np.asarray(targets),
              "inner_targets": np.asarray(inner), "virtual_targets": np.asarray(virtual),
              "decision_indices": np.asarray(indices), "controller": np.asarray(control), "rows": rows}
    assert np.array_equal(arrays["decision_indices"], np.arange(252, 3779))
    assert rows.shape == (3526, 5) and arrays["forecast"].shape == (3780, 1000)
    assert all(np.isfinite(a).all() for a in arrays.values())
    assert np.abs(arrays["targets"]).sum(axis=1).max() <= 5 + 1e-10
    assert np.abs(arrays["targets"]).max() <= .10005 + 1e-10
    assert np.abs(arrays["virtual_targets"]).max() <= .05 + 1e-10
    errors = accounting(arrays["targets"], arrays["decision_indices"], rows, R, c)
    if label == "research":
        assert len(policy.inner.engine.CERTIFICATES) == len(policy.inner.actual_engine.CERTIFICATES) == 3527
        certificates = [x for pair in zip(policy.inner.engine.CERTIFICATES, policy.inner.actual_engine.CERTIFICATES) for x in pair]
        allowed = {"ok", "ok_after_recovery"}
    else:
        certificates = policy.POLICY.certificates
        allowed = ACCEPTED
    assert len(certificates) == 7054 and all(x["status"] in allowed for x in certificates)
    stats = metrics(rows)
    assert abs(stats["net_beta"]) < .2
    ids = save_arrays(folder, arrays)
    dump(folder / "certificates.json", certificates)
    with (folder / "daily.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["return_index", "gross_return", "full_cost", "net_return", "closing_target_gross", "market_return", "rebalance_seconds"])
        for t, (g, fee, gross, market, seconds) in zip(range(253, 3779), rows):
            w.writerow([t, g, fee, g - fee, gross, market, seconds])
    summary = {"performance": stats, "forecast_seconds": fsec, "accounting_errors": errors,
               "certificate_count": len(certificates), "certificate_statuses": sorted({x["status"] for x in certificates}),
               "opening_free": True, "final_charged_fee": float(rows[-1, 1]), "no_forced_liquidation": True,
               "array_manifest": ids, "controller_columns": ["earned", "q63", "q1008", "multiplier", "virtual_upto", "inner_upto"]}
    dump(folder / "summary.json", summary)
    return arrays, summary


def replay(bindings, staged, out):
    sys.path.insert(0, str(staged["research"]))
    from joint import make_joint
    from common import scorer
    R, X, c = load_inputs(bindings)
    inputs_before = [raw_sha(a) for a in (R, X, c)]
    score = scorer(staged["ce3"])
    ref, rs = run_book("research", make_joint(staged["ce3"]), score, R, X, c, out / "research")
    sys.path.insert(0, str(staged["production"] / "handoff_v3"))
    import strategy
    assert Path(strategy.__file__).resolve() == (staged["production"] / "handoff_v3/strategy.py").resolve()
    package, ps = run_book("package", strategy, score, R, X, c, out / "package")
    assert inputs_before == [raw_sha(a) for a in (R, X, c)]
    differences = {name: maxdiff(package[name], ref[name]) for name in ref}
    assert differences["forecast"] == differences["decision_indices"] == 0
    for name in ("targets", "inner_targets", "virtual_targets"):
        assert differences[name] <= 1e-8
    economic = np.max(np.abs(package["rows"][:, :4] - ref["rows"][:, :4]), axis=0)
    assert np.all(economic <= 1e-8)
    assert maxdiff(package["controller"][:, [0, 4, 5]], ref["controller"][:, [0, 4, 5]]) == 0
    assert maxdiff(package["controller"][:, [1, 2, 3]], ref["controller"][:, [1, 2, 3]]) <= 1e-12
    assert abs(ps["performance"]["net_sharpe"] - rs["performance"]["net_sharpe"]) <= 1e-8
    published = pd.read_csv(bindings["published_daily"]["path"], float_precision="round_trip")
    assert np.array_equal(published.return_index.to_numpy(), np.arange(253, 3779))
    columns = ["gross_return", "full_cost", "closing_target_gross", "market_return"]
    pr = published[columns].to_numpy()
    published_rows = np.column_stack([pr, np.zeros(len(pr))])
    historic = {}
    for name, arrays in (("research", ref), ("package", package)):
        err = np.max(np.abs(arrays["rows"][:, :4] - pr), axis=0)
        ds = metrics(arrays["rows"])["net_sharpe"] - metrics(published_rows)["net_sharpe"]
        assert np.all(err <= 1e-8) and abs(ds) <= 1e-8
        historic[name] = {"four_economic_max_errors": err.tolist(), "net_sharpe_difference": ds}
    declared = json.loads(Path(bindings["published_array_manifest"]["path"]).read_text())
    identity = {}
    original_differences = {}
    for name in ("forecast", "targets", "inner_targets", "virtual_targets"):
        old = declared[name]
        identity[name] = {"original_file_sha256": old["file_sha256"],
                          "original_array_sha256": old["array_sha256"]}
        for label, summary in (("research", rs), ("package", ps)):
            new = summary["array_manifest"][name]
            assert new["shape"] == old["shape"] and new["dtype"] == old["dtype"]
            identity[name][label] = {"file_sha256": new["file_sha256"], "array_sha256": new["array_sha256"],
                                     "matches_original_file": old["file_sha256"] == new["file_sha256"],
                                     "matches_original_array": old["array_sha256"] == new["array_sha256"]}
        if identity[name]["research"]["matches_original_array"]:
            original_differences[name] = {"research": 0.0, "package": maxdiff(package[name], ref[name]),
                                          "basis": "research array restored exactly by original SHA256"}
        elif identity[name]["package"]["matches_original_array"]:
            original_differences[name] = {"research": maxdiff(package[name], ref[name]), "package": 0.0,
                                          "basis": "package array restored exactly by original SHA256"}
        else:
            original_differences[name] = {"research": None, "package": None,
                                          "basis": "unmeasured: original arrays unavailable and hashes differ"}
    return {"all_passed": True, "research": rs, "package": ps, "differences_including_timing": differences,
            "four_economic_max_errors": economic.tolist(), "historical_daily_bridge": historic,
            "original_array_identity_diagnostics": identity,
            "original_array_max_differences": original_differences,
            "input_raw_sha256": inputs_before}


def temporal(bindings, staged, out, reference, prerequisite):
    assert reference.name == "research"
    assert reference.parent.resolve() == prerequisite.parent.resolve()
    prior = json.loads(prerequisite.read_text())
    declared = json.loads((reference / "array_manifest.json").read_text())
    assert declared == prior["research"]["array_manifest"]
    for name, identity in declared.items():
        p = reference / identity["path"]
        assert sha(p) == identity["file_sha256"], name
        a = np.load(p, mmap_mode="r", allow_pickle=False)
        assert list(a.shape) == identity["shape"] and str(a.dtype) == identity["dtype"]
        assert raw_sha(a) == identity["array_sha256"], name
    dump(out / "reference_readback.json", {"reference": str(reference),
         "prior_result_sha256": sha(prerequisite), "array_manifest_sha256": sha(reference / "array_manifest.json"),
         "all_declared_files_and_raw_arrays_verified": True})
    source = staged["production"] / "verification/v3_integration_checks.py"
    report = out / "existing_temporal_report.json"
    argv = [str(source), "--data", bindings["inputs"]["root"], "--reference", str(reference), "--report", str(report)]
    dump(out / "existing_script_invocation.json", {"argv": argv, "source_sha256": sha(source)})
    sys.argv = argv
    with (out / "existing_script.stdout.log").open("w") as stdout, (out / "existing_script.stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            worker = module("verified_temporal", source)
            code = worker.main()
    assert code == 0
    result = json.loads(report.read_text())
    checks = {k: v for k, v in result.items() if "pass" in v}
    assert len(checks) == 15 and all(v["pass"] for v in checks.values())
    return {"all_passed": True, "exit_code": code, "checks": checks,
            "observed": result["observed"], "reference_directory": str(reference)}


def runtime(bindings, staged, out):
    source = staged["production"] / "verification/v3_runtime_check.py"
    argv = [str(source), "--data", bindings["inputs"]["root"], "--sleeve", "0.05"]
    dump(out / "existing_script_invocation.json", {"argv": argv, "source_sha256": sha(source)})
    sys.argv = argv
    spec = importlib.util.spec_from_file_location("verified_runtime", source)
    worker = importlib.util.module_from_spec(spec)
    code = None
    with (out / "existing_script.stdout.log").open("w") as stdout, (out / "existing_script.stderr.log").open("w") as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                spec.loader.exec_module(worker)
            except SystemExit as exc:
                code = exc.code
    assert code == 0
    p = worker.S.POLICY
    assert worker.RT.shape == (25200, 1000) and worker.XT.shape == (25200, 1000, 13)
    assert worker.rows.shape == (24946, 5) and p.last_day == 25198 and p.earned == 24946
    certs = p.certificates
    assert len(certs) == 49894 and {c["status"] for c in certs} <= ACCEPTED
    arrays = {"rows": worker.rows, "forecast": p.forecast_output,
              "final_targets": p.outer_target, "final_inner_targets": p.inner.target,
              "final_virtual_targets": p.virtual.target}
    assert all(np.isfinite(a).all() for a in arrays.values())
    assert np.min(1 + worker.rows[:, 0]) > 0
    assert worker.out["pass"] and worker.fsec < 3600 and worker.rows[:, 4].mean() < .1
    ids = save_arrays(out / "runtime_arrays", arrays)
    dump(out / "certificates.json", certs)
    return {"all_passed": True, "exit_code": code, "existing_runtime_result": worker.out,
            "input_shapes": [list(worker.RT.shape), list(worker.XT.shape), list(worker.c.shape)],
            "runtime_input_raw_sha256": [raw_sha(a) for a in (worker.RT, worker.XT, worker.c)],
            "forecast_rows": len(p.forecast_output), "decisions": len(certs) // 2,
            "certificate_count": len(certs), "certificate_statuses": sorted({x["status"] for x in certs}),
            "last_day": p.last_day, "earned_observations": p.earned,
            "array_manifest": ids, "performance": {}, "not_alpha_evidence": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("replay", "temporal", "runtime"), required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--reference", type=Path)
    ap.add_argument("--prerequisite", type=Path)
    a = ap.parse_args(); a.out.mkdir(parents=True, exist_ok=False)
    initial_env = env()
    identities = {"harness_sha256": sha(__file__), "plan_sha256": sha(ROOT / "REPLAY_PLAN.md"),
                  "bindings_sha256": sha(ROOT / "bindings.json")}
    dump(a.out / "invocation.json", {"argv": sys.argv, "cwd": str(Path.cwd()), "environment": initial_env, **identities})
    bindings = json.loads((ROOT / "bindings.json").read_text())
    release = json.loads(a.release.read_text())
    release_id = sha(a.release)
    assert a.mode in release["allow_modes"] and all(release[k] == v for k, v in identities.items())
    if a.mode != "replay":
        assert a.prerequisite is not None
        assert sha(a.prerequisite) == release["prerequisite_sha256"][a.mode]
        prior = json.loads(a.prerequisite.read_text())
        assert prior["all_passed"] and prior["mode"] == {"temporal": "replay", "runtime": "temporal"}[a.mode]
        assert all(prior[k] == v for k, v in identities.items())
        shutil.copyfile(a.prerequisite, a.out / "prerequisite_result.json")
    assert len(initial_env["cpu_affinity"]) == 1 and all(initial_env["thread_variables"][k] == "1" for k in THREADS)
    verify_sources(bindings)
    for path in (Path(__file__), ROOT / "REPLAY_PLAN.md", ROOT / "bindings.json", a.release):
        shutil.copyfile(path, a.out / path.name)
    staged = stage(bindings, a.out)
    started = time.perf_counter()
    try:
        if a.mode == "replay":
            result = replay(bindings, staged, a.out)
        elif a.mode == "temporal":
            assert a.reference is not None
            result = temporal(bindings, staged, a.out, a.reference.resolve(), a.prerequisite.resolve())
        else:
            result = runtime(bindings, staged, a.out)
        verify_sources(bindings)
        assert sha(a.release) == release_id
        final_env = env()
        assert final_env["cpu_affinity"] == initial_env["cpu_affinity"]
        assert final_env["thread_variables"] == initial_env["thread_variables"]
        result.update({"mode": a.mode, "elapsed_seconds": time.perf_counter() - started,
                       "source_bindings_unchanged": True, "environment_after": final_env,
                       "release_sha256": release_id, **identities})
        dump(a.out / "result.json", result)
        print(json.dumps({"mode": a.mode, "all_passed": result["all_passed"], "result": str(a.out / "result.json")}))
    except BaseException:
        (a.out / "failure_traceback.log").write_text(traceback.format_exc())
        dump(a.out / "failure.json", {"mode": a.mode, "all_passed": False,
                                     "elapsed_seconds": time.perf_counter() - started, **identities})
        raise


if __name__ == "__main__":
    main()
