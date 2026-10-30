"""Archive research branch snapshots without publishing the private benchmark.

This is an organizational tool, not a model or a statistical validation.
The archive deduplicates file contents while keeping every branch/path mapping.
Binary inputs, third-party source, caches and private correspondence are omitted
from the public snapshot and listed explicitly. Original history stays private.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

TEXT_EXTENSIONS={'.py','.md','.txt','.json','.toml','.yaml','.yml','.csv','.tsv','.ini','.cfg','.sh','.rst','.cff','.log'}
PRIVATE_NAMES={'returns.csv','characteristics.csv','costs.csv','score.py','example_equal_weight.py','example_naive_mv.py'}
PRIVATE_ROOTS={'source','original_source','original_source_metadata','data','private_data','raw_data','.git','.github'}
PRIVATE_PARTS={'__pycache__','.venv','venv','node_modules'}
# Identities of the externally supplied specification/scorer/examples, not authored research.
THIRD_PARTY_BLOBS={'ec17c8be161b6dc5a5a8e6dd292fa3f7da349a9a','8625aa4d82d6fa08ecec32e7f8bbbc0efb6e1f4d','0f3662207fe4dbf8f7e9313fc959d146dc9b65bc','a19c95d0fef40734709983c3b97eead1e9e41357','8218c6edbe2c3600692bdfdd2a659e98465402e7','ff207b4c447f8ad5922524552dc25adfccf75dec'}
SECRET_PATTERNS=[
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{20,}\b'),
    re.compile(r'\bgithub_pat_[A-Za-z0-9_]{20,}\b'),
    re.compile(r'(?i)([?&](?:token|access_token|auth_token)=)[^\s\"\'<>&)]+'),
    re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),
]
EMAIL=re.compile(r'(?<![\w.-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])')

def git(repo:Path,*args:str,raw:bool=False):
    data=subprocess.check_output(['git','-C',str(repo),*args])
    return data if raw else data.decode('utf-8').strip()

def git_blob(data:bytes)->str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def path_reason(path:str,mode:str,sha:str,size:int)->str|None:
    p=PurePosixPath(path)
    if mode!='100644' and mode!='100755':return 'non_regular_file'
    if p.parts[0] in PRIVATE_ROOTS or sha in THIRD_PARTY_BLOBS:return 'third_party_source'
    if p.name.lower() in PRIVATE_NAMES:return 'benchmark_input_or_external_scorer'
    if any(part in PRIVATE_PARTS for part in p.parts):return 'generated_cache'
    if p.suffix.lower() in {'.eml','.mbox','.ics'} or 'email_thread' in path.lower():return 'private_correspondence'
    if p.name.startswith('.env') or 'credentials' in p.name.lower() or 'private_key' in p.name.lower():return 'credential_or_environment_file'
    if p.suffix.lower() not in TEXT_EXTENSIONS:return 'binary_or_unreviewed_asset'
    if size>4*1024*1024:return 'large_generated_text'
    return None

def sanitize(text:str)->tuple[str,list[str]]:
    changes=[]
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            changes.append('credential_redacted')
            text=pattern.sub(lambda m:(m.group(1) if m.lastindex else '')+'REDACTED',text)
    def replace_email(m):
        value=m.group(0)
        if value.endswith('@users.noreply.github.com'):return value
        changes.append('email_redacted');return '[redacted-email]'
    text=EMAIL.sub(replace_email,text)
    # Logs can contain local machine names and private Drive/account links.
    text,n=re.subn(r'https?://(?:mail\.google\.com|drive\.google\.com|docs\.google\.com)/[^\s<>\"\)]+','[private-link-removed]',text)
    if n:changes.append('private_cloud_link_removed')
    return text,sorted(set(changes))

def build_archive(repo:Path,heads:dict[str,str],destination:Path)->dict:
    destination.mkdir(parents=True,exist_ok=True)
    object_root=destination/'archive'/'objects';object_root.mkdir(parents=True,exist_ok=True)
    snapshots=[];cache={};report_candidates=[]
    for name,commit in sorted(heads.items()):
        if not re.fullmatch(r'[0-9a-f]{40}',commit):raise ValueError('Expected exact immutable commit identity')
        git(repo,'cat-file','-e',commit+'^{commit}')
        entries=[];excluded=[]
        for record in git(repo,'ls-tree','-r','-l','-z',commit,raw=True).split(b'\0'):
            if not record:continue
            meta,pathbytes=record.split(b'\t',1);mode,kind,sha,size=meta.decode().split()
            path=pathbytes.decode('utf-8');size=int(size) if size!='-' else 0
            if PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts:raise ValueError('Unsafe git tree path')
            reason=path_reason(path,mode,sha,size)
            if reason:excluded.append({'path':path,'source_blob':sha,'reason':reason});continue
            if sha not in cache:
                raw=git(repo,'cat-file','blob',sha,raw=True)
                if git_blob(raw)!=sha:raise ValueError('Git blob identity mismatch')
                try:text=raw.decode('utf-8')
                except UnicodeDecodeError:
                    cache[sha]=None
                else:
                    if '\0' in text:cache[sha]=None
                    elif '-----BEGIN PRIVATE KEY-----' in text or '-----BEGIN RSA PRIVATE KEY-----' in text:
                        cache[sha]=None
                    else:
                        clean,changes=sanitize(text);payload=clean.encode('utf-8');published=git_blob(payload)
                        extension=PurePosixPath(path).suffix.lower() or '.txt'
                        object_path=f'archive/objects/{published[:2]}/{published}{extension}'
                        output=destination/object_path;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(payload)
                        cache[sha]={'object':object_path,'published_blob':published,'sha256':hashlib.sha256(payload).hexdigest(),'sanitized':changes}
            stored=cache[sha]
            if stored is None:
                excluded.append({'path':path,'source_blob':sha,'reason':'non_text_or_private_key'});continue
            entry={'path':path,'source_blob':sha,'mode':mode,**stored};entries.append(entry)
            basename=PurePosixPath(path).name.upper()
            if path.endswith('.md') and any(k in basename for k in ['RESULT','SUMMARY','REVIEW','PLAN','REPRODUCE']):
                if path.startswith(('research/','verification/')):report_candidates.append((name,path,stored['object']))
        snapshots.append({'branch':name,'commit':commit,'files':entries,'excluded':excluded})
    result={'schema':1,'purpose':'Research archive; not a new backtest or untouched holdout','privacy':'Raw benchmark, external scorer, original brief, credentials and correspondence are not distributed. Original Git history must remain private.','snapshots':snapshots,'unique_source_blobs':len(cache),'unique_public_objects':len(list(object_root.rglob('*.*')))}
    (destination/'archive'/'index.json').write_text(json.dumps(result,indent=2)+'\n')
    # Human-readable directory: grouped by original branch, exact objects linked.
    lines=['# Experiment archive','','Every imported branch is indexed below, including failed research and verification work.','','The snapshots are content-addressed: repeated files are stored once. Source paths and all distinct versions remain in the index. The public archive omits third-party benchmark inputs, caches, binaries and private material; omissions are explicit, not missing experimental successes.','','Use `python tools/restore_research.py --list` to browse and `--branch NAME --output DIR` to restore a historical source layout. A restored workspace still needs its original private inputs and environment. It is not automatically an independently reproducible benchmark.','']
    for snapshot in snapshots:
        name=snapshot['branch'];slug=re.sub(r'[^a-zA-Z0-9_-]','-',name)
        folder=destination/'experiments'/slug;folder.mkdir(parents=True,exist_ok=True)
        rows=[f'# {name}','','Archived research snapshot. The current runtime remains the single N0 package at the project root.','',f"Source commit: `{snapshot['commit']}`.",f"Preserved text/source files: **{len(snapshot['files'])}**. Explicit omissions: **{len(snapshot['excluded'])}**.",'','## Reading guide','']
        chosen={}
        for branch,path,obj in report_candidates:
            if branch==name:chosen[path]=obj
        # Show all plans/results, with important reports first, not hidden winning subsets.
        for path,obj in sorted(chosen.items(),key=lambda pair:('RESULT' not in pair[0].upper() and 'SUMMARY' not in pair[0].upper(),pair[0])):
            rows.append(f'- [`{path}`](../../{obj})')
        if not chosen:rows.append('This snapshot contains release/maintenance code or an earlier reference. Its complete path mapping is in the archive index.')
        rows+=['','## Restore this snapshot','','```bash',f'python tools/restore_research.py --branch "{name}" --output /tmp/premia-experiment','```','','See [archive index](../../archive/index.json) for byte identities, publication redactions and omissions.','']
        (folder/'README.md').write_text('\n'.join(rows))
        lines.append(f"- [{name}](experiments/{slug}/README.md) — {len(snapshot['files'])} files; {len(snapshot['excluded'])} explicit omissions.")
    (destination/'ARCHIVE.md').write_text('\n'.join(lines)+'\n')
    audit=audit_snapshot(destination)
    if not audit['passed']:raise RuntimeError(audit)
    return result

def audit_snapshot(destination:Path)->dict:
    manifest=json.loads((destination/'archive/index.json').read_text());errors=[];checked=set()
    for snapshot in manifest['snapshots']:
        for entry in snapshot['files']:
            obj=entry['object']
            if obj in checked:continue
            checked.add(obj)
            path=(destination/obj).resolve()
            if not path.is_relative_to(destination.resolve()):errors.append('unsafe archive object');continue
            payload=path.read_bytes()
            if git_blob(payload)!=entry['published_blob'] or hashlib.sha256(payload).hexdigest()!=entry['sha256']:errors.append('object identity mismatch '+obj)
            text=payload.decode('utf-8')
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                # Query-string values were intentionally replaced with a stable marker.
                if any(m.group(0).split('=')[-1]!='REDACTED' for pattern in SECRET_PATTERNS for m in pattern.finditer(text)):errors.append('unredacted credential pattern '+obj)
    return {'passed':not errors,'objects_checked':len(checked),'snapshots':len(manifest['snapshots']),'errors':errors}

def restore_snapshot(archive:Path,branch:str,output:Path)->None:
    manifest=json.loads((archive/'archive/index.json').read_text())
    matches=[s for s in manifest['snapshots'] if s['branch']==branch]
    if len(matches)!=1:raise ValueError('Unknown snapshot: '+branch)
    if output.exists() and any(output.iterdir()):raise ValueError('Output must be a new or empty directory')
    output.mkdir(parents=True,exist_ok=True)
    for entry in matches[0]['files']:
        target=(output/entry['path']).resolve()
        if not target.is_relative_to(output.resolve()):raise ValueError('Unsafe path')
        source=archive/entry['object'];data=source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('Corrupt archive')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        if entry['mode']=='100755':target.chmod(0o755)
    (output/'PUBLIC_ARCHIVE_NOTICE.md').write_text('Restored authored research only. See the source index for omitted private/third-party inputs and any publication redactions. Historical research may require its original environment.\n')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--heads',type=Path,required=True);parser.add_argument('--output',type=Path,default=Path('research'))
    args=parser.parse_args();result=build_archive(args.repo,json.loads(args.heads.read_text()),args.output)
    print(json.dumps({'snapshots':len(result['snapshots']),'unique_public_objects':result['unique_public_objects'],'audit':audit_snapshot(args.output)},indent=2))
if __name__=='__main__':main()
