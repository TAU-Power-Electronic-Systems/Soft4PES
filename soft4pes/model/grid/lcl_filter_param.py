"""
Parameters for an LCL-filter.
"""


class LCLFilterParameters():
    """
    Parameters for an LCL-filter.

    Parameters
    ----------
    L_fc_SI : float
        Inductance of the converter side filter inductor [H].
    C_SI : float
        Capacitance of the filter capacitor [F].
    base : base value object
        Base values.
    L_fg_SI : float, optional
        Inductance of the grid side filter inductor [H].
    R_fc_SI : float, optional
        Resistance of the converter side filter inductor [Ohm].
    R_c_SI : float, optional
        Resistance of the filter capacitor [Ohm].
    R_fg_SI : float, optional
        Resistance of the grid side filter inductor [Ohm].

    Attributes
    ----------
    X_fc : float
        Reactance of the converter side filter inductor [p.u.].
    R_fc : float
        Resistance of the converter side filter inductor [p.u.].
    Xc : float
        Reactance of the filter capacitor [p.u.].
    Rc : float
        Resistance of the filter capacitor [p.u.].
    X_fg : float
        Reactance of the grid side filter inductor [p.u.].
    R_fg : float
        Resistance of the grid side filter inductor [p.u.].
    base : base value object
    """

    def __init__(self,
                 L_fc_SI,
                 C_SI,
                 base,
                 L_fg_SI=0,
                 R_fc_SI=0,
                 R_c_SI=0,
                 R_fg_SI=0):
        self.X_fc = L_fc_SI / base.L
        self.R_fc = R_fc_SI / base.Z
        self.Xc = C_SI / base.C
        self.Rc = R_c_SI / base.Z
        self.X_fg = L_fg_SI / base.L
        self.R_fg = R_fg_SI / base.Z
        self.base = base
