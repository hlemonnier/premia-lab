# V3 market-sleeve review: retain the selected policy, correct the scenario language

29 October 2026, Europe/Paris. Independent reviewer: v3_market_challenge.
Claude head: `978824d4b6140c43566ebd61a3ee8157f4080e35`.
Research evidence head: `9e56aa755d20c5876485188f4c50ce959f6d63f3`.

## Decision within this review's scope

**Retain the fixed +0.05 sleeve as the selected score-first candidate.** Claude
is right that most of the latest score increment is deliberate market exposure,
and right that a lower market premium can reverse its advantage. Those facts
should be stated plainly. They do not establish that the supplied rules require
zero beta or that the no-sleeve policy is now the better future policy.

The material correction is to the interpretation of the sensitivity calculation.
The reported 1.286 figure is reproducible as a narrow change to the sleeve's mean
contribution. It is not the result of rerunning the strategy in a market with
zero expected return. A consistent common-market-mean comparison changes both
books, because the no-sleeve book already has approximately 0.053 realized beta.

This review introduces no policy, tuning, selection threshold, modified-market
replay or statistical-significance veto. It does not approve the independent
integration/reference/causality questions owned by the other reviewers.

## Finding 1 — qualify the zero-premium claim and report both books

**Severity: medium, interpretation/documentation; no score invalidation.**

Locations in the pinned Claude snapshot: `verification/V3_INTEGRATION_RESULTS.md:25`,
`:67`, `:73` and `handoff_v3/strategy.py:20`. The user-facing sentence
"if the market had earned nothing" is broader than the report's more careful
"sleeve earns no premium" label.

The number 1.286 is obtained by holding the final book's observed volatility and
fees fixed and subtracting 0.05 times the historical market mean from its mean:

    (mu_joint - 0.05*mu_market) / sigma_joint = 1.2864659455.

The no-sleeve book is then left at its original 1.3395817822. This is a useful
conditional diagnostic: what if the **added sleeve alone** contributed no mean
return while the rest of the book kept its historical distribution? It is not
a scenario in which the same market's mean changes for both strategies.

A consistent descriptive common-market shift uses each book's observed OLS beta:

    S_j(nu) = [mu_j + beta_j*(nu - mu_market)] / sigma_j.

Here all means and volatilities are annual arithmetic quantities. Keep each
book's beta, centered return fluctuations, nonmarket mean, positions and costs
fixed. Only the common market mean changes to nu. Under that explicitly limited
assumption, the comparison is:

| Assumed common annual market mean | E2 + sleeve | E2 without sleeve | Joint minus E2 |
|---|---:|---:|---:|
| Observed 14.4799% | 1.444733 | 1.339582 | +0.105152 |
| Zero | 1.118774 | 1.165241 | -0.046467 |
| Reversed to -14.4799% | 0.792814 | 0.990900 | -0.198086 |

The lower-premium risk survives the corrected comparison. The correction does
not rescue the sleeve under zero mean; it makes the comparison internally
consistent and prevents a descriptive mean adjustment being mistaken for an
executed counterfactual.

The two fixed-moment expressions cross at a common annual market mean of
**4.43772035%**. Thus, under these frozen quantities, the sleeve's advantage
does not require the full historical 14.48% market mean to persist. This crossing
is conditional on estimated betas, volatility, covariance and nonmarket means.
It has no confidence interval here and is not a forecast, an optimal weight or
a threshold to add to production. No live timing rule is proposed.

In a real change to the return-generating process, forecasts, residual labels,
risk estimates, actual positions, drift and costs can also change. Neither this
formula nor Claude's formula predicts the resulting strategy path. A claim
about that path would require a separately specified scenario and a full rerun.

## Finding 2 — preserve the sensitivity calculation as evidence

**Severity: low, reproducibility/documentation.**

`verification/V3_INTEGRATION_RESULTS.md:8` says every number comes from a committed
log. The newly committed `verification/v3_sleeve_comparison.py:20` executes only
the two sleeve settings and `:27` records their original-history moments. It
contains no mean-shift sensitivity calculation. The new comparison JSON/log
contains the two actual policy results, not the 1.286/1.128/1.119 table.

The arithmetic is reproducible and therefore not evidence of a false score.
Still, retain a formula and source-bound calculation output, or qualify that
the table is an analytical sensitivity derived from the committed results.
This review supplies both calculations under scopes written before execution:

- [PLAN.md](../evidence/v3_market_challenge_20261029/PLAN.md)
- [mean_sensitivity_readback.py](../evidence/v3_market_challenge_20261029/mean_sensitivity_readback.py)
- [mean_sensitivity_001.json](../evidence/v3_market_challenge_20261029/mean_sensitivity_001.json)

The narrow calculation reproduces Claude's rounded figures: zero sleeve mean
1.2864659455 and reversed sleeve mean 1.1281985905. The common-zero calculation
for the final book reproduces its reported 1.119. The missing comparison was
the no-sleeve book treated under that same common-market assumption.

## The original brief does not specify a second zero-beta threshold

The immutable supplied `README.md:29` states that future net Sharpe is the
objective. `README.md:33` specifies a whole-future-period net-return regression
beta below 0.2. `README.md:36` adds the market-hedging language and says a
mostly market-long strategy is unwanted. `README.md:39` says there are no other
portfolio constraints. Read these together.

My interpretation is that the numerical condition operationalizes the market
exposure restriction. The brief does not state a second beta-equals-zero rule
or explicitly prohibit a small chosen stock-replicated market allocation.
Consequently, calling the sleeve a demonstrated rule violation is unsupported.
The qualitative wording still deserves an honest explanation in the note; the
numeric limit is not a reason to allocate arbitrarily close to the limit.

The candidate's observed net beta of 0.102978 passes the historical numerical
condition. It does not establish the beta of the evaluator's unseen future.
The no-sleeve policy also carries observed beta 0.052981; switching it off does
not produce a truly market-neutral return stream. Replacing raw-beta hedging
with the previously rejected corrected-beta policies would be a different
experiment and is outside this integration.

The brief also says code and research/portfolio reasoning are reviewed
separately (`README.md:149`). The user has explicitly prioritized the numerical
score, while the accompanying note should describe the market contribution
and the actual human/AI work accurately. Nothing in this audit changes that
priority or invents applicant contributions.

## Most of an increment is different from most of the whole portfolio

An OLS projection of the observed net return on the equal-weight market gives:

| Descriptive quantity | E2 without sleeve | E2 + sleeve |
|---|---:|---:|
| Market regression beta | 0.052981 | 0.102978 |
| Market regression R-squared | 2.9068% | 10.1613% |
| Annual net mean | 5.8946% | 6.6090% |
| Beta times annual market mean | 0.7672% | 1.4911% |
| That term as a share of annual net mean | 13.0146% | 22.5619% |

These describe the entire current return stream. They support describing the
market component as meaningful without describing the whole strategy as mostly
the market factor. They do not identify the remaining mean as economic alpha,
and they do not show the net performance of a tradable market-neutral hedge.
They are full-sample descriptive projections, with no guarantee about future
factor dependence.

R-squared and beta-times-market mean were specified before the first readback.
The additional mean-share ratio has a separate prospective
[scope](../evidence/v3_market_challenge_20261029/TOTAL_DEPENDENCE_SCOPE.md) and
[output](../evidence/v3_market_challenge_20261029/total_dependence_001.json).

## Recommendation to the parent reviewer

Keep +0.05 as the selected policy under the existing score-first decision and
continue the independent integration audit. A frozen rule is not a reason to
ignore new evidence; here, however, a hypothetical zero market mean is an
assumption rather than new evidence that the future market mean is zero.
The sensitivity makes a risk assumption visible and quantifies it. It does not
by itself justify reversing the observed policy selection.

Require a wording correction, not an automatic change to `POLICY.sleeve`:

> The package carries a deliberate +0.05 equal-weight stock sleeve, bringing
> observed total net beta to 0.103. It improves the supplied-history net score
> from 1.340 to 1.445. Frozen-return mean sensitivities favor the no-sleeve book
> if the common market premium is sufficiently low; they are not executions
> in an altered market. Future market premium and beta remain uncertain.

Preserve the no-sleeve result as a comparator. Do not claim that the selected
gain is newly discovered stock-selection alpha, future superiority, or proof
of no overfitting. No sleeve-weight grid, forecast change or extra optimization
is needed to correct the documentation.

## Provenance and exact workflow

The readback uses the published E2 and joint daily CSVs from research commit
`9e56aa7`, with 3,526 earning rows at zero-based indices 253..3778. Original
returns.csv SHA256 is
`6ebf41a2f7ff09edb704e0a867c91d6d60c9eb135bd2c1f3a3f6917bf55bbe2d`.
Each source copy is checked against its original Git blob SHA and SHA256.
The resulting original-market mean check differs by at most 1.04e-16; the saved
net-return identities are exact. Joint-minus-E2 gross return equals 0.05 times
the market return within 6.18e-18.

The reproduced Sharpe values differ from Claude's deployed summary by at most
3.08e-13. This observation supports using the published series for these
descriptive quantities; it is not a substitute for the separate target-stream
integration audit.

First exact-byte verification caught CRLF line endings normalized by the patch
transfer and a JSON final newline added during transfer. Exact original bytes
were restored only when their Git blob hashes matched; no numerical calculation
was run on unverified copies. The failure and correction are recorded in
[source_copy_verification.json](../evidence/v3_market_challenge_20261029/source_copy_verification.json).

Executed readback command, exit 0, empty stderr:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 taskset -c 2 \
python evidence/v3_market_challenge_20261029/mean_sensitivity_readback.py \
  --data '/workspace/scratch/a83c191d516f/v2-original-input/extracted/Quant Research Take-Home' \
  --out evidence/v3_market_challenge_20261029/mean_sensitivity_001.json \
  > evidence/v3_market_challenge_20261029/mean_sensitivity_001.stdout.log \
  2> evidence/v3_market_challenge_20261029/mean_sensitivity_001.stderr.log
```

The supplemental command is
`python evidence/v3_market_challenge_20261029/total_dependence_readback.py`, with
stdout/stderr preserved under the matching `total_dependence_001` names; exit 0.
Neither script imports, executes, alters or retunes a strategy. Original results
are never overwritten. For a rerun, supply the same original inputs and a new
output path; the supplemental script deliberately refuses to overwrite its
preserved first output.

Output identities: mean sensitivity SHA256
`a40de33bfc14f8c84b5148617973af0332d34d2a62cae9649ec5a6740bb9c8bf`;
total dependence SHA256
`a3eb839a2f48355a3efeac5ad5a0d7f9ea49aa302adb96fa5df05aa1cb90c1ef`.
