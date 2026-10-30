"""Independently read back the eight already-executed synthetic M1 workflows."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'evidence/v2_score2_review_20261029/m1'
RUN = PACKET / 'synthetic_002'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fixture():
    rng = np.random.default_rng(20261028)
    T, N = 420, 64
    X = np.zeros((T, N, 13)); X[0] = rng.normal(size=(N, 13))
    for t in range(1, T):
        X[t] = .92*X[t-1] + np.sqrt(1-.92**2)*rng.normal(size=(N, 13))
    beta = rng.uniform(.7, 1.3, size=N)
    m = .0003 + .006*rng.normal(size=T)
    R = np.empty((T, N))
    for t in range(T):
        z = X[max(0, t-1)]
        scale = .6 if t < 330 else 2.
        R[t] = (beta*m[t] + .00008*z[:, 0] + .00006*(z[:, 1]**2-1)
                + scale*(.0015*z[:, 2]*rng.normal() + .008*rng.normal(size=N)))
    return R, X, np.linspace(.0001, .0005, N)


def main():
    result = json.loads((RUN/'result.json').read_text())
    assert result['all_passed'] and len(result['checks']) == 97
    assert all(result['checks'].values())
    for rel, h in result['executed_sources'].items():
        assert sha(PACKET/rel) == h, rel
    manifest = json.loads((RUN/'artifact_manifest.json').read_text())
    for rel, h in manifest.items():
        assert sha(RUN/rel) == h, rel
    R, X, cost = fixture()
    input_ids = json.loads((RUN/'input_manifest.json').read_text())
    for key, a in [('R', R), ('X', X), ('costs', cost)]:
        assert hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest() == input_ids[key], key
    toy = np.array([[0.,0.,0.],[-.01,.03,.005],[.02,-.01,.01],[-.03,.01,.02],
                    [.01,.01,.01],[-.02,0.,.01],[.005,-.007,.012],[0.,0.,0.]])
    toy_cost = np.array([.001, .002, .003])
    outputs = {}; arrays_checked = 0
    for folder in sorted(RUN.iterdir()):
        if not (folder/'array_manifest.json').exists():
            continue
        arrays = {}
        for key, item in json.loads((folder/'array_manifest.json').read_text()).items():
            path = folder/Path(item['path']).name
            assert sha(path) == item['sha256'], path
            a = np.load(path, allow_pickle=False)
            assert list(a.shape) == item['shape'] and str(a.dtype) == item['dtype']
            assert hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest() == item['array_sha256']
            arrays[key] = a; arrays_checked += 1
        name = folder.name
        if name in ('known_returns_reversals', 'forced_aggregate_cap', 'zero_returns'):
            data = np.zeros_like(toy) if name == 'zero_returns' else toy
            c = toy_cost
        else:
            data = R.copy(); c = cost
            if name.endswith('_future'):
                data[360:] = -.6*data[360:] + .0007
            if name.endswith('_prefix'):
                data = data[:361]
        days = pd.read_csv(folder/'decisions.csv')['decision_index'].to_numpy(int)
        expected = []; previous = np.zeros(data.shape[1])
        for j, (t, target) in enumerate(zip(days, arrays['targets'])):
            g = float(np.sum(previous*data[t])); assert g > -1
            held = previous*(1+data[t])/(1+g)
            fee = 0. if j == 0 else float(np.sum(c*np.abs(target-held)))
            expected.append([g, fee, float(np.abs(target).sum()), float(data[t].mean())])
            previous = target
        err = np.max(np.abs(np.array(expected)[1:]-arrays['rows'][:, :4]), axis=0)
        assert np.all(err <= 1e-12), (name, err)
        outputs[name] = {'decisions': len(days), 'economic_rows': len(arrays['rows']),
                         'max_error_g_fee_gross_market': err.tolist()}
    m0 = np.load(RUN/'M0/targets.npy', allow_pickle=False)
    assert np.array_equal(m0, np.load(RUN/'M1/inner_targets.npy', allow_pickle=False))
    answer = {'decision': 'accepted_for_actual_release', 'reviewer': 'root',
              'scope_sha256': sha(Path(__file__).with_name('M1_EVIDENCE_SCOPE.md')),
              'readback_source_sha256': sha(__file__), 'synthetic_result_sha256': sha(RUN/'result.json'),
              'source_sha256': result['executed_sources'],
              'baseline_source_manifest': json.loads((RUN/'source_manifest.json').read_text()),
              'reference_sources': result['reference_sources'],
              'artifact_hashes_verified': len(manifest), 'atomic_arrays_verified': arrays_checked,
              'checks_passed': 97, 'workflows': outputs, 'inner_is_exact_M0': True,
              'source_findings': ['Independent inner and outer drift denominators and states.',
                  'Fixed market sleeve added after inner multiplier; true combined stock trades.',
                  'Causal forecast forwarding and own-session resets; no future data use.',
                  'Only proportional outer gross reduction; no implied free market instrument.',
                  'Atomic writes and final-rebalance/no-liquidation endpoint match scorer.',
                  'Original failed serialization run and expected missing-policy run preserved.'],
              'required_changes': []}
    Path(__file__).with_name('M1_SOURCE_EVIDENCE_REVIEW.json').write_text(json.dumps(answer, indent=2)+'\n')
    print(json.dumps({k: answer[k] for k in ['decision','checks_passed','artifact_hashes_verified','atomic_arrays_verified','inner_is_exact_M0']}))


if __name__ == '__main__':
    main()
