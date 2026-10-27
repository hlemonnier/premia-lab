# Independent follow-up review of the frozen C09 policy

27 October 2026, Europe/Paris. Reviewer: the independent follow-up causality agent. Base checkpoint: `4e2a17816ce674c6a781771ca1e6cbe24c1d19c6`.

## Scope and current verdict

The newer recovered checkpoint already completed the twelve-configuration discovery cycle, selected C09 by the frozen validation rule, and opened the single-policy audit. This review does not restart that cycle. It reads the exact handoff, original assignment/scorer, causal controller and its saved evidence, nomination/selection records, and existing economic ledgers. It introduces no candidate, unit test, parameter change, new performance window, or model execution.

**Source conclusion: no identified lookahead path in the reviewed C09 package.** The implementation and the finite existing intervention evidence support that statement. They do not prove that no future implementation failure is possible, that research selection introduced no optimism, or that the hidden continuation will be profitable.

The compact saved-artifact reconciliation below is specified before its execution. Its status and actual output are recorded at the end. This is an independent arithmetic and identity readback of completed runs, not a new strategy E2E execution.

## Information flow checked against the supplied interface

| Item | Observed implementation | Review judgment |
|---|---|---|
| Prediction for row `t` | `_basis(X[t-1])` multiplied by the current coefficients | Uses a published panel strictly before earning day `t`. |
| Latest training observation | Design `X[t-2]` paired with `R[t-1]` | Does not train on the return being predicted. |
| Label market adjustment | Beta from `R[:t-1]`, followed by the observed market return on `t-1` | Both are known when forecasting `t`; the beta estimate itself excludes its label day. |
| Feature normalization | Means/scales, clipping, centering and squares computed from one panel | No full-history mean, rank, PCA, selected date or future normalization. |
| First active forecast | 126 matured pairs, hence row 127 | Earlier forecasts are zero. No startup estimates are applied retrospectively. |
| Forecast learning state | Gram matrix, response moment, effective mass and coefficients are local variables | No fitted full-history object survives to seed `rebalance`. |
| Portfolio risk | Recomputed from at most the last 252 supplied return rows | Under the scorer, these rows end before the target earning day. |
| Module globals | Static validated `CONFIG`; last-call diagnostics written for reporting | Forecast does not learn global state; diagnostics are never read to select a future target. |
| Length dependence | Allocation and loop termination use the available length | No calendar cutoff, future-dependent refresh policy or full-length hyperparameter. |
| External access | No project file reads, network, random seed search, subprocess or wall-clock decision in the imported candidate closure | Candidate cannot read saved validation/audit results or fitted research artifacts. |

The handoff entry point statically configures the original engine and exposes direct aliases. Its helper defaults are development defaults, but the wrapper explicitly overrides every C09 setting. The frozen literal configuration, rather than the helper's historical introductory prose, governs the selected method. This is already disclosed in the top-level note.

The original scorer supplies the actual drifted book, earns the day's return, then charges that day's closing trade. Its initial trade is free, the first empty-book row is removed, and the final supplied return is not earned. The reviewed strategy does not override this accounting. The verifier protects forecasts through a changed row `c`, targets for earning days through `c`, and economic rows strictly before `c`; the changed row's closing trade is correctly outside the protected economic interval.

## What the existing causal evidence establishes

`verification/C09_FULL_DISCOVERY_CAUSALITY_PLAN.md` prospectively specifies nineteen fresh-process runs: baseline, repeat, three intervention modes at five cutoffs (127, 253, 254, 1008 and 2015), shorter prefix and synthetic append. The saved review reports 57 nonempty protected numerical comparisons, all exact, and 15 empty comparisons explicitly not applicable. These are finite representative paths, not nineteen independent estimates of profitability and not coverage of every possible input.

The source review inspected `tools/verify_causality.py` as well as the candidate: the worker calls the original scorer, captures the actual returned forecasts/targets, verifies caller-input integrity, and compares the correct index masks. It does not substitute the baseline targets into the perturbed run. All fitted candidate state remains local, so a hidden forecast-created risk cache is not an unresolved pathway in this package.

The C/F-layout correction preserved the original failed evidence and restored the original loader representation; no model parameter or numeric tolerance was widened. Existing same-representation comparisons are exact. This does not promise byte-identical arrays across arbitrary NumPy/BLAS/platform changes. The specified tolerance and observed exact equality are different claims.

The recorded 25,200-row workflow supports computational feasibility on that machine with one numerical-library thread. It repeats discovery inputs; it is neither a new alpha sample nor proof against every pathological numeric input. The learner has fixed-dimensional sufficient statistics, while the required returned forecast array grows with the number of days.

## Remaining research and portfolio limitations

1. **Selection exposure remains.** Twelve complete discovery configurations and the diagnostic decisions are research exposures. Only two frozen nominees entered validation, and only selected C09 entered the audit. The separate audit is useful confirmation of that frozen policy; it does not erase earlier selection or justify evaluating redesigned policies there.
2. **Bootstrap ranges are conditional summaries.** The fixed 21/63-day block resampling describes variability in observed daily ledgers under its resampling assumptions. It is not a universal probability that future alpha is positive, and it does not guarantee stationarity for decades. A paired model comparison needs paired returns; independent single-model error bars cannot establish superiority.
3. **Market hedge is estimated.** The equality constrains estimated beta, not the beta of unknown future net returns. C09 does not separately constrain dollar neutrality, which the assignment does not require. Near-zero realized beta on the saved periods is evidence about those periods only.
4. **C09's residual risk model is diagonal.** After hedging its estimated market beta, common residual shocks can remain. The more elaborate C06 was evaluated and lost the prescribed pooled validation comparison. That empirical selection does not establish that off-diagonal risks are absent or irrelevant.
5. **The final gross cap is an approximation.** The scalar-dual allocator solves the stated diagonal-risk, box and beta constrained one-step problem with absolute turnover cost. Proportional postsolve gross scaling can turn a no-trade coordinate into a trade and is not the exact jointly gross-constrained optimum. This limitation is acknowledged in the frozen note; it should not be described as a fully optimal transaction-cost policy.
6. **The 20-day cost horizon is a fixed control choice.** It is not proof that all predicted alphas have the same measured persistence, nor does characteristic autocorrelation identify predictive decay. Full actual costs are still deducted by the scorer. Doubling a saved fee ledger is a fixed-decision stress, not a reoptimized higher-cost strategy run.
7. **Caps do not guarantee universal solvency.** Gross exposure of one and per-stock bounds reduce risk on tested paths, but short returns can be arbitrarily adverse under unrestricted future inputs. The code raises on invalid/nonfinite or unrepresentable arithmetic; the package does not claim a successful fallback for every malformed input. No such malformed-input contract is established by the supplied clean dataset.

The notes' broad concern about Sharpe noise is correct, but their displayed approximation mixes annual and per-observation units. For IID Gaussian daily returns, the usual delta-method expression implies approximately `SE(SR_annual) = sqrt((1 + SR_annual**2/(2*252))/years)`. Serial dependence, non-normality, adaptive policies and selection require additional treatment. Also, contemporaneous characteristic/return correlation alone does not prove that the characteristic was constructed from returns; common causes are another explanation.

## Prospective compact saved-evidence reconciliation

Inputs: the four frozen handoff files, original C09 configuration, protocol, original scorer, nomination/selection/package manifests, and the existing validation C06/C09 and audit C09 daily CSVs and summaries. No new return/characteristic observations are requested. This procedure does not rerun the candidate or replace the historical comprehensive array readback.

Failure modes: changed candidate bytes, changed configuration, broken selected-policy/package bindings, substituted daily ledgers, wrong endpoints, incorrect net arithmetic or beta/Sharpe reporting, and an audit continuation that changes the earlier validation economics. Each mismatch must fail visibly. Expected: all stated identities and endpoints match, daily `net = gross - full_cost` is exact after Python-float parsing, summaries agree within `1e-12`, the selected policy is the frozen higher pooled validation score, and the audit's entire earlier C09 validation economic prefix remains exact. The arithmetic tolerance is chosen here before this readback; it does not amend any original gate.

Rerun from the repository root with Python and NumPy available. The following is read-only and prints the complete compact result:

```python
import ast
import csv
import hashlib
import json
import zipfile
from pathlib import Path
import numpy as np

root = Path('.')
checks = []
result = {'status': 'RUNNING', 'model_executions': 0, 'new_selection': False}
def load(path):
    return json.loads((root / path).read_text())
def sha(path):
    return hashlib.sha256((root / path).read_bytes()).hexdigest()
def require(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(name)
def bound(name, path, expected):
    require(name, sha(path) == expected)
def ledger(path):
    with (root / path).open(newline='') as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]

try:
    sel = load('research/VALIDATION_SELECTION.json')
    nom = load('research/AUDIT_NOMINATION.json')
    pkg_path = 'evidence/handoff_discovery_001/package_manifest.json'
    pkg = load(pkg_path)
    bound('selection_protocol', 'RESEARCH_PROTOCOL.json', sel['protocol_sha256'])
    bound('audit_protocol', 'RESEARCH_PROTOCOL.json', nom['protocol_sha256'])
    bound('scorer', 'source/Quant Research Take-Home/score.py', nom['scorer_sha256'])
    bound('validation_nomination', sel['validation_nomination_path'], sel['validation_nomination_sha256'])
    bound('selection_binding', nom['selection_record']['path'], nom['selection_record']['sha256'])
    bound('package_binding', pkg_path, nom['handoff_package_manifest_sha256'])
    config = load(sel['config_path'])
    bound('config', sel['config_path'], sel['config_sha256'])
    require('one_audit_policy', len(nom['candidates']) == 1 and nom['selected_candidate_id'] == sel['selected_candidate_id'] == config['candidate_id'])
    for path, digest in pkg['files'].items():
        bound('handoff/' + path, 'handoff/' + path, digest)
    archive_path = 'artifacts/continual_research_C09.zip'
    archive_manifest = load('artifacts/handoff_archive_manifest.json')
    bound('frozen_archive', archive_path, archive_manifest['sha256'])
    require('archive_size', (root / archive_path).stat().st_size == archive_manifest['bytes'] == 8709)
    with zipfile.ZipFile(root / archive_path) as archive:
        require('exact_four_archive_members', sorted(archive.namelist()) == sorted(pkg['files']) and len(archive.namelist()) == 4)
        for path, digest in pkg['files'].items():
            require('archive_member:' + path, hashlib.sha256(archive.read(path)).hexdigest() == digest)
    module = ast.parse((root / 'handoff/strategy.py').read_text())
    literal = next(ast.literal_eval(n.value) for n in module.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_FROZEN_CONFIG' for t in n.targets))
    require('literal_config', literal == config)
    require('engine_source', sha('handoff/model/strategy.py') == sel['source_sha256']['submission/strategy.py'])
    require('portfolio_source', sha('handoff/model/portfolio.py') == sel['source_sha256']['submission/portfolio.py'])
    result['metrics'] = {}
    ledgers = {}
    for tag, folder, period, lo, hi in [
        ('C06_validation', 'evidence/validation_C06_001', 'pooled_validation', 2016, 3023),
        ('C09_validation', 'evidence/validation_C09_001', 'pooled_validation', 2016, 3023),
        ('C09_audit', 'evidence/audit_C09_001', 'locked_audit', 3024, 3779),
    ]:
        manifest = load(folder + '/artifact_manifest.json')
        for name in ('daily.csv', 'summary.json', 'config.json', 'source/score.py'):
            bound(tag + ':' + name, folder + '/' + name, manifest[name]['sha256'])
        rows = ledger(folder + '/daily.csv')
        ledgers[tag] = rows
        require(tag + ':full_row_indices', [int(r['return_index']) for r in rows] == list(range(253, max(int(r['return_index']) for r in rows) + 1)))
        require(tag + ':day_labels', all(r['csv_day_label'] == r['return_index'] + 1 for r in rows))
        require(tag + ':net_arithmetic', all(r['net_return'] == r['gross_return'] - r['full_cost'] for r in rows))
        active = [r for r in rows if lo <= r['return_index'] < hi]
        require(tag + ':score_indices', [int(r['return_index']) for r in active] == list(range(lo, hi)))
        gross = np.array([r['gross_return'] for r in active])
        fee = np.array([r['full_cost'] for r in active])
        net = gross - fee
        market = np.array([r['raw_market_return'] for r in active])
        beta = np.linalg.lstsq(np.column_stack([np.ones(len(market)), market]), net, rcond=None)[0][1]
        metrics = {
            'net_sharpe': float(np.sqrt(252) * net.mean() / net.std(ddof=0)),
            'annual_arithmetic_net_return': float(252 * net.mean()),
            'annual_net_volatility': float(np.sqrt(252) * net.std(ddof=0)),
            'annual_full_cost': float(252 * fee.mean()),
            'realized_net_market_beta': float(beta),
        }
        summary = load(folder + '/summary.json')['metrics'][period]
        for key, value in metrics.items():
            require(tag + ':' + key, abs(value - summary[key]) <= 1e-12)
        result['metrics'][tag] = {'observations': len(active), **metrics}
    economic = ('gross_return', 'full_cost', 'net_return', 'closing_target_gross', 'raw_market_return')
    v = ledgers['C09_validation']
    a = ledgers['C09_audit']
    require('entire_2770_row_prior_validation_economic_prefix_exact', len(v) == 2770 and all(all(x[k] == y[k] for k in economic) and x['return_index'] == y['return_index'] for x, y in zip(v, a[:len(v)])))
    require('frozen_validation_ranking', result['metrics']['C09_validation']['net_sharpe'] > result['metrics']['C06_validation']['net_sharpe'] and sel['ranking_eligible_by_primary'][0] == config['candidate_id'])
    result['status'] = 'SAVED_ARTIFACT_READBACK_PASS_SCOPE_ONLY'
finally:
    result['checks'] = checks
    result['passing_checks'] = sum(c['pass'] for c in checks)
    result['total_checks'] = len(checks)
    print(json.dumps(result, indent=2, allow_nan=False))
```

## Execution record

**Executed successfully: 63 of 63 recorded checks passed, process exit code 0.** No candidate was executed and no new model selection occurred. The procedure was recorded before this readback, including the archive/member identity checks requested before launch. No failure, exception, tolerance change or result-driven adjustment occurred.

Exact command, run from `/workspace/scratch/a83c191d516f/continual-research-takehome`:

```sh
python - <<'PY'
from pathlib import Path
p=Path('reviews/NOTES_FOLLOWUP_CAUSALITY_REVIEW.md')
code=p.read_text().split('```python\n',1)[1].split('\n```',1)[0]
exec(compile(code, str(p)+'#compact-readback', 'exec'))
PY
```

Observed summary printed by that command:

```json
{
  "status": "SAVED_ARTIFACT_READBACK_PASS_SCOPE_ONLY",
  "model_executions": 0,
  "new_selection": false,
  "passing_checks": 63,
  "total_checks": 63,
  "metrics": {
    "C06_validation": {
      "observations": 1007,
      "net_sharpe": 0.39860308981402176,
      "annual_arithmetic_net_return": 0.014825848470750061,
      "annual_net_volatility": 0.03719451466788035,
      "annual_full_cost": 0.006439879129465286,
      "realized_net_market_beta": 0.004670284463437024
    },
    "C09_validation": {
      "observations": 1007,
      "net_sharpe": 0.6592096865251688,
      "annual_arithmetic_net_return": 0.026759435195336974,
      "annual_net_volatility": 0.04059320689960052,
      "annual_full_cost": 0.0020875968449677613,
      "realized_net_market_beta": 0.005858261127586511
    },
    "C09_audit": {
      "observations": 755,
      "net_sharpe": 1.799230712243462,
      "annual_arithmetic_net_return": 0.096760703596526,
      "annual_net_volatility": 0.05377893059410654,
      "annual_full_cost": 0.003331189682351051,
      "realized_net_market_beta": 0.0056655488540628745
    }
  }
}
```

The 63 observed successes comprise 22 protocol, scorer, selection, configuration, handoff and archive identity checks; 13 daily-ledger/summary checks for each of the three completed periods; exact equality of all 2,770 previous C09 economic rows within the longer audit replay; and consistency of the frozen validation ranking. Every individual success is named by the self-contained procedure and printed on rerun. The independent beta calculation uses least squares with an intercept; it agrees with the saved covariance-ratio estimate to the predeclared numerical tolerance.

The archive is exactly 8,709 bytes, with SHA256 `cba024cae44dd84b17b17dcde48e4276e677a52883220c54da455664a770b7fa`. It contains exactly the four pre-audit package members, each matching its original frozen source hash. No historical manifest or source was edited to achieve the result.

This compact reconciliation does not repeat the earlier nineteen causal executions, 25,200-row runtime execution, full drift/target-array reconciliation, or bootstrap simulation. Their previously executed records are reviewed and cited above, rather than relabeled as freshly executed checks. The missing historical partial input artifact and its documented byte-exact recovery remain visible in the original audit evidence; this readback did not touch that artifact.

## Final disposition

No new release-blocking defect was identified in the reviewed frozen package or the compact evidence. Preserve C09's exact bytes and describe its finite causal evidence and positive reserved-audit result accurately. The user notes support several useful diagnostic distinctions, but they do not reopen any now-exposed interval as fresh evidence. A changed alpha model, optimizer or cost rule would be a new policy and would need genuinely unseen evaluation for another clean confirmation.
