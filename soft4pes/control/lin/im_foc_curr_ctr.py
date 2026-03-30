"""
Field-oriented control (FOC) for the current control of an induction machine (IM).

"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal


class FOCCurrCtr(Controller):
    """
    Field-oriented control (FOC) for the current control of a induction machine (IM).
    
    Parameters
    ----------
    sys : object
        System model.
    
    Attributes
    ----------
    iS_ii_dq : ndarray (2,)
        Integrator state of the PI-controller.
    sys : object
        System model.
    ctr_pars : SimpleNamespace
        Controller parameters. 
    """

    def __init__(self, sys):
        super().__init__()
        self.iS_ii_dq = np.zeros(2)
        self.sys = sys
        self.ctr_pars = None

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and compute controller parameters.

        Magnitude optimum criterion based on:
        J. W. Umland and M. Safiuddin, 
        "Magnitude and symmetric optimum criterion for the design 
        of linear control systems: what is it and how does it compare with the others?," 
        in IEEE Transactions on Industry Applications, vol. 26, no. 3, 
        pp. 489-497, May-June 1990, doi: 10.1109/28.55967
        
        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts
        Ts_pu = self.Ts * self.sys.base.w

        # First-order approximaton of the stator current dynamics, time constant
        t1 = self.sys.par.Xsigma / self.sys.par.Rs

        # First-order gain
        k1 = 1 / self.sys.par.Rs

        # PWM delay
        td = 1 / 2 * Ts_pu

        # Integration time
        ti = 2 * k1 * td

        # Integral gain (discretized)
        ki = 1 / ti * Ts_pu

        # Proportional gain
        kp = t1 / ti

        self.ctr_pars = SimpleNamespace(k_i=ki, k_p=kp)

    def execute(self, sys, kTs):
        """
        Execute the Current Controller (CC) and save the controller data.

        Parameters
        ----------
        sys : object
            System model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Three-phase modulating signal.
        """
        # Calculate the transformation angle
        theta = np.arctan2(sys.psiR[1], sys.psiR[0])

        # Stator current in dq frame
        iS_dq = alpha_beta_2_dq(sys.iS, theta)

        # Stator current reference in the dq frame for the current step
        T_ref = self.input.T_ref
        iS_ref_dq = sys.calc_stator_current(sys.psiR_mag_ref, T_ref)

        # Current control error in dq-frame
        e_i_conv_dq = iS_ref_dq - iS_dq

        # Integrator update
        self.iS_ii_dq += (self.ctr_pars.k_i * e_i_conv_dq)

        # Proportional + integral action (lambda in dq frame)
        lambda_dq = self.ctr_pars.k_p * e_i_conv_dq + (self.iS_ii_dq)

        # Calculate cross coupling compensation term
        x_coup_dq = np.array([
            -sys.wr * sys.par.Xsigma * iS_dq[1],
            sys.wr * sys.par.Xsigma * iS_dq[0]
        ])

        # Compute the voltage reference in dq frame
        v_conv_ref_dq = lambda_dq + x_coup_dq

        # Get the modulating signal in abc frame
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        u_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)

        self.output = SimpleNamespace(u_abc=u_abc)
        return self.output
