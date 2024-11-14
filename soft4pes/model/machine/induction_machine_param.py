"""
Parameters for an induction machine.
"""

import numpy as np


class InductionMachineParameters:
    """
    Parameters for the InductionMachine.

    Parameters
    ----------
    f_SI : float
        Rated frequency [Hz].
    pf_SI : float
        Power factor.
    Rs_SI : float
        Stator resistance [Ohm].
    Rr_SI : float
        Rotor resistance [Ohm].
    Lls_SI : float
        Stator leakage inductance [H].
    Llr_SI : float
        Rotor leakage inductance [H].
    Lm_SI : float
        Mutual inductance [H].
    base : base value object
        Base values.

    Attributes
    ----------
    f : float
        Rated frequency [p.u.].
    pf : float
        Power factor.
    Rs : float
        Stator resistance [p.u.].
    Rr : float
        Rotor resistance [p.u.].
    Lls : float
        Stator leakage inductance [p.u.].
    Llr : float
        Rotor leakage inductance [p.u.].
    Lm : float
        Mutual inductance [p.u.].
    """

    def __init__(self, f_SI, pf, Rs_SI, Rr_SI, Lls_SI, Llr_SI, Lm_SI, base):
        self.w = 2 * np.pi * f_SI / base.w
        self.pf = pf
        self.Rs = Rs_SI / base.Z
        self.Rr = Rr_SI / base.Z
        self.Xls = Lls_SI / base.L
        self.Xlr = Llr_SI / base.L
        self.Xm = Lm_SI / base.L
        self.Xs = self.Xls + self.Xm
        self.Xr = self.Xlr + self.Xm
        self.D = self.Xs * self.Xr - self.Xm**2
        self.kT = 1 / pf
