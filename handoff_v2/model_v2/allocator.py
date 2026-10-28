"""Exact cost-aware allocator with diagonal + low-rank factor risk.

Solves, for the drifted book h,

    maximize   mu'w - gamma/2 (w' diag(d) w + ||L'B'w||^2) - kappa'|w - h|
    subject to b'w = beta_target (default 0),  |w_i| <= cap_i,

where F = L L' is the factor covariance. The equalities z = L'B'w and b'w = target
are dualized; given the multipliers each stock solves the scalar no-trade-band /
clip problem of the original C09 allocator. The convex dual is minimized by
damped Newton with Armijo backtracking, then the beta multiplier is polished by
bisection so the hedge holds to floating-point tolerance. A final certificate
checks finiteness, caps, the hedge and the duality gap
gamma/2 ||M'w - lam/gamma||^2 - nu * (bn'w - c), with c the normalized target. If it
fails: resume from the polished point, then a cold start, then a certified
matched-diagonal fallback (status `fallback_diagonal`); an uncertified vector is never
returned. `info` (a dict) receives the certificate and status.
Specification and pre-implementation tests: research/v2/ALLOCATOR_SPEC.md and
research/v2/test_allocator.py.
"""
import numpy as np


def _vec(x, name, n=None):
    try:
        v = np.asarray(x, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if v.ndim != 1 or v.size == 0 or (n is not None and v.size != n):
        raise ValueError(f"{name} must be a nonempty vector of length {n}")
    if not np.isfinite(v).all():
        raise ValueError(f"{name} must be finite")
    return v


def allocate_factor(mu, held, d, B, L, beta, kappa, gamma, cap, warm=None,
                    max_iter=100, tol=1e-13, info=None, beta_target=0.0, _fallback=False):
    mu = _vec(mu, "mu"); n = mu.size
    h = _vec(held, "held", n); d = _vec(d, "d", n); b = _vec(beta, "beta", n)
    kappa = _vec(kappa, "kappa", n)
    B = np.asarray(B, dtype=np.float64); L = np.asarray(L, dtype=np.float64)
    if B.ndim != 2 or B.shape[0] != n or L.ndim != 2 or L.shape[0] != B.shape[1]:
        raise ValueError("B must be (n, k) and L must be (k, r)")
    if not (np.isfinite(B).all() and np.isfinite(L).all()):
        raise ValueError("B and L must be finite")
    gamma = float(gamma)
    if not np.isfinite(gamma) or gamma <= 0:
        raise ValueError("gamma must be positive and finite")
    if np.any(d <= 0):
        raise ValueError("specific variances must be strictly positive")
    if np.any(kappa < 0):
        raise ValueError("costs must be nonnegative")
    cap = np.broadcast_to(np.asarray(cap, dtype=np.float64), (n,)).copy()
    if not np.isfinite(cap).all() or np.any(cap < 0):
        raise ValueError("caps must be finite and nonnegative")

    diag = gamma * d
    M = B @ L
    r = M.shape[1]
    movable = cap > 0
    if not np.isfinite(float(beta_target)):
        raise ValueError("beta_target must be finite")
    if not movable.any():
        if float(beta_target) != 0.0:
            raise ValueError("a nonzero beta_target is infeasible when every cap is zero")
        if info is not None:
            info.update(status="ok", gap=0.0, factor_residual=0.0, hedge_residual=0.0, primal=0.0)
        return np.zeros(n)
    bscale = float(np.max(np.abs(b[movable])))
    use_beta = bscale > 0
    bn = b / bscale if use_beta else np.zeros(n)
    A = np.hstack([M, bn[:, None]]) if use_beta else M
    A[~movable] = 0.0
    m = A.shape[1]
    reg = np.zeros(m); reg[:r] = 1.0 / gamma
    expo_tol = max(64 * np.finfo(float).eps * float(np.abs(bn) @ cap), np.nextafter(0, 1))
    beta_target = float(beta_target)
    if not use_beta and beta_target != 0.0:
        raise ValueError("a nonzero beta_target needs a nonzero movable beta")
    c = beta_target / bscale if use_beta else 0.0          # target in normalized-beta units
    if use_beta and abs(c) >= float(np.abs(bn) @ cap):
        raise ValueError("beta_target must lie strictly inside the attainable range (|target| < sum |b_i| cap_i)")

    def primal(theta):
        s = mu - A @ theta
        gain = s - diag * h
        w = h.copy()
        up = gain > kappa; dn = gain < -kappa
        w[up] = (s[up] - kappa[up]) / diag[up]
        w[dn] = (s[dn] + kappa[dn]) / diag[dn]
        wc = np.clip(w, -cap, cap)
        inner = (up | dn) & (wc == w) & movable
        return wc, s, inner

    def dual(theta, w, s):
        phi = s @ w - 0.5 * (diag * w) @ w - kappa @ np.abs(w - h)
        lam = theta[:r]
        return phi + lam @ lam / (2 * gamma) + (theta[r] * c if use_beta else 0.0)

    def grad(theta, w):
        g = -(A.T @ w)
        g[:r] += theta[:r] / gamma
        if use_beta:
            g[r] += c
        return g

    theta = np.zeros(m)
    if warm is not None and isinstance(warm.get("theta"), np.ndarray) and warm["theta"].shape == (m,):
        theta = warm["theta"].copy()

    def solve_pass(theta, iters):
        w, s, inner = primal(theta)
        val = dual(theta, w, s)
        for _ in range(iters):
            g = grad(theta, w)
            if np.max(np.abs(g[:r]), initial=0.0) <= tol * (1 + np.max(np.abs(theta[:r]), initial=0.0) / gamma) \
                    and (not use_beta or abs(g[r]) <= expo_tol):
                break
            Ai = A[inner]
            H = Ai.T @ (Ai / diag[inner, None]) + np.diag(reg)
            H[np.diag_indices(m)] += 1e-12 * max(np.trace(H), 1e-300)
            try:
                step = -np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                step = -g
            slope = g @ step
            if slope >= 0:
                step = -g; slope = -(g @ g)
            t = 1.0
            for _ in range(60):
                cand = theta + t * step
                wc, sc, ic = primal(cand)
                vc = dual(cand, wc, sc)
                if vc <= val + 1e-4 * t * slope:
                    break
                t *= 0.5
            else:
                break
            theta, w, s, inner, val = cand, wc, sc, ic, vc

        if use_beta:
            def expo(nu):
                th = theta.copy(); th[r] = nu
                wv = primal(th)[0]
                return float(bn @ wv) - c, wv, th
            e0, w0, th0 = expo(theta[r])
            if abs(e0) > expo_tol:
                step = max(np.max(np.abs(mu[movable])), np.max(diag[movable] * cap[movable]),
                           np.max(kappa[movable]), 1e-300)
                lo = hi = theta[r]
                if e0 > 0:
                    while True:
                        hi += step; e, _, _ = expo(hi)
                        if e <= 0:
                            break
                        step *= 2
                        if step > 1e300:
                            raise RuntimeError("cannot bracket beta hedge")
                else:
                    while True:
                        lo -= step; e, _, _ = expo(lo)
                        if e >= 0:
                            break
                        step *= 2
                        if step > 1e300:
                            raise RuntimeError("cannot bracket beta hedge")
                best = (abs(e0), w0, th0)
                for _ in range(200):
                    mid = 0.5 * (lo + hi)
                    if mid in (lo, hi):
                        break
                    e, wv, th = expo(mid)
                    if abs(e) < best[0]:
                        best = (abs(e), wv, th)
                    if abs(e) <= expo_tol:
                        break
                    if e > 0:
                        lo = mid
                    else:
                        hi = mid
                if best[0] > expo_tol:
                    raise RuntimeError("beta hedge did not converge")
                _, w, theta = best
        return w, theta

    def certify(w, theta):
        q = M.T @ w - theta[:r] / gamma
        e = float(bn @ w) - c if use_beta else 0.0
        nu = float(theta[r]) if use_beta else 0.0
        gap = 0.5 * gamma * float(q @ q) - nu * e
        primal_value = float(mu @ w - 0.5 * (diag * w) @ w - 0.5 * gamma * float((M.T @ w) @ (M.T @ w))
                             - kappa @ np.abs(w - h))
        ok = (np.isfinite(w).all() and bool(np.all(np.abs(w) <= cap)) and abs(e) <= expo_tol
              and abs(gap) <= 1e-12 * max(abs(primal_value), 1e-12))
        return ok, {"gap": gap, "factor_residual": float(np.max(np.abs(q), initial=0.0)),
                    "hedge_residual": e, "primal": primal_value}

    w, theta = solve_pass(theta, max_iter)
    ok, cert = certify(w, theta)
    status = "ok"
    if not ok:
        w, theta = solve_pass(theta, max_iter)      # 2: resume the joint solve from the polished point
        ok, cert = certify(w, theta)
        status = "ok_after_recovery"
    if not ok:
        w, theta = solve_pass(np.zeros(m), 2 * max_iter)    # 3: cold start, more iterations
        ok, cert = certify(w, theta)
        status = "ok_after_cold_restart"
    if not ok:
        if _fallback:
            raise RuntimeError("allocator could not certify a solution")
        # 4: certified fallback - the matched-diagonal problem (same caps and target,
        # factor risk folded into each stock's variance, no cross-stock covariance).
        sub = {}
        w = allocate_factor(mu, h, d + np.sum(M * M, axis=1), B, np.zeros_like(L), b, kappa, gamma, cap,
                            warm=None, max_iter=max_iter, tol=tol, info=sub, beta_target=beta_target, _fallback=True)
        if info is not None:
            info.update(sub, status="fallback_diagonal")
        if warm is not None:
            warm.pop("theta", None)
        return w
    if info is not None:
        info.update(cert, status=status)
    if warm is not None:
        warm["theta"] = theta.copy()
    return w
