"""Frozen N0 configuration; no learned coefficients or sample data."""
from . import engine as E
CONFIG = {
    **E.CONFIG,
    'alpha_half_life': 1008.0, 'ridge': 0.1, 'min_training_days': 126,
    'feature_clip': 4.0, 'beta_window': 252, 'factor_half_life': 126.0,
    'specific_half_life': 126.0, 'specific_shrinkage': 0.2,
    'variance_floor': 1e-6, 'factor_risk_scale': 0.3,
    'risk_aversion': 200.0, 'cost_horizon': 20.0,
    'weight_cap': 0.05, 'gross_cap': 5.0,
    'risk_beta_column': False, 'matched_diagonal': False,
    'beta_shrinkage': False, 'beta_target': 0.0,
}
