"""
Electrical angular speed calculation for an induction machine (IM).
"""

import numpy as np
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import FirstOrderFilter


class IMwsEstimator(Controller):
    """
    Electrical angular speed calculator for an induction machine (IM). The angular speed is 
    calculated based on the rotor flux angle, which is derived from the rotor flux components. The 
    angular speed is filtered using a first-order low-pass filter to reduce noise in the estimation.

    Parameters
    ----------
    sys : object
        System model.
    w_bw : float, optional
        Cutoff frequency for the low-pass filter applied to the angular speed estimation.
    
    Attributes
    ----------
    sys : object
        System model.
    theta_km1 : float
        Previous rotor flux angle used for angular speed calculation.
    w_bw : float
        Cutoff frequency for the low-pass filter applied to the angular speed estimation [p.u.]
    filter : FirstOrderFilter
        First-order low-pass filter for smoothing the angular speed estimate.
    """

    def __init__(self, sys, w_bw=0.5):
        super().__init__()
        self.sys = sys
        self.theta_km1 = None
        self.w_bw = w_bw
        self.filter = FirstOrderFilter(w_bw=w_bw, size=1, init=sys.wr)

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
        Calculate and filter electrical angular speed

        Parameters
        ----------
        sys : object
            System model

        Returns
        -------
        output : SimpleNamespace
            Output containing the estimated electrical angular speed.
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

        # Raw derivative of the angle
        ws_raw = (theta - self.theta_km1) / self.Ts / sys.base.w

        # Apply a first-order low-pass filter to smooth the angular speed estimate
        self.filter.update(ws_raw, self.Ts, sys.base)

        # Update the previous angle for next step
        self.theta_km1 = theta

        self.output.ws = self.filter.output

        return self.output
