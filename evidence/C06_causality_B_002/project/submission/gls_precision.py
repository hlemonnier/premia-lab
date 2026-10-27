"""Normalized precision application for a positive diagonal plus factor model.

This helper implements no fitting, market access or mutable state. Its numerical
fixtures and expectations were frozen before this source was written; see
verification/GLS_PRECISION_PLAN.md and evidence/gls_precision_build_order_001.
"""
from __future__ import annotations

import numpy as np


def normalized_precision_apply(diagonal, factors, values):
    """Apply Sigma^-1 / mean(diag(Sigma^-1)) to a vector or matrix.

    Sigma = diag(diagonal) + factors @ factors.T. Return the weighted values
    with their original shape and the positive scalar mean precision. Inputs
    remain unchanged. Invalid or unrepresentable arithmetic raises ValueError.
    """
    arrays = []
    for value, name in ((diagonal, "diagonal"), (factors, "factors"), (values, "values")):
        try:
            if np.iscomplexobj(value):
                raise ValueError(f"{name} must contain real numbers")
            arrays.append(np.asarray(value, dtype=np.float64))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a real numeric array") from exc
    d, b, v = arrays
    if d.ndim != 1 or not d.size or not np.isfinite(d).all() or np.any(d <= 0):
        raise ValueError("diagonal must be a nonempty positive finite vector")
    n = d.size
    if b.ndim != 2 or b.shape[0] != n or not np.isfinite(b).all():
        raise ValueError("factors must be a finite stock-by-factor matrix")
    if (v.ndim not in (1, 2) or v.shape[0] != n
            or (v.ndim == 2 and v.shape[1] == 0) or not np.isfinite(v).all()):
        raise ValueError("values must be a finite matching vector or nonempty matrix")
    rhs = v[:, None] if v.ndim == 1 else v
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            inverse_diagonal = 1.0 / d
            weighted = inverse_diagonal[:, None] * rhs
            precision_diagonal = inverse_diagonal
            if b.shape[1] and np.any(b):
                inverse_factors = inverse_diagonal[:, None] * b
                inner = np.eye(b.shape[1]) + b.T @ inverse_factors
                weighted -= inverse_factors @ np.linalg.solve(inner, inverse_factors.T @ rhs)
                correction = np.linalg.solve(inner, inverse_factors.T).T
                precision_diagonal = inverse_diagonal - np.sum(inverse_factors * correction, axis=1)
            mean_precision = float(np.mean(precision_diagonal))
            if not np.isfinite(mean_precision) or mean_precision <= 0:
                raise ValueError("mean precision must be positive and finite")
            weighted /= mean_precision
    except (FloatingPointError, np.linalg.LinAlgError) as exc:
        raise ValueError("precision arithmetic must be numerically representable") from exc
    if not np.isfinite(weighted).all():
        raise ValueError("normalized precision result must be finite")
    return (weighted[:, 0] if v.ndim == 1 else weighted), mean_precision
