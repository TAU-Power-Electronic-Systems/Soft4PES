"""Base class for MPC solvers."""

from abc import ABC, abstractmethod
from types import SimpleNamespace
import numpy as np


def make_soft_constraint_matrices(soft_constraints_max, soft_constr_weights):
    """
    Create matrices for soft constraint formulation in MPC.

    Parameters
    ----------
    soft_constraints_max : float or ndarray
        Maximum allowed values for constrained variables [p.u.].
    soft_constr_weights : float or ndarray
        Weighting matrix in the objective function for the soft constraints.

    Returns
    -------
    SimpleNamespace
        Namespace containing soft constraint matrices.
    """

    # Convert scalar inputs to arrays
    if np.isscalar(soft_constraints_max):
        soft_constraints_max = np.array([soft_constraints_max])
    if np.isscalar(soft_constr_weights):
        soft_constr_weights = np.array([soft_constr_weights])

    R = np.eye(np.size(soft_constr_weights)) * soft_constr_weights
    R_size = np.size(R, 1)

    K_inv = np.array([[1, 0], [-1 / 2, np.sqrt(3) / 2],
                      [-1 / 2, -np.sqrt(3) / 2]])
    K_inv_tilde = np.kron(np.eye(R_size), K_inv)

    W = np.array([[1, -1, 0, 0, 0, 0, 0],\
                  [0, 0, 1, -1, 0, 0, 0],
                  [0, 0, 0, 0, 1, -1, 0]]).T
    W_tilde = np.kron(np.eye(R_size), W)

    M = np.kron(np.eye(R_size), np.ones((7, 1)))

    N = np.kron(np.eye(R_size), np.block([[np.ones((6, 1))], [0]]))
    Nc = np.dot(N, soft_constraints_max)

    return SimpleNamespace(M=M,
                           W_tilde=W_tilde,
                           K_inv_tilde=K_inv_tilde,
                           N=N,
                           Nc=Nc,
                           R=R)


class MPCSolverBase(ABC):
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
