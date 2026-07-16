"""
Modulation methods for power electronic converters.

"""

from soft4pes.control.modulation.carrier_pwm import CarrierPWM
from soft4pes.control.modulation.common_mode_injection import CommonModeInjection
from soft4pes.control.modulation.opp_computation import OPPComputation

__all__ = [
    "CarrierPWM",
    "CommonModeInjection",
    "OPPComputation",
]
