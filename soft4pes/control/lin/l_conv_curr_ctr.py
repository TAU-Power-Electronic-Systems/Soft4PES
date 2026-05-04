"""
Current Controller (CC) for the control of the converter (or grid) current with L filter.
Based on the following reference:
E. Pouresmaeil, C. Miguel-Espinar, M. Massot-Campos, D. Montesinos-Miracle and O. Gomis-Bellmunt, 
"A Control Technique for Integration of DG Units to the Electrical Networks," in IEEE Transactions 
on Industrial Electronics, vol. 60, no. 7, pp. 2881-2893, July 2013, doi: 10.1109/TIE.2012.2209616.

"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal


class LConvCurrCtr(Controller):
    """
    Current Controller for converter (or grid) current with an L filter. 
    
    Parameters
    ----------
    sys : object
        System model.
    
    Attributes
    ----------
    i_conv_ii_dq : ndarray (2,)
        Integrator state of the PI-controller.
    sys : object
        System model.
    ctr_pars : SimpleNamespace
        Controller parameters. 
    """

    def __init__(self, sys):
        super().__init__()
        self.i_conv_ii_dq = np.zeros(2)
        self.sys = sys
        self.ctr_pars = None

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

        # Natural undamped angular frequency
        wn = 2 * np.pi / 20 / Ts_pu

        # Damping ratio
        zeta = np.sqrt(2) / 2

        # Integral gain (discretized)
        k_i = wn**2 * self.sys.par.X_fc * Ts_pu

        # Proportional gain
        k_p = 2 * wn * zeta * self.sys.par.X_fc - self.sys.par.R_fc

        self.ctr_pars = SimpleNamespace(k_i=k_i, k_p=k_p)

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
        theta = self.input.theta

        # Get the reference for current step (converter current equals grid current)
        i_conv_ref_dq = self.input.ig_ref_dq

        # Get dq frame current measurements
        i_conv_dq = alpha_beta_2_dq(sys.i_conv, theta)

        # Current control error in dq-frame
        e_i_conv_dq = i_conv_ref_dq - i_conv_dq

        # Integrator update
        self.i_conv_ii_dq += (self.ctr_pars.k_i * e_i_conv_dq)

        # Proportional + integral action (lambda in dq frame)
        lambda_dq = self.ctr_pars.k_p * e_i_conv_dq + (self.i_conv_ii_dq)

        # Calculate the PCC output voltage in dq frame
        J = np.array([[0, -1], [1, 0]])
        v_pcc = sys.get_pcc_voltage()
        v_pcc_dq = alpha_beta_2_dq(v_pcc, theta)

        # Calculate the switching state functions in the dq frame
        v_conv_ref_dq = lambda_dq + (self.sys.par.X_fc * self.sys.par.wg *
                                     (J.dot(i_conv_dq))) + np.array(
                                         [v_pcc_dq[0], 0])

        # Get the modulating signal in abc frame
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        u_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)

        self.output = SimpleNamespace(u_abc=u_abc)
        return self.output
