"""Independent observational workflows specified in PLAN.md; no strategy changes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SNAPSHOT = Path('/workspace/scratch/a83c191d516f/v2-followup-snapshot')
DATA = Path('/workspace/scratch/a83c191d516f/v2-original-input/extracted/Quant Research Take-Home')
SOURCE_FILES = [
    'handoff_v2/strategy.py', 'handoff_v2/model_v2/__init__.py',
    'handoff_v2/model_v2/engine.py', 'handoff_v2/model_v2/allocator.py',
    'verification/v2_package_checks.py', 'source/Quant Research Take-Home/score.py',
    'research/v2/beta_correction_diagnostic.py',
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def independent_beta(W):
    market = W.mean(axis=1)
    mc = market - market.mean()
    centered = W - W.mean(axis=0)
    return (mc @ centered) / (mc @ mc)


def readback():
    p = DATA / 'returns.csv'
    R = np.ascontiguousarray(pd.read_csv(p, index_col='day').to_numpy(np.float64))
    T = len(R)
    grid = list(range(252, T - 251, 21))
    pair_slopes = {}
    for s in grid:
        if s + 252 <= T:
            pre = independent_beta(R[s-252:s])
            post = independent_beta(R[s:s+252])
            x = pre - pre.mean()
            pair_slopes[s] = float(x @ (post - post.mean()) / (x @ x))
    rows = []
    for t in range(504, T - 251, 21):
        completed = [s for s in pair_slopes if s + 252 <= t]
        eta = 1.0 - float(np.mean([pair_slopes[s] for s in completed]))
        raw = independent_beta(R[t-252:t])
        corrected = (1-eta)*raw + eta*raw.mean()
        future = independent_beta(R[t:t+252])
        rows.append(dict(t=t, eta=eta, mse_raw=float(np.mean((raw-future)**2)),
                         mse_corrected=float(np.mean((corrected-future)**2)),
                         completed_pair_count=len(completed),
                         newest_training_s=max(completed),
                         newest_training_end_exclusive=max(completed)+252,
                         evaluated_future_end_exclusive=t+252,
                         submitted_sample=bool(t < T-252)))
    frame = pd.DataFrame(rows)
    frame.to_csv(HERE/'beta_mse_by_date.csv', index=False)
    exact = frame[frame.submitted_sample].reset_index(drop=True)

    def summarize(f):
        return dict(dates=len(f), eta_first=float(f.iloc[0].eta), eta_last=float(f.iloc[-1].eta),
                    mse_raw=float(f.mse_raw.mean()), mse_corrected=float(f.mse_corrected.mean()),
                    share_of_dates_corrected_better=float((f.mse_corrected<f.mse_raw).mean()))

    actual = summarize(exact)
    submitted = json.loads((SNAPSHOT/'research/v2/results/beta_correction_diagnostic.json').read_text())
    differences = {k: abs(float(actual[k])-float(submitted[k])) for k in actual}
    phases = []
    for phase in range(12):
        sub = exact.iloc[phase::12]
        d = summarize(sub)
        d.update(phase=phase, first_t=int(sub.iloc[0].t), last_t=int(sub.iloc[-1].t),
                 mean_paired_mse_difference=float((sub.mse_corrected-sub.mse_raw).mean()))
        phases.append(d)
    result = dict(input=dict(csv_sha256=sha(p.read_bytes()), array_sha256=sha(R.tobytes()), shape=list(R.shape), dtype=str(R.dtype)),
                  submitted=submitted, independently_recomputed=actual,
                  aggregate_absolute_differences=differences,
                  reproduction_within_1e_12=all(v<=1e-12 for v in differences.values()),
                  all_training_labels_mature=bool((frame.newest_training_end_exclusive<=frame.t).all()),
                  adjacent_future_window_overlap_days=231,
                  descriptive_phase_cohorts=phases,
                  boundary_sensitivity=dict(omitted_dates=frame[~frame.submitted_sample].to_dict(orient='records'),
                                            summary_including_endpoint=summarize(frame)))
    save_json(HERE/'beta_mse_readback.json', result)
    if not result['reproduction_within_1e_12'] or not result['all_training_labels_mature']:
        raise AssertionError('Beta readback differs from specified expectation')
    return result


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def e2e():
    clean = HERE/'source'
    manifest = {}
    for name in SOURCE_FILES:
        src = SNAPSHOT/name
        dst = clean/name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        manifest[name] = sha(src.read_bytes())
    save_json(HERE/'source_manifest.json', manifest)
    checks = load_module('provided_package_workflow', clean/'verification/v2_package_checks.py')
    scorer = checks.load_score()
    R, X, cost = checks.fixture(20261028, T=820, N=96)
    cut = 650
    rng = np.random.default_rng(73111)
    R2, X2 = R.copy(), X.copy()
    R2[cut:] = rng.normal(0.0002, 0.03, R2[cut:].shape)
    X2[cut:] = rng.normal(0, 1, X2[cut:].shape)
    np.savez_compressed(HERE/'inputs.npz', R=R, X=X, cost=cost, R_future=R2, X_future=X2)
    cases = {'baseline':(R, X), 'future':(R2, X2),
             'future_X_fortran':(R2, np.asfortranarray(X2)),
             'future_both_fortran':(np.asfortranarray(R2), np.asfortranarray(X2)),
             'prefix':(R[:cut], X[:cut])}
    output = {}
    metrics = {}
    for name, (r, x) in cases.items():
        S = checks.load_strategy(str(clean/'handoff_v2'))
        eng = sys.modules['model_v2.engine']
        eng.configure({**S._CONFIG, 'beta_shrinkage':True, 'beta_target':0.05})
        f, w, rows = checks.record(S, scorer, r, x, cost, start=252)
        output[name] = (f,w,rows)
        np.savez_compressed(HERE/f'{name}.npz', forecasts=f, targets=w, rows=rows)
        certificates = eng.CERTIFICATES
        metrics[name] = dict(forecast_shape=list(f.shape), target_shape=list(w.shape),
                             ledger_shape=list(rows.shape),
                             certificates={s:sum(c.get('status')==s for c in certificates)
                                           for s in ('ok','ok_after_recovery','not_certified')})
    baseline=output['baseline']
    comparisons={}
    for name in ('future','future_X_fortran','future_both_fortran','prefix'):
        f,w,r=output[name]
        nf = len(f) if name=='prefix' else cut+1
        nw = len(w) if name=='prefix' else cut-252
        nr = len(r) if name=='prefix' else cut-253
        pairs={'forecasts':(baseline[0][:nf],f[:nf]), 'targets':(baseline[1][:nw],w[:nw]),
               'economic_columns':(baseline[2][:nr,:4],r[:nr,:4])}
        comparisons[name]={}
        for k,(a,b) in pairs.items():
            tol=1e-12 if name=='future_both_fortran' and k!='forecasts' else 0.0
            maxdiff=float(np.max(np.abs(a-b)))
            comparisons[name][k]=dict(equal=bool(np.array_equal(a,b)), max_abs_diff=maxdiff,
                                      tolerance=tol, pass_expected=bool(maxdiff<=tol),
                                      compared_shape=list(a.shape))
    eng=sys.modules['model_v2.engine']
    eta_at_cut=float(eng._EtaTracker().eta(R,cut))
    all_equal=all(d['equal'] for case in comparisons.values() for d in case.values())
    all_pass=all(d['pass_expected'] for case in comparisons.values() for d in case.values())
    later_changed=dict(forecasts=bool(np.any(baseline[0][cut+1:]!=output['future'][0][cut+1:])),
                       targets=bool(np.any(baseline[1][cut-252:]!=output['future'][1][cut-252:])))
    source_after={name:sha((SNAPSHOT/name).read_bytes()) for name in SOURCE_FILES}
    copied_after={name:sha((clean/name).read_bytes()) for name in SOURCE_FILES}
    result=dict(seed=20261028, future_seed=73111, cut_row_zero_based=cut,
                source_commit='ce3fe4e76271709422165d6f24e2fbecd9d0fe07',
                overrides={'beta_shrinkage':True,'beta_target':0.05},
                eta_at_protected_cut=eta_at_cut, correction_active=bool(eta_at_cut!=0),
                runs=metrics, protected_comparisons=comparisons,
                all_protected_values_exactly_equal=all_equal,
                all_prespecified_comparisons_pass=all_pass, future_stimulus_changes_later_outputs=later_changed,
                source_unchanged=source_after==manifest, clean_source_unchanged=copied_after==manifest)
    save_json(HERE/'corrected_path_e2e.json',result)
    if not all_pass or not result['correction_active'] or not all(later_changed.values()) or source_after!=manifest or copied_after!=manifest:
        raise AssertionError('Corrected E2E differs from prespecified expectation')
    return result


if __name__ == '__main__':
    save_json(HERE/'environment.json', dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,
                                          platform=platform.platform(),cwd=os.getcwd()))
    result={'beta_mse':readback(), 'corrected_path_e2e':e2e()}
    save_json(HERE/'result.json',result)
    artifacts={str(p.relative_to(HERE)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
               for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
               and p.name not in ('artifact_manifest.json','stdout.log','stderr.log')}
    save_json(HERE/'artifact_manifest.json',artifacts)
    print(json.dumps({'beta_mse_reproduction':result['beta_mse']['reproduction_within_1e_12'],
                      'beta_mse':result['beta_mse']['independently_recomputed'],
                      'e2e_equal':result['corrected_path_e2e']['all_protected_values_exactly_equal'],
                      'e2e_expected_pass':result['corrected_path_e2e']['all_prespecified_comparisons_pass'],
                      'eta_at_cut':result['corrected_path_e2e']['eta_at_protected_cut']},indent=2))
