"""
Utility functions and classes for the control module.
"""

import numpy as np
from soft4pes.utils import alpha_beta_2_abc


def wrap_theta(theta):
    """
    Wrap the angle theta to the range [-pi, pi].

    Parameters
    ----------
    theta : float
        The angle in radians.

    Returns
    -------
    float
        The wrapped angle in radians.
    """

    return (theta + np.pi) % (2 * np.pi) - np.pi


def get_modulating_signal(v_ref, v_dc):
    """
    Convert a voltage reference to a modulating signal.

    Parameters
    ----------
    v_ref : ndarray
        The reference voltage in alpha-beta frame.
    v_dc : float
        The DC link voltage.

    Returns
    -------
    ndarray
        The modulating signal in abc frame.
    """

    return np.clip(alpha_beta_2_abc(v_ref / (v_dc / 2)), -1, 1)


class FirstOrderFilter:
    """
    General first order filter.

    Parameters
    ----------
    wb : float
        The bandwidth of the filter [p.u.].
    size : int
        The size of the signal to be filtered.

    Attributes
    ----------
    wb : float
        The bandwidth of the filter [p.u.].
    output : ndarray
        The filtered signal.
    """

    def __init__(self, wb, size):
        self.wb = wb
        self.output = np.zeros(size)

    def update(self, value_in, Ts, base):
        """
        Update the filter with a new input signal.

        Parameters
        ----------
        value_in : ndarray
            The input signal to be filtered.
        Ts : float
            The sampling interval [s].
        base : object
            The base values object containing the base angular frequency.
        """
        Ts_pu = Ts * base.w
        self.output += Ts_pu * self.wb * (value_in - self.output)
