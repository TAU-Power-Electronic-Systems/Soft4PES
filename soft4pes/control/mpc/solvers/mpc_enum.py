"""Enumeration based solver for Model Predictive Control (MPC)."""

from itertools import product
import numpy as np


class MpcEnum:
    """
    Enumeration-based solver for Model predictive control (MPC).

    Attributes
    ----------
    J : 1 x conv.nl^(3*Np) ndarray of floats
        Array for costs.
    u_seq : 3*Np x conv.nl^(3*Np) ndarray of ints
        Array for 3-phase switch position sequences.
    i : int
        Counter for the switch position sequences.
    SW_COMB : 1 x conv.nl^3 ndarray of ints
        All possible 3-phase switch position.
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
        self.u_seq = None
        self.i = 0

        if conv.nl == 2:
            sw_pos_3ph = np.array([-1, 1])

        elif conv.nl == 3:
            sw_pos_3ph = np.array([-1, 0, 1])

        # Create all possible 3-phase switch position
        self.SW_COMB = np.array(list(product(sw_pos_3ph, repeat=3)))

    def __call__(self, sys, conv, ctr, y_ref):
        """
        Solve MPC problem by using exhaustive enumeration.

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
            The 3-phase switch position sequence with the lowest cost.
        """

        # Initialize array for costs and 3-phase switch position sequences
        self.J = np.zeros((conv.nl**(3 * ctr.Np), 1))
        self.u_seq = np.zeros((conv.nl**(3 * ctr.Np), 3 * ctr.Np))
        self.i = 0
        k = 0

        self.solve(sys, conv, ctr, sys.x, y_ref, ctr.u_km1, k)

        # Find the 3-phase switch position sequence with the lowest cost
        min_index = np.argmin(self.J)
        uk = self.u_seq[min_index, 0:3]
        return uk

    def solve(self, sys, conv, ctr, xk, y_ref, u_km1, k):
        """
        Recursively compute the cost for different 3-phase switch position sequences.

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
            Previous 3-phase switch position.
        k : int
            Prediction step.
        """

        # Calculate the range of columns for the current prediction step
        # This is done in order to save calculation effort, as redundant calculations are avoided
        u_col_range_start = 3 * k
        u_col_range_end = 3 * (k + 1)
        u_col_range = range(u_col_range_start, u_col_range_end)

        # Iterate over all possible 3-phase switch position
        for uk in self.SW_COMB:
            # Check if switching constraint is violated or cost is infinite
            if self.switching_constraint_violated(
                    conv.nl, uk, u_km1) or self.J[self.i] == np.inf:
                # Set the cost to infinity and use the current state for the next
                # prediction step
                self.J[self.i] = np.inf
                x_kp1 = xk
            else:
                # Compute the next state
                x_kp1 = ctr.get_next_state(sys, xk, uk, k)

                # Calculate the cost of reference tracking and control effort
                ref_error = np.linalg.norm(y_ref[k] - np.dot(ctr.C, x_kp1))**2
                delta_u = ctr.lambda_u * np.linalg.norm(uk - u_km1, ord=1)
                self.J[self.i] = self.J[self.i] + ref_error + delta_u

            if k < ctr.Np - 1:
                # If not at the last prediction step, recursively call mpc_enum
                # Assign the used 3-phase switch position to all reduntant switch position sequences
                # Otherwise, try the next 3-phase switch position
                u_row_range = range(self.i,
                                    self.i + conv.nl**(3 * (ctr.Np - k - 1)))
                self.u_seq[np.ix_(u_row_range, u_col_range)] = np.ones(
                    (len(u_row_range), 1)) * uk
                self.J[u_row_range] = self.J[self.i]

                # Move to the next prediction step
                self.solve(sys, conv, ctr, x_kp1, y_ref, uk, k + 1)
            else:
                # If at the last prediction step, store the 3-phase switch position
                self.u_seq[self.i, u_col_range_start:u_col_range_end] = uk
                self.i = self.i + 1

    def switching_constraint_violated(self, nl, uk, u_km1):
        """
        Check if the converter violates a switching constraint. 
        A three-level converter is not allowed to change directly between switch positions -1 and 1. 

        Parameters
        ----------
        nl : int
            Number of converter voltage levels.
        uk : 1 x 3 ndarray of ints
            3-phase switch position.
        u_km1 : 1 x 3 ndarray of ints
            Previously applied 3-phase switch position.

        Returns
        -------
        bool
            Constraint violated.
        """

        if nl == 2:
            res = 0
        elif nl == 3:
            res = np.linalg.norm(uk - u_km1, np.inf) >= 2

        return res
