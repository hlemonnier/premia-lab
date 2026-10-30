# Independent V3 policy/source audit

29 October 2026, Europe/Paris. Reviewer: v3_policy_audit.

Pin the supplied integration at commit
`978824d4b6140c43566ebd61a3ee8157f4080e35` and the prior production engine at
`c51d31fe63c68255f2220935a8bc615c62bd1d0c`. Inspect exact source fetched through
the GitHub connector, preserving file Git-object SHA and SHA256 in
`source_manifest.json`. No production source is modified.

Scope: forecast information clock; virtual/inner/outer book isolation; earned
observation and volatility-controller timing; actual-versus-internal drift;
preservation and wiring of hardened solver/final-book safeguards; session
reset and portable scorer interfaces; scope of the existing integration and
failure-path checks. Interpret existing evidence only to its actual coverage.

This is a static source review and saved-evidence interpretation. No policy is
executed, no new unit tests are written, and no model, parameter, portfolio or
stress variant is added. Another reviewer covers numerical-reference provenance
and root handles the market-sleeve decision and full integration acceptance.
All historical periods are already exposed development data under the user's
score-first instruction and original brief; no new confirmation is claimed.

Expected causal clock: forecast row t uses X[t-1] and beta from returns before t;
its newest matured label is return t-1 paired with X[t-2]. At close s, rebalance
sees rows through s, uses forecast row s+1, updates virtual earned-return moments
only after a previous target has earned, then chooses the next targets. Each
inner portfolio's drift denominator is its own gross return. The original
scorer charges final combined trades; internal fees are not added to outer fees.
