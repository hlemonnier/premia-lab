"""The sole public strategy: N0, with no alternate mode or cache injection."""
from __future__ import annotations
import numpy as np
from .premia import _PremiaPolicy
from .residuals import snapshots, ew_level, design, cap_increment


def _own_correlation(A, B):
    a = A - A.mean(0)
    b = B - B.mean(0)
    sx = np.maximum(np.sqrt(np.mean(a * a, 0)), 1e-8)
    sy = np.maximum(np.sqrt(np.mean(b * b, 0)), 1e-8)
    # Preserve the frozen matrix-product accumulation order exactly. Only the
    # diagonal is used; no cross-stock links, rankings or slopes are constructed.
    rho = np.diag(a.T @ b / len(a)) / (sx * sy)
    return rho, sx, sy


class N0Policy(_PremiaPolicy):
    def __init__(self):
        super().__init__()
        self.records = []

    def forecast(self, returns_history, characteristics_history):
        R = np.ascontiguousarray(returns_history, dtype=np.float64)
        X = np.ascontiguousarray(characteristics_history, dtype=np.float64)
        self.records = []
        base = super().forecast(R, X)
        S = snapshots(R, X, self.cfg)
        T, N = R.shape
        z = np.zeros((T, N))
        z[1:] = np.clip(S['u'][1:] / np.sqrt(S['d'][:-1]), -6, 6)
        x = ew_level(z, 5)
        out = np.array(base, copy=True)
        own = np.zeros(N)
        xm = np.zeros(N)
        for t in range(505, T):
            if (t - 505) % 126 == 0:
                labels = np.arange(t - 504, t)
                A, Y = x[labels - 1], z[labels]
                rho, sx, sy = _own_correlation(A, Y)
                r1, _, _ = _own_correlation(A[:252], Y[:252])
                r2, _, _ = _own_correlation(A[252:], Y[252:])
                threshold = 3 / np.sqrt(504)
                valid = (r1 * r2 > 0) & (np.abs(rho) > threshold)
                shrink = np.sign(rho) * np.maximum(np.abs(rho) - threshold, 0)
                slopes = shrink * sy / sx
                own = np.clip(np.where(valid, slopes, 0), -.25, .25)
                xm = A.mean(0)
                self.records.append(dict(target_row=t, last_label=t - 1,
                                         own=int(np.count_nonzero(own))))
            normalized = (x[t - 1] - xm) * own
            extra = np.sqrt(S['d'][t - 1]) * normalized
            D = np.column_stack([np.ones(N), design(X, S['beta'], t - 1, self.cfg)])
            extra -= D @ np.linalg.solve(D.T @ D / N + 1e-8 * np.eye(28), D.T @ extra / N)
            out[t, :N] += cap_increment(extra, base[t, :N])
        self.forecast_output = out
        return out
