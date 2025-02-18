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


def magnitude_limiter(input_signal, limit):
    """
    Limit the input in to maximum magnitude. The input can be in alpha-beta or dq-frame, and given  
    as a vector or complex number. 

    Parameters
    ----------
    limit : float
        Maximum magnitude [p.u.].
    input_signal : 1 x 2 ndarray of floats or complex
        Unlimited input [p.u.].

    Returns
    -------
    1 x 2 ndarray of floats
        Limited output [p.u.].
    """

    if isinstance(input_signal, complex):
        input_mag = np.abs(input_signal)
    else:
        input_mag = np.linalg.norm(input_signal)

    if input_mag <= limit:
        output = input_signal
    else:
        output = (input_signal / input_mag) * limit

    return output


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
