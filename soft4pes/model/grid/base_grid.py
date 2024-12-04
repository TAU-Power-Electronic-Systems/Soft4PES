"""
Base values for a grid.
"""

import numpy as np


class BaseGrid:
    """
    Base values for a grid.

    The class computes the base values for a grid based on the rated values.

    Parameters
    ----------
    Vgr_SI : float
        Rated voltage [V] (line-to-line rms voltage).
    Igr_SI : float
        Rated current [A] (line rms current).
    fgr_SI : float
        Rated frequency [Hz].

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
    C : float
        Base capacitance [F].
    """

    def __init__(self, Vgr_SI: float, Igr_SI: float, fgr_SI: float):
        self.V = np.sqrt(2 / 3) * Vgr_SI
        self.I = np.sqrt(2) * Igr_SI
        self.w = 2 * np.pi * fgr_SI
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.C = 1 / (self.Z * self.w)
