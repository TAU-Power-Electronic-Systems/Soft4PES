"""Branch-and-bound (BnB) solver for direct model predictive control (MPC)."""

from itertools import product
import numpy as np
from soft4pes.control.mpc.solvers.base_solver import BaseMpcSolver
from soft4pes.control.mpc.solvers.utils import (switching_constraint_violated,
                                                compute_next_state,
                                                compute_step_ell_cost)


class BranchAndBound(BaseMpcSolver):
    """
    BnB solver for direct MPC.
    
    This solver exhaustively explores the tree of possible switching sequences using a recursive 
    depth-first search with pruning. Branches are pruned when their accumulated cost exceeds the 
    current best solution, significantly reducing the search space compared to enumeration.

    Attributes
    ----------
    J_min : float
        Minimum cost found during the search.
    U_seq : 1 x 3*Np ndarray of ints
        Sequence of three-phase switch positions (switching sequence) with the lowest cost.
    U_temp : 1 x 3*Np ndarray of ints
        Temporary array storing the incumbent switching sequence during recursion.
    SW_COMB : conv.nl^3 x 3 ndarray of ints
        All possible three-phase switch positions.
    """

    def __init__(self):
        super().__init__()
        self.J_min = np.inf
        self.U_seq = None
        self.U_temp = None
        self.SW_COMB = None

    def __call__(self, sys, ctr, y_ref_pred, d_pred=None):
        """
        Solve the MPC optimization problem using the BnB algorithm.

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

        self.J_min = np.inf
        self.U_seq = np.zeros(3 * ctr.Np)
        self.U_temp = np.zeros(3 * ctr.Np)

        if not self.initialized:
            # Create all possible three-phase switch positions
            self.SW_COMB = np.array(
                list(product(sys.conv.sw_pos_3ph, repeat=3)))
            self.initialized = True

            # Initialize soft constraint matrices if needed
            self.init_soft_constraints(ctr)

        # Start the recursive BnB algorithm
        self.solve(sys, ctr, sys.x, y_ref_pred, ctr.u_km1_abc, d_pred)

        # Get the three-phase switch position with the lowest cost
        u_abc = self.U_seq[0:3]
        return u_abc

    def solve(self,
              sys,
              ctr,
              x_ell,
              y_ref_pred,
              u_ell_abc_prev,
              d_pred=None,
              ell=0,
              J_prev=0):
        """
        Recursively explore switching sequences and prune branches with suboptimal costs.
        
        This method implements the core branch-and-bound logic: for each possible switch position at
        the current prediction step, it computes the cost and either prunes the branch (if cost 
        exceeds J_min) or recursively explores deeper levels. When reaching the final prediction 
        step, it updates the best solution if a lower cost is found.

        Parameters
        ----------
        sys : object
            System model.
        ctr : object
            Controller object.
        x_ell : ndarray of floats
            State vector at prediction step ell [p.u.].
        y_ref_pred : ndarray of floats
            Reference trajectory over the prediction horizon [p.u.].
        u_ell_abc_prev : 1 x 3 ndarray of ints
            Three-phase switch position from the previous prediction step or the last applied switch
            position for ell=0.
        d_pred : ndarray of floats, optional
            Disturbance trajectory over the prediction horizon [p.u.].
        ell : int, optional
            Current prediction step index (default is 0).
        J_prev : float, optional
            Accumulated cost from previous prediction steps (default is 0).
        """

        # Iterate over all possible three-phase switch positions
        for u_ell_abc in self.SW_COMB:

            # Check if switching constraint is violated or cost is infinite
            if not switching_constraint_violated(sys.conv.nl, u_ell_abc,
                                                 u_ell_abc_prev):

                # Compute the next state
                x_ell_next = compute_next_state(ctr.state_space, x_ell,
                                                u_ell_abc, d_pred, ell)

                # Compute the cost for the current step and update the total cost
                step_ell_cost = compute_step_ell_cost(
                    ctr, y_ref_pred, u_ell_abc, u_ell_abc_prev, x_ell_next,
                    ell, self.soft_constraint_matrices)

                J_temp = J_prev + step_ell_cost

                # If the cost is smaller than the current minimum cost, continue
                if J_temp < self.J_min:

                    # If not at the last prediction step, move to the next prediction step
                    if ell < ctr.Np - 1:
                        self.U_temp[3 * ell:3 * (ell + 1)] = u_ell_abc
                        self.solve(sys, ctr, x_ell_next, y_ref_pred, u_ell_abc,
                                   d_pred, ell + 1, J_temp)
                    else:
                        # If at the last prediction step, store the three-phase switch position and
                        # update the minimum cost
                        self.U_temp[3 * ell:3 * (ell + 1)] = u_ell_abc
                        self.U_seq = np.copy(self.U_temp)
                        self.J_min = J_temp
