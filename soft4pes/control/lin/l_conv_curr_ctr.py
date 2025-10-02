"""
Current Controller (CC) for the control of the converter current with L filter.

"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal, magnitude_limiter


class LConvCurrCtr(Controller):
    """
    Current Controller for converter current with an L filter. 
    
    Parameters
    ----------
    sys : object
        System model containing electrical parameters and base values.
    
    Attributes
    ----------
    u_ii_comp : complex
        Integrator state for the converter voltage reference in the dq-frame.
    v_conv_kp1_comp : complex
        Next converter voltage reference in the dq-frame.
    u_km1_abc : ndarray (3,)
        Previous converter voltage reference in the abc-frame.
    sys : object
        System model containing electrical parameters and base values.
    ctr_pars : SimpleNamespace
        Controller parameters including delta, K_p, k_i, and K_t.
    """

    def __init__(self, sys):
        super().__init__()
        self.u_ii_comp = complex(0, 0)
        self.v_conv_kp1_comp = complex(0, 0)
        self.u_km1_abc = np.array([0, 0, 0])
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

        # Closed-loop controller bandwidth (10x crossover frequency)
        alpha_c = 2 * np.pi / 10 / Ts_pu

        # Consider delta due to considering delay
        delta = 1

        # Controller parameters
        # Integral gain
        k_i = alpha_c^2 * self.sys.par.X_fc
        # Proportional gain
        k_p = (2*alpha_c - 1j*self.sys.par.wg)*self.sys.par.X_fc
        # Feedforward gain
        k_t = alpha_c * self.sys.par.X_fc

        self.ctr_pars = SimpleNamespace(delta=delta,
                                        k_p=k_p,
                                        k_i=k_i,
                                        k_t=k_t)

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

        # Get the grid-voltage angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the reference for current step
        i_conv_ref_comp = complex(*self.input.ig_ref_dq)

        # Get the converter current in dq-frame
        i_conv_comp = complex(*alpha_beta_2_dq(sys.i_conv, theta))

        v_conv_ref_unlim_comp = self.ctr_pars.k_t*i_conv_ref_comp - self.ctr_pars.k_p*i_conv_comp + self.u_ii_comp

        # Limiting the converter voltage reference
        v_conv_ref_comp = magnitude_limiter(v_conv_ref_unlim_comp,
                                            sys.conv.v_dc / 2)

        self.v_conv_kp1_comp = v_conv_ref_comp

        self.u_ii_comp += self.ctr_pars.k_ii * (
            ((v_conv_ref_comp - v_conv_ref_unlim_comp) / self.ctr_pars.k_t) +
            (i_conv_ref_comp - i_conv_comp))

        # Get the modulating signal and Hold it for one cycle before sending it out from the
        # controller
        u_abc = self.u_km1_abc
        v_conv_ref_dq = np.array([v_conv_ref_comp.real, v_conv_ref_comp.imag])
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        self.u_km1_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)
        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
