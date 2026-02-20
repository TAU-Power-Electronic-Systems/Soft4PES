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


class DiscreteTransferFunction:
    """
    Generic discrete-time transfer function implementation.

    The transfer function is defined as

        Y(z) / U(z) = (b0 + b1 z^-1 + ... + bm z^-m)
                      --------------------------------
                      (a0 + a1 z^-1 + ... + an z^-n)

    Parameters
    ----------
    numerator_coeffs : array-like
        Numerator coefficients of the transfer function.
    denominator_coeffs : array-like, optional
        Denominator coefficients of the transfer function.
        If not given, [1] is used.
    """

    def __init__(self, numerator_coeffs, denominator_coeffs=None):
        self.numerator_coeffs = np.array(numerator_coeffs)
        self.denominator_coeffs = np.array(
            [1] if denominator_coeffs is None else denominator_coeffs
        )

        if self.denominator_coeffs[0] != 1:
            self.numerator_coeffs = self.numerator_coeffs / self.denominator_coeffs[0]
            self.denominator_coeffs = self.denominator_coeffs / self.denominator_coeffs[0]

        self.buffer_input = None
        self.buffer_output = None

    def apply(self, input_signal):
        """
        Apply the discrete transfer function to the input signal.

        Parameters
        ----------
        input_signal : float or array-like
            The current input signal.

        Returns
        -------
        float or ndarray
            The filtered output signal.
        """
        input_signal = np.array(input_signal)

        scalar_input = input_signal.ndim == 0
        if scalar_input:
            input_signal = np.array([input_signal])

        if self.buffer_input is None:
            self.buffer_input = np.zeros((len(self.numerator_coeffs),) + input_signal.shape)
            self.buffer_output = np.zeros((len(self.denominator_coeffs) - 1,) + input_signal.shape)

        self.buffer_input[1:] = self.buffer_input[:-1]
        self.buffer_input[0] = input_signal

        output = np.tensordot(self.numerator_coeffs, self.buffer_input, axes=(0, 0))

        if len(self.denominator_coeffs) > 1:
            output -= np.tensordot(self.denominator_coeffs[1:], self.buffer_output, axes=(0, 0))
            self.buffer_output[1:] = self.buffer_output[:-1]
            self.buffer_output[0] = output

        if scalar_input:
            return output[0]
        return output
