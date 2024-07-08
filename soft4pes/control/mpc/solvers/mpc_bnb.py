"""Branch-and-bound solver for model predictive control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.utils import switching_constraint_violated


class MpcBnB:
    """
    Branch-and-bound (BnB) solver for model predictive control (MPC).

    Attributes
    ----------
    J_min : float
        Minimum cost.
    U_seq : 1 x 3*Np ndarray
        Array for sequences of three-phase switch positions (switching sequences) with the lowest cost.
    U_temp : 1 x 3*Np ndarray
        Temporary array for incumbent swithing sequence.
    SW_COMB : 1 x conv.nl^3 ndarray
        All possible three-phase switch positions.
    """

    def __init__(self, conv):
        """
        Initialize an MpcBnB instance.

        Parameters
        ----------
        conv : converter object
            Converter model.
        """
        self.J_min = np.inf
        self.U_seq = None
        self.U_temp = None

        if conv.nl == 2:
            sw_pos_3ph = np.array([-1, 1])

        elif conv.nl == 3:
            sw_pos_3ph = np.array([-1, 0, 1])

        # Create all possible three-phase switch positions
        self.SW_COMB = np.array(list(product(sw_pos_3ph, repeat=3)))

    def __call__(self, sys, conv, ctr, y_ref):
        """
        Solve MPC problem by using a simple BnB method.

        Parameters
        ----------
        sys : system object
            System model.
        conv : converter object
            Converter model.
        ctr : controller object
            Controller model.
        y_ref : 1 x _ ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk : 1 x 3 ndarray of ints
            The three-phase switch position.
        """

        self.J_min = np.inf
        J_prev = 0
        self.U_seq = np.zeros(3 * ctr.Np)
        self.U_temp = np.zeros(3 * ctr.Np)
        k = 0

        self.solve(sys, conv, ctr, sys.x, y_ref, ctr.u_km1, k, J_prev)

        uk = self.U_seq[0:3]
        return uk

    def solve(self, sys, conv, ctr, xk, y_ref, u_km1, k, J_prev):
        """
        Recursively compute the cost for different switching sequences.

        Parameters
        ----------
        sys : object
            System model.
        conv : object
            Converter model.
        ctr : object
            Controller model.
        xk : 1 x _ ndarray
            Current state vector [p.u.].
        y_ref : 1 x _ ndarray
            Reference vector [p.u.].
        u_km1 : ndarray
            Previous three-phase switch position.
        k : int
            Prediction step.
        J_prev : float
            Previous cost.
        """

        # Iterate over all possible three-phase switch positions
        for uk in self.SW_COMB:

            # Check if switching constraint is violated or cost is infinite
            if not switching_constraint_violated(conv.nl, uk, u_km1):

                # Compute the next state
                x_kp1 = ctr.get_next_state(sys, xk, uk, k)

                # Calculate the cost of reference tracking and control effort
                y_error = np.linalg.norm(y_ref[k] - np.dot(ctr.C, x_kp1))**2
                delta_u = ctr.lambda_u * np.linalg.norm(uk - u_km1, ord=1)
                J_temp = J_prev + y_error + delta_u

                # if the cost is smaller than the current minimum cost, continue
                if J_temp < self.J_min:

                    # If not at the last prediction step, move to the next prediction step
                    if k < ctr.Np - 1:
                        self.U_temp[3 * k:3 * (k + 1)] = uk
                        self.solve(sys, conv, ctr, x_kp1, y_ref, uk, k + 1,
                                   J_temp)
                    else:
                        # If at the last prediction step, store the three-phase switch position and
                        # update the minimum cost
                        self.U_temp[3 * k:3 * (k + 1)] = uk
                        self.U_seq = np.copy(self.U_temp)
                        self.J_min = J_temp
