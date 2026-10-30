"""E2E release check: validate and execute the actual exported submission ZIP.

Existing N0 archive E2E checks adapted to the single-package layout.
Numerical comparisons and tolerances are unchanged.
Uses constructed data only;
this is a packaging/causality regression check, not an economic validation.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

FILES = {'README.md', 'model_n0/allocator.py', 'model_n0/execution.py', 'strategy.py', 'model_n0/residuals.py', 'model_n0/config.py', 'model_n0/risk.py', 'model_n0/__init__.py', 'requirements.txt', 'model_n0/policy.py', 'model_n0/premia.py', 'model_n0/engine.py'}
MAINTENANCE = {
    '.gitattributes', '.gitignore', 'AGENTS.md',
    '.github/scripts/check_submission.py', '.github/workflows/submission.yml',
}
FROZEN_BLOBS = {'model_n0/__init__.py': '482f7e7a6bfc04b62648347d9c4bea563cae8d40', 'model_n0/allocator.py': 'dc1cfcd4a1c7a3a4c1371525f3946518f5c7e01f', 'model_n0/config.py': 'b336ac32f308807b8afe3bbd7f1be1c80887aff8', 'model_n0/engine.py': 'a6ef8ea51e0a37cbc53fe79a5eb764321d8cc341', 'model_n0/execution.py': 'b7cc050a8502a8d03c15ba89fe755cad0915a4ab', 'model_n0/policy.py': '2e63aae2db04712e54bf91e590f4f708c88c6cc4', 'model_n0/premia.py': 'b8f1bc40194bb234e0ce2478e937a092235212d7', 'model_n0/residuals.py': 'a411f8cc33557ca0116d2bf3dd6479a84d36caf2', 'model_n0/risk.py': 'a653cd7eeea6d952b57f5c7104b9ec23c635ec9d', 'requirements.txt': 'f8c52fbb464d1ce17380b1450a954b25918e7459'}
RATIONALE = 'I selected the frozen N0 own-history correction on top of the GLS ensemble because its historical gain at the supplied fees survives removing the explicit market sleeve and the largest signal sources. Its added value remains statistically uncertain; the model was discovered as a control, and selection on the same exposed history can overstate its future performance.'

# Executable structure of the frozen N0 submission adapter.
ENTRYPOINT = '''from model_n0 import N0Policy
POLICY = N0Policy()
def forecast(returns_history, characteristics_history):
    return POLICY.forecast(returns_history, characteristics_history)
def rebalance(held_positions, expected_returns, returns_history,
              characteristics_history, trading_costs):
    return POLICY.rebalance(held_positions, expected_returns, returns_history,
                            characteristics_history, trading_costs)
'''


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def inside(package: Path) -> dict:
    import numpy as np
    package = package.resolve()
    sys.path.insert(0, str(package))
    import strategy
    require(Path(strategy.__file__).resolve() == package / 'strategy.py', 'wrong imported strategy')
    rng = np.random.default_rng(20261029)
    days, stocks = 760, 48
    x = np.empty((days, stocks, 13), dtype=np.float64)
    x[0] = rng.normal(size=(stocks, 13))
    for s in range(1, days):
        x[s] = .99 * x[s - 1] + np.sqrt(1 - .99**2) * rng.normal(size=(stocks, 13))
    r = .008 * rng.normal(size=(days, stocks)) + .003 * rng.normal(size=(days, 1))
    # Known own-residual reversal ensures the correction is exercised.
    for s in range(1, days):
        r[s, 0] = -.5 * r[s - 1, 0] + .008 * rng.normal()
    from model_n0 import N0Policy
    require(type(strategy.POLICY) is N0Policy, 'N0 must be the only public strategy')
    require(not hasattr(strategy.POLICY, 'mode') and not hasattr(strategy.POLICY, 'shared'),
            'alternate model modes or research caches are forbidden')
    require(not (package / 'model_f').exists() and not (package / 'gls_alpha.py').exists(),
            'legacy model packages are forbidden')
    costs = np.linspace(.0002, .0008, stocks)

    def replay(rr, xx):
        forecast = np.asarray(strategy.forecast(rr, xx))
        require(len(forecast) == len(rr) and np.isfinite(forecast).all(), 'invalid forecasts')
        weights = np.zeros(stocks)
        targets = []
        net = []
        for today in range(252, len(rr) - 1):
            gross_return = float(weights @ rr[today])
            require(np.isfinite(gross_return) and gross_return > -1, 'nonfinite return or ruin')
            held = weights * (1 + rr[today]) / (1 + gross_return)
            weights = np.asarray(strategy.rebalance(
                held, forecast[today + 1], rr[:today + 1], xx[:today + 1], costs,
            ))
            require(weights.shape == (stocks,) and np.isfinite(weights).all(), 'invalid positions')
            require(np.abs(weights).sum() <= 5 * (1 + 1e-12), 'gross bound failed')
            fee = 0.0 if today == 252 else float(costs @ np.abs(weights - held))
            net.append(gross_return - fee)
            targets.append(weights.copy())
        require(all(not name.startswith('model_f') and name != 'gls_alpha'
                    for name in sys.modules), 'legacy module imported')
        require(np.isfinite(net).all(), 'nonfinite net cashflows')
        return forecast.copy(), np.array(targets), np.array(net)

    comparisons = {}
    def equal(name, a, b):
        error = float(np.max(np.abs(a - b), initial=0.))
        comparisons[name] = error
        require(error <= 1e-10, f'{name}: error {error}')

    full = replay(r, x)
    from model_n0.premia import _PremiaPolicy
    reference = _PremiaPolicy().forecast(r, x)
    equal('no_correction_before_activation', full[0][:505], reference[:505])
    require(np.max(np.abs(full[0][505:, :stocks] - reference[505:, :stocks])) > 1e-12,
            'own-history fixture did not activate N0')
    equal('risk_payload_unchanged', full[0][:, stocks:], reference[:, stocks:])
    prefix = replay(r[:631], x[:631])
    equal('prefix_forecasts', full[0][:631], prefix[0])
    equal('prefix_positions', full[1][:len(prefix[1])], prefix[1])
    equal('prefix_cashflows', full[2][:len(prefix[2])], prefix[2])
    for kind in ('returns', 'characteristics', 'joint'):
        rr, xx = r.copy(), x.copy()
        cut = 630
        if kind != 'characteristics':
            rr[cut:] = rng.normal(0, .012, rr[cut:].shape)
        if kind != 'returns':
            xx[cut:] = rng.normal(size=xx[cut:].shape)
        changed = replay(rr, xx)
        equal(kind + '_past_forecasts', full[0][:cut + 1], changed[0][:cut + 1])
        equal(kind + '_past_positions', full[1][:cut - 252], changed[1][:cut - 252])
        require(np.max(np.abs(full[0][cut + 1:] - changed[0][cut + 1:])) > 1e-12,
                'future-mutation test has no effect')
    repeat = replay(r, x)
    for name, a, b in zip(('forecasts', 'positions', 'cashflows'), full, repeat):
        equal('repeat_' + name, a, b)
    return {'synthetic_days': days, 'stocks': stocks, 'comparisons': comparisons,
            'finite_bounded_replays': 6, 'economic_performance_claim': False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--output', type=Path, default=Path('dist/Continual_Research_Submission.zip'))
    parser.add_argument('--inside', type=Path)
    args = parser.parse_args()
    if args.inside:
        print(json.dumps(inside(args.inside), indent=2))
        return
    repo = args.repo.resolve()
    output = args.output.resolve()
    paths = set(subprocess.check_output(
        ['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', args.ref], text=True,
    ).splitlines())
    require(FILES <= paths, f'missing submission-root files: {sorted(FILES - paths)}')
    require(paths <= FILES | MAINTENANCE, f'unexpected tracked files: {sorted(paths - FILES - MAINTENANCE)}')
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', '-C', str(repo), 'archive', '--format=zip',
                    '--output=' + str(output), args.ref], check=True)
    with zipfile.ZipFile(output) as archive, tempfile.TemporaryDirectory(prefix='n0_submission_') as temp:
        names = {i.filename for i in archive.infolist() if not i.is_dir()}
        require(names == FILES, f'export contents differ: {sorted(names ^ FILES)}')
        package = Path(temp)
        for name in names:
            destination = package / name
            require(destination.resolve().is_relative_to(package.resolve()), 'unsafe archive path')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.read(name))
        for name, expected in FROZEN_BLOBS.items():
            data = (package / name).read_bytes()
            actual = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
            require(actual == expected, 'verified N0 component changed: ' + name)
        module = ast.parse((package / 'strategy.py').read_text())
        note = ast.get_docstring(module)
        require(note is not None and 150 <= len(note.split()) <= 650, 'missing or oversized strategy note')
        require(RATIONALE in ' '.join(note.split()), 'selection rationale missing from strategy note')
        require(RATIONALE in ' '.join((package / 'README.md').read_text().split()), 'README rationale missing')
        module.body = module.body[1:]
        require(ast.dump(module) == ast.dump(ast.parse(ENTRYPOINT)), 'audited N0 executable entry point changed')
        env = dict(os.environ, PYTHONPATH='', PYTHONDONTWRITEBYTECODE='1',
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        child = subprocess.run([sys.executable, '-I', str(Path(__file__).resolve()), '--inside', str(package)],
                               cwd=package, env=env, text=True, capture_output=True, timeout=180)
        require(child.returncode == 0, child.stdout + child.stderr)
        result = json.loads(child.stdout)
    receipt = {'passed': True, 'commit': subprocess.check_output(
        ['git', '-C', str(repo), 'rev-parse', args.ref], text=True).strip(),
        'archive': output.name, 'archive_files': sorted(names),
        'archive_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'frozen_helper_and_requirements_checks': len(FROZEN_BLOBS),
        'entrypoint_matches_frozen_n0_adapter': True, 'e2e': result}
    output.with_suffix('.checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
