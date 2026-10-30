"""Exact cost-aware allocator with diagonal + low-rank factor risk.

Solves, for the drifted book h,

    maximize   mu'w - gamma/2 (w' diag(d) w + ||L'B'w||^2) - kappa'|w - h|
    subject to b'w = 0,  |w_i| <= cap_i,

where F = L L' is the factor covariance. The k+1 equalities z = L'B'w and
b'w = 0 are dualized; given the multipliers each stock solves the same scalar
no-trade-band/clip problem as the C09 allocator. The convex dual is minimized
by damped Newton with Armijo backtracking, then the beta multiplier is polished
by bisection so the hedge holds to floating-point tolerance.
See ALLOCATOR_SPEC.md for the specification and test_allocator.py for checks.
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
                    max_iter=100, tol=1e-13):
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
    M = B @ L                                   # (n, r): z = M'w
    r = M.shape[1]
    movable = cap > 0
    if not movable.any():
        return np.zeros(n)
    bscale = float(np.max(np.abs(b[movable])))
    use_beta = bscale > 0
    bn = b / bscale if use_beta else np.zeros(n)
    A = np.hstack([M, bn[:, None]]) if use_beta else M
    A[~movable] = 0.0
    m = A.shape[1]
    reg = np.zeros(m); reg[:r] = 1.0 / gamma   # z-block curvature
    expo_tol = max(64 * np.finfo(float).eps * float(np.abs(bn) @ cap), np.nextafter(0, 1))

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
        return phi + lam @ lam / (2 * gamma)

    def grad(theta, w):
        g = -(A.T @ w)
        g[:r] += theta[:r] / gamma
        return g

    theta = np.zeros(m)
    if warm is not None and isinstance(warm.get("theta"), np.ndarray) and warm["theta"].shape == (m,):
        theta = warm["theta"].copy()
    w, s, inner = primal(theta)
    val = dual(theta, w, s)
    for _ in range(max_iter):
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
        # Polish the beta multiplier: exposure bn'w is nonincreasing in theta[r].
        def expo(nu):
            th = theta.copy(); th[r] = nu
            wv = primal(th)[0]
            return float(bn @ wv), wv, th
        e0, w0, th0 = expo(theta[r])
        if abs(e0) > expo_tol:
            step = max(np.max(np.abs(mu[movable])), np.max(diag[movable] * cap[movable]),
                       np.max(kappa[movable]), 1e-300)
            lo = hi = theta[r]
            if e0 > 0:
                while True:
                    hi += step; e, _, _ = expo(hi)
                    if e <= 0: break
                    step *= 2
                    if step > 1e300: raise RuntimeError("cannot bracket beta hedge")
            else:
                while True:
                    lo -= step; e, _, _ = expo(lo)
                    if e >= 0: break
                    step *= 2
                    if step > 1e300: raise RuntimeError("cannot bracket beta hedge")
            best = (abs(e0), w0, th0)
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if mid in (lo, hi): break
                e, wv, th = expo(mid)
                if abs(e) < best[0]: best = (abs(e), wv, th)
                if abs(e) <= expo_tol: break
                if e > 0: lo = mid
                else: hi = mid
            if best[0] > expo_tol:
                raise RuntimeError("beta hedge did not converge")
            _, w, theta = best
    if warm is not None:
        warm["theta"] = theta.copy()
    return w
