""" 
n-level converter model.
"""


class Converter:
    """ 
    Class representing a 2- or 3-level converter with constant dc-link voltage. 

    Initialize a Converter instance.

    Parameters
    ----------
    v_dc_SI : float
        Dc-link voltage [V].
    nl : int
        Number of voltage levels in the converter.
    base : base value object
        Base values.

    Attributes
    ----------
    v_dc : float
        Dc-link voltage [p.u.]
    nl : int
        Number of voltage levels in the converter.
    SW_COMB : 3^nl x 3 ndarray of ints
        Possible converter three-phase switch positions.
    """

    def __init__(self, v_dc_SI, nl, base):
        self.v_dc = v_dc_SI / base.V
        self.nl = nl
