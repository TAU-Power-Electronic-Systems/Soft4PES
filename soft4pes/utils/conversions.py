"""
Reference-frame conversions.
"""

import numpy as np


def abc_2_alpha_beta(abc):
    """
    Convert a quantity from abc-frame to alpha-beta frame using the reduced 
    Clarke transformation. The common-mode component is neglected.

    Parameters
    ----------
    abc : 1 x 3 ndarray of floats
        Input quantity in abc-frame. 

    Returns
    -------
    1 x 2 ndarray of floats
        Quantity in alpha-beta frame. 
    """

    K = (2 / 3) * np.array([[1, -1 / 2, -1 / 2],
                            [0, np.sqrt(3) / 2, -np.sqrt(3) / 2]])

    ab = np.dot(K, abc)

    return ab


def alpha_beta_2_abc(alpha_beta):
    """
    Convert a quantity from abc-frame to alpha-beta frame using the inverse 
    reduced Clarke transformation. The common-mode component is neglected.

    Parameters
    ----------
    abc : 1 x 3 ndarray of floats
        Input quantity in abc-frame. 

    Returns
    -------
    1 x 2 ndarray of floats
        Quantity in alpha-beta frame. 
    """

    K_inv = np.array([[1, 0], \
                      [-1 / 2, np.sqrt(3) / 2],
                      [-1 / 2, -np.sqrt(3) / 2]])

    abc = np.dot(K_inv, alpha_beta)

    return abc


def alpha_beta_2_dq(alpha_beta, theta):
    """
    Convert a quantity from alpha-beta frame to dq-frame. The common-mode
    component is neglected.

    Parameters
    ----------
    alpha_beta : 1 x 2 ndarray of floats
        Quantity in alpha-beta frame. 
    theta : float
        Angle of the reference frame in radians.

    Returns
    -------
    1 x 2 ndarray of floats
        Quantity in dq-frame.
    """

    R = np.array([[np.cos(theta), np.sin(theta)],
                  [-np.sin(theta), np.cos(theta)]])

    return np.dot(R, alpha_beta)


def dq_2_alpha_beta(dq, theta):
    """
    Convert a quantity from dq-frame to alpha-beta frame. The common-mode
    component is neglected.

    Parameters
    ----------
    dq : 1 x 2 ndarray of floats
        Quantity in dq-frame. 
    theta : float
        Angle of the reference frame in radians.

    Returns
    -------
    1 x 2 ndarray of floats
        Quantity in alpha-beta frame.
    """

    R_inv = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta), np.cos(theta)]])

    return np.dot(R_inv, dq)


def dq_2_abc(dq, theta):
    """
    Convert a quantity from dq-frame to abc-frame using the inverse reduced Park 
    trasformation. The common-mode component is neglected.

    Parameters
    ----------
    dq : 1 x 2 ndarray of floats
        Quantity in dq-frame. 
    theta : float
        Angle of the reference frame in radians.

    Returns
    -------
    1 x 3 ndarray of floats
        Quantity in abc-frame.
    """

    K_inv_theta = np.array(
        [[np.cos(theta), -np.sin(theta)],
         [np.cos(theta - (2 * np.pi / 3)), -np.sin(theta - (2 * np.pi / 3))], \
         [np.cos(theta + (2 * np.pi / 3)), -np.sin(theta + (2 * np.pi / 3))]])

    return np.dot(K_inv_theta, dq)
