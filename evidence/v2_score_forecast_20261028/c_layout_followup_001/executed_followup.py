"""Complete-scorer follow-up specified in EXECUTION.md; no changed tolerances."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import numpy as np

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
    controller.write_json(args.out / "invocation.json", {
        "argv": sys.argv, "source_hashes": hashes,
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
    R, X, c = controller.fixture(engine)
    Ra, Xa = R.copy(), X.copy()
    rng = np.random.default_rng(20261029)
    Ra[320:] = rng.normal(0, .025, Ra[320:].shape)
    Xa[320:] = rng.normal(0, 3, Xa[320:].shape)
    base = controller.run_case(engine, score, prototype, "F1", R, X, c, args.out / "F1_base")
    future = controller.run_case(engine, score, prototype, "F1", Ra, Xa, c, args.out / "F1_future_C")
    reference = np.load(controller.ROOT / "synthetic_001/F1_base/arrays.npz")
    saved = {"forecast": reference["forecast"], "targets": reference["targets"],
             "indices": reference["decision_indices"], "rows": reference["rows"],
             "days": reference["earning_indices"]}
    findings = {"repeat_original_baseline": controller.compare(saved, base),
                "future_C_layout": controller.compare(base, future, cut=320),
                "source_identity": {"pass": hashes == {rel: controller.sha(clean / rel) for rel in controller.SOURCE_FILES}}}
    controller.write_json(args.out / "verification.json", findings)
    print(json.dumps(findings, indent=2), flush=True)
    assert all(v["pass"] for v in findings.values()), findings


if __name__ == "__main__":
    main()
