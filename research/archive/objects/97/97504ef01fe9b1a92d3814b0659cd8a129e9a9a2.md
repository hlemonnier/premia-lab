# Audit observer failures

The first attempted V2 and B0 observer launches exited1 before importing any
strategy or producing any economic observation. The observer summary dictionary
had one extra closing brace. Both stderr logs, exact commands and the executed
observer source are preserved under `failed_parse_attempt_001/`. The first B05
command had been prepared but was not launched.

The extra brace was removed, with no change to any strategy or to the planned
analysis. The corrected observer is executed as attempt002. The prior peer review
covered API forwarding, noninterference, chronology and comparisons; it did not
catch this Python parse error. Successful replays, if completed, are separately
identified by their output directories and exit statuses.
