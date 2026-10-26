# C08: higher risk-aversion control, fixed before execution

## Observed problem and question

The completed C02 discovery run used the proportional gross rescale on 79.75% of its calls, with mean pre-scale gross 1.2123 and maximum 2.2536. The first design had hoped this would be exceptional. The rescale generally changes the box/turnover optimizer's solution and can move holdings that its no-trade decision would otherwise retain. These observations motivate a controlled implementation-sizing comparison; they do not establish that scaling caused the weak Sharpe.

## Exact candidate and scope

C08 uses C02's existing additive strategy with **risk_aversion = 5000**, rather than 1000. Only that number and the candidate identifier change. Basis, EW half-life252, normalized ridge0.1, warmup126, risk estimates, 20-day cost horizon, 1% stock bound, gross cap1, full actual trading costs and every other rule remain unchanged. The value5000 is a single engineering choice motivated by the observed pre-scale exposures, not the winner of a gamma grid. Changes in drift and holdings mean gross cannot be assumed to scale exactly by one fifth; observe the actual trace.

Use only the existing discovery cache `[0,2016)`, with the official scored rows `[253,2015)` and continuous empty-book initialization. Invoke the unchanged official scorer via the existing E2E runner. Save frozen sources/configuration, input identities, exact rerun command, full daily/target ledgers, expected/actual checks and timing. C08 consumes one additional selectable pipeline slot and must be entered in the lead's ledger before any score is inspected.

## Interpretation fixed before results

Compare net/gross Sharpe, full fees, turnover, scaling frequency and magnitude, mean/gross/net exposures, realized beta, all four fixed blocks and runtime with C02. First establish whether scaling actually becomes exceptional. If it does and performance improves, that supports investigating the construction distortion without establishing a new alpha discovery. If performance remains weak, lower exposure alone has not solved the research problem. No profitability floor, block-profit requirement or predeclared winner is imposed. A negative result remains visible. Further sizing choices require another declared slot; no automatic gamma search follows.

C02's numerical causality result does not constitute a C08 configuration-specific pass. Exact finalist verification is still required if this candidate is retained. Validation/audit stays closed. The wave1 uncertainty report remains restricted to C01–C04 and is not revised to include this later result.
