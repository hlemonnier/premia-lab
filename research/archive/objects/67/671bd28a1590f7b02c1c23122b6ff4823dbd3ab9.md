# Execution record

28 October 2026, Europe/Paris.

Parent reviewed `PLAN.md` and `readback.py` before execution and authorized the
fixed observational method. The parent specifically confirmed retrospective
mixture scaling is labeled, stage masks match, and EW risk uses previous outcomes
only. No additional pairs or policy scores were admitted after results.

Working directory:
`/workspace/scratch/a83c191d516f/continual-research-takehome`

Exact executed command:

```bash
python evidence/v2_score_opportunity_20261028/readback.py > evidence/v2_score_opportunity_20261028/stdout.log 2> evidence/v2_score_opportunity_20261028/stderr.log
```

Exit code: **0**. Tool wall time: 0.113232816 seconds. All29 saved ledgers passed
the predeclared shape, finiteness, row, fee and common-market reconciliation.
No strategy code ran. No new forecasting policy or portfolio was scored.

`results.json` records the exact plan, source and input-manifest hashes, Python
and NumPy versions, platform, every policy summary, all three specified reference
mixtures and all five risk buckets. `v2_lagged_risk_diagnostic.csv` preserves the
lagged estimate and bucket labels. Its first lag estimate is deliberately NaN;
the first126 observations are excluded from bucket analysis. JSON statistics
are finite. `earlier_reported_results.json` transcribes the already reported
C01–C12 discovery metadata, whose identities are also in the input manifest.

No failed execution or unexecuted verification is relabeled as passed. The
descriptive mixture accounting is not a replay of real aggregate trades.
