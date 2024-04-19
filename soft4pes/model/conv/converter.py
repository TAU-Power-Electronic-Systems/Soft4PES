""" 
n-level converter model.
"""

from itertools import product
import numpy as np


class Converter:
    """ 
    Class representing an 2- or 3-level converter with constant dc-link voltage. 

    Attributes
    ----------
    v_dc : float
        Dc_link voltage [pu]
    nl : int
        Number of voltage levels in the converter.
    SW_COMB : 3^nl x 3 ndarray of ints
        Possible converter 3-phase switch positions.
    """

    def __init__(self, v_dc, nl, base):
        """
        Initialize a Converter instance.

        Parameters
        ----------
        v_dc : float
            Dc-link voltage [V].
        nl : int
            Number of voltage levels in the converter.
        base : base value object
            Base values.
        """

        self.v_dc = v_dc / base.V
        self.nl = nl

        if nl == 2:
            sw_pos_3ph = np.array([-1, 1])

        elif nl == 3:
            sw_pos_3ph = np.array([-1, 0, 1])

        # Create all possible 3-phase switch position combinations
        self.SW_COMB = np.array(list(product(sw_pos_3ph, repeat=3)))

    def switching_constraint_violated(self, u_k, u_km1):
        """
        Check if the converter violates a switching constraint. 
        A three level converter is not allowed to change directly between switch positions -1 and 1. 

        Parameters
        ----------
        u_k : 1 x 3 ndarray of ints
            3-phase switch position.
        u_km1 : 1 x 3 ndarray of ints
            Previously applied 3-phase switch position.

        Returns
        -------
        bool
            Constraint violated.
        """

        if self.nl == 2:
            res = 0
        elif self.nl == 3:
            res = np.max(np.abs(u_k - u_km1)) >= 2

        return res

    def get_allowed_switch_positions(self, u_km1):
        """
        Get allowed 1-phase switch positions based on the previously applied position. 
        A three level converter is not allowed to change directly between positions -1 and 1. 

        Parameters
        ----------
        u_km1 : int
            Previously applied 1-phase switch position.

        Returns
        -------
        1 x n ndarray of ints (n is the number of allowed switch positions)
            Allowed 1-phase switch positions.
        """

        if self.nl == 2:
            res = np.array([-1, 1])

        elif self.nl == 3:
            if u_km1 == -1:
                res = np.array([-1, 0])
            if u_km1 == 0:
                res = np.array([-1, 0, 1])
            if u_km1 == 1:
                res = np.array([0, 1])

        return res
