""" Enumeration based finite-control set model-predictive controller for current control."""

import numpy as np


class CurrCtrMpcEnum:
    """
    Enumeration-based finite-control set model-predictive controller for current control.

    Attributes
    ----------
    lambda_u : float
        Weighting factor for the control switching.
    Np : int
        Prediction horizon.
    Ts : float
        Sampling time [s].
    u_km1 : 1 x 3 ndarray of ints
        Previous 3-phase switch position.
    i_ref_seq_dq : Sequence
        Current reference sequence instance in dq-frame [pu].
    """

    def __init__(self, lambda_u, Np, Ts, i_ref_seq_dq):
        """
        Initialize an MpcEnum instance.

        Parameters
        ----------
        lambda_u : float
            Weighting factor for the switching effort.
        Np : int
            Prediction horizon.
        Ts : float
            Sampling time [s].
        curr_ref_seq_dq : Sequence
            Reference sequence instance in dq-frame [pu].
        """
        self.lambda_u = lambda_u
        self.Np = Np
        self.Ts = Ts
        self.u_km1 = np.array([0, 0, 0])
        self.i_ref_seq_dq = i_ref_seq_dq

    def __call__(self, sys, conv, t):
        """
        Solve the optimum switch position at time t.

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
            3-phase switch position.
        """

        # Get the reference for the next Np time steps
        i_ref_kpNp = self.i_ref_seq_dq.get_ref_Np(self, t)

        # Initialize array for costs and 3-phase switch position sequences
        J = np.zeros((conv.nl**(3 * self.Np), 1))
        u_seq = np.zeros((conv.nl**(3 * self.Np), 3 * self.Np))

        # Check all switch position sequences
        J, u_seq, _ = self.mpc_enum(sys, conv, sys.x, t, i_ref_kpNp, u_seq,
                                    self.u_km1, 0, 0, J)

        # Find the switch position sequence with the lowest cost
        min_index = np.argmin(J)
        u_k = u_seq[min_index, 0:3]
        self.u_km1 = u_k
        return u_k

    def mpc_enum(self, sys, conv, xk, t, i_ref_kpNp, u_seq, u_km1, i, k, J):
        """
        Recursively compute the cost for different 3-phase switch positions.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        xk : ndarray of floats
            State vector [pu].
        t : float
            Current time [s].
        i_ref_kpNp : Np x 2 ndarray of floats
            Current reference for Np timesteps [pu].
        u_seq : 1 x 3*Np ndarray of ints
            3-phase switch position sequence for Np timesteps.
        u_km1 : 1 x 3 ndarray of ints
            Previous 3-phase switch position.
        i : int
            Index for storing the cost in the cost array.
        k : int
            Prediction step.
        J : 1 x conv.nl^(3*self.Np) ndarray of floats
            Cost array.

        Returns
        -------
        J : 1 x conv.nl^(3*self.Np) ndarray of floats
            Updated cost array.
        u_seq : 1 x 3*Np ndarray of ints
            Updated 3-phase switch position sequence for Np timesteps.
        i: int
            Updated index.
        """

        # Calculate the range of columns for the current prediction step
        # These are the columns for the 3-phase switch positions
        # The costs of redundant 3-phase switch positions are calculated at once
        u_col_range_start = 3 * k
        u_col_range_end = 3 * (k + 1)
        u_col_range = range(u_col_range_start, u_col_range_end)

        # Iterate over all possible 3-phase switch positions
        for u_k in conv.SW_COMB:

            # Check if switching constraint is violated or cost is infinite
            if conv.switching_constraint_violated(u_k,
                                                  u_km1) or J[i] == np.inf:
                # Set the cost to infinity and use the current state for the next
                # prediction step
                J[i] = np.inf
                x_kp1 = xk
            else:
                # Compute the next state and calculate the cost
                x_kp1 = sys.get_next_state(xk, u_k, conv.v_dc, t, self.Ts)
                i_error = np.sum((i_ref_kpNp[k] - sys.get_current(x_kp1))**2)
                delta_u = self.lambda_u * np.sum(np.abs(u_k - u_km1))
                J[i] = J[i] + i_error + delta_u

            if k < self.Np - 1:
                # If not at the last prediction step, recursively call mpc_enum and store the
                # 3-phase switch position
                u_row_range = range(i, i + conv.nl**(3 * (self.Np - k - 1)))
                u_seq[np.ix_(u_row_range, u_col_range)] = np.ones(
                    (len(u_row_range), 1)) * u_k
                J[u_row_range] = J[i]
                J, u_seq, i = self.mpc_enum(sys, conv, x_kp1, t + self.Ts,
                                            i_ref_kpNp, u_seq, u_k, i, k + 1,
                                            J)
            else:
                # If at the last prediction step, store the 3-phase switch position
                u_seq[i, u_col_range_start:u_col_range_end] = u_k
                i = i + 1

        return J, u_seq, i
