# Contributing to Premia Lab

I welcome focused improvements to reproducibility, numerical correctness,
documentation and clearly motivated research. A higher historical Sharpe alone
is not enough to establish that a change is useful.

## Start with a reproducible case

Use Python 3.13, create a virtual environment and install the pinned dependencies:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/check_project.py
python examples/synthetic_demo.py --days 660 --stocks 48
```

The demo uses an independently generated market. Do not describe its results as a
reproduction of the original development benchmark. For a bug report, include the
commit, environment, exact command, expected behavior and a small synthetic example.
Do not attach external benchmark files, private messages, credentials or personal data.

## Propose research before tuning it

For a new experiment, write a short protocol under `research/` before implementing
or scoring it. State the mechanism, baseline, matched control, fixed settings,
information available at each decision, evaluation rule and stopping rule.
Retain unsuccessful runs and distinguish exploratory findings from predeclared tests.

Separate return estimation from risk estimation and execution. Every economic
comparison must use each policy's actual positions, drift and transaction costs.
Do not infer net portfolio value from an improved prediction metric alone.
Previously inspected history does not become a fresh holdout when replayed
chronologically. A change discovered after looking at results must be identified
as exploratory rather than presented as prospectively selected.

## Verification and pull requests

Document failure modes and expected outputs first, then write end-to-end checks
before the implementation they cover. Relevant checks include changed futures,
truncated histories, reset state and separately reconstructed cashflows. Keep
numerical-tolerance exceptions visible; do not change thresholds to hide a failure.

Keep documentation-only changes separate from numerical changes. The maintained
policy and dependency pins are checked by `docs/runtime_manifest.json`; changing
an expected hash is not a substitute for validating the change. Do not rewrite
content-addressed research objects. Add a new result or correction with provenance.

Open a focused pull request from a fork, with the hypothesis or bug, changes,
commands actually executed, observed failures and unexecuted checks. The maintained
repository keeps `main` as its durable branch and research evidence in `research/`.

## Reuse and credit

Contribute only material you have the right to share. Original contributions to
the maintained project are made under its [MIT License](LICENSE), unless explicitly
agreed otherwise. Retain third-party notices and distinguish human decisions,
AI assistance, independent implementations and separate reviews accurately.
See [NOTICE.md](NOTICE.md) for the boundary between original code and external material.
