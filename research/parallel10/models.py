"""Fixed experiment factory. Controls are not an invitation to tune settings."""
def make_policy(mode,shared=None):
    if mode=='G':
        from gls_alpha import CandidatePolicy
        return CandidatePolicy()
    if mode in ('N','N0'):
        from .network import NetworkPolicy
        return NetworkPolicy(mode,shared)
    if mode in ('V','V0'):
        from .factorvar import FactorVARPolicy
        return FactorVARPolicy(mode,shared)
    if mode in ('R','R0'):
        from .robust import RobustPolicy
        return RobustPolicy(mode,shared)
    if mode in ('M','M0'):
        from .mixture import MixturePolicy
        return MixturePolicy(mode,shared)
    if mode in ('C','C0'):
        from .residualcov import ResidualCovPolicy
        return ResidualCovPolicy(mode,shared)
    raise ValueError(mode)
