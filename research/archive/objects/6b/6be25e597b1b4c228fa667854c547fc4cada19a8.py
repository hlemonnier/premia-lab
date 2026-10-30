"""E2E portability and invariants audit, within the frozen release plan."""
from __future__ import annotations
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import ast,hashlib,json
from pathlib import Path
import numpy as np
import runner as V
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
from release_e2e import check,exercise
root=V.ROOT;work=args.work;source=args.source
checks=[];imports={};forbidden=[]
for f in (root/'handoff_f').rglob('*.py'):
    names=[]
    for node in ast.walk(ast.parse(f.read_text())):
        if isinstance(node,ast.Import): names += [a.name for a in node.names]
        if isinstance(node,ast.ImportFrom) and node.level==0 and node.module:names.append(node.module)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('open','eval','exec','compile','__import__'):forbidden.append(str(f))
    imports[str(f.relative_to(root/'handoff_f'))]=names
allowed={'__future__','math','warnings','numpy','sklearn','model_f'}
checks.append({'name':'only declared installed imports','passed':all(n.split('.')[0] in allowed for ns in imports.values() for n in ns)})
checks.append({'name':'no disk/network/code-loading entry points','passed':not forbidden})
for n in ('__init__.py','engine.py','allocator.py','policy.py'):
    checks.append({'name':'unchanged V3 '+n,'passed':(root/'handoff_v3/model_v3'/n).read_bytes()==(root/'handoff_f/model_f'/n).read_bytes()})
# Exact AST identity of the statistical and fitting functions, not similarity of descriptions.
a=ast.parse((root/'research/wave6/wave6_models.py').read_text());b=ast.parse((root/'handoff_f/model_f/factor_risk.py').read_text())
for n in ('sufficient_statistics','fitted_multipliers','_RescaledState','_RescaledBook'):
    aa=next(x for x in a.body if getattr(x,'name',None)==n);bb=next(x for x in b.body if getattr(x,'name',None)==n)
    checks.append({'name':'unchanged F AST '+n,'passed':ast.dump(aa)==ast.dump(bb)})
score=V.module(source/'score.py','invariant_scorer');p=V.load_policy('release');rng=np.random.default_rng(20261101);T,N=420,48
R=rng.normal(0,.005,(T,N));X=rng.normal(size=(1,N,13))+np.cumsum(rng.normal(0,.02,(T,N,13)),axis=0);c=np.linspace(.0002,.0008,N)
f,w,rows=exercise(p,R,X,c,score)
perm=rng.permutation(N);iv=np.argsort(perm)
ff,ww,rr=exercise(p,R[:,perm],X[:,perm],c[perm],score)
check(checks,'standalone asset permutation alpha',ff[:,:N][:,iv],f[:,:N]);check(checks,'standalone asset permutation risk',ff[:,N:],f[:,N:]);check(checks,'standalone asset permutation weights',ww[:,iv],w,tol=1e-8);check(checks,'standalone asset permutation economics',rr[:,[0,1,3]],rows[:,[0,1,3]])
checks.append({'name':'matured label manifests','passed':all(r['last_label']<r['target_row'] and r['latest_feature_row']<r['last_label'] for r in p.POLICY.training_records)})
# Shape-generalization operational checks; no economic claim on tiny stock universes.
for N in (1,13):
    rr=rng.normal(0,.002,(420,N));xx=rng.normal(size=(420,N,13));cc=np.full(N,.0005)
    ff,ww,rs=exercise(p,rr,xx,cc,score)
    checks.append({'name':f'{N}-stock complete workflow','passed':bool(np.isfinite(ff).all() and np.isfinite(ww).all() and np.isfinite(rs).all())})
# Explicit state contract: failure on skipping rows rather than silently reusing a book.
f=p.forecast(R,X);p.rebalance(np.zeros(48),f[253],R[:253],X[:253],c)
try:p.rebalance(np.zeros(48),f[255],R[:255],X[:255],c);failed=False
except RuntimeError:failed=True
checks.append({'name':'nonsequential session rejected','passed':failed})
res={'imports':imports,'checks':checks,'passed':all(v['passed'] for v in checks)};V.write(work/'checks/package_audit.json',res);print(json.dumps(res),flush=True);assert res['passed']
