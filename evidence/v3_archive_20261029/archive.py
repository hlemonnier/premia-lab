"""Lossless, deterministic, split preservation of the approved actual replay."""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import traceback

ROOT = Path(__file__).resolve().parent
PART_BYTES = 2 * 1024 * 1024
CHUNK = 1024 * 1024
RESULT_SHA = "8665d0bf6748cc6c45d88da201cc4aadff258770cb7f0a5dab18916ee4c5fd66"
ARRAYS = ("forecast", "targets", "inner_targets", "virtual_targets",
          "decision_indices", "rows", "controller")
HEX = re.compile(r"[0-9a-f]{64}\Z")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def relative(name):
    require(isinstance(name, str) and name != "", "Empty or non-string path")
    require(not any(c in name for c in ("\\", ":", "\0")), "Nonportable path")
    require(all(p not in ("", ".", "..") for p in name.split("/")), "Unsafe path component")
    p = PurePosixPath(name)
    require(not p.is_absolute(), "Absolute path")
    return p


def regular(path):
    require(path.is_file() and not path.is_symlink(), "Not a regular input file: " + str(path))


def inventory(result_path):
    base = result_path.parent
    result = json.loads(result_path.read_text())
    require(result.get("all_passed") is True and result.get("mode") == "replay",
            "Input replay did not pass")
    require(result.get("source_bindings_unchanged") is True, "Unbound replay sources")
    files = []

    def add(name, array=None):
        relative(name)
        path = base / name
        regular(path)
        digest = sha(path)
        if array is not None:
            require(digest == array["file_sha256"], "Replay array file mismatch: " + name)
        record = {"path": name, "sha256": digest, "bytes": path.stat().st_size}
        if array is not None:
            record["array"] = {k: array[k] for k in ("shape", "dtype", "array_sha256")}
        files.append(record)

    add("result.json")
    add("invocation.json")
    for book in ("research", "package"):
        declared = result[book]["array_manifest"]
        require(set(declared) == set(ARRAYS), "Unexpected array inventory")
        actual = json.loads((base / book / "array_manifest.json").read_text())
        require(actual == declared, "Array manifest differs from passed result")
        summary = json.loads((base / book / "summary.json").read_text())
        require(summary == result[book], "Summary differs from passed result")
        for name in ARRAYS:
            require(declared[name]["path"] == name + ".npy", "Unexpected array filename")
            add(book + "/" + name + ".npy", declared[name])
        for name in ("array_manifest.json", "summary.json", "certificates.json", "daily.csv"):
            add(book + "/" + name)
    return sorted(files, key=lambda x: x["path"])


class PartsReader(io.RawIOBase):
    """Read sequential part files as one stream without a concatenated copy."""
    def __init__(self, paths):
        super().__init__()
        self.paths = iter(paths)
        self.current = None

    def readable(self):
        return True

    def readinto(self, buffer):
        view = memoryview(buffer)
        total = 0
        while total < len(view):
            if self.current is None:
                path = next(self.paths, None)
                if path is None:
                    break
                self.current = path.open("rb")
            n = self.current.readinto(view[total:])
            if n:
                total += n
            else:
                self.current.close()
                self.current = None
        return total

    def close(self):
        if self.current is not None:
            self.current.close()
        super().close()


def read_manifest(packet, expected=None):
    manifest_path = packet / "manifest.json"
    regular(manifest_path)
    actual = sha(manifest_path)
    sidecar = (packet / "manifest.sha256").read_text().strip()
    require(sidecar == actual + "  manifest.json", "Manifest checksum mismatch")
    if expected is not None:
        require(actual == expected, "Trusted manifest identity mismatch")
    m = json.loads(manifest_path.read_text())
    require(m["format"] == "v3-exact-archive-v1", "Unknown archive format")
    require(m["part_bytes"] == PART_BYTES, "Unexpected part size")
    require(m["source_result_sha256"] == RESULT_SHA, "Unexpected replay result")
    objects = m["objects"]
    require(objects and all(HEX.fullmatch(k) for k in objects), "Invalid object IDs")
    aliases = set()
    for item in m["files"]:
        name = item["path"]
        relative(name)
        reserved = {"_archive_objects", "RESTORED_ARCHIVE.json", "RESTORE_FAILURE.log"}
        require(name not in aliases and name.split("/")[0] not in reserved, "Duplicate/reserved alias")
        aliases.add(name)
        require(item["sha256"] in objects, "Unknown alias object")
        require(item["bytes"] == objects[item["sha256"]]["bytes"], "Alias size mismatch")
    require(set(item["sha256"] for item in m["files"]) == set(objects), "Unreferenced object")
    for digest, item in objects.items():
        require(item["member"] == "objects/" + digest, "Unexpected tar member path")
        require(isinstance(item["bytes"], int) and item["bytes"] >= 0, "Invalid object length")
    require(m["parts"], "No parts")
    joined = hashlib.sha256()
    total = 0
    for i, part in enumerate(m["parts"], 1):
        name = "parts/part-" + str(i).zfill(6) + ".bin"
        require(part["path"] == name, "Unexpected part path/order")
        require(0 < part["bytes"] <= PART_BYTES, "Oversized or empty part")
        if i < len(m["parts"]):
            require(part["bytes"] == PART_BYTES, "Short interior part")
        path = packet / name
        regular(path)
        require(path.stat().st_size == part["bytes"], "Part size mismatch")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(CHUNK), b""):
                digest.update(block)
                joined.update(block)
                total += len(block)
        require(digest.hexdigest() == part["sha256"], "Part digest mismatch")
    require(total == m["archive"]["bytes"] and joined.hexdigest() == m["archive"]["sha256"],
            "Concatenated archive mismatch")
    return m


def read_objects(packet, manifest, destination=None):
    expected = manifest["objects"]
    seen = set()
    paths = [packet / p["path"] for p in manifest["parts"]]
    with io.BufferedReader(PartsReader(paths)) as joined:
        with gzip.GzipFile(fileobj=joined, mode="rb") as compressed:
            with tarfile.open(fileobj=compressed, mode="r|") as archive:
                for member in archive:
                    require(member.isreg(), "Archive contains a non-regular member")
                    require(member.name.startswith("objects/"), "Unknown archive member")
                    digest = member.name[len("objects/"):]
                    require(digest in expected and digest not in seen, "Unknown/duplicate object")
                    require(member.name == expected[digest]["member"], "Object member mismatch")
                    require(member.size == expected[digest]["bytes"], "Object size mismatch")
                    stream = archive.extractfile(member)
                    require(stream is not None, "Missing object stream")
                    target = (destination / digest).open("xb") if destination is not None else None
                    observed = hashlib.sha256()
                    count = 0
                    try:
                        for block in iter(lambda: stream.read(CHUNK), b""):
                            observed.update(block)
                            count += len(block)
                            if target is not None:
                                target.write(block)
                    finally:
                        stream.close()
                        if target is not None:
                            target.close()
                    require(count == member.size and observed.hexdigest() == digest, "Object content mismatch")
                    seen.add(digest)
    require(seen == set(expected), "Missing archive objects")
    return {"objects_verified": len(seen), "aliases_verified": len(manifest["files"])}


def build(result_path, out, release_path):
    result_path = result_path.resolve()
    require(not os.path.lexists(out), "Refusing existing build output")
    out = out.resolve()
    require(out != ROOT and ROOT in out.parents, "Build output must be inside archive owner directory")
    require(not out.exists(), "Refusing existing build output")
    regular(result_path)
    release_id = sha(release_path)
    release = json.loads(release_path.read_text())
    ids = {"archive_script_sha256": sha(__file__),
           "archive_spec_sha256": sha(ROOT / "ARCHIVE_SPEC.md"),
           "replay_result_sha256": sha(result_path)}
    require(release.get("allow") == "build", "No build release")
    require(all(release.get(k) == v for k, v in ids.items()), "Release identities differ")
    require(ids["replay_result_sha256"] == RESULT_SHA, "Unapproved actual replay")
    require(release.get("output_directory") == str(out), "Release output differs")
    files = inventory(result_path)
    out.mkdir(parents=True, exist_ok=False)
    try:
        for source, name in ((Path(__file__), "archive.py"), (ROOT / "ARCHIVE_SPEC.md", "ARCHIVE_SPEC.md"),
                             (release_path, "release.json")):
            shutil.copyfile(source, out / name)
        dump(out / "build_invocation.json", {"argv": sys.argv, "source_directory": str(result_path.parent), **ids})
        representatives = {}
        for item in files:
            representatives.setdefault(item["sha256"], item["path"])
        objects = {digest: {"member": "objects/" + digest,
                           "bytes": (result_path.parent / name).stat().st_size}
                   for digest, name in sorted(representatives.items())}
        archive_path = out / "actual-sample.tar.gz"
        with archive_path.open("xb") as raw:
            with gzip.GzipFile(filename="", fileobj=raw, mode="wb", compresslevel=9, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
                    for digest, item in objects.items():
                        member = tarfile.TarInfo(item["member"])
                        member.size = item["bytes"]
                        member.mode = 0o644
                        member.mtime = member.uid = member.gid = 0
                        member.uname = member.gname = ""
                        with (result_path.parent / representatives[digest]).open("rb") as stream:
                            archive.addfile(member, stream)
        parts = []
        (out / "parts").mkdir()
        with archive_path.open("rb") as stream:
            for i, block in enumerate(iter(lambda: stream.read(PART_BYTES), b""), 1):
                name = "parts/part-" + str(i).zfill(6) + ".bin"
                with (out / name).open("xb") as part:
                    part.write(block)
                parts.append({"path": name, "bytes": len(block), "sha256": hashlib.sha256(block).hexdigest()})
        manifest = {"format": "v3-exact-archive-v1", "part_bytes": PART_BYTES,
                    "source_result_sha256": ids["replay_result_sha256"],
                    "archive_script_sha256": ids["archive_script_sha256"],
                    "archive_spec_sha256": ids["archive_spec_sha256"],
                    "release_sha256": release_id, "files": files, "objects": objects,
                    "archive": {"format": "ustar+gzip-9-mtime0", "bytes": archive_path.stat().st_size,
                                "sha256": sha(archive_path)}, "parts": parts}
        dump(out / "manifest.json", manifest)
        with (out / "manifest.sha256").open("x") as sidecar:
            sidecar.write(sha(out / "manifest.json") + "  manifest.json\n")
        verified = read_objects(out, read_manifest(out))
        require(all(sha(result_path.parent / item["path"]) == item["sha256"] for item in files),
                "Input evidence changed during archive build")
        require(sha(__file__) == ids["archive_script_sha256"] and
                sha(ROOT / "ARCHIVE_SPEC.md") == ids["archive_spec_sha256"], "Archive source changed")
        require(sha(release_path) == release_id and sha(out / "release.json") == release_id,
                "Archive release changed")
        archive_path.unlink()
        result = {"all_passed": True, **verified, "part_count": len(parts),
                  "archive_bytes": manifest["archive"]["bytes"],
                  "original_file_bytes": sum(x["bytes"] for x in files),
                  "unique_object_bytes": sum(x["bytes"] for x in objects.values()),
                  "manifest_sha256": sha(out / "manifest.json"),
                  "archive_sha256": manifest["archive"]["sha256"],
                  "source_evidence_unchanged": True, "economic_execution": False}
        dump(out / "build_result.json", result)
        print(json.dumps(result, sort_keys=True))
    except BaseException:
        (out / "failure_traceback.log").write_text(traceback.format_exc())
        raise


def restore(packet, destination, expected):
    require(not os.path.lexists(destination), "Refusing existing restore destination")
    destination = destination.resolve()
    require(not destination.exists(), "Refusing existing restore destination")
    manifest = read_manifest(packet, expected)
    destination.mkdir(parents=True, exist_ok=False)
    object_dir = destination / "_archive_objects"
    object_dir.mkdir()
    try:
        verified = read_objects(packet, manifest, object_dir)
        for item in manifest["files"]:
            path = destination / item["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            with (object_dir / item["sha256"]).open("rb") as source, path.open("xb") as target:
                shutil.copyfileobj(source, target, CHUNK)
            require(path.stat().st_size == item["bytes"] and sha(path) == item["sha256"],
                    "Restored alias identity mismatch")
        shutil.rmtree(object_dir)
        dump(destination / "RESTORED_ARCHIVE.json", {"all_passed": True, **verified,
             "manifest_sha256": sha(packet / "manifest.json"), "original_file_bytes_preserved": True})
        print(json.dumps({"all_passed": True, "restored_to": str(destination), **verified}))
    except BaseException:
        (destination / "RESTORE_FAILURE.log").write_text(traceback.format_exc())
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    b = commands.add_parser("build")
    b.add_argument("--result", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--release", type=Path, required=True)
    for command in ("verify", "restore"):
        p = commands.add_parser(command)
        p.add_argument("--packet", type=Path, required=True)
        p.add_argument("--manifest-sha256")
        if command == "restore":
            p.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        build(args.result, args.out, args.release.resolve())
    elif args.command == "verify":
        manifest = read_manifest(args.packet, args.manifest_sha256)
        print(json.dumps({"all_passed": True, **read_objects(args.packet, manifest)}))
    else:
        restore(args.packet, args.destination, args.manifest_sha256)


if __name__ == "__main__":
    main()
