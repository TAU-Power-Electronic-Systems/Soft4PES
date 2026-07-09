"""
Modulation methods for power electronic converters.

"""

from soft4pes.control.modulation.carrier_pwm import CarrierPWM
from soft4pes.control.modulation.common_mode_injection import CommonModeInjection
from soft4pes.control.modulation.opp_pwm import OPPPWM
from soft4pes.control.modulation.utils import read_switching_angles, load_switching_angles

__all__ = [
    "CarrierPWM",
    "CommonModeInjection",
    "OPPPWM",
    "read_switching_angles",
    "load_switching_angles",
]
