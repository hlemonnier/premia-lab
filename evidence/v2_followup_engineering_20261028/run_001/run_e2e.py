"""Independent complete-workflow audit; see PLAN.md, written before this harness."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types

import numpy as np


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(seed):
    rng = np.random.default_rng(seed)
    t, n, k = 340, 96, 13
    x = np.empty((t, n, k), dtype=np.float64)
    x[0] = rng.normal(size=(n, k))
    for j in range(1, t):
        x[j] = 0.96 * x[j - 1] + 0.28 * rng.normal(size=(n, k))
    beta = np.linspace(0.5, 1.5, n)
    market = rng.normal(0.0001, 0.008, t)
    coef = np.linspace(-0.00025, 0.0003, k)
    r = market[:, None] * beta + rng.normal(0, 0.008, size=(t, n))
    for j in range(1, t):
        factor = rng.normal(0, 0.0005, k)
        r[j] += x[j - 1] @ (coef + factor)
    return r, x, np.linspace(0.0002, 0.0008, n)


def worker(out, case):
    src = out / "source"
    sys.path.insert(0, str(src / "handoff_v2"))
    import strategy
    from model_v2 import engine
    spec = importlib.util.spec_from_file_location("immutable_score", src / "score.py")
    score = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(score)
    data = np.load(out / "inputs.npz")
    r, x, costs = data["R"], data["X"], data["costs"]
    rb, xb = data["R_alt"], data["X_alt"]

    def execute(rr, xx, start=252):
        targets, target_days, forecasts, prior_state = [], [], [], []

        def fc(returns_history, characteristics_history):
            ans = strategy.forecast(returns_history, characteristics_history)
            forecasts.append(ans)
            return ans

        def rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs):
            prior_state.append(None if engine._STATE is None else int(engine._STATE.upto))
            ans = strategy.rebalance(held_positions, expected_returns, returns_history, characteristics_history, trading_costs)
            targets.append(ans.copy())
            target_days.append(len(returns_history) - 1)
            return ans

        strat = types.SimpleNamespace(forecast=fc, rebalance=rebalance)
        ledger, fsec = score.run(strat, rr, xx, costs, start=start)
        return dict(forecast=forecasts[0], targets=np.asarray(targets), target_days=np.asarray(target_days),
                    ledger=ledger[:, :4], ledger_days=np.arange(start + 1, len(rr) - 1),
                    prior_state=np.asarray([-1 if v is None else v for v in prior_state]), forecast_seconds=fsec)

    if case in ("baseline", "repeat"):
        result = execute(r, x)
    elif case in ("future", "future_R_F", "future_X_F"):
        rr, xx = r.copy(), x.copy()
        rr[300:], xx[300:] = rb[300:], xb[300:]
        if case == "future_R_F":
            rr = np.asfortranarray(rr)
        if case == "future_X_F":
            xx = np.asfortranarray(xx)
        result = execute(rr, xx)
    elif case == "truncated":
        result = execute(r[:301], x[:301])
    elif case == "cold_alt_custom_start":
        result = execute(rb, xb, start=299)
    elif case == "warm_alt_custom_start":
        execute(r[:301], x[:301])
        result = execute(rb, xb, start=299)
    elif case == "cold_alt_default_start":
        result = execute(rb, xb)
    elif case == "warm_alt_default_start":
        execute(r, x)
        result = execute(rb, xb)
    else:
        raise ValueError(case)
    np.savez(out / "runs" / (case + ".npz"), **result)
    print(json.dumps({"case": case, "forecasts": result["forecast"].shape,
                      "targets": result["targets"].shape, "ledger": result["ledger"].shape,
                      "nonzero_targets": int(np.count_nonzero(result["targets"])),
                      "prior_state_first": int(result["prior_state"][0])}))


def difference(a, b):
    a, b = np.asarray(a), np.asarray(b)
    delta = np.abs(a - b)
    mismatch = np.argwhere(a != b)
    return {"bitwise_equal": bool(np.array_equal(a, b)),
            "allclose": bool(np.allclose(a, b, atol=1e-12, rtol=1e-10)),
            "max_abs": float(delta.max()) if delta.size else 0,
            "first_mismatch": mismatch[0].tolist() if mismatch.size else None,
            "mismatch_count": int(np.count_nonzero(a != b)), "shape": list(a.shape)}


def control(snapshot, out):
    out.mkdir(parents=True, exist_ok=False)
    (out / "runs").mkdir()
    (out / "logs").mkdir()
    (out / "source").mkdir()
    shutil.copytree(snapshot / "handoff_v2", out / "source" / "handoff_v2")
    shutil.copy2(snapshot / "source/Quant Research Take-Home/score.py", out / "source" / "score.py")
    shutil.copy2(Path(__file__).with_name("PLAN.md"), out / "PLAN.md")
    shutil.copy2(__file__, out / "run_e2e.py")
    r, x, c = fixture(20261028)
    rb, xb, _ = fixture(20261029)
    np.savez(out / "inputs.npz", R=r, X=x, costs=c, R_alt=rb, X_alt=xb)
    source_paths = [p for p in (out / "source").rglob("*") if p.is_file()]
    source_hashes = {str(p.relative_to(out)): sha(p) for p in source_paths}
    source_hashes.update({"PLAN.md": sha(out / "PLAN.md"), "run_e2e.py": sha(out / "run_e2e.py"), "inputs.npz": sha(out / "inputs.npz")})
    (out / "input_source_manifest.json").write_text(json.dumps(source_hashes, indent=2) + "\n")
    cases = ["baseline", "repeat", "future", "future_R_F", "future_X_F", "truncated",
             "cold_alt_custom_start", "warm_alt_custom_start", "cold_alt_default_start", "warm_alt_default_start"]
    commands = []
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    for case in cases:
        cmd = [sys.executable, str(out / "run_e2e.py"), "--worker", case, "--out", str(out)]
        commands.append({"case": case, "command": cmd, "thread_environment": {k: env[k] for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}})
        with (out / "logs" / (case + ".log")).open("w") as log:
            p = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT)
        commands[-1]["exit_code"] = p.returncode
        print(case, p.returncode, flush=True)
        if p.returncode:
            (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
            raise RuntimeError(case)
    (out / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
    arrays = {case: dict(np.load(out / "runs" / (case + ".npz"))) for case in cases}
    base = arrays["baseline"]
    results = {}
    for field in ("forecast", "targets", "ledger"):
        results["repeat_" + field] = difference(base[field], arrays["repeat"][field])
    for case in ("future", "future_R_F", "future_X_F"):
        a = arrays[case]
        results[case + "_forecast_protected"] = difference(base["forecast"][:301], a["forecast"][:301])
        for field, dayfield in (("targets", "target_days"), ("ledger", "ledger_days")):
            mask = base[dayfield] < 300
            results[case + "_" + field + "_protected"] = difference(base[field][mask], a[field][mask])
        results[case + "_later_forecast_changed"] = bool(not np.array_equal(base["forecast"][301:], a["forecast"][301:]))
        results[case + "_later_targets_changed"] = bool(not np.array_equal(base["targets"][base["target_days"] >= 300], a["targets"][a["target_days"] >= 300]))
    trunc = arrays["truncated"]
    results["truncated_forecast"] = difference(base["forecast"][:301], trunc["forecast"])
    for field, dayfield in (("targets", "target_days"), ("ledger", "ledger_days")):
        results["truncated_" + field] = difference(base[field][:len(trunc[dayfield])], trunc[field])
    for label in ("custom", "default"):
        cold, warm = arrays["cold_alt_" + label + "_start"], arrays["warm_alt_" + label + "_start"]
        for field in ("forecast", "targets", "ledger"):
            results["restart_" + label + "_" + field] = difference(cold[field], warm[field])
        results["restart_" + label + "_initial_state_lengths"] = {"cold": int(cold["prior_state"][0]), "warm": int(warm["prior_state"][0])}
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    (out / "environment.json").write_text(json.dumps({"python": sys.version, "executable": sys.executable, "numpy": np.__version__, "snapshot": str(snapshot), "pinned_commit": "afed8d0cb017acda151c4ea262fc30db7568a4bb"}, indent=2) + "\n")
    artifacts = {str(p.relative_to(out)): sha(p) for p in out.rglob("*") if p.is_file()}
    (out / "artifact_manifest.json").write_text(json.dumps(artifacts, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--worker")
    args = parser.parse_args()
    if args.worker:
        worker(args.out.resolve(), args.worker)
    else:
        control(args.snapshot.resolve(), args.out.resolve())
