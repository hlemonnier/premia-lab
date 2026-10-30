"""Lead readback of the complete clean-folder discovery artifacts.

Scope follows the prospective handoff plan: exact package, original full-array
identities and full ledger equality. No model or protected period is executed.
"""
import csv
import datetime
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
destination = out/'summary.json'
if destination.exists(): raise FileExistsError(destination)
checks = []
result = {'status':'RUNNING','checks':checks,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'command':f'{sys.executable} {Path(__file__).resolve()}', 'model_executions':0,'audit_access':False}
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def check(name,ok,actual=None):
    checks.append({'name':name,'status':'PASS' if ok else 'FAIL','actual':actual})
    if not ok:raise AssertionError(name)
try:
    p=root/'evidence/handoff_discovery_001';s=read(p/'summary.json');w=read(p/'worker_summary.json')
    check('complete_workflow',s['status']==w['status']=='EXECUTED_PASS_SCOPE_ONLY' and s['exit_code']==w['exit_code']==0 and s['scorer_workflows']==1)
    check('all_recorded_checks',all(c['status']=='PASS' for c in s['checks']+w['checks']),len(s['checks']+w['checks']))
    for rel,m in read(p/'artifact_manifest.json').items():
        f=p/rel;check('artifact:'+rel,f.stat().st_size==m['bytes'] and sha(f)==m['sha256'])
    package=read(p/'package_manifest.json');selected=read(root/'research/VALIDATION_SELECTION.json')
    check('selected_identity',package['candidate_id']==selected['selected_candidate_id']=='C09_additive_long_memory' and package['selection_sha256']==sha(root/'research/VALIDATION_SELECTION.json') and package['config_sha256']==selected['config_sha256'])
    check('exact_member_set',set(package['files'])=={'strategy.py','model/__init__.py','model/strategy.py','model/portfolio.py'})
    for rel,digest in package['files'].items():
        check('current_package:'+rel,sha(root/'handoff'/rel)==digest)
        check('clean_package:'+rel,sha(p/'clean'/rel)==digest)
    original=read(root/'evidence/discovery_C09_001/summary.json')
    for name in ('forecasts.npy','targets.npy','held_books.npy'):
        check('historical_array:'+name,sha(p/name)==original['output_arrays'][name]['sha256'],sha(p/name))
    with (p/'daily.csv').open(newline='') as f:new=list(csv.DictReader(f))
    with (root/'evidence/discovery_C09_001/daily.csv').open(newline='') as f:old=list(csv.DictReader(f))
    keys=('gross_return','full_cost','net_return','closing_target_gross','raw_market_return')
    check('all_original_economic_rows',len(new)==len(old)==1762 and all(int(a['return_index'])==int(b['return_index'])==i+253 and all(float(a[k])==float(b[k]) for k in keys) for i,(a,b) in enumerate(zip(new,old))),len(new))
    check('discovery_only',w['numeric_input_slice']==[0,2016] and w['score_mask']==[253,2015])
    result.update(status='EXECUTED_PASS_SCOPE_ONLY',exit_code=0,package_manifest_sha256=sha(p/'package_manifest.json'),source_summary_sha256=sha(p/'summary.json'))
except Exception:
    import traceback
    result.update(status='EXECUTED_FAIL',exit_code=1,error=traceback.format_exc())
finally:
    result.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),review_source_sha256=sha(Path(__file__)),limitations=['Complete saved-artifact equivalence, not a new model execution or universal causal/overfit proof.'])
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'exit_code':result['exit_code'],'checks':len(checks),'error':result.get('error')}))
raise SystemExit(result['exit_code'])
