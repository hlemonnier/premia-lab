#!/usr/bin/env python3
"""Create the protocol-limited discovery cache. See research/DATA_PREPARATION_PLAN.md."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import sys
import traceback

for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"
sys.dont_write_bytecode = True

import numpy as np
import pandas as pd


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    root, out, cache = args.project.resolve(), args.out.resolve(), args.cache.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cache.mkdir(parents=True, exist_ok=True)
    if (cache / "metadata.json").exists():
        raise FileExistsError("A ready cache already exists; choose another cache directory")
    code = Path(__file__).resolve()
    command = shlex.join([sys.executable, str(code), "--project", str(root), "--out", str(out), "--cache", str(cache)])
    rerun = shlex.join([sys.executable, str(out / "runner_used.py"), "--project", str(root),
                       "--out", str(out) + "_rerun", "--cache", str(cache) + "_rerun"])
    status = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "command": command, "rerun_command": rerun, "checks": [],
              "numeric_input_slice": [0,2016], "model_fitted": False}
    (out / "summary.json").write_text(json.dumps(status, indent=2) + "\n")
    (out / "runner_used.py").write_bytes(code.read_bytes())
    (out / "expectations.md").write_bytes((root / "research/DATA_PREPARATION_PLAN.md").read_bytes())
    (out / "rerun.txt").write_text(rerun + "\n")
    log = []

    def check(name, condition, actual):
        record = {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual}
        status["checks"].append(record)
        line = json.dumps(record)
        print(line, flush=True)
        log.append(line)
        if not condition:
            raise AssertionError(name)

    exit_code = 1
    try:
        manifest = json.loads((root / "evidence/preflight_002/source_manifest.json").read_text())
        source = root / "source/Quant Research Take-Home"
        expected = {item["path"]: item for item in manifest}
        source_hashes = {}
        for name in ("returns.csv", "characteristics.csv", "costs.csv"):
            source_hashes[name] = file_hash(source / name)
            check("source_identity_" + name, source_hashes[name] == expected[name]["sha256"], source_hashes[name])
        r = pd.read_csv(source / "returns.csv", index_col="day", nrows=2016)
        c = pd.read_csv(source / "costs.csv", index_col="stock")["cost"]
        check("returns_shape", r.shape == (2016,1000), list(r.shape))
        check("day_sequence", np.array_equal(r.index.to_numpy(), np.arange(1,2017)), [int(r.index[0]), int(r.index[-1])])
        check("stock_order", np.array_equal(r.columns.to_numpy(), c.index.to_numpy()), "returns columns equal cost rows")
        check("returns_finite", np.isfinite(r.to_numpy()).all(), "finite prefix")
        check("costs_valid", np.isfinite(c.to_numpy()).all() and (c.to_numpy() >= 0).all(), "finite nonnegative costs")
        np.save(cache / "returns.npy", r.to_numpy(dtype=np.float64))
        np.save(cache / "costs.npy", c.to_numpy(dtype=np.float64))
        feature_names = ["Woe","Malice","Dread","Frolic","Up","Down","Charm","Strange","Top","Bottom","Snap","Crackle","Pop"]
        x = np.lib.format.open_memmap(cache / "characteristics.npy", mode="w+", dtype="float64", shape=(2016,1000,13))
        flat = x.reshape(-1,13)
        offset = 0
        for frame in pd.read_csv(source / "characteristics.csv", nrows=2016000, chunksize=100000):
            if list(frame.columns) != ["day","stock"] + feature_names:
                raise AssertionError("Characteristic columns differ")
            locations = np.arange(offset, offset + len(frame))
            if not np.array_equal(frame["day"].to_numpy(), locations // 1000 + 1):
                raise AssertionError("Characteristic day order differs")
            if not np.array_equal(frame["stock"].to_numpy(), r.columns.to_numpy()[locations % 1000]):
                raise AssertionError("Characteristic stock order differs")
            values = frame[feature_names].to_numpy(dtype=np.float64)
            if not np.isfinite(values).all():
                raise AssertionError("Nonfinite characteristics")
            flat[offset:offset + len(frame)] = values
            offset += len(frame)
        check("characteristics_rows_and_alignment", offset == 2016000, offset)
        x.flush()
        del flat, x
        output_hashes = {name: file_hash(cache / name) for name in ("returns.npy","characteristics.npy","costs.npy")}
        metadata = {"status": "READY", "input_slice": [0,2016], "day_labels": [1,2016],
                    "shape_returns": [2016,1000], "shape_characteristics": [2016,1000,13],
                    "stocks": list(r.columns), "features": feature_names,
                    "source_sha256": source_hashes, "cache_sha256": output_hashes,
                    "creator_sha256": file_hash(code)}
        (cache / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        (out / "cache_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        (out / "environment.json").write_text(json.dumps({"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,"pandas":pd.__version__}, indent=2) + "\n")
        status["status"] = "PASS"
        exit_code = 0
    except Exception:
        status["status"] = "FAIL"
        status["traceback"] = traceback.format_exc()
        log.append(status["traceback"])
        print(status["traceback"], file=sys.stderr, flush=True)
    finally:
        status["exit_code"] = exit_code
        status["finished_utc"] = datetime.now(timezone.utc).isoformat()
        (out / "summary.json").write_text(json.dumps(status, indent=2) + "\n")
        (out / "run.log").write_text("\n".join(log) + "\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
