"""
Voltage Controller (VC) for the control of the capacitor voltage in the three-phase voltage-source 
converter equipped with an LC(L) filter.
Provide the converter current reference in dq-frame for Current Controller (CC).

[Ref.]. V. Pirsto, J. Kukkola and M. Hinkkanen, "Multifunctional Cascade Control of Voltage-Source 
Converters Equipped With an LC Filter," IEEE Trans. Ind. Electron., vol. 69, no. 3, pp. 2610-2620, 
March 2022.
"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils import alpha_beta_2_dq
from soft4pes.control.common.controller import Controller
from soft4pes.control.common.utils import magnitude_limiter


class LCLVcCtr(Controller):
    """
    Voltage Controller for the control of the capacitor voltage. 
    
    Parameters
    ----------
    sys : object
        The system model containing electrical parameters and base values.
    curr_ctr : object
        The current controller containing its controller parameters and attributes.
    I_conv_max: float (optional)
        The maximum converter current in per unit (p.u.).
    
    Attributes
    ----------
    u_iu_comp : complex
        Integrator state for the converter voltage reference in the dq-frame.
    sys : object
        System model containing electrical parameters and base values.
    I_conv_max: float
        The maximum converter current in per unit (p.u.).
    ctr_pars : SimpleNamespace
        Controller parameters including delta, K_u, k_iu, and K_tu.
    curr_ctr : object
        The current controller containing its controller parameters and attributes.    
    """

    def __init__(self, sys, curr_ctr, I_conv_max=1.2):
        super().__init__()
        self.u_iu_comp = complex(0, 0)
        self.sys = sys
        self.I_conv_max = I_conv_max
        self.ctr_pars = None
        self.curr_ctr = curr_ctr

    def set_sampling_interval(self, Ts):
        """
        Set the sampling interval and compute controller parameters.
        
        [Ref.]. H.-S. Kim, H.-S. Jung, and S.-K. Sul, “Discrete-time voltage controller for voltage 
        source converters with LC ﬁlter based on state-space models,” IEEE Trans. Ind. Appl., 
        vol. 55, no. 1, pp. 529-540, Jan./Feb. 2019.

        Parameters
        ----------
        Ts : float
            Sampling interval [s].
        """
        self.Ts = Ts
        Ts_pu = self.Ts * self.sys.base.w

        # Consider the damping ratio of the resonant pole pair equals to constant value
        ZETA_R = 0.707

        # Undamped angular resonance frequency of the filter
        wr = np.sqrt(1 / (self.sys.par.X_fc * self.sys.par.Xc))

        # Consider delta due to considering delay
        delta = np.exp(-self.sys.par.wg * Ts_pu * 1j)

        # The closed-loop poles
        alpha1 = np.exp(-(wr - self.sys.par.wg) * Ts_pu)
        alpha2 = np.exp((-ZETA_R + np.sqrt(1 - ZETA_R**2) * 1j) *
                        (wr - self.sys.par.wg) * Ts_pu)
        alpha3 = np.exp((-ZETA_R - np.sqrt(1 - ZETA_R**2) * 1j) *
                        (wr - self.sys.par.wg) * Ts_pu)

        # Coefficients
        a_0 = 0
        a_1 = -alpha1 * alpha2 * alpha3
        a_2 = alpha1 * alpha2 + alpha2 * alpha3 + alpha3 * alpha1
        a_3 = -alpha1 - alpha2 - alpha3

        a_11 = delta * np.cos(wr * Ts_pu)
        a_12 = delta * -np.sin(wr * Ts_pu) / (wr * self.sys.par.X_fc)
        a_21 = delta * np.sin(wr * Ts_pu) * wr * self.sys.par.X_fc
        a_22 = delta * np.cos(wr * Ts_pu)

        b_i1 = delta * np.sin(wr * Ts_pu) / (wr * self.sys.par.X_fc)
        b_i2 = delta * (1 - np.cos(wr * Ts_pu))

        p_0 = 0
        p_1 = -a_11 * a_22 + a_12 * a_21
        p_2 = a_11 * a_22 - a_12 * a_21 + a_11 + a_22
        p_3 = -a_11 - a_22 - 1

        q_0 = a_22 * b_i1 - a_12 * b_i2
        q_1 = (-a_22 - 1) * b_i1 + a_12 * b_i2
        q_2 = b_i1
        q_3 = 0

        r_0 = -a_21 * b_i1 + a_11 * b_i2
        r_1 = a_21 * b_i1 + (-a_11 - 1) * b_i2
        r_2 = b_i2
        r_3 = 0

        s_0 = -a_11 * a_22 + a_12 * a_21
        s_1 = a_11 * a_22 - a_12 * a_21 + a_11 + a_22
        s_2 = -a_11 - a_22 - 1
        s_3 = 1

        t_0 = a_21 * b_i1 - a_11 * b_i2
        t_1 = b_i2
        t_2 = 0
        t_3 = 0

        M = np.array([[q_0, r_0, s_0, t_0], [q_1, r_1, s_1, t_1],
                      [q_2, r_2, s_2, t_2], [q_3, r_3, s_3, t_3]])

        W = np.array([[a_0 - p_0], [a_1 - p_1], [a_2 - p_2], [a_3 - p_3]])

        # The state-feedback gains K can be obtained by using matrix inversion K = (M^−1)*W
        K = np.linalg.inv(M) @ W

        # Extract individual elements
        k_v1, k_v2, k_v3, k_iu = K.flatten()

        K_u = np.array([k_v1, k_v2, k_v3])
        k_tu = k_iu / (1 - alpha1)

        self.ctr_pars = SimpleNamespace(delta=delta,
                                        K_u=K_u,
                                        k_iu=k_iu,
                                        k_tu=k_tu)

    def execute(self, sys, conv, kTs):
        """
        Execute the Voltage Controller (VC) and save the controller data.

        Parameters
        ----------
        sys : object
            System model.
        conv : object
            Converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 2 ndarray of floats
            The converter current reference in dq-frame for Current Controller (CC).
        """

        vg = sys.get_grid_voltage(kTs)

        # Get the grid-voltage angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the capacitor voltage reference for current step
        vc_ref_comp = complex(*self.input.vc_ref_dq)

        # Get the converter current in dq-frame
        i_conv_comp = complex(*alpha_beta_2_dq(sys.x[:2], theta))

        # Get the capacitor voltage in dq-frame
        vc_comp = complex(*alpha_beta_2_dq(sys.x[4:6], theta))

        # Get the converter voltage
        v_conv_comp = self.curr_ctr.v_conv_kp1_comp * self.ctr_pars.delta

        x_LC = np.array([i_conv_comp, vc_comp, v_conv_comp])

        v_conv_ref_prime_comp = self.ctr_pars.k_tu * vc_ref_comp + self.u_iu_comp - np.dot(
            self.ctr_pars.K_u, x_LC)

        # Decoupling feedback part. If the limiter is not active, it cancels the effect of
        # current controller dynamics from the converter voltage reference through
        # the static reference feedforward with gain k_ti.
        # If the current reference is limited,
        # the decoupling is not active and the current controller takes over.

        i_conv_ref_unlim_comp = (v_conv_ref_prime_comp -
                                 (self.curr_ctr.u_ii_comp -
                                  np.dot(self.curr_ctr.ctr_pars.K_i, x_LC))
                                 ) / self.curr_ctr.ctr_pars.k_ti

        i_conv_ref_comp = magnitude_limiter(i_conv_ref_unlim_comp,
                                            self.I_conv_max)

        self.u_iu_comp += self.ctr_pars.k_iu * (
            (vc_ref_comp - vc_comp) +
            (i_conv_ref_comp - i_conv_ref_unlim_comp) *
            (self.curr_ctr.ctr_pars.k_ti / self.ctr_pars.k_tu))

        i_conv_ref_dq = np.array([i_conv_ref_comp.real, i_conv_ref_comp.imag])
        self.output.i_conv_ref_dq = i_conv_ref_dq

        return self.output
