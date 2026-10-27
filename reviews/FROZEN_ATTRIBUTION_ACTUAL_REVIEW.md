# Independent readback of the executed frozen C09 attribution

27 October 2026, Europe/Paris. Reviewer: independent causality/source agent. This document concerns the single descriptive run in `evidence/frozen_attribution_real_001`; it does not authorize or execute a new strategy, modify the frozen policy, or reopen model selection.

## Expectations recorded before numerical readback

The pre-execution source/synthetic review is frozen separately and must remain unchanged. The operative release is `research/FROZEN_ATTRIBUTION_RELEASE_20261027.json`, SHA256 `25a01472940793c40b9213fc65938a8ff4565bc1d2beac3b05ce54bfa1b1f8a3`, published before execution in commit `49fc43f2489f4a75050702f1f2297413d7abe088`. The original release draft remains preserved and superseded because it captured the source-review file before that file's completed approval was saved; no canonical attribution ran under that draft.

The run's top-level status was confirmed complete before this readback: `EXECUTED_PASS_SCOPE_ONLY`, exit code 0, 3,526 rows and zero model executions. Its numerical attribution results have not been inspected at the time these expectations are recorded.

The independent readback will verify the executed/frozen source identities, release bindings, all new saved artifact hashes, original consumed input identities, and the unchanged four-file handoff. It will read the saved attributed daily table and original C09 economic ledger and reconcile their gross returns, full fees and net returns. The opening-target identity will also be checked directly from the saved original targets and return array, without invoking any strategy or factor fit.

Expected daily indices are exactly 253 through 3778 inclusive: 3,526 rows. Opening target index is `t-253`; risk and variance history stops are `t`; the cached correlation-loading cutoff is `253 + 21*floor((t-253)/21)`; factor age is `(t-253) mod 21`; refresh occurs when that age is zero. The factor rank must be between zero and ten and is reported as observed rather than forced to a desired value.

The three components must sum to gross and subtract the original full fees to net at the already declared attribution tolerance (`atol=1e-12`, `rtol=1e-10`). Full gross/fee/net values copied from the original ledger must match exactly. Stage masks remain discovery `[253,2015)`, validation `[2016,3023)`, and audit `[3024,3779)`, with exactly 1,762, 1,007 and 755 rows. The two boundary rows excluded by these masks remain in the complete daily reconciliation. Stage annual arithmetic means, annual volatilities, signed gross covariance contributions, exposure/rank summaries, cutoffs/ages and maximum reconciliation errors will be recomputed independently from the saved table. Undefined zero-variance ratios remain null.

This is saved-evidence reconciliation of the already admitted workflow. No new numerical tests, candidate run, factor estimate, alternative rank/window/threshold, or clean evaluation period is introduced. Any mismatch will be recorded and will block interpretation until its cause is resolved; original evidence will not be edited to agree with the reviewer.

## Executed readback

**Executed pass within the declared readback scope: 146 of 146 checks passed, exit code 0.** There were zero candidate executions, zero factor fits and no new selection. All nineteen new saved artifact entries and eleven consumed-file identities matched. The current tool, frozen tool copy, pre-execution review/protocol bindings and four-file C09 handoff were unchanged.

The full 3,526 daily rows preserve the original gross returns, full fees and net returns exactly. Direct recomputation of opening-target P&L from the original saved targets and return array agrees within `3.8163916471489756e-17`. The maximum absolute error in both component-to-gross and component-less-fees-to-net reconciliation is `2.0816681711721685e-17`. All 3,526 target indices, prior-risk cutoffs, correlation-fit cutoffs, variance cutoffs, refresh indicators and ages match the fixed chronology. Factor rank is ten throughout this particular observed history.

The release's command uses an absolute output path; the executed command records the equivalent relative `evidence/frozen_attribution_real_001` path. The readback resolves those paths before checking command equivalence. No numerical setting, input packet, source identity, mode or output destination changed.

### Observed attribution

These are annual arithmetic contributions of the existing fixed C09 positions. Full fees remain a separate subtraction, and the table retains the original three evaluation masks.

| Component | Discovery: 1,762 days | Validation: 1,007 days | Audit: 755 days |
|---|---:|---:|---:|
| Estimated-market P&L | Numerically negligible | Numerically negligible | Numerically negligible |
| Residual-factor-span gross contribution | 3.1537% | 1.4153% | 7.7465% |
| Remainder gross contribution | 2.2244% | 1.4694% | 2.2627% |
| Total gross | 5.3781% | 2.8847% | 10.0092% |
| Full original fees | 0.5880% | 0.2088% | 0.3331% |
| Original net return | 4.7901% | 2.6759% | 9.6761% |

| Covariance contribution to gross variance | Discovery | Validation | Audit |
|---|---:|---:|---:|
| Estimated-market component | Numerically negligible | Numerically negligible | Numerically negligible |
| Residual-factor-span component | 71.0109% | 52.6165% | 67.3772% |
| Remainder component | 28.9891% | 47.3835% | 32.6228% |

These last entries are the prespecified signed `Cov(component,gross)/Var(gross)` quantities. They happen to be positive here; they remain covariance contributions rather than independent-risk shares. Their near-unit totals follow the verified additive identity. Component annual volatilities, which do not add, are preserved in the exact output below.

### Interpretation and practical consequence

The stronger reserved-audit earnings appear mainly in the common-factor span defined by this particular prior-estimated risk model. The remainder's annual arithmetic contribution is positive in all three recorded periods and is closer between discovery and audit than the factor-span contribution. This is descriptive evidence that the observed improvement is not confined to the part left outside ten estimated residual directions.

It does **not** establish that the factor contribution is compensation for priced risk, that the remainder is stock-specific mispricing, or that either source of earnings will persist. The basis is inferred from past realized returns with a prespecified rank and refresh policy; omitted factors, nonlinear exposures, basis error and changing factor realizations can affect both components. Nor does it imply that all common risk should be hedged away: the existing factor-aware complete candidate already lost the original validation comparison, and that comparison changed more than one component.

The estimated-market component is almost zero because the same prior beta estimator defines C09's portfolio hedge. This is a consistency observation, not another independent test of unknown future market exposure. The separately measured realized net beta is the relevant empirical quantity for the employer's beta condition.

The useful addition is a more precise account of where this frozen policy's historical P&L sits under one declared factor construction. It strengthens explanation and reveals a plausible common-factor dependency to investigate with genuinely new observations. It supplies no reason to retune C09 on these exposed periods or to claim a new untouched confirmation sample. No new factor count, alternative projection, subperiod, component Sharpe, significance claim or mean-contribution percentage was selected after inspection.

The following self-contained read-only procedure is the exact readback code. It was recorded before execution and imports no candidate or attribution implementation:

```python
from pathlib import Path
import csv
import hashlib
import json
import math
import shlex
import numpy as np

root = Path('.').resolve()
out = root / 'evidence/frozen_attribution_real_001'
checks = []
result = {'status': 'RUNNING', 'model_executions': 0, 'factor_fits': 0, 'new_selection': False}
def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()
def load(path):
    return json.loads(Path(path).read_text())
def check(name, passed):
    checks.append({'name': name, 'pass': bool(passed)})
    if not passed:
        raise AssertionError(name)
def close(name, observed, expected):
    observed, expected = np.asarray(observed, dtype=float), np.asarray(expected, dtype=float)
    check(name, observed.shape == expected.shape and np.isfinite(observed).all()
          and np.allclose(observed, expected, atol=1e-12, rtol=1e-10))
def read_csv(path):
    with Path(path).open(newline='') as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
def command_key(command):
    tokens = shlex.split(command)
    for flag in ('--project', '--packet', '--out'):
        pos = tokens.index(flag) + 1
        tokens[pos] = str((root / tokens[pos]).resolve())
    tokens[0] = str(Path(tokens[0]).resolve())
    tokens[1] = str((root / tokens[1]).resolve())
    return tokens

try:
    release_path = root / 'research/FROZEN_ATTRIBUTION_RELEASE_20261027.json'
    check('operative_release_hash', digest(release_path) == '25a01472940793c40b9213fc65938a8ff4565bc1d2beac3b05ce54bfa1b1f8a3')
    release = load(release_path)
    check('release_snapshot_identity', digest(root / 'evidence/frozen_attribution_release_002/release.json') == digest(release_path))
    for path, expected in release['preexecution_identities'].items():
        check('current_preexecution:' + path, digest(root / path) == expected)
        check('frozen_preexecution:' + path, digest(root / release['preserved_snapshot_root'] / path) == expected)
    check('executed_tool_identity', digest(out / 'tool_used.py') == release['preexecution_identities']['tools/attribute_frozen_policy.py'])
    for path, expected in release['handoff_sha256'].items():
        check('unchanged_handoff:' + path, digest(root / 'handoff' / path) == expected)
    artifact_inventory = load(out / 'artifact_manifest.json')
    for path, item in artifact_inventory.items():
        f = out / path
        check('saved_artifact:' + path, f.is_file() and f.stat().st_size == item['bytes'] and digest(f) == item['sha256'])
    consumed = load(out / 'consumed_manifest.json')
    for path, item in consumed.items():
        f = Path(item['path'])
        check('unchanged_consumed:' + path, f.is_file() and f.stat().st_size == item['bytes'] and digest(f) == item['sha256'])
    packet = Path(release['canonical_packet'])
    check('original_packet_identity', digest(packet / 'artifact_manifest.json') == release['canonical_packet_artifact_manifest_sha256'])
    summary = load(out / 'summary.json')
    check('complete_original_run', summary['status'] == 'EXECUTED_PASS_SCOPE_ONLY' and summary['exit_code'] == 0
          and summary['mode'] == 'real' and summary['model_executions'] == 0 and summary['completed_rows'] == 3526)
    check('released_command_semantics', command_key(summary['command']) == command_key(release['command']))
    check('recorded_run_checks', all(item['status'] == 'PASS' for item in summary['checks']))
    actual = read_csv(out / 'daily_attribution.csv')
    original = read_csv(packet / 'daily.csv')
    check('full_3526_row_range', [int(r['return_index']) for r in actual] == list(range(253, 3779)) and len(original) == 3526)
    check('original_indices', [r['return_index'] for r in actual] == [r['return_index'] for r in original])
    for name in ('gross_return', 'full_cost', 'net_return'):
        check('exact_original_economics:' + name, all(a[name] == b[name] for a, b in zip(actual, original)))
    check('all_finite_daily', all(math.isfinite(value) for row in actual for value in row.values()))
    for row in actual:
        t = int(row['return_index'])
        expected = {
            'target_index': t - 253,
            'risk_history_stop_exclusive': t,
            'factor_variance_history_stop_exclusive': t,
            'factor_history_stop_exclusive': 253 + 21 * ((t - 253) // 21),
            'factor_age_days': (t - 253) % 21,
            'factor_refreshed': int((t - 253) % 21 == 0),
        }
        if any(row[k] != v for k, v in expected.items()):
            raise AssertionError('Incorrect prior-state/index metadata at row ' + str(t))
    check('all_3526_prior_state_and_target_indices', True)
    check('rank_bounds', all(0 <= r['factor_rank'] <= 10 and r['factor_rank'].is_integer() for r in actual))
    components = ('market_component', 'residual_factor_component', 'remainder_component')
    values = (*components, 'full_cost', 'gross_return', 'net_return')
    series = {key: np.array([r[key] for r in actual]) for key in values}
    attributed = series['market_component'] + series['residual_factor_component'] + series['remainder_component']
    close('daily_components_sum_gross', attributed, series['gross_return'])
    close('daily_full_fee_subtraction', attributed - series['full_cost'], series['net_return'])
    returns = np.load(packet / 'inputs/returns.npy', mmap_mode='r', allow_pickle=False)
    targets = np.load(packet / 'targets.npy', mmap_mode='r', allow_pickle=False)
    opening_gross = np.einsum('ij,ij->i', targets[:3526], returns[253:3779])
    close('independent_opening_target_return_identity', opening_gross, series['gross_return'])
    close('recorded_gross_errors', [r['gross_reconciliation_error'] for r in actual], attributed - series['gross_return'])
    close('recorded_net_errors', [r['net_reconciliation_error'] for r in actual], attributed - series['full_cost'] - series['net_return'])
    close('recorded_opening_errors', [r['opening_gross_reconciliation_error'] for r in actual], opening_gross - series['gross_return'])
    masks = {'discovery': (253, 2015, 1762), 'validation': (2016, 3023, 1007), 'audit': (3024, 3779, 755)}
    check('only_original_stage_names', set(summary['stages']) == set(masks))
    result['stages'] = {}
    indices = np.array([r['return_index'] for r in actual])
    for stage, (lo, hi, count) in masks.items():
        keep = (indices >= lo) & (indices < hi)
        selected = [r for r, retained in zip(actual, keep) if retained]
        stats = summary['stages'][stage]
        check(stage + ':count_and_mask', len(selected) == count and stats['rows'] == count and stats['index_slice'] == [lo, hi])
        s = {k: x[keep] for k, x in series.items()}
        means = {k: float(x.mean() * 252) for k, x in s.items()}
        vols = {k: float(x.std(ddof=0) * math.sqrt(252)) for k, x in s.items()}
        for k in values:
            close(stage + ':mean:' + k, means[k], stats['annual_arithmetic_mean'][k])
            close(stage + ':volatility:' + k, vols[k], stats['annual_volatility'][k])
        g = s['gross_return']
        covariance = np.cov(np.column_stack([*(s[k] for k in components), g]), rowvar=False, ddof=0)
        contributions = {k: float(covariance[i, 3] / covariance[3, 3]) if covariance[3, 3] > 0 else None for i, k in enumerate(components)}
        for k in components:
            if contributions[k] is None:
                check(stage + ':undefined_covariance:' + k, stats['gross_covariance_contribution'][k] is None)
            else:
                close(stage + ':covariance:' + k, contributions[k], stats['gross_covariance_contribution'][k])
        if covariance[3, 3] > 0:
            close(stage + ':covariance_sum', sum(contributions.values()), 1.0)
        exposure = np.abs([r['estimated_market_exposure'] for r in selected])
        close(stage + ':mean_abs_exposure', exposure.mean(), stats['estimated_market_exposure']['mean_abs'])
        close(stage + ':max_abs_exposure', exposure.max(), stats['estimated_market_exposure']['max_abs'])
        ranks = [int(r['factor_rank']) for r in selected]
        check(stage + ':rank_range', stats['factor_rank'] == {'min': min(ranks), 'max': max(ranks)})
        for key in ('risk_history_stop_exclusive', 'factor_history_stop_exclusive', 'factor_age_days'):
            check(stage + ':max_' + key, stats['max_' + key] == max(r[key] for r in selected))
        for key in ('gross_reconciliation_error', 'net_reconciliation_error', 'opening_gross_reconciliation_error'):
            close(stage + ':max_abs_' + key, stats['max_abs_' + key], max(abs(r[key]) for r in selected))
        result['stages'][stage] = {'rows': count, 'annual_arithmetic_mean': means, 'annual_volatility': vols,
            'gross_covariance_contribution': contributions, 'mean_abs_estimated_beta_exposure': float(exposure.mean()),
            'max_abs_estimated_beta_exposure': float(exposure.max()), 'rank_min': min(ranks), 'rank_max': max(ranks)}
    result['full_row_max_abs_errors'] = {
        'component_sum_vs_gross': float(np.max(np.abs(attributed - series['gross_return']))),
        'component_sum_less_fees_vs_net': float(np.max(np.abs(attributed - series['full_cost'] - series['net_return']))),
        'independent_opening_targets_vs_gross': float(np.max(np.abs(opening_gross - series['gross_return']))),
    }
    result['saved_artifact_entries'] = len(artifact_inventory)
    result['consumed_file_entries'] = len(consumed)
    result['status'] = 'SAVED_CANONICAL_ATTRIBUTION_READBACK_PASS_SCOPE_ONLY'
finally:
    result['checks_total'] = len(checks)
    result['checks_passed'] = sum(c['pass'] for c in checks)
    result['failed_checks'] = [c['name'] for c in checks if not c['pass']]
    print(json.dumps(result, indent=2, allow_nan=False))
```

Exact execution command, run from `/workspace/scratch/a83c191d516f/continual-research-takehome`:

```sh
python - <<'PY'
from pathlib import Path
p=Path('reviews/FROZEN_ATTRIBUTION_ACTUAL_REVIEW.md')
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
exec(compile(code,str(p)+'#saved-readback','exec'))
PY
```

Complete observed readback output:

```json
{
  "status": "SAVED_CANONICAL_ATTRIBUTION_READBACK_PASS_SCOPE_ONLY",
  "model_executions": 0,
  "factor_fits": 0,
  "new_selection": false,
  "stages": {
    "discovery": {
      "rows": 1762,
      "annual_arithmetic_mean": {
        "market_component": 3.744750652560767e-15,
        "residual_factor_component": 0.03153697702466987,
        "remainder_component": 0.02224429715723772,
        "full_cost": 0.005879786749547073,
        "gross_return": 0.05378127418191134,
        "net_return": 0.04790148743236427
      },
      "annual_volatility": {
        "market_component": 7.617122638828165e-15,
        "residual_factor_component": 0.05123216526808726,
        "remainder_component": 0.025643171197694072,
        "full_cost": 0.00014876646974617988,
        "gross_return": 0.06841991720011589,
        "net_return": 0.06841558128436026
      },
      "gross_covariance_contribution": {
        "market_component": -3.121305271857318e-15,
        "residual_factor_component": 0.7101092434775335,
        "remainder_component": 0.28989075652246965
      },
      "mean_abs_estimated_beta_exposure": 5.6502642864084785e-14,
      "max_abs_estimated_beta_exposure": 1.4101744418980702e-13,
      "rank_min": 10,
      "rank_max": 10
    },
    "validation": {
      "rows": 1007,
      "annual_arithmetic_mean": {
        "market_component": -1.018552577946654e-15,
        "residual_factor_component": 0.014152620550698887,
        "remainder_component": 0.014694411489606873,
        "full_cost": 0.0020875968449677613,
        "gross_return": 0.028847032040304733,
        "net_return": 0.026759435195336974
      },
      "annual_volatility": {
        "market_component": 1.2603540634439628e-14,
        "residual_factor_component": 0.025714315830443875,
        "remainder_component": 0.023979320070762387,
        "full_cost": 7.665739742155715e-05,
        "gross_return": 0.040590398398024356,
        "net_return": 0.04059320689960052
      },
      "gross_covariance_contribution": {
        "market_component": 1.9825056617655915e-14,
        "residual_factor_component": 0.5261651101724973,
        "remainder_component": 0.47383488982748334
      },
      "mean_abs_estimated_beta_exposure": 6.247368608672011e-14,
      "max_abs_estimated_beta_exposure": 1.4197432200976404e-13,
      "rank_min": 10,
      "rank_max": 10
    },
    "audit": {
      "rows": 755,
      "annual_arithmetic_mean": {
        "market_component": -8.964271481833884e-15,
        "residual_factor_component": 0.07746454532083091,
        "remainder_component": 0.0226273479580551,
        "full_cost": 0.003331189682351051,
        "gross_return": 0.10009189327887706,
        "net_return": 0.096760703596526
      },
      "annual_volatility": {
        "market_component": 1.0013651663246586e-14,
        "residual_factor_component": 0.038957340489187704,
        "remainder_component": 0.022639612138633945,
        "full_cost": 0.00013480411192103706,
        "gross_return": 0.053777977289993686,
        "net_return": 0.05377893059410654
      },
      "gross_covariance_contribution": {
        "market_component": -4.805364687495886e-15,
        "residual_factor_component": 0.6737720815502403,
        "remainder_component": 0.32622791844976523
      },
      "mean_abs_estimated_beta_exposure": 6.075653503377362e-14,
      "max_abs_estimated_beta_exposure": 1.418765180604096e-13,
      "rank_min": 10,
      "rank_max": 10
    }
  },
  "full_row_max_abs_errors": {
    "component_sum_vs_gross": 2.0816681711721685e-17,
    "component_sum_less_fees_vs_net": 2.0816681711721685e-17,
    "independent_opening_targets_vs_gross": 3.8163916471489756e-17
  },
  "saved_artifact_entries": 19,
  "consumed_file_entries": 11,
  "checks_total": 146,
  "checks_passed": 146,
  "failed_checks": []
}
```

The procedure reads the immutable original packet at its recorded path. A later workspace must restore those exact identified inputs or explicitly remap the packet location without changing their identities. This reviewer did not rewrite any original input, output, manifest, frozen review, release record, or handoff file. The earlier source/synthetic review remains pinned at its pre-execution identity; the present report is a separate post-execution readback.
