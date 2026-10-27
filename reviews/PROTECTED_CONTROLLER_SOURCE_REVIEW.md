# Independent source review: protected replay controller

27 October 2026, Europe/Paris. Reviewed by the lead agent before either controller E2E and before protected market access. The implementation owner is a separate verification agent. This is source review, not an executed-test claim.

Reviewed controller: `tools/run_protected_candidate.py`, SHA256 `d3c3cfd4a1fde10398fc5546f3dc48d395f68a4c06fbe73311c8b5c2cdc37dfe`. The prospective replay plan is `32dc6a11c84ce4009490cccd057f0b0836f22581ef42e05ede77c51ebb0dd436`. The original protocol, admission plan, scorer and metric helper are pinned separately in the controller.

## Admission and information boundary

Actual validation or audit requires an exact root-owned manifest and its supplied hash. Before any protected numeric parsing, the controller checks the stage, candidate identities, configuration, source closure, engineering evidence, original discovery reference and frozen control-file identities. Audit additionally requires a single selected candidate and the prior selection record. The manifest is an execution record of the lead's admission decision; writing a matching status string does not itself supply approval.

The protected loader checks original raw-file identities, records that access has begun before parsing, and limits numeric reads to the approved length. It preserves canonical Fortran-order returns and C-order characteristics and checks the complete discovery input prefix against the existing cache. It does not call the supplied unrestricted loader. Failures after access begins remain recorded as exposed, including incomplete runs.

The two engineering modes accept only the original C06 configuration. Discovery parity copies the existing discovery arrays. The zero fixture contains no market observations. Neither mode grants admission to validation or audit.

## Continuous trading and accounting

One unchanged official scorer call starts at row252 and continues through the original endpoint. The controller records forecasts, targets, held books, target-day indices and both candidate and adapter timing. It checks finite shapes, position caps, gross exposure, held-book immutability, path solvency, all expected calls and the original target/score sequences.

Captured costs and closing gross exposure must equal the scorer output exactly. Independent vectorized reconstruction checks earned gross return, the original gross-return drift denominator, and all full fees with the already frozen arithmetic tolerance. The original first trade remains free and later closing costs remain charged. Full input and source hashes are rechecked after execution.

For actual market replays, discovery forecasts, targets and held books must reproduce the original NPY file hashes exactly. The original economic and net-return ledger prefix must also match exactly. A longer input cannot silently change an earlier decision or substitute a new historical reference.

## Reporting and failures

The validation masks contain504,503 and1,007 observations; audit contains755. Pooled statistics use the pooled daily rows. The original population-standard-deviation convention is retained. Zero-variance ratios remain null with reasons, and the zero fixture explicitly requires that behavior. Candidate feasibility is reported separately from whether the workflow executed successfully; an economically ineligible result is retained.

The runner refuses output-directory reuse, copies its executed source/configuration/reference/control files, records a frozen rerun command, and preserves errors and incomplete artifacts. Rerunning an actual protected mode still requires the exact approved manifest. The source review also checked that the rerun uses the copied candidate closure, helper, scorer, plans and reference.

Two pre-execution implementation defects were corrected before freezing: a mistyped scorer hash and serialization of dictionary keys. These did not execute a market or synthetic workflow and did not expose protected observations. No strategy source, parameter, score mask or tolerance changed.

## Disposition

Source review found no remaining blocker to the two prospectively specified engineering E2Es. The lead authorized only discovery parity and synthetic zero on the frozen controller. Actual protected access remains blocked until those workflows complete, their saved evidence is independently read back, and the lead freezes the concrete nomination manifest. This review does not establish absence of research overfitting, universal causality, or future profitability.
