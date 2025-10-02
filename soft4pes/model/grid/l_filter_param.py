"""
Parameters for an L-filter.
"""


class LFilterParameters():
    """
    Parameters for an LCL-filter.

    Parameters
    ----------
    L_fc_SI : float
        Inductance of the converter side filter inductor [H].
    base : base value object
        Base values.
    R_fc_SI : float, optional
        Resistance of the converter side filter inductor [Ohm].


    Attributes
    ----------
    X_fc : float
        Reactance of the converter side filter inductor [p.u.].
    R_fc : float
        Resistance of the converter side filter inductor [p.u.].
    base : base value object
    """

    def __init__(self,
                 L_fc_SI,
                 base,
                 R_fc_SI=0):
        self.X_fc = L_fc_SI / base.L
        self.R_fc = R_fc_SI / base.Z
        self.base = base
