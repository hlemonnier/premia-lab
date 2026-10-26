# Same-affinity reproduction

The executed controller was launched under `taskset -c 8`; all workers inherited that single CPU. `rerun.txt` already freezes code, configuration and inputs and constrains each worker to one available CPU. For the same original CPU on this machine, use `bash rerun_same_affinity.sh`. These reproduction scripts are supplied commands, not an additional claimed completed run. On another machine choose one allowed CPU and retain the declared single-thread environment. Gate timing is instrumentation- and load-dependent and is not the candidate runtime qualification.
