"""
Phase-locked loop (PLL)
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import wrap_theta


class PLL(Controller):
    """
    Phase-locked loop (PLL) implementation.
    """

    def __init__(self, sys, zeta=np.sqrt(2) / 2, wn=2 * np.pi * 20):
        super().__init__()
        self.theta_pll = -np.pi / 2
        self.w_pll_ii = sys.par.wg
        self.sys = sys
        self.ctr_pars = None
        self.zeta = zeta
        self.wn = wn

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and compute controller parameters.
        
        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts
        Ts_pu = self.Ts * self.sys.base.w

        # Integral gain (discretized)
        k_i = (self.wn / self.sys.base.w)**2 * Ts_pu
        # Proportional gain
        k_p = 2 * (self.wn / self.sys.base.w) * self.zeta

        self.ctr_pars = SimpleNamespace(k_i=k_i, k_p=k_p)

    def execute(self, sys, kTs):
        """
        Execute the PLL control algorithm to estimate the grid voltage angle.
        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].
        Returns
        -------
        output : SimpleNamespace
            The output of the PLL, containing the estimated grid voltage angle (theta) and 
            the active and reactive power references.
        """
        theta = self.theta_pll

        # Get PCC voltage and transform to dq-frame
        v_pcc = sys.get_pcc_voltage()
        v_pcc_dq = alpha_beta_2_dq(v_pcc, self.theta_pll)

        # Update PLL states
        w_pll = self.ctr_pars.k_p * v_pcc_dq[1] + self.w_pll_ii
        self.w_pll_ii += self.ctr_pars.k_i * v_pcc_dq[1]
        self.theta_pll += w_pll * self.Ts * self.sys.base.w

        # Wrap the angle to [-pi, pi]
        self.theta_pll = wrap_theta(self.theta_pll)

        self.output = SimpleNamespace(theta=theta,
                                      P_ref=self.input.P_ref,
                                      Q_ref=self.input.Q_ref)

        return self.output
