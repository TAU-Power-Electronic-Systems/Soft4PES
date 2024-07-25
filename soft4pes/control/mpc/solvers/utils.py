"""Utility functions for MPC solvers."""

import numpy as np


def switching_constraint_violated(nl, uk, u_km1):
    """
    Check if the converter violates a switching constraint. 
    A three-level converter is not allowed to change directly between switch positions -1 and 1. 

    Parameters
    ----------
    nl : int
        Number of converter voltage levels.
    uk : 1 x 3 ndarray of ints
        3-phase switch position.
    u_km1 : 1 x 3 ndarray of ints
        Previously applied 3-phase switch position.

    Returns
    -------
    bool
        Constraint violated.
    """

    if nl == 2:
        res = False
    elif nl == 3:
        res = np.linalg.norm(uk - u_km1, np.inf) >= 2

    return res
