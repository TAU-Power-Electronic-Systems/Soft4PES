"""
Current Controller (CC) for the control of the converter (or grid) current with L filter.

"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal, magnitude_limiter


class LConvCurrCtr(Controller):
    """
    Current Controller for converter (or grid) current with an L filter. 
    
    Parameters
    ----------
    sys : object
        System model containing electrical parameters and base values.
    
    Attributes
    ----------
    u_ii_comp : complex
        Integrator state for the converter voltage reference in the dq-frame.
    uc_km1_dq : complex
        Previous converter voltage reference in dq frame [p.u.].     
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
        self.uc_km1_dq = complex(0, 0)
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

        # Consider delta equals to one due to not considering delay
        delta = 1

        # Coefficients
        phi = np.exp((-self.sys.par.R_fc / self.sys.par.X_fc) * Ts_pu) * delta
        landa = (delta - phi) / self.sys.par.R_fc

        # The closed-loop pole locations
        p_1 = 0
        p_2 = np.exp(-alpha_c * Ts_pu)
        p_3 = p_2

        # Coefficients
        k_2 = -p_1 - p_2 - p_3 + phi + 1
        k_1 = (p_1 * p_2 + p_1 * p_3 + p_2 * p_3 + k_2 * phi + k_2 -
               phi) / landa

        # State feedback gain
        K_i = np.array([k_1, 0, k_2 * 0])

        # Integral gain
        k_ii = (-p_1 * p_2 * p_3 + k_1 * landa - k_2 * phi) / landa

        # Feedforward gain
        k_ti = k_ii / (1 - p_3)

        self.ctr_pars = SimpleNamespace(delta=delta,
                                        K_i=K_i,
                                        k_ii=k_ii,
                                        k_ti=k_ti)     

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
        i_conv_ref_comp = complex(*self.input.ig_ref_dq)

        # Get dq frame current (converter current equals grid current due to lack of a filter)
        i_conv_comp = complex(*alpha_beta_2_dq(sys.i_conv, theta))

        # As the filter is not concidered, the filter capacitor voltage is assumed to be the same
        # as the grid voltage after the grid indutance.
        uf_dq = complex(*alpha_beta_2_dq(vg-((self.sys.par.Rg+self.sys.par.Xg)* sys.i_conv), theta))

        x_lc = np.array([i_conv_comp, uf_dq, self.uc_km1_dq])

        # State space controller with anti-windup in dq frame
        v_conv_ref_unlim_comp = (self.ctr_pars.k_ti * i_conv_ref_comp) - np.dot(
            self.ctr_pars.K_i, x_lc) + self.u_ii_comp

        # Limiting the converter voltage reference
        v_conv_ref_comp = magnitude_limiter(v_conv_ref_unlim_comp,
                                           sys.conv.v_dc / 2)

        self.u_ii_comp += self.ctr_pars.k_ii * ((
            (v_conv_ref_comp - v_conv_ref_unlim_comp) / self.ctr_pars.k_ti) +
                                              (i_conv_ref_comp - i_conv_comp))
        
        # Get the modulating signal and Hold it for one cycle before sending it out from the
        # controller
        u_abc = self.u_km1_abc
        v_conv_ref_dq = np.array([v_conv_ref_comp.real, v_conv_ref_comp.imag])
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        self.uc_km1_dq = self.ctr_pars.delta * v_conv_ref_comp
        self.u_km1_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)
        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
