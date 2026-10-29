# Independent V3 integration evidence audit

29 October 2026, Europe/Paris. Reviewer: v3_evidence_audit.

Pin the reviewed repository `hlemonnier/continual-research-takehome` at
`978824d4b6140c43566ebd61a3ee8157f4080e35`. The prior production head is
`c51d31fe63c68255f2220935a8bc615c62bd1d0c`; the published research winner is
`9e56aa755d20c5876485188f4c50ce959f6d63f3`.

This scope permits static review of the committed verification specification,
harnesses, reports and logs; observational reconciliation of their recorded
numbers; exact source/file identity recording; and identification of missing
evidence. It does not authorize another predictive variant, parameter choice,
or execution of the strategy. Existing input history is exposed development.

Questions: whether the integration checks implement their frozen comparisons;
what the reference replacement proves; whether the runtime and clean-folder
logs support their descriptions; whether failure-path coverage is accurately
reported; and what minimal extra evidence would close a material gap. Distinguish
actual code defects from provenance gaps and unexecuted or unexercised checks.

Retain source copies fetched from the exact GitHub commit, their remote Git blob
SHAs and local SHA256 values. Cite exact files and line ranges in the review.
No original code, scorer, source inputs, prior results or deployed package may be
modified. Root owns any separately specified independent full-workflow replay;
this reviewer initially executes none and does not invent retrospective unit
tests. A completed review records both support and limitations, without treating
missing evidence as proof of a numerical or causal failure.
