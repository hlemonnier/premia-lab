"""Restore approved archive bytes and verify their exact Git staging identities.

No branch refs, repository settings or historical objects are modified. Source
blobs remain in the private Git history preserved during consolidation. Only
already-indexed, sanitized archive objects can be repaired.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.archive_research import git_blob,sanitize

def inspect(repo:Path,archive:Path,repair:bool=False,staged:bool=False)->dict:
    repo=repo.resolve();archive=archive.resolve()
    index=json.loads((archive/'archive/index.json').read_text())
    entries={entry['object']:entry for snapshot in index['snapshots'] for entry in snapshot['files']}
    errors=[];restored=0;verified=0
    for name,entry in sorted(entries.items()):
        target=(archive/name).resolve()
        if not target.is_relative_to(archive):raise ValueError('Unsafe archive object path')
        current=target.read_bytes() if target.exists() else None
        valid=current is not None and hashlib.sha256(current).hexdigest()==entry['sha256'] and git_blob(current)==entry['published_blob']
        if not valid and repair:
            raw=subprocess.check_output(['git','-C',str(repo),'cat-file','blob',entry['source_blob']])
            if git_blob(raw)!=entry['source_blob']:raise RuntimeError('Invalid source blob')
            clean,redactions=sanitize(raw.decode('utf-8'));payload=clean.encode('utf-8')
            if git_blob(payload)!=entry['published_blob'] or hashlib.sha256(payload).hexdigest()!=entry['sha256']:
                raise RuntimeError('Source transformation no longer matches registered archive: '+name)
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
            restored+=1;valid=True
        if not valid:errors.append('Missing or altered archive bytes: '+name)
        if staged:
            relative=target.relative_to(repo).as_posix()
            row=subprocess.run(['git','-C',str(repo),'ls-files','--stage','--',relative],capture_output=True,text=True,check=True).stdout.strip()
            if not row:errors.append('Object not staged: '+relative)
            else:
                metadata,_=row.split('\t',1);mode,sha,stage=metadata.split()
                if stage!='0' or sha!=entry['published_blob']:errors.append('Staged object mismatch: '+relative)
                else:verified+=1
    return {'passed':not errors,'snapshots':len(index['snapshots']),'objects_checked':len(entries),'restored_objects':restored,'staged_objects_verified':verified,'errors':errors}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--archive',type=Path);p.add_argument('--repair',action='store_true');p.add_argument('--staged',action='store_true');a=p.parse_args()
    report=inspect(a.repo,a.archive or a.repo/'research',a.repair,a.staged)
    print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()
