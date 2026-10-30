"""Publish a NEW clean snapshot, never the legacy repository's private history.

Default: validate and explain the proposed publication, without a remote write.
Explicit --publish: create OWNER/premia-lab with one root commit and branch main.
Requires GitHub CLI authentication on the operator's machine. No token is read,
printed, stored or requested by this script. The legacy repository is unchanged.
"""
from __future__ import annotations
import argparse,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def command(args,cwd=None,check=True):
    return subprocess.run(args,cwd=cwd,check=check,text=True,capture_output=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--name',default='premia-lab');p.add_argument('--publish',action='store_true');a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',a.name):p.error('Invalid repository name')
    if not (ROOT/'research/archive/index.json').exists():p.error('Consolidate the research archive before publication.')
    checked=command([sys.executable,'tools/check_project.py'],ROOT)
    print(checked.stdout,end='')
    if not a.publish:
        print(f'DRY RUN: a new public {a.name} repository would contain the reviewed working tree, one new commit and only main. The legacy repository and its private history would stay private.')
        return
    for tool in ('git','gh'):
        if not shutil.which(tool):p.error(f'{tool} is required. Install it and authenticate with gh auth login; do not paste credentials into chat.')
    command(['gh','auth','status'])
    user=json.loads(command(['gh','api','user']).stdout);owner=user['login'];target=f'{owner}/{a.name}'
    existing=command(['gh','api',f'repos/{target}'],check=False)
    if existing.returncode==0:p.error('Destination already exists; refusing to overwrite it: '+target)
    if '404' not in existing.stderr+existing.stdout:p.error('Could not verify that the destination is available.')
    status=command(['git','status','--porcelain','--untracked-files=no'],ROOT).stdout
    if status.strip():p.error('Commit or discard tracked working-tree changes before publication.')
    # Use tracked files at HEAD only. No .git directory, reflog or parent commit is copied.
    paths=command(['git','ls-tree','-r','--name-only','HEAD'],ROOT).stdout.splitlines()
    with tempfile.TemporaryDirectory(prefix='premia-public-') as temporary:
        clean=Path(temporary)
        for name in paths:
            if name in {'tools/consolidate_remote.py','research/import_plan.json','.github/workflows/organize-research.yml'}:continue
            destination=(clean/name).resolve()
            if not destination.is_relative_to(clean.resolve()):raise RuntimeError('Unsafe tracked path')
            destination.parent.mkdir(parents=True,exist_ok=True)
            payload=subprocess.check_output(['git','show',f'HEAD:{name}'],cwd=ROOT)
            destination.write_bytes(payload)
        command(['git','init','-b','main'],clean)
        command(['git','config','user.name',user.get('name') or owner],clean)
        command(['git','config','user.email',f"{user['id']}+{owner}@users.noreply.github.com"],clean)
        command(['git','add','.'],clean)
        command(['git','commit','-m','Initial public research snapshot: Premia Lab'],clean)
        command(['gh','repo','create',target,'--public','--source',str(clean),'--remote','origin','--push','--description','Causal forecasts, conditional risk and cost-aware portfolio research. Reproducible synthetic demo and an inspectable experiment archive.'],clean)
        command(['gh','repo','edit',target,'--add-topic','quantitative-finance','--add-topic','portfolio-optimization','--add-topic','factor-models','--add-topic','python','--add-topic','research'],clean)
        info=json.loads(command(['gh','api',f'repos/{target}']).stdout)
        branches=json.loads(command(['gh','api',f'repos/{target}/branches']).stdout)
        if info['private'] or [b['name'] for b in branches]!=['main']:raise RuntimeError('Publication verification failed; inspect repository settings.')
        print(json.dumps({'public_repository':info['html_url'],'visibility':'public','branches':['main'],'private_history_copied':False},indent=2))
if __name__=='__main__':main()
