"""Restore an archived experiment to its historical source layout (no private data)."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.archive_research import restore_snapshot

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--list',action='store_true');p.add_argument('--branch');p.add_argument('--output',type=Path);a=p.parse_args()
    source=ROOT/'research';index=source/'archive/index.json'
    if not index.exists():p.error('The archive has not been imported yet.')
    if a.list:
        for s in json.loads(index.read_text())['snapshots']:print(f"{s['branch']:55s} {len(s['files']):5d} files")
        return
    if not a.branch or not a.output:p.error('--branch and --output are required unless --list is used')
    restore_snapshot(source,a.branch,a.output)
    print(f'Restored {a.branch} to {a.output}; private benchmark inputs are intentionally absent.')
if __name__=='__main__':main()
