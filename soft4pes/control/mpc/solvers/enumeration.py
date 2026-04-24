"""Enumeration-based solver for direct model predictive control (MPC) with integer optimization 
problems."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.common.solver_base import MPCSolverBase
from soft4pes.control.mpc.solvers.utils import (switching_constraint_violated,
                                                compute_next_state,
                                                compute_step_ell_cost)


class Enumeration(MPCSolverBase):
    """
    Enumeration-based solver for direct MPC with integer optimization problems.
    
    This solver exhaustively evaluates all possible three-phase switching sequences over the 
    prediction horizon, computing the cost for each sequence. The sequence with the minimum cost is 
    selected as the optimal solution. 

    "Slack variables" can be included in the cost function. In the enumeration-based solvers, slack 
    variables are not explicit optimization variables. Instead, they are represented as a function 
    of the predicted state that quantifies constraint violation and enters the objective function as
    a penalty term. Therefore, the direct enumeration problem remains a discrete search over three-
    phase switching sequences with an augmented cost, rather than a mixed-integer optimization with
    explicit continuous slack optimization variables.

    Attributes
    ----------
    U_seq : conv.nl^(3*Np) x 3*Np ndarray of ints
        Precomputed array of all possible switching sequences (three-phase switch positions).
    """

    def __init__(self):
        super().__init__()
        self.U_seq = None

    def __call__(self, sys, ctr, y_ref_pred, d_pred=None):
        """
        Solve the MPC optimization problem using exhaustive enumeration.

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object
            Controller object.
        y_ref_pred : ndarray of floats
            Reference trajectory over the prediction horizon [p.u.].
        d_pred : ndarray of floats, optional
            Disturbance trajectory over the prediction horizon [p.u.].

        Returns
        -------
        u_abc : 1 x 3 ndarray of ints
            Optimal three-phase switch position for the current time step.
        """

        if not self.initialized:
            # Initialize array for the trhee-phase switching sequences
            sw_pos_3ph = np.array(sys.conv.sw_pos_3ph)
            self.U_seq = np.array(list(product(sw_pos_3ph, repeat=3 * ctr.Np)))
            self.initialized = True

            # Initialize soft constraint matrices if needed
            self.init_soft_constraints(ctr)

        # Compute the cost for all three-phase switching sequences
        J = self.solve(sys, ctr, sys.x, y_ref_pred, ctr.u_km1_abc, d_pred)

        # Find the three-phase switching sequences with the lowest cost
        min_index = np.argmin(J)
        u_abc = self.U_seq[min_index, 0:3]
        return u_abc

    def solve(self, sys, ctr, xk, y_ref_pred, u_km1_abc, d_pred):
        """
        Compute the cost for all possible three-phase switching sequences.
        
        This method evaluates the total cost of each precomputed three-phase switching sequence by 
        stepping through the prediction horizon. Sequences that violate switching constraints are 
        assigned infinite cost.

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object.
            Controller object.
        xk : ndarray of floats
            Current state vector at time step k [p.u.].
        y_ref_pred : ndarray of floats
            Reference trajectory over the prediction horizon [p.u.].
        u_km1_abc : 1 x 3 ndarray of ints
            Three-phase switch position applied at step k-1.
        d_pred : ndarray of floats, optional
            Disturbance trajectory over the prediction horizon [p.u.].

        Returns
        -------
        J : 1 x nl^(3*Np) ndarray of floats
            Cost array with one entry per switching sequence.
        """

        # Initialize the cost array
        J = np.zeros((sys.conv.nl**(3 * ctr.Np), 1))

        # Iterate over all possible three-phase switching sequences and three-phase switch positions
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
                    x_ell_next = compute_next_state(ctr.state_space, x_ell,
                                                    u_ell_abc, d_pred, ell)

                    # Compute the cost for the current step and update the total cost
                    step_ell_cost = compute_step_ell_cost(
                        ctr, y_ref_pred, u_ell_abc, u_ell_abc_prev, x_ell_next,
                        ell, self.soft_constraint_matrices)

                    J[i] += step_ell_cost

        return J
