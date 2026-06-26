"""
Parameters for an induction machine.
"""

import numpy as np


class InductionMachineParameters:
    """
    Parameters for the InductionMachine.

    Parameters
    ----------
    fs_SI : float
        Synchronous (stator) electrical frequency [Hz].
    n_R_SI : float
        Rotor speed [rpm].
    pf_SI : float
        Power factor.
    npp : int
        Number of pole pairs.
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
    ws : float
        Synchronous (stator) electrical angular frequency [p.u.].
    pf : float
        Power factor.
    npp : int
        Number of pole pairs.
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

    def __init__(self, fs_SI, n_R_SI, pf, npp, Rs_SI, Rr_SI, Lls_SI, Llr_SI,
                 Lm_SI, base):
        self.ws = 2 * np.pi * fs_SI / base.w
        self.pf = pf
        self.npp = npp
        self.Rs = Rs_SI / base.Z
        self.Rr = Rr_SI / base.Z
        self.Xls = Lls_SI / base.L
        self.Xlr = Llr_SI / base.L
        self.Xm = Lm_SI / base.L
        self.Xs = self.Xls + self.Xm
        self.Xr = self.Xlr + self.Xm
        self.D = self.Xs * self.Xr - self.Xm**2
        self.kT = 1 / pf
        self.Xsigma = self.D / self.Xr
        self.wl = self.ws - self.npp * n_R_SI / 60 / fs_SI
