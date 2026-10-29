"""Lossless copies of completed runtime evidence; no policy execution."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result_path = args.runtime / "result.json"
    original_result_sha = digest(result_path)
    result = json.loads(result_path.read_text())
    assert result["mode"] == "runtime" and result["all_passed"]
    assert result["harness_sha256"] == "ba5379050c51e20b74aba1e45f787e5e5f643fbaf2bb316179263b0289ce516d"
    assert result["plan_sha256"] == "8d64a56d242aaa516012fd8fa9cc9f1206175eb703591985d7a2e66d0d79acd8"
    assert result["bindings_sha256"] == "fce32c98e78cef9b008fd6823e98321327474b84e0ae268dfb3822a225f3f2f7"
    args.out.mkdir(parents=True, exist_ok=False)
    selections = [("certificates.json", None)]
    for name in ("rows", "final_targets", "final_inner_targets", "final_virtual_targets"):
        identity = result["array_manifest"][name]
        selections.append(("runtime_arrays/" + identity["path"], identity))
    entries = []
    for relative, identity in selections:
        source = args.runtime / relative
        original_sha = digest(source)
        original_bytes = source.stat().st_size
        if identity is not None:
            assert original_sha == identity["file_sha256"], relative
        target = args.out / (source.name + ".gz")
        with source.open("rb") as stream, target.open("xb") as destination:
            with gzip.GzipFile(filename="", mode="wb", fileobj=destination, mtime=0, compresslevel=9) as compressed:
                for block in iter(lambda: stream.read(1 << 20), b""):
                    compressed.write(block)
            destination.flush()
            os.fsync(destination.fileno())
        restored = hashlib.sha256()
        restored_bytes = 0
        with gzip.open(target, "rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                restored.update(block)
                restored_bytes += len(block)
        assert restored.hexdigest() == original_sha and restored_bytes == original_bytes
        assert digest(source) == original_sha
        entries.append({"original_path": relative, "original_bytes": original_bytes,
                        "original_sha256": original_sha, "compressed_path": target.name,
                        "compressed_bytes": target.stat().st_size, "compressed_sha256": digest(target),
                        "round_trip_exact": True, "array_identity": identity})
    assert digest(result_path) == original_result_sha
    root = Path(__file__).resolve().parent
    manifest = {"scope": "lossless completed-runtime evidence packaging; no strategy execution",
                "runtime_result": str(result_path), "runtime_result_sha256": original_result_sha,
                "packaging_script_sha256": digest(Path(__file__)),
                "packaging_plan_sha256": digest(root / "RUNTIME_PACKAGING_PLAN.md"),
                "gzip_mtime": 0, "gzip_level": 9, "all_round_trips_exact": True,
                "files": entries,
                "runtime_forecast": {"durably_archived_by_this_packet": False,
                                     "regenerable_from_frozen_runtime_workflow": True,
                                     "captured_local_path": "runtime_arrays/forecast.npy",
                                     "array_identity": result["array_manifest"]["forecast"]}}
    path = args.out / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"manifest": str(path), "sha256": digest(path),
                      "all_round_trips_exact": True, "files": len(entries)}))


if __name__ == "__main__":
    main()
