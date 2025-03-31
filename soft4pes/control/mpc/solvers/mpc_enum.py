"""Enumeration based solver for model predictive control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.utils import (switching_constraint_violated,
                                                squared_weighted_second_norm)


class MpcEnum:
    """
    Enumeration-based solver for model predictive control (MPC).

    Parameters
    ----------
    conv : converter object
        Converter model.

    Attributes
    ----------
    U_seq : 3*Np x conv.nl^(3*Np) ndarray of ints
        Array for sequences of three-phase switch positions (switching sequences).
    sw_pos_3ph : 1 x conv.nl ndarray of ints
        Possible one-phase switch positions.
    """

    def __init__(self, conv):
        self.U_seq = None
        if conv.nl == 2:
            self.sw_pos_3ph = np.array([-1, 1])
        elif conv.nl == 3:
            self.sw_pos_3ph = np.array([-1, 0, 1])
        else:
            raise ValueError(
                'Only two- and three-level converters are supported.')

    def __call__(self, sys, ctr, y_ref):
        """
        Solve MPC problem with exhaustive enumeration.

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object
            Controller object.
        y_ref : ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk_abc : 1 x 3 ndarray of ints
            The three-phase switch position with the lowest cost.
        """

        # Initialize array for switching sequences
        if self.U_seq is None:
            self.U_seq = np.array(
                list(product(self.sw_pos_3ph, repeat=3 * ctr.Np)))

        J = self.solve(sys, ctr, sys.x, y_ref, ctr.u_km1_abc)

        # Find the switching sequences with the lowest cost
        min_index = np.argmin(J)
        uk_abc = self.U_seq[min_index, 0:3]
        return uk_abc

    def solve(self, sys, ctr, xk, y_ref, u_km1_abc):
        """
        Recursively compute the cost for different switching sequences

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object.
            Controller object.
        xk : ndarray of floats
            Current state vector [p.u.].
        y_ref : ndarray of floats
            Reference vector [p.u.].
        u_km1_abc : 1 x 3 ndarray of ints
            Three-phase switch position applied at step k-1.


        Returns
        -------
        J : 1 x nl^(3*Np) ndarray of floats
            Cost array.
        """

        # Initialize the cost array
        J = np.zeros((sys.conv.nl**(3 * ctr.Np), 1))

        # Iterate over all possible switching sequences and three-phase switch positionss
        for i, u_seq in enumerate(self.U_seq):
            for ell in range(ctr.Np):
                u_ell_abc = u_seq[3 * ell:3 * (ell + 1)]

                # Update the state and the previous three-phase switch position
                if ell == 0:
                    u_ell_abc_prev = u_km1_abc
                    x_ell = xk
                else:
                    x_ell = x_ell_next
                    u_ell_abc_prev = u_seq[3 * (ell - 1):3 * ell]

                # Check if switching constraint is violated or the cost is already infinite
                if switching_constraint_violated(
                        sys.conv.nl, u_ell_abc,
                        u_ell_abc_prev) or J[i] == np.inf:
                    # Set the cost to infinity and the next state to infinity
                    J[i] = np.inf
                    x_ell_next = np.full_like(x_ell, np.inf)
                else:
                    # Compute the next state
                    x_ell_next = ctr.get_next_state(sys, x_ell, u_ell_abc, ell)

                    # Calculate the cost of the reference tracking and the control effort
                    y_ell_next = np.dot(ctr.C, x_ell_next)
                    Q = np.eye(np.size(y_ref[ell + 1]))
                    y_error = squared_weighted_second_norm(
                        y_ref[ell + 1] - y_ell_next, Q)
                    delta_u = np.linalg.norm(u_ell_abc - u_ell_abc_prev, ord=1)
                    J[i] += y_error + ctr.lambda_u * delta_u

        return J
