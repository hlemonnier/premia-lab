"""Independent readback of both complete pre-access controller workflows.

Uses the prospective PROTECTED_REPLAY_PLAN expectations. This examines complete
saved E2E artifacts; it does not execute a model, create unit tests, or read a
protected market interval.
"""
from pathlib import Path
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import shlex
import sys

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DEST = OUT / 'summary.json'
if DEST.exists():
    raise FileExistsError(DEST)
checks = []
result = {'status': 'RUNNING', 'checks': checks, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'command': shlex.join([sys.executable, str(Path(__file__).resolve())]),
          'scope': 'Independent saved-output readback of discovery parity and fully synthetic zero E2Es',
          'protected_market_observations_read': False}

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text())

def check(name, passed, actual):
    checks.append({'name': name, 'status': 'PASS' if passed else 'FAIL', 'actual': actual})
    if not passed:
        raise AssertionError(name)

def close(a, b):
    return bool(a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all()
                and np.all(np.abs(a-b) <= 1e-14 + 1e-12*np.abs(b)))

try:
    helper_path = ROOT / 'tools/run_candidate.py'
    check('metric_helper_identity', sha(helper_path) == '6d34f2e9779ee50ab3a376e0f096c9524d09c3576649952c117fab32cb692f69', sha(helper_path))
    spec = importlib.util.spec_from_file_location('readback_metric_helper', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    result['input_packets'] = {}
    for name, days, synthetic in [('protected_replay_discovery_001', 2016, False), ('protected_replay_zero_001', 3024, True)]:
        p = ROOT / 'evidence' / name
        s = read(p/'summary.json')
        result['input_packets'][name] = {'summary_sha256': sha(p/'summary.json'), 'artifact_manifest_sha256': sha(p/'artifact_manifest.json')}
        check(name+':completed', s['status'] == 'EXECUTED_PASS_SCOPE_ONLY' and s['exit_code'] == 0, s['status'])
        check(name+':unopened', not any(s[k] for k in ('protected_numeric_access_started', 'validation_opened', 'audit_opened')), False)
        check(name+':controller', sha(p/'runner_used.py') == 'd3c3cfd4a1fde10398fc5546f3dc48d395f68a4c06fbe73311c8b5c2cdc37dfe', sha(p/'runner_used.py'))
        check(name+':reported_checks', all(c['status'] == 'PASS' for c in s['checks']), len(s['checks']))
        manifest = read(p/'artifact_manifest.json')
        for rel, meta in manifest.items():
            q = p/rel
            check(name+':artifact:'+rel, q.stat().st_size == meta['bytes'] and sha(q) == meta['sha256'], meta['sha256'])
        r = np.load(p/'inputs/returns.npy', mmap_mode='r')
        x = np.load(p/'inputs/characteristics.npy', mmap_mode='r')
        c = np.load(p/'inputs/costs.npy', mmap_mode='r')
        f = np.load(p/'forecasts.npy', mmap_mode='r')
        t = np.load(p/'targets.npy', mmap_mode='r')
        h = np.load(p/'held_books.npy', mmap_mode='r')
        check(name+':arrays', r.shape == (days,1000) and x.shape == (days,1000,13) and c.shape == (1000,)
              and f.shape == (days,1000) and t.shape == h.shape == (days-253,1000)
              and all(np.isfinite(a).all() for a in (r,x,c,f,t,h)), [list(a.shape) for a in (r,x,c,f,t,h)])
        check(name+':canonical_layout', r.flags.f_contiguous and x.flags.c_contiguous, [list(r.strides),list(x.strides)])
        with (p/'daily.csv').open(newline='') as stream:
            daily = list(csv.DictReader(stream))
        indices = np.array([int(row['return_index']) for row in daily])
        fields = ('gross_return','full_cost','closing_target_gross','raw_market_return','official_instrumented_rebalance_seconds')
        rows = np.array([[float(row[k]) for k in fields] for row in daily])
        net = np.array([float(row['net_return']) for row in daily])
        check(name+':full_indices', np.array_equal(indices,np.arange(253,days-1)), len(indices))
        check(name+':net_identity', np.array_equal(net,rows[:,0]-rows[:,1]), True)
        gross = np.einsum('ij,ij->i',t[:-1],r[indices])
        drift = t[:-1]*(1+r[indices])/(1+gross[:,None])
        fees = np.abs(t[1:]-drift) @ c
        market = np.mean(r[indices],axis=1)
        check(name+':full_gross', close(gross,rows[:,0]), float(np.max(np.abs(gross-rows[:,0]))))
        check(name+':full_drift', close(drift,h[1:]), float(np.max(np.abs(drift-h[1:]))))
        check(name+':full_cost', close(fees,rows[:,1]), float(np.max(np.abs(fees-rows[:,1]))))
        check(name+':full_market', close(market,rows[:,3]), float(np.max(np.abs(market-rows[:,3]))))
        check(name+':gross_exposure', close(np.abs(t[1:]).sum(axis=1),rows[:,2]), True)
        check(name+':empty_opening', np.count_nonzero(h[0]) == 0, int(np.count_nonzero(h[0])))
        check(name+':path_controls', np.max(np.abs(t)) <= .01+1e-12 and np.abs(t).sum(axis=1).max() <= 1+1e-12
              and np.all(net > -1), {'max_stock': float(np.abs(t).max()), 'max_gross': float(np.abs(t).sum(axis=1).max())})
        for period, bounds in s['score_masks'].items():
            start,stop = bounds
            m = (indices >= start)&(indices < stop)
            metrics = helper.summarize_rows(rows[m],indices[m])
            check(name+':metric_recomputation:'+period, metrics == s['metrics'][period], metrics)
            if synthetic:
                check(name+':null_ratios:'+period, metrics['net_sharpe'] is None and metrics['gross_sharpe'] is None
                      and metrics['realized_net_market_beta'] is None, metrics['undefined_metrics'])
        if synthetic:
            check(name+':zero_path', all(np.count_nonzero(a)==0 for a in (r,x,f,t,h,rows[:,:4],net)), True)
            check(name+':positive_costs', np.array_equal(c,np.full(1000,1e-5)), True)
        else:
            original = read(ROOT/'evidence/discovery_C06_001/summary.json')
            for filename in ('forecasts.npy','targets.npy','held_books.npy'):
                check(name+':original_array:'+filename, sha(p/filename) == original['output_arrays'][filename]['sha256'], sha(p/filename))
            with (ROOT/'evidence/discovery_C06_001/daily.csv').open(newline='') as stream:
                old = list(csv.DictReader(stream))
            expected = np.array([[float(row[k]) for k in fields[:4]] for row in old])
            check(name+':original_economics', np.array_equal(rows[:,:4],expected), float(np.max(np.abs(rows[:,:4]-expected))))
    result['status'], result['exit_code'] = 'EXECUTED_PASS_SCOPE_ONLY', 0
except Exception:
    import traceback
    result['status'], result['exit_code'] = 'EXECUTED_FAIL', 1
    result['error'] = traceback.format_exc()
finally:
    result['reviewer_source_sha256'] = sha(__file__)
    result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result['limitations'] = ['Saved complete-workflow evidence only; no universal causality or no-overfit claim.',
                             'No actual validation or audit observations were read.']
    DEST.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'exit_code':result['exit_code'],'checks':len(checks),'error':result.get('error')}))
raise SystemExit(result['exit_code'])
