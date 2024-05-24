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
    values : n x 2 ndarray of floats
        Output values.
    wb : float
        Base angular frequency [rad/s].
    periodic : bool, optional
        Enables periodicity. The default is False.
    """

    def __init__(self, times, values, wb, periodic=False):
        """
        Initialize a Sequence instance.

        Parameters
        ----------
        times : n x 1 ndarray of floats
            Time values is seconds.
        values : n x 2 ndarray of floats
            Output values.
        wb : float
            Base angular frequency [rad/s].
        periodic : bool, optional
            Enables periodicity. The default is False.
        """

        self.times = times
        self.values = values
        self.wb = wb
        if periodic is True:
            self._period = times[-1] - times[0]
        else:
            self._period = None

    def __call__(self, t):
        """
        Interpolate the output.

        Parameters
        ----------
        t : float
            Time [s].

        Returns
        -------
        1 x 2 ndarray of floats
            Interpolated output.

        """
        return np.array([
            np.interp(t, self.times, self.values[:, 0], period=self._period),
            np.interp(t, self.times, self.values[:, 1], period=self._period)
        ])
