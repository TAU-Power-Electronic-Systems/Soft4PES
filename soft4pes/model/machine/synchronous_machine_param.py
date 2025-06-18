"""
Parameters for an induction machine.
"""

import numpy as np


class SynchronousMachineParameters:
    """
    Parameters for the InductionMachine.

    Parameters
    ----------
    fs_SI : float
        Synchronous (stator) electrical frequency [Hz].
    pf_SI : float
        Power factor.
    Rs_SI : float
        Stator resistance [Ohm].
    Lsd_SI : float
        Stator d-axis inductance [H].
    Lsq_SI : float
        Stator q-axis inductance [H].
    LambdaPM_SI : float
        Permanent magnet flux linkage [Wb].
    base : base value object
        Base values.

    Attributes
    ----------
    ws : float
        Synchronous (stator) electrical angular frequency [p.u.].
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

    def __init__(self, fs_SI, pf_S1, Rs_SI, Lsd_SI, Lsq_SI, LambdaPM_SI, base):
        self.ws = 2 * np.pi * fs_SI / base.w
        self.pf = pf_S1
        self.Rs = Rs_SI / base.Z
        self.Xsd = Lsd_SI / base.L
        self.Xsq = Lsq_SI / base.L
        self.PsiPM = LambdaPM_SI * base.w / base.V
        self.kT = 1 / pf_S1
