"""
Base values for a machine.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class BaseMachine:
    """
    Base values for a machine.

    The class computes the base values for a machine based on the rated values.

    Attributes
    ----------
    V : float
        Base voltage [V].
    I : float
        Base current [A].
    w : float
        Base angular frequency [rad/s].
    S : float
        Base apparent power [VA].
    Z : float
        Base impedance [Ohm].
    L : float
        Base inductance [H].
    T : float
        Base torque [Nm].

    Parameters
    ----------
    Vr: float
        Rated voltage of the machine [V] (line-to-line rms voltage).
    Ir : float
        rated current of the machine [A] (line rms current).
    fr : float
        Machine rated frequency [Hz].
    npp : int
        Number of pole pairs.
    """

    Vr: float
    Ir: float
    fr: float
    npp: int

    def __post_init__(self):
        self.V = np.sqrt(2 / 3) * self.Vr
        self.I = np.sqrt(2) * self.Ir
        self.w = 2 * np.pi * self.fr
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.T = self.npp * self.S / self.w
