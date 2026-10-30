# Adaptive premium memory — plan and frozen decision rule (written before execution)

28 October 2026. Motivation: the hindsight constant-premium ceiling of the 27 factor
returns is 1.46 gross (bias-corrected, `results/ceiling.json`), and V2 earns 1.29 gross, so
re-weighting constant premia has little room. Period ceilings are higher (first half 1.18,
second half 2.02; discovery / validation / audit 1.20 / 1.48 / 2.48, noisy), which suggests
the premia move. V2 tracks them with a fixed 1,008-day memory chosen by Sharpe comparisons.
The block-shuffle drift test could not resolve drift (p = 0.21), so the model must be able to
fall back to stable premia if the data say so.

## Model: stable premium plus a learned, shrunk deviation

Two causal exponentially weighted ridge learners on V2's 27-column design (identical
features, ridge 0.1, labels, maturity rules):
- θ∞(t): no forgetting (expanding), the stable premium;
- θ252(t): one-year half-life, the dynamic estimate.

Forecast coefficient: θ(t) = θ∞(t) + κ_t·(θ252(t) − θ∞(t)), κ_t ∈ [0, 1].

κ_t is the least-squares weight that would have best predicted matured labels, using only
pairs whose label day is ≤ t − 1: for each matured pair (design D_s from X[s], label e_{s+1}),
with both learners' coefficients as they stood when that pair was predicted,
a = D_s θ∞, δ = D_s (θ252 − θ∞): κ = Σ ⟨e − a, δ⟩ / Σ ⟨δ, δ⟩, sums from the start
(expanding), clipped to [0, 1]. κ = 0 before 252 matured predictions exist. κ → 0 recovers
stable premia; κ → 1 is the one-year learner. One parameter, learned online; 252 is fixed a
priori (the same window as the betas and risk), not tuned.

Everything else is packaged V2 (risk, φ 0.3, γ 200, caps, costs, raw-beta hedge).

## Gates (in order)

1. **Forecast gate (primary, causal):** mean one-step squared prediction error of matured
   labels, Σ_i (e_{s+1,i} − ŷ_i)² / N averaged over prediction rows 378..3778, adaptive
   learner versus V2's 1,008-day learner. Pass iff the adaptive mean loss is lower. Report
   21/63/126-day block ranges of the daily loss difference and every stage.
2. **Policy run (only if gate 1 passes):** one full-fee run. **Retain** iff full-run net
   Sharpe > 1.243 (packaged V2) and realized beta < 0.2 and runtime within budget. Report
   stages, paired ranges, κ path, costs, beta, net investment, certificates.
3. **Causality:** altered-future and truncation checks on the new forecast (rows ≤ cut
   bitwise identical) before any result is reported as valid.

A failure rejects this version. No retuning of 252, the ridge, or κ's clipping after results.
