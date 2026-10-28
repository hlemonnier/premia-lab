"""Actual F2 canonical-layout future isolation, specified in EXECUTION.md."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pandas as pd

import run_research as controller


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
    inputs = {n: controller.sha(controller.DATA / n) for n in ("returns.csv", "characteristics.csv", "costs.csv")}
    reference_inputs = json.loads((controller.ROOT / "actual_001/input_hashes.json").read_text())
    assert inputs == reference_inputs
    controller.write_json(args.out / "invocation.json", {
        "argv": sys.argv, "source_hashes": hashes, "input_hashes": inputs,
        "controller_sha256": controller.sha(controller.__file__),
        "followup_sha256": controller.sha(__file__),
        "prototype_sha256": controller.sha(prototype_path),
        "prospective_spec_sha256": controller.sha(controller.ROOT / "EXECUTION.md"),
    })
    shutil.copyfile(__file__, args.out / "executed_followup.py")
    sys.path.insert(0, str(clean / "handoff_v2"))
    controller.load_module("baseline_strategy", clean / "handoff_v2/strategy.py")
    from model_v2 import engine
    score = controller.load_module("unchanged_score", clean / controller.SOURCE_FILES[-1])
    prototype = controller.load_module("research_prototype", prototype_path)
    R = np.ascontiguousarray(pd.read_csv(controller.DATA / "returns.csv", index_col="day").to_numpy(np.float64))
    X = np.ascontiguousarray(pd.read_csv(controller.DATA / "characteristics.csv", index_col=["day", "stock"]).to_numpy(np.float64).reshape(len(R), R.shape[1], 13))
    c = pd.read_csv(controller.DATA / "costs.csv", index_col="stock")["cost"].to_numpy(np.float64)
    rng = np.random.default_rng(20261029)
    R[1500:] = rng.normal(0, .025, R[1500:].shape)
    X[1500:] = rng.normal(0, 3, X[1500:].shape)
    assert R.flags.c_contiguous and X.flags.c_contiguous
    future = controller.run_case(engine, score, prototype, "F2", R, X, c, args.out / "F2_future_C")
    reference = np.load(controller.ROOT / "actual_001/F2_base/arrays.npz")
    saved = {"forecast": reference["forecast"], "targets": reference["targets"],
             "indices": reference["decision_indices"], "rows": reference["rows"],
             "days": reference["earning_indices"]}
    findings = {"future_C_layout": controller.compare(saved, future, cut=1500),
                "source_identity": {"pass": hashes == {rel: controller.sha(clean / rel) for rel in controller.SOURCE_FILES}}}
    controller.write_json(args.out / "verification.json", findings)
    print(json.dumps(findings, indent=2), flush=True)
    assert all(v["pass"] for v in findings.values()), findings


if __name__ == "__main__":
    main()
