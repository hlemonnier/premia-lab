"""Independent saved-target whole-workflow accounting under READBACK_PLAN.md."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

STAGES = {'full': (253,3779), 'discovery': (253,2015),
          'validation': (2016,3023), 'audit': (3024,3779)}
INPUT_IDS = {'returns.csv': '6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d',
             'costs.csv': 'ec0930e480078ce4c8d6f59b802c4c303cdae2dea8d15d7e08417e6b414d0186',
             'prior_joint_daily.csv': '6b5a467fff8ca72be740195ca41e52b0d8b15057f899dfdb6b88fe448ced246c'}


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def performance(rows):
    days = np.arange(253, 253+len(rows)); answer = {}
    for label, (lo, hi) in STAGES.items():
        select = (days >= lo) & (days < hi)
        g, c, gross, market, seconds = rows[select].T
        net = g-c; centered_market = market-market.mean()
        answer[label] = {
            'n': int(select.sum()),
            'net_sharpe': float(np.sqrt(252)*net.mean()/net.std(ddof=0)),
            'gross_sharpe': float(np.sqrt(252)*g.mean()/g.std(ddof=0)),
            'net_return_ann_pct': float(25200*net.mean()),
            'net_vol_ann_pct': float(100*np.sqrt(252)*net.std(ddof=0)),
            'cost_ann_pct': float(25200*c.mean()),
            'net_beta': float(np.sum(centered_market*(net-net.mean()))/np.sum(centered_market**2)),
            'mean_gross': float(gross.mean()),
            'max_closing_gross': float(gross.max()),
            'worst_gross_daily_return': float(g.min()),
            'rebalance_ms_mean': float(1000*seconds.mean()),
            'rebalance_ms_p99': float(1000*np.quantile(seconds,.99)),
            'rebalance_ms_max': float(1000*seconds.max())}
    return answer


def intervals(reference, candidate):
    answer = {}; n = len(reference)
    point = float(np.sqrt(252)*(candidate.mean()/candidate.std()-reference.mean()/reference.std()))
    for length in (21,63,126):
        rng = np.random.default_rng(20261027); values = []
        blocks = (n+length-1)//length
        for _ in range(20):
            starts = rng.integers(0,n-length+1,size=(100,blocks))
            ix = (starts[:,:,None]+np.arange(length)).reshape(100,-1)[:,:n]
            a, b = candidate[ix], reference[ix]
            values.extend((np.sqrt(252)*(a.mean(axis=1)/a.std(axis=1)-b.mean(axis=1)/b.std(axis=1))).tolist())
        lo, hi = np.quantile(values,[.025,.975])
        answer[str(length)] = {'point': point, 'lo': float(lo), 'hi': float(hi),
                               'draws': 2000, 'seed': 20261027,
                               'last_legal_block_start_included': True}
    return answer


def read_policy(label, folder, R, costs):
    targets_path, rows_path = folder/'targets.npy', folder/'rows.npy'
    manifest_path = folder/'array_manifest.json'
    if not manifest_path.exists():
        manifest_path = folder/'verification.json'
    declared = json.loads(manifest_path.read_text())
    declared = declared.get('arrays',declared)
    verified = {}
    for key, item in declared.items():
        name = Path(item['path']).name
        file = folder/name
        file_hash = sha(file)
        assert file_hash == item.get('file_sha256',item.get('sha256')), (label,name)
        array = np.load(file,mmap_mode='r',allow_pickle=False)
        assert list(array.shape) == item['shape'] and str(array.dtype) == item['dtype'], (label,name)
        if 'array_sha256' in item:
            assert hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest() == item['array_sha256'], (label,name)
        verified[name] = file_hash
    assert {'targets.npy','rows.npy'} <= set(verified), label
    targets = np.load(targets_path, mmap_mode='r', allow_pickle=False)
    rows = np.load(rows_path, allow_pickle=False)
    assert targets.shape == (3527,1000), (label, targets.shape)
    assert rows.shape == (3526,5), (label, rows.shape)
    assert np.isfinite(targets).all() and np.isfinite(rows).all(), label
    previous = np.zeros(1000); reconstructed = []; worst = 0.
    for j, target in enumerate(targets):
        t = 252+j
        g = float(np.sum(previous*R[t])); assert g > -1, (label,t,g)
        held = previous*(1+R[t])/(1+g)
        fee = 0. if j == 0 else float(np.sum(costs*np.abs(target-held)))
        reconstructed.append([g,fee,float(np.abs(target).sum()),float(R[t].mean())])
        previous = target; worst = min(worst,g)
    reconstructed = np.asarray(reconstructed)[1:]
    errors = np.max(np.abs(reconstructed-rows[:,:4]),axis=0)
    assert np.all(errors <= 1e-12), (label,errors)
    gross = np.abs(targets).sum(axis=1)
    max_weight = float(np.abs(targets).max())
    allowed_weight = .10005 if label in ('M1','joint_E2_M1') else .1
    perf = performance(rows)
    checks = {'saved_target_accounting': bool(np.all(errors <= 1e-12)),
              'finite': True, 'solvent': worst > -1,
              'gross_cap': bool(gross.max() <= 5+1e-12),
              'stock_bound': max_weight <= allowed_weight+1e-12,
              'net_beta': abs(perf['full']['net_beta']) < .2,
              'mean_runtime': perf['full']['rebalance_ms_mean'] < 100}
    assert all(checks.values()), (label,checks)
    info = {'folder': str(folder), 'input_sha256': {'targets.npy': sha(targets_path),
            'rows.npy': sha(rows_path)}, 'performance': perf,
            'verified_array_manifest': {'path':str(manifest_path),'sha256':sha(manifest_path),
                                        'verified_files':verified},
            'checks': checks, 'max_error_g_fee_gross_market': errors.tolist(),
            'decision_rows': len(targets), 'economic_rows': len(rows),
            'first_decision': 252, 'last_decision': 3778,
            'earning_rows': [253,3778], 'first_opening_fee': 0.,
            'final_charged_rebalance_fee': float(rows[-1,1]),
            'no_forced_liquidation': True, 'max_actual_weight': max_weight,
            'allowed_stock_weight_bound': allowed_weight, 'max_target_gross': float(gross.max())}
    for name in ('forecast.npy','virtual_targets.npy','inner_targets.npy'):
        if (folder/name).exists():
            assert name in verified, (label,name)
            info['input_sha256'][name] = sha(folder/name)
    return info, rows[:,0]-rows[:,1], rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--reference',type=Path,required=True)
    ap.add_argument('--candidate',action='append',required=True)
    ap.add_argument('--out',type=Path,required=True)
    args = ap.parse_args(); args.out.parent.mkdir(exist_ok=True,parents=True)
    if args.out.exists():
        raise RuntimeError('Do not overwrite an earlier readback')
    scorer_sha = sha(args.data/'score.py')
    assert scorer_sha == 'ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96'
    for name in ('returns.csv','costs.csv'):
        assert sha(args.data/name) == INPUT_IDS[name], name
    assert sha(args.reference) == INPUT_IDS['prior_joint_daily.csv']
    R = np.ascontiguousarray(pd.read_csv(args.data/'returns.csv',index_col='day').to_numpy(float))
    costs = pd.read_csv(args.data/'costs.csv',index_col='stock')['cost'].to_numpy(float)
    assert R.shape == (3780,1000) and costs.shape == (1000,)
    reference = pd.read_csv(args.reference)
    assert np.array_equal(reference['return_index'].to_numpy(),np.arange(253,3779))
    base_net = reference['net_return'].to_numpy()
    expected = reference[['gross_return','full_cost','closing_target_gross','market_return']].to_numpy()
    results = {}; net_series = {}; row_series = {}
    for item in args.candidate:
        label, directory = item.split('=',1)
        assert label not in results
        info, net, rows = read_policy(label,Path(directory),R,costs)
        info['paired_intervals_vs_prior_leader'] = intervals(base_net,net)
        if label in ('baseline','M0'):
            err = float(np.max(np.abs(rows[:,:4]-expected)))
            assert err <= 1e-8
            info['prior_leader_economic_reproduction_max_error'] = err
        results[label] = info; net_series[label] = net; row_series[label] = rows
    if 'joint_E2_M1' in results and 'M1' in results:
        results['joint_E2_M1']['paired_intervals_vs_M1'] = intervals(net_series['M1'],net_series['joint_E2_M1'])
    if 'M1' in results and 'M0' in results:
        diff = row_series['M1']-row_series['M0']
        gross_error = float(np.max(np.abs(diff[:,0]-.05*R[253:3779].mean(axis=1))))
        # This identity is expected only on the observed path with no outer cap.
        assert gross_error <= 1e-12
        results['M1']['actual_increment_vs_M0'] = {
            'gross_equals_fixed_market_sleeve_max_error': gross_error,
            'gross_return_increment_ann_pct': float(25200*diff[:,0].mean()),
            'actual_fee_increment_ann_pct': float(25200*diff[:,1].mean()),
            'net_return_increment_ann_pct': float(25200*(diff[:,0]-diff[:,1]).mean())}
    answer = {'scope_sha256': sha(Path(__file__).with_name('READBACK_PLAN.md')),
              'readback_source_sha256': sha(__file__), 'original_scorer_unchanged': True,
              'no_policy_execution': True, 'all_history_development': True,
              'input_sha256': {'returns.csv':sha(args.data/'returns.csv'),
                              'costs.csv':sha(args.data/'costs.csv'),
                              'score.py':scorer_sha,
                              'prior_joint_daily.csv':sha(args.reference)},
              'results':results,
              'ranked_observed_scores':sorted([(label,info['performance']['full']['net_sharpe'])
                  for label,info in results.items()],key=lambda x:x[1],reverse=True),
              'limitations':['Source/temporal/solver certification is recorded in each independent release packet.',
                 'Intervals are fixed-policy development-history descriptions, not search-adjusted validation.',
                 'An integrated production runtime gate is separate from current instrumented timings.']}
    args.out.write_text(json.dumps(answer,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'out':str(args.out),'ranking':answer['ranked_observed_scores'],
                      'max_accounting_error':max(max(v['max_error_g_fee_gross_market']) for v in results.values())}))


if __name__ == '__main__':
    main()
