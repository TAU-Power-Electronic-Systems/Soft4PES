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
        The dc-link voltage.

    Returns
    -------
    ndarray
        The modulating signal in abc-frame.
    """

    return np.clip(alpha_beta_2_abc(v_ref / (v_dc / 2)), -1, 1)


def magnitude_limiter(unlimited_input, maximum_output):
    """
    Limit the input in dq-frame. The instantaneous limiting function is used
    to limit the amplitude of the current and voltage reference in dq-frame.

    Parameters
    ----------
    maximum_output : float
        Maximum magnitude [p.u.].
    unlimited_input : 1 x 2 ndarray of floats
        Unlimited input [p.u.].

    Returns
    -------
    1 x 2 ndarray of floats
        Limited output [p.u.].
    """

    unlimited_input_mag = np.linalg.norm(unlimited_input)

    if unlimited_input_mag <= maximum_output:
        limited_output = unlimited_input
    else:
        limited_output = (unlimited_input /
                          unlimited_input_mag) * maximum_output

    return limited_output


class FirstOrderFilter:
    """
    General first-order filter.

    Parameters
    ----------
    w_bw : float
        The bandwidth of the filter [p.u.].
    size : int
        The size of the signal to be filtered, i.e. the length of the input vector.

    Attributes
    ----------
    w_bw : float
        The bandwidth of the filter [p.u.].
    output : ndarray
        The filtered signal.
    """

    def __init__(self, w_bw, size):
        self.w_bw = w_bw
        self.output = np.zeros(size)

    def update(self, value_in, Ts, base):
        """
        Update the filter with a new input signal of the defined size.

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
        self.output += Ts_pu * self.w_bw * (value_in - self.output)
