"""
Modulation methods for power electronic converters.

"""

from soft4pes.control.modulation.carrier_pwm import CarrierPWM
from soft4pes.control.modulation.common_mode_injection import CommonModeInjection
from soft4pes.control.modulation.opp_pwm import OPPPWM
from soft4pes.control.modulation.utils import get_opp_switching_instants, load_switching_angles_from_file

__all__ = [
    "CarrierPWM",
    "CommonModeInjection",
    "OPPPWM",
    "get_opp_switching_instants",
    "load_switching_angles_from_file",
]
