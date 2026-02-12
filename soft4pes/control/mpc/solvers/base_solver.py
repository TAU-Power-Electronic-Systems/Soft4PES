"""Base class for MPC solvers."""

from abc import ABC, abstractmethod
from soft4pes.control.mpc.solvers.utils import make_soft_constraint_matrices


class BaseMpcSolver(ABC):
    """
    Abstract base class for MPC solvers.

    This class provides common initialization and soft constraint handling
    for all MPC solver implementations.

    Attributes
    ----------
    soft_constraint_matrices : SimpleNamespace or None
        Namespace containing soft constraint matrices (M, W_tilde, K_inv_tilde, N, Nc, R).
    initialized : bool
        Flag indicating whether solver-specific initialization has been performed.
    """

    def __init__(self):
        """Initialize base solver attributes."""
        self.soft_constraint_matrices = None
        self.initialized = False

    def init_soft_constraints(self, ctr):
        """
        Initialize soft constraint matrices if needed.

        This method should be called during solver initialization to set up
        soft constraint matrices based on controller configuration.

        Parameters
        ----------
        ctr : controller object
            Controller object with soft constraint configuration.
        """
        if ctr.has_soft_constraints:
            self.soft_constraint_matrices = make_soft_constraint_matrices(
                ctr.soft_constraints_max, ctr.soft_constr_weights)

    @abstractmethod
    def __call__(self, sys, ctr, y_ref, d_pred=None):
        """
        Solve the MPC optimization problem.

        Parameters
        ----------
        sys : system object
            System model.
        ctr : controller object
            Controller object.
        y_ref : ndarray of floats
            Reference vector [p.u.].
        d_pred : ndarray of floats, optional
            Disturbance prediction vector [p.u.].

        Returns
        -------
        u_abc : ndarray
            Optimal control input (three-phase switch position or modulating signal).
        """
