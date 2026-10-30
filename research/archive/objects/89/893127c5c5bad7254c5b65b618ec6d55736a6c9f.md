# Reproduce the preflight-001 inventory failure

## Status and purpose

This supplementary procedure was documented after independent review. **It has not been executed.** The original `summary.json`, `run.log`, `rerun.txt`, `expectations.md`, `runner_used.py` and inventory manifest remain unchanged.

Run 001 failed before reading market data because its original runner counted every file under the working source directory and required a total of twelve. Two incidental files made that count fourteen. This was a preflight-harness defect; it did not establish a dataset defect.

The historical `rerun.txt` refers to the live runner that was subsequently corrected. The preserved old runner also expects a `PREFLIGHT_PLAN.md` one directory above its own directory. The setup below reconstructs that layout in a fresh temporary directory and uses the frozen run-001 runner and expectations. It copies the twelve original source members and adds two harmless, deliberately named incidental fixtures to reproduce the same inventory-count failure deterministically.

The fixtures reproduce the **counting defect**. They do not claim to recreate the historical incidental files' contents or transient lifecycle. The historical inventory remains available in `source_manifest.json`.

## Required setup and inputs

- The project tree remains at `/workspace/scratch/305f831f543f/continual_takehome`.
- The preserved original source files remain under `source/Quant Research Take-Home`.
- `evidence/preflight_002/source_manifest.json` identifies exactly the twelve original members and their SHA-256 hashes.
- Run-001 `runner_used.py` and `expectations.md` are available in this directory.
- Use the recorded primary-runtime Python executable below; numpy and pandas are required by the frozen runner. See `environment.json` for recorded versions.
- Allow space in `/tmp` for an isolated copy of the original source. The procedure creates a fresh directory and does not edit the project source or historical evidence.

If reproducing on another machine, change the project path and Python executable to that machine's equivalents and use the versions recorded in `environment.json`.

## Exact reproduction command

```bash
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python - <<'PY'
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

project = Path('/workspace/scratch/305f831f543f/continual_takehome')
historical = project / 'evidence/preflight_001'
original_source = project / 'source/Quant Research Take-Home'
original_manifest = json.loads(
    (project / 'evidence/preflight_002/source_manifest.json').read_text()
)

reproduction = Path(tempfile.mkdtemp(prefix='continual-preflight001-reproduction-'))
(reproduction / 'tools').mkdir()
isolated_source = reproduction / 'source'
isolated_source.mkdir()

if len(original_manifest) != 12:
    raise RuntimeError('Expected exactly twelve original source members')

for item in original_manifest:
    relative = Path(item['path'])
    if relative.is_absolute() or '..' in relative.parts:
        raise RuntimeError('Unexpected manifest path')
    src = original_source / relative
    digest = hashlib.sha256()
    with src.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    if src.stat().st_size != item['bytes'] or digest.hexdigest() != item['sha256']:
        raise RuntimeError(f'Original source identity mismatch: {relative}')
    dst = isolated_source / relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

for number in (1, 2):
    (isolated_source / f'incidental_fixture_{number}.txt').write_text(
        'Benign fixture for reproducing the overbroad inventory count.\n'
    )

frozen_runner = reproduction / 'tools/preflight.py'
shutil.copy2(historical / 'runner_used.py', frozen_runner)
shutil.copy2(historical / 'expectations.md', reproduction / 'PREFLIGHT_PLAN.md')
output = reproduction / 'evidence'
command = [
    sys.executable, str(frozen_runner),
    '--source', str(isolated_source), '--out', str(output),
]
(reproduction / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
result = subprocess.run(command, capture_output=True, text=True, check=False)
(reproduction / 'stdout.log').write_text(result.stdout)
(reproduction / 'stderr.log').write_text(result.stderr)

summary_path = output / 'summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
first_check = (summary.get('checks') or [{}])[0]
expected_failure_observed = (
    result.returncode == 1
    and summary.get('status') == 'FAIL'
    and summary.get('exit_code') == 1
    and first_check.get('name') == 'source_file_count'
    and first_check.get('status') == 'FAIL'
    and first_check.get('actual') == 14
    and len(summary.get('checks', [])) == 1
    and not (output / 'scorer_report.txt').exists()
)
print(json.dumps({
    'reproduction_directory': str(reproduction),
    'frozen_runner_exit_code': result.returncode,
    'expected_failure_observed': expected_failure_observed,
    'summary': str(summary_path),
    'stdout': str(reproduction / 'stdout.log'),
    'stderr': str(reproduction / 'stderr.log'),
}, indent=2))
raise SystemExit(0 if expected_failure_observed else 2)
PY
```

## Expected outcome and interpretation

The **frozen runner** should exit with code 1 and save a `FAIL` summary whose sole recorded check is `source_file_count`, actual value 14. It should stop before market CSV analysis or any scorer report. The wrapper exits with code 0 only when it observes that expected failure; wrapper success therefore means the historical harness defect was reproduced, not that a preflight or strategy passed.

Inspect the printed temporary directory, `command.json`, stdout/stderr logs, preserved runner and plan, and the new evidence summary. Unexpected results should be reported as such. No actual results from this supplementary procedure are claimed until it is executed.
