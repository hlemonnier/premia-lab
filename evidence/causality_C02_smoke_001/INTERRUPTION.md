# Infrastructure interruption

The orchestration stopped this run with Ctrl-C (tool exit 130) after observing that the global Python profiling hook, used only for partial-failure evidence, substantially distorted runtime. Completed comparisons remain in summary.json; the complete requested gate was not executed. This is not a candidate causality failure or pass. The corrected harness uses exception-only traceback inspection and is run into a fresh smoke_002 directory with the same candidate and configuration. Original files and commands are preserved.

Timing qualification: replacement baselines had shorter rebalance portions but longer forecast wall times amid shared-machine work, leaving overall wall time similar. Thus the revision removes avoidable instrumentation; these concurrent observations do not establish a controlled overall speedup or prove profiling alone caused the original total delay.
