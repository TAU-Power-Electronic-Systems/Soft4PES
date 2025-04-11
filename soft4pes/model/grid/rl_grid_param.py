"""
Parameters for a grid with a voltage source and an RL-load. The grid voltage can be given as a 
constant or as a function of time using a Sequence object. 
"""

import numpy as np
from soft4pes.utils import Sequence


class RLGridParameters:
    """
    Parameters for a grid with a voltage source and an RL-load. The grid voltage can be given as a 
    constant or as a function of time using a Sequence object. 

    Parameters
    ----------
    Vg_SI : float or Sequence
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
    Vg : float or Sequence
        Grid voltage [p.u.] (line-to-line rms voltage).
    wg : float
        Angular frequency [p.u.].
    Rg : float
        Resistance [p.u.].
    Xg : float
        Reactance [p.u.].
    """

    def __init__(self, Vg_SI, fg_SI, Rg_SI, Lg_SI, base):
        if isinstance(Vg_SI, Sequence):
            self.Vg = Sequence(times=Vg_SI.times, values=Vg_SI.values / base.V)
        else:
            self.Vg = Vg_SI / base.V

        self.wg = 2 * np.pi * fg_SI / base.w
        self.Rg = Rg_SI / base.Z
        self.Xg = Lg_SI / base.L
