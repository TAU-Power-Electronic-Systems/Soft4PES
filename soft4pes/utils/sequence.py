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
        Time instants is seconds.
    values : n x m ndarray of floats
        Output values.

    Attributes
    ----------
    times : n x 1 ndarray of floats
        Time instants is seconds.
    values : n x m ndarray of floats
        Output values.
    """

    def __init__(self, times, values):
        self.times = times
        self.values = values

    def __call__(self, kTs):
        """
        Interpolate the output.

        Parameters
        ----------
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x m ndarray of floats
            Interpolated output.

        """

        # Check if the "values" attribute is one dimensional
        if self.values.ndim == 1:
            return np.interp(kTs, self.times, self.values)

        # Perform interpolation for each column
        interpolated_values = []
        for m in range(self.values.shape[1]):
            inter_value = np.interp(kTs, self.times, self.values[:, m])
            interpolated_values.append(inter_value)

        return np.array(interpolated_values)
