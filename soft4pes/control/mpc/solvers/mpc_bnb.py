"""Branch-and-bound solver for model predictive control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.utils import switching_constraint_violated


class MpcBnB:
    """
    Branch-and-bound (BnB) solver for model predictive control (MPC).

    Parameters
    ----------
    conv : converter object
        Converter model.

    Attributes
    ----------
    J_min : float
        Minimum cost.
    U_seq : 1 x 3*Np ndarray of ints
        Sequence of three-phase switch positions (switching sequence) with the lowest cost.
    U_temp : 1 x 3*Np ndarray of ints
        Temporary array for incumbent swithing sequence.
    SW_COMB : 1 x conv.nl^3 ndarray of ints
        All possible three-phase switch positions.
    """

    def __init__(self, conv):
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
            Controller object.
        y_ref : ndarray of floats
            Reference vector [p.u.].

        Returns
        -------
        uk_abc : 1 x 3 ndarray of ints
            The three-phase switch position.
        """

        self.J_min = np.inf
        self.U_seq = np.zeros(3 * ctr.Np)
        self.U_temp = np.zeros(3 * ctr.Np)

        self.solve(sys, conv, ctr, sys.x, y_ref, ctr.u_km1_abc)

        uk_abc = self.U_seq[0:3]
        return uk_abc

    def solve(self,
              sys,
              conv,
              ctr,
              x_ell,
              y_ref,
              u_ell_abc_prev,
              ell=0,
              J_prev=0):
        """
        Recursively compute the cost for different switching sequences.

        Parameters
        ----------
        sys : object
            System model.
        conv : object
            Converter model.
        ctr : object
            Controller object.
        x_ell : ndarray of floats
            State vector [p.u.].
        y_ref : ndarray of floats
            Reference vector [p.u.].
        u_ell_abc_prev : 1 x 3 ndarray of ints
            Previous three-phase switch position.
        ell : int
            Prediction step. The default is 0.
        J_prev : float
            Previous cost. The default is 0.
        """

        # Iterate over all possible three-phase switch positions
        for u_ell_abc in self.SW_COMB:

            # Check if switching constraint is violated or cost is infinite
            if not switching_constraint_violated(conv.nl, u_ell_abc,
                                                 u_ell_abc_prev):

                # Compute the next state
                x_ell_next = ctr.get_next_state(sys, x_ell, u_ell_abc, ell)

                # Calculate the cost of reference tracking and control effort
                y_ell_next = np.dot(ctr.C, x_ell_next)
                y_error = np.linalg.norm(y_ref[ell + 1] - y_ell_next)**2
                delta_u = np.linalg.norm(u_ell_abc - u_ell_abc_prev, ord=1)
                J_temp = J_prev + y_error + ctr.lambda_u * delta_u

                # if the cost is smaller than the current minimum cost, continue
                if J_temp < self.J_min:

                    # If not at the last prediction step, move to the next prediction step
                    if ell < ctr.Np - 1:
                        self.U_temp[3 * ell:3 * (ell + 1)] = u_ell_abc
                        self.solve(sys, conv, ctr, x_ell_next, y_ref,
                                   u_ell_abc, ell + 1, J_temp)
                    else:
                        # If at the last prediction step, store the three-phase switch position and
                        # update the minimum cost
                        self.U_temp[3 * ell:3 * (ell + 1)] = u_ell_abc
                        self.U_seq = np.copy(self.U_temp)
                        self.J_min = J_temp
