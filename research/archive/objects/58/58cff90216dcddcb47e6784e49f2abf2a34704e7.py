"""Exactly the pre-admitted F2 forecast plus unchanged VTvol composition."""
from overlay import VolatilityOverlay
from prototype import make_forecast


def make_joint(engine, config, power=.5):
    if power not in (0.0,.5):
        raise ValueError("joint admits only fixed-F2 control and VTvol")
    engine.forecast=make_forecast(engine,"F2")
    return VolatilityOverlay(engine,config,power=power)
