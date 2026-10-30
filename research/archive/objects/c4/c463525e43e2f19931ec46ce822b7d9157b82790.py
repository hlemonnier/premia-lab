#!/usr/bin/env python3
"""Independent saved-evidence readback of the two completed century E2Es."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CASES = (('C06_long_history_002', 'discovery_C06_001', 6),
         ('C09_long_history_001', 'discovery_C09_001', 8))
THREADS = {'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'}
ATOL, RTOL = 1e-14, 1e-12


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(path.read_text())


def csv_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def main():
    destination = OUT / 'summary.json'
    if destination.exists():
        raise FileExistsError('Preserve previous readback; do not overwrite it')
    records = []
    result = {'started_utc': datetime.now(timezone.utc).isoformat(), 'checks': records, 'cases': [],
              'source_sha256': digest(Path(__file__)), 'scope': 'Saved century E2E outputs and permitted discovery-derived inputs only'}

    def check(name, passed, actual=None):
        records.append({'name': name, 'status': 'PASS' if passed else 'FAIL', 'actual': actual})

    try:
        shared_cache = None
        for run_name, historical_name, cpu in CASES:
            run, old = ROOT / 'evidence' / run_name, ROOT / 'evidence' / historical_name
            summary, historical = read(run / 'summary.json'), read(old / 'summary.json')
            source_manifest, old_source = read(run / 'source_manifest.json'), read(old / 'source_manifest.json')
            artifact_manifest = read(run / 'artifact_manifest.json')
            prefix = run_name + ':'
            check(prefix + 'all_saved_artifacts', all((run / name).is_file() and (run / name).stat().st_size == item['bytes']
                  and digest(run / name) == item['sha256'] for name, item in artifact_manifest.items()), len(artifact_manifest))
            check(prefix + 'all_frozen_sources', all(digest(run / name) == sha for name, sha in source_manifest.items()), len(source_manifest))
            check(prefix + 'original_reference_identity', all(digest(run / 'reference' / name) == digest(old / name)
                  for name in ('summary.json', 'source_manifest.json', 'daily.csv')))
            check(prefix + 'exact_old_candidate_config_protocol_scorer', all(digest(run / name) == sha for name, sha in old_source.items()
                  if name.startswith('source/') or name in ('config.json', 'protocol_used.json')))
            check(prefix + 'corrected_controller', digest(run / 'runner_used.py') == digest(ROOT / 'tools/verify_long_history.py'))
            by_name = {item['name']: item for item in summary['checks']}
            required = {'complete_counts', 'forecast_shape_finite', 'exact_discovery_forecast_prefix',
                        'exact_discovery_prefix:targets.npy', 'exact_discovery_prefix:held_books.npy',
                        'historical_score_mask', 'exact_discovery_economics', 'full_fee_reconciliation',
                        'gross_reconciliation', 'century_forecast_runtime', 'mean_rebalance_runtime',
                        'frozen_sources_unchanged', 'inputs_unchanged', 'scored_rows_finite_and_solvency'}
            check(prefix + 'complete_expected_runtime_checks', required <= set(by_name) and len(by_name) == len(summary['checks'])
                  and all(item['status'] == 'PASS' for item in summary['checks']))
            check(prefix + 'completion_and_original_masks', summary['status'] == 'EXECUTED_PASS_SCOPE_ONLY' and summary['exit_code'] == 0
                  and summary['completed_rebalances'] == 24947 and summary['days'] == 25200
                  and by_name['complete_counts']['actual'] == {'forecast_calls': 1, 'targets': 24947, 'scored_rows': [24946, 5]})
            environment = read(run / 'environment.json')
            check(prefix + 'single_core_threads', environment['cpu_affinity'] == [cpu]
                  and set(environment['thread_environment']) == THREADS
                  and all(value == '1' for value in environment['thread_environment'].values()))
            arguments = shlex.split((run / 'rerun.txt').read_text())
            cache = Path(arguments[arguments.index('--cache') + 1])
            metadata = read(run / 'input_manifest.json')
            check(prefix + 'frozen_cache_recipe', metadata == read(cache / 'metadata.json')
                  and metadata['recipe']['kind'] == 'fixed_discovery_tile_preserving_layout'
                  and metadata['recipe']['numeric_source_slice'] == [0, 2016]
                  and metadata['recipe']['days'] == 25200 and metadata['recipe']['base_days'] == 2016)
            if shared_cache is None:
                shared_cache = cache
                check('shared_cache:all_bytes', all(digest(cache / name) == sha for name, sha in metadata['cache_sha256'].items()))
                for name in ('returns.npy', 'characteristics.npy', 'costs.npy'):
                    source = np.load(ROOT / 'cache/discovery' / name, mmap_mode='r', allow_pickle=False)
                    tiled = np.load(cache / name, mmap_mode='r', allow_pickle=False)
                    check('shared_cache:source_identity:' + name, digest(ROOT / 'cache/discovery' / name) == metadata['recipe']['source_sha256'][name])
                    check('shared_cache:read_only_dtype:' + name, not tiled.flags.writeable and tiled.dtype == np.float64)
                    if name == 'costs.npy':
                        check('shared_cache:unchanged_costs', np.array_equal(source, tiled) and tiled.shape == (1000,))
                    else:
                        exact_tile = all(np.array_equal(tiled[start:start + min(2016, 25200 - start)], source[:min(2016, 25200 - start)])
                                         for start in range(0, 25200, 2016))
                        check('shared_cache:exact_full_recipe:' + name, exact_tile and tiled.shape == (25200, *source.shape[1:]))
                        check('shared_cache:canonical_layout:' + name, bool(tiled.flags.f_contiguous and not tiled.flags.c_contiguous)
                              == metadata['recipe']['source_layouts'][name]['fortran_order'])
            else:
                check(prefix + 'same_verified_shared_cache', cache == shared_cache)

            chunks = sorted((run / 'daily').glob('part_*.csv'))
            saved = [row for chunk in chunks for row in csv_rows(chunk)]
            check(prefix + 'full_economic_day_sequence', len(chunks) == 25 and [int(row['return_index']) for row in saved] == list(range(253, 25199)))
            columns = ('gross_return', 'full_cost', 'net_return', 'target_gross', 'market_return',
                       'candidate_rebalance_ms', 'official_rebalance_seconds')
            ledger = np.array([[float(row[name]) for name in columns] for row in saved], dtype=float)
            check(prefix + 'full_ledger_finite_solvency_fees', ledger.shape == (24946, 7) and bool(np.isfinite(ledger).all())
                  and bool((ledger[:, 0] > -1).all() and (ledger[:, 2] > -1).all() and (ledger[:, 1] >= 0).all())
                  and np.array_equal(ledger[:, 2], ledger[:, 0] - ledger[:, 1]))
            actual_timing = np.load(run / 'all_candidate_rebalance_seconds.npy', allow_pickle=False)
            check(prefix + 'all_24947_timings', actual_timing.shape == (24947,) and bool(np.isfinite(actual_timing).all())
                  and bool((actual_timing >= 0).all()) and np.array_equal(ledger[:, 5], actual_timing[1:] * 1000))
            timing = summary['timing']
            calculated = {'mean_candidate_rebalance_ms': float(actual_timing.mean() * 1000),
                          'mean_scored_candidate_rebalance_ms': float(actual_timing[1:].mean() * 1000)}
            check(prefix + 'timing_means_recomputed', all(calculated[key] == timing[key] for key in calculated), calculated)
            check(prefix + 'timing_quantiles_quarters_recomputed', all(float(np.quantile(actual_timing, float(q)) * 1000) == value
                  for q, value in timing['quantiles_candidate_ms'].items())
                  and [float(part.mean() * 1000) for part in np.array_split(actual_timing, 4)] == timing['quarter_mean_candidate_ms'])
            check(prefix + 'official_timing_mean', bool(np.isclose(ledger[:, 6].mean() * 1000,
                  timing['mean_official_instrumented_rebalance_ms'], atol=ATOL, rtol=RTOL)))
            check(prefix + 'measured_runtime_limits', timing['actual_century_executed']
                  and timing['forecast_candidate_seconds'] < 3600 and timing['forecast_official_instrumented_seconds'] < 3600
                  and actual_timing.mean() < .1 and actual_timing[1:].mean() < .1)
            for name in ('forecasts.npy', 'targets.npy', 'held_books.npy'):
                check(prefix + 'original_array_bytes:' + name, digest(run / name) == historical['output_arrays'][name]['sha256'])
            targets = np.load(run / 'targets.npy', allow_pickle=False)
            held = np.load(run / 'held_books.npy', allow_pickle=False)
            forecasts = np.load(run / 'forecasts.npy', allow_pickle=False)
            check(prefix + 'saved_prefix_shapes', targets.shape == held.shape == (1763, 1000) and forecasts.shape == (2016, 1000))
            check(prefix + 'empty_opening_book', bool(np.array_equal(held[0], np.zeros(1000))))
            old_rows = csv_rows(old / 'daily.csv')
            old_fields = ('gross_return', 'full_cost', 'closing_target_gross', 'raw_market_return')
            historical_rows = np.array([[float(row[key]) for key in old_fields] for row in old_rows])
            check(prefix + 'original_economic_rows_exact', [int(r['return_index']) for r in old_rows] == list(range(253, 2015))
                  and np.array_equal(ledger[:1762][:, [0, 1, 3, 4]], historical_rows))
            returns = np.load(cache / 'returns.npy', mmap_mode='r', allow_pickle=False)
            costs = np.load(cache / 'costs.npy', mmap_mode='r', allow_pickle=False)
            rebuilt_gross, rebuilt_fees, rebuilt_held = [], [], []
            for i, day in enumerate(range(253, 2015)):
                gross = float(targets[i] @ returns[day])
                rebuilt_gross.append(gross)
                rebuilt_held.append(targets[i] * (1 + returns[day]) / (1 + gross))
                rebuilt_fees.append(float(costs @ np.abs(targets[i + 1] - held[i + 1])))
            rebuilt_held = np.asarray(rebuilt_held)
            check(prefix + 'prefix_gross_drift_full_fees_rebuilt', np.array_equal(ledger[:1762, 0], rebuilt_gross)
                  and np.array_equal(held[1:], rebuilt_held) and np.array_equal(ledger[:1762, 1], rebuilt_fees),
                  {'gross_max_error': float(np.max(np.abs(ledger[:1762, 0] - rebuilt_gross))),
                   'held_max_error': float(np.max(np.abs(held[1:] - rebuilt_held))),
                   'fee_max_error': float(np.max(np.abs(ledger[:1762, 1] - rebuilt_fees)))})
            check(prefix + 'all_runtime_fees_exposures_exact', by_name['full_fee_reconciliation']['actual']['max_abs_error'] == 0
                  and by_name['gross_reconciliation']['actual']['max_abs_error'] == 0)
            result['cases'].append({'run': run_name, 'original_reference': historical_name,
                'artifact_files_rehashed': len(artifact_manifest), 'frozen_source_files_rehashed': len(source_manifest),
                'full_targets_executed': len(actual_timing), 'full_economic_rows_read': len(saved),
                'forecast_seconds': timing['forecast_candidate_seconds'], **calculated,
                'maximum_rebalance_ms': float(actual_timing.max() * 1000),
                'full_fee_scope': 'Every full-path fee checked during frozen execution; saved 1762-row prefix independently rebuilt here.',
                'stdout_sha256': digest(run / 'stdout.log'), 'stderr_sha256': digest(run / 'stderr.log')})
        result['status'] = 'EXECUTED_PASS_SCOPE_ONLY' if all(r['status'] == 'PASS' for r in records) else 'EXECUTED_FAIL'
    except Exception as exc:
        import traceback
        result.update(status='EXECUTED_FAIL', error=str(exc), traceback=traceback.format_exc())
    result['finished_utc'] = datetime.now(timezone.utc).isoformat()
    result['limits'] = ['A repeated discovery workload is not independent market history or alpha evidence.',
        'Host-specific executed runtime; no guarantee for every environment or possible history.',
        'Only the original target/held prefix is saved; later full-path per-stock targets cannot be independently reconstructed from daily aggregates.',
        'No candidate replay, protected-period access, model change, or new selectable configuration occurred in this readback.']
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(records),
                      'failed': [r['name'] for r in records if r['status'] == 'FAIL'],
                      'cases': result['cases'], 'error': result.get('error')}, indent=2))
    return 0 if result['status'] == 'EXECUTED_PASS_SCOPE_ONLY' else 1


if __name__ == '__main__':
    sys.exit(main())
