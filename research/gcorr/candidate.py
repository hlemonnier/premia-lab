"""Frozen GLS alpha plus the pre-existing standardized-correlation policy.

Only the allocation covariance changes. The covariance used to estimate GLS
premia deliberately remains the original one: no extra interaction is tuned.
"""
from __future__ import annotations
import numpy as np
from gls_alpha import gls_forecast
from .correlation_reference import CandidatePolicy as CorrelationPolicy


class CandidatePolicy(CorrelationPolicy):
    def forecast(self, returns_history, characteristics_history):
        base = super().forecast(returns_history, characteristics_history)
        n = np.shape(returns_history)[1]
        alpha, self.learner_records = gls_forecast(
            returns_history, characteristics_history, base[:, :n + 27], self.cfg,
        )
        self.forecast_output = np.hstack([alpha, base[:, n:]])
        return self.forecast_output
