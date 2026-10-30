# Reproducibility and the data boundary

There are two distinct levels of reproducibility here.

## Public software demonstration

`examples/synthetic_demo.py` creates a new, small simulated market independently of the original benchmark. It exercises the actual N0 interface and portfolio loop. Its output is not expected to match the recorded 1.5508 Sharpe, and a favorable demo score is not evidence for the original research claims.

```bash
python -m pip install -r requirements.txt
python examples/synthetic_demo.py --days 800 --stocks 64
python -m unittest discover -s tests -v
python tools/check_project.py
```

Use Python 3.13. The frozen runtime pins NumPy 2.3.5, SciPy 1.17.0 and scikit-learn 1.8.0. The public demo uses NumPy arrays, not CSV files or pandas.

## Original benchmark results

The historical research used 3,780 source rows, 1,000 stocks, 13 characteristics and an external scorer. The original benchmark, its specification, reference examples and scorer are not redistributed. Exact reproduction of its scores requires legitimate access to those inputs and the recorded environment. The archive provides authored implementations, reports, relevant identities and available summaries; it does not remove this dependency.

The original scorer's SHA-256 was `ff1be0c7d4a2c074f9f5353bcaa536d0b883d5c3224df0bf4e22347ff3e57c96`. Refer to individual archived records for commands and dependencies. A historical report stating that a check passed is archival evidence, not a new execution in this publication task.

## Restoring a research snapshot

```bash
python tools/restore_research.py --list
python tools/restore_research.py --branch research-n0-frozen-review-20261030 --output /tmp/premia-review
```

The destination must be empty. Each archived path is mapped to a content-addressed object with a SHA-256 digest and original Git-blob identity. Duplicate files are stored once; distinct versions are retained. Sanitized copies identify their redactions. Omissions are enumerated for every snapshot.

Restored research is historical code: some experiments rely on old directory layouts or unavailable private inputs. Restoration is not automatic execution and does not claim that every old script passes the maintained public tests.

## Operational tests versus economic evidence

Prefix/future-mutation/reset tests check the implementation's information boundary. The recorded 25,200-day endurance run repeated the original history and checked resources; it was not an unseen future. Neither test establishes absence of selection overfit, future profitability or tail safety.
