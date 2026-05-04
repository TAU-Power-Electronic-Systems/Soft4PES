""" 
Class representing a 2- or 3-level converter with constant dc-link voltage. 
"""


class Converter:
    """ 
    Class representing a 2- or 3-level converter with constant dc-link voltage. 

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
    sw_pos_3ph : list of ints
        Possible one-phase switch positions.
    """

    def __init__(self, v_dc_SI, nl, base):
        self.v_dc = v_dc_SI / base.V
        self.nl = nl
        if nl == 2:
            self.sw_pos_3ph = [-1, 1]
        elif nl == 3:
            self.sw_pos_3ph = [-1, 0, 1]
        else:
            raise ValueError(
                'Only two- and three-level converters are supported.')
