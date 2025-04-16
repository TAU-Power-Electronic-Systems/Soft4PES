"""
Modulation methods for power electronic converters.

"""

from soft4pes.control.modulation.carrier_pwm import CarrierPWM
from soft4pes.control.modulation.carrier_pwm_old import CarrierPWMOld

__all__ = [
    "CarrierPWM",
    "CarrierPWMOld",
]
