"""Branch-and-bound solver for Model Predictive Control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.utils import switching_constraint_violated


class MpcBnB:
    """
    Branch-and-bound solver for Model predictive control (MPC).

    Attributes
    ----------
    J_min : float
        Minimum cost.
    u_seq : 1 x 3*Np ndarray
        Array for the 3-phase switch position sequence with the lowest cost.
    u_temp : 1 x 3*Np ndarray
        Temporary array for 3-phase switch position sequence.
    SW_COMB : 1 x conv.nl^3 ndarray
        All possible 3-phase switch positions.
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
        self.u_seq = None
        self.u_temp = None

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
        y_ref : 1 x _ ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk : 1 x 3 ndarray of ints
            The 3-phase switch position.
        """

        self.J_min = np.inf
        J_prev = 0
        self.u_seq = np.zeros(3 * ctr.Np)
        self.u_temp = np.zeros(3 * ctr.Np)
        k = 0

        self.solve(sys, conv, ctr, sys.x, y_ref, ctr.u_km1, k, J_prev)

        uk = self.u_seq[0:3]
        return uk

    def solve(self, sys, conv, ctr, xk, y_ref, u_km1, k, J_prev):
        """
        Recursively compute the cost for different 3-phase switch position sequences.

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
            Previous 3-phase switch position.
        k : int
            Prediction step.
        J_prev : float
            Previous cost.
        """

        # Iterate over all possible 3-phase switch position
        for uk in self.SW_COMB:

            # Check if switching constraint is violated or cost is infinite
            if not switching_constraint_violated(conv.nl, uk, u_km1):

                # Compute the next state
                x_kp1 = ctr.get_next_state(sys, xk, uk, k)

                # Calculate the cost of reference tracking and control effort
                ref_error = np.linalg.norm(y_ref[k] - np.dot(ctr.C, x_kp1))**2
                delta_u = ctr.lambda_u * np.linalg.norm(uk - u_km1, ord=1)
                J_temp = J_prev + ref_error + delta_u

                # if the cost is smaller than the current minimum cost, continue
                if J_temp < self.J_min:

                    # If not at the last prediction step, move to the next prediction step
                    if k < ctr.Np - 1:
                        self.u_temp[3 * k:3 * (k + 1)] = uk
                        self.solve(sys, conv, ctr, x_kp1, y_ref, uk, k + 1,
                                   J_temp)
                    else:
                        # If at the last prediction step, store the 3-phase switch position and
                        # update the minimum cost
                        self.u_temp[3 * k:3 * (k + 1)] = uk
                        self.u_seq = np.copy(self.u_temp)
                        self.J_min = J_temp
