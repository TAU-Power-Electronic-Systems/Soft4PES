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
        System model containing electrical parameters and base values.
    
    Attributes
    ----------
    i_conv_ii_d : float
        Integrator state for the converter current reference in the d-axis.
    i_conv_ii_q : float
        Integrator state for the converter current reference in the q-axis.
    sys : object
        System model containing electrical parameters and base values.
    ctr_pars : SimpleNamespace
        Controller parameters including delta, K_p, k_i, and K_t.
    """

    def __init__(self, sys):
        super().__init__()
        self.i_conv_ii_d = 0
        self.i_conv_ii_q = 0
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
        wn = 2 * np.pi / 10 / Ts_pu

        # Damping ratio
        zeta = np.sqrt(2) / 2

        # Integral gain
        k_i = wn**2 * self.sys.par.X_fc

        # Proportional gain
        k_p = 2 * wn * zeta * self.sys.par.X_fc - self.sys.par.R_fc

        # To faster dynamics response, uncomment the following line
        #k_i = (wn**2 * self.sys.par.X_fc)/5
        #k_p = (2 * wn * zeta *self.sys.par.X_fc - self.sys.par.R_fc)*10

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

        vg = sys.get_grid_voltage(kTs)

        # Calculate the transformation angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the reference for current step (converter current equals grid current)
        i_conv_ref_d = self.input.ig_ref_dq[0]
        i_conv_ref_q = self.input.ig_ref_dq[1]

        # Get dq frame current measurements
        i_conv_dq = alpha_beta_2_dq(sys.i_conv, theta)
        i_conv_d = i_conv_dq[0]
        i_conv_q = i_conv_dq[1]

        self.i_conv_ii_d += self.ctr_pars.k_i * (i_conv_ref_d - i_conv_d)
        self.i_conv_ii_q += self.ctr_pars.k_i * (i_conv_ref_q - i_conv_q)

        lambda_d = self.ctr_pars.k_p * (i_conv_ref_d -
                                        i_conv_d) + self.i_conv_ii_d
        lambda_q = self.ctr_pars.k_p * (i_conv_ref_q -
                                        i_conv_q) + self.i_conv_ii_q

        # Calculate the switching state functions in the dq frame
        d_nd = (lambda_d - self.sys.par.X_fc * self.sys.par.wg * i_conv_q +
                vg[0]) / sys.conv.v_dc
        d_nq = (lambda_q - self.sys.par.X_fc * self.sys.par.wg * i_conv_d +
                vg[1]) / sys.conv.v_dc

        # Get the modulating signal in abc frame
        v_conv_ref_dq = np.array([d_nd, d_nq])
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        u_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)
        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
