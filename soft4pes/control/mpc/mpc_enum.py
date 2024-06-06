""" Enumeration based finite-control set model-predictive controller"""

from types import SimpleNamespace
import numpy as np
from soft4pes.utils.conversions import dq_2_alpha_beta


class CurrCtrMpcEnum:
    """
    Enumeration-based finite-control set model-predictive controller.

    Attributes
    ----------
    lambda_u : float
        Weighting factor for the control effort.
    Np : int
        Prediction horizon.
    Ts : float
        Sampling time [s].
    i_ref_seq_dq : Sequence
        Current reference sequence instance in dq-frame [p.u.].
    state_space : SimpleNamespace
        Discrete state-space model of the system.
    """

    def __init__(self, lambda_u, Np, Ts, i_ref_seq_dq):
        """
        Initialize an MpcEnum instance.

        Parameters
        ----------
        lambda_u : float
            Weighting factor for the control effort.
        Np : int
            Prediction horizon.
        Ts : float
            Sampling time.
        curr_ref_seq_dq : Sequence
            Reference sequence instance in dq-frame [p.u.].
        """
        self.lambda_u = lambda_u
        self.Np = Np
        self.Ts = Ts
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
        vg = sys.get_grid_voltage(t)
        theta = np.arctan2(vg[1], vg[0])
        i_ref = dq_2_alpha_beta(i_ref_dq, theta)

        # Initialize array for costs and switching sequences
        J = np.zeros((conv.nl**(3 * self.Np), 1))
        u_seq = np.zeros((conv.nl**(3 * self.Np), 3 * self.Np))

        # Check all switching sequences
        J, u_seq, _ = self.mpc_enum(sys, conv, sys.x, vg, i_ref, u_seq,
                                    self.u_km1, 0, 0, J)

        # Find the switching sequence with the lowest cost and apply that to the converter
        min_index = np.argmin(J)
        u_k = u_seq[min_index, 0:3]
        self.u_km1 = u_k
        return u_k

    def mpc_enum(self, sys, conv, xk, vg, i_ref_k, u_seq, u_km1, i, k, J):
        """
        Recursively compute the cost function and control sequences for different switching states.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        xk : ndarray of floats
            Current state vector.
        vg : float
            Grid voltage [p.u.].
        i_ref_kpNp : Np x 2 ndarray of floats
            Current reference for Np timesteps.
        u_seq : 1 x 3*Np ndarray of ints
            Switching sequence for Np timesteps.
        u_km1 : 1 x 3 ndarray of ints
            Previous switching state.
        i : int
            Index for storing the cost in the cost array.
        k : int
            Prediction step.
        J : 1 x conv.nl^(3*self.Np) ndarray of floats
            Cost array.

        Returns
        -------
        J : ndarray
            Updated cost array.
        u_seq : ndarray of ints
            Updated control sequence matrix.
        i: int
            Updated index.
        """

        # Calculate the range of columns for the current prediction step
        # This is done in order to save calculation effort, as redundant calculations are avoided
        u_col_range_start = 3 * k
        u_col_range_end = 3 * (k + 1)
        u_col_range = range(u_col_range_start, u_col_range_end)

        # Make a rotation matrix
        delta_theta = sys.wg * self.Ts * sys.base.w
        R_ref = np.array([[np.cos(delta_theta), -np.sin(delta_theta)], \
                          [np.sin(delta_theta), np.cos(delta_theta)]])

        # Get the current reference at step k + 1
        i_ref_kp1 = np.dot(R_ref, i_ref_k)

        # Iterate over all possible switching states
        for u_k in conv.SW_COMB:
            # Check if switching constraint is violated or cost is infinite
            if conv.switching_constraint_violated(u_k,
                                                  u_km1) or J[i] == np.inf:
                # If so, set the cost to infinity and use the current state for the next
                # prediction step
                J[i] = np.inf
                x_kp1 = xk
            else:
                # Compute the next state
                x_kp1 = np.dot(self.state_space.A, xk) + \
                        np.dot(self.state_space.B1, u_k) + \
                        np.dot(self.state_space.B2, vg)

                # Calculate the cost of reference tracking and control effort
                i_error = np.sum((i_ref_kp1 - sys.get_current(x_kp1))**2)
                delta_u = np.sum(np.abs(u_k - u_km1))
                J[i] = J[i] + i_error + self.lambda_u * delta_u

            if k < self.Np - 1:
                # If not at the last prediction step, recursively call mpc_enum
                # Assign the used swicthing state to all reduntant swicthing sequences
                u_row_range = range(i, i + conv.nl**(3 * (self.Np - k - 1)))
                u_seq[np.ix_(u_row_range, u_col_range)] = np.ones(
                    (len(u_row_range), 1)) * u_k
                J[u_row_range] = J[i]

                # Get the voltage at the next step
                vg_kp1 = np.dot(R_ref, vg)

                # Move to the next prediction step
                J, u_seq, i = self.mpc_enum(sys, conv, x_kp1, vg_kp1,
                                            i_ref_kp1, u_seq, u_k, i, k + 1, J)
            else:
                # If at the last prediction step, store the switching state
                u_seq[i, u_col_range_start:u_col_range_end] = u_k
                i = i + 1

        return J, u_seq, i
