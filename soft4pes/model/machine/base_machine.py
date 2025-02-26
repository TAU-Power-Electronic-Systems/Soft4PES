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
    Vm_R_SI : float
        Rated voltage of the machine [V] (line-to-line rms voltage).
    Im_R_SI : float
        Rated current of the machine [A] (line rms current).
    fm_R_SI : float
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

    def __init__(self, Vm_R_SI, Im_R_SI, fm_R_SI, npp, pf):
        self.V = np.sqrt(2 / 3) * Vm_R_SI
        self.I = np.sqrt(2) * Im_R_SI
        self.w = 2 * np.pi * fm_R_SI
        self.S = 3 / 2 * self.V * self.I
        self.Z = self.V / self.I
        self.L = self.Z / self.w
        self.T = pf * npp * self.S / self.w
