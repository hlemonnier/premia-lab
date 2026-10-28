"""Unchanged F2 scorer replay and separately verified atomic array artifacts."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

import numpy as np
import pandas as pd

import run_research as controller


def save_verified(path, array):
    temporary = path.with_suffix(".tmp")
    with temporary.open("wb") as f:
        np.save(f, array, allow_pickle=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)
    reread = np.load(path, allow_pickle=False)
    assert reread.shape == array.shape and np.array_equal(reread, array)
    return {"shape": list(array.shape), "bytes": path.stat().st_size,
            "file_sha256": controller.sha(path), "array_sha256": controller.array_sha(reread)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    clean = args.out / "clean"
    for rel in controller.SOURCE_FILES:
        target = clean / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(controller.SNAPSHOT / rel, target)
    hashes = {rel: controller.sha(clean / rel) for rel in controller.SOURCE_FILES}
    assert hashes[controller.SOURCE_FILES[-1]] == controller.SCORER_SHA
    prototype_path = controller.ROOT / "prototype.py"
    original_summary = json.loads((controller.ROOT / "actual_001/F2_base/summary.json").read_text())
    inputs = {n: controller.sha(controller.DATA / n) for n in ("returns.csv", "characteristics.csv", "costs.csv")}
    assert inputs == json.loads((controller.ROOT / "actual_001/input_hashes.json").read_text())
    controller.write_json(args.out / "invocation.json", {
        "argv": sys.argv, "source_hashes": hashes, "input_hashes": inputs,
        "controller_sha256": controller.sha(controller.__file__),
        "repair_sha256": controller.sha(__file__),
        "prototype_sha256": controller.sha(prototype_path),
        "prospective_spec_sha256": controller.sha(controller.ROOT / "EXECUTION.md"),
        "original_forecast_hash": original_summary["forecast_sha256"],
        "original_target_hash": original_summary["targets_sha256"],
    })
    shutil.copyfile(__file__, args.out / "executed_repair.py")
    sys.path.insert(0, str(clean / "handoff_v2"))
    controller.load_module("baseline_strategy", clean / "handoff_v2/strategy.py")
    from model_v2 import engine
    score = controller.load_module("unchanged_score", clean / controller.SOURCE_FILES[-1])
    prototype = controller.load_module("research_prototype", prototype_path)
    R = np.ascontiguousarray(pd.read_csv(controller.DATA / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(controller.DATA / "characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
    c = pd.read_csv(controller.DATA / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    baseline = controller.run_case(engine, score, prototype, "F2", R, X, c, args.out / "F2_base")
    verified = args.out / "verified_arrays"
    verified.mkdir()
    array_manifest = {k: save_verified(verified / (k + ".npy"), baseline[k])
                      for k in ("forecast", "targets", "indices", "rows", "days")}
    controller.write_json(args.out / "verified_array_manifest.json", array_manifest)
    original_daily = pd.read_csv(controller.ROOT / "actual_001/F2_base/daily.csv")
    original_economics = original_daily[["gross_return", "cost", "target_gross", "market"]].to_numpy()
    comparison = {
        "original_forecast_hash": controller.array_sha(baseline["forecast"]) == original_summary["forecast_sha256"],
        "original_target_hash": controller.array_sha(baseline["targets"]) == original_summary["targets_sha256"],
        "max_economic_difference": controller.maximum_difference(original_economics, baseline["rows"][:, :4]),
    }
    comparison["pass"] = (comparison["original_forecast_hash"] and comparison["original_target_hash"]
                          and comparison["max_economic_difference"] <= 1e-12)
    future_path = controller.ROOT / "actual_c_future_001/F2_future_C/arrays.npz"
    with zipfile.ZipFile(future_path) as archive:
        assert archive.testzip() is None
    future_data = np.load(future_path, allow_pickle=False)
    future = {"forecast": future_data["forecast"], "targets": future_data["targets"],
              "indices": future_data["decision_indices"], "rows": future_data["rows"],
              "days": future_data["earning_indices"]}
    findings = {"original_F2_reproduction": comparison,
                "canonical_future": controller.compare(baseline, future, cut=1500),
                "source_identity": {"pass": hashes == {rel: controller.sha(clean / rel) for rel in controller.SOURCE_FILES}}}
    findings["new_npz_integrity"] = {"is_zipfile": zipfile.is_zipfile(args.out / "F2_base/arrays.npz")}
    if findings["new_npz_integrity"]["is_zipfile"]:
        with zipfile.ZipFile(args.out / "F2_base/arrays.npz") as archive:
            findings["new_npz_integrity"]["bad_member"] = archive.testzip()
    controller.write_json(args.out / "verification.json", findings)
    print(json.dumps(findings, indent=2), flush=True)
    assert all(findings[k]["pass"] for k in ("original_F2_reproduction", "canonical_future", "source_identity")), findings


if __name__ == "__main__":
    main()
