""" 
n-level inverter model.
"""

from itertools import product
import numpy as np


class Inverter:
    """ 
    Class representing an 2- or 3-level inverter with constant dc-link voltage. 

    Attributes
    ----------
    v_dc : float
        Dc_link voltage [pu]
    nl : float
        Number of voltage levels in the inverter
    SW_COMB : 3^nl x 3 ndarray of ints
        Possible converter switching states.
    """

    def __init__(self, v_dc, nl, base):
        """
        Initialize an Inverter instance.

        Parameters
        ----------
        v_dc : float
            Dc_link voltage [V].
        nl : int
            Number of voltage levels in the inverter.
        base : base value object
            Base values.
        """

        self.v_dc = v_dc / base.V
        self.nl = nl

        if nl == 2:
            sw_pos = np.array([-1, 1])
        elif nl == 3:
            sw_pos = np.array([-1, 0, 1])

        # Create all possible switching states combinations
        self.SW_COMB = np.array(list(product(sw_pos, repeat=3)))

    def switching_constraint_violated(self, u_k, u_km1):
        """
        Check if the converter violates a switching constraint. 
        A three level inverter is not allowed to change directly between states -1 and 1. 

        Parameters
        ----------
        u_k : 3 x 1 ndarray of ints
            Switching state.
        u_km1 : 1 x 3 ndarray of ints
            Previously applied switching state.

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

    def get_allowed_switching_states(self, u_km1):
        """
        Get possible switching states based on the previously applied state. 
        A three level inverter is not allowed to change directly between states -1 and 1. 

        Parameters
        ----------
        u_km1 : 1 x 3 ndarray of ints
            Previously applied switching state.

        Returns
        -------
        1 x n ndarray of ints
            Allowed swithcing states.
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
