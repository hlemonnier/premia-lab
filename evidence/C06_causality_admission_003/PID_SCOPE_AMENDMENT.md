# PID namespace evidence correction before reporter execution

27 October 2026, Europe/Paris. The original supplemental plan and admission hashes remain unchanged. The original reporter and the version after the independent configuration/path review are preserved separately. No reporter had been executed when this amendment was approved by the root agent.

The original reporter required39 globally distinct numeric worker PIDs. Independent review identified that separate execution-controller invocations use separate PID namespaces. Actual saved environment records show controller PID2 and parent PID1 for every concurrently launched group; child PIDs6,8,... recur in different groups. Numeric PID values are therefore scoped to each controller execution. Repeated values across those separate executions do not imply module state reuse. The unchanged harness explicitly launches a new Python subprocess for every scenario, using separate complete manifests and logs.

The root approved the following evidence correction before reporter execution: require13 distinct worker PIDs inside each group, each worker's recorded parent PID equal to that group's controller PID, and39 distinct `(group, worker_pid)` identities across the three independently launched controller sessions. Preserve each controller and worker execution record. This corrects the interpretation of process identifiers; it changes no candidate, input scenario, protected mask, numerical tolerance, scoring condition or economic experiment.

This amendment does not waive the separate exact historical forecast/target hash reconciliation. A subsequent observed mismatch to historical bytes must remain a failed historical reproducibility check, even if all current-run protected-output comparisons pass.
