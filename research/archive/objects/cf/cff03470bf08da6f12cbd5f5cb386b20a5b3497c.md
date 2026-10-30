# Explicit market exposure — results

28 October 2026. Executes `EXPLICIT_BETA_PLAN.md` unchanged. Supplied scorer, full fees,
all rows already exposed.

## Pre-execution diagnostic: passed

Past-only corrected betas predicted realized next-252-day betas better than raw betas
on 97% of 144 dates (mean squared error 0.0393 versus 0.0431). The causal shrinkage
intensity rises from 0.09 at the first completed pair to 0.18 at the end
(`results/beta_correction_diagnostic.json`).

## Candidates

| | Net Sharpe | Rows 253–2014 / 2016–3022 / 3024–3778 | Realized beta | Return / vol per yr | Net investment | Market-removed Sharpe (ex post) |
|---|---|---|---|---|---|---|
| V2 (packaged) | **1.243** | 1.098 / 1.657 / 1.148 | 0.047 | 4.76% / 3.83% | 40% | 1.083 |
| B0: corrected betas, β* = 0 | 1.044 | 1.018 / 1.161 / 1.106 | −0.014 | 3.84% / 3.67% | 24% | 1.101 |
| B05: corrected betas, β* = 0.05 | 1.231 | 1.129 / 1.490 / 1.339 | 0.036 | 4.55% / 3.70% | 29% | 1.099 |

Paired 95% block ranges versus V2 (21 / 63 / 126 days):
B0 −0.198 [−0.34, −0.06] / [−0.34, −0.06] / [−0.35, −0.07];
B05 −0.012 [−0.10, +0.08] / [−0.11, +0.08] / [−0.12, +0.07].
Costs 0.16–0.17% a year; rebalance 4.3–4.7 ms; 3,527/3,527 certificates ok for both.
The beta-corrected forecast passed the altered-future check at cuts 400, 600, 1500,
3024 and 3700, including Fortran-layout and truncated inputs
(`results/explicit_beta_causality.txt`).

## Frozen rules applied

- **Measurement check:** B0 realized beta −0.014 (target 0) and B05 0.036 (target
  0.05). Both are within ±0.02, so exposure is now under control: B0's per-period betas
  are −0.008 / −0.018 / −0.016 and B05's are 0.042 / 0.032 / 0.034. The correction
  slightly overshoots: both land about 0.014 below target.
- **B0 is not retained as the neutral core:** 1.044 is below the 1.083 bar.
- **B05 does not replace V2:** 1.231 is below 1.243. The difference is −0.012, with a
  range symmetric around zero; it is a statistical tie.
- **V2 stays the candidate**, now with its market exposure explained and measured.

## What this establishes

1. **V2's hidden beta is real and controllable.** Correcting betas with past-only
   shrinkage moves realized beta from +0.047 to −0.014 at β* = 0, and to 0.036 with an
   explicit target of 0.05.
2. **The pure stock-selection edge is about 1.10 Sharpe.** All three books have nearly
   the same market-removed Sharpe (1.08–1.10). The rest of V2's 1.24 comes from about
   0.04–0.05 of market beta earning this sample's market premium.
3. **Explicit beyond hidden is a near tie in Sharpe.** B05 has steadier periods (lowest
   period 1.13 versus 1.10 for V2; validation and audit closer together), but it did not
   clear the frozen bar.

## Judgment left to the applicant

The rule keeps V2. A defensible argument for B05 exists: the same Sharpe within noise,
exposure chosen and measured rather than produced by estimation error, and steadier
periods. Adopting it would override a frozen rule after seeing the result, so if chosen
it must be stated as such in the note. Either way, the note should say: about 0.04–0.05
of the book's return stream is market exposure; if the continuation's market premium is
lower, that part shrinks or turns negative, and the stock-selection core is about 1.1
Sharpe in this sample.
