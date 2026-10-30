# Allocator failure paths and final-book certificate — plan (written before the fix)

28 October 2026. From `reviews/V2_FOLLOWUP_ENGINEERING_20261028.md` §4–6 and
`research/v2/REVIEWER_NEXT_DECISION_20261028.md` §1. Default V2 behaviour must not change.

## Decided behaviour

A strategy scored over decades must not crash on a rare numerical failure, and must never
trade an uncertified vector. Allocator sequence:

1. Pass 1: warm-started joint solve (`max_iter`), beta polish, certificate.
2. Pass 2: resume from the polished point (`max_iter`), certificate. *(existing)*
3. Pass 3: cold start (multipliers zero), `2*max_iter` iterations, certificate.
4. Fallback: the matched-diagonal problem: same caps, same beta target, specific variance
   `d + rowsum((B L)^2)`, no factor block. Exact scalar-dual bisection, certified
   (hedge, caps, finiteness, gap). Status `fallback_diagonal`.
5. If even that fails: raise `RuntimeError`. Never return an uncertified vector.

`info["status"]` ∈ {`ok`, `ok_after_recovery`, `ok_after_cold_restart`, `fallback_diagonal`}.

Final book (engine): if gross exceeds the cap, a zero target is scaled (exact), and a
nonzero target is re-solved with risk aversion multiplied by gross/cap, up to 8 times,
each solve certified. Then a final post-processing check: finite, |w| ≤ cap,
gross ≤ gross_cap·(1+1e-12), |b'w − target| ≤ hedge tolerance. If it fails: `RuntimeError`.

Edge cases (allocator domain):
- (a) Every movable beta is zero, target 0: valid, no hedge needed, no error.
- (b) Every cap is zero, nonzero target: `ValueError` (infeasible).
- (c) Every cap is zero, target 0: returns zeros with status `ok` in `info`.
- (d) Target at or beyond the maximum attainable exposure: `ValueError` ("strictly inside
  the attainable range"), a documented domain.

## Checks (`verification/v2_failure_paths.py`, nonzero exit on any failure)

1. `max_iter=0` on a problem with factor risk: status `fallback_diagonal`, caps exact,
   beta target exact, finite; no exception.
2. The engine never stores an uncertified status across a full synthetic scorer run.
3. A nonzero target with a gross cap forced to bind (synthetic, cap 0.3): every final book
   has gross ≤ cap and |b'w − target| within tolerance; no proportional scaling of a
   nonzero target.
4. Edge cases (a)–(d) as specified.
5. Unchanged default: real-data V2 ledger identical to the pre-change package (re-run of
   `v2_package_checks.py` with `--old-ledger`), both allocator suites pass.

Red: run checks 1–4 on the current code (expected failures: 1 returns `not_certified`
or similar, 3 scales a nonzero target, 4a raises, 4c gives no status).
