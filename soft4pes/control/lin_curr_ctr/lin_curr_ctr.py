from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import alpha_beta_2_dq, dq_2_abc


class CurrentControlPI:
    """
    PI current controller for grid-connected inverter with RL load and switching constraints.
    
    Attributes
    ----------
    sys : system object
        System model.
    base : base value object
        Base values.
    Ts : float
        Sampling time [s].
    i_ref_seq_dq : Sequence
        Current reference sequence instance in dq-frame [p.u.].
    """

    def __init__(self, sys, base, Ts, i_ref_seq_dq):
        self.L = sys.Xg  # Inductance
        self.R = sys.Rg  # Resistance
        self.Ts = Ts
        self.Ts_pu = (Ts * base.w) / (2 * np.pi)  # Sampling time
        self.alpha_c = (
            2 * np.pi /
            10) / self.Ts_pu  # Controller bandwidth (10x crossover frequency)
        self.k_p = self.alpha_c * self.L  # Proportional gain
        self.k_i = self.alpha_c * self.R  # Integral gain
        self.integral_error_d = 0.0
        self.integral_error_q = 0.0
        self.u_km1 = np.array([0, 0, 0])
        self.i_ref_seq_dq = i_ref_seq_dq
        self.state_space = SimpleNamespace()

    def __call__(self, sys, conv, t):
        """
        Compute the switching state at time t.

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
        1 x 3 ndarray of ints
            Switching state.
        """

        # Get the discrete state-space model of the system
        self.state_space = sys.get_discrete_state_space(conv.v_dc, self.Ts)

        # Get the grid voltage
        vg = sys.get_grid_voltage(t)

        # Get the reference for current step
        i_ref_dq = self.i_ref_seq_dq(t)

        # Calculate the transformation angle
        theta = np.arctan2(vg[1], vg[0])

        # Measure the current in dq frame
        i_meas_dq = alpha_beta_2_dq(sys.x, theta)

        # Compute the control effort in dq frame using the PI controller
        u_c_dq = self.pi_controller(i_meas_dq, i_ref_dq)

        # Transform the control effort back to abc frame
        u_c_abc = dq_2_abc(u_c_dq, theta)

        u_k = u_c_abc / (conv.v_dc / 2)

        return np.clip(u_k, -1, 1)  # Ensure switching state within -1 and 1

    def pi_controller(self, i_meas_dq, i_ref_dq):
        """
        PI controller in dq frame.
        
        Parameters
        ----------
        i_meas_dq : ndarray
            Measured current in dq frame [p.u.].
        i_ref_dq : ndarray
            Reference current in dq frame [p.u.].

        Returns
        -------
        ndarray
            Control effort in dq frame [p.u.].
        """

        # PI controller in dq frame
        error_d = i_ref_dq[0] - i_meas_dq[0]
        error_q = i_ref_dq[1] - i_meas_dq[1]

        self.integral_error_d += error_d * self.Ts_pu
        self.integral_error_q += error_q * self.Ts_pu

        u_c_d = self.k_p * error_d + self.k_i * self.integral_error_d
        u_c_q = self.k_p * error_q + self.k_i * self.integral_error_q

        return np.array([u_c_d, u_c_q])
