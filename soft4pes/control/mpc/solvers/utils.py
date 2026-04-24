"""Utility functions for solvers used for model predictive control (MPC)."""

from types import SimpleNamespace
import numpy as np
from soft4pes.control.mpc.common.solver_base import make_soft_constraint_matrices


def switching_constraint_violated(nl, u_abc, u_km1_abc):
    """
    Check if a candidate three-phase switch position violates a switching constraint.
    A three-level converter is not allowed to directly switch from -1 and 1 (and vice versa)
    on one phase.

    Parameters
    ----------
    nl : int
        Number of converter voltage levels (2 or 3).
    u_abc : 1 x 3 ndarray of ints
        Candidate three-phase switch position.
    u_km1_abc : 1 x 3 ndarray of ints
        Previously applied three-phase switch position.

    Returns
    -------
    bool
        True if switching constraint is violated, False otherwise.
    """

    if nl == 2:
        return False
    elif nl == 3:
        return np.linalg.norm(u_abc - u_km1_abc, np.inf) >= 2
    else:
        raise ValueError('Only two- and three-level converters are supported.')


def squared_weighted_second_norm(vector, Q):
    """
    Compute the squared weighted second norm of a vector. The elements of the norm are weighted by 
    the weighting matrix Q, i.e. sqrt(x.T * Q * x)^2 = x.T * Q * x.
    
    Parameters
    ----------
    vector : ndarray
        Input vector.
    Q : ndarray
        Symmetric positive semi-definite weighting matrix.

    Returns
    -------
    float
        Squared weighted second norm.
    """

    return np.dot(vector.T, Q).dot(vector)


def compute_next_state(state_space, x_ell, u_ell_abc, d_pred, ell):
    """
    Compute the next state using discrete-time state-space.

    Parameters
    ----------
    state_space : SimpleNamespace
        Discrete-time state-space model.
    x_ell : ndarray
        State vector at prediction step ell [p.u.].
    u_ell_abc : ndarray
        Three-phase switch position or modulating signal at step ell.
    d_pred : ndarray or None
        Disturbance trajectory over the prediction horizon [p.u.].
    ell : int
        Current prediction step index.

    Returns
    -------
    ndarray
        State vector at prediction step ell+1 [p.u.].
    """

    x_ell_next = state_space.A.dot(x_ell) + state_space.B.dot(u_ell_abc)
    if d_pred is not None and hasattr(state_space, 'D'):
        size_d = np.size(state_space.D, 1)
        x_ell_next = x_ell_next + state_space.D.dot(
            d_pred[ell * size_d:(ell + 1) * size_d])
    return x_ell_next


def compute_step_ell_cost(ctr, y_ref_pred, u_ell_abc, u_ell_abc_prev,
                          x_ell_next, ell, soft_constraint_matrices):
    """
    Compute the total cost for a single prediction step.

    Parameters
    ----------
    ctr : object
        Controller object.
    y_ref_pred : ndarray
        Reference trajectory over the prediction horizon [p.u.].
    u_ell_abc : 1 x 3 ndarray of ints or floats
        Three-phase switch position or modulating signal at step ell.
    u_ell_abc_prev : 1 x 3 ndarray of ints or floats
        Three-phase switch position or modulating signal from the previous step.
    x_ell_next : ndarray
        State vector at step ell+1 [p.u.].
    ell : int
        Current prediction step index.
    soft_constraint_matrices : SimpleNamespace or None
        Namespace containing soft constraint matrices.

    Returns
    -------
    float
        Total cost for prediction step ell.
    """

    y_ell_next = np.dot(ctr.C, x_ell_next)
    y_error_cost = squared_weighted_second_norm(
        y_ref_pred[ell * np.size(ctr.Q, 1):(ell + 1) * np.size(ctr.Q, 1)] -
        y_ell_next, ctr.Q)
    delta_u_cost = ctr.lambda_u * np.linalg.norm(u_ell_abc - u_ell_abc_prev,
                                                 ord=1)

    if ctr.has_soft_constraints:
        m = soft_constraint_matrices
        zeta = m.W_tilde.dot(
            m.K_inv_tilde.dot(ctr.C_soft_constr.dot(x_ell_next))) - m.Nc

        R_size = np.size(m.R, 1)
        zeta_max = np.array(
            [np.max(zeta[j * 7:(j + 1) * 7]) for j in range(R_size)])
        zeta_cost = squared_weighted_second_norm(zeta_max, m.R)
    else:
        zeta_cost = 0

    return y_error_cost + delta_u_cost + zeta_cost


def make_QP_matrices(ctr):
    """
    Construct matrices for the quadratic programming (QP) formulation of MPC.
    
    This function builds the matrices needed for the QP problem: 
    minimize (1/2) * x.T @ H @ x + f.T @ x 
    subject to A @ x <= b. 

    Parameters
    ----------
    ctr : controller object
        Controller object.

    Returns
    -------
    SimpleNamespace
        Namespace containing the QP matrices.
    """

    model = ctr.state_space
    C = ctr.C

    Np = ctr.Np
    lambda_u = ctr.lambda_u
    has_soft_constraints = ctr.has_soft_constraints

    Q_tilde = np.kron(np.eye(Np), ctr.Q)

    # If soft constraints are used, create the related matrices and determine the size of the slack
    # variable vector
    if has_soft_constraints:
        soft_mats = make_soft_constraint_matrices(ctr.soft_constraints_max,
                                                  ctr.soft_constr_weights)
        R_size = np.size(soft_mats.R, 1)
        R_tilde = np.kron(np.eye(Np), soft_mats.R)
    else:
        R_tilde = None
        R_size = 0
        soft_mats = None

    S = np.eye(3 * Np) - np.block([[np.zeros(
        (3, 3 * Np))], [np.eye(3 * (Np - 1)),
                        np.zeros((3 * (Np - 1), 3))]])
    E = np.block([[np.eye(3)], [np.zeros(((Np - 1) * 3, 3))]])

    Gamma = make_Gamma(Np, C, model.A)

    Gamma_constraints = make_Gamma(Np, ctr.C_soft_constr,
                                   model.A) if has_soft_constraints else None

    # If the system has a disturbance input, create the related Psi matrices. Otherwise, set the Psi
    # matrices to None
    if hasattr(model, 'D'):
        B = model.B
        D = model.D
        Upsilon = make_Upsilon(Np, C, model.A, B)
        Upsilon_constraints = make_Upsilon(Np, ctr.C_soft_constr, model.A,
                                           B) if has_soft_constraints else None
        Psi = make_Upsilon(Np, C, model.A, D)
        Psi_constraints = make_Upsilon(Np, ctr.C_soft_constr, model.A,
                                       D) if has_soft_constraints else None
    else:
        B = model.B
        Upsilon = make_Upsilon(Np, C, model.A, B)
        Upsilon_constraints = make_Upsilon(Np, ctr.C_soft_constr, model.A,
                                           B) if has_soft_constraints else None
        Psi = None
        Psi_constraints = None

    # Form the quadratic objective matrix H_tilde
    H = Upsilon.T.dot(Q_tilde).dot(Upsilon) + lambda_u * S.T.dot(S)
    if has_soft_constraints:
        H_tilde = np.block(
            [[H, np.zeros((H.shape[0], R_tilde.shape[1]))],
             [np.zeros((R_tilde.shape[0], H.shape[1])), R_tilde]])
    else:
        H_tilde = H

    if has_soft_constraints:
        W_tilde = soft_mats.W_tilde
        K_inv_tilde = soft_mats.K_inv_tilde
        M = soft_mats.M
        Nc = soft_mats.Nc

        Z = np.kron(np.eye(Np), -M)
        Pi = np.kron(np.eye(Np), np.dot(W_tilde, K_inv_tilde))
        Delta = np.kron(np.ones(Np), Nc)
    else:
        K_inv_tilde = None
        W_tilde = None
        Z = None
        Pi = None
        Delta = None

    V = np.array(
        [[1, 0, 0, -1, 0, 0],\
            [0, 1, 0, 0, -1, 0],\
            [0, 0, 1, 0, 0, -1]]).T

    Omega = np.kron(np.eye(Np), V)

    # Form the linear inequality constraint matrix A_QP
    if has_soft_constraints:
        A_QP = np.block([[Omega, np.zeros((6 * Np, R_size * Np))],
                         [np.dot(Pi, Upsilon_constraints), Z]])
    else:
        A_QP = np.block([[Omega, np.zeros((6 * Np, R_size * Np))]])

    return SimpleNamespace(
        R_size=R_size,
        Gamma=Gamma,
        Gamma_constraints=Gamma_constraints,
        Upsilon=Upsilon,
        S=S,
        E=E,
        H_tilde=H_tilde,
        Q_tilde=Q_tilde,
        Delta=Delta,
        Pi=Pi,
        A_QP=A_QP,
        Psi=Psi,
        Psi_constraints=Psi_constraints,
    )


def make_Gamma(Np, C, A):
    """
    Construct the Gamma matrix mapping initial state to future outputs.

    Parameters
    ----------
    Np : int
        Prediction horizon steps.
    C : ndarray
        Output matrix of the discrete-time state-space model.
    A : ndarray
        State matrix of the discrete-time state-space model.

    Returns
    -------
    ndarray
        Gamma matrix.
    """
    Gamma = np.zeros((Np * C.shape[0], A.shape[1]))
    for i in range(0, Np):
        Gamma_row_index = range(i * C.shape[0], (i + 1) * C.shape[0])
        Gamma[Gamma_row_index] = np.dot(C, np.linalg.matrix_power(A, i + 1))
    return Gamma


def make_Upsilon(Np, C, A, B):
    """
    Construct the Upsilon matrix mapping control inputs to future outputs.

    Parameters
    ----------
    Np : int
        Prediction horizon steps.
    C : ndarray
        Output matrix of the discrete-time state-space model.
    A : ndarray
        State matrix of the discrete-time state-space model.
    B : ndarray
        Input matrix of the discrete-time state-space model.

    Returns
    -------
    ndarray
        Upsilon matrix.
    """
    Upsilon = np.zeros((Np * C.shape[0], Np * B.shape[1]))
    Upsilon_row = np.zeros((C.shape[0], Np * B.shape[1]))
    for i in range(Np):
        Upsilon_row = np.roll(Upsilon_row, B.shape[1], axis=1)
        Upsilon_row[:, :B.shape[1]] = C.dot(np.linalg.matrix_power(A,
                                                                   i)).dot(B)
        Upsilon_row_index = range(i * C.shape[0], (i + 1) * C.shape[0])
        Upsilon[Upsilon_row_index] = Upsilon_row
    return Upsilon
