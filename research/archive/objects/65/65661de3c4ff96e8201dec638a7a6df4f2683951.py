"""Root-approved byte-exact recovery of one recorded transient artifact.

No model execution, manifest/source/summary change, or tolerance change.
The file is created exclusively from a proven canonical byte prefix.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shlex
import sys
import traceback

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PACKET=ROOT/"evidence/audit_C09_001"
RELATIVE="inputs/.characteristics.npy.g4GTIG.3yQoQL"
COUNT=214433792
DIGEST="35ffdd2b0a27b2c58aa2bb5ad2680b44caa3ad00a4ffc4820ee700771b01a7e5"
MANIFEST_SHA="2e1aff5ae8e1257a6abef712b821e4859778dd20f0bb60f2a9903cf0c350d95b"


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


def identities():
    return {str(p.relative_to(ROOT)):sha(p) for p in [
        PACKET/"inputs/returns.npy",PACKET/"inputs/characteristics.npy",PACKET/"inputs/costs.npy",
        PACKET/"artifact_manifest.json",PACKET/"summary.json",PACKET/"runner_used.py",
        ROOT/"tools/review_audit_evidence.py",ROOT/"research/AUDIT_NOMINATION.json"]}


record={"started_utc":datetime.now(timezone.utc).isoformat(),"command":shlex.join([sys.executable,str(Path(__file__).resolve())]),
        "authorization":"Root explicitly authorized exact prefix recovery and unchanged reviewer rerun after preserving failure001.",
        "source_sha256":sha(Path(__file__).resolve()),"relative_artifact":RELATIVE,"expected_bytes":COUNT,"expected_sha256":DIGEST,
        "origin":"Unresolved; recorded bytes match a canonical file prefix. No specific infrastructure cause asserted.",
        "model_executions":0,"manifest_or_gate_changes":False,"exclusive_create_mode":"xb"}
destination=OUT/"recovery.json"
if destination.exists():
    raise FileExistsError(destination)
code=1
try:
    record["before"]=identities()
    assert sha(PACKET/"artifact_manifest.json")==MANIFEST_SHA
    manifest=json.loads((PACKET/"artifact_manifest.json").read_text())
    assert manifest[RELATIVE]=={"sha256":DIGEST,"bytes":COUNT}
    record["artifact_existed_before"]=(PACKET/RELATIVE).exists()
    assert not record["artifact_existed_before"]
    remaining=COUNT
    with (PACKET/"inputs/characteristics.npy").open("rb") as source, (PACKET/RELATIVE).open("xb") as target:
        while remaining:
            block=source.read(min(1<<20,remaining))
            if not block:
                raise EOFError("Canonical input shorter than frozen prefix")
            target.write(block)
            remaining-=len(block)
    record["restored"]={"sha256":sha(PACKET/RELATIVE),"bytes":(PACKET/RELATIVE).stat().st_size}
    assert record["restored"]==manifest[RELATIVE]
    record["after"]=identities()
    assert record["before"]==record["after"]
    record["status"],code="RESTORED_EXACT_ORIGINAL_ARTIFACT",0
except Exception:
    record["status"]="RECOVERY_FAILED"
    record["error"]=traceback.format_exc()
finally:
    record["finished_utc"]=datetime.now(timezone.utc).isoformat()
    record["exit_code"]=code
    destination.write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record,indent=2))
raise SystemExit(code)
