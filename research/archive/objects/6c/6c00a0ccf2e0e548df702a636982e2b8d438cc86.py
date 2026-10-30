"""Lossless evidence packaging; no policy execution or score changes.

Run once after owners freeze their files. Small NPY outputs and non-primary CSV
ledgers are archived with their original repository-relative names. Large NPY
intermediates remain reproducible from the recorded original-input workflows.
"""
from pathlib import Path
import hashlib
import io
import json
import zipfile

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("publication")
MAX_ARRAY_BYTES = 1_048_576
TARGET_ARCHIVE_BYTES = 1_000_000
PRIMARY_CSV = {
    "evidence/v2_score2_execution_20261029/actual_001/baseline/daily.csv",
    "evidence/v2_score2_execution_20261029/actual_001/E1/daily.csv",
    "evidence/v2_score2_execution_20261029/actual_001/E2/daily.csv",
    "evidence/v2_score2_forecast_20261029/actual_001/F3_VTvol/daily.csv",
    "evidence/v2_score2_review_20261029/m1/actual_001/M0/daily.csv",
    "evidence/v2_score2_review_20261029/m1/actual_001/M1/daily.csv",
    "evidence/v2_score2_joint_20261029/actual_001/E2_M1/daily.csv",
}
EVIDENCE_SUFFIXES = {".py", ".md", ".json", ".log", ".csv", ".npy"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def make_zip(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    raw = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        assert z.namelist() == [name for name, _ in entries]
        for name, data in entries:
            assert z.read(name) == data
    return raw


def main():
    OUT.mkdir(exist_ok=False)
    artifacts = []
    archives = []
    standalone_paths = []
    for directory in sorted((REPO / "evidence").glob("v2_score2_*")):
        pending = []
        pending_bytes = 22
        part = 0

        def flush():
            nonlocal part, pending, pending_bytes
            if not pending:
                return
            part += 1
            raw = make_zip(pending)
            file = OUT / f"{directory.name}_{part:02d}.zip"
            file.write_bytes(raw)
            assert file.read_bytes() == raw
            name = str(file.relative_to(REPO))
            archives.append({"path": name, "bytes": len(raw), "sha256": digest(raw),
                             "entries": [n for n, _ in pending]})
            for item in artifacts:
                if item["path"] in {n for n, _ in pending}:
                    item["archive"] = name
            pending = []
            pending_bytes = 22

        for file in sorted(directory.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts or OUT in file.parents:
                continue
            if file.suffix not in EVIDENCE_SUFFIXES or any(p.startswith(".") for p in file.relative_to(directory).parts):
                continue
            name = str(file.relative_to(REPO))
            size = file.stat().st_size
            if file.suffix == ".npy" and size > MAX_ARRAY_BYTES:
                h = hashlib.sha256()
                with file.open("rb") as f:
                    for block in iter(lambda: f.read(1 << 20), b""):
                        h.update(block)
                artifacts.append({"path": name, "bytes": size, "sha256": h.hexdigest(),
                                  "storage": "regenerable_large_array"})
                continue
            data = file.read_bytes()
            entry = {"path": name, "bytes": len(data), "sha256": digest(data)}
            if file.suffix == ".npy" or (file.suffix == ".csv" and name not in PRIMARY_CSV):
                entry["storage"] = "lossless_archive"
                added_bytes = len(make_zip([(name, data)])) - 22
                if pending and pending_bytes + added_bytes > TARGET_ARCHIVE_BYTES:
                    flush()
                pending.append((name, data))
                pending_bytes += added_bytes
            else:
                entry["storage"] = "repository_file"
                standalone_paths.append(name)
            artifacts.append(entry)
        flush()
    document = {
        "purpose": "Preserve original evidence bytes without checking multi-gigabyte reproducible arrays into git.",
        "large_array_limit_bytes": MAX_ARRAY_BYTES,
        "selection": "Declared research evidence extensions only; interpreter caches and incidental environment files are excluded without reading their contents.",
        "primary_csv_paths": sorted(PRIMARY_CSV),
        "archive_entry_paths_are_repository_relative": True,
        "all_archive_entries_roundtrip_verified": True,
        "artifacts": artifacts,
        "archives": archives,
        "standalone_paths": standalone_paths,
        "restore": "Follow ../EVIDENCE_RESTORATION.md. From the repository root, extract evidence/v2_score2_root_20261029/publication/*.zip into '.', checking existing hashes. Pass --snapshot evidence/v2_score2_execution_20261029/actual_001/source and original inputs to recorded commands with a NEW empty --out. Restore only omitted large arrays after checking original hashes; retain original measured timing rows. Restore E2 reference arrays before joint replay.",
        "scope": "No forecasts, positions, economic results, acceptance decisions or source files were modified by packaging. Large arrays are research intermediates, with original source commands and hashes retained.",
    }
    file = OUT / "manifest.json"
    file.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({"manifest": str(file), "artifacts": len(artifacts),
                      "archives": len(archives), "archive_bytes": sum(a["bytes"] for a in archives),
                      "standalone_files": len(standalone_paths),
                      "regenerable_large_arrays": sum(a["storage"] == "regenerable_large_array" for a in artifacts)}))


if __name__ == "__main__":
    main()
