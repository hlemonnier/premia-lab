# Score research, wave 2: conditional premia, execution costs and a measured market sleeve

29 October 2026, Europe/Paris. Root-owned prospective specification.

## Objective, authority and fixed baseline

The user requests continued research to improve the official score. Optimize
future net Sharpe under the original brief's causal-information, solvency,
market-beta and runtime requirements. There is no additional pure-alpha,
mean-square forecast error, turnover or statistical-significance admission gate.
All supplied historical periods have been exposed and are development data.
The old split names are diagnostics, not newly untouched confirmation samples.

The completed first wave is committed at
`37b323e00f2e79d0a5d799a3fdab6946ad04c2e8`. Its leader is F2 + VTvol, original
scorer net Sharpe 1.318334966090838. V2 remains 1.242503073307361 and F2 alone
1.291780064333837. This wave does not reopen that wave's parameter search.

Economic comparisons retain its pinned ce3 research engine
(`ce3fe4e76271709422165d6f24e2fbecd9d0fe07`), F2 prototype and
VTvol reference so new effects can be isolated. Current Claude production head
is `c51d31fe63c68255f2220935a8bc615c62bd1d0c`, whose allocator safeguards must
be preserved at eventual integration. No production file is edited here, and
the research score cannot be inherited by an unexecuted integration.

## Known evidence before new policy scores

The first wave's inverse-variance policy beat inverse-volatility before fees,
but lost after fees. F2 + VTvol pays annual fees 0.336406%, against 0.207145%
for F2 alone. This motivates pricing actual trades when changing exposure.

Earlier all-hinge additive expansion C12 and all-interaction expansion C11
failed under earlier portfolio controls. That lowers the priority of another
generic basis expansion; it does not establish failure under every allocator.
Conditional characteristic premia are a distinct hypothesis: change relative
factor forecasts with one published market-volatility state, with strong shrinkage.

The research leader's realized net beta is 0.05272035. The brief defines the
market as the equal-weight return of the supplied stocks, and allows stock
replication of a modest market sleeve subject to whole-period beta below 0.2.
There is no separately supplied free index asset. The proposed +0.05 sleeve was
specified before a scoped marginal-Sharpe diagnostic. That diagnostic evaluates
only the derivative at zero, omits incremental trading costs, and does not score
or optimize a saved-return mixture. Its outcome and fixed choice are retained
in the independent review packet. This is intentional market exposure, not a
claim that its return is stock-selection alpha.

## Exactly four standalone alternatives

Every alternative is scored against the reproduced F2 + VTvol leader, with the
same original scorer and all its costs. The F2 virtual portfolio, raw-beta
labels, 27 original forecast variables and 26-column risk model are unchanged
except where the specific transformation below says otherwise.

### E1: cost-aware scalar exposure projection

Maintain the exact F2 virtual book and existing VTvol clock. Let v be its new
target, a_star its desired multiplier, h the actual drifted portfolio supplied
by the scorer, and q63 the past virtual gross-return second moment. After the
existing 63-earned-observation warm-up choose a to minimize

    0.5 * 200 * max(q63, 1e-12) * (a-a_star)^2
      + sum_i costs_i * abs(a*v_i-h_i) / 20

over [0.5, min(2, 5/sum(abs(v)))]. For zero v the target is zero and the choice
of multiplier is immaterial. The certified virtual gross is at most 5, so the
nonzero-v upper bound is at least 1 and the interval is feasible. Before 63
earned observations retain a=1; the first opening trade remains free.

Use the inherited risk-aversion 200 and cost horizon 20; there is no additional
penalty-strength search. This is a chosen convex tracking objective, not a claim
of calibrated expected utility. It prices actual stock trades and their netting
with underlying strategy rotations, not just abs(a-a_previous). Record its
global scalar optimality certificate. A same-held-book cost inequality is not
asserted to imply lower fees over the entire different future path.

### E2: solve the actual portfolio at the desired risk scale

Compute a from the exact unchanged F2 virtual portfolio and VTvol clock. A second
independent allocator uses the same forecast and published risk inputs, but
optimizes around the actual h, with risk_aversion=200/a, stock cap=0.05*a,
cost_horizon=20, gross cap=5 and raw-beta target zero. Maintain independent risk
and optimizer state for the reference and actual engines. Configure/reset once
per forecast session; daily allocation-coefficient changes must not reset the
risk history or share warm starts across books.

The gamma/a rule follows the frictionless substitution w=a*v in the quadratic
objective. Exact zero-cost scaling equivalence is required only on synthetic
paths where the reference gross cap does not bind. A fixed actual gross-5 cap
is not a homothetic image of the virtual gross cap when a differs from one.
Extreme-cap feasibility is therefore checked separately. Real actual holdings
differ from a times virtual holdings; handling that difference and its costs
inside the full optimizer is this policy's economic change.

### F3: strongly shrunk volatility-conditioned characteristic premia

At each published close s, m_s is the equal-weight stock return. Update normalized
EW second moments q63_s and q1008_s of m_s squared, from row zero through s:

    S_h <- 2^(-1/h)*S_h + m_s^2; M_h <- 2^(-1/h)*M_h + 1; q_h=S_h/M_h.

Before 63 observed market returns set c_s=0. Thereafter use

    c_s = clip(log(max(q1008_s,1e-12)/max(q63_s,1e-12))/(2*log(2)), -1, 1).

Thus the fixed state scale spans recent volatility from twice to half its long
reference. There is no full-sample centering, standardization, learned threshold
or fitted state window. The market state is independent of the strategy book.

Append c_s times each of the original 26 characteristic columns to the original
27-column design; do not interact the beta feature. Both complete pooled fits
have 53 columns, half-lives 1008 and 252, ridge 0.1 on the original 27 and 1.0 on
the 26 interactions. Combine only the first 13 original linear coefficients
50/50, exactly as F2; retain the slow fit for the other 40 coefficients. The
126-matured-pair warm-up is unchanged. The bounded state gives interactions no
larger amplitude than their parent columns and a tenfold larger ridge penalty.

Forecast row t uses X[t-1], beta[t] and c_(t-1). Its newest training observation
uses X[t-2], beta[t-1], c_(t-2) against the residual return at t-1. The state must
not include that label return. Risk basis and base allocator are unchanged;
VTvol now observes its own F3 virtual-book gross returns. No state, ridge,
feature-subset or half-life grid is authorized in this wave.

### M1: a fixed, costed +0.05 equal-weight market sleeve

Run the unchanged F2 + VTvol policy as an independent inner portfolio, with its
own drifted holdings, allocation state and multiplier clock. After its target
p is available, the outer target is p + 0.05/N in every stock, followed only by
proportional reduction if aggregate gross exceeds 5. The sleeve begins with the
free opening and is kept at equal stock weights at each subsequent decision.
The pre-cap absolute stock bound is 0.10 + 0.05/N, not the inner 0.10 bound.

The original scorer charges actual combined trades, including netting; there is
no free index return or additive virtual-fee shortcut. The actual combined
portfolio's drift denominator must never replace the inner portfolio's own
denominator. No beta shrinkage, market-premium predictor or sleeve-weight grid
is added. Report market exposure explicitly and reject if actual beta fails.

## Exactly one conditional composition

After all four outcomes are recorded, select the highest-scoring admitted
execution alternative E1/E2, if either improves on 1.318334966090838 by more than
1e-8. F3 and M1 qualify separately only if each beats that baseline and passes
its operational checks. Numerical ties choose E1.

If at least two distinct families qualify, run exactly one composition of all
qualifying families. Construction order is F3 (if qualified), the selected
execution rule (if qualified), then the outer M1 sleeve (if qualified). An
unqualified family retains its baseline behavior. E1 and E2 are never combined.
When F3 qualifies, the execution reference portfolio and its VT moments follow
the F3 forecast, rather than retaining a separate F2 reference return path.
The outer market sleeve must preserve the inner execution portfolio's independent
holdings; its positions cannot be fed into the inner optimizer as its own book.

This is an explicitly counted adaptive experiment, not independent confirmation.
There is no subset search if it disappoints. Promote it only if it beats the best
admitted standalone by more than 1e-8; otherwise retain that standalone or the
existing leader. At most five new economic policies are scored in this wave.

## Verification, economics and decision rule

Write prospective E2E harnesses before policy implementation, retain the expected
missing-policy failures, and obtain independent source review before actual
market scoring. Synthetic paths cover known costs, drift, reversals, opening,
endpoint, future alterations, prefixes, cross-history restarts, zero-risk cases,
state independence and relevant cap/solver branches. Distinguish canonical-layout
causal invariance from earlier mixed-layout numerical failures. Record a priori
tolerances and report failed or blocked checks without relabeling them.

Reproduce the baseline daily economics within 1e-8 and inspect actual differences.
Use zero-based earning rows 253..3778, 3526 economic observations, 3527 decisions,
and the scorer's final charged rebalance without forced liquidation. Primary
score is sqrt(252)*mean(net)/std(net,ddof=0). All fees use actual traded holdings.

Admission requires finite, solvent paths; absolute whole-sample net beta<0.2;
causal protected forecasts/decisions; certified solves and declared constraints;
mean rebalance time<100ms on one core; forecast runtime feasibility under the
brief. Retain exact scores, beta, gross/net returns, fees, exposure, source/data
identities, commands and all outcomes. A full long-history runtime stress check
of the selected prototype may be run under its prospectively written harness;
repeated synthetic/history data are not evidence of future alpha.

Use the original stage masks only as diagnostics. Paired moving-block intervals
use lengths 21/63/126, 2000 draws and seed 20261027, including the last legal
block start. These fixed-policy intervals do not correct the entire research
search and are not a new significance admission hurdle. Independently reconstruct
the selected candidate's stock-level accounting before recommending integration.

## Ownership and literature

Execution owner: evidence/v2_score2_execution_20261029. Forecast owner:
evidence/v2_score2_forecast_20261029. Independent challenge and M1 owner:
evidence/v2_score2_review_20261029. Root owns this plan, integration, publication
and conditional composition; another agent cross-reviews each owner's source.

Primary motivation: Garleanu-Pedersen, Dynamic Trading with Predictable Returns
and Transaction Costs (NBER w15205/JF 2013); Boyd et al., Multi-Period Trading
via Convex Optimization (arXiv:1705.00109); DeMiguel-Martin-Utrera-Uppal,
A Multifactor Perspective on Volatility-Managed Portfolios (JF 2024,
doi:10.1111/jofi.13395). Their results motivate hypotheses, not expected gains
or an optimality theorem for this simulated market. Source URLs and limitations
belong in the owned research reports. No calendar or outgoing submission is made.
