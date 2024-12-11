"""
Parameters for a grid with a stiff voltage source and RL-load.
"""

import numpy as np


class RLGridParameters:
    """
    Parameters for a grid with a stiff voltage source and RL-load.

    Parameters
    ----------
    Vgr_SI : float
        Rated voltage [V] (line-to-line rms voltage).
    fgr_SI : float
        Rated frequency [Hz].
    Rg_SI : float
        Resistance [Ohm].
    Lg_SI : float
        Inductance [H].
    base : base value object
        Base values.

    Attributes
    ----------
    Vgr : float
        Rated voltage [p.u.] (line-to-line rms voltage).
    wg : float
        Angular frequency [p.u.].
    Rg : float
        Resistance [p.u.].
    Xg : float
        Reactance [p.u.].
    """

    def __init__(self, Vgr_SI, fgr_SI, Rg_SI, Lg_SI, base):
        self.Vgr = Vgr_SI / base.V
        self.wg = 2 * np.pi * fgr_SI / base.w
        self.Rg = Rg_SI / base.Z
        self.Xg = Lg_SI / base.L
