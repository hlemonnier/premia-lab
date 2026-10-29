"""Only the predeclared composition of unchanged E2 and unchanged M0/M1."""
from common import wrapper
from execution import make_execution
from sleeve import MarketSleeve


def make_joint(clean, sleeve=.05):
    inner = wrapper(clean, "E2", make_execution)
    return MarketSleeve(inner, sleeve)
