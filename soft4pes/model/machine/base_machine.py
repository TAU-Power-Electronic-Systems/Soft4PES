"""
Base values for a machine.
"""

import numpy as np


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
    Vr : float
        Rated voltage of the machine [V] (line-to-line rms voltage).
    Ir : float
        Rated current of the machine [A] (line rms current).
    fr : float
        Rated frequency [Hz].
    npp : int
        Number of pole pairs.
    pf : float
        Power factor.
    """

    def __init__(self, Vr, Ir, fr, npp, pf):
        """
        Initialize a BaseMachine instance.

        Parameters
        ----------
        Vr : float
            Rated voltage of the machine [V] (line-to-line rms voltage).
        Ir : float
            Rated current of the machine [A] (line rms current).
        fr : float
            Rated frequency [Hz].
        npp : int
            Number of pole pairs.
        pf : float
            Power factor.
        """
        self.V = np.sqrt(2 / 3) * Vr
        self.I = np.sqrt(2) * Ir
        self.w = 2 * np.pi * fr
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.T = pf * npp * self.S / self.w
