"""
Parameters for a grid with a stiff voltage source and RL-load.
"""

import numpy as np


class RLGridParameters:
    """
    Parameters for a grid with a stiff voltage source and RL-load.

    Parameters
    ----------
    Vg_SI : float
        Grid voltage [V] (line-to-line rms voltage).
    fg_SI : float
        Grid frequency [Hz].
    Rg_SI : float
        Resistance [Ohm].
    Lg_SI : float
        Inductance [H].
    base : base value object
        Base values.

    Attributes
    ----------
    Vg : float
        Grid voltage [p.u.] (line-to-line rms voltage).
    wg : float
        Angular frequency [p.u.].
    Rg : float
        Resistance [p.u.].
    Xg : float
        Reactance [p.u.].
    """

    def __init__(self, Vg_SI, fg_SI, Rg_SI, Lg_SI, base):
        self.Vg = Vg_SI / base.V
        self.wg = 2 * np.pi * fg_SI / base.w
        self.Rg = Rg_SI / base.Z
        self.Xg = Lg_SI / base.L
