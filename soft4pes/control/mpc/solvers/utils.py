"""Utility functions for MPC solvers."""

import numpy as np


def switching_constraint_violated(nl, uk_abc, u_km1_abc):
    """
    Check if a candidate three-phase switch position violates a switching constraint. 
    A three-level converter is not allowed to directly switch from -1 and 1 (and vice versa) 
    on one phase. 

    Parameters
    ----------
    nl : int
        Number of converter voltage levels.
    uk_abc : 1 x 3 ndarray of ints
        three-phase switch position.
    u_km1_abc : 1 x 3 ndarray of ints
        Previously applied three-phase switch position.

    Returns
    -------
    bool
        Constraint violated.
    """

    if nl == 2:
        res = False
    elif nl == 3:
        res = np.linalg.norm(uk_abc - u_km1_abc, np.inf) >= 2

    return res
