"""
Modulation methods for power electronic converters.

"""

from soft4pes.control.modulation.carrier_pwm import CarrierPWM
from soft4pes.control.modulation.common_mode_injection import CommonModeInjection

__all__ = [
    "CarrierPWM",
    "CommonModeInjection",
]
