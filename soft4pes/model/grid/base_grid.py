"""
Base values for a grid.
"""

import numpy as np


class BaseGrid:
    """
    Base values for a grid.

    The class computes the base values for a grid based on the rated values.

    Attributes
    ----------
    Vgr : float
        Nominal voltage [V].
    Igr : float
        Nominal current [A].
    fgr : float
        Nominal frequency [Hz].
    V : float
        Base voltage [V].
    I : float
        Base current [A].
    w : float
        Angular frequency [rad/s].
    S : float
        Apparent power [VA].
    Z : float
        Impedance [Ohm].
    L : float
        Inductance [H].
    C : float
        Capacitance [F].
    """

    def __init__(self, Vgr: float, Igr: float, fgr: float):
        """
        Initialize a BaseGrid instance.

        Parameters
        ----------
        Vgr : float
            Rated voltage [V].
        Igr : float
            Rated current [A].
        fgr : float
            Rated frequency [Hz].
        """

        self.Vgr = Vgr
        self.Igr = Igr
        self.fgr = fgr
        self.compute_base_values()

    def compute_base_values(self):
        """
        Compute the base values.

        """

        self.V = np.sqrt(2 / 3) * self.Vgr
        self.I = np.sqrt(2) * self.Igr
        self.w = 2 * np.pi * self.fgr
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.C = 1 / (self.Z * self.w)
