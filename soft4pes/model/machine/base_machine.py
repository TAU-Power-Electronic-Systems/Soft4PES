"""
Base values for a machine.
"""

import numpy as np


class BaseMachine:
    """
    Base values for a machine.

    The class computes the base values for a machine based on the rated values.

    Parameters
    ----------
    V_R_SI : float
        Rated voltage of the machine [V] (line-to-line rms voltage).
    I_R_SI : float
        Rated current of the machine [A] (line rms current).
    f_R_SI : float
        Rated frequency [Hz].
    npp : int
        Number of pole pairs.
    pf : float
        Power factor.

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

    """

    def __init__(self, V_R_SI, I_R_SI, f_R_SI, npp, pf):
        self.V = np.sqrt(2 / 3) * V_R_SI
        self.I = np.sqrt(2) * I_R_SI
        self.w = 2 * np.pi * f_R_SI
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.T = pf * npp * self.S / self.w
