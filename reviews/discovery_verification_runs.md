# Reviewer-owned discovery executions: C03, C06, C08 and C10

All four configurations were admitted by the lead before their outcomes. Each ran through the unchanged official scorer with actual discovery inputs `[0,2016)`, retained scored indices253–2014 (1762 daily observations), and1763 continuous rebalance calls. Each completed exit0 with20 passing workflow checks; recorded cost and gross ledgers reconciled exactly, and frozen source/input identities remained unchanged. These are development results, not untouched-period performance or a substitute for exact-config causality gates.

| Candidate | Net Sharpe | Gross Sharpe | Annual net mean | Annual volatility | Annual full fees | Net beta | Max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|
| C03 faster additive | 0.106491 | 0.351449 | 0.7517% | 7.0590% | 1.7267% | 0.028195 | 16.0091% |
| C06 GLS + factor portfolio | 0.762944 | 0.963122 | 2.5907% | 3.3956% | 0.6810% | 0.006330 | 5.2777% |
| C08 higher gamma | 0.626206 | 0.691187 | 1.1916% | 1.9029% | 0.1236% | 0.006259 | 2.4613% |
| C10 GLS + factor rank50 | 0.739890 | 0.959189 | 1.7307% | 2.3391% | 0.5144% | −0.000089 | 3.7902% |

| Candidate | Block1 net Sharpe | Block2 | Block3 | Block4 | Rescaled calls | Mean candidate rebalance |
|---|---:|---:|---:|---:|---:|---:|
| C03 | 0.830993 | −0.389999 | 0.058515 | 0.203757 | 1704/1763 (96.65%) | 11.1669ms |
| C06 | 0.328476 | 0.957261 | 1.194222 | 0.602360 | 914/1763 (51.84%) | 27.8495ms |
| C08 | 1.251679 | 0.488690 | 0.546912 | 0.372144 | 0/1763 | 7.8106ms |
| C10 | 0.756679 | 0.814397 | 1.030645 | 0.423914 | 431/1763 (24.45%) | 27.8833ms |

Block1 contains251 scoring observations, blocks2/3 contain504 each, and block4 contains503. Book state was not reset at boundaries. No block-profit criterion was added to the selection rule.

## Interpretation and limits

**C03:** Faster adaptation was weak before costs and worse after them. Relative to C02, annual fees rose from0.7773% to1.7267%, and turnover rose from0.06212 to0.13716 absolute weight per day. Rescaling was nearly continuous. This does not support continuing a fast-half-life parameter search. Its engineering checks passed, but its exact configuration has not passed a numerical causality gate.

**C06:** Forecasts are byte-identical to C05, so that contrast isolates the portfolio change. The factor solver used no fallback on1763 calls, refreshed84 times, had ages0–20 and a maximum dual-gradient diagnostic4.45e−15. The measured net-Sharpe increase over C04 is about0.1087. It is an encouraging development observation relative to these weak alternatives, not evidence that a strong durable edge or the proposed noise mechanism has been established.

**C08:** The intended sizing effect occurred: maximum gross0.4599 and no proportional rescaling. Mean gross was0.2556, turnover0.01032 per day and fees0.1236% annually. Its pooled net Sharpe0.6262 remained close to C02's0.6376. Eliminating rescaling alone did not materially improve this development-sample objective. The lower drawdown and positive descriptive blocks do not override the frozen Sharpe-based validation selection rule.

**C10:** The single admitted expansion changes only the learning and portfolio factor ranks10→50 plus the candidate ID. Its pre-run mechanical review verified all seven imported candidate files and the workflow runner were identical to C06 snapshots. The result did not improve pooled discovery net Sharpe:0.739890 versus C06's0.762944 (difference−0.023054), with essentially similar gross Sharpe0.959189 versus0.963122. Mean gross fell to0.8311, annual fees to0.5144% and net volatility to2.3391%, but these descriptive reductions do not override the primary objective. Because both ranks changed, no result identifies which side was responsible. There is no paired uncertainty estimate for this later contrast and no new rank search is authorized.

C10 recorded zero fallback on1763 calls,84 scheduled refreshes, cache ages0–20 and actual portfolio rank50 on every call. Maximum factor variance fraction was0.484990, below the inherited0.5 bound; covariance diagonal identity error was at most2.17e−19. Maximum dual-gradient diagnostic was4.16e−12, below the unchanged solver's minimum stopping tolerance1e−11. Measured candidate mean rebalance was27.8833ms, official instrumented mean33.6218ms and maximum candidate call641.3870ms. Its35.5017s forecast implies a straight-line century estimate0.1233h, not an actual century execution. Shared-load timings do not establish that rank50 is as fast as rank10 on comparable hardware/load.

Measured forecast times were33.7829s,19.5201s and17.8516s for C03/C06/C08. Their straight-line century extrapolations are0.1173h,0.0678h and0.0620h; no century simulation was performed. Candidate average rebalance timings were below100ms on the assigned single cores, but isolated slow calls occurred (maximum602.6ms,1204.5ms,107.6ms respectively). The employer requirement is an average. These concurrent shared-environment wall times are not guaranteed on other hardware.

## Evidence

- `evidence/discovery_C03_001/`: frozen config/source, official report, full daily/target ledgers and final summary.
- `evidence/discovery_C06_001/`: the same evidence plus factor diagnostics.
- `evidence/discovery_C08_001/`: the same evidence and the zero-rescale sizing trace.
- `evidence/discovery_C10_admission_001/`: plan/config/ledger frozen before execution, exact three-key difference and unchanged source identities.
- `evidence/discovery_C10_001/`: official workflow evidence, rank50 diagnostics and unchanged full-fee accounting.
- `evidence/comparison_wave1_001/`: a separate report restricted to C01–C04. It deliberately contains no C06/C08 update; its paired bootstrap must not be described as uncertainty for these later contrasts.

No validation/audit data was opened by these executions or reviews. All candidate-specific future-alteration, long-history and final-folder claims require their actual separate evidence.
