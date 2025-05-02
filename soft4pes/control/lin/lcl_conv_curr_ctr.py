"""
Current Controller (CC) for the control of the converter current with LC(L) filter.

[Ref.]. V. Pirsto, J. Kukkola and M. Hinkkanen, "Multifunctional Cascade Control of Voltage-Source 
Converters Equipped With an LC Filter," IEEE Trans. Ind. Electron., vol. 69, no. 3, 
pp. 2610-2620, March 2022.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_alpha_beta
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import get_modulating_signal, magnitude_limiter


class LCLConvCurrCtr(Controller):
    """
    Current Controller for converter current with an LC(L) filter. 
    
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
        Controller parameters including delta, K_i, k_ii, and K_ti.
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

        # The closed-loop pole locations
        p_1 = 0
        p_2 = np.exp(-alpha_c * Ts_pu)
        p_3 = p_2

        # Consider delta due to considering delay
        delta = np.exp(-self.sys.par.wg * Ts_pu * 1j)

        # Coefficients
        phi = np.exp((-self.sys.par.R_fc / self.sys.par.X_fc) * Ts_pu) * delta
        gamma = (delta - phi) / self.sys.par.R_fc

        k_2 = -p_1 - p_2 - p_3 + phi + 1
        k_1 = (p_1 * p_2 + p_1 * p_3 + p_2 * p_3 + k_2 * phi + k_2 -
               phi) / gamma
        K_i = np.array([k_1, 0, k_2])

        # Integral gain
        k_ii = (-p_1 * p_2 * p_3 + k_1 * gamma - k_2 * phi) / gamma

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

        # Get the grid-voltage angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the reference for current step
        i_conv_ref_comp = complex(*self.input.i_conv_ref_dq)

        # Get the converter current in dq-frame
        i_conv_comp = complex(*alpha_beta_2_dq(sys.i_conv, theta))

        # Get the capacitor voltage in dq-frame
        vc_comp = complex(*alpha_beta_2_dq(sys.vc, theta))

        # Get the converter voltage
        v_conv_comp = self.v_conv_kp1_comp * self.ctr_pars.delta

        x_LC = np.array([i_conv_comp, vc_comp, v_conv_comp])

        v_conv_ref_unlim_comp = (self.ctr_pars.k_ti *
                                 i_conv_ref_comp) - np.dot(
                                     self.ctr_pars.K_i, x_LC) + self.u_ii_comp

        # Limiting the converter voltage reference
        v_conv_ref_comp = magnitude_limiter(v_conv_ref_unlim_comp,
                                            sys.conv.v_dc / 2)
        self.v_conv_kp1_comp = v_conv_ref_comp

        self.u_ii_comp += self.ctr_pars.k_ii * (
            ((v_conv_ref_comp - v_conv_ref_unlim_comp) / self.ctr_pars.k_ti) +
            (i_conv_ref_comp - i_conv_comp))

        # Get the modulating signal and Hold it for one cycle before sending it out from the
        # controller
        u_abc = self.u_km1_abc
        v_conv_ref_dq = np.array([v_conv_ref_comp.real, v_conv_ref_comp.imag])
        v_conv_ref = dq_2_alpha_beta(v_conv_ref_dq, theta)
        self.u_km1_abc = get_modulating_signal(v_conv_ref, sys.conv.v_dc)
        self.output = SimpleNamespace(u_abc=u_abc)

        return self.output
