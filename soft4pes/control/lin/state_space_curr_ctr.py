""" State-space current controller with anti-windup scheme for grid-connected converter with RL load """

import numpy as np
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_abc, dq_2_alpha_beta


class RLGridStateSpaceCurrCtr:
    """
    State-space current controller with anti-windup scheme for grid-connected converter with RL load.
    
    Attributes
    ----------
    Rf : float
        Resistance [p.u.].
    Xf : float
        Reactance [p.u.].       
    base : base-value object
        Base values.
    Ts : float
        Sampling interval [s].
    Ts_pu : float
        Sampling interval [p.u.].
    alpha_c : float
        Desired closed-loop controller bandwidth [p.u.].
    delta : float
        Coefficient [p.u.].       
    phi : float
        Coefficient [p.u.].
    landa : float
        Coefficient [p.u.].
    p_1 : float
        Closed-loop pole location [p.u.].
    p_2 : float
        Closed-loop pole location [p.u.].
    p_3 : float
        Closed-loop pole location [p.u.].
    k_2 : float
        Coefficient [p.u.].
    k_1 : float
        Current state feedback gain [p.u.].
    k_ii : float
        Current integral gain [p.u.].
    k_ti : float
        Current reference feedforward gain [p.u.].
    u_c_ref_sat : 1 x 2 ndarray of floats
        Converter voltage reference after saturation block in dq frame [p.u.].
    u_c_ref_unsat : 1 x 2 ndarray of floats
        Converter voltage reference before saturation block in dq frame [p.u.].                               
    i_ref_seq_dq : Sequence
        Current reference sequence instance in dq-frame [p.u.].   
    sim_data : dict
        Controller data.
    """

    def __init__(self, sys, base, Ts, i_ref_seq_dq):
        """
        Initialize a RLGridStateSpaceCurrCtr.

        Parameters
        ----------
        sys : system object
           System model.
        base : base-value object
           Base values.
        Ts : float
           Sampling interval [s].
        i_ref_seq_dq : Sequence
           Current reference sequence instance in dq-frame [p.u.].
        """
        self.V = base.V
        self.I = base.I
        self.Xf = sys.Xg * base.L  # Consider the filter inductane equals to the grid inductance
        self.Rf = sys.Rg * base.Z  # Consider the filter resitance equals to the grid resitance
        self.Ts = Ts
        #self.Ts_pu = self.Ts * base.w
        self.alpha_c = 2 * np.pi / 10 / self.Ts  # Closed-loop controller bandwidth (10x crossover frequency)
        self.delta = 1  # Consider delta equals to one due to not considering delay
        self.phi = np.exp((-self.Rf / self.Xf) * self.Ts) * self.delta
        self.landa = (self.delta - self.phi) / self.Rf
        self.p_1 = 0
        self.p_2 = np.exp(-self.alpha_c * self.Ts)
        self.p_3 = self.p_2
        self.k_2 = -self.p_1 - self.p_2 - self.p_3 + self.phi + 1
        self.k_1 = (self.p_1 * self.p_2 + self.p_1 * self.p_3 +
                    self.p_2 * self.p_3 + self.k_2 * self.phi + self.k_2 -
                    self.phi) / self.landa  # State feedback gain
        self.k_ii = (-self.p_1 * self.p_2 * self.p_3 + self.k_1 * self.landa -
                     self.k_2 * self.phi) / self.landa  # Integral gain
        self.k_ti = self.k_ii / (1 - self.p_3)  # Feedforward gain
        self.i_error = np.array([0, 0], dtype=np.float64)
        self.u_c_error = np.array([0, 0], dtype=np.float64)
        self.u_ii = np.array([0, 0], dtype=np.float64)
        self.u_c_ref_sat = np.array([0, 0], dtype=np.float64)
        self.u_c_ref_unsat = np.array([0, 0], dtype=np.float64)
        self.integral_u_ii = np.array([0, 0], dtype=np.float64)
        self.i_ref_seq_dq = i_ref_seq_dq

        self.sim_data = {
            'ig_ref': [],
            'u': [],
            't': [],
        }

    def __call__(self, sys, conv, t):
        """
        Perform control.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        t : float
            Current time [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Modulating signal.
        """

        # Get the grid voltage
        vg = sys.get_grid_voltage(t)

        # Get the reference for current step
        i_ref_dq = self.i_ref_seq_dq(t) * self.I

        # Calculate the transformation angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the current in dq frame
        i_dq = alpha_beta_2_dq(sys.x, theta) * self.I

        u_max = self.V * (conv.v_dc / 2)

        # Compute the converter voltage reference in dq frame using the state space controller with anti-windup
        u_c_dq = self.state_space_controller(i_dq, i_ref_dq, u_max) / self.V

        # Transform the converter voltage reference back to abc frame
        u_c_abc = dq_2_abc(u_c_dq, theta)

        u_k = u_c_abc / (conv.v_dc / 2)

        # Save controller data
        ig_ref = dq_2_alpha_beta(i_ref_dq / self.I, theta)
        self.save_data(ig_ref, u_k, t)
        return np.clip(u_k, -1, 1)  # Ensure modulating signal within -1 and 1

    def state_space_controller(self, i_dq, i_ref_dq, u_max):
        """
        State-space controller in dq frame.
        
        Parameters
        ----------
        i_dq : 1 x 2 ndarray of floats
            Grid Current in dq frame [p.u.].

        i_ref_dq : 1 x 2 ndarray of floats
            Reference current in dq frame [p.u.].
        u_max : float
            Maximum voltage.        

        Returns
        -------
        1 x 2 ndarray of floats
            Converter voltage reference in dq frame [p.u.].
        """

        # State space controller with anti-windup in dq frame
        u_c_ref_unsat = (self.k_ti * i_ref_dq) - (self.k_1 * i_dq) + (
            self.k_ii * self.integral_u_ii)

        self.i_error = i_ref_dq - i_dq

        self.u_c_error = (self.u_c_ref_sat - self.u_c_ref_unsat) / self.k_ti

        self.u_ii = self.u_c_error + self.i_error

        self.integral_u_ii += self.u_ii

        self.u_c_ref_unsat = u_c_ref_unsat

        # Check for saturation
        u_c_ref_sat = self.u_saturation_check(u_max, u_c_ref_unsat)
        self.u_c_ref_sat = u_c_ref_sat

        return u_c_ref_sat

    def u_saturation_check(self, u_max, u_c_ref_unsat):
        """
        Check and handle saturation of the converter voltage reference.

        Parameters
        ----------
        u_max : float
            Maximum voltage.
        u_c_ref_unsat : 1 x 2 ndarray of floats
            Unsaturated converter voltage reference.

        Returns
        -------
        1 x 2 ndarray of floats
            Saturated converter voltage reference.
        """

        u_c_abs = np.sqrt(u_c_ref_unsat[0]**2 + u_c_ref_unsat[1]**2)

        if u_c_abs <= u_max:
            u_c = u_c_ref_unsat
        else:
            u_c = (u_c_ref_unsat / u_c_abs) * u_max

        return u_c

    def save_data(self, ig_ref, u_k, t):
        """
        Save controller data.

        Parameters
        ----------
        ig_ref : 1 x 2 ndarray of floats
            Current reference in alpha-beta frame.
        u_k : 1 x 3 ndarray of ints
            Converter 3-phase switch position.
        t : float
            Current time [s].
        """
        self.sim_data['ig_ref'].append(ig_ref)
        self.sim_data['u'].append(u_k)
        self.sim_data['t'].append(t)
