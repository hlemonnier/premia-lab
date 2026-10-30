"""Verify the public project tree without claiming economic validation."""
from __future__ import annotations
import ast,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.archive_research import audit_snapshot, SECRET_PATTERNS

def main():
    errors=[];manifest=json.loads((ROOT/'docs/runtime_manifest.json').read_text())
    for path,expected in manifest.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:errors.append('Frozen runtime changed: '+path)
    module=ast.parse((ROOT/'strategy.py').read_text())
    if ast.get_docstring(module):module.body=module.body[1:]
    if hashlib.sha256(ast.dump(module).encode()).hexdigest()!=(ROOT/'docs/entrypoint_ast.sha256').read_text().strip():errors.append('Entrypoint executable changed')
    for forbidden in ['model_f','gls_alpha.py','returns.csv','costs.csv','characteristics.csv','score.py','source']:
        if (ROOT/forbidden).exists():errors.append('Forbidden public root: '+forbidden)
    if (ROOT/'research/archive/index.json').exists():
        archive=audit_snapshot(ROOT/'research')
        errors+=archive['errors']
    else:archive={'status':'not_imported_yet'}
    # Validate maintained documentation links; archival references are historical.
    broken=[]
    for doc in [ROOT/'README.md',ROOT/'research/README.md',*sorted((ROOT/'docs').glob('*.md'))]:
        for link in re.findall(r'(?<!!)\[[^\]]*\]\(([^ )]+)(?:\s+[^)]*)?\)',doc.read_text()):
            if link.startswith(('http:','https:','#','mailto:')):continue
            target=(doc.parent/link.split('#')[0])
            if not target.exists():
                if 'archive/' in link or link=='ARCHIVE.md':continue # import runs after the initial packaging commit
                broken.append(f'{doc.relative_to(ROOT)} -> {link}')
    errors+=broken
    report={'passed':not errors,'frozen_runtime_files':len(manifest),'entrypoint_ast_verified':True,'archive':archive,'errors':errors,'economic_claim':False}
    print(json.dumps(report,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
