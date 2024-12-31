""" PI current controller for grid-connected converter with RL load """

import numpy as np
from soft4pes.utils import alpha_beta_2_dq, dq_2_abc, dq_2_alpha_beta


class RLGridPICurrCtr:
    """
    PI current controller for grid-connected converter with RL load
    
    Parameters
    ----------
    sys : system object
        System model.
    base : base-value object
        Base values.
    Ts : float
        Sampling interval [s].
    i_ref_seq_dq : Sequence object
        Current reference sequence instance in dq-frame [p.u.].
    
    Attributes
    ----------
    Rg : float
        Resistance [p.u.].
    Xg : float
        Reactance [p.u.].       
    base : base-value object
        Base values.
    Ts : float
        Sampling interval [s].
    Ts_pu : float
        Sampling interval [p.u.].
    alpha_c : float
        Controller bandwidth [p.u.]
    k_p : float
        Proportional gain [p.u.]
    k_i : float
        Proportional gain [p.u.]
    integral_error_d : float
        Current error instance in d-frame [p.u.].
    integral_error_q : float
        Current error instance in q-frame [p.u.].                               
    i_ref_seq_dq : Sequence object
        Current reference sequence instance in dq-frame [p.u.].   
    data : dict
        Controller data.
    """

    def __init__(self, sys, base, Ts, i_ref_seq_dq):
        self.Xg = sys.par.Xg
        self.Rg = sys.par.Rg
        self.Ts = Ts
        self.Ts_pu = self.Ts * base.w
        self.alpha_c = 2 * np.pi / 10 / self.Ts_pu  # Controller bandwidth (10x crossover frequency)
        self.k_p = self.alpha_c * self.Xg  # Proportional gain
        self.k_i = self.alpha_c * self.Rg  # Integral gain
        self.integral_error_d = 0
        self.integral_error_q = 0
        self.i_ref_seq_dq = i_ref_seq_dq

        self.data = {
            'ig_ref': [],
            'u': [],
            't': [],
        }

    def __call__(self, sys, conv, kTs):
        """
        Perform control.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        kTs : float
            Current discrete time instant [s].

        Returns
        -------
        1 x 3 ndarray of floats
            Modulating signal.
        """

        # Get the grid voltage
        vg = sys.get_grid_voltage(kTs)

        # Get the reference for current step
        i_ref_dq = self.i_ref_seq_dq(kTs)

        # Calculate the transformation angle
        theta = np.arctan2(vg[1], vg[0])

        # Get the current in dq frame
        i_dq = alpha_beta_2_dq(sys.x, theta)

        # Compute the converter voltage reference in dq frame using the PI controller
        u_c_dq = self.pi_controller(i_dq, i_ref_dq)

        # Transform the converter voltage reference back to abc frame
        u_c_abc = dq_2_abc(u_c_dq, theta)

        # Normalize converter voltage reference for modulation
        uk_abc = u_c_abc / (conv.v_dc / 2)

        # Save controller data
        ig_ref = dq_2_alpha_beta(i_ref_dq, theta)
        self.save_data(ig_ref, uk_abc, kTs)
        return uk_abc

    def pi_controller(self, i_dq, i_ref_dq):
        """
        PI controller in dq frame.
        
        Parameters
        ----------
        i_dq : 1 x 2 ndarray of floats
            Grid Current in dq frame [p.u.].

        i_ref_dq : 1 x 2 ndarray of floats
            Reference current in dq frame [p.u.].

        Returns
        -------
        1 x 2 ndarray of floats
            Converter voltage reference in dq frame [p.u.].
        """

        # PI controller in dq frame
        error_d = i_ref_dq[0] - i_dq[0]
        error_q = i_ref_dq[1] - i_dq[1]

        self.integral_error_d += error_d * self.Ts_pu
        self.integral_error_q += error_q * self.Ts_pu

        u_c_d = self.k_p * error_d + self.k_i * self.integral_error_d
        u_c_q = self.k_p * error_q + self.k_i * self.integral_error_q

        return np.array([u_c_d, u_c_q])

    def save_data(self, ig_ref, uk_abc, kTs):
        """
        Save controller data.

        Parameters
        ----------
        ig_ref : 1 x 2 ndarray of floats
            Current reference in alpha-beta frame.
        uk_abc : 1 x 3 ndarray of floats
            Converter three-phase switch position or modulating signal.
        kTs : float
            Current discrete time instant [s].
        """
        self.data['ig_ref'].append(ig_ref)
        self.data['u'].append(uk_abc)
        self.data['t'].append(kTs)

    def get_control_system_data(self):
        """
        This is a empty method to make different controllers compatible when building the new 
        control system structure.
        """
