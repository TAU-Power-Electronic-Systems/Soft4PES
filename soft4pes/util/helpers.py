"""
Sequency class is used to save reference sequences and interpolate the output values.
"""

import numpy as np
from soft4pes.util.conversions import dq_2_alpha_beta


class Sequence:
    """
    Sequence generator.

    The time array must be increasing. The output values are interpolated
    between the data points.

    Attributes
    ----------
    times : n x 1 ndarray of floats
        Time values [s]
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
            Time values [s].
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

    def get_ref_Np(self, ctr, t):
        """
        Get the reference value for the next Np time steps.

        Parameters
        ----------
        sys : system object
            System object.
        ctr : object
            Control system object.
        t : float
            Current time [s].

        Returns
        -------
        Np x 2 ndarray of floats
            Reference values for the next Np time steps.
        """
        # Get current reference in dq-frame
        ref_k_dq = self(t)

        # Convert to alpha-beta frame for next Np timesteps
        angle_vect = -np.pi / 2 + t * self.wb + self.wb * np.arange(
            1, ctr.Np + 1) * ctr.Ts

        return dq_2_alpha_beta(np.ones((ctr.Np, 1)) * ref_k_dq, angle_vect)
