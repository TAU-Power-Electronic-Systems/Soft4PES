"""
Electrical angular speed calculation for an induction machine (IM).
"""

import numpy as np
from soft4pes.control.common.controller import Controller


class WSCalculator(Controller):
    """
    Electrical angular speed calculator for an induction machine (IM).
    The angular speed is calculated based on the rotor flux angle, which 
    is derived from the rotor flux components. The angular speed is filtered 
    using a first-order low-pass filter to reduce noise in the estimation. 
    """

    def __init__(self, sys):
        super().__init__()
        self.sys = sys
        self.ws = 1
        self.theta_km1 = None
        self.tau_ws = 0.01

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and compute controller parameters.
        
        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts

    def execute(self, sys, kTs):
        """
        Calculate electrical angular speed

        Parameters
        ----------
        sys : object
            System model

        Returns
        -------
        ws : float
            Electrical angular speed [rad/s].
        """
        self.output = self.input

        # Calculate current rotor flux angle
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])

        # Handle the first call to this function by initializing the previous angle
        if self.theta_km1 is None:
            self.theta_km1 = theta
            self.output.ws = 1
            return self.output

        # Handle angle wrapping
        if theta < 0 and self.theta_km1 > 0:
            self.theta_km1 -= 2 * np.pi

        # Raw derivative of the angle to calculate angular speed
        ws_raw = (theta - self.theta_km1) / self.Ts / sys.base.w

        # Apply a first-order low-pass filter to smooth the angular speed estimate
        alpha = self.Ts / (self.tau_ws + self.Ts)
        self.ws = alpha * ws_raw + (1.0 - alpha) * self.ws

        # Update the previous angle for next step
        self.theta_km1 = theta

        self.output.ws = self.ws

        return self.output
