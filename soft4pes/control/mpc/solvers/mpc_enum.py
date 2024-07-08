"""Enumeration based solver for model predictive control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.utils import switching_constraint_violated


class MpcEnum:
    """
    Enumeration-based solver for model predictive control (MPC).

    Attributes
    ----------
    J : 1 x conv.nl^(3*Np) ndarray of floats
        Array for costs.
    U_seq : 3*Np x conv.nl^(3*Np) ndarray of ints
        Array for sequences of three-phase switch positions (switching sequences).
    i : int
        Counter for the switch position sequences.
    SW_COMB : 1 x conv.nl^3 ndarray of ints
        All possible three-phase switch positions.
    """

    def __init__(self, conv):
        """
        Initialize an MpcEnum instance.

        Parameters
        ----------
        conv : converter object
            Converter model.
        """
        self.J = None
        self.U_seq = None
        self.i = 0

        if conv.nl == 2:
            sw_pos_3ph = np.array([-1, 1])

        elif conv.nl == 3:
            sw_pos_3ph = np.array([-1, 0, 1])

        # Create all possible three-phase switch positions
        self.SW_COMB = np.array(list(product(sw_pos_3ph, repeat=3)))

    def __call__(self, sys, conv, ctr, y_ref):
        """
        Solve MPC problem with exhaustive enumeration.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        ctr : controller object
            Controller model.
        y_ref : ndarray of floats
            Reference vector.

        Returns
        -------
        uk : 1 x 3 ndarray of ints
            The three-phase switch position with the lowest cost.
        """

        # Initialize array for costs and switching sequences
        self.J = np.zeros((conv.nl**(3 * ctr.Np), 1))
        self.U_seq = np.zeros((conv.nl**(3 * ctr.Np), 3 * ctr.Np))
        self.i = 0
        k = 0

        self.solve(sys, conv, ctr, sys.x, y_ref, ctr.u_km1, k)

        # Find the switching sequences with the lowest cost
        min_index = np.argmin(self.J)
        uk = self.U_seq[min_index, 0:3]
        return uk

    def solve(self, sys, conv, ctr, xk, y_ref, u_km1, k):
        """
        Recursively compute the cost for different switching sequences

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        xk : ndarray of floats
            Current state vector.
        ref : ndarray of floats
            Reference vector.
        u_km1 : 1 x 3 ndarray of ints
            Previous three-phase switch position.
        k : int
            Prediction step.
        """

        # Calculate the range of columns for the current prediction step
        # This is done in order to save calculation effort, as redundant calculations are avoided
        u_col_range_start = 3 * k
        u_col_range_end = 3 * (k + 1)
        u_col_range = range(u_col_range_start, u_col_range_end)

        # Iterate over all possible three-phase switch positions
        for uk in self.SW_COMB:
            # Check if switching constraint is violated or cost is infinite
            if switching_constraint_violated(
                    conv.nl, uk, u_km1) or self.J[self.i] == np.inf:
                # Set the cost to infinity and use the current state for the next
                # prediction step
                self.J[self.i] = np.inf
                x_kp1 = np.full_like(xk, np.inf)
            else:
                # Compute the next state
                x_kp1 = ctr.get_next_state(sys, xk, uk, k)

                # Calculate the cost of reference tracking and control effort
                y_error = np.linalg.norm(y_ref[k] - np.dot(ctr.C, x_kp1))**2
                delta_u = ctr.lambda_u * np.linalg.norm(uk - u_km1, ord=1)
                self.J[self.i] = self.J[self.i] + y_error + delta_u

            if k < ctr.Np - 1:
                # If not at the last prediction step, recursively call mpc_enum
                # Assign the used three-phase switch position to all redundant switching sequences
                # Otherwise, try the next three-phase switch position
                u_row_range = range(self.i,
                                    self.i + conv.nl**(3 * (ctr.Np - k - 1)))
                self.U_seq[np.ix_(u_row_range, u_col_range)] = np.ones(
                    (len(u_row_range), 1)) * uk
                self.J[u_row_range] = self.J[self.i]

                # Move to the next prediction step
                self.solve(sys, conv, ctr, x_kp1, y_ref, uk, k + 1)
            else:
                # If at the last prediction step, store the three-phase switch position
                self.U_seq[self.i, u_col_range_start:u_col_range_end] = uk
                self.i = self.i + 1
