"""E2E release check: validate and execute the actual exported submission ZIP.

Written before moving F to the submission root. Uses constructed data only;
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

FILES = {
    'README.md', 'requirements.txt', 'strategy.py',
    'model_f/__init__.py', 'model_f/allocator.py', 'model_f/config.py',
    'model_f/engine.py', 'model_f/factor_risk.py', 'model_f/policy.py',
}
MAINTENANCE = {
    '.gitattributes', '.gitignore', 'AGENTS.md',
    '.github/scripts/check_submission.py', '.github/workflows/submission.yml',
}
FROZEN_BLOBS = {
    'model_f/__init__.py': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391',
    'model_f/allocator.py': 'dc1cfcd4a1c7a3a4c1371525f3946518f5c7e01f',
    'model_f/config.py': '03d427d67f3f87eb22850ac4f7acc8e581ba1b2c',
    'model_f/engine.py': '30397d946d967265ef28cbaa1165d267f1077760',
    'model_f/factor_risk.py': '33a46ec19c9d8b227b917c935b9132eacfffe99c',
    'model_f/policy.py': 'eef0be64dc44502a42378ee738c1cb4c5412c55d',
    'requirements.txt': 'f8c52fbb464d1ce17380b1450a954b25918e7459',
}
RATIONALE = (
    'We selected a parsimonious, causally fitted factor-variance adjustment '
    'because its historical improvement survives removing the explicit market '
    'sleeve and increasing trading costs, while improving the factor-variance '
    'forecasting diagnostic. The incremental Sharpe remains statistically '
    'uncertain, and a simpler total-risk scaling control performs similarly.'
)
# Executable structure of the previously audited F strategy entry point.
ENTRYPOINT = '''from model_f.factor_risk import FactorPolicy
POLICY = FactorPolicy()
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
    days, stocks = 420, 48
    x = np.empty((days, stocks, 13), dtype=np.float64)
    x[0] = rng.normal(size=(stocks, 13))
    for s in range(1, days):
        x[s] = .99 * x[s - 1] + np.sqrt(1 - .99**2) * rng.normal(size=(stocks, 13))
    r = .008 * rng.normal(size=(days, stocks)) + .003 * rng.normal(size=(days, 1))
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
        require(np.isfinite(net).all(), 'nonfinite net cashflows')
        return forecast.copy(), np.array(targets), np.array(net)

    comparisons = {}
    def equal(name, a, b):
        error = float(np.max(np.abs(a - b), initial=0.))
        comparisons[name] = error
        require(error <= 1e-10, f'{name}: error {error}')

    full = replay(r, x)
    prefix = replay(r[:379], x[:379])
    equal('prefix_forecasts', full[0][:379], prefix[0])
    equal('prefix_positions', full[1][:len(prefix[1])], prefix[1])
    equal('prefix_cashflows', full[2][:len(prefix[2])], prefix[2])
    for kind in ('returns', 'characteristics', 'joint'):
        rr, xx = r.copy(), x.copy()
        cut = 378
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
    with zipfile.ZipFile(output) as archive, tempfile.TemporaryDirectory(prefix='f_submission_') as temp:
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
            require(actual == expected, 'audited F source changed: ' + name)
        module = ast.parse((package / 'strategy.py').read_text())
        note = ast.get_docstring(module)
        require(note is not None and 150 <= len(note.split()) <= 650, 'missing or oversized strategy note')
        require(RATIONALE in ' '.join(note.split()), 'selection rationale missing from strategy note')
        require(RATIONALE in ' '.join((package / 'README.md').read_text().split()), 'README rationale missing')
        module.body = module.body[1:]
        require(ast.dump(module) == ast.dump(ast.parse(ENTRYPOINT)), 'F executable entry point changed')
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
        'entrypoint_executable_ast_unchanged': True, 'e2e': result}
    output.with_suffix('.checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
