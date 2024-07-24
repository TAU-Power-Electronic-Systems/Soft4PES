"""
This module contains the Sequence class which is used to generate a sequence of values over time.
"""

import numpy as np


class Sequence:
    """
    Sequence generator.

    The time array must be increasing. The output values are interpolated
    between the data points.

    Attributes
    ----------
    times : n x 1 ndarray of floats
        Time values is seconds.
    values : n x m ndarray of floats
        Output values.
    """

    def __init__(self, times, values):
        """
        Initialize a Sequence instance.

        Parameters
        ----------
        times : n x 1 ndarray of floats
            Time values is seconds.
        values : n x m ndarray of floats
            Output values.
        """

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
        # Define the dimensions of columns to iterate over
        dim = range(self.values.shape[1])

        #Initialize a list to hold the interpolated values
        interpolated_values = []

        # Perform interpolation for each dimension
        for m in dim:
            inter_value = np.interp(t, self.times, self.values[:, m])
            interpolated_values.append(inter_value)

        return np.array(interpolated_values)
