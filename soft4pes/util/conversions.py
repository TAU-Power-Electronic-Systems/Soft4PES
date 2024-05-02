"""
Reference-frame conversions.
"""

import numpy as np


def dq_2_alpha_beta(dq, theta):
    """
    Convert data from dq-frame to alpha-beta frame.

    Parameters
    ----------
    dq : n x 2 ndarray of floats
        Data in dq-frame. 
    theta : n x 1 ndarray of floats
        Angle of the reference frame in radians.

    Returns
    -------
    n x 2 ndarray of floats
        Data in alpha-beta frame.
    """

    n = len(dq)
    ab = np.zeros((n, 2))

    for i in range(n):
        angle = theta[i]
        R = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])

        ab[i, :] = np.dot(R, dq[i, :].T)

    return ab


def abc_2_alpha_beta(abc):
    """
    Convert data from abc-frame to alpha-beta frame.

    Parameters
    ----------
    abc : n x 3 ndarray of floats
        Input data in abc-frame. 

    Returns
    -------
    n x 2 ndarray of floats
        Data in alpha-beta frame. 
    """

    n = len(abc)
    ab = np.zeros((n, 2))
    K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                            [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

    ab = np.dot(K, abc.T)

    return ab.T
