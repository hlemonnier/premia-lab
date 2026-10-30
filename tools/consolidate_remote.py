"""One-time, user-authorized branch consolidation inside the PRIVATE legacy repo.

Archive first; validate; commit with every imported head as a parent; only then
delete the exact recorded remote branch refs with leases. Original history is
retained privately, not erased. This tool never changes repository visibility.
"""
from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.archive_research import build_archive,audit_snapshot,git

def remote_heads():
    rows=git(ROOT,'ls-remote','--heads','origin').splitlines()
    return {line.split()[1].removeprefix('refs/heads/'):line.split()[0] for line in rows}

def main():
    if os.environ.get('GITHUB_REPOSITORY')!='hlemonnier/continual-research-takehome':raise RuntimeError('Restricted to the authorized private legacy repository')
    expected=os.environ['GITHUB_SHA'];heads=json.loads((ROOT/'research/import_plan.json').read_text())
    before=remote_heads()
    if before.get('main')!=expected:raise RuntimeError('main advanced; refusing concurrent changes')
    for name,sha in heads.items():
        if name!='main' and before.get(name)!=sha:raise RuntimeError('Branch changed or disappeared: '+name)
    subprocess.run(['git','fetch','origin','+refs/heads/*:refs/remotes/origin/*'],cwd=ROOT,check=True)
    result=build_archive(ROOT,heads,ROOT/'research')
    if not audit_snapshot(ROOT/'research')['passed']:raise RuntimeError('Archive verification failed')
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'tools/check_project.py'],cwd=ROOT,check=True)
    report={'imported_snapshots':len(result['snapshots']),'unique_public_objects':result['unique_public_objects'],
            'recorded_file_mappings':sum(len(s['files']) for s in result['snapshots']),
            'explicit_omissions':sum(len(s['excluded']) for s in result['snapshots']),
            'private_history_retained':True,'repository_visibility_changed':False,'rename_performed':False,
            'note':'Do not make the legacy repository public: original third-party material is retained in its history. Use the clean-snapshot publisher.'}
    (ROOT/'research/MIGRATION.json').write_text(json.dumps(report,indent=2)+'\n')
    # Remove the temporary migration workflow, not the maintained CI.
    (ROOT/'.github/workflows/organize-research.yml').unlink()
    subprocess.run(['git','add','research','.github/workflows/organize-research.yml'],cwd=ROOT,check=True)
    tree=git(ROOT,'write-tree')
    parents=list(dict.fromkeys([expected,*heads.values()]))
    command=['git','commit-tree',tree]
    for parent in parents:command+=['-p',parent]
    command+=['-m','research: consolidate all branch snapshots into the documented archive']
    new=subprocess.check_output(command,cwd=ROOT,text=True).strip()
    if remote_heads().get('main')!=expected:raise RuntimeError('main advanced before archive publication')
    subprocess.run(['git','push','origin',new+':refs/heads/main'],cwd=ROOT,check=True)
    # All original objects remain reachable through merge parents before refs are removed.
    for name,sha in heads.items():
        subprocess.run(['git','merge-base','--is-ancestor',sha,new],cwd=ROOT,check=True)
    delete=[(name,sha) for name,sha in heads.items() if name!='main']
    current=remote_heads()
    if current.get('main')!=new:raise RuntimeError('main advanced before cleanup; leave branches intact')
    for name,sha in delete:
        if current.get(name)!=sha:raise RuntimeError('Branch moved before cleanup: '+name)
    args=['git','push','--atomic']
    args += [f'--force-with-lease=refs/heads/{name}:{sha}' for name,sha in delete]
    args += ['origin',*[f':refs/heads/{name}' for name,_ in delete]]
    subprocess.run(args,cwd=ROOT,check=True)
    remaining=remote_heads()
    print(json.dumps({'archived_commit':new,'deleted_branches':[name for name,_ in delete],'remaining_heads':remaining,'archive_report':report},indent=2))
    if set(remaining)!={'main'}:raise RuntimeError('Additional new branches exist; they were not deleted without authorization')
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as f:
            f.write(f"## Research consolidation complete\n\nArchived {len(result['snapshots'])} snapshots; deleted {len(delete)} verified branch refs. Only main remains.\n\nPrivate history is retained. Visibility and repository name were not changed.\n")
if __name__=='__main__':main()
