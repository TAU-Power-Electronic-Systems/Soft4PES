"""
Sequence class can be used to generate a sequence of values over time.
"""

import numpy as np


class Sequence:
    """
    Sequence class can be used to generate a sequence of values over time.

    The time array must be increasing. The output values are interpolated
    between the data points.

    Parameters
    ----------
    times : n x 1 ndarray of floats
        Time values is seconds.
    values : n x m ndarray of floats
        Output values.

    Attributes
    ----------
    times : n x 1 ndarray of floats
        Time values is seconds.
    values : n x m ndarray of floats
        Output values.
    """

    def __init__(self, times, values):
        self.times = times
        self.values = values

    def __call__(self, t):
        """
        Interpolate the output.

        Parameters
        ----------
        t : float
            Time [s].

        Returns
        -------
        1 x m ndarray of floats
            Interpolated output.

        """
        interpolated_values = []

        # Perform interpolation for each column
        for m in range(self.values.shape[1]):
            inter_value = np.interp(t, self.times, self.values[:, m])
            interpolated_values.append(inter_value)

        return np.array(interpolated_values)
